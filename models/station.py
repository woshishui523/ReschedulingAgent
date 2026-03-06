from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Station(Base):
    __tablename__ = "stations"

    station_id = Column(Integer, primary_key=True, autoincrement=True)
    station_code = Column(String(10), unique=True, nullable=False)
    station_name = Column(String(50), nullable=False)
    station_type = Column(String(20))