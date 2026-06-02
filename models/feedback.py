from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime
from config.database import Base


class Feedback(Base):
    """反馈控制参数表：存储 p 和 q 参数"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    p = Column(Float, nullable=False, comment="反馈控制参数 p")
    q = Column(Float, nullable=False, comment="反馈控制参数 q")
    c = Column(Float, nullable=True, default=1.0, comment="控制参数 c")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    description = Column(String(255), nullable=True, comment="参数说明")
