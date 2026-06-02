"""
统一调度服务 — 集成反馈控制、ILC、RMPC 三种算法
输出以"区间运行时间调整"为核心的调度命令
"""
import re
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple  # noqa: F401

from sqlalchemy import and_
from config.database import SessionLocal
from models.train_model import TrainModel
from models.station import Station
from models.delay_record import DelayRecord
from models.dispatch_record import DispatchRecord
from models.feedback import Feedback
from models.fuzzy_membership import FuzzyMembershipFunction

from algorithms.rescheduler import compute_reschedule
from algorithms.ilc_controller import ILCController
from algorithms.rmpc_controller import lmi_solve
from tools.fuzzy_passenger_flow import get_c_from_fuzzy_logic
from tools.index_mapper import (
    parse_command_to_index, STATION_TOPOLOGY,
    N_STATIONS_PER_CIRCLE, NUM_TRAINS
)
from services.timetable_projector import project_timetable
from services.timetable_viz import generate_time_distance_diagram

logger = logging.getLogger(__name__)

# ── 车站邻接关系（确定区间） ──
STATION_NEXT = {
    # 下行方向: 当前站 → 下一站
    ("北京南", "down"): "武清",
    ("武清", "down"): "天津",
    ("天津", "down"): "塘沽",
    ("塘沽", "down"): "滨海",
    ("滨海", "down"): "北京南",
    # 上行方向
    ("滨海", "up"): "塘沽",
    ("塘沽", "up"): "天津",
    ("天津", "up"): "武清",
    ("武清", "up"): "北京南",
    ("北京南", "up"): "滨海",
}

# 默认区间标准运行时间（分钟）
DEFAULT_SECTION_TIME = 10


def get_next_station(station_name: str, direction: str) -> str:
    """获取下一站名称"""
    # 去掉站名中的"下行""上行"后缀
    base = station_name.replace("下行", "").replace("上行", "")
    return STATION_NEXT.get((base, direction), "下一站")


def _extract_section_adjustment(algorithm_result: dict) -> float:
    """从算法结果中安全提取区间调整量（处理标量/列表/数组）"""
    val = algorithm_result.get("adjusted_departure_delay",
          algorithm_result.get("Uik",
          algorithm_result.get("control_signal", 0)))
    if isinstance(val, (list, np.ndarray)):
        val = float(val[0]) if len(val) > 0 else 0.0
    return abs(float(val))


def analyze_intent(text: str) -> Dict[str, Any]:
    """解析调度员意图，选择控制算法"""
    intent = {
        "algorithm": "rmpc",
        "reason": "常规晚点场景，采用鲁棒模型预测控制（RMPC）",
        "is_fast": False,
        "is_surge": False,
    }

    fast_keywords = ["迅速", "快速", "立即", "马上", "紧急", "急"]
    surge_keywords = ["客流突变", "客流激增", "乘客突增", "人流突增", "客流突然"]

    for kw in fast_keywords:
        if kw in text:
            intent["algorithm"] = "feedback"
            intent["reason"] = "检测到紧急关键词，需快速响应，采用反馈控制"
            intent["is_fast"] = True
            break

    for kw in surge_keywords:
        if kw in text:
            intent["algorithm"] = "ilc"
            intent["reason"] = "检测到客流突变关键词，采用迭代学习控制（ILC）"
            intent["is_surge"] = True
            break

    return intent


