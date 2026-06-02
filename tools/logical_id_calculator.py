# tools/logical_id_calculator.py
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from config.database import SessionLocal


def calculate_logical_ids(
        train_number: str,
        station_name: str,
        direction: str = None
) -> Dict[str, Any]:
    """
    计算列车和车站的逻辑索引

    输入:
        train_number: 车次号 (例如 "C2501", "C2502")
        station_name: 站名 (例如 "天津南站")
        direction: 方向 ("down" 下行/"up" 上行), 如果为 None 则根据车次奇偶性自动判断

    返回:
        {
            "logic_train_id": 列车逻辑索引 (1 到 N_train),
            "logic_station_index": 全局唯一站点索引，
            "base_station_id": 基础站点编号 (1 到 N_station),
            "circle_k": 运行圈数，
            "direction": 运行方向 ("down"/"up"),
            "train_prefix": 车次前缀 ("C"/"G"等),
            "reversed_station_id": 反向站点编号 (用于上行方向)
        }
    """
    train_prefix, train_digits = extract_train_info(train_number)

    if not train_digits:
        raise ValueError(f"无法从车次号 '{train_number}' 提取数字")

    base_config = get_base_config()
    n_train = base_config.get("train_num", 6)
    n_station = base_config.get("station_num", 8)
    train_start = base_config.get("train_start", 2501)

    logic_train_id, circle_k = calculate_train_logic_index(
        train_digits,
        n_train,
        train_start
    )

    if direction is None:
        direction = "down" if train_digits % 2 == 1 else "up"

    base_station_id = get_base_station_id(station_name)

    reversed_station_id = calculate_reversed_station_id(base_station_id, n_station)

    effective_station_id = reversed_station_id if direction == "up" else base_station_id

    logic_station_index = calculate_global_station_index(
        effective_station_id,
        circle_k,
        n_station
    )

    return {
        "logic_train_id": logic_train_id,
        "logic_station_index": logic_station_index,
        "base_station_id": base_station_id,
        "reversed_station_id": reversed_station_id,
        "effective_station_id": effective_station_id,
        "circle_k": circle_k,
        "direction": direction,
        "n_train": n_train,
        "n_station": n_station,
        "train_prefix": train_prefix
    }


def extract_train_info(train_number: str) -> Tuple[str, int]:
    """
    从车次号中提取前缀和数字部分
    例如："C2501" -> ("C", 2501), "G2501" -> ("G", 2501)
    
    返回:
        (前缀，数字部分)
    """
    prefix = ''
    digits_str = ''
    
    for i, char in enumerate(train_number):
        if char.isalpha():
            prefix += char
        elif char.isdigit():
            digits_str = train_number[i:]
            break
    
    return prefix.upper(), int(digits_str) if digits_str else None


def extract_train_digits(train_number: str) -> int:
    """
    从车次号中提取数字部分 (向后兼容)
    例如："C2501" -> 2501
    """
    _, digits = extract_train_info(train_number)
    return digits


def get_base_config() -> Dict[str, int]:
    """
    从 base_data 表获取全局配置
    返回示例：{"train_num": 6, "station_num": 8, "train_start": 2501}
    """
    db = SessionLocal()
    try:
        from sqlalchemy import text
        query = text("SELECT trainnum, stationnum FROM base_data LIMIT 1")
        result = db.execute(query).fetchone()
        
        config = {
            "train_num": result.trainnum if result else 6,
            "station_num": result.stationnum if result else 8,
            "train_start": 2501
        }
        
        return config
    finally:
        db.close()


