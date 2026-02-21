import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, localtime


def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]#取文件扩展名，-1取最后一段
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'#去随机字符串的十六进制前十位
    return f'user/photos/{instance.user_id}_{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #绑定
    photo =models.ImageField(default='user/photos/default.ong', upload_to=photo_upload_to)
    profile =models.TextField(default='你好，欢迎来找我玩!',max_length=500) #默认签名和最大长度，TextField中最大长度需要后续函数单独判读
    create_time=models.DateTimeField(default=now)#默认当前时间
    update_time=models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}'
