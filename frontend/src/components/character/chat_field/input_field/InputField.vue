<!--frontend/src/components/character/chat_field/input_field/InputField.vue-->

<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";
import flattenColorPalette from "tailwindcss/lib/util/flattenColorPalette";

const props = defineProps(['friendID'])//接收来自母组件的friendID
const emit = defineEmits(['pushBackMessage','addToLastMessage']) //接收函数
const inputRef = useTemplateRef('inputRef') //定义一个输入框
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

  //每次一回车会存储两次变化：1. 用户自己的消息;2. ai回复的消息
  emit('pushBackMessage',{role:'user',content:content,id:crypto.randomUUID()})//随机字符串
  emit('pushBackMessage',{role:'ai',content:'',id:crypto.randomUUID()})

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
          //每次流式收到一条消息，就将这条消息流式补充到最后一条消息上
          emit('addToLastMessage',data.content)
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