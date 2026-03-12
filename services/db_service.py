# services/db_service.py
from config.database import SessionLocal
from models.delay_record import DelayRecord

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
