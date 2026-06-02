# run.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
列车晚点智能调度系统 - 主运行脚本

使用方法:
    python run.py              # 交互式运行
    python run.py --test       # 运行测试用例
"""
import sys
from main import dispatch_input_processor

import logging

# 将 SQLAlchemy 的日志级别设置为 WARNING，这样只会显示错误，不会显示每条 SQL 语句
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 70)
    print(" " * 20 + "🚄 列车晚点智能调度系统 🚄")
    print("=" * 70)
    print("\n✨ 功能特性:")
    print("   • 基于逻辑索引的列车与站点映射")
    print("   • 重调度控制信号算法")
    print("   • 相邻列车晚点影响分析")
    print("   • 智能调度命令生成")
    print("\n📐 核心算法:")
    print("   公式：u_{k}^{i} = g·x_{k}^{i} + f·x_{k+1}^{i-1}")
    print("   增益参数：g=0.6 (本车), f=0.4 (前车)")
    print("=" * 70)


def run_test_cases():
    """运行测试用例"""
    print("\n" + "=" * 70)
    print("🧪 测试用例演示")
    print("=" * 70)

    test_cases = [
        "C2501 次列车在北京南站因设备故障晚点 5 分钟",
        "C2502 次列车在天津站因天气原因晚点 8 分钟",
        "C2507 次列车在武清站因乘客紧急制动晚点 3 分钟",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"测试用例 {i}: {test_input}")
        print('=' * 70)

        try:
            result = dispatch_input_processor(test_input)
            print(f"\n✅ 测试用例 {i} 通过\n")
        except Exception as e:
            print(f"\n❌ 测试用例 {i} 失败：{e}\n")

    print("\n" + "=" * 70)
    print("所有测试用例执行完毕")
    print("=" * 70)


def interactive_mode():
    """交互式模式"""
    print_banner()

    print("\n💡 使用说明:")
    print("   请输入列车晚点信息，格式如:")
    print("   - C2501 次列车在北京南站因设备故障晚点 5 分钟")
    print("   - C2503 次列车在天津南站晚点 3 分钟")
    print("\n   输入 'quit' 或 'exit' 退出系统")
    print("=" * 70)

    while True:
        try:
            print("\n")
            user_input = input("📝 请输入晚点信息：").strip()

            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 感谢使用，再见！")
                break

            if not user_input:
                continue

            result = dispatch_input_processor(user_input)

            print("\n✨ 调度命令已生成并保存到数据库")
            print("\n💾 您可以:")
            print("   1. 查看数据库中的 delay_records 表")
            print("   2. 使用查询工具查看晚点记录")
            print("   3. 继续输入下一个晚点事件")

        except KeyboardInterrupt:
            print("\n\n⚠️  检测到中断，正在退出...")
            print("👋 感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n💥 错误：{e}")
            print("请检查输入格式后重试")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == '--test':
            run_test_cases()

        else:
            print(f"未知参数：{arg}")
            print("使用方法:")
            print("  python run.py           - 交互模式")
            print("  python run.py --test    - 运行测试")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
