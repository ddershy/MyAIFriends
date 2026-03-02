# 一个伟大的开始！！！—— AIFriends
## 五、流式布局

### 0. 删头像补丁
修复每次用户上传头像会删除默认头像的问题
函数写错了：
```py
def remove_old_photo(photo):
    if photo and photo.name != 'user/photo/default.png':
        old_path = settings.MEDIA_ROOT / photo.name
        if os.path.exists(old_path):
            os.remove(old_path)
```
修改为` 'user/photos/default.png'`

### 1 实现个人主页
#### 1.1 创建后端
在`AIFriends/backend/web/views/create/character/`目录下实现：`get_list.py`：返回角色列表和作者信息。

1. 无需登录；
2. 前端传递需要返回当前前端的创建角色数量；`request.query_params.get`前端传递过来为字符串，需要强制转int；
3. 传递列表后的按照id排序方法：` Character.objects.filter(author = user_profile,).order_by('id')`，若想逆向排序，则`order_by('-id')`；
4. 返回前20个元素，直接在后面限定长度，`.order_by('-id')[items_count:items_count + 20]`；

```py
from django.contrib.auth.models import User
from rest_framework.response import Response #API 响应
from rest_framework.views import APIView#API 视图框架

from web.models.character import Character
from web.models.user import UserProfile


class GetListCharacterView(APIView):
    def get(self, request):
        try:
            items_count = int(request.query_params.get('items_count'))#从 URL 查询参数中获取 items_count，并将其转换为整数。
            user_id = int(request.query_params.get('user_id'))
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            characters_raw = Character.objects.filter(
                author = user_profile,
            ).order_by('-id')[items_count:items_count + 20]#按照id正序排序，-id为逆向；并返回前20个元素
            characters = []
            for character in characters_raw:
                author = character.author
                characters.append({
                    'id': character.id,
                    'name': character.name,
                    'profile': character.profile,
                    'photo': character.photo.url,#切记图片为.url
                    'background_image': character.background_image.url,
                    'author': {
                        'user_id':author.user_id,
                        'username':author.user.username,
                        'photo':author.photo.url,
                    }
                })
            return Response({
                'result':'success',
                'user_profile':{
                    'user_id':user_id,
                    'username':user.username,
                    'profile':user_profile.profile,
                    'photo':user_profile.photo.url,
                },
                'characters':characters,
            })
        except:
            return Response({
                'result': '系统错误，请稍后重试',
            })
```
5. 添加路由` path('/api/create/character/get_list/',GetListCharacterView.as_view()),`

#### 1.2 实现前端
1. 创建文件夹：`AIFriends/frontend/src/views/user/space/components/`；
2. 在该目录下创建空组件：`UserInfoField.vue`：展示个人信息；
3. 文件夹：`AIFriends/frontend/src/components/character/`；
4. 目录下创建空组件：`Character.vue`：展示角色卡片；
5. 在`AIFriends/frontend/src/views/user/space/SpaceIndex.vue`中对接后端。

##### 1.2.1 对接后端 SpaceIndex.vue
`AIFriends/frontend/src/views/user/space/SpaceIndex.vue`
1. 垂直布局；
2. 将角色信息加载进来；
3. 改成网格布局：可以根据屏幕宽度自动决定每行的元素数量，并将元素均匀排列在屏幕上；当最后一行元素不足时会左对齐；`<div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">`;
4. 添加哨兵，标记渲染出卡片的底端，并用哨兵来实现动态加载；当哨兵在可视窗口内时，继续加载渲染，当哨兵不可见时，停止加载，随着滚动页面，继续加载或停止加载卡片；
5. 判断当前是否有角色在加载，当有角色在加载时显示加载中；
6. 判断是否还有多余角色；
7. 实现哨兵加载逻辑循环：
      1. async加载函数；
      2. `characters.value.push(...newCharacters)`//...为展开列表；
      3. 监听器：`observer = new IntersectionObserver`；root 判断视窗是否交叉，rootMargin 缩小检测视窗范围提前判断,threshold:交叉的大小为某个值的时候触发
      4. 组件移除前释放资源`onBeforeUnmount`；
      5. `observer?.disconnect()` ,解绑监听器
