"""一圈有多少车站即 nnum"""
from sqlalchemy import Column, Integer, String
from config.database import Base


class CircleConfig(Base):
    """环线配置表：一圈的车站数量 nnum"""
    __tablename__ = "circle_configs"

    id = Column(Integer, primary_key=True, index=True)
    line_name = Column(String(50), nullable=False)  # 线路名称
    total_stations = Column(Integer, nullable=False)  # 一圈车站总数 nnum
    description = Column(String(255))
