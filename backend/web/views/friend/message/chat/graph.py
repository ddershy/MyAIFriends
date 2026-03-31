import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class ChatGraph: #用于封装函数逻辑
    @staticmethod
    def create_app():
        llm = ChatOpenAI( #连接大模型
            models='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'), #gentenv：获取环境变量
            openai_api_base=os.getenv('API_BASE') #访问的URL
        )

        class AgentState(TypedDict): #数据类型
            messages: Annotated[Sequence[BaseMessage], add_messages] #本质为条件更丰富的字典，add_message为它的合并方式，将agent的结果追加在sequence末尾

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages']) #存储返回的model
            return {'messages': [res]} #将res追加到message的末尾

        graph = StateGraph(AgentState) #StateGraph创建状态图，()内为维护的状态类型
        graph.add_node('agent',model_call()) #定义自己加入的agent节点,(名字,节点函数)

        #加上连接的两条边 staet ----> agent ----> end
        graph.add_edge(START,'agent')
        graph.add_edge('agent', END)

        return graph.compiled()