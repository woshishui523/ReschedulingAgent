# tools/example_usage.py
"""
逻辑索引计算工具使用示例
"""
from tools.logical_id_calculator import calculate_logical_ids, find_neighbor_trains
from tools.neighbor_query_tool import query_neighbor_delay_records
from services.db_service import add_delay_record_with_logic


def example_1_basic_mapping():
    """示例 1: 基本逻辑索引计算"""
    print("=== 示例 1: 基本逻辑索引计算 ===")

    # 假设 base_data 配置：train_num=6, station_num=8, train_start=2501
    result = calculate_logical_ids("G2501", "天津南站")

    print(f"车次：G2501, 车站：天津南站")
    print(f"  列车逻辑 ID: {result['logic_train_id']}")
    print(f"  全局站点索引：{result['logic_station_index']}")
    print(f"  基础站点 ID: {result['base_station_id']}")
    print(f"  运行圈数：{result['circle_k']}")
    print(f"  运行方向：{result['direction']}")

    # G2507 的计算
    result2 = calculate_logical_ids("G2507", "天津南站")
    print(f"\n车次：G2507, 车站：天津南站")
    print(f"  列车逻辑 ID: {result2['logic_train_id']}")
    print(f"  运行圈数：{result2['circle_k']}")


def example_2_neighbor_search():
    """示例 2: 相邻列车查找"""
    print("\n=== 示例 2: 相邻列车查找 ===")

    # 查找列车 1 的相邻列车 (假设总共 6 列)
    neighbors = find_neighbor_trains(1, 6)
    print(f"列车 1 的相邻列车：{neighbors}")  # 应该输出 [6, 2]

    # 查找列车 3 的相邻列车
    neighbors = find_neighbor_trains(3, 6)
    print(f"列车 3 的相邻列车：{neighbors}")  # 应该输出 [2, 4]


def example_3_save_delay_record():
    """示例 3: 保存带逻辑索引的晚点记录"""
    print("\n=== 示例 3: 保存晚点记录 ===")

    try:
        record = add_delay_record_with_logic(
            train_number="G2501",
            station_name="天津南站",
            duration=15,
            reason="设备故障",
            is_urgent=1
        )

        print(f"成功保存记录:")
        print(f"  记录 ID: {record.delay_id}")
        print(f"  逻辑列车 ID: {record.logic_train_id}")
        print(f"  逻辑站点索引：{record.logic_station_index}")
        print(f"  晚点时长：{record.delay_duration}分钟")

    except Exception as e:
        print(f"保存失败：{e}")


def example_4_query_neighbors():
    """示例 4: 查询相邻晚点记录"""
    print("\n=== 示例 4: 查询相邻晚点记录 ===")

    # 查询列车 1 在站点 2 的相邻晚点记录
    result = query_neighbor_delay_records(
        logic_train_id=1,
        logic_station_index=2,
        n_train=6,
        n_station=8,
        time_window_hours=2.0
    )

    print(f"查询结果:")
    print(f"  相邻记录数：{result['total_neighbors']}")
    print(f"  聚合晚点时间：{result['aggregated_delay']}分钟")
    print(f"  查询参数：{result['query_params']}")

    if result['records']:
        print(f"  详细记录:")
        for rec in result['records'][:5]:  # 只显示前 5 条
            print(f"    - 列车{rec['logic_train_id']} @ "
                  f"站点{rec['logic_station_index']}: "
                  f"{rec['delay_duration']}分钟")


if __name__ == "__main__":
    example_1_basic_mapping()
    example_2_neighbor_search()
    example_3_save_delay_record()
    example_4_query_neighbors()
