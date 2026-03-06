from langchain.tools import Tool
from config.database import engine
from sqlalchemy import text

def query_train_info(train_number: str):
    with engine.connect() as conn:
        sql = text("""
            SELECT * FROM trains 
            WHERE train_number = :train_number
        """)
        result = conn.execute(sql, {"train_number": train_number})
        return [dict(row._mapping) for row in result]

db_query_tool = Tool(
    name="TrainDatabaseQuery",
    func=query_train_info,
    description="根据车次查询列车数据库信息"
)