# services/db_service.py
from config.database import SessionLocal
from models.delay_record import DelayRecord
from models.train_model import TrainModel
from models.station import Station

# 插入数据（对应你智能体）
def add_delay_record(train_id, station_id, duration, reason, is_urgent=0):
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
