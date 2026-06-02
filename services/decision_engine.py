# services/decision_engine.py
"""
决策引擎服务
根据模糊规则和调度员输入选择合适的控制策略
"""
import logging
import numpy as np
from typing import Dict, Any, Optional
from sqlalchemy import func
from config.database import SessionLocal
from models.fuzzy_membership import FuzzyMembershipFunction
from tools.fuzzy_passenger_flow import get_c_from_fuzzy_logic
from algorithms.ilc_controller import ILCController
from algorithms.rmpc_controller import lmi_solve
from services.db_service import get_latest_delay_record
from models.feedback import Feedback

logger = logging.getLogger(__name__)


def check_fuzzy_rules_exist() -> bool:
    """
    检查数据库中是否存在模糊规则

    返回:
        bool: 如果存在模糊规则返回True，否则返回False
    """
    db = SessionLocal()
    try:
        count = db.query(FuzzyMembershipFunction).count()
        return count > 0
    finally:
        db.close()


def parse_dispatcher_intent(text: str) -> Dict[str, Any]:
    """
    解析调度员输入中的意图关键词

    参数:
        text: 调度员输入文本

    返回:
        包含意图标志的字典
    """
    intent = {
        "need_fast_response": False,  # 是否需要快速响应
        "passenger_flow_surge": False,  # 是否客流突变
        "raw_text": text
    }

    # 检查是否需要快速响应
    fast_keywords = ["迅速", "快速", "立即", "马上", "紧急", "急"]
    for keyword in fast_keywords:
        if keyword in text:
            intent["need_fast_response"] = True
            break

    # 检查是否客流突变
    surge_keywords = ["客流突变", "客流激增", "乘客突增", "人流突增", "客流突然"]
    for keyword in surge_keywords:
        if keyword in text:
            intent["passenger_flow_surge"] = True
            break

    logger.info(f"调度员意图解析结果: {intent}")
    return intent


def get_feedback_parameters() -> Optional[Dict[str, float]]:
    """
    从数据库获取反馈控制参数

    返回:
        包含p, q, c参数的字典，如果没有则返回None
    """
    db = SessionLocal()
    try:
        latest_feedback = db.query(Feedback).order_by(
            Feedback.created_at.desc()
        ).first()

        if latest_feedback:
            return {
                "p": latest_feedback.p,
                "q": latest_feedback.q,
                "c": latest_feedback.c if latest_feedback.c else 1.0
            }
        return None
    finally:
        db.close()


