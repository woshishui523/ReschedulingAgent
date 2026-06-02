"""
调度相关工具函数集合
"""
import json
from langchain_core.tools import Tool
from config.llm_config import get_llm
from models.fuzzy_membership import FuzzyMembershipFunction
from models.feedback import Feedback
from config.database import SessionLocal
from algorithms.ilc_controller import ILCController, ilc_compute_control
from algorithms.rmpc_controller import lmi_solve
from tools.fuzzy_passenger_flow import get_c_from_fuzzy_logic
import logging
import re

logger = logging.getLogger(__name__)


def _dispatch_decision_wrapper(input_str: str) -> str:
    """
    智能体驱动的调度决策工具包装函数
    
    输入格式: JSON字符串，包含dispatcher_input和可选的delay_info
    """
    try:
        # 解析输入
        if isinstance(input_str, str):
            params = json.loads(input_str)
        else:
            params = input_str
        
        dispatcher_input = params.get('dispatcher_input', '')
        delay_info = params.get('delay_info', {})
        
        # 获取LLM实例
        llm = get_llm()
        
        # 步骤1: 检查数据库状态
        db = SessionLocal()
        try:
            fuzzy_count = db.query(FuzzyMembershipFunction).count()
            latest_feedback = db.query(Feedback).order_by(
                Feedback.created_at.desc()
            ).first()
            
            feedback_params = None
            if latest_feedback:
                feedback_params = {
                    "p": latest_feedback.p,
                    "q": latest_feedback.q,
                    "c_db": latest_feedback.c if latest_feedback.c else 1.0
                }
        finally:
            db.close()
        
        has_fuzzy_rules = fuzzy_count > 0
        
        # 步骤2: 使用LLM进行语义分析
        analysis_prompt = f"""
你是一个列车调度意图分析专家。请分析以下调度员描述，判断场景特征。

【调度员描述】
{dispatcher_input}

【晚点信息】
{json.dumps(delay_info, ensure_ascii=False)}

【分析任务】
请判断以下三个维度（每个维度只能选择一个）：

1. **紧急程度判断**：
   - "urgent"（紧急）：描述中包含"紧急"、"立即"、"迅速"、"快速"、"马上"等词汇，或语气急迫
   - "normal"（普通）：一般性描述，没有紧急词汇

2. **延误原因类型**：
   - "passenger_surge"（客流突变）：明确提到"客流突变"、"客流激增"、"乘客突增"、"人流突然增加"等
   - "other"（其他原因）：设备故障、天气、信号问题等其他原因

3. **延误严重程度**（根据delay_minutes）：
   - "minor"（轻微）：< 5分钟
   - "moderate"（中等）：5-10分钟
   - "severe"（严重）：> 10分钟

【输出要求】
必须返回严格的JSON格式，不要有任何额外文字：
{{
    "urgency": "urgent" 或 "normal",
    "reason_type": "passenger_surge" 或 "other",
    "severity": "minor" 或 "moderate" 或 "severe",
    "analysis_reason": "简要说明判断理由"
}}
"""
        
        analysis_response = llm.invoke(analysis_prompt)
        analysis_text = analysis_response.content if hasattr(analysis_response, 'content') else str(analysis_response)
        
        # 提取JSON
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            analysis_result = json.loads(json_match.group())
        else:
            analysis_result = json.loads(analysis_text)
        
        urgency = analysis_result.get('urgency', 'normal')
        reason_type = analysis_result.get('reason_type', 'other')
        
        # 步骤3: 根据规则选择策略
        # 决策逻辑：
        # - 需要快速响应(urgent) → 反馈控制
        # - 客流突变(passenger_surge) → ILC
        # - 其他情况 → RMPC
        
        if urgency == 'urgent':
            selected_algorithm = 'feedback'
            strategy_name = 'fuzzy_plus_feedback' if has_fuzzy_rules else 'feedback_only'
            reason = "检测到需要快速响应，选择反馈控制算法"
        elif reason_type == 'passenger_surge':
            selected_algorithm = 'ilc'
            strategy_name = 'fuzzy_plus_ilc' if has_fuzzy_rules else 'ilc_only'
            reason = "检测到客流突变，选择迭代学习控制(ILC)算法"
        else:
            selected_algorithm = 'rmpc'
            strategy_name = 'fuzzy_plus_rmpc' if has_fuzzy_rules else 'rmpc_only'
            reason = "常规延误场景，选择鲁棒模型预测控制(RMPC)算法"
        
        # 步骤4: 获取参数并执行相应算法
        execution_result = {
            "algorithm": selected_algorithm,
            "has_fuzzy_rules": has_fuzzy_rules,
            "status": "success"
        }
        
        # 获取模糊规则的c值
        c_value = None
        if has_fuzzy_rules:
            try:
                c_value = get_c_from_fuzzy_logic()
                execution_result["c_from_fuzzy"] = c_value
            except Exception as e:
                logger.warning(f"模糊规则计算c失败: {e}")
                c_value = feedback_params.get('c_db', 0.4) if feedback_params else 0.4
        else:
            c_value = feedback_params.get('c_db', 0.4) if feedback_params else 0.4
        
        execution_result["c_parameter"] = c_value
        
        # 根据选择的算法执行计算
        if selected_algorithm == 'feedback' and feedback_params:
            execution_result["feedback_params"] = {
                "p": feedback_params['p'],
                "q": feedback_params['q'],
                "c": c_value
            }
            execution_result["message"] = f"{'模糊规则 + ' if has_fuzzy_rules else ''}反馈控制已就绪"
            
        elif selected_algorithm == 'ilc' and delay_info:
            try:
                time_schedule = {
                    'TrCir': {1: 1},
                    'TimeError': {(1, 9): delay_info.get("delay_minutes", 0)},
                    'TimeUk': {}
                }
                controller = ILCController(M=16, N=8)
                ilc_result = controller.compute_control(
                    train_num=1,
                    platform_num=1,
                    time_schedule=time_schedule,
                    c=c_value
                )
                execution_result["ilc_output"] = {
                    "Uik": ilc_result.get("Uik", 0),
                    "elapsed_time": ilc_result.get("elapsed_time", 0)
                }
                execution_result["message"] = f"{'模糊规则 + ' if has_fuzzy_rules else ''}ILC控制已就绪"
            except Exception as e:
                logger.error(f"ILC计算失败: {e}")
                execution_result["error"] = str(e)
                execution_result["message"] = "ILC计算失败"

        elif selected_algorithm == 'rmpc' and delay_info:
            try:
                M, N = 18, 14
                delay_minutes = delay_info.get("delay_minutes", 0)
                
                # 构建RMPC状态向量：前(M-N)项为同站其他列车晚点时间，后N项为零填充
                x_real = build_state_vector_for_rmpc(
                    current_train_id=1,
                    current_global_station_idx=9,
                    delay_dict={(1, 9): delay_minutes},
                    M=M,
                    N=N
                )
                
                control_params = {
                    'ckd': 0,
                    'd': 0.2,
                    'ckpoint': c_value
                }
                u_result = lmi_solve(M, N, x_real, control_params)
                execution_result["rmpc_output"] = {
                    "control_signal": u_result.tolist() if hasattr(u_result, 'tolist') else list(u_result),
                    "dimensions": {"M": M, "N": N},
                    "state_vector_length": len(x_real)
                }
                execution_result["message"] = f"{'模糊规则 + ' if has_fuzzy_rules else ''}RMPC控制已计算完成"
            except Exception as e:
                logger.error(f"RMPC求解失败: {e}")
                execution_result["error"] = str(e)
                execution_result["message"] = "RMPC求解失败"
        
        # 步骤5: 整合最终结果
        final_result = {
            "dispatcher_input": dispatcher_input,
            "delay_info": delay_info,
            "system_status": {
                "fuzzy_rules_exist": has_fuzzy_rules,
                "fuzzy_rules_count": fuzzy_count,
                "feedback_available": feedback_params is not None
            },
            "intent_analysis": analysis_result,
            "decision": {
                "selected_strategy": strategy_name,
                "algorithm": selected_algorithm,
                "reasoning": reason,
                "analysis_reason": analysis_result.get('analysis_reason', '')
            },
            "execution_result": execution_result,
            "final_recommendation": execution_result.get("message", "决策完成")
        }
        
        return json.dumps(final_result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"智能体决策失败: {e}", exc_info=True)
        return json.dumps({
            'error': f'智能体调度决策失败: {str(e)}',
            'input': str(input_str),
            'fallback_strategy': 'fuzzy_plus_rmpc' if 'fuzzy_count' in locals() and fuzzy_count > 0 else 'rmpc_only'
        }, ensure_ascii=False, indent=2)


