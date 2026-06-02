# database/migration_add_logical_fields.py
"""
数据库迁移脚本：为 delay_records 表添加逻辑索引字段

执行方式:
    python database/migration_add_logical_fields.py
"""
from config.database import engine
from sqlalchemy import text


def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")

    with engine.connect() as conn:
        try:
            # 添加 logic_train_id 字段
            print("添加 logic_train_id 字段...")
            conn.execute(text("""
                              ALTER TABLE delay_records
                                  ADD COLUMN logic_train_id INT NULL COMMENT '列车逻辑索引 (1 到 N_train)'
                              """))

            # 添加 logic_station_index 字段
            print("添加 logic_station_index 字段...")
            conn.execute(text("""
                              ALTER TABLE delay_records
                                  ADD COLUMN logic_station_index INT NULL COMMENT '全局唯一站点索引'
                              """))

            # 添加 circle_k 字段
            print("添加 circle_k 字段...")
            conn.execute(text("""
                              ALTER TABLE delay_records
                                  ADD COLUMN circle_k INT NULL COMMENT '运行圈数'
                              """))

            # 添加 direction 字段
            print("添加 direction 字段...")
            conn.execute(text("""
                              ALTER TABLE delay_records
                                  ADD COLUMN direction VARCHAR(10) NULL COMMENT '运行方向：down(下行)/up(上行)'
                              """))

            # 添加索引以提高查询性能
            print("添加索引...")
            conn.execute(text("""
                              CREATE INDEX idx_logic_train ON delay_records (logic_train_id)
                              """))
            conn.execute(text("""
                              CREATE INDEX idx_logic_station ON delay_records (logic_station_index)
                              """))

            conn.commit()
            print("✓ 数据库迁移完成!")

        except Exception as e:
            conn.rollback()
            print(f"✗ 迁移失败：{e}")
            raise


if __name__ == "__main__":
    migrate()
