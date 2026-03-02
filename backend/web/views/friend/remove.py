# 导入 DRF 的基础视图类
from rest_framework.views import APIView
# 用于构造 HTTP 响应对象
from rest_framework.response import Response
# 用于限制接口必须登录后才能访问
from rest_framework.permissions import IsAuthenticated

# 导入好友关系模型
from web.models.friend import Friend


# 定义“删除好友关系”的接口视图
class RemoveFriendView(APIView):
    # 设置权限：必须是已认证用户
    permission_classes = [IsAuthenticated]

    # 使用 POST 请求执行删除操作
    def post(self, request):
        try:
            # 从前端传递的数据中获取 friend_id（好友关系的主键）
            friend_id = request.data['friend_id']

            # 执行删除操作：
            # 1. id=friend_id：确保删除的是指定的好友记录
            # 2. me__user=request.user：确保该好友关系属于当前登录用户
            #    me 是外键指向 UserProfile
            #    me__user 是跨表查询，确保只能删除自己的好友关系
            Friend.objects.filter(
                id=friend_id,
                me__user=request.user
            ).delete()

            # 删除成功后返回 success
            return Response({
                'result': 'success',
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })