# create_tables.py
from config.database import engine, Base
from models.delay_record import DelayRecord

# 自动创建所有表
Base.metadata.create_all(bind=engine)

print("数据库表创建成功！")