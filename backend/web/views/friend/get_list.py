# 导入 DRF 的 Response 用于构造接口返回数据
from rest_framework.response import Response
# 导入 DRF 的 APIView 基类
from rest_framework.views import APIView
# 设置接口权限（必须登录）
from rest_framework.permissions import IsAuthenticated

# 导入好友关系模型
from web.models.friend import Friend


# 定义“获取好友列表”的接口
class GetListFriends(APIView):
    # 只有已认证（登录）的用户才能访问
    permission_classes = [IsAuthenticated]

    # 使用 GET 请求获取好友列表
    def get(self, request):
        try:
            # 从查询参数中获取 items_count，用于分页（偏移量）
            # 如果前端未传，默认值为 0
            items_count = int(request.query_params.get('items_count', 0))

            # 查询当前用户的好友关系：
            # me__user=request.user 表示筛选当前登录用户的好友
            # 按 update_time 倒序排列（最新更新的排在前面）
            # 使用切片实现分页：每次取 20 条
            friends_raw = Friend.objects.filter(
                me__user=request.user,
            ).order_by('-update_time')[items_count: items_count + 20]

            # 定义一个空列表，用于存储最终返回的数据
            friends = []  # 返回数组

            # 遍历查询结果
            for friend in friends_raw:
                # 获取好友对应的角色对象
                character = friend.character

                # 获取角色的作者对象
                author = character.author

                # 构造单条好友数据并添加到列表
                friends.append({
                    'id': friend.id,  # 好友关系ID
                    'character': {
                        'id': character.id,  # 角色ID
                        'name': character.name,  # 角色名称
                        'profile': character.profile,  # 角色简介
                        'photo': character.photo.url,  # 角色头像URL
                        'background_image': character.background_image.url,  # 角色背景图URL
                    },
                    'author': {
                        'user_id': author.user_id,  # 作者关联的用户ID
                        'username': author.user.username,  # 作者用户名
                        'photo': author.photo.url,  # 作者头像URL
                    }
                })

            return Response({
                'result': 'success',
                'friends': friends,
            })

        except:
            return Response({
                'result': '系统错误，请稍后重试',
            })