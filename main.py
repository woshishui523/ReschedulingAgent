from agent.dispatch_agent import create_dispatch_agent
import json
from algorithms.rescheduler import compute_reschedule

from tools.generate_dispatch_command import generate_dispatch_command


def main():
    print("🚄 智能调度系统启动...")

    while True:
        user_input = input("调度员输入：")
        if user_input == "exit":
            break

        # 假设我们已经有了结构化数据（这是从NLP解析得到的）
        structured_data = {
            "train_number": "G123",
            "station_name": "广州南站",
            "delay_duration": 20,
            "is_urgent": 0
        }

        # 调用调度命令生成函数
        dispatch_command = generate_dispatch_command(structured_data)

        # 输出调度命令
        print("调度命令：")
        print(dispatch_command)

if __name__ == "__main__":
    main()