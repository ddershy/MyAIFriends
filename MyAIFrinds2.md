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

```html
<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import Character from "@/components/character/Character.vue";

const characters = ref([])
const isLoading = ref(false)
const hasCharacter = ref(true)
const sentinelRef = useTemplateRef('sentinel-ref')

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

async function loadMore(){
  if (isLoading.value || !hasCharacter.value) return
  isLoading.value=true

  let newCharacters =[]
  try{
    const res = await api.get('/api/homepage/index/',{
      params:{
        items_count: characters.value.length,
      }
    })
    const data = res.data
    if(data.result === 'success'){
      newCharacters = data.characters
    }
  }catch (err){
    console.log(err)
  }finally {
    isLoading.value=false
    if(newCharacters.length === 0){
      hasCharacter.value = false
    }else{
      characters.value.push(...newCharacters)
      await nextTick()

      if(checkSentinelVisible()){
        await loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()

  observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {//能看到监听器就加载一遍
          if(entry.isIntersecting){
            loadMore()
          }
        })
      },
      {root:null,rootMargin:'2px',threshold:0}
  )

  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

</script>

<template>
  <div class="flex flex-col items-center mb-12">
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">
      <Character
          v-for="character in characters"
          :key="character.id"
          :character="character"
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

#### 2.3 添加搜索功能
在`AIFriends/frontend/src/components/navbar/NavBar.vue`中添加搜索逻辑：
1. 点击搜索按钮后，打开首页，并将搜索文本添加到url的query参数中。
2. 监听route.query.q，并将最新值赋给searchQuery。这样刷新页面后，搜索文本才能自动填充到搜索框内。   

##### 2.3.1 NavBar.vue
1. 增加变量保存在搜索框中输入的内容，`const searchQuery = ref('')`；
2. 将变量绑定在输入搜索栏里：`<input v-model="searchQuery" class="input join-item rounded-l-full " placeholder="搜索你感兴趣的内容" />` ；
3. 搜索函数`function handleSerch()`；
4. 将搜索栏变成一个表单，`          <form @submit.prevent="handleSerch" class="join w-4/5 flex justify-center">`;@submit指可以用回车键触发搜索，.prevent为搜索后不得刷新页面，handleSearch为触发的函数；
5. 回车后希望将信息放在url中并打开首页：
   1. 打开首页，router
   2. 将输入的内容放在q中，
   3. q在url中，
```js
function handleSerch(){
  router.push({
    name:'home-index',
    query:{
      q: searchQuery.value.trim()//删前后空格，并将searchQuery的内容放在q中
    }
  })
}
```
6. 搜索框内保留剛剛輸入的内容 route
```js
const route = useRoute()
watch(() => route.query.q, newQ =>{
  searchQuery.value = newQ ||''
})
```

```html
<script setup>

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
import {useUserStore} from "@/stores/user.js";
import UserMenu from "@/components/navbar/UserMenu.vue";
import {ref, watch} from "vue";
import Router from "@/router/index.js";
import {useRoute, useRouter} from "vue-router";

const user = useUserStore()//引入刚定义的函数
const searchQuery = ref('')
const router = useRouter()
const route = useRoute()

watch(() => route.query.q, newQ =>{
  searchQuery.value = newQ ||''
})

function handleSerch(){
  router.push({
    name: 'home-index',
    query:{
      q: searchQuery.value.trim()//删前后空格，并将searchQuery的内容放在q中
    }
  })
}
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <nav class="navbar w-full bg-base-100 shadow-sm">
        <div class="navbar-start">
          <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <MenuIcon/>
          </label>
          <div class="px-2 font-bold text-xl">AIFriends</div>
        </div>
        <div class="navbar-center w-4/5 max-w-180 flex justify-center">
          <form @submit.prevent="handleSerch" class="join w-4/5 flex justify-center">
            <input v-model="searchQuery" class="input join-item rounded-l-full " placeholder="搜索你感兴趣的内容" />
            <button class="btn join-item rounded-r-full gap-0">
              <SearchIcon/>
              搜索
            </button>
          </form>
        </div>
        <div class="navbar-end">
          <RouterLink v-if="user.isLogin()" :to="{name:'create-index'}" active-class="btn-active" class="btn btn-ghost text-lg mr-6">
            <CreateIcon/>
            创作
          </RouterLink>
          <RouterLink v-if="user.hasPulledUserInfo &&!user.isLogin()" :to="{name:'user-account-login-index'}" active-class="btn-active" class="btn btn-ghost text-lg">
            登录
          </RouterLink>
          <UserMenu v-else-if="user.isLogin()"/>
        </div>
      </nav>
      <slot></slot>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-54">
        <ul class="menu w-full grow">
          <li>
            <RouterLink :to="{name: 'home-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="首页">
              <HomepageIcon/>
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">首页</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{name: 'friend-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="好友">
              <FriendIcon/>
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">好友</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{name: 'create-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="创作">
              <CreateIcon/>
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">创作</span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>

