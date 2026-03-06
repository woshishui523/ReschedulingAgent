# models/delay_record.py
from sqlalchemy import Column, Integer, String
from config.database import Base

class DelayRecord(Base):
    __tablename__ = "delay_records"  # 对应MySQL表名

    delay_id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer)
    station_id = Column(Integer)
    delay_duration = Column(Integer)
    delay_reason = Column(String(255))