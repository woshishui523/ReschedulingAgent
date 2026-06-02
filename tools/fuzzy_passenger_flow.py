# tools/fuzzy_passenger_flow.py
"""
基于时间的客流模糊推理工具
根据当前时间计算客流隶属度，并映射为参数 c
"""
from sqlalchemy import func
from config.database import SessionLocal
from models.fuzzy_membership import FuzzyMembershipFunction
from datetime import datetime

# 客流概率权重配置
PASSENGER_FLOW_WEIGHTS = {
    'NB': 0.1,  # 早间低峰
    'NM': 0.3,  # 上午平峰
    'NS': 0.2,  # 中午平峰
    'PS': 0.15,  # 下午次高峰
    'PM': 0.3,  # 晚高峰
    'PB': 0.1  # 夜间低峰
}


def calculate_membership(x: float, left: float, peak: float, right: float) -> float:
    """
    计算三角/肩形隶属度函数的隶属度值

    参数:
        x: 输入值（当前时间，小时）
        left: 左边界
        peak: 峰值点
        right: 右边界

    返回:
        隶属度值 [0, 1]
    """
    if x <= left or x >= right:
        return 0.0

    if left == peak:
        # 左肩形函数（如 NB）
        if x <= peak:
            return 1.0
        else:
            return (right - x) / (right - peak)

    elif peak == right:
        # 右肩形函数（如 PB）
        if x >= peak:
            return 1.0
        else:
            return (x - left) / (peak - left)

    else:
        # 标准三角形函数
        if x <= peak:
            return (x - left) / (peak - left)
        else:
            return (right - x) / (right - peak)


def get_current_hour() -> float:
    """获取当前时间的小时数（含小数）"""
    now = datetime.now()
    return now.hour + now.minute / 60.0


def query_fuzzy_memberships(current_hour: float = None) -> dict:
    """
    查询当前时间对所有模糊集的隶属度

    参数:
        current_hour: 当前时间（小时），默认为当前系统时间

    返回:
        字典 {label: membership_degree}
    """
    db = SessionLocal()
    try:
        if current_hour is None:
            current_hour = get_current_hour()

        # 确保时间在有效范围内
        current_hour = max(6.0, min(22.0, current_hour))

        # 查询所有隶属度函数
        memberships = db.query(FuzzyMembershipFunction).all()

        result = {}
        for mf in memberships:
            degree = calculate_membership(
                current_hour,
                mf.point_left,
                mf.point_peak,
                mf.point_right
            )
            result[mf.label] = degree

        return result

    finally:
        db.close()


def calculate_passenger_flow_probability(memberships: dict = None, current_hour: float = None) -> float:
    """
    计算客流概率期望值

    参数:
        memberships: 隶属度字典，如果为None则自动查询
        current_hour: 当前时间（小时）

    返回:
        客流概率值 [0, 1]
    """
    if memberships is None:
        memberships = query_fuzzy_memberships(current_hour)

    # 加权求和计算期望
    probability = 0.0
    for label, weight in PASSENGER_FLOW_WEIGHTS.items():
        if label in memberships:
            probability += memberships[label] * weight

    # 归一化（确保在合理范围内）
    total_membership = sum(memberships.values())
    if total_membership > 0:
        probability = probability / total_membership if total_membership != 1 else probability

    return round(probability, 4)


def map_probability_to_c(probability: float) -> float:
    """
    将客流概率映射为控制参数 c

    映射策略:
    - 低客流 (0-0.15): c = 1.2 (宽松调整)
    - 中低客流 (0.15-0.25): c = 1.0 (标准调整)
    - 中等客流 (0.25-0.35): c = 0.8 (适度收紧)
    - 中高客流 (0.35-0.45): c = 0.6 (较紧调整)
    - 高客流 (>0.45): c = 0.5 (严格调整)

    参数:
        probability: 客流概率 [0, 1]

    返回:
        参数 c 的值
    """
    if probability <= 0.15:
        c = 1.2
    elif probability <= 0.25:
        # 线性插值
        c = 1.2 - (probability - 0.15) * (1.2 - 1.0) / (0.25 - 0.15)
    elif probability <= 0.35:
        c = 1.0 - (probability - 0.25) * (1.0 - 0.8) / (0.35 - 0.25)
    elif probability <= 0.45:
        c = 0.8 - (probability - 0.35) * (0.8 - 0.6) / (0.45 - 0.35)
    else:
        c = 0.6 - (probability - 0.45) * (0.6 - 0.5) / (1.0 - 0.45)

    return round(c, 4)


def get_c_from_fuzzy_logic(current_hour: float = None) -> float:
    """
    一站式接口：根据当前时间通过模糊推理获取参数 c

    参数:
        current_hour: 当前时间（小时），默认使用系统时间

    返回:
        参数 c 的值
    """
    # 1. 查询隶属度
    memberships = query_fuzzy_memberships(current_hour)

    # 2. 计算客流概率
    probability = calculate_passenger_flow_probability(memberships)

    # 3. 映射为参数 c
    c = map_probability_to_c(probability)

    return c


if __name__ == "__main__":
    # 测试示例
    print("=== 模糊客流推理测试 ===\n")

    test_hours = [6.0, 9.5, 13.0, 17.5, 20.5, 22.0]

    for hour in test_hours:
        memberships = query_fuzzy_memberships(hour)
        probability = calculate_passenger_flow_probability(memberships)
        c = map_probability_to_c(probability)

        print(f"时间: {hour:5.1f}h")
        print(f"  隶属度: {memberships}")
        print(f"  客流概率: {probability:.4f}")
        print(f"  参数 c: {c:.4f}\n")
