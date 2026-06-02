# database/fix_feedback_table.py
from config.database import engine
from sqlalchemy import text


def fix_feedback_table():
    """修复 feedback 表结构，确保包含所有必需字段"""
    with engine.connect() as conn:
        try:
            # 检查 feedback 表是否存在
            check_table_sql = text("""
                                   SELECT COUNT(*)
                                   FROM information_schema.TABLES
                                   WHERE TABLE_SCHEMA = 'train_dispatch'
                                     AND TABLE_NAME = 'feedback'
                                   """)
            table_exists = conn.execute(check_table_sql).scalar()

            if table_exists == 0:
                print("❌ feedback 表不存在，请先运行 create_feedback_table.py")
                return

            # 检查表中有哪些列
            check_columns_sql = text("""
                                     SELECT COLUMN_NAME
                                     FROM information_schema.COLUMNS
                                     WHERE TABLE_SCHEMA = 'train_dispatch'
                                       AND TABLE_NAME = 'feedback'
                                     """)
            existing_columns = [row[0] for row in conn.execute(check_columns_sql).fetchall()]
            print(f"当前 feedback 表的字段: {existing_columns}")

            # 删除旧表并重新创建
            print("\n⚠️  检测到表结构不完整，将删除旧表并重新创建...")
            conn.execute(text("DROP TABLE IF EXISTS feedback"))
            conn.commit()
            print("✅ 旧表已删除")

            # 重新创建表
            from models.feedback import Feedback
            Feedback.__table__.create(engine)
            print("✅ feedback 表重新创建成功")

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

            # 验证表结构
            new_columns = [row[0] for row in conn.execute(check_columns_sql).fetchall()]
            print(f"\n✅ 新的 feedback 表字段: {new_columns}")

        except Exception as e:
            print(f"❌ 修复失败：{e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    fix_feedback_table()
