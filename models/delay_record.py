# models/delay_record.py
from sqlalchemy import Column, Integer, String
from config.database import Base

class DelayRecord(Base):
    __tablename__ = "delay_records"  # 对应 MySQL 表名

    delay_id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer)
    station_id = Column(Integer)
    delay_duration = Column(Integer)
    delay_reason = Column(String(255))
    is_urgent = Column(Integer, default=0)  # 是否紧急：0-不紧急，1-紧急
