# models/train_model.py
from sqlalchemy import Column, Integer, String
from config.database import Base


class TrainModel(Base):
    """列车型号表：存放列车编号 m 和对应的圈数 c"""
    __tablename__ = "train_models"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(20), unique=True, nullable=False)  # 车次号，如 G123
    model_code = Column(Integer, nullable=False)  # 列车型号编号 m
    circle_count = Column(Integer, nullable=False)  # 圈数 c
