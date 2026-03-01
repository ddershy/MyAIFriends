<script setup>

import Photo from "@/views/create/character/components/Photo.vue";
import Name from "@/views/create/character/components/Name.vue";
import Profile from "@/views/create/character/components/Profile.vue";
import BackgroundImage from "@/views/create/character/components/BackgroundImage.vue";
import {ref, useTemplateRef} from "vue";
import {base64ToFile} from "@/js/utils/base64_to_file.js";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";
import {useUserStore} from "@/stores/user.js";

const user = useUserStore()
const router = useRouter()

const photoRef = useTemplateRef('photo-ref') //四个引用
const nameRef = useTemplateRef('name-ref')
const profileRef = useTemplateRef('profile-ref')
const bgImageRef = useTemplateRef('bgImage-ref')
const errorMessage =ref('')

//对接后端的函数
async function handleCreate(){
  const photo = photoRef.value.myPhoto //获取四个变量
  const name = nameRef.value.myName?.trim()//去掉前后空格,为空返回空，不空调用.trim()
  const profile = profileRef.value.myProfile?.trim()
  const bgImage = bgImageRef.value.myBGImage

  errorMessage.value = ''
  if(!photo){
    errorMessage.value='头像不得为空'
  }else if(!name){
    errorMessage.value='名字不得为空'
  }else if(!profile){
    errorMessage.value='角色简介不得为空'
  }else if(!bgImage){
    errorMessage.value='聊天背景不得为空'
  }else{
    const formData = new FormData()//对接后端，因为传文件创建一个FORM表单数据FormData
    formData.append('name',name)
    formData.append('profile',profile)
    formData.append('photo',base64ToFile(photo,'photo.png'))
    formData.append('background_image',base64ToFile(bgImage,'bgImage.png')) //key与`/api/create/character/create/`的变量一致

    try{
      const res = await api.post('/api/create/character/create/',formData)//对接后端的请求
      const data = res.data //获取返回结果
      if(data.result === 'success'){//成功自动跳转用户主页
        await router.push({
          name:'user-space-index',
          params:{
            user_id: user.id,
          }
        })
      }else{
        errorMessage.value = data.result
      }

    }catch (err){
      console.log(err)
    }
  }
}
</script>

<template>
  <div class="flex justify-center mt-18">
    <div class="card w-120 bg-base-200 shadow-sm">
      <div class="card-body">
        <h3 class="text-lg font-bold my-4">创建角色</h3>
        <Photo ref="photo-ref"/>
        <Name ref="name-ref"/>
        <Profile ref="profile-ref"/>
        <BackgroundImage ref="bgImage-ref"/>

        <p v-if="errorMessage" class="text-sm text-red-500">{{errorMessage}}</p>

        <div class="flex justify-center">
          <button @click="handleCreate" class="btn btn-neutral w-60 mt-2">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>