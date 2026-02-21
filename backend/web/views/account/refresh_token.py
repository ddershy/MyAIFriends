from multiprocessing.reduction import steal_handle

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class RefreshTokenView(APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')#获取refresh_token
            if not refresh_token:#空字符串
                return Response({
                    'result': 'refresh token 不存在'
                },status=status.HTTP_401_UNAUTHORIZED) #必须401
            refresh=RefreshToken(refresh_token) #如果refresh token过期了/不合法会报异常
            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
                refresh.set_jti()#刷新为有效
                response=Response({
                    'result': 'success',
                    'access': str(refresh.access_token)
                })
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),  # refresh返回的是refresh，refresh.access_token返回access，
                    httponly=True,
                    samesite='Lax',
                    max_age=86400 * 7,  # 七天内有效
                )
                return response
            return Response({
                'result': 'success',
                'access': str(refresh.access_token)
            })
        except:
            return Response({
                'result':'refresh token 已过期'
            },status=status.HTTP_401_UNAUTHORIZED) # 必须401