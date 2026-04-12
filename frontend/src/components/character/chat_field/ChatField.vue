<!--frontend/src/components/character/chat_field/ChatField.vue-->
<script setup>
import {computed, nextTick, ref, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import ChatHistory from "@/components/character/chat_field/chat_history/ChatHistory.vue";

const props = defineProps(['friend'])
const modalRef= useTemplateRef('modal-ref')
const inputRef = useTemplateRef('input-ref') //接收来自子组件的函数
const chatHistoryRef = useTemplateRef('chat-history-ref')
const history = ref([])//母组件定义，然后传递给子组件input_field，chat_filed，子组件不要直接修改母组件变量，但母组件可以定义一些函数，让子组件调用来修改

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

//两条history操作
function handlePushBackMessage(msg){
  history.value.push(msg) //回车后增加一条消息
  chatHistoryRef.value.scrollToButtom()
}

function handleAddToLastMessage(delta){
  history.value.at(-1).content += delta//在最后一条消息上增添内容
  chatHistoryRef.value.scrollToButtom()
}

//往上加消息
function handlePushFrontMessage(msg){
  history.value.unshift(msg)
}

function handleClose(){
  modalRef.value.close()
  inputRef.value.close()
}

defineExpose({
  showModal,

})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="handleClose" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute top-1 right-1">✕</button>
      <!--用于写历史聊天记录      -->
      <ChatHistory
          ref="chat-history-ref"
          v-if="friend"
          :history="history"
          :friendId="friend.id"
          :character="friend.character"
          @pushFrontMessage="handlePushFrontMessage"
      />
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendID="friend.id"
          @pushBackMessage="handlePushBackMessage"
          @addToLastMessage="handleAddToLastMessage"
      />
      <CharacterPhotoField v-if="friend" :character="friend.character"/>
    </div>
  </dialog>
</template>

<style scoped>

</style>