import re
import logging
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from config.database import SessionLocal
from models.delay_record import DelayRecord
from models.train_model import TrainModel
from models.station import Station
from models.dispatch_record import DispatchRecord
from algorithms.rescheduler import compute_reschedule
from tools.logical_id_calculator import calculate_logical_ids, get_base_config
from tools.index_mapper import parse_command_to_index

logger = logging.getLogger(__name__)


def process_delay_event(
    target_train_number: str,
    target_station_name: str,
    delay_minutes: int,
    reason_text: str
) -> str:
    """
    处理列车晚点事件并生成调度命令
    
    参数:
        target_train_number: 车次号 (例："C2503")
        target_station_name: 车站名称 (例："北京南站")
        delay_minutes: 晚点分钟数
        reason_text: 晚点原因
    
    返回:
        生成的调度命令字符串
    
    异常:
        ValueError: 当找不到列车或车站信息时
    """
    logger.info(f"开始处理晚点事件: 车次={target_train_number}, 车站={target_station_name}, 晚点={delay_minutes}分钟")
    db = SessionLocal()
    try:
        logger.info("步骤 1: 查询列车信息...")
        train = db.query(TrainModel).filter(
            TrainModel.train_number == target_train_number
        ).first()
        
        # 如果没找到，尝试根据复用规律查找基础车次（例如 C2533 -> C2503）
        if not train:
            match = re.search(r'(\d+)', target_train_number)
            if match:
                num = int(match.group())
                # 如果车次号大于 2530，说明是复用或第二圈以后的，尝试减去 30
                if num > 2530:
                    base_num = num - 30
                    base_train_number = f"C{base_num}"
                    logger.info(f"⚠️ 未找到 {target_train_number}，尝试查询其对应的基础车次：{base_train_number}")
                    train = db.query(TrainModel).filter(
                        TrainModel.train_number == base_train_number
                    ).first()

        if not train:
            logger.error(f"未找到车次: {target_train_number}")
            raise ValueError(f"未找到车次：{target_train_number}")
        
        logger.info(f"✅ 找到列车: train_id={train.train_id}, train_number={train.train_number}")

        # 提取车次号中的数字，奇偶判断方向用
        train_digits_match = re.search(r'(\d+)', target_train_number)
        train_digits = int(train_digits_match.group()) if train_digits_match else 1

        logger.info("步骤 2: 查询车站信息...")
        
        # 1. 首先尝试精确匹配
        station = db.query(Station).filter(
            Station.station_name == target_station_name
        ).first()
        
        # 2. 如果没找到，且输入中包含“下行”或“上行”，尝试直接匹配
        if not station:
            direction_hint = ""
            if "下行" in target_station_name:
                direction_hint = "下行"
            elif "上行" in target_station_name:
                direction_hint = "上行"
            
            # 3. 如果输入没带方向，根据车次号奇偶性自动推断方向并拼接
            if not direction_hint:
                direction_hint = "下行" if train_digits % 2 != 0 else "上行"
            
            # 4. 使用推断出的方向再次查询 (例如：天津站 + 下行 -> 天津站下行)
            if direction_hint:
                # 确保名字里已经有“站”字，如果没有则补上
                base_name = target_station_name.replace("下行", "").replace("上行", "")
                if "站" not in base_name:
                    base_name += "站"
                
                full_station_name = f"{base_name}{direction_hint}"
                logger.info(f"⚠️ 精确匹配失败，尝试根据方向自动拼接站名：{full_station_name}")
                
                station = db.query(Station).filter(
                    Station.station_name == full_station_name
                ).first()

        if not station:
            logger.error(f"未找到车站: {target_station_name}")
            raise ValueError(f"未找到车站：{target_station_name}")
        
        logger.info(f"✅ 找到车站: station_id={station.station_id}, station_name={station.station_name}")
        
        train_id = train.train_id
        station_id = station.station_id
        current_time = datetime.now()
        
        logger.info("步骤 3: 计算仿真模型索引 (i, J_global)...")
        # 构造一个简单的命令字符串传入解析器
        command_str = f"{target_train_number}次列车在{target_station_name}"
        try:
            physical_train_idx, global_station_idx = parse_command_to_index(command_str)
            logger.info(f"✅ 索引映射成功: 物理列车索引 i={physical_train_idx}, 全局车站索引 J={global_station_idx}")
        except Exception as e:
            logger.warning(f"索引映射失败，回退到旧逻辑: {e}")
            # 如果新映射失败，可以保留旧逻辑作为备份
            logical_ids = calculate_logical_ids(target_train_number, target_station_name)
            physical_train_idx = logical_ids["logic_train_id"]
            global_station_idx = logical_ids["logic_station_index"]

        logger.info("步骤 4: 创建晚点记录...")
        delay_record = DelayRecord(
            train_id=train_id,
            station_id=station_id,
            delay_duration=delay_minutes,
            delay_reason=reason_text,
            is_urgent=0,
            logic_train_id=physical_train_idx,  # 使用新的物理列车索引 i
            logic_station_index=global_station_idx, # 使用新的全局车站索引 J
            circle_k=(global_station_idx - 1) // 8 + 1, # 根据全局索引反推圈数 k
            direction="down" if train_digits % 2 != 0 else "up"
        )
        db.add(delay_record)
        db.flush()
        logger.info(f"✅ 晚点记录已创建: delay_record_id={delay_record.delay_id}")
        
        logger.info("步骤 5: 执行重调度算法...")
        # 注意：这里可能需要修改 compute_reschedule 以支持新的索引逻辑
        reschedule_result = compute_reschedule(train_id, station_id, delay_minutes)
        logger.info(f"✅ 重调度计算完成: {reschedule_result}")
        
        final_adjustment = reschedule_result["adjusted_departure_delay"]
        control_signal_u = reschedule_result["control_signal_u"]
        previous_train_influence = reschedule_result["previous_train_influence"]
        strategy = reschedule_result["reschedule_strategy"]
        
        logger.info("步骤 6: 生成调度命令...")
        command_content = (
            f"【调度命令】车次 {target_train_number} 在 {target_station_name} "
            f"因 {reason_text} 晚点 {delay_minutes} 分钟。\n"
            f"经重调度控制算法测算：\n"
            f"  • 本列车晚点影响：{delay_minutes} 分钟\n"
            f"  • 前续列车影响：{previous_train_influence} 分钟\n"
            f"  • 综合控制信号值：{control_signal_u} 分钟\n"
            f"  • 建议调整量：{final_adjustment} 分钟\n"
            f"  • 调度策略：{strategy}\n"
            f"请调度员据此执行。"
        )
        
        logger.info("步骤 7: 保存调度记录...")
        existing_record = db.query(DispatchRecord).filter(
            and_(
                DispatchRecord.train_id == train_id,
                DispatchRecord.station_id == station_id
            )
        ).first()
        
        if existing_record:
            logger.info(f"发现已存在的调度记录 (dispatch_id={existing_record.dispatch_id})，执行更新操作")
            existing_record.adjustment_value = final_adjustment
            existing_record.command_content = command_content
            existing_record.created_at = current_time
            logger.info("✅ 调度记录已更新")
        else:
            logger.info("创建新的调度记录")
            dispatch_record = DispatchRecord(
                train_id=train_id,
                station_id=station_id,
                adjustment_value=final_adjustment,
                command_content=command_content,
                created_at=current_time
            )
            db.add(dispatch_record)
            logger.info("✅ 调度记录已创建")
        
        logger.info("步骤 8: 提交事务...")
        db.commit()
        logger.info("✅ 所有操作成功完成！")
        
        return command_content
        
    except Exception as e:
        logger.error(f"❌ 处理失败，回滚事务: {e}", exc_info=True)
        db.rollback()
        raise e
    finally:
        logger.info("关闭数据库会话")
        db.close()
