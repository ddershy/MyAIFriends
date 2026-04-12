<!--frontend/src/components/character/chat_field/input_field/InputField.vue-->

<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {onUnmounted, ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";
import flattenColorPalette from "tailwindcss/lib/util/flattenColorPalette";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";

const props = defineProps(['friendID'])//接收来自母组件的friendID
const emit = defineEmits(['pushBackMessage','addToLastMessage']) //接收函数
const inputRef = useTemplateRef('inputRef') //定义一个输入框
const message = ref('') //获取聊天框内内容
// let  isProcessing = false //防止用户重复发消息
let processId = 0//实现消息打断，记录版本号
const showMic = ref(false) //判断麦克风组件是否渲染

let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

const initAudioStream = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener('sourceopen', () => {
        try {
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
            console.error("MSE AddSourceBuffer Error:", e);
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};

const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);
    } catch (e) {
        console.error("SourceBuffer Append Error:", e);
        isUpdating = false;
    }
};

const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
        console.error("Base64 Decode Error:", e);
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});


function focus(){
  inputRef.value.focus()
}

async function handleSend(event,audio_msg){
  let content
  if(audio_msg){
    content = audio_msg.trim() //优先使用语音消息
  }else{
     content = message.value.trim() //先取出内容
  }
  if(!content) return

  initAudioStream() //初始化音频播放器

  // if(isProcessing) return
  // isProcessing = true //占用逻辑放在检测是否为空的后面
  const curId = ++ processId;//版本号+1，存储这一版版本号
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
        if(curId != processId) return //当版本号不是最新就遗弃，实现打断
        if(data.content){
          //每次流式收到一条消息，就将这条消息流式补充到最后一条消息上
          emit('addToLastMessage',data.content)
        }
        if(data.audio) {
          handleAudioChunk(data.audio) //处理音频
        }
      },
      onerror(err){//用于接收错误
        // isProcessing = false
      },
    }) //发送流式请求
  }catch(err){
    // isProcessing = false //错误表示信息发送完毕
  }
}

function close(){
  ++ processId //更新版本号，用于停止接收消息
  showMic.value = false // 关闭时强制切回文字输入模式
  stopAudio()
}

function handleStop(){ //打断ai的输出
  ++ processId
  stopAudio()
}

defineExpose({ //当母组件一调用聊天框函数，这个逻辑应当被执行。因为需要在母组件调用子组件，所以需要将这个部分暴漏出去
  focus,
  close,
})
</script>

<template>
  <form v-if="!showMic" @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
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
    <div @click="showMic = true" class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon/>
    </div>
  </form>
  <Microphone
      v-else
      @close="showMic = false"
      @send="handleSend"
      @stop="handleStop"
  />
</template>

<style scoped>

</style>