def build_state_vector_for_rmpc(current_train_id, current_global_station_idx, delay_dict, M=18, N=14):
    """
    为RMPC算法构建状态向量 X
    
    参数:
        current_train_id (int): 当前关注的列车序号
        current_global_station_idx (int): 当前关注的全局车站序号
        delay_dict (dict): 存储了所有晚点记录的字典，键为 (train_id, global_station_idx)
        M (int): 系统状态维度，默认 18
        N (int): 控制输入维度，默认 14
    
    返回:
        np.ndarray: 长度为 M 的一维数组
                   前 (M-N) 项为同站其他列车晚点时间
                   后 N 项为零填充
    """
    import numpy as np
    
    state_vector = []
    
    # 第一部分：前 (M-N) 项 - 同站其他列车的晚点时间
    for t_id in range(1, M - N + 1):
        delay_time = delay_dict.get((t_id, current_global_station_idx), 0)
        state_vector.append(float(delay_time))
    
    # 第二部分：后 N 项 - 零填充
    state_vector.extend([0.0] * N)
    
    return np.array(state_vector)

# 定义调度决策工具
dispatch_decision_tool = Tool(
    name="DispatchDecisionMaker",
    func=_dispatch_decision_wrapper,
    description="""智能调度决策工具，根据语义分析选择合适的控制策略。

决策逻辑：
1. 首先检查是否存在模糊规则
2. 分析调度员描述的语义（紧急程度、延误原因类型）
3. 根据以下规则选择策略：
   - 如果需要快速响应(包含"紧急"、"立即"、"迅速"等) → 采用反馈控制
   - 如果客流突变(包含"客流突变"、"客流激增"等) → 采用迭代学习控制(ILC)
   - 其他情况 → 采用鲁棒模型预测控制(RMPC)
4. 如果有模糊规则，则"模糊规则+算法"；如果没有，则"纯算法"

输入：JSON格式字符串，包含：
  - dispatcher_input (str): 调度员的自然语言输入
  - delay_info (dict, 可选): 晚点信息 {train_number, station_name, delay_minutes}

输出：JSON格式，包含：
  - system_status: 系统状态（是否有模糊规则等）
  - intent_analysis: 意图分析结果
  - decision: 选择的策略和推理过程
  - execution_result: 算法执行结果
  - final_recommendation: 最终建议

示例输入：
{"dispatcher_input": "列车G101在北京南站因设备故障晚点5分钟，需要迅速处理", 
 "delay_info": {"train_number": "G101", "station_name": "北京南站", "delay_minutes": 5}}"""
)


