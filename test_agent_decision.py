# test_agent_decision.py
"""
测试智能体驱动的调度决策系统
"""
import json
from agent.dispatch_agent import create_dispatch_agent
from langchain_core.messages import HumanMessage
import logging

# 将 SQLAlchemy 的日志级别设置为 WARNING，这样只会显示错误，不会显示每条 SQL 语句
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


def test_agent_decision():
    """测试智能体决策流程"""

    print("=" * 70)
    print("🤖 智能体驱动的列车调度决策测试")
    print("=" * 70)

    # 创建智能体
    agent_executor = create_dispatch_agent()

    # 测试用例1: 需要快速响应（应该选择反馈控制）
    print("\n📋 测试用例1: 需要快速响应")
    print("-" * 50)
    query1 = "列车G101在北京南站因设备故障晚点5分钟，需要迅速处理"

    result1 = agent_executor.invoke({
        "messages": [HumanMessage(content=f"""
        请使用 DispatchDecisionMaker 工具处理以下调度场景：
        {query1}
        
        直接调用工具并返回结果。
        """)]
    })

    print(f"输入: {query1}")
    print(f"\n智能体输出:")
    print(result1)

    # 测试用例2: 客流突变（应该选择ILC）
    print("\n\n" + "=" * 70)
    print("📋 测试用例2: 客流突变")
    print("-" * 50)
    query2 = "由于客流突变导致C2503次列车在天津站晚点8分钟"

    result2 = agent_executor.invoke({
        "messages": [HumanMessage(content=f"""
        请使用 DispatchDecisionMaker 工具处理以下调度场景：
        {query2}

        直接调用工具并返回结果。
        """)]
    })

    print(f"输入: {query2}")
    print(f"\n智能体输出:")
    print(result2)

    # 测试用例3: 普通情况（应该选择RMPC）
    print("\n\n" + "=" * 70)
    print("📋 测试用例3: 普通晚点")
    print("-" * 50)
    query3 = "D789次列车在上海虹桥站晚点10分钟"

    result3 = agent_executor.invoke({
        "messages": [HumanMessage(content=f"""
        请使用 DispatchDecisionMaker 工具处理以下调度场景：
        {query3}

        直接调用工具并返回结果。
        """)]
    })

    print(f"输入: {query3}")
    print(f"\n智能体输出:")
    print(result3)

    # 测试用例4: 多个关键词（紧急+客流突变，优先紧急）
    print("\n\n" + "=" * 70)
    print("📋 测试用例4: 紧急且客流突变")
    print("-" * 50)
    query4 = "紧急！由于客流突变，Z12次列车在北京站晚点15分钟，请立即处理"

    result4 = agent_executor.invoke({
        "messages": [HumanMessage(content=f"""
        请使用 DispatchDecisionMaker 工具处理以下调度场景：
        {query4}

        直接调用工具并返回结果。
        """)]
    })

    print(f"输入: {query4}")
    print(f"\n智能体输出:")
    print(result4)

    print("\n" + "=" * 70)
    print("✅ 智能体测试完成")
    print("=" * 70)


if __name__ == "__main__":
    test_agent_decision()