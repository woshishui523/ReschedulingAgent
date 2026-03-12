from sqlalchemy import Column, Integer, String
from config.database import Base


class StationInfo(Base):
    """车站信息表：存放车站编号 n"""
    __tablename__ = "station_infos"

    station_id = Column(Integer, primary_key=True, index=True)
    station_name = Column(String(50), nullable=False)  # 车站名称
    station_code = Column(Integer, nullable=False, unique=True)  # 车站编号 n
