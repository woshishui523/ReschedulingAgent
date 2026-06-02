# models/dispatch_record.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from datetime import datetime
from config.database import Base


class DispatchRecord(Base):
    __tablename__ = "dispatch_records"

    dispatch_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    train_id = Column(Integer, ForeignKey('trains.train_id'), nullable=False)
    station_id = Column(Integer, ForeignKey('stations.station_id'), nullable=False)
    adjustment_value = Column(Float, nullable=False)
    command_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

