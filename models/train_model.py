# models/train_model.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from config.database import Base


class TrainModel(Base):
    __tablename__ = "trains"

    train_id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(20), unique=True, nullable=False)
    logic_station_index = Column(Integer, nullable=True, index=True, comment="逻辑车站索引")
    created_at = Column(DateTime, default=datetime.utcnow)
