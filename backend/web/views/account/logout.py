from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated#登陆状态才可以退出，需要判断当前帐号状态

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]#强制必须登录才能返回，否则返回401
    def post(self, request):
        response = Response({
            'result': 'success'
        })
        response.delete_cookie('refresh_token')
        return response