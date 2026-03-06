from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from config.llm_config import get_llm
from tools.nlp_parser_tool import nlp_parser_tool
from tools.scheduling_tool import scheduling_tool

tools = [
    nlp_parser_tool,
    scheduling_tool
]

def create_dispatch_agent():
    llm = get_llm()

    tools = [nlp_parser_tool]

    # ✅ 使用官方 ReAct Prompt 模板
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    return agent_executor