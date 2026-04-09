<!--frontend/src/components/character/chat_field/ChatField.vue-->
<script setup>
import {computed, nextTick, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";

const props = defineProps(['friend'])
const modalRef= useTemplateRef('modal-ref')
const inputRef = useTemplateRef('input-ref') //接收来自子组件的函数

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

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute top-1 right-1">✕</button>
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendID="friend.id"
      />
      <CharacterPhotoField v-if="friend" :character="friend.character"/>
    </div>
  </dialog>
</template>

<style scoped>

</style>