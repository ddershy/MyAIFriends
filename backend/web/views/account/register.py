from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from web.models.user import UserProfile


class RegisterView(APIView):
    def post(self,request):
        try:
            username = request.data.get('username').strip()
            password = request.data.get('password').strip()
            if not username or not password:#若为空
                return Response({
                    'result':'用户名和密码不能为空'
                })
            if User.objects.filter(username=username).exists():
                return Response({
                    'result': '用户名已存在'
                })
            user=User.objects.create_user(username=username,password=password)
            user_profile=UserProfile.objects.create(user=user)
            refresh = RefreshToken.for_user(user)
            response = Response({
                'result': 'success',
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'photo': user_profile.photo.url,  # 必须加url返回路径
                'profile': user_profile.profile,
            })
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),  # refresh返回的是refresh，refresh.access_token返回access，
                httponly=True,
                samesite='Lax',
                max_age=86400 * 7,  # 七天内有效
            )
            return response
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })