# backend/web/views/friend/message/chat/chat.py
import json

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph

class SSERenderer(BaseRenderer): #渲染器
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self,data, accepted_media_type=None, renderer_context=None):
        return data

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer] #引入渲染器
    def post(self, request):
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不得为空',
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friends.exists():
            return Response({
                'result': '好友不存在',
            })

        # 对接大模型
        friend = friends.first()
        app = ChatGraph.create_app()

        #构造输入,构造刚刚定义的字典
        inputs ={
            'messages': [HumanMessage(message)] #和构造的函数内变量名对应，封装传入的消息
        }

        # res = app.invoke(inputs) #调用计算流程  非流式回复
        # print(res['messages'][-1].content) #会返回一个

        # 流式回复： yield：生成器，每执行一次，会往下进行一个yield之前的内容；
            #生成器定义
        def event_stream():
            full_usage ={} #存储消耗量
            for msg,metadata in app.stream(inputs,stream_mode="messages"):
                if isinstance(msg,BaseMessageChunk): #消息是否是本次片段
                    if msg.content:#判断是否有消息
                        yield f"data:{json.dumps({'content':msg.content},ensure_ascii=False)}\n\n" #ensure_ascii=False 确保返回为unicode 看中文
                    if hasattr(msg,'usage_metadata') and msg.usage_metadata: #存储usage信息
                        full_usage = msg.usage_metadata
            yield 'data: [DONE]\n\n' #结束格式 data: [DONE]\n\n
            print(full_usage)

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream") #返回StreamingHttpResponse
        response['Cache-Control'] = 'no-cache'
        return response