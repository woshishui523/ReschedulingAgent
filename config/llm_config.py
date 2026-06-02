from langchain_community.chat_models import ChatTongyi

def get_llm():
    llm = ChatTongyi(
        model_name="qwen-turbo",
        dashscope_api_key="sk-44c0b71ba40e47078aec089a40119fdb"
    )
    return llm