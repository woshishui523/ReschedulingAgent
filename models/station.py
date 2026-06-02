from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from config.database import Base


class Station(Base):
    __tablename__ = "stations"

    station_id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