```
##### 2.3.2 实现搜索 HomepageIndex.vue
1. 在HomepageIndex.vue添加监听内容，watch；
```js
watch(() => route.query.q, newQ =>{//当q发生改变，刷新整个页面内容
  reset()
})
```
2. 当q发生改变刷新整个首页内容，添加辅助函数`function reset(){`
```js
function reset(){
  characters.value=[] //把之前元素清空
  isLoading.value = false
  hasCharacter.value = true
  loadMore()
}
```
3. 每次reset需要把前端内容传递给后端`try->search_query`
```js
try{
    const res = await api.get('/api/homepage/index/',{
      params:{
        items_count: characters.value.length,
        search_query:route.query.q ||''
      }
    })
    ...
}
```
```html
<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef, watch} from "vue";
import api from "@/js/http/api.js";
import Character from "@/components/character/Character.vue";
import {useRoute} from "vue-router";

const characters = ref([])
const isLoading = ref(false)
const hasCharacter = ref(true)
const sentinelRef = useTemplateRef('sentinel-ref')
const route = useRoute()

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

async function loadMore(){
  if (isLoading.value || !hasCharacter.value) return
  isLoading.value=true

  let newCharacters =[]
  try{
    const res = await api.get('/api/homepage/index/',{
      params:{
        items_count: characters.value.length,
        search_query:route.query.q ||''
      }
    })
    const data = res.data
    if(data.result === 'success'){
      newCharacters = data.characters
    }
  }catch (err){
    console.log(err)
  }finally {
    isLoading.value=false
    if(newCharacters.length === 0){
      hasCharacter.value = false
    }else{
      characters.value.push(...newCharacters)
      await nextTick()

      if(checkSentinelVisible()){
        await loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()

  observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {//能看到监听器就加载一遍
          if(entry.isIntersecting){
            loadMore()
          }
        })
      },
      {root:null,rootMargin:'2px',threshold:0}
  )

  observer.observe(sentinelRef.value)
})

function reset(){
  characters.value=[] //把之前元素清空
  isLoading.value = false
  hasCharacter.value = true
  loadMore()
}

