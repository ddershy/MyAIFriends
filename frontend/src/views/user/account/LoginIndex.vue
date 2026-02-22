<script setup>
import {useUserStore} from "@/stores/user.js";
import {ref} from "vue";
import {useRouter} from "vue-router";
import api from "@/js/http/api.js";

const username = ref('')
const password = ref('')
const user = useUserStore()
const errorMessage = ref('')
const router = useRouter()

async function handleLogin(){
  errorMessage.value=''
  if(!username.value.trim()){
    errorMessage.value='用户名不得为空'
  }else if(!password.value.trim()){
    errorMessage.value='密码不得为空'
  }else {
    try {
      const res = api.post('/api/user/account/login/',{ //api要定义
        username:username.value,
        password:password.value,
      })
      const data = (await res).data;
      if(data.result === 'success'){
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        await router.push({
          name: 'home-index'
        })
      }else{
        errorMessage.value = data.result
      }
    }
    catch (err){
    }
  }
}
</script>

<template>
    <div class="flex justify-center mt-30">
      <form @submit.prevent="handleLogin" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
        <label class="label">用户名</label>
        <input v-model="username" type="text" class="input" placeholder="用户名" />

        <label class="label">密码</label>
        <input v-model="password" type="password" class="input" placeholder="密码" />

        <button class="btn btn-neutral mt-4">登录</button>

        <p v-if="errorMessage" class="font-bold text-red-500 text-base">{{errorMessage}}</p>
        <div class="flex justify-end">
          <RouterLink :to="{name: 'user-account-register-index'}" class="btn btn-sm btn-ghost text-gray-500 mt-2">
            注册
          </RouterLink>
        </div>
      </form>
    </div>
</template>

<style scoped>

</style>

