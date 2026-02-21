from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from web.models.user import UserProfile


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data['username'].strip()
            password = request.data['password'].strip()
            if not username or not password:#若为空
                return Response({
                    'result':'用户名和密码不能为空',
                })
            user= authenticate(username=username, password=password)#验证用户名和密码是否匹配,若匹配返回用户名， 若不匹配为空
            if user: #用户名密码正确
                user_profile = UserProfile.objects.get(username=username)#括号内为查询条件
                refresh = RefreshToken.for_user(user)#生成JWT
                response = Response({
                    'result':'success',
                    'access': str(refresh.access_token),
                    'user_id':user.id,
                    'username': user.username,
                    'photo': user_profile.photo.url,#必须加url返回路径
                    'profile':user_profile.profile,
                })
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh), #refresh返回的是refresh，refresh.access_token返回access，
                    httponly=True,
                    samesite='Lax',
                    max_age=86400*7,#七天内有效
                )
                return response
            return Response({ #错误的情况
                'result':'用户名或密码错误'
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试',
            })