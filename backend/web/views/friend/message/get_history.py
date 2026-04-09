# backend/web/views/friend/message/get_history.py

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Message


class GetHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            last_message_id = int(request.query_params.get('last_message_id')) #获取最新一条消息id
            friend_id = int(request.query_params.get('friend_id'))
            queryset =  Message.objects.filter(friend_id=friend_id,friend__me__user=request.user) #只能拉取自己好友的消息，不能看别人的聊天记录
            if last_message_id > 0:#不是第一次加载
                queryset = queryset.filter(pk__lt=last_message_id) #lt->小于last_message_id的消息 lte<= gt> gte>=,django数据库判断
            message_raw = queryset.order_by('-id')[:1] #倒序排列信息，新的在前
            messages = []
            for m in message_raw:
                messages.append({
                    'id': m.id,
                    'user_message': m.user_message,
                    'output': m.output,
                })
            return Response({
                'result': 'success',
                'messages': messages,
            })
        except:
            return Response({
                'result':'系统异常，请稍后再试',
            })
