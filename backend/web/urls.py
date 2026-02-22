from django.urls import path, re_path

from web.views.account.get_user_info import GetUserInfoView
from web.views.account.login import LoginView
from web.views.account.logout import LogoutView
from web.views.account.refresh_token import RefreshTokenView
from web.views.account.register import RegisterView
from web.views.index import index

urlpatterns = [
    path('api/user/account/login/',LoginView.as_view()),#前加api为了与系统默认做区分
    path('api/user/account/logout/',LogoutView.as_view()),
    path('api/user/account/register/',RegisterView.as_view()),
    path('api/user/account/refresh_token/',RefreshTokenView.as_view()),
    path('api/user/account/get_user_info/',GetUserInfoView.as_view()),
    path('',index),
    re_path(r'^(?!media/|static/|assets/).*$', index)
]

