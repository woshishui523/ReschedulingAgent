# tools/generate_dispatch_command.py
import json
from langchain_core.tools import Tool
from services.delay_service import process_delay_event


def generate_dispatch_command_tool(train_number: str, station_name: str, duration: int, reason: str) -> str:
    """
    生成调度命令的工具函数

    参数:
        train_number: 车次号
        station_name: 车站名称
        duration: 晚点时长（分钟）
        reason: 晚点原因

    返回:
        调度命令字符串
    """
    try:
        command = process_delay_event(train_number, station_name, duration, reason)
        return f"调度命令生成成功：\n{command}"
    except Exception as e:
        return f"调度命令生成失败：{str(e)}"


dispatch_command_tool = Tool(
    name="DispatchCommandGenerator",
    func=lambda input_str: generate_dispatch_command_tool(
        **json.loads(input_str)
    ),
    description="根据列车晚点信息生成调度命令。输入参数格式：JSON 字符串，包含 train_number(车次号), station_name(车站名), duration(晚点分钟数), reason(晚点原因)"
)

