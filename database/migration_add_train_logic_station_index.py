# database/migration_add_train_logic_station_index.py
"""
数据库迁移脚本：为 trains 表添加 logic_station_index 字段

执行方式:
    python database/migration_add_train_logic_station_index.py
"""
from config.database import engine
from sqlalchemy import text


def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")

    with engine.connect() as conn:
        try:
            # 检查字段是否已存在
            check_sql = text("""
                             SELECT COUNT(*)
                             FROM information_schema.COLUMNS
                             WHERE TABLE_SCHEMA = 'train_dispatch'
                               AND TABLE_NAME = 'trains'
                               AND COLUMN_NAME = 'logic_station_index'
                             """)
            result = conn.execute(check_sql).scalar()

            if result > 0:
                print("⚠ logic_station_index 字段已存在，跳过添加")
            else:
                # 添加 logic_station_index 字段
                print("添加 logic_station_index 字段到 trains 表...")
                conn.execute(text("""
                                  ALTER TABLE trains
                                      ADD COLUMN logic_station_index INT NULL COMMENT '逻辑列车ID'
                                  """))

                # 添加索引以提高查询性能
                print("添加索引...")
                conn.execute(text("""
                                  CREATE INDEX idx_trains_logic_station ON trains (logic_station_index)
                                  """))

                print("✓ logic_station_index 字段添加成功!")

            conn.commit()
            print("✓ 数据库迁移完成!")

        except Exception as e:
            conn.rollback()
            print(f"✗ 迁移失败：{e}")
            raise


if __name__ == "__main__":
    migrate()
