from langchain_core.messages import HumanMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph


class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
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

        res = app.invoke(inputs) #调用计算流程
        print(res['messages'][-1].content) #会返回一个
        return Response({
            'result':'success',
        })