def calculate_train_logic_index(
        train_digits: int,
        n_train: int,
        train_start: int = 2501
) -> Tuple[int, int]:
    """
    计算列车逻辑索引和运行圈数

    规则:
    - 每两个连续车次号对应同一辆物理列车（奇数为下行，偶数为上行）
    - Logic_Train_Index = ((车次序号 // 2) % N_train) + 1
    - Circle_K = (车次序号 // (2 * N_train)) + 1

    输入:
        train_digits: 车次数字 (如 2501)
        n_train: 列车底数 (从 base_data.trainnum 查询，如 10)
        train_start: 起始车次数字 (如 2501)

    返回:
        (logic_train_id, circle_k)
        
    示例（当 n_train=10 时）：
        C2501/C2502 -> (1, 1)   # 列车1
        C2503/C2504 -> (2, 1)   # 列车2
        ...
        C2521/C2522 -> (11, 1) -> (1, 2)  # 第2圈的列车1
        C2523/C2524 -> (12, 1) -> (2, 2)  # 第2圈的列车2
    """
    train_sequence = train_digits - train_start

    if train_sequence < 0:
        logic_train_id = ((train_digits // 2) % n_train) + 1
        circle_k = train_digits // (2 * n_train) + 1
    else:
        pair_index = train_sequence // 2
        logic_train_id = (pair_index % n_train) + 1
        circle_k = (pair_index // n_train) + 1

    return logic_train_id, circle_k


def get_base_station_id(station_name: str) -> int:
    """
    根据站名获取基础站点编号 (1 到 N_station)

    标准站序表示例 (下行方向 - 北京南 -> 滨海):
    1  -> 北京南
    2  -> 天津南
    3  -> 沧州西
    4  -> 德州东
    5  -> 济南西
    6  -> 淄博北
    7  -> 潍坊北
    8  -> 滨海
    """
    station_order_map = {
        "北京南": 1,
        "天津南": 2,
        "沧州西": 3,
        "德州东": 4,
        "济南西": 5,
        "淄博北": 6,
        "潍坊北": 7,
        "滨海": 8
    }

    clean_name = station_name.replace("站", "")

    if clean_name in station_order_map:
        return station_order_map[clean_name]

    db = SessionLocal()
    try:
        from models.station import Station
        station = db.query(Station).filter(
            Station.station_name == station_name
        ).first()

        if station:
            return station.station_id
    finally:
        db.close()

    return 1


def calculate_reversed_station_id(base_station_id: int, n_station: int) -> int:
    """
    计算反向站点编号 (用于上行方向)
    
    上行方向 (滨海 -> 北京南) 需要将站点顺序反转:
    - 下行站点 1 (北京南) -> 上行站点 8
    - 下行站点 2 (天津南) -> 上行站点 7
    - ...
    - 下行站点 8 (滨海) -> 上行站点 1
    
    公式：reversed_id = N_station - base_id + 1
    
    示例:
    - 天津南站在下行是 2，在上行变为：8 - 2 + 1 = 7
    - 北京南站在下行是 1，在上行变为：8 - 1 + 1 = 8
    """
    return n_station - base_station_id + 1


def calculate_global_station_index(
        base_station_id: int,
        circle_k: int,
        n_station: int
) -> int:
    """
    计算全局唯一站点索引

    公式：Global_Station_Index = S + (Circle_K - 1) × N_station

    例如:
    - 第 1 圈，站点 2: 2 + (1-1)×8 = 2
    - 第 2 圈，站点 2: 2 + (2-1)×8 = 10
    - 第 3 圈，站点 2: 2 + (3-1)×8 = 18
    
    注意:
    - 下行方向使用原始站点编号
    - 上行方向使用反转后的站点编号
    """
    return base_station_id + (circle_k - 1) * n_station


def find_neighbor_trains(
        logic_train_id: int,
        n_train: int,
        include_self: bool = False
) -> list:
    """
    查找相邻列车逻辑 ID

    考虑循环特性:
    - 列车 1 的左邻居是列车 N_train
    - 列车 N_train 的右邻居是列车 1
    """
    neighbors = []

    left = (logic_train_id - 2) % n_train + 1
    right = logic_train_id % n_train + 1

    neighbors.append(left)

    if include_self:
        neighbors.append(logic_train_id)

    neighbors.append(right)

    return neighbors


def find_neighbor_stations(
        logic_station_index: int,
        n_station: int,
        include_self: bool = False
) -> list:
    """
    查找相邻站点逻辑索引

    注意：这里只处理同一圈次内的相邻
    跨圈次的相邻需要结合时间窗口判断
    """
    circle_k = (logic_station_index - 1) // n_station + 1
    position_in_circle = (logic_station_index - 1) % n_station + 1

    if position_in_circle > 1:
        prev_index = logic_station_index - 1
    else:
        prev_index = logic_station_index - 1

    if position_in_circle < n_station:
        next_index = logic_station_index + 1
    else:
        next_index = logic_station_index + 1

    neighbors = []

    if prev_index >= 1:
        neighbors.append(prev_index)

    if include_self:
        neighbors.append(logic_station_index)

    neighbors.append(next_index)

    return neighbors
