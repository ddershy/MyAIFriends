# backend/web/views/friend/message/memory/graph.py 设计记忆模块
import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class MemoryGraph:
    @staticmethod
    def create_app():
        llm = ChatOpenAI(#连接大模型
            model='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'),
            openai_api_base=os.getenv('API_BASE')
        )

        class AgentState(TypedDict): #数据类型
            messages: Annotated[Sequence[BaseMessage], add_messages]

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages']) #调用大模型
            return {'messages':[res]}

        graph = StateGraph(AgentState) #定义流程图
        graph.add_node('agent',model_call)#定义自己加入的agent节点,(名字,节点函数)

        graph.add_edge(START,'agent')
        graph.add_edge('agent',END)

        return graph.compile()