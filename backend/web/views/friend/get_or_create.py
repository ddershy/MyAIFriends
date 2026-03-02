# 导入 DRF 的基础视图类
from rest_framework.views import APIView
# 用于构造 HTTP 响应
from rest_framework.response import Response
# 用于设置接口访问权限
from rest_framework.permissions import IsAuthenticated

# 导入好友模型
from web.models.friend import Friend
# 导入用户扩展信息模型
from web.models.user import UserProfile


# 定义一个视图类：用于“获取或创建好友关系”
class GetOrCreateFriendView(APIView):
    # 设置权限：必须是已认证（登录）用户才能访问该接口
    permission_classes = [IsAuthenticated]

    # 定义 POST 请求处理函数（因为涉及创建操作，所以使用 POST）
    def post(self, request):  # 要创建用 post
        try:
            # 从前端传来的请求体中获取 character_id
            character_id = request.data['character_id']

            # 获取当前登录用户
            user = request.user

            # 根据当前登录用户，查找对应的 UserProfile（一对一关系）
            user_profile = UserProfile.objects.get(user=user)

            # 查询是否已经存在该用户与该角色之间的好友关系
            # me 表示当前用户，character_id 表示目标角色
            friends = Friend.objects.filter(character_id=character_id, me=user_profile)

            # 如果好友关系已经存在
            if friends.exists():
                # 取第一条记录（理论上应该只有一条）
                friend = friends.first()  # 若存在获取第一个
            else:
                # 如果不存在，则创建一条新的好友关系记录
                friend = Friend.objects.create(character_id=character_id, me=user_profile)

            # 获取好友关系对应的角色对象
            character = friend.character

            # 获取角色的作者信息
            author = character.author

            # 构造并返回成功响应数据
            return Response({
                'result': 'success',
                'friend': {
                    'id': friend.id,  # 好友关系的ID
                    'character': {
                        'id': character.id,  # 角色ID
                        'name': character.name,  # 角色名称
                        'profile': character.profile,  # 角色简介
                        'photo': character.photo.url,  # 角色头像图片URL
                        'background_image': character.background_image.url,  # 角色背景图URL
                        'author': {
                            'user_id': author.user_id,  # 作者关联的用户ID
                            'username': author.user.username,  # 作者用户名
                            'photo': author.photo.url,  # 作者头像URL
                        }
                    }
                }
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试',
            })