# backend/web/views/friend/message/chat/graph.py

import os
# from pprint import pprint
from typing import TypedDict, Annotated, Sequence

import lancedb
from django.utils.timezone import localtime, now
from langchain_community.vectorstores import LanceDB
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode

from web.documents.utils.custom_embeddings import CustomEmbeddings


class ChatGraph: #用于封装函数逻辑
    @staticmethod
    def create_app():
        @tool
        def get_time() -> str:
            """当需要查询精确时间时，调用此函数，返回格式为：[年-月-日 时:分:秒]"""
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        @tool
        def search_knowledge_base(query: str) -> str:
            """当用户查询阿里云百炼平台的相关信息时，调用此函数，输入为要查询的问题，输出为查询结果"""
            db = lancedb.connect('./web/documents/lancedb_storage') #连接数据库
            embeddings = CustomEmbeddings()
            vector_db = LanceDB(
                connection=db,
                embedding = embeddings,
                table_name= 'my_knowledge_base',
            )
            docs = vector_db.similarity_search(query,k=3)#查询最相近的三个文档
            context = '\n\n'.join([f'内容片段： {i+1}\n{doc.page_content}' for i,doc in enumerate(docs)])
            return f'从知识库中找到以下相关信息：\n\n{context}\n'

        tools = [get_time,search_knowledge_base] #工具列表

        llm = ChatOpenAI( #连接大模型
            model='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'), #gentenv：获取环境变量
            openai_api_base=os.getenv('API_BASE'),#访问的URL
            streaming = True, # 流式输出
            model_kwargs = {
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        ).bind_tools(tools)

        class AgentState(TypedDict): #数据类型
            messages: Annotated[Sequence[BaseMessage], add_messages] #本质为条件更丰富的字典，add_message为它的合并方式，将agent的结果追加在sequence末尾

        def model_call(state: AgentState) -> AgentState:
            # pprint(state['messages'])
            res = llm.invoke(state['messages']) #存储返回的model
            return {'messages': [res]} #将res追加到message的末尾

        def should_continue(state:AgentState) -> str: #路由节点
            last_message = state['messages'][-1]
            if last_message.tool_calls:#是否有工具调用
                return "tools"
            return "end"

        tool_node = ToolNode(tools) #工具节点，toolnode是langgraph自己实现的

        graph = StateGraph(AgentState) #StateGraph创建状态图，()内为维护的状态类型
        graph.add_node('agent',model_call) #定义自己加入的agent节点,(名字,节点函数)
        graph.add_node('tools',tool_node) #工具节点

        #加上连接的两条边
        graph.add_edge(START,'agent')
        graph.add_conditional_edges( #条件边
            'agent',
            should_continue,#条件判断节点
            {#路由字典
                'tools':'tools',
                'end':END,
            }
        )
        graph.add_edge('tools','agent')

        return graph.compile()
