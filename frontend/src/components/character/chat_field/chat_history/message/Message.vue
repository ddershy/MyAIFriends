<!--frontend/src/components/character/chat_field/chat_history/message/Message.vue-->

<script setup>
import {useUserStore} from "@/stores/user.js";

defineProps(['message','character'])//接收来自ChatHistory的参数

const user = useUserStore()//用户头像
</script>

<template>
  <div v-if="message.content">
    <div v-if="message.role === 'ai'" class="chat chat-start" >
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="character.photo" alt="">
        </div>
      </div>
      <div class="chat-bubble whitespace-pre-wrap">{{ message.content }}</div>
    </div>
    <div v-else class="chat chat-end ">
      <div class="chat-image avatar ">
        <div class="w-10 rounded-full ">
          <img :src="user.photo" alt="">
        </div>
      </div>
      <div class="chat-bubble chat-bubble-success whitespace-pre-wrap">{{ message.content }}</div>
    </div>
  </div>
</template>

<style scoped>

</style>