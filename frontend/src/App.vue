<script setup>

import NavBar from "@/components/navbar/NavBar.vue";
import {onMounted} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";
import {useRoute, useRouter} from "vue-router";

const user = useUserStore()
const route = useRoute()
const router = useRouter()

onMounted(async ()=>{
  try {
    const res = await api.get('/api/user/account/get_user_info/')
    const data = res.data
    if (data.result === 'success') {
      user.setUserInfo(data)
    }
  }catch(err){
  }finally {
  //   无论如何都要执行
    user.setHasPulledUserInfo(true)
    if(route.meta.needLogin && !user.isLogin())
      await router.replace({
        name: 'user-account-login-index',
      })
  }
})
</script>

<template>
  <NavBar>
    <RouterView />  <!-- 根据index.js的组件开始匹配，将组件渲染在这里-->
  </NavBar>
</template>

<style scoped>

</style>
