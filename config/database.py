# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 修改为你的MySQL信息
USERNAME = "root"
PASSWORD = "kjj521131"
HOST = "localhost"
PORT = "3306"
DATABASE = "train_dispatch"

# 数据库连接URL
DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# 创建引擎（核心）
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 调试时显示SQL
    pool_pre_ping=True
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建ORM基类（所有表继承它）
Base = declarative_base()