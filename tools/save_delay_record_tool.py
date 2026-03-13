from langchain.tools import Tool
from services.db_service import add_delay_record
from tools.nlp_parser_tool import parse_dispatch_text
from tools.db_query_tool import query_train_info, query_station_info
import json


def save_delay_record(text: str) -> dict:
    """
    从调度员的自然语言描述中创建晚点记录

    处理流程：
    1. 解析自然语言，提取车次、车站、晚点时间、原因、是否紧急
    2. 查询 trains 表获取列车 ID
    3. 查询 stations 表获取车站 ID
    4. 保存到 delay_records 表

    输入示例："C2503 在北京南站晚点 20 分钟，原因是设备故障"
    """
    # Step 1: 解析自然语言
    parsed_data = parse_dispatch_text(text)

    if "error" in parsed_data:
        return {"success": False, "message": "NLP 解析失败", "data": parsed_data}

    train_number = parsed_data.get("train_number")
    station_name = parsed_data.get("station_name")
    delay_duration = parsed_data.get("delay_duration")
    delay_reason = parsed_data.get("delay_reason", "未知")
    is_urgent = parsed_data.get("is_urgent", 0)

    # 验证必要字段
    if not all([train_number, station_name, delay_duration]):
        return {
            "success": False,
            "message": "缺少必要字段",
            "data": parsed_data
        }

    # Step 2: 查询列车 ID
    train_results = query_train_info(train_number)
    if not train_results:
        return {"success": False, "message": f"未找到列车：{train_number}"}

    train_id = train_results[0].get('id') or train_results[0].get('train_id')
    if not train_id:
        return {"success": False, "message": "列车数据格式错误"}

    # Step 3: 查询车站 ID
    station_results = query_station_info(station_name)
    if not station_results:
        return {"success": False, "message": f"未找到车站：{station_name}"}

    station_id = station_results[0].get('station_id') or station_results[0].get('id')
    if not station_id:
        return {"success": False, "message": "车站数据格式错误"}

    # Step 4: 保存到晚点记录表
    record = add_delay_record(
        train_id=train_id,
        station_id=station_id,
        duration=delay_duration,
        reason=delay_reason,
        is_urgent=is_urgent
    )

    return {
        "success": True,
        "message": "晚点记录已保存",
        "data": {
            "delay_id": record.delay_id,
            "train_number": train_number,
            "station_name": station_name,
            "delay_duration": delay_duration,
            "delay_reason": delay_reason,
            "is_urgent": is_urgent
        }
    }


save_delay_record_tool = Tool(
    name="DelayRecordSaver",
    func=save_delay_record,
    description="从调度员自然语言描述创建晚点记录：解析文本 -> 查询列车和车站 ID -> 保存到 delay_records 表"
)
