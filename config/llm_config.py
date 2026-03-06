from langchain_community.chat_models import ChatTongyi

def get_llm():
    llm = ChatTongyi(
        model_name="qwen-turbo",
        dashscope_api_key="sk-76b614a5c2594980a9f4c7a66f94362c"
    )
    return llm