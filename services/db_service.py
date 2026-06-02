# services/db_service.py
from config.database import SessionLocal
from models.delay_record import DelayRecord
from models.train_model import TrainModel
from models.station import Station
from tools.logical_id_calculator import calculate_logical_ids


def add_delay_record_with_logic(
    train_number: str,
    station_name: str,
    duration: int,
    reason: str,
    is_urgent: int = 0
):
    """
    保存晚点记录（使用逻辑索引）
    
    输入:
        train_number: 车次号 (如"G2501")
        station_name: 站名 (如"天津南站")
        duration: 晚点时长 (分钟)
        reason: 晚点原因
        is_urgent: 是否紧急
    
    返回:
        插入的记录对象
    """
    db = SessionLocal()
    try:
        # 1. 计算逻辑索引
        logical_ids = calculate_logical_ids(train_number, station_name)
        
        # 2. 获取原始的 train_id 和 station_id
        train = db.query(TrainModel).filter(
            TrainModel.train_number == train_number
        ).first()
        
        station = db.query(Station).filter(
            Station.station_name == station_name
        ).first()
        
        if not train or not station:
            raise ValueError(f"列车 {train_number} 或车站 {station_name} 不存在")
        
        # 3. 创建记录
        record = DelayRecord(
            train_id=train.train_id,
            station_id=station.station_id,
            delay_duration=duration,
            delay_reason=reason,
            is_urgent=is_urgent,
            logic_train_id=logical_ids["logic_train_id"],
            logic_station_index=logical_ids["logic_station_index"],
            circle_k=logical_ids["circle_k"],
            direction=logical_ids["direction"]
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return record
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def add_delay_record(train_id, station_id, duration, reason, is_urgent=0):
    """
    旧版本：向后兼容
    建议迁移到 add_delay_record_with_logic
    """
    db = SessionLocal()
    try:
        record = DelayRecord(
            train_id=train_id,
            station_id=station_id,
            delay_duration=duration,
            delay_reason=reason,
            is_urgent=is_urgent
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    finally:
        db.close()


# 查询所有晚点记录
def get_all_delay_records():
    db = SessionLocal()
    try:
        return db.query(DelayRecord).all()
    finally:
        db.close()


# 查询最新的晚点记录
def get_latest_delay_record():
    db = SessionLocal()
    try:
        return db.query(DelayRecord).order_by(DelayRecord.delay_id.desc()).first()
    finally:
        db.close()


# 查询列车信息
def get_train_by_number(train_number: str):
    db = SessionLocal()
    try:
        return db.query(TrainModel).filter(TrainModel.train_number == train_number).first()
    finally:
        db.close()


# 查询车站信息
def get_station_by_name(station_name: str):
    db = SessionLocal()
    try:
        return db.query(Station).filter(Station.station_name == station_name).first()
    finally:
        db.close()
