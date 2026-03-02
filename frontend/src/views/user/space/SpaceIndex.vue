<script setup>

import UserInfoField from "@/views/user/space/components/UserInfoField.vue";
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import {useRoute} from "vue-router";
import api from "@/js/http/api.js";
import Character from "@/components/character/Character.vue";

const userProfile = ref(null)
const characters = ref([])
const isLoading = ref(false) //判断当前是否有角色在加载
const hasCharacter = ref(true) //判断是否还有多余角色
const sentinelRef = useTemplateRef('sentinel-ref')
const route = useRoute()

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}


async function loadMore(){
  if(isLoading.value || !hasCharacter.value) return //无角色返回
  isLoading.value = true

  let newCharacters= [] //定义从云端在家的函数
  try{
    const res = await api.get('/api/create/character/get_list/',{
      params:{
        items_count: characters.value.length,
        user_id: route.params.user_id,
      }
    })
    const data = res.data
    if(data.result === 'success'){
      userProfile.value = data.user_profile //与api/create/character/get_list/返回值一致
      newCharacters = data.characters
    }
  }catch (err){
  }finally { //实现循环加载逻辑
    isLoading.value = false
    if(newCharacters.length === 0){//云端无可加载函数
      hasCharacter.value = false
    }else{
      characters.value.push(...newCharacters)//...为展开列表；
      await nextTick() //等待渲染完，判断哨兵能否被看到

      if(checkSentinelVisible()){
        await loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()

  observer = new IntersectionObserver(//监听器 循环加载
      entries => {
        entries.forEach(entry => {
          if(entry.isIntersecting) {
            loadMore()
          }
        })
      },
      {root:null,rootMargin:'2px',threshold:0}//root 判断视窗是否交叉，rootMargin 缩小检测视窗范围提前判断,threshold:交叉的大小为某个值的时候触发
  )
  observer.observe(sentinelRef.value)
})

function removeCharcater(characterId){
  characters.value = characters.value.filter(c => c.id !== characterId) //取出所有id!==characterId的值付给原来的值，效果保留所有不相等的元素，删除别的
}

onBeforeUnmount(() => { //组件移除前释放资源
  observer?.disconnect()  // 解绑监听器
})
</script>

<template>
  <div class="flex flex-col items-center mb-12">
    <UserInfoField :userProfile="userProfile"/>
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">
      <!--循环渲染角色  -->
      <Character
          v-for="character in characters"
          :key="character.id"
          :character="character"
          :canEdit="true"
          @remove="removeCharcater"
      />
    </div>
    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasCharacter" class="text-gray-500 mt-4">没有更多的角色了</div>
  </div>
</template>

<style scoped>

</style>