def get_delay_time(i, j, delay_dict):
    """
    查询指定列车在指定车站的晚点时间
    
    参数:
        i (int): 列车序号（物理列车编号）
        j (int): 全局车站序号，计算公式为 (k-1)*8 + n
                 其中 k 为圈数，n 为该圈内的相对站位置(1-8)
        delay_dict (dict): 晚点记录字典，键为元组 (i, j)，值为晚点分钟数
    
    返回:
        float/int: 晚点时间（分钟），如果没有记录则返回 0
    """
    return delay_dict.get((i, j), 0)


def build_state_vector(current_train_id, current_global_station_idx, delay_dict, M=15, N=8):
    """
    构建算法的状态向量 X
    
    参数:
        current_train_id (int): 当前关注的列车序号 i
        current_global_station_idx (int): 当前关注的全局车站序号 j
        delay_dict (dict): 存储了所有晚点记录的字典，键为 (train_id, global_station_idx)
        M (int): 列车总数，默认 15
        N (int): 车站数量，默认 8
    
    返回:
        list: 长度为 M 的一维列表，包含前 (M-N) 项的同站其他列车晚点时间
              和后 N 项的零填充
    """
    state_vector = []
    
    # 第一部分：前 (M-N) 项
    # 遍历列车编号 1 到 (M-N)，获取它们在 current_global_station_idx 的晚点时间
    for t_id in range(1, M - N + 1):  # 1 到 7
        delay_time = get_delay_time(t_id, current_global_station_idx, delay_dict)
        state_vector.append(delay_time)
    
    # 第二部分：后 N 项
    # 直接填充 N 个 0
    state_vector.extend([0] * N)
    
    return state_vector