def build_dispatch_command(
    train_number: str,
    station_name: str,
    delay_minutes: int,
    reason_text: str,
    algorithm_result: Dict[str, Any],
    intent: Dict[str, Any],
    c_value: float,
    direction: str,
    physical_train_idx: int,
    global_station_idx: int,
) -> str:
    """生成以区间运行时间调整为核心的调度命令"""

    algorithm_name = {
        "feedback": "反馈控制 (Feedback Control)",
        "ilc": "迭代学习控制 (ILC)",
        "rmpc": "鲁棒模型预测控制 (RMPC)",
    }.get(intent["algorithm"], intent["algorithm"])

    # 确定下一站
    next_station = get_next_station(station_name, direction)

    # 区间运行时间调整量
    if intent["algorithm"] == "rmpc":
        control_signal = algorithm_result.get("control_signal", 0)
        if isinstance(control_signal, (list, np.ndarray)):
            section_adjustment = abs(float(control_signal[0]))
        else:
            section_adjustment = abs(float(control_signal))
    elif intent["algorithm"] == "ilc":
        section_adjustment = abs(float(algorithm_result.get("Uik", 0)))
    else:
        section_adjustment = abs(float(algorithm_result.get("adjusted_departure_delay", 0)))

    section_adjustment = round(section_adjustment, 1)
    adjusted_time = round(DEFAULT_SECTION_TIME - section_adjustment, 1)

    # 策略描述
    if section_adjustment <= 2:
        strategy_desc = "轻微调整 — 司机正常驾驶即可消化"
        urgent_level = "🟢 低"
    elif section_adjustment <= 5:
        strategy_desc = "适度调整 — 建议适当提速，压缩区间运行时间"
        urgent_level = "🟡 中"
    else:
        strategy_desc = "强制调整 — 需明显提速，注意行车安全"
        urgent_level = "🔴 高"

    # 参数展示
    if intent["algorithm"] == "feedback":
        params = algorithm_result.get("parameters", {})
        formulas = (
            f"g = -(p+q)/[p+q+(c-1)²] = {params.get('g', 'N/A')}\n"
            f"  f = (q+c·p)/[p+q+(c-1)²] = {params.get('f', 'N/A')}\n"
            f"  u = g·x_current + f·x_previous_next\n"
            f"    = ({params.get('g', 'N/A')})×{delay_minutes} + "
            f"({params.get('f', 'N/A')})×{params.get('x_previous_next', 0)}"
        )
        sig = algorithm_result.get("control_signal_u", "N/A")
    elif intent["algorithm"] == "ilc":
        formulas = (
            f"  u_k = u_{k-1} + H1·(yP_{k-1} + F·A·ΔX_k)\n"
            f"  利用上一批次控制率与状态偏差迭代修正"
        )
        sig = algorithm_result.get("Uik", "N/A")
    else:
        formulas = (
            f"  min a  s.t.  LMI半正定约束\n"
            f"  U = K_opt · X （CVXPY/SCS求解）"
        )
        sig = algorithm_result.get("control_signal", [0])
        if isinstance(sig, (list, np.ndarray)):
            sig = round(float(sig[0]), 2)

    # 多车协同建议
    multi_train = ""
    if intent["algorithm"] == "rmpc":
        multi_train = "\n【多车协同调整建议】\n  基于RMPC控制向量，建议关注以下列车在相邻区间的运行时间：\n"
        cs = algorithm_result.get("control_signal", [])
        if isinstance(cs, (list, np.ndarray)) and len(cs) > 1:
            for idx, val in enumerate(cs[:5]):
                if abs(val) > 0.1:
                    multi_train += f"  · 列车#{idx+1} 区间运行时间调整: {abs(round(float(val),1))} 分钟\n"
        multi_train += "  注：以上为模型全局优化建议，请结合实际运行图执行"

    if intent["algorithm"] == "ilc":
        uik_full = algorithm_result.get("uik_full", [])
        if uik_full and len(uik_full) > 1:
            multi_train = "\n【多车协同调整建议】\n  基于ILC控制向量，建议关注以下列车：\n"
            for idx, val in enumerate(uik_full[:5]):
                if abs(val) > 0.01:
                    multi_train += f"  · 列车#{idx+1} 控制量: {round(float(val),3)}\n"

    # ── 拼接最终命令 ──
    command = f"""
╔══════════════════════════════════════════════════╗
║           列车晚点智能调度命令                    ║
╚══════════════════════════════════════════════════╝

【基本信息】
  车次：{train_number}          车站：{station_name}
  晚点：{delay_minutes} 分钟         原因：{reason_text}
  方向：{direction}          时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

【控制策略】
  算法：{algorithm_name}
  选择原因：{intent['reason']}

【模糊客流参数】
  参数 c：{c_value}
  （由当前时段客流模糊推理计算）

【控制公式】
  {formulas}
  控制信号值：{sig}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        区间运行时间调整方案
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  车次 {train_number} | {station_name} → {next_station}{direction}

  标准区间运行时间：{DEFAULT_SECTION_TIME} 分钟
  建议压缩量：      {section_adjustment} 分钟
  调整后运行时间：  {adjusted_time} 分钟

  紧急程度：{urgent_level}
  调度策略：{strategy_desc}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{multi_train}

【执行说明】
  请调度员向 {train_number} 次列车司机下达指令：
  "在 {station_name} 至 {next_station} 区间压缩运行时间 {section_adjustment} 分钟"
"""
    return command.strip()