watch(() => route.query.q, newQ =>{//当q发生改变，刷新整个页面内容
  reset()
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

</script>

<template>
  <div class="flex flex-col items-center mb-12">
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">
      <Character
          v-for="character in characters"
          :key="character.id"
          :character="character"
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
##### 2.3.3 传递给后端 backend/web/views/homepage/index.py

1. 获取前端内容`            search_query = request.query_params.get('search_query','').strip()`;
2. 名字或者简介匹配都可以呈现：`Q(name__icontains=search_query)  |  Q(profile__icontains=search_query)  ` Django自带；`contains`匹配，`icontains`忽略大小写后匹配；
3. characters_raw = queryset.order_by('-id')[items_count:items_count+20]

```py
    def get(self, request):
        try:
            items_count = int(request.query_params.get('items_count'))
            search_query = request.query_params.get('search_query','').strip()
            if search_query:
                queryset  = Character.objects.filter(
                    Q(name__icontains=search_query)  |  Q(profile__icontains=search_query)
                )
            else:
                queryset = Character.objects.all() #所有内容
            characters_raw = queryset.order_by('-id')[items_count:items_count+20]
```

### 3. 实现好友页面
#### 3.1 创建后端
##### 3.1.1 创建数据库 friend.py
在`AIFriends/backend/web/models/friend.py`中创建Friend数据库。

1. 引入数据库包`from django.db import models`;
2. 短期记忆`    memory = models.TextField(default="",max_length=5000,blank=True,null=True)`；
3. 返回格式`        return f"{self.character.name} - {self.me.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"`;
```py
from django.db import models
from django.utils.timezone import now, localtime

from web.models.character import Character
from web.models.user import UserProfile


class Friend(models.Model):
    me = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    memory = models.TextField(default="",max_length=5000,blank=True,null=True)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.character.name} - {self.me.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"
```
##### 3.1.2 在admain中加friend数据库
1. `backend/web/admin.py`
```py
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
    
```

2. 在后端同步数据库
`AIFriends\backend> python .\manage.py makemigrations
AIFriends\backend> python .\manage.py migrate   
`


##### 3.1.3  创建views 
在软件包`AIFriends/backend/web/views/friend/`目录下实现：
1. `get_or_create.py`：如果有该好友，则返回；如果没有，则创建并返回

```py
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
```
2. `remove.py`：删除好友

```py
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
```

3. `get_list.py`：获取好友列表

```py
# 导入 DRF 的 Response 用于构造接口返回数据
from rest_framework.response import Response
# 导入 DRF 的 APIView 基类
from rest_framework.views import APIView
# 设置接口权限（必须登录）
from rest_framework.permissions import IsAuthenticated

# 导入好友关系模型
from web.models.friend import Friend


# 定义“获取好友列表”的接口
class GetListFriendsView(APIView):
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
                        'author': {
                            'user_id': author.user_id,  # 作者关联的用户ID
                            'username': author.user.username,  # 作者用户名
                            'photo': author.photo.url,  # 作者头像URL
                        },
                    },
                })

            return Response({
                'result': 'success',
                'friends': friends,
            })

        except:
            return Response({
                'result': '系统错误，请稍后重试',
            })
```

4. 添加路由`backend/web/urls.py`
```py
  path('api/friend/get_or_create/',GetOrCreateFriendView.as_view()),
    path('api/friend/remove/',RemoveFriendView.as_view()),
    path('api/friend/get_list/',GetListCharacterView.as_view()),
```

#### 3.2 实现前端
##### 3.2.1 创建聊天界面组件
目录`AIFriends/frontend/src/components/character/chat_field/`目录下创建：
1. ChatField.vue组件：显示聊天界面
      1. 获取从母组件取得的信息；
      2. 创建文件框及其引用`<dialog ref="modal-ref" class="modal">`;
      3. 暴漏显示函数；
      4. 将聊天框组件引入`frontend/src/components/character/Character.vue`;`    <ChatField ref="chat-field-ref"/>`，

```html
<!-- frontend/src/components/character/Character.vue -->
<script setup>
import {ref, useTemplateRef} from "vue";
import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

const props=defineProps(['character','canEdit'])//接收变量
const emit = defineEmits(['remove'])//接收响应
const isHover = ref(false)//判断是否悬浮
const user = useUserStore()
const router = useRouter()

async function handleRemoveCharacter(){
  try{
    const res = await api.post('/api/create/character/remove/',{//发送请求
      character_id:props.character.id,
    })
    if(res.data.result === 'success'){
      emit('remove',props.character.id)//调用函数，传参数
    }
  }catch (err){
  }
}

const charFieldRef = useTemplateRef('chat-field-ref')
const friend = ref(null) //存储传递过来的朋友

async function openChatFiled() {//打开聊天框的逻辑
  if(!user.isLogin()){//没登陆
    await router.push({
      name:'user-account-login-index'//弹到登录界面
    })
  } else{
    try{
      const res = await  api.post('/api/friend/get_or_create/',{
        character_id:props.character.id,
      })
      const data = res.data
      if(data.result === 'success'){
        friend.value = data.friend //先保存
        charFieldRef.value.showModal()
      }
    }catch (err){
      console.log(err)
    }
  }
}
</script>

<template>
  <div>
    <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false" @click="openChatFiled">
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
    <ChatField ref="chat-field-ref" :friend="friend"/>
  </div>
</template>

<style scoped>

</style>
```
  5. 将模态框背景图片设置成聊天背景：
```py
const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})
```

```html
<!-- ChartField.vue -->
<script setup>
import {computed, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";

const props = defineProps(['friend'])
const modalRef= useTemplateRef('modal-ref')

function showModal(){
  modalRef.value.showModal()
}

const modalStyle = computed(() => {//将模态框背景图片设置成聊天背景：
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover', //大小覆盖
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute top-1 right-1">✕</button>
      <InputField />
      <CharacterPhotoField v-if="friend" :character="friend.character"/>
    </div>
  </dialog>
</template>

<style scoped>

</style>
```

2. input_field/InputField.vue组件：聊天输入框
   1. input的提示文字：`placeholder="文本输入..."`;
   2. input毛玻璃:`class =backdrop-blur-smtext-white`
   3. 实现发送和开麦功能；
   4. 实现左上角头像和用户名；
```html
<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
</script>

<template>
  <div class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        class="input bg-black/30  backdrop-blur-smtext-white text-white w-full h-full rounded-2xl"
        type="text"
        placeholder="文本输入..."
    >
    <div class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon/>
    </div>
    <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon/>
    </div>
  </div>
</template>

<style scoped>

</style>
```
3. character_photo_field/CharacterPhotoField.vue组件：虚拟角色头像
```html
<script setup>
defineProps(['character'])
</script>

<template>
  <div class="absolute letf-1 max-w-48 top-6 h-10 w-fit rounded-full bg-black/50 flex items-center gap-2 px-2">
    <div class="avatar">
      <div class="w-8 rounded-full">
        <img :src="character.photo" alt="">
      </div>
    </div>
    <div class="text-white text-sm line-clamp-1 break-all">
      {{ character.name }}
    </div>
  </div>
</template>

<style scoped>

</style>
```

##### 3.2.2 实现好友列表页面 FriendIndex.vue
实现`AIFriends/frontend/src/views/friend/FriendIndex.vue`。
1. 获取好友列表、设置哨兵、渲染、同界面渲染逻辑；
2. 实现删除好友功能：
   1. 在好友页面加删除按钮；
   2. 在好友列表实现删除`async function removeFried(friendID){   friends.value = friends.value.filter(f => f.id !== friendID)} `;
   3. 修改<Character>，增加接收变量:`const props=defineProps(['character','canEdit','canRemoveFriend','firendID'])`
   4. 在<Character>内增加删除函数:
```js
async function handleRemoveFriend(){
  try{
    const res = await api.post('/api/friend/remove/',{
      friend_id: props.friendID,
    })
    if(res.data.result === 'success')
      emit('remove',props.friendID)
  }catch (err){
    console.log(err)
  }
}

<div v-if="canRemoveFriend" class="absolute right-0 top-50">
          <button @click="handleRemoveFriend" class="btn btn-ghost btn-circle bg-transparent">
            <RemoveIcon/>
          </button>
        </div>

```
  
3. 阻止卡片内的点击事件向上传播即因为删除键在卡片上，点击删除后会同时触发卡片的逻辑，需阻止<Character>：@click.top:
`<button @click.stop="handleRemoveFriend" class="btn btn-ghost btn-circle bg-transparent">`;
     1. 绑定后发现只触发get_or_creat，因为`openChatFiled`绑定在了最外层，修改到背景容器 <div class="w-60 h-100 rounded-2xl relative"> 上可正确进行；
     2. 给超链接也绑定阻止调用逻辑`          <RouterLink @click.stop >`


4. character= models.ForeignKey(Character, on_delete=models.CASCADE)：当删除character时，会自动将关联的friend删掉。
```html
<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import Character from "@/components/character/Character.vue";
import api from "@/js/http/api.js";

const friends = ref([])
const isLoading = ref(false)
const hasFriends = ref(true)
const sentinelRef =useTemplateRef('sentinel-ref')

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}


async function loadMore(){
  if(isLoading.value || !hasFriends.value) return
  isLoading.value = true

  let newFriends=[]
  try{
    const res = await api.get('/api/friend/get_list/',{
      params:{
        items_count:friends.value.length,
      }
    })
    const data= res.data
    if(data.result === 'success'){
      newFriends = data.friends
    }
  }catch (err) {
    console.log(err)
  }finally {
    isLoading.value=false
    if(newFriends.length === 0){
      hasFriends.value = false
    }else{
      friends.value.push(...newFriends)
      await nextTick()

      if(checkSentinelVisible())
        await loadMore()
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()  // 加载新元素

  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadMore()
        }
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )

  //监听哨兵元素， 每次哨兵被看到时，都会触发一次
  observer.observe(sentinelRef.value)
})

async function removeFriend(friendID){
  friends.value = friends.value.filter(f => f.id !== friendID)
}

onBeforeUnmount(() => {
  observer?.disconnect()  // 解绑监听器
})
</script>

<template>
  <div class="flex flex-col items-center mb-12">
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">
      <Character
          v-for="friend in friends"
          :key="friend.id"
          :character="friend.character"
          :canRemoveFriend="true"
          :friendID="friend.id"
          @remove="removeFriend"
      />
    </div>

    <div ref="sentinel-ref" class="h-2 wt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasFriends" class="text-gray-500 mt-4">没有更多的聊天了</div>
  </div>
</template>

<style scoped>

</style>
```

## 六、文字聊天

### 0. 补丁
修复bug：在首页点进其他用户的个人空间后，再去右上角点击自己的个人空间，页面内容没更新。
`frontend/src/views/user/space/SpaceIndex.vue` 增加监听space id的逻辑，当id发生变化后自动刷新页面。
```js
function reset(){
  userProfile.value=null
  characters.value = []
  isLoading.value= false
  hasCharacter.value = true
  loadMore()
}

watch(() => route.params.user_id,() => {
  reset()
})
```
### 1. 实现聊天后端

安装`langgraph`：`pip install langgraph langchain langchain-openai`

安装`python-dotenv`：`pip install python-dotenv`，负责加载环境变量,不将api key放在代码中


#### 1.1 创建数据库
在`AIFriends/backend/web/models/friend.py`中创建数据库Message。

```py

class Message(models.Model):
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)
    user_message= models.TextField(max_length = 500)
    input = models.TextField(max_length = 500)
    output = models.TextField(max_length = 500)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    create_time = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"{self.friend.character.name} - {self.friend.me.user.username} - {self.user_message[:50]} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"
```

为了可以在管理员页面看到Message页面，需要将Message加入admin中。
```py
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('friend',)
```
`\backend> python .\manage.py makemigrations  `；` python .\manage.py migrate  `

#### 1.2 实现views
1. 创建文件：`AIFriends/backend/.env`，用来存环境变量。
   1. 在AIFriends/.gitignore中添加*.env。
   2. 如果git status后仍然有.env，可以执行：git rm --cached -f backend/.env来清除对.env的索引。
   3. 在文件中添加：
```py
API_KEY=""  # 替换成自己创建的API Key
API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

2. 在`AIFriends/backend/backend/settings.py`开头添加：

```py
from dotenv import load_dotenv

load_dotenv()
```
然后要重启Django服务，这样才可以加载环境变量。

3. 实现 `AIFriends/backend/web/views/friend/message/chat/chat.py`。 message和chat均为软件包；前端发送后，后端有API可以接收消息。软件包、软件包、文件。
   1. 只能修改自己用户下的好友，所以需要核对用户信息
```py
#/chat/chat.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不得为空',
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friends.exists():
            return Response({
                'result': '好友不存在',
            })
```
  2. 为了维护代码，将LangGraph逻辑存放在`backend/web/views/friend/message/chat/graph.py`
     1. LangGraph用图来封装逻辑
     2. ChatOpenAI#连接大模型
     3. `langgraph`数据类型：
```py
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```
```py
import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class ChatGraph: #用于封装函数逻辑
    @staticmethod
    def create_app():
        llm = ChatOpenAI( #连接大模型
            model='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'), #gentenv：获取环境变量
            openai_api_base=os.getenv('API_BASE') #访问的URL
        )

        class AgentState(TypedDict): #数据类型
            messages: Annotated[Sequence[BaseMessage], add_messages] #本质为条件更丰富的字典，add_message为它的合并方式，将agent的结果追加在sequence末尾

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages']) #存储返回的model
            return {'messages': [res]} #将res追加到message的末尾

        graph = StateGraph(AgentState) #StateGraph创建状态图，()内为维护的状态类型
        graph.add_node('agent',model_call) #定义自己加入的agent节点,(名字,节点函数)

        #加上连接的两条边 staet ----> agent ----> end
        graph.add_edge(START,'agent')
        graph.add_edge('agent', END)
        
        return graph.compile()
```
  3. 封装完LangGraph后,可以在`AIFriends/backend/web/views/friend/message/chat/chat.py`下调用：
```py
from langchain_core.messages import HumanMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph


class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不得为空',
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friends.exists():
            return Response({
                'result': '好友不存在',
            })

        # 对接大模型
        friend = friends.first()
        app = ChatGraph.create_app()

        #构造输入,构造刚刚定义的字典
        inputs ={
            'messages': [HumanMessage(message)] #和构造的函数内变量名对应，封装传入的消息
        }

        res = app.invoke(inputs) #调用计算流程
        print(res['messages'][-1].content) #会返回一个
        return Response({
            'result':'success',
        })
```
  4. 添加路由`backend/web/urls.py`：`path('api/friend/message/chat',MessageChatView.as_view()),`

### 2. 实现聊天前端
`frontend/src/components/character/chat_field/input_field/InputField.vue`
1. 打开聊天页面后，自动聚焦输入框。
   1. 定义一个输入框和相关引用 
   2. 将这个函数逻辑暴露出去
```js
const inputRef = useTemplateRef('input-ref') //定义一个输入框

function focus(){
  inputRef.value.focus()
}

defineExpose({ //当母组件一调用聊天框函数，这个逻辑应当被执行。因为需要在母组件调用子组件，所以需要将这个部分暴漏出去
  focus,
})
```
   3. 在母组件中添加调用逻辑`frontend/src/components/character/chat_field/ChatField.vue`
```js
const inputRef = useTemplateRef('input-ref') //接收来自子组件的函数

async function showModal(){
  modalRef.value.showModal()

  await nextTick() //等待元素渲染
  inputRef.value.focus()
}
.....
      <InputField ref="input-ref"/>
```


2. 对接并调试后端api `frontend/src/components/character/chat_field/input_field/InputField.vue`
   1. 发送事件，当点击按钮/回车的时候可以调用这个函数，故需要在按钮上绑定函数逻辑以及将div改成表单，且因为在按回车时不许刷新页面，所以为.prevent。添加绑定逻辑
```py
<template>
  <form @submit.prevent="handelSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        ref="input-ref"
        class="input bg-black/30  backdrop-blur-smtext-white text-white w-full h-full rounded-2xl"
        type="text"
        placeholder="文本输入..."
    >
    <div @click="handelSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon/>
    </div>
    <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon/>
    </div>
  </form>
</template>
``` 

  2. 添加`handleSend`函数逻辑，先添加响应式变量message获取到l聊天框内的内容；获取friend.id，需要在母组件（chatfiled）中添加逻辑`<InputField 
          v-if="friend"
          ref="input-ref"
          :friendID="friend.id"
      />`

此时在调试时我一直在报403的错误，最终的解决方法是将前端url最后加了'/'。
```py
<!--frontend/src/components/character/chat_field/input_field/InputField.vue-->

<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

const props = defineProps(['friendID'])//接收来自母组件的friendID
const inputRef = useTemplateRef('input-ref') //定义一个输入框
const message = ref('') //获取聊天框内内容


function focus(){
  inputRef.value.focus()
}

async function handleSend(){
  const content = message.value.trim() //先取出内容
  if(!content) return
  message.value=''

  try { //给后端发送请求
    const res = await api.post('/api/friend/message/chat/',{ //神啊 为什么这里一定要加/，我当时修改了django版本
      friend_id:props.friendID,
      message: content,
    })
    console.log(res.data)
  }catch (err){
    console.log(err)
  }
}

defineExpose({ //当母组件一调用聊天框函数，这个逻辑应当被执行。因为需要在母组件调用子组件，所以需要将这个部分暴漏出去
  focus,
})
</script>

<template>
  <form @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        ref="inputRef"
        v-model="message"
        class="input bg-black/30  backdrop-blur-smtext-white text-white w-full h-full rounded-2xl"
        type="text"
        placeholder="文本输入..."
    >
    <div @click="handleSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon/>
    </div>
    <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon/>
    </div>
  </form>
</template>

<style scoped>

</style>
```

```py
<!--frontend/src/components/character/chat_field/ChatField.vue-->
<script setup>
import {computed, nextTick, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";

const props = defineProps(['friend'])
const modalRef= useTemplateRef('modal-ref')
const inputRef = useTemplateRef('input-ref') //接收来自子组件的函数

async function showModal(){
  modalRef.value.showModal()

  await nextTick() //等待元素渲染
  inputRef.value.focus()
}

const modalStyle = computed(() => {//将模态框背景图片设置成聊天背景：
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover', //大小覆盖
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute top-1 right-1">✕</button>
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendID="friend.id"
      />
      <CharacterPhotoField v-if="friend" :character="friend.character"/>
    </div>
  </dialog>
</template>

<style scoped>

</style>
```

### 3. 实现流式回复
#### 3.1 改造后端

1. 修改`graph.py`,在ChatOpenAI中添加参数
```py
# backend/web/views/friend/message/chat/graph.py

import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class ChatGraph: #用于封装函数逻辑
    @staticmethod
    def create_app():
        llm = ChatOpenAI( #连接大模型
            model='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'), #gentenv：获取环境变量
            openai_api_base=os.getenv('API_BASE'),#访问的URL
            streaming = True, # 流式输出
            model_kwargs = {
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        )

        class AgentState(TypedDict): #数据类型
            messages: Annotated[Sequence[BaseMessage], add_messages] #本质为条件更丰富的字典，add_message为它的合并方式，将agent的结果追加在sequence末尾

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages']) #存储返回的model
            return {'messages': [res]} #将res追加到message的末尾

        graph = StateGraph(AgentState) #StateGraph创建状态图，()内为维护的状态类型
        graph.add_node('agent',model_call) #定义自己加入的agent节点,(名字,节点函数)

        #加上连接的两条边 staet ----> agent ----> end
        graph.add_edge(START,'agent')
        graph.add_edge('agent', END)

        return graph.compile()
```
2. 实现`event_stream`生成器,未来消息从后端传到前端，由于http不是流式返回；需要将请求从SSE,请求为单次，但返回是流式；websocket 客户端和服务器端谁先发都行。大模型常用SSE。
```py
# backend/web/views/friend/message/chat/chat.py
import json

from langchain_core.messages import HumanMessage, BaseMessageChunk
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph


class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不得为空',
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friends.exists():
            return Response({
                'result': '好友不存在',
            })

        # 对接大模型
        friend = friends.first()
        app = ChatGraph.create_app()

        #构造输入,构造刚刚定义的字典
        inputs ={
            'messages': [HumanMessage(message)] #和构造的函数内变量名对应，封装传入的消息
        }

        # res = app.invoke(inputs) #调用计算流程  非流式回复
        # print(res['messages'][-1].content) #会返回一个

        # 流式回复： yield：生成器，每执行一次，会往下进行一个yield之前的内容；
            #生成器定义
        def event_stream():
            full_usage ={} #存储消耗量
            for msg,metadata in app.stream(inputs,stream_mode="messages"):
                if isinstance(msg,BaseMessageChunk): #消息是否是本次片段
                    if msg.content:#判断是否有消息
                        yield f"data:{json.dumps({'content':msg.content},ensure_ascii=False)}\n\n" #ensure_ascii=False 确保返回为unicode 看中文
                    if hasattr(msg,'usage_metadata') and msg.usage_metadata: #存储usage信息
                        full_usage = msg.usage_metadata
            yield 'data: [DONE]\n\n' #结束格式 data: [DONE]\n\n
            print(full_usage)

            #生成器执行
        for data in event_stream():
            print(data)

        return Response({
            'result':'success',
        })
```
