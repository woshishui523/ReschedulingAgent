# test_decision_flow.py
"""
测试决策流程
"""
import json
from services.decision_engine import make_dispatch_decision


def test_decision_flow():
    """测试完整的决策流程"""

    print("=" * 70)
    print("🚂 列车调度决策系统测试")
    print("=" * 70)

    # 测试用例1: 需要快速响应
    print("\n📋 测试用例1: 需要快速响应的情况")
    print("-" * 50)
    input1 = "列车G101在北京南站因设备故障晚点5分钟，需要迅速处理"
    result1 = make_dispatch_decision(
        dispatcher_input=input1,
        delay_info={"train_number": "G101", "station_name": "北京南站", "delay_minutes": 5}
    )
    print(f"输入: {input1}")
    print(f"模糊规则存在: {result1['fuzzy_rules_exist']}")
    print(f"选择策略: {result1['selected_strategy']}")
    print(f"最终建议: {result1['final_recommendation']}")

    # # 测试用例2: 客流突变
    # print("\n📋 测试用例2: 客流突变的情况")
    # print("-" * 50)
    # input2 = "由于客流突变导致C2503次列车在天津站晚点8分钟"
    # result2 = make_dispatch_decision(
    #     dispatcher_input=input2,
    #     delay_info={"train_number": "C2503", "station_name": "天津站", "delay_minutes": 8}
    # )
    # print(f"输入: {input2}")
    # print(f"模糊规则存在: {result2['fuzzy_rules_exist']}")
    # print(f"选择策略: {result2['selected_strategy']}")
    # print(f"最终建议: {result2['final_recommendation']}")
    #
    # # 测试用例3: 普通情况
    # print("\n📋 测试用例3: 普通晚点情况")
    # print("-" * 50)
    # input3 = "D789次列车在上海虹桥站晚点10分钟"
    # result3 = make_dispatch_decision(
    #     dispatcher_input=input3,
    #     delay_info={"train_number": "D789", "station_name": "上海虹桥站", "delay_minutes": 10}
    # )
    # print(f"输入: {input3}")
    # print(f"模糊规则存在: {result3['fuzzy_rules_exist']}")
    # print(f"选择策略: {result3['selected_strategy']}")
    # print(f"最终建议: {result3['final_recommendation']}")
    #
    # # 测试用例4: 多个关键词
    # print("\n📋 测试用例4: 同时包含多个关键词")
    # print("-" * 50)
    # input4 = "紧急！由于客流突变，Z12次列车在北京站晚点15分钟，请立即处理"
    # result4 = make_dispatch_decision(
    #     dispatcher_input=input4,
    #     delay_info={"train_number": "Z12", "station_name": "北京站", "delay_minutes": 15}
    # )
    # print(f"输入: {input4}")
    # print(f"模糊规则存在: {result4['fuzzy_rules_exist']}")
    # print(f"意图解析: {result4['intent']}")
    # print(f"选择策略: {result4['selected_strategy']}")
    # print(f"最终建议: {result4['final_recommendation']}")

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)


if __name__ == "__main__":
    test_decision_flow()
