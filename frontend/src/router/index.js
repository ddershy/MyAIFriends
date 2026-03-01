import { createRouter, createWebHistory } from 'vue-router'
import HomepageIndex from "@/views/homepage/HomepageIndex.vue";
import FriendsIndex from "@/views/friend/FriendsIndex.vue";
import CreateIndex from "@/views/create/CreateIndex.vue";
import NotFoundIndex from "@/views/error/NotFoundIndex.vue";
import LoginIndex from "@/views/user/account/LoginIndex.vue";
import RegisterIndex from "@/views/user/account/RegisterIndex.vue";
import SpaceIndex from "@/views/user/space/SpaceIndex.vue";
import ProfileIndex from "@/views/user/profile/ProfileIndex.vue";
import {useUserStore} from "@/stores/user.js";
import UpdateCharacter from "@/views/create/character/UpdateCharacter.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [//匹配顺序：自上而下
    { //路由字典
      path:'/',//根路径
      component:HomepageIndex,
      name:'home-index',
      meta:{
        needLogin: false,
      }
    },
    { //路由字典
      path:'/friend/',//根路径下好友路径
      component:FriendsIndex,
      name:'friend-index',
      meta:{
        needLogin: true,
      }
    },
    { //路由字典
      path:'/create/',
      component:CreateIndex,
      name:'create-index',
      meta:{
        needLogin: true,
      }
    },
    { //路由字典-创建角色
      path:'/create/character/update/:character_id/',//传递参数character_id
      component:UpdateCharacter,
      name:'update-character',
      meta:{
        needLogin: true,
      }
    },
    { //路由字典
      path:'/404/',
      component:NotFoundIndex,
      name:'404',
      meta:{
        needLogin: false,
      }
    },
    { //路由字典
      path:'/user/account/login',
      component:LoginIndex,
      name:'user-account-login-index',
      meta:{
        needLogin: false,
      }
    },
    { //路由字典
      path:'/user/account/register',
      component:RegisterIndex,
      name:'user-account-register-index',
      meta:{
        needLogin: false,
      }
    },
    { //路由字典
      path:'/user/space/:user_id', //':+P'=此处需要有一个参数P
      component:SpaceIndex,
      name:'user-space-index',
      meta:{
        needLogin: true,
      }
    },
    { //路由字典
      path:'/user/profile/',
      component:ProfileIndex,
      name:'user-profile-index',
      meta:{
        needLogin: true,
      }
    },
    {
      path:'/:pathMatch(.*)*',//正则表达式，可以匹配任意路径。
      component:NotFoundIndex,
      name:'not-found',
    }
  ],
})

router.beforeEach((to,form)=>{
  const user = useUserStore()
  if(to.meta.needLogin && user.hasPulledUserInfo && !user.isLogin()){
    return {
      name:'user-account-login-index',
    }
  }
  return true
})
export default router
