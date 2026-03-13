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

def query_station_info(station_name: str):
    with engine.connect() as conn:
        sql = text("""
            SELECT * FROM stations 
            WHERE station_name = :station_name
        """)
        result = conn.execute(sql, {"station_name": station_name})
        return [dict(row._mapping) for row in result]

db_query_tool = Tool(
    name="TrainDatabaseQuery",
    func=query_train_info,
    description="根据车次查询列车数据库信息"
)

station_query_tool = Tool(
    name="StationDatabaseQuery",
    func=query_station_info,
    description="根据车站名称查询车站数据库信息"
)
