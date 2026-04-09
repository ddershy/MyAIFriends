<!--frontend/src/components/character/chat_field/input_field/InputField.vue-->

<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";
import flattenColorPalette from "tailwindcss/lib/util/flattenColorPalette";

const props = defineProps(['friendID'])//接收来自母组件的friendID
const inputRef = useTemplateRef('input-ref') //定义一个输入框
const message = ref('') //获取聊天框内内容
let  isProcessing = false //防止用户重复发消息

function focus(){
  inputRef.value.focus()
}

async function handleSend(){
  if(isProcessing) return
  isProcessing = true

  const content = message.value.trim() //先取出内容
  if(!content) return
  message.value=''

  try{
    await  streamApi('/api/friend/message/chat/',{
      body:{
        friend_id:props.friendID,
        message:content,
      },
      onmessage(data,isDone) {//用于接收消息
        if(isDone){
          isProcessing = false
        }else if(data.content){
          console.log(data.content)//文本内有消息没输出完则全部输出
        }
      },
      onerror(err){//用于接收错误
        isProcessing = false
      },
    }) //发送流式请求
  }catch(err){
    console.log(err)
    isProcessing = false //错误表示信息发送完毕
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