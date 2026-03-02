from django.contrib import admin
from web.models.user import UserProfile
from web.models.character import Character
from web.models.friend import Friend

@admin.register(UserProfile)#注册
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',) #逗号必须保留！！！为一个列表，查找时页面加载100条；若写成`raw_id_fields`,则添加用户时，名字为所有用户的下拉菜单

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    raw_id_fields = ('me','character')#所有外键
