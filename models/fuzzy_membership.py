# models/fuzzy_membership.py
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from config.database import Base


class FuzzyMembershipFunction(Base):
    """模糊隶属度函数表"""
    __tablename__ = "fuzzy_membership_functions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(10), nullable=False, comment="语言变量标签: NB, NM, NS, PS, PM, PB")
    point_left = Column(Float, nullable=False, comment="左边界点（小时）")
    point_peak = Column(Float, nullable=False, comment="峰值点（小时）")
    point_right = Column(Float, nullable=False, comment="右边界点（小时）")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<FuzzyMembershipFunction(label={self.label}, left={self.point_left}, peak={self.point_peak}, right={self.point_right})>"
