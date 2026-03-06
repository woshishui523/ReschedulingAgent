from langchain.tools import Tool
from algorithms.rescheduler import compute_reschedule
import json

def scheduling_func(input_data: str):
    """
    输入：结构化JSON字符串
    """
    data = json.loads(input_data)

    train_id = data["train_number"]
    station = data["station_name"]
    delay = data["delay_duration"]

    result = compute_reschedule(train_id, station, delay)

    return json.dumps(result, ensure_ascii=False)

scheduling_tool = Tool(
    name="TrainRescheduler",
    func=scheduling_func,
    description="根据列车编号、车站和晚点时间计算最优调度调整量"
)