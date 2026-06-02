# test_direction_logic.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试上下行方向逻辑
"""
from tools.logical_id_calculator import calculate_logical_ids


def test_direction_logic():
    """测试方向判断和站点索引计算"""
    print("=" * 80)
    print("🧪 测试上下行方向逻辑")
    print("=" * 80)

    test_cases = [
        ("C2501", "天津南站", "下行 (奇数)", 2),
        ("C2502", "天津南站", "上行 (偶数)", 7),
        ("C2503", "北京南站", "下行 (奇数)", 1),
        ("C2504", "北京南站", "上行 (偶数)", 8),
        ("C2501", "滨海站", "下行 (奇数)", 8),
        ("C2502", "滨海站", "上行 (偶数)", 1),
    ]

    print("\n测试场景：假设 N_station = 8")
    print("-" * 80)
    print(f"{'车次':<10} {'车站':<10} {'方向':<15} {'基础 ID':<10} {'反向 ID':<10} {'有效 ID':<10} {'逻辑索引':<10}")
    print("-" * 80)

    for train_num, station_name, expected_dir, _ in test_cases:
        result = calculate_logical_ids(train_num, station_name)

        print(f"{train_num:<10} {station_name:<10} {result['direction']:<15} "
              f"{result['base_station_id']:<10} {result['reversed_station_id']:<10} "
              f"{result['effective_station_id']:<10} {result['logic_station_index']:<10}")

    print("-" * 80)

    print("\n📋 说明:")
    print("  • 下行 (奇数车次): 使用原始站点编号 (北京南=1, 天津南=2, ..., 滨海=8)")
    print("  • 上行 (偶数车次): 使用反转站点编号 (滨海=1, ..., 天津南=7, 北京南=8)")
    print("  • 有效 ID = 下行用 base_station_id, 上行用 reversed_station_id")
    print("  • 逻辑索引 = 有效 ID + (圈数 -1) × N_station")

    print("\n✅ 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_direction_logic()

