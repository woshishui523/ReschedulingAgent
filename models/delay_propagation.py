from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from config.database import Base


class DelayPropagation(Base):
    """晚点传播表：存储晚点量及传播关系"""
    __tablename__ = "delay_propagations"

    id = Column(Integer, primary_key=True, index=True)
    train_model_code = Column(Integer, nullable=False)  # 列车型号编号 m
    station_code = Column(Integer, nullable=False)  # 车站编号 n
    circle_offset = Column(Integer, default=0)  # 圈数偏移 c*nnum
    delay_amount = Column(Float, nullable=False)  # 晚点量
    adjustment_amount = Column(Float, default=0)  # 调整量
    adjacent_train_delay = Column(Float, default=0)  # 相邻列车晚点
    adjacent_station_delay = Column(Float, default=0)  # 相邻车站晚点
    created_at = Column(DateTime, default=datetime.now)