8. 信息渲染需要传递变量，给`<UserInfoFile/>`加:变量；
9. 注意前端路由以`/`开头:`  const res = await api.get('/api/create/character/get_list/'`;
10. 角色循环渲染
```py
<script setup>

import UserInfoField from "@/views/user/space/components/UserInfoField.vue";
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import {useRoute} from "vue-router";
import api from "@/js/http/api.js";
import Character from "@/components/character/Character.vue";

const userProfile = ref(null)
const characters = ref([])
const isLoading = ref(false) //判断当前是否有角色在加载
const hasCharacter = ref(true) //判断是否还有多余角色
const sentinelRef = useTemplateRef('sentinel-ref')
const route = useRoute()

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}


async function loadMore(){
  if(isLoading.value || !hasCharacter.value) return //无角色返回
  isLoading.value = true

  let newCharacters= [] //定义从云端在家的函数
  try{
    const res = await api.get('/api/create/character/get_list/',{
      params:{
        items_count: characters.value.length,
        user_id: route.params.user_id,
      }
    })
    const data = res.data
    if(data.result === 'success'){
      userProfile.value = data.user_profile //与api/create/character/get_list/返回值一致
      newCharacters = data.characters
    }
  }catch (err){
  }finally { //实现循环加载逻辑
    isLoading.value = false
    if(newCharacters.length === 0){//云端无可加载函数
      hasCharacter.value = false
    }else{
      characters.value.push(...newCharacters)//...为展开列表；
      await nextTick() //等待渲染完，判断哨兵能否被看到

      if(checkSentinelVisible()){
        await loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()

  observer = new IntersectionObserver(//监听器 循环加载
      entries => {
        entries.forEach(entry => {
          if(entry.isIntersecting) {
            loadMore()
          }
        })
      },
      {root:null,rootMargin:'2px',threshold:0}//root 判断视窗是否交叉，rootMargin 缩小检测视窗范围提前判断,threshold:交叉的大小为某个值的时候触发
  )
  observer.observe(sentinelRef.value)
})

function removeCharcater(characterId){
  characters.value = characters.value.filter(c => c.id !== characterId) //取出所有id!==characterId的值付给原来的值，效果保留所有不相等的元素，删除别的
}

onBeforeUnmount(() => { //组件移除前释放资源
  observer?.disconnect()  // 解绑监听器
})
</script>

<template>
  <div class="flex flex-col items-center mb-12">
    <UserInfoField :userProfile="userProfile"/>
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">
      <!--循环渲染角色  -->
      <Character
          v-for="character in characters"
          :key="character.id"
          :character="character"
          :canEdit="true"
          @remove="removeCharcater"
      />
    </div>
    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasCharacter" class="text-gray-500 mt-4">没有更多的角色了</div>
  </div>
</template>

<style scoped>

</style>
```

##### 1.2.2 UserInfoField.vue 个人信息
1. ``AIFriends/frontend/src/views/user/space/components/UserInfoFie.vue`
2. `defineProps(['userProfile'])`，传递接口；
3. 渲染前判断userProfile是否为空，`<div v-if="userProfile" class="w-44 rounded-full">`，不为空加载图片`<img :src="userProfile.photo" alt="">`；
```py
<script setup>
defineProps(['userProfile'])
</script>


<template>
  <div v-if="userProfile" class="flex mt-12 gap-8">
    <div class="avatar">
      <div class="w-44 rounded-full">
        <img :src="userProfile.photo" alt="">
      </div>
    </div>
    <div class="flex flex-col justify-center w-64 h-44">
      <div class="text-2xl font-bold line-clamp-1 break-all">{{userProfile.username}}</div>
      <div class="=text-sm text-gray-500 mt-5">MyAIFriends号：{{ userProfile.user_id }}</div>
      <div class="text-sm h-20 line-clamp-4 break-all">{{ userProfile.profile }}</div>
    </div>
  </div>
</template>

<style scoped>

</style>
```

##### 1.2.2 Character.vue 展示角色
1. 接收变量，因为有多余一个，所以用`const props=defineProps(['character','canEdit'])`；
2. 由卡片和用户名组成，<div>将两者放在一起；
3. 鼠标移动到角色页面时，角色放大：
      1. 判断鼠标是否悬浮：`const isHover = ref(flase)`；
      2. 给<div>组件绑定两个事件，鼠标在为真，移出为假：` @mouseover="isHover=true" @mouseout="isHover=false`；
      3. 给img绑定逻辑`:class="{'scale-120':isHover}">`,isHover为真，将图片放大到120%；
      4. 加入过渡动画`class="transition-transform duration-300"`用300ms发生改变；
      5. 实现渐变色，最下面是黑色40%透明，最上面是完全透明：`bg-linear-to-t from-black/40 to-transparent`；
      6. 加删除和修改按钮；
      7. 页面跳转需要用`<RouterLink :to="{name:'update-character',params:{character_id: character.id}}"`;
      8. 透明背景色`bg-transparent`；