def execute_fuzzy_rule_based_control(intent: Dict[str, Any], delay_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于模糊规则执行控制策略

    参数:
        intent: 调度员意图
        delay_info: 晚点信息

    返回:
        控制结果
    """
    result = {
        "strategy": "",
        "parameters": {},
        "control_output": {},
        "message": ""
    }

    # 获取模糊规则计算的c值
    try:
        c = get_c_from_fuzzy_logic()
        result["parameters"]["c"] = c
    except Exception as e:
        logger.error(f"模糊规则计算失败: {e}")
        c = 1.0  # 默认值
        result["parameters"]["c"] = c

    # 根据意图选择控制策略
    if intent["need_fast_response"]:
        # 策略1: 模糊规则 + 反馈控制
        result["strategy"] = "fuzzy_plus_feedback"
        feedback_params = get_feedback_parameters()

        if feedback_params:
            result["parameters"].update(feedback_params)
            # 这里可以调用反馈控制算法
            result["control_output"] = {
                "type": "feedback_control",
                "c": c,
                "p": feedback_params["p"],
                "q": feedback_params["q"]
            }
            result["message"] = "采用模糊规则+反馈控制策略进行快速响应"
        else:
            result["message"] = "需要快速响应，但未找到反馈控制参数，仅使用模糊规则"

    elif intent["passenger_flow_surge"]:
        # 策略2: 模糊规则 + 迭代学习控制(ILC)
        result["strategy"] = "fuzzy_plus_ilc"
        result["message"] = "检测到客流突变，采用模糊规则+迭代学习控制算法"

        # 准备ILC控制器所需的数据
        ilc_result = execute_ilc_with_fuzzy(c, delay_info)
        result["control_output"] = ilc_result

    else:
        # 策略3: 模糊规则 + 鲁棒模型预测控制(RMPC)
        result["strategy"] = "fuzzy_plus_rmpc"
        result["message"] = "采用模糊规则+鲁棒模型预测控制策略"

        # 准备RMPC控制器所需的数据
        rmpc_result = execute_rmpc_with_fuzzy(c, delay_info)
        result["control_output"] = rmpc_result

    return result


def execute_ilc_with_fuzzy(c: float, delay_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行基于模糊规则的ILC控制

    参数:
        c: 模糊规则计算的参数
        delay_info: 晚点信息

    返回:
        ILC控制结果
    """
    time_schedule = {
        'TrCir': {1: 1},
        'TimeError': {(1, 9): delay_info.get("delay_minutes", 0)},
        'TimeUk': {}
    }

    controller = ILCController(M=16, N=8)
    
    try:
        ilc_result = controller.compute_control(
            train_num=1,
            platform_num=1,
            time_schedule=time_schedule,
            c=c
        )

        return {
            "algorithm": "ILC",
            "c_parameter": c,
            "control_signal": ilc_result.get("Uik", 0),
            "details": ilc_result,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"ILC计算失败: {e}")
        return {
            "algorithm": "ILC",
            "c_parameter": c,
            "error": str(e),
            "status": "failed"
        }


def execute_rmpc_with_fuzzy(c: float, delay_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行基于模糊规则的RMPC控制

    参数:
        c: 模糊规则计算的参数
        delay_info: 晚点信息字典，包含train_number, station_name, delay_minutes等

    返回:
        RMPC控制结果
    """
    M, N = 18, 14
    delay_minutes = delay_info.get("delay_minutes", 0)
    
    x_real = np.zeros(M)
    x_real[0] = float(delay_minutes)
    
    control_params = {
        'ckd': 0,
        'd': 0.2,
        'ckpoint': c
    }

    try:
        u_result = lmi_solve(M, N, x_real, control_params)
        return {
            "algorithm": "RMPC",
            "c_parameter": c,
            "control_signal": u_result.tolist() if hasattr(u_result, 'tolist') else list(u_result),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"RMPC求解失败: {e}")
        return {
            "algorithm": "RMPC",
            "c_parameter": c,
            "error": str(e),
            "status": "failed"
        }


def execute_algorithm_only(delay_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    当没有模糊规则时，仅使用算法

    参数:
        delay_info: 晚点信息

    返回:
        控制结果
    """
    M, N = 18, 14
    delay_minutes = delay_info.get("delay_minutes", 0)
    
    x_real = np.zeros(M)
    x_real[0] = float(delay_minutes)

    control_params = {
        'ckd': 0,
        'd': 0.2,
        'ckpoint': 0.4
    }

    try:
        u_result = lmi_solve(M, N, x_real, control_params)
        return {
            "strategy": "algorithm_only",
            "algorithm": "RMPC",
            "control_signal": u_result.tolist() if hasattr(u_result, 'tolist') else list(u_result),
            "message": "未检测到模糊规则，仅使用RMPC算法"
        }
    except Exception as e:
        logger.error(f"算法执行失败: {e}")
        return {
            "strategy": "algorithm_only",
            "error": str(e),
            "message": "算法执行失败"
        }


def make_dispatch_decision(dispatcher_input: str, delay_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    主决策函数：根据模糊规则和调度员输入做出调度决策

    参数:
        dispatcher_input: 调度员输入文本
        delay_info: 晚点信息字典，包含train_number, station_name, delay_minutes等

    返回:
        决策结果
    """
    decision_result = {
        "dispatcher_input": dispatcher_input,
        "delay_info": delay_info or {},
        "fuzzy_rules_exist": False,
        "intent": {},
        "selected_strategy": "",
        "execution_result": {},
        "final_recommendation": ""
    }

    try:
        # 步骤1: 检查是否存在模糊规则
        fuzzy_exists = check_fuzzy_rules_exist()
        decision_result["fuzzy_rules_exist"] = fuzzy_exists

        if not fuzzy_exists:
            # 没有模糊规则，仅使用算法
            logger.info("数据库中无模糊规则，采用纯算法策略")
            algo_result = execute_algorithm_only(delay_info or {})
            decision_result["selected_strategy"] = "algorithm_only"
            decision_result["execution_result"] = algo_result
            decision_result["final_recommendation"] = algo_result.get("message", "")
            return decision_result

        # 步骤2: 解析调度员意图
        intent = parse_dispatcher_intent(dispatcher_input)
        decision_result["intent"] = intent

        # 步骤3: 根据意图执行相应控制策略
        execution_result = execute_fuzzy_rule_based_control(intent, delay_info or {})
        decision_result["selected_strategy"] = execution_result["strategy"]
        decision_result["execution_result"] = execution_result
        decision_result["final_recommendation"] = execution_result["message"]

        logger.info(f"决策完成，选择策略: {execution_result['strategy']}")
        return decision_result

    except Exception as e:
        logger.error(f"决策过程出错: {e}", exc_info=True)
        decision_result["error"] = str(e)
        decision_result["final_recommendation"] = f"决策过程出错: {str(e)}"
        return decision_result


# 测试代码
if __name__ == "__main__":
    # 测试用例1: 有模糊规则，需要快速响应
    print("=" * 60)
    print("测试1: 需要快速响应的情况")
    result1 = make_dispatch_decision(
        dispatcher_input="列车G101在北京南站因设备故障晚点5分钟，需要迅速处理",
        delay_info={"train_number": "G101", "station_name": "北京南站", "delay_minutes": 5}
    )
    print(f"最终建议: {result1['final_recommendation']}")
    print(f"选择策略: {result1['selected_strategy']}")

    print("\n" + "=" * 60)
    print("测试2: 客流突变的情况")
    result2 = make_dispatch_decision(
        dispatcher_input="由于客流突变导致C2503次列车在天津站晚点8分钟",
        delay_info={"train_number": "C2503", "station_name": "天津站", "delay_minutes": 8}
    )
    print(f"最终建议: {result2['final_recommendation']}")
    print(f"选择策略: {result2['selected_strategy']}")

    print("\n" + "=" * 60)
    print("测试3: 普通情况")
    result3 = make_dispatch_decision(
        dispatcher_input="D789次列车在上海虹桥站晚点10分钟",
        delay_info={"train_number": "D789", "station_name": "上海虹桥站", "delay_minutes": 10}
    )
    print(f"最终建议: {result3['final_recommendation']}")
    print(f"选择策略: {result3['selected_strategy']}")
