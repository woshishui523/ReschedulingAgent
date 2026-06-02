"""
迁移脚本：更新 dispatch_records 表结构
- 将 adjustment_value 从 INTEGER 改为 FLOAT
- 添加 dispatch_id 主键字段（如果不存在）
"""
from sqlalchemy import text
from config.database import SessionLocal, engine


def migrate_dispatch_records():
    """执行数据库迁移"""
    db = SessionLocal()
    try:
        print("开始迁移 dispatch_records 表...")
        
        # 检查当前表结构
        result = db.execute(text("DESCRIBE dispatch_records"))
        columns = {row[0]: row for row in result.fetchall()}
        print(f"当前表结构: {list(columns.keys())}")
        
        # 检查是否存在 dispatch_id 字段
        if 'dispatch_id' not in columns:
            print("⚠️  表中缺少 dispatch_id 主键字段，需要添加...")
            
            # 先删除可能存在的旧主键约束
            try:
                db.execute(text("ALTER TABLE dispatch_records DROP PRIMARY KEY"))
                print("已删除旧的主键约束")
            except Exception as e:
                print(f"删除主键约束时出错（可能不存在）: {e}")
            
            # 添加 dispatch_id 作为第一列并设为主键
            db.execute(text(
                "ALTER TABLE dispatch_records "
                "ADD COLUMN dispatch_id INT AUTO_INCREMENT PRIMARY KEY FIRST"
            ))
            print("✅ dispatch_id 字段已添加并设置为主键（AUTO_INCREMENT）")
        else:
            print("✅ dispatch_id 字段已存在")
            
            # 检查是否为 AUTO_INCREMENT
            extra = columns['dispatch_id'][5] if len(columns['dispatch_id']) > 5 else ""
            print(f"dispatch_id 额外属性: {extra}")
            
            if 'auto_increment' not in extra.lower():
                print("需要为 dispatch_id 添加 AUTO_INCREMENT...")
                db.execute(text("ALTER TABLE dispatch_records MODIFY COLUMN dispatch_id INT AUTO_INCREMENT PRIMARY KEY"))
                print("✅ dispatch_id 已设置为 AUTO_INCREMENT")
            else:
                print("✅ dispatch_id 已经是 AUTO_INCREMENT")
        
        # 检查 adjustment_value 的类型
        if 'adjustment_value' in columns:
            col_type = columns['adjustment_value'][1]
            print(f"adjustment_value 当前类型: {col_type}")
            
            if 'int' in col_type.lower():
                print("需要将 adjustment_value 从 INT 改为 FLOAT...")
                db.execute(text("ALTER TABLE dispatch_records MODIFY COLUMN adjustment_value FLOAT NOT NULL"))
                print("✅ adjustment_value 类型已更新为 FLOAT")
            else:
                print("✅ adjustment_value 已经是正确的类型")
        
        db.commit()
        print("\n✅ 迁移完成！")
        
        # 再次检查最终表结构
        result = db.execute(text("DESCRIBE dispatch_records"))
        final_columns = result.fetchall()
        print("\n最终表结构:")
        for col in final_columns:
            print(f"  - {col[0]}: {col[1]} (Key: {col[3]}, Extra: {col[5] if len(col) > 5 else ''})")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    migrate_dispatch_records()
