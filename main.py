from agent.dispatch_agent import create_dispatch_agent
import json
from algorithms.rescheduler import compute_reschedule

from tools.generate_dispatch_command import generate_dispatch_command
from services.db_service import get_all_delay_records
from config.database import SessionLocal
from models.delay_record import DelayRecord
from sqlalchemy import text


def main():
    print("🚄 智能调度系统启动...")

    while True:
        user_input = input("调度员输入：")
        if user_input == "exit":
            break

        # 从数据库读取最新的晚点记录
        db = SessionLocal()
        try:
            # 查询最新的晚点记录（按 delay_id 降序排列，取第一条）
            sql = text("""
                SELECT dr.*, s.station_name, dr.is_urgent
                FROM delay_records dr
                LEFT JOIN stations s ON dr.station_id = s.station_id
                ORDER BY dr.delay_id DESC
                LIMIT 1
            """)
            result = db.execute(sql).fetchone()
            
            if result:
                # 构建结构化数据
                structured_data = {
                    "train_number": str(result.train_id),  # 如果有 trains 表，可以关联查询车次号
                    "station_name": result.station_name if result.station_name else f"车站_{result.station_id}",
                    "delay_duration": result.delay_duration,
                    "is_urgent": result.is_urgent if hasattr(result, 'is_urgent') and result.is_urgent is not None else 0
                }
                
                print(f"\n从数据库读取到以下信息:")
                print(f"  列车 ID: {result.train_id}")
                print(f"  车站 ID: {result.station_id}")
                print(f"  车站名称：{result.station_name}")
                print(f"  晚点时长：{result.delay_duration} 分钟")
                print(f"  紧急程度：{result.is_urgent if hasattr(result, 'is_urgent') else '无此字段'}")
                print(f"  晚点原因：{result.delay_reason}")
                
                # 调用调度命令生成函数
                dispatch_command = generate_dispatch_command(structured_data)
                
                # 输出调度命令
                print("\n生成的调度命令：")
                print(dispatch_command)
            else:
                print("⚠️  数据库中没有晚点记录")
                
        finally:
            db.close()

if __name__ == "__main__":
    main()