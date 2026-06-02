# database/seed_data.py
"""
种子数据脚本：初始化 trains 和 stations 表的基础数据
"""
from config.database import SessionLocal, engine, Base
from models.train_model import TrainModel
from models.station import Station
from models.feedback import Feedback
from models.fuzzy_membership import FuzzyMembershipFunction


def seed_trains():
    """根据 index_mapper.py 的车底映射规律插入列车数据"""
    db = SessionLocal()
    try:
        existing = db.query(TrainModel).count()
        if existing > 0:
            print(f"ℹ️  trains 表已有 {existing} 条记录，跳过插入")
            return

        # 生成 15 个车底 × 6 个车次号 = 90 条记录
        train_numbers = []
        for k in range(1, 16):
            base_odd = 2 * k - 1
            base_even = 2 * k
            train_numbers.extend([
                f"C25{base_odd:02d}", f"C25{base_even:02d}",
                f"C25{base_odd + 30:02d}", f"C25{base_even + 30:02d}",
                f"C25{base_odd + 60:02d}", f"C25{base_even + 60:02d}",
            ])

        for tn in train_numbers:
            db.add(TrainModel(train_number=tn))

        db.commit()
        print(f"✅ 已插入 {len(train_numbers)} 条列车记录")
    finally:
        db.close()


def seed_stations():
    """插入车站数据（基于两个索引系统共用的站名）"""
    db = SessionLocal()
    try:
        existing = db.query(Station).count()
        if existing > 0:
            print(f"ℹ️  stations 表已有 {existing} 条记录，跳过插入")
            return

        # 基于 index_mapper.py 的拓扑：北京南、武清、天津、塘沽、滨海
        # 带上下行方向的站名（用于 delay_service 的方向匹配逻辑）
        topology_stations = [
            "北京南站", "北京南站下行", "北京南站上行",
            "武清站下行", "武清站上行",
            "天津站下行", "天津站上行",
            "塘沽站下行", "塘沽站上行",
            "滨海站", "滨海站下行", "滨海站上行",
        ]

        # 基于 logical_id_calculator.py 的站名（用于向后兼容）
        extra_stations = [
            "天津南站", "沧州西站", "德州东站",
            "济南西站", "淄博北站", "潍坊北站",
        ]

        all_stations = topology_stations + extra_stations
        for name in all_stations:
            db.add(Station(station_name=name))

        db.commit()
        print(f"✅ 已插入 {len(all_stations)} 条车站记录")
    finally:
        db.close()


def seed_feedback():
    """插入默认反馈控制参数"""
    db = SessionLocal()
    try:
        existing = db.query(Feedback).count()
        if existing > 0:
            print(f"ℹ️  feedback 表已有 {existing} 条记录，跳过插入")
            return

        db.add(Feedback(p=0.5, q=0.5, c=1.0, description="默认反馈控制参数"))
        db.commit()
        print("✅ 已插入默认反馈控制参数")
    finally:
        db.close()


def seed_fuzzy_rules():
    """插入默认模糊隶属度函数（按时间划分客流）"""
    db = SessionLocal()
    try:
        existing = db.query(FuzzyMembershipFunction).count()
        if existing > 0:
            print(f"ℹ️  fuzzy_membership_functions 表已有 {existing} 条记录，跳过插入")
            return

        rules = [
            # label, left, peak, right (小时)
            ("NB", 5.0, 6.0, 8.0),    # 早间低峰 5-8h
            ("NM", 7.0, 9.0, 11.0),   # 上午平峰 7-11h
            ("NS", 10.0, 13.0, 15.0),  # 中午平峰 10-15h
            ("PS", 14.0, 16.0, 18.0),  # 下午次高峰 14-18h
            ("PM", 16.0, 18.0, 20.0),  # 晚高峰 16-20h
            ("PB", 19.0, 22.0, 24.0),  # 夜间低峰 19-24h
        ]
        for label, left, peak, right in rules:
            db.add(FuzzyMembershipFunction(
                label=label,
                point_left=left,
                point_peak=peak,
                point_right=right
            ))

        db.commit()
        print("✅ 已插入 6 条模糊隶属度函数")
    finally:
        db.close()


def seed_all():
    """一键初始化所有种子数据"""
    print("=" * 60)
    print("🔧 初始化数据库种子数据")
    print("=" * 60)

    # 先确保表存在
    from models.delay_record import DelayRecord
    from models.train_model import TrainModel
    from models.station import Station
    from models.dispatch_record import DispatchRecord
    from models.feedback import Feedback
    from models.fuzzy_membership import FuzzyMembershipFunction
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表检查/创建完成")

    seed_trains()
    seed_stations()
    seed_feedback()
    seed_fuzzy_rules()

    print("=" * 60)
    print("✅ 所有种子数据初始化完成")
    print("=" * 60)


if __name__ == "__main__":
    seed_all()
