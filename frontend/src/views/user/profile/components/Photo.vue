<script setup>
import {nextTick, onBeforeUnmount, ref, useTemplateRef, watch} from "vue";
import CameraIcon from "@/views/user/profile/components/icon/CameraIcon.vue";
import Croppie from 'croppie'
import 'croppie/croppie.css'

const props = defineProps(['photo'])
const myPhoto = ref(props.photo)

watch(() => props.photo, newVal => {
  myPhoto.value = newVal
})

const fileInputRef = useTemplateRef('file-input-ref')
const modalRef = useTemplateRef('modal-ref')
const croppieRef = useTemplateRef('croppie-ref')
let croppie = null

async function openModal(photo){ //打开文件框
  modalRef.value.showModal()
  await nextTick() //等所有元素渲染完

  if(!croppie){
    croppie = new Croppie(croppieRef.value,{
      viewport: {width: 200, height: 200, type: 'square'},// 创建croppie对象
      boundary: {width: 300, height: 300},
      enableOrientation: true,
      enforceBoundary: true,
    })
  }

  croppie.bind({// 绑定裁剪图片
    url:photo,
  })
}

async function crop(){
  if(!croppie) return //确保存在

  myPhoto.value = await croppie.result({  // 获取裁剪结果
    type: 'base64',
    size: 'viewport',
  })

  modalRef.value.close()
}

function onFileChange(e){ //文件上传函数
  const file = e.target.files[0]
  e.target.value = '' //保证用户效果，每次换头像不管是否是同一张图都触发写
  if(!file) return

  const reader = new FileReader() //将图片读成一个文件
  reader.onload = () =>{
    openModal(reader.result)
  }

  reader.readAsDataURL(file)
}

onBeforeUnmount(() => {  // 释放croppie对象，防止内存泄漏
  croppie?.destroy()
})

defineExpose({ //将组件暴露出去
  myPhoto,
})
</script>

<template>
  <div class="flex justify-center">
    <div class="avatar relative">
      <div class="w-28 rounded-full">
        <img :src="myPhoto">
      </div>
      <div @click="fileInputRef.click()" class="absolute left-0 top-0 w-28 h-28 flex justify-center items-center bg-black/20 rounded-full cursor-pointer">
        <CameraIcon/>
      </div>
    </div>
  </div>

  <input ref="file-input-ref" type="file" accept="image/*" class="hidden" @change="onFileChange">

<!--  文件框，实现点击头像后可以选范围-->
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box transition-none">
      <button @click="modalRef.close()" class="btn btn-circle btn-sm btn-ghost absolute right-2 top-2">✕</button> <!--  关闭按钮  -->

      <div ref="croppie-ref" class="flex flex-col justify-center my-4"></div>

      <div class="modal-action">
        <button @click="modalRef.close()" class = "btn">取消</button>
        <button @click="crop" class="btn btn-neutral">确认</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped>

</style>