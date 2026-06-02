# database/create_feedback_table.py
from config.database import engine
from sqlalchemy import text
from models.feedback import Feedback


def create_feedback_table():
    """创建 feedback 表并插入默认参数"""
    with engine.connect() as conn:
        try:
            # 检查表是否存在
            check_sql = text("""
                             SELECT COUNT(*)
                             FROM information_schema.TABLES
                             WHERE TABLE_SCHEMA = 'train_dispatch'
                               AND TABLE_NAME = 'feedback'
                             """)
            result = conn.execute(check_sql).scalar()

            if result == 0:
                print("创建 feedback 表...")
                Feedback.__table__.create(engine)
                print("✅ feedback 表创建成功")

                # 插入默认参数
                insert_sql = text("""
                                  INSERT INTO feedback (p, q, c, description)
                                  VALUES (:p, :q, :c, :description)
                                  """)
                conn.execute(insert_sql, {
                    "p": 0.5,
                    "q": 0.5,
                    "c": 1.0,
                    "description": "默认反馈控制参数"
                })
                conn.commit()
                print("✅ 已插入默认参数: p=0.5, q=0.5, c=1.0")
            else:
                print("ℹ️  feedback 表已存在")

        except Exception as e:
            print(f"❌ 创建表失败：{e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    create_feedback_table()
