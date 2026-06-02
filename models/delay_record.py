# models/delay_record.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from datetime import datetime
from config.database import Base


class DelayRecord(Base):
    __tablename__ = "delay_records"

    delay_id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey('trains.train_id'), nullable=False)
    station_id = Column(Integer, ForeignKey('stations.station_id'), nullable=False)
    delay_duration = Column(Integer, nullable=False)
    delay_reason = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    is_urgent = Column(Integer, default=0)
    logic_train_id = Column(Integer, nullable=True, index=True, comment="列车逻辑索引 (1 到 N_train)")
    logic_station_index = Column(Integer, nullable=True, index=True, comment="全局唯一站点索引")
    circle_k = Column(Integer, nullable=True, comment="运行圈数")
    direction = Column(String(10), nullable=True, comment="运行方向：down(下行)/up(上行)")
