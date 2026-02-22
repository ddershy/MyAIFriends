<script setup>
import {useUserStore} from "@/stores/user.js";
import UserSpaceIcon from "@/components/navbar/icons/UserSpaceIcon.vue";
import UserLogoutIcon from "@/components/navbar/icons/UserLogoutIcon.vue";
import UserProfileIcon from "@/components/navbar/icons/UserProfileIcon.vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";

const user = useUserStore()
const router = useRouter()

function closeMenu() { //下拉后自动关闭菜单
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
}

async function handleLogout(){
  try {
    const ref = await api.post('/api/user/account/logout/')
    if(ref.data.result === 'success'){
      user.logout()
      await router.push({
          name: 'home-index'
        })
    }
  }
  catch (err){
  }
}
</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="avatar w-8 btn btn-circle w-8 h-8 mr-6">
      <div class="w-8 rounded-full">
        <img :src="user.photo" alt="" /> <!--变量的引用方式为‘:src = "usr.sth"’-->
      </div>
    </div>
      <ul tabindex="-1" class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm">
        <li>
          <RouterLink @click="closeMenu" :to="{name:'user-space-index',params: {user_id:user.id}}">
            <div class="avatar">
              <div class="w-9 rounded-full">
                <img :src="user.photo" alt="" /> <!--变量的引用方式为‘:src = "usr.sth"’-->
              </div>
            </div>
            <span class="text-base font-bold">{{user.username}}</span> <!--括号内放函数-->
          </RouterLink>
        </li>
        <li>
          <RouterLink @click="closeMenu"  :to="{name:'user-space-index',params:{user_id:user.id}}" class="text-sm font-bold py-3 "> <!--注意加user_id的参数-->
            <UserSpaceIcon/>
            个人空间
          </RouterLink>
        </li>
        <li>
          <RouterLink @click="closeMenu"  :to="{name:'user-profile-index'}" class="text-sm font-bold py-3 ">
            <UserProfileIcon/>
            编辑资料
          </RouterLink>
        </li>
        <li></li>
        <li>
          <a @click="handleLogout"  class="text-sm font-bold py-3 ">
            <UserLogoutIcon/>
            退出登录
          </a>
        </li>
      </ul>
    </div>
</template>

<style scoped>

</style>