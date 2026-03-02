<script setup>
import {nextTick, onBeforeUnmount, ref, useTemplateRef, watch} from "vue";
import CameraIcon from "@/views/user/profile/components/icon/CameraIcon.vue";
import Croppie from 'croppie'
import 'croppie/croppie.css'

const props = defineProps(['photo'])
const myPhoto = ref(props.photo)

watch(()=> props.photo,newVal =>{
  myPhoto.value = newVal
})

const fileInputRef = useTemplateRef('file-input-ref') //绑定弹出文件框
const modalRef = useTemplateRef('modal-ref')
const croppieRef = useTemplateRef('croppie-ref')
let croppie = null

async function openModal(photo){//打开文件框
  modalRef.value.showModal()
  await nextTick() //等所有元素渲染完

  if(!croppie){
    croppie = new Croppie(croppieRef.value,{// 创建croppie对象
      viewport: {width: 200, height: 200, type: 'square'},
      boundary: {width: 300, height: 300},
      enableOrientation: true,
      enforceBoundary: true,
    })
  }

  croppie.bind({
    url:photo,
  })
}

//裁剪函数
async function crop(){
  if(!croppie) return//如果没有裁剪对象，直接返回

  myPhoto.value = await croppie.result({//将我的头像换成裁剪后的
    type:'base64',
    size:'viewport',
  })

  modalRef.value.close()
}

function onFileChange(e){//上传头像
  const file = e.target.files[0]
  e.target.value= ''
  if(!file) return

  const reader = new FileReader()
  reader.onload = () => {
    openModal(reader.result) //打开文件框
  }
  reader.readAsDataURL(file)
}

onBeforeUnmount(() => {  // 释放croppie对象，防止内存泄漏
  croppie?.destroy()
})

defineExpose({
  myPhoto
})
</script>

<template>
  <div class="flex justify-center">
    <div class="avatar relative">
      <div v-if="myPhoto" class="w-28 rounded-full">
        <img :src="myPhoto" alt="">
      </div>
      <div v-else class="w-28 h-28 rounded-full bg-base-200"></div>
      <div @click="fileInputRef.click()" class="w-28 h-28 rounded-full bg-black/20 absolute left-0 top-0 flex justify-center items-center cursor-pointer">
        <CameraIcon/>
      </div>
    </div>
  </div>

  <input ref="file-input-ref" type="file" class="hidden" accept="image/*" @change="onFileChange">

  <dialog ref="modal-ref" class="modal">
    <div class="modal-box transition-none">
      <button @click="modalRef.close()" class="btn btn-sm btn-ghost btn-circle absolute right-2 top-2">✕</button>

      <div ref="croppie-ref" class="flex flex-col my-4"></div>

      <div class="modal-action">
        <button @click="modalRef.close()" class="btn">取消</button>
        <button @click="crop" class="btn btn-neutral">确定</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped>

</style>