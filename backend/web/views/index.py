#目的：返回templates文件夹下文件

from django.shortcuts import render

def index(request):
    return render(request,'index.html')