def compute_ilc_control(train_num, platform_num, time_schedule, c=0.4, M=16, N=8):
    """
    计算迭代学习控制 (ILC) 控制率
    
    参数:
        train_num (int): 当前列车序号 Tnum
        platform_num (int): 当前站台序号 Pnum
        time_schedule (dict): 时间调度表，包含:
            - TrCir: 列车圈数字典 {train_num: circle_number}
            - TimeError: 晚点时间字典 {(train_num, station_idx): delay}
            - TimeUk: 历史控制率字典 {(train_num, station_idx): control_value}
        c (float): 客流与停车时间关系参数，默认 0.4
        M (int): 列车总数，默认 16
        N (int): 站台数量，默认 8
    
    返回:
        dict: 包含以下字段:
            - Uik: 实际控制量 (第一个控制值)
            - uik_full: 完整控制向量列表
            - Xk: 当前状态向量
            - elapsed_time: 计算耗时 (秒)
            - is_first_circle: 是否为第一圈运行
    """
    result = ilc_compute_control(
        train_num=train_num,
        platform_num=platform_num,
        time_schedule=time_schedule,
        c=c,
        M=M,
        N=N
    )
    
    return result


# ========== LangChain Tools 定义 ==========



def _ilc_control_wrapper(input_str: str) -> str:
    """
    ILC 控制计算的包装函数，用于 LangChain Tool
    
    输入格式: JSON 字符串，包含 train_num, platform_num, time_schedule, c, M, N
    """
    try:
        # 解析输入
        if isinstance(input_str, str):
            params = json.loads(input_str)
        else:
            params = input_str
        
        # 提取参数
        train_num = params.get('train_num', 1)
        platform_num = params.get('platform_num', 1)
        time_schedule = params.get('time_schedule', {})
        c = params.get('c', 0.4)
        M = params.get('M', 16)
        N = params.get('N', 8)
        
        # 调用 ILC 控制计算
        result = compute_ilc_control(
            train_num=train_num,
            platform_num=platform_num,
            time_schedule=time_schedule,
            c=c,
            M=M,
            N=N
        )
        
        # 返回 JSON 格式结果
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            'error': f'ILC 控制计算失败: {str(e)}',
            'input': str(input_str)
        }, ensure_ascii=False)


# 定义 ILC 控制工具
ilc_control_tool = Tool(
    name="ILCControlCalculator",
    func=_ilc_control_wrapper,
    description="""计算迭代学习控制 (ILC) 控制率。
输入：JSON 格式字符串，包含以下字段：
  - train_num (int): 当前列车序号
  - platform_num (int): 当前站台序号
  - time_schedule (dict): 时间调度表，包含 TrCir, TimeError, TimeUk
  - c (float, 可选): 客流参数，默认 0.4
  - M (int, 可选): 列车总数，默认 16
  - N (int, 可选): 站台数量，默认 8

输出：JSON 格式，包含 Uik (控制量), uik_full (完整控制向量), elapsed_time (计算耗时) 等字段。

示例输入：
{"train_num": 1, "platform_num": 1, "time_schedule": {"TrCir": {1: 1}, "TimeError": {(1, 9): 5.0}, "TimeUk": {}}, "c": 0.4}"""
)


# 测试代码
if __name__ == "__main__":
    # 初始化晚点记录字典
    delay_dict = {
        (1, 15): 5,  # 列车1在全局车站15晚点5分钟
        (2, 15): 2,  # 列车2在全局车站15晚点2分钟
        (1, 14): 1   # 列车1在全局车站14晚点1分钟
    }
    
    # 测试场景：current_train_id=1, current_global_station_idx=15
    current_train_id = 1
    current_global_station_idx = 15
    
    state_vector = build_state_vector(current_train_id, current_global_station_idx, delay_dict)
    
    print(f"当前列车ID: {current_train_id}")
    print(f"当前全局车站索引: {current_global_station_idx}")
    print(f"状态向量长度: {len(state_vector)}")
    print(f"状态向量: {state_vector}")
    print()
    
    # 详细解释
    print("=== 状态向量解析 ===")
    print(f"第一部分 (前 {15-8}=7 项) - 同站其他列车的晚点时间:")
    for i in range(7):
        print(f"  列车{i+1}在车站{current_global_station_idx}的晚点时间: {state_vector[i]} 分钟")
    
    print(f"\n第二部分 (后 8 项) - 零填充:")
    for i in range(7, 15):
        print(f"  位置{i}: {state_vector[i]}")
    
    print("\n=== 预期结果验证 ===")
    print("第一部分应该包含:")
    print("  - 列车1在车站15: 5分钟 ✓" if state_vector[0] == 5 else "  - 列车1在车站15: 错误 ✗")
    print("  - 列车2在车站15: 2分钟 ✓" if state_vector[1] == 2 else "  - 列车2在车站15: 错误 ✗")
    print("  - 列车3-7在车站15: 0分钟 ✓" if all(state_vector[i] == 0 for i in range(2, 7)) else "  - 列车3-7: 错误 ✗")
    print("\n第二部分应该全部为0:")
    print("  - 后8项全为0 ✓" if all(state_vector[i] == 0 for i in range(7, 15)) else "  - 后8项: 错误 ✗")
    
    # 测试 ILC 控制计算
    print("\n" + "=" * 60)
    print("🧪 测试 ILC 控制计算")
    print("=" * 60)
    
    test_time_schedule = {
        'TrCir': {1: 1, 2: 1},
        'TimeError': {
            (1, 9): 5.0,
            (2, 9): 3.0,
        },
        'TimeUk': {
            (1, 1): 0.5,
        }
    }
    
    ilc_result = compute_ilc_control(
        train_num=1,
        platform_num=1,
        time_schedule=test_time_schedule,
        c=0.4
    )
    
    print(f"\nILC 控制结果:")
    print(f"  控制量 Uik: {ilc_result['Uik']:.4f}")
    print(f"  计算耗时: {ilc_result['elapsed_time']:.6f} 秒")
    print(f"  是否第一圈: {ilc_result['is_first_circle']}")
    
    # 测试调度决策工具
    print("\n" + "=" * 60)
    print("🧪 测试调度决策工具")
    print("=" * 60)
    
    test_input = {
        "dispatcher_input": "列车G101在北京南站因设备故障晚点5分钟，需要迅速处理",
        "delay_info": {"train_number": "G101", "station_name": "北京南站", "delay_minutes": 5}
    }
    
    decision_result = _dispatch_decision_wrapper(json.dumps(test_input))
    print(f"调度决策结果:\n{decision_result}")
