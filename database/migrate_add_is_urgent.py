# database/migrate_add_is_urgent.py
from config.database import engine
from sqlalchemy import text

def add_is_urgent_column():
    """向 delay_records表添加 is_urgent 字段"""
    with engine.connect() as conn:
        try:
            # 检查列是否存在，不存在则添加
            check_sql = text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'train_dispatch' 
                AND TABLE_NAME = 'delay_records' 
                AND COLUMN_NAME = 'is_urgent'
            """)
            result = conn.execute(check_sql).scalar()
            
            if result == 0:
                alter_sql = text("""
                    ALTER TABLE delay_records 
                    ADD COLUMN is_urgent INT DEFAULT 0
                """)
                conn.execute(alter_sql)
                conn.commit()
                print("✅ 成功添加 is_urgent 字段")
            else:
                print("ℹ️  is_urgent 字段已存在")
                
        except Exception as e:
            print(f"❌ 添加字段失败：{e}")
            conn.rollback()

if __name__ == "__main__":
    add_is_urgent_column()
