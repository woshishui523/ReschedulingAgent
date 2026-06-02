# tools/neighbor_query_tool.py
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.delay_record import DelayRecord
from datetime import datetime, timedelta
from tools.logical_id_calculator import find_neighbor_trains, find_neighbor_stations


def query_neighbor_delay_records(
        logic_train_id: int,
        logic_station_index: int,
        n_train: int,
        n_station: int,
        time_window_hours: float = 2.0
) -> dict:
    """
    查询相邻列车在相邻车站的晚点记录

    时空临近条件:
    1. 列车相邻：logic_train_id 为 Target_ID-1 和 Target_ID+1 (考虑循环)
    2. 车站相邻：logic_station_index 为 Target_Index-1 和 Target_Index+1
    3. 时间窗口：前后 2 小时

    返回:
        {
            "total_neighbors": 满足条件的记录数，
            "aggregated_delay": 聚合晚点时间和，
            "records": [详细记录列表]
        }
    """
    db = SessionLocal()
    try:
        # 获取相邻列车 ID
        neighbor_trains = find_neighbor_trains(logic_train_id, n_train, include_self=False)

        # 获取相邻站点索引
        neighbor_stations = find_neighbor_stations(logic_station_index, n_station, include_self=False)

        # 时间窗口
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=time_window_hours)
        end_time = current_time + timedelta(hours=time_window_hours)

        # 构建查询条件
        train_condition = DelayRecord.logic_train_id.in_(neighbor_trains)
        station_condition = DelayRecord.logic_station_index.in_(neighbor_stations)
        time_condition = and_(
            DelayRecord.created_at >= start_time,
            DelayRecord.created_at <= end_time
        )

        # 执行查询
        records = db.query(DelayRecord).filter(
            and_(train_condition, station_condition, time_condition)
        ).all()

        # 聚合晚点时间
        aggregated_delay = sum(r.delay_duration for r in records)

        # 格式化返回结果
        result = {
            "total_neighbors": len(records),
            "aggregated_delay": aggregated_delay,
            "records": [
                {
                    "delay_id": r.delay_id,
                    "logic_train_id": r.logic_train_id,
                    "logic_station_index": r.logic_station_index,
                    "delay_duration": r.delay_duration,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in records
            ],
            "query_params": {
                "target_train_id": logic_train_id,
                "target_station_index": logic_station_index,
                "neighbor_trains": neighbor_trains,
                "neighbor_stations": neighbor_stations,
                "time_window": f"{start_time.isoformat()} ~ {end_time.isoformat()}"
            }
        }

        return result

    finally:
        db.close()


def query_by_logical_conditions(
        logic_train_id: int = None,
        logic_station_index: int = None,
        circle_k: int = None,
        direction: str = None,
        start_time: datetime = None,
        end_time: datetime = None
) -> list:
    """
    根据逻辑索引条件查询晚点记录

    可用于各种复杂的 SQL 查询场景
    """
    db = SessionLocal()
    try:
        query = db.query(DelayRecord)

        if logic_train_id is not None:
            query = query.filter(DelayRecord.logic_train_id == logic_train_id)

        if logic_station_index is not None:
            query = query.filter(DelayRecord.logic_station_index == logic_station_index)

        if circle_k is not None:
            query = query.filter(DelayRecord.circle_k == circle_k)

        if direction is not None:
            query = query.filter(DelayRecord.direction == direction)

        if start_time is not None:
            query = query.filter(DelayRecord.created_at >= start_time)

        if end_time is not None:
            query = query.filter(DelayRecord.created_at <= end_time)

        records = query.all()

        return [
            {
                "delay_id": r.delay_id,
                "train_id": r.train_id,
                "station_id": r.station_id,
                "logic_train_id": r.logic_train_id,
                "logic_station_index": r.logic_station_index,
                "circle_k": r.circle_k,
                "direction": r.direction,
                "delay_duration": r.delay_duration,
                "delay_reason": r.delay_reason,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]

    finally:
        db.close()
