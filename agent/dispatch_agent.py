from config.llm_config import get_llm
from tools.nlp_parser_tool import parse_dispatch_text
from tools.scheduling_tool import _dispatch_decision_wrapper
import json


def create_dispatch_agent():
    """创建调度智能体"""
    llm = get_llm()

    print("✅ 使用简化版智能体（直接分析模式）")
    
    # 创建一个简化的智能体包装器
    class SimpleDispatchAgent:
        def __init__(self, llm):
            self.llm = llm
        
        def invoke(self, input_dict):
            """
            模拟 agent 的 invoke 接口
            输入: {"messages": [HumanMessage(content=...)]} 或 {"input": ...}
            输出: {"output": ...}
            """
            # 提取输入内容
            if "messages" in input_dict:
                content = input_dict["messages"][0].content
            elif "input" in input_dict:
                content = input_dict["input"]
            else:
                content = str(input_dict)
            
            # 步骤1: 解析自然语言
            print("\n📝 步骤1: 解析调度员输入...")
            parsed_data = parse_dispatch_text(content)
            
            if "error" in parsed_data:
                return {
                    "output": f"❌ 解析失败: {parsed_data['error']}"
                }
            
            print(f"✅ 解析成功: {json.dumps(parsed_data, ensure_ascii=False)}")
            
            # 步骤2: 调用决策工具
            print("\n⚙️  步骤2: 执行调度决策...")
            delay_info = {
                "train_number": parsed_data.get("train_number", "UNKNOWN"),
                "station_name": parsed_data.get("station_name", "未知车站"),
                "delay_minutes": parsed_data.get("delay_duration", 0)
            }
            
            decision_input = {
                "dispatcher_input": content,
                "delay_info": delay_info
            }
            
            decision_result = _dispatch_decision_wrapper(json.dumps(decision_input))
            
            print(f"✅ 决策完成")
            
            # 返回结果
            return {
                "output": f"""
调度场景分析结果：

【原始输入】
{content}

【解析结果】
- 车次号: {parsed_data.get('train_number')}
- 车站: {parsed_data.get('station_name')}
- 晚点时长: {parsed_data.get('delay_duration')} 分钟
- 原因: {parsed_data.get('delay_reason')}
- 紧急程度: {'紧急' if parsed_data.get('is_urgent') else '普通'}

【决策结果】
{decision_result}
"""
            }
    
    agent_executor = SimpleDispatchAgent(llm)
    
    return agent_executor
