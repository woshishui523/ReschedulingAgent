from langchain.tools import Tool
from config.llm_config import get_llm
import json

llm = get_llm()


def parse_dispatch_text(text: str) -> dict:
    """
    将调度员口头描述转为结构化数据
    """
    prompt = f"""
    你是铁路调度系统的信息解析模块。
    请从以下描述中提取：
    1. train_number（车次）
    2. station_name（车站）
    3. delay_duration（分钟，数字）
    4. delay_reason（晚点原因）
    5. is_urgent（是否紧急，0 或 1，如果描述中没有明确说明则默认为 0）

    输入：
    {text}

    只输出 JSON，不要解释。JSON 格式如下：
    {{
        "train_number": "车次号",
        "station_name": "车站名",
        "delay_duration": 数字，
        "delay_reason": "原因",
        "is_urgent": 0 或 1
    }}
    """

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        return {"error": "解析失败"}


nlp_parser_tool = Tool(
    name="DispatchNLPParser",
    func=parse_dispatch_text,
    description="解析调度员口头晚点描述为结构化数据"
)