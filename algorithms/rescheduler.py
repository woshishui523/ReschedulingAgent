import logging  # <--- 1. 导入 logging 模块

# 2. 初始化 logger 对象
logger = logging.getLogger(__name__)

def compute_reschedule(train_id, station_id, delay_minutes):
    """
    基于重调度控制信号的调度算法
    控制信号公式：u_{k}^{i} = g * x_{k}^{i} + f * x_{k+1}^{i-1}
    
    增益参数计算公式：
        g = -(p + q) / [p + q + (c - 1)^2]
        f = (q + c * p) / [p + q + (c - 1)^2]
    
    参数 c 的动态获取：
        - 优先从 fuzzy_membership_functions 表通过模糊推理计算
        - 如果没有模糊函数表，则从 feedback 表获取
        - 最后使用默认值 1.0
    
    输入:
        train_id: 列车 ID (数据库主键，1和2对应列车1，3和4对应列车2...)
        station_id: 车站 ID
        delay_minutes: 晚点时间
    输出:
        调度调整量
    """
    from sqlalchemy import and_
    from config.database import SessionLocal
    from models.train_model import TrainModel
    from models.station import Station
    from models.delay_record import DelayRecord
    from models.feedback import Feedback
    from datetime import datetime, timedelta
    from tools.neighbor_query_tool import query_neighbor_delay_records
    from tools.logical_id_calculator import find_neighbor_trains, get_base_config
    from tools.fuzzy_passenger_flow import get_c_from_fuzzy_logic
    from tools.index_mapper import N_STATIONS_PER_CIRCLE
    
    db = SessionLocal()
    try:
        # 从数据库获取反馈控制参数 p, q
        latest_feedback = db.query(Feedback).order_by(
            Feedback.created_at.desc()
        ).first()
        
        if latest_feedback:
            p = latest_feedback.p
            q = latest_feedback.q
        else:
            # 默认值（如果没有配置）
            p = 0.5
            q = 0.5
        
        # 动态获取参数 c：优先使用模糊推理，否则从 feedback 表或默认值
        try:
            c = get_c_from_fuzzy_logic()
            c_source = "fuzzy_logic"
        except Exception as e:
            # 如果模糊推理失败，降级到 feedback 表
            if latest_feedback and latest_feedback.c is not None:
                c = latest_feedback.c
                c_source = "feedback_table"
            else:
                c = 1.0
                c_source = "default"
        
        # 计算控制增益参数 g 和 f
        denominator = p + q + (c - 1) ** 2
        
        if denominator == 0:
            raise ValueError(f"分母为零：p={p}, q={q}, c={c}，无法计算控制增益")
        
        g = -(p + q) / denominator
        f = (q + c * p) / denominator
        
        # 获取当前列车在当前车站的晚点量 x_{k}^{i}
        x_current = delay_minutes
        
        # --- 重构：基于新索引逻辑查找相邻列车影响 ---
        
        # 获取当前列车的最新逻辑记录（包含我们新计算的 logic_train_id 和 logic_station_index）
        latest_record = db.query(DelayRecord).filter(
            DelayRecord.train_id == train_id
        ).order_by(DelayRecord.created_at.desc()).first()
        
        x_previous_next = 0
        if latest_record and latest_record.logic_train_id and latest_record.logic_station_index:
            # i: 物理列车索引 (1-15), J: 全局车站索引
            current_i = latest_record.logic_train_id
            current_J = latest_record.logic_station_index
            
            # 1. 确定前续列车索引 (i-1)，考虑车底的循环
            from tools.index_mapper import NUM_TRAINS
            prev_i = (current_i - 2) % NUM_TRAINS + 1
            
            # 2. 确定下一个全局车站索引 (J+1)
            # 在闭环模型中，下一站就是 J+1
            next_J = current_J + 1
            
            logger.info(f"正在查询相邻影响: 前续列车 ID={prev_i}, 下一站全局索引={next_J}")
            
            # 3. 在数据库中精确查找 x_{i-1, J+1}
            # 我们需要找到物理列车为 prev_i，且全局车站索引为 next_J 的晚点记录
            time_window = timedelta(hours=2)
            current_time = datetime.now()
            start_time = current_time - time_window
            end_time = current_time + time_window
            
            # 注意：这里需要先在 TrainModel 中找到所有属于 prev_i 的车次号对应的 train_id
            # 简化处理：假设我们在 index_mapper 中有一个反向映射，或者我们直接查 DelayRecord
            # 因为 DelayRecord 现在存的是 logic_train_id (即 physical index)
            
            neighbor_records = db.query(DelayRecord).filter(
                and_(
                    DelayRecord.logic_train_id == prev_i,
                    DelayRecord.logic_station_index == next_J,
                    DelayRecord.created_at >= start_time,
                    DelayRecord.created_at <= end_time
                )
            ).all()
            
            if neighbor_records:
                x_previous_next = max(r.delay_duration for r in neighbor_records)
                logger.info(f"找到相邻晚点记录，影响值: {x_previous_next}")
        else:
            logger.warning("未找到当前列车的逻辑索引记录，无法计算相邻影响，默认设为 0")
        
        # 应用重调度控制信号公式: u = g * x_current + f * x_previous_next
        u = g * x_current + f * x_previous_next
        
        # 策略选择
        if u <= 3:
            strategy = "轻微调整，维持正常运行"
            adjustment = 0
        elif u <= 10:
            strategy = "适度调整，压缩停站时间"
            adjustment = u * 0.5
        else:
            strategy = "强制调整，延后发车 + 路径优化"
            adjustment = u * 0.8
        
        result = {
            "train_id": train_id,
            "logic_train_id": latest_record.logic_train_id if latest_record else None,
            "logic_station_index": latest_record.logic_station_index if latest_record else None,
            "station_id": station_id,
            "original_delay": delay_minutes,
            "previous_train_influence": x_previous_next,
            "control_signal_u": round(u, 2),
            "adjusted_departure_delay": round(adjustment, 2),
            "reschedule_strategy": strategy,
            "parameters": {
                "g": round(g, 4),
                "f": round(f, 4),
                "p": p,
                "q": q,
                "c": c,
                "x_current": x_current,
                "x_previous_next": x_previous_next
            }
        }
        
        return result
        
    finally:
        db.close()
