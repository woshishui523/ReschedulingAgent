# create_tables.py
from config.database import engine, Base
from models.delay_record import DelayRecord
from models.train_model import TrainModel
from models.station import Station
from models.dispatch_record import DispatchRecord
from models.feedback import Feedback
from models.fuzzy_membership import FuzzyMembershipFunction

# 自动创建所有表
Base.metadata.create_all(bind=engine)

print("数据库表创建成功！")