def unified_process_delay(
    target_train_number: str,
    target_station_name: str,
    delay_minutes: int,
    reason_text: str,
    original_text: str = "",
) -> Tuple[str, str]:
    """
    统一调度处理 — 集成三种控制算法

    流程：
    1. 数据库查询（列车、车站）
    2. 索引映射
    3. 创建晚点记录
    4. 意图分析 → 选择算法
    5. 获取模糊参数 c
    6. 执行选定算法
    7. 时刻表投影
    8. 生成区间运行时间调度命令
    9. 保存调度记录

    返回:
        (command_text, diagram_path) 元组
    """
    logger.info(f"统一调度处理: 车次={target_train_number}, 车站={target_station_name}, 晚点={delay_minutes}分钟")

    db = SessionLocal()
    try:
        # ── 步骤1: 查询列车 ──
        train = db.query(TrainModel).filter(
            TrainModel.train_number == target_train_number
        ).first()

        if not train:
            match = re.search(r'(\d+)', target_train_number)
            if match:
                num = int(match.group())
                if num > 2530:
                    base_num = num - 30
                    base_train_number = f"C{base_num}"
                    logger.info(f"未找到 {target_train_number}，尝试基础车次：{base_train_number}")
                    train = db.query(TrainModel).filter(
                        TrainModel.train_number == base_train_number
                    ).first()

        if not train:
            raise ValueError(f"未找到车次：{target_train_number}")

        logger.info(f"✅ 找到列车: {train.train_number} (ID={train.train_id})")

        # ── 步骤2: 查询车站 & 推断方向 ──
        train_digits_match = re.search(r'(\d+)', target_train_number)
        train_digits = int(train_digits_match.group()) if train_digits_match else 1
        direction = "down" if train_digits % 2 != 0 else "up"

        station = db.query(Station).filter(
            Station.station_name == target_station_name
        ).first()

        if not station:
            base_name = target_station_name.replace("下行", "").replace("上行", "")
            if "站" not in base_name:
                base_name += "站"
            full_station_name = f"{base_name}{'下行' if direction == 'down' else '上行'}"
            logger.info(f"尝试方向拼接：{full_station_name}")
            station = db.query(Station).filter(
                Station.station_name == full_station_name
            ).first()

        if not station:
            raise ValueError(f"未找到车站：{target_station_name}")

        logger.info(f"✅ 找到车站: {station.station_name} (ID={station.station_id})")

        train_id = train.train_id
        station_id = station.station_id

        # ── 步骤3: 索引映射 ──
        command_str = f"{target_train_number}次列车在{target_station_name}"
        try:
            physical_train_idx, global_station_idx = parse_command_to_index(command_str)
        except Exception:
            physical_train_idx, global_station_idx = 1, 1
        logger.info(f"索引: i={physical_train_idx}, J={global_station_idx}")

        # ── 步骤4: 创建晚点记录 ──
        delay_record = DelayRecord(
            train_id=train_id,
            station_id=station_id,
            delay_duration=delay_minutes,
            delay_reason=reason_text,
            is_urgent=1 if ("紧急" in original_text or "急" in original_text) else 0,
            logic_train_id=physical_train_idx,
            logic_station_index=global_station_idx,
            circle_k=(global_station_idx - 1) // N_STATIONS_PER_CIRCLE + 1,
            direction=direction,
        )
        db.add(delay_record)
        db.flush()
        logger.info(f"✅ 晚点记录已创建: delay_id={delay_record.delay_id}")

        # ── 步骤5: 意图分析 → 选择算法 ──
        intent = analyze_intent(original_text or f"{target_train_number}在{target_station_name}因{reason_text}晚点{delay_minutes}分钟")
        logger.info(f"算法选择: {intent['algorithm']} — {intent['reason']}")

        # ── 步骤6: 获取模糊参数 c ──
        try:
            c_value = get_c_from_fuzzy_logic()
            c_source = "fuzzy_logic"
        except Exception:
            latest_fb = db.query(Feedback).order_by(Feedback.created_at.desc()).first()
            if latest_fb and latest_fb.c is not None:
                c_value = latest_fb.c
                c_source = "feedback_table"
            else:
                c_value = 1.0
                c_source = "default"
        logger.info(f"参数 c={c_value} (来源: {c_source})")

        # ── 步骤7: 执行选定算法 ──
        algorithm_result = {}

        if intent["algorithm"] == "feedback":
            # 反馈控制 — 使用现有 compute_reschedule
            algorithm_result = compute_reschedule(train_id, station_id, delay_minutes)
            algorithm_result["algorithm"] = "feedback"

        elif intent["algorithm"] == "ilc":
            # ILC 迭代学习控制
            time_schedule = {
                'TrCir': {physical_train_idx: (global_station_idx - 1) // N_STATIONS_PER_CIRCLE + 1},
                'TimeError': {(physical_train_idx, global_station_idx): float(delay_minutes)},
                'TimeUk': {}
            }
            try:
                controller = ILCController(M=16, N=8)
                ilc_result = controller.compute_control(
                    train_num=physical_train_idx,
                    platform_num=1,
                    time_schedule=time_schedule,
                    c=c_value
                )
                algorithm_result = {
                    "algorithm": "ilc",
                    "Uik": ilc_result.get("Uik", 0),
                    "uik_full": ilc_result.get("uik_full", []),
                    "elapsed_time": ilc_result.get("elapsed_time", 0),
                    "control_signal": ilc_result.get("Uik", 0),
                }
            except Exception as e:
                logger.error(f"ILC计算失败，回退到反馈控制: {e}")
                algorithm_result = compute_reschedule(train_id, station_id, delay_minutes)
                algorithm_result["algorithm"] = "feedback"
                intent["algorithm"] = "feedback"
                intent["reason"] = f"ILC计算失败({str(e)[:50]})，回退至反馈控制"

        else:  # rmpc
            # RMPC 鲁棒模型预测控制
            M, N_rmpc = 18, 14
            x_real = np.zeros(M)
            x_real[0] = float(delay_minutes)
            control_params = {'ckd': 0, 'd': 0.2, 'ckpoint': c_value}
            try:
                u_result = lmi_solve(M, N_rmpc, x_real, control_params)
                algorithm_result = {
                    "algorithm": "rmpc",
                    "control_signal": u_result.tolist() if hasattr(u_result, 'tolist') else list(u_result),
                    "dimensions": {"M": M, "N": N_rmpc},
                    "c_parameter": c_value,
                }
            except Exception as e:
                logger.error(f"RMPC求解失败，回退到反馈控制: {e}")
                algorithm_result = compute_reschedule(train_id, station_id, delay_minutes)
                algorithm_result["algorithm"] = "feedback"
                intent["algorithm"] = "feedback"
                intent["reason"] = f"RMPC求解失败({str(e)[:50]})，回退至反馈控制"

        logger.info(f"✅ 算法执行完成: {intent['algorithm']}")

        # ── 步骤7.5: 时刻表投影 ──
        timetable_summary = ""
        timetable_diagram_path = ""
        try:
            section_adjustment_val = _extract_section_adjustment(algorithm_result)

            snapshot = project_timetable(
                delay_train_idx=physical_train_idx - 1,  # 转0-based
                delay_station_idx=global_station_idx - 1,
                delay_minutes=float(delay_minutes),
                control_signal=section_adjustment_val,
                algorithm=intent["algorithm"],
                c_param=c_value,
                total_circles=3,
            )

            import os as _os
            _os.makedirs("static/output", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            diagram_filename = f"diagram_{target_train_number}_{timestamp}.png"
            diagram_path = f"static/output/{diagram_filename}"
            generate_time_distance_diagram(snapshot, output_path=diagram_path,
                                          title=f"列车运行图 — {intent['algorithm'].upper()}控制",
                                          show_planned=True, show_controlled=True,
                                          show_fcfs=False, dpi=150)
            timetable_diagram_path = f"/static/output/{diagram_filename}"

            timetable_summary = f"""

    【时刻表投影分析】
      FCFS(无控制)总延误: {snapshot.total_delay_fcfs:.1f} min
      受控后总延误:      {snapshot.total_delay_controlled:.1f} min
      延误减少:          {snapshot.delay_reduction():.1f} min ({snapshot.delay_reduction_pct():.1f}%)
      影响列车数:        {snapshot.projection_steps} 站次
      运行图已生成:      {timetable_diagram_path}
    """
            logger.info(f"✅ 时刻表投影完成: 延误减少 {snapshot.delay_reduction():.1f} min")
        except Exception as e:
            logger.warning(f"时刻表投影失败（不影响主流程）: {e}")

        # ── 步骤8: 生成调度命令 ──
        command = build_dispatch_command(
            train_number=target_train_number,
            station_name=station.station_name,
            delay_minutes=delay_minutes,
            reason_text=reason_text,
            algorithm_result=algorithm_result,
            intent=intent,
            c_value=c_value,
            direction=direction,
            physical_train_idx=physical_train_idx,
            global_station_idx=global_station_idx,
        )

        # ── 步骤9: 保存调度记录 ──
        current_time = datetime.now()
        section_adjustment = _extract_section_adjustment(algorithm_result)

        existing_record = db.query(DispatchRecord).filter(
            and_(
                DispatchRecord.train_id == train_id,
                DispatchRecord.station_id == station_id
            )
        ).first()

        if existing_record:
            existing_record.adjustment_value = section_adjustment
            existing_record.command_content = command
            existing_record.created_at = current_time
        else:
            dispatch_record = DispatchRecord(
                train_id=train_id,
                station_id=station_id,
                adjustment_value=section_adjustment,
                command_content=command,
                created_at=current_time,
            )
            db.add(dispatch_record)

        db.commit()
        logger.info("✅ 调度记录已保存")

        # 追加时刻表投影结果
        full_output = command + timetable_summary
        return full_output, timetable_diagram_path

    except Exception as e:
        logger.error(f"❌ 处理失败: {e}", exc_info=True)
        db.rollback()
        raise e
    finally:
        db.close()
