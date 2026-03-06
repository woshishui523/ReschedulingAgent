import uuid
from datetime import datetime


def generate_dispatch_command(data):
    """
    根据解析的数据生成调度命令。

    输入：
        data (dict): 解析出的结构化数据，包括列车编号、车站、晚点时长等

    输出：
        dict: 调度命令（命令编号，列车编号，命令类型，命令内容等）
    """
    command_id = str(uuid.uuid4())  # 生成唯一命令ID
    train_number = data["train_number"]
    station_name = data["station_name"]
    delay_duration = data["delay_duration"]
    is_urgent = data["is_urgent"]

    # 根据晚点时间生成调度命令
    if delay_duration > 10:
        command_type = "调整发车时间"
        command_content = f"{train_number}次列车在{station_name}晚点{delay_duration}分钟，建议延后发车{delay_duration - 10}分钟"
    else:
        command_type = "无需调整"
        command_content = f"{train_number}次列车在{station_name}晚点{delay_duration}分钟，建议维持原发车时间"

    # 创建调度命令
    dispatch_command = {
        "command_id": command_id,
        "train_number": train_number,
        "station_name": station_name,
        "command_type": command_type,
        "command_content": command_content,
        "status": "待处理",
        "issued_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return dispatch_command