4. 在角色页面加头像，头像用圆环环住：` <div class="w-16 rounded-full ring-3 ring-base-300">`；ring-base为颜色；
5. 用户头像和名字加超链接跳转到个人主页；
6. 增加删除逻辑：需要删除后台和前端:
      1. `frontend/src/views/user/space/SpaceIndex.vue`；
      2. 取出所有id!==characterId的值付给原来的值：` characters.value = characters.value.filter(c => c.id !== characterId)`;效果保留所有不相等的元素，删除别的;
      3. 将母函数传递给子函数的方式：`@remove="removeCharcater"`，绑定一个事件；
      4. 子组件接收方式：``const emit = defineEmits(['remove'])；
      5. `emit('remove',props.character.id)`;/调用函数，传参数;
```py
<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";

const props=defineProps(['character','canEdit'])//接收变量
const emit = defineEmits(['remove'])//接收响应
const isHover = ref(false)//判断是否悬浮
const user = useUserStore()

async function handleRemoveCharacter(){
  try{
    const res = await api.post('/api/create/character/remove/',{//发送请求
      character_id:props.character.id,
    })
    if(res.data.result === 'success'){
      emit('remove',props.character.id)//调用函数，传参数
    }
  }catch (err){
    console.log(err)
  }
}
</script>

<template>
  <div>
    <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false">
      <div class="w-60 h-100 rounded-2xl relative">
        <img :src="character.background_image" class="transition-transform duration-300" :class="{'scale-120': isHover}" alt="">
        <div class="absolute left-0 top-50 w-60 h-50 bg-linear-to-t from-black/40 to-transparent"></div>
        <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-0 top-45">
          <RouterLink :to="{name:'update-character',params:{character_id: character.id}}" class="btn btn-circle btn-ghost bg-transparent">
            <UpdateIcon/>
          </RouterLink>
          <button @click="handleRemoveCharacter" class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon/>
          </button>
        </div>

        <div class="absolute left-4 top-48 avatar">
          <div class="w-16 rounded-full ring-3 ring-base-300">
            <img :src="character.photo" alt="">
          </div>
        </div>
        <div class="absolute left-24 right-4 top-55 text-white font-bold line-clamp-1 break-all">
          {{character.name}}
        </div>
        <div class="absolute left-4 right-4 top-68 text-white line-clamp-4 break-all">
          {{character.profile}}
        </div>
      </div>
    </div>
    <RouterLink :to="{name:'user-space-index',params:{user_id:character.author.user_id}}" class="flex items-center mt-4 gap-2 w-60">
      <div class="avatar">
        <div class="w-7 rounded-full">
          <img :src="character.author.photo" alt="">
        </div>
      </div>
      <div class="text-sm line-clamp-1 break-all">{{character.author.username}}</div>
    </RouterLink>
  </div>
</template>

<style scoped>

</style>
```

#### 1.3 将前端代码打包到后端

### 2. 实现首页
#### 2.1 创建后端 index.py
1. 在`AIFriends/backend/web/views/homepage/`软件包目录下实现：index.py：返回所有角色列表;
2. 添加路由
```py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from web.models.character import Character


class HomepageIndexView(APIView):
    def get(self, request):
        try:
            items_count = int(request.query_params.get('items_count'))
            characters_raw = Character.objects.all().order_by('-id')[items_count:items_count+20]
            characters = []
            for character in characters_raw:
                author = character.author
                characters.append({
                    'id': character.id,
                    'name': character.name,
                    'profile': character.profile,
                    'photo': character.photo.url,
                    'background_image': character.background_image.url,
                    'author': {
                        'user_id':author.user.id,
                        'username': author.user.username,
                        'photo': author.photo.url,
                    }
                })
            return Response({
                'results': 'success',
                'characters': characters
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
```
`    path('api/homepage/index/',HomepageIndexView.as_view()),
`

#### 2.2 实现前端 HomepageIndex.vue
实现AIFriends/frontend/src/views/homepage/HomepageIndex.vue。


