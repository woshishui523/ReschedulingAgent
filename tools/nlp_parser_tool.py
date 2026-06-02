# tools/nlp_parser_tool.py
import json
import re
import logging
from typing import Optional, Dict, Any, List, Union

from langchain_core.tools import Tool
from config.llm_config import get_llm

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化 LLM
try:
    llm = get_llm()
except Exception as e:
    logger.error(f"LLM 初始化失败: {e}")
    llm = None


def extract_json_from_response(response_text: str) -> Optional[str]:
    """
    从 LLM 响应中提取 JSON 字符串。
    增强版：支持嵌套 JSON 对象，支持多种 Markdown 格式。
    """
    if not response_text:
        return None

    response_text = response_text.strip()

    # 1. 尝试匹配 ```json ... ``` 代码块
    # 使用 non-greedy 匹配，允许内部包含换行和任意字符
    pattern_json_block = r'```json\s*(.*?)\s*```'
    match = re.search(pattern_json_block, response_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 2. 尝试匹配普通 ``` ... ``` 代码块
    pattern_code_block = r'```\s*(.*?)\s*```'
    match = re.search(pattern_code_block, response_text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        # 防止提取到非 JSON 的代码
        if content.startswith('{') or content.startswith('['):
            return content

    # 3. 尝试直接查找平衡的 JSON 对象 ({...})
    # 使用栈原理或递归正则难以在单行 regex 完美实现，这里使用简化策略：
    # 寻找第一个 '{' 和最后一个 '}'，然后尝试验证
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        potential_json = response_text[start_idx: end_idx + 1]
        # 简单验证是否看起来像 JSON (避免截取过多无关文本)
        try:
            # 尝试预解析，如果失败则说明结构不对，返回 None 让上层处理
            json.loads(potential_json)
            return potential_json
        except json.JSONDecodeError:
            pass

    return None


def parse_dispatch_text(text: str) -> Dict[str, Any]:
    """
    将调度员口头描述转为结构化数据
    """
    if not llm:
        return {"error": "LLM 服务未初始化"}

    prompt = f"""
你是一个铁路调度系统的智能信息解析专家。你的任务是从非结构化文本中提取关键晚点信息。

**输入内容**：
{text}

**提取规则**：
1. **train_number** (车次号): 提取字母+数字组合 (如 G101, C2503)。若无明确车次，设为 "UNKNOWN"。
2. **station_name** (车站名): 提取包含 "站" 的地名。若无，设为 "未知车站"。
3. **delay_duration** (晚点时长): 仅提取数字 (int)，单位默认为分钟。若无数字，设为 0。
4. **delay_reason** (原因): 概括原因 (如 "设备故障", "暴雨")。若无，设为 "未知原因"。
5. **is_urgent** (紧急程度): 若包含 "紧急", "立即", "急", "快", "马上" 等词，设为 1，否则为 0。

**输出约束**：
- **必须且只能**输出一个标准的 JSON 对象。
- **严禁**输出 markdown 标记 (如 ```json)、解释性文字、前言或后缀。
- 确保 JSON 格式合法，可以直接被 `json.loads()` 解析。

**JSON 模板**：
{{
    "train_number": "string",
    "station_name": "string",
    "delay_duration": integer,
    "delay_reason": "string",
    "is_urgent": integer (0 or 1)
}}

开始解析：
"""

    try:
        # 调用 LLM
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        # 提取 JSON 字符串
        json_str = extract_json_from_response(response_text)

        if not json_str:
            logger.warning(f"未能提取 JSON。原始响应片段: {response_text[:100]}...")
            return {"error": "LLM 未返回有效的 JSON 格式", "raw_response": response_text[:200]}

        # 解析 JSON
        parsed_json = json.loads(json_str)

        # --- 数据后处理与验证 ---

        # 1. 字段完整性检查
        required_fields = ["train_number", "station_name", "delay_duration"]
        for field in required_fields:
            if field not in parsed_json:
                # 尝试自动补全默认值
                if field == "delay_duration":
                    parsed_json[field] = 0
                elif field == "train_number":
                    parsed_json[field] = "UNKNOWN"
                elif field == "station_name":
                    parsed_json[field] = "未知车站"
                else:
                    return {"error": f"缺少关键字段且无法推断: {field}"}

        # 2. 类型转换与清洗
        # 确保 delay_duration 是整数
        try:
            val = parsed_json["delay_duration"]
            if isinstance(val, str):
                # 尝试从字符串中提取数字 (防止 LLM 返回 "5 分钟")
                nums = re.findall(r'\d+', val)
                parsed_json["delay_duration"] = int(nums[0]) if nums else 0
            else:
                parsed_json["delay_duration"] = int(val)
        except (ValueError, TypeError):
            parsed_json["delay_duration"] = 0

        # 确保 is_urgent 是 0 或 1
        urgent_val = parsed_json.get("is_urgent", 0)
        parsed_json["is_urgent"] = 1 if urgent_val else 0

        # 确保 reason 不为空
        if not parsed_json.get("delay_reason"):
            parsed_json["delay_reason"] = "未知原因"

        return parsed_json

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {e}")
        return {"error": f"JSON 格式错误: {str(e)}", "raw_snippet": json_str[:100] if 'json_str' in locals() else ""}
    except Exception as e:
        logger.exception(f"解析过程发生未知错误: {e}")
        return {"error": f"系统异常: {str(e)}"}


def validate_parsed_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证和规范化解析后的数据
    """
    if "error" in parsed_data:
        return parsed_data

    errors = []

    # 验证车次号
    train_number = parsed_data.get("train_number", "")
    if train_number == "UNKNOWN":
        logger.warning("车次号未识别，标记为 UNKNOWN")

    # 验证车站名称
    station_name = parsed_data.get("station_name", "")
    if not station_name or station_name == "未知车站":
        logger.warning("车站名称未识别")

    # 验证晚点时长
    delay_duration = parsed_data.get("delay_duration", -1)
    if delay_duration < 0:
        errors.append("晚点时长不能为负数")

    if errors:
        return {"error": "; ".join(errors), "data": parsed_data}

    return parsed_data


def parse_dispatch_batch(text_list: Union[str, List[str]]) -> List[Dict[str, Any]]:
    """
    批量解析多条调度记录

    参数:
        text_list: 可以是 Python list 对象，也可以是 JSON 格式的字符串列表
    """
    # 安全解析输入
    if isinstance(text_list, str):
        try:
            # 使用 json.loads 替代 eval，防止代码注入
            texts = json.loads(text_list)
            if not isinstance(texts, list):
                raise ValueError("输入必须是 JSON 数组")
        except json.JSONDecodeError:
            return [{"input": text_list, "parsed": {"error": "输入格式错误，期望 JSON 列表"}}]
    elif isinstance(text_list, list):
        texts = text_list
    else:
        return [{"input": str(text_list), "parsed": {"error": "输入类型不支持"}}]

    results = []
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            text = str(text)

        logger.info(f"处理批次 {i + 1}/{len(texts)}")
        parsed_result = parse_dispatch_text(text)

        # 可选：在此处加入 validate_parsed_data
        # validated_result = validate_parsed_data(parsed_result)

        results.append({
            "input": text,
            "parsed": parsed_result
        })

    return results


# ========== LangChain Tools 定义 ==========

nlp_parser_tool = Tool(
    name="DispatchNLPParser",
    func=lambda x: json.dumps(parse_dispatch_text(x), ensure_ascii=False),
    description="""解析单条调度员口头晚点描述为结构化 JSON。
输入：自然语言字符串 (例如："C2503 次列车在北京南站因设备故障晚点 5 分钟")
输出：JSON 字符串，包含 train_number, station_name, delay_duration, delay_reason, is_urgent 字段。
注意：如果解析失败，返回的 JSON 中将包含 "error" 字段。"""
)

batch_parser_tool = Tool(
    name="DispatchBatchParser",
    func=lambda x: json.dumps(parse_dispatch_batch(x), ensure_ascii=False),
    description="""批量解析多条调度记录。
输入：JSON 格式的字符串列表 (例如："[\"C2503 晚点 5 分钟\", \"G101 晚点 10 分钟\"]") 或直接传入列表。
输出：JSON 格式的列表，每个元素包含 input 和 parsed 字段。"""
)

# ========== 测试入口 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 NLP 解析器本地测试")
    print("=" * 60)

    test_cases = [
        "C2503 次列车在北京南站因设备故障晚点 5 分钟",
        "紧急！G101 在上海虹桥站因为暴雨晚点了 15 分钟",
        "D789 在广州南站，乘客突发疾病，晚点 8 分钟",
        "Z12 次北京站信号故障，延误 20 分钟",
        "T45 在杭州东站供电故障，需要立即处理，晚点 30 分钟",
        "这是一条没有车次和时间的无效测试消息"  # 测试容错
    ]

    # 测试单条解析
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] 输入: {test_text}")
        print("-" * 40)
        result = parse_dispatch_text(test_text)

        if "error" in result:
            print(f"❌ 解析警告/失败: {result['error']}")
            if 'raw_response' in result:
                print(f"   原始响应预览: {result['raw_response'][:50]}...")
        else:
            print("✅ 解析成功:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

    # 测试批量解析
    print("\n" + "=" * 60)
    print("📦 批量解析测试")
    print("=" * 60)
    batch_input = json.dumps(test_cases[:3])  # 取前三条作为 JSON 字符串输入
    batch_results = parse_dispatch_batch(batch_input)
    print(f"处理了 {len(batch_results)} 条记录")
    for item in batch_results:
        status = "✅" if "error" not in item['parsed'] else "⚠️"
        print(f"{status} {item['input']} -> {item['parsed'].get('train_number', 'N/A')}")