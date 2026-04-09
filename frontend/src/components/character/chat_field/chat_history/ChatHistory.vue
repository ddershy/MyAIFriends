<!--frontend/src/components/character/chat_field/chat_history/ChatHistory.vue-->
<script setup>
import Message from "@/components/character/chat_field/chat_history/message/Message.vue";
import {nextTick, onBeforeUnmount, onMounted, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

const props = defineProps(['history', 'friendId', 'character']) //来自ChatField的参数
const emit = defineEmits(['pushFrontMessage'])//接收事件
const scrollRef = useTemplateRef('scroll-ref')
const sentinelRef = useTemplateRef('sentinel-ref')
let isLoading = false
let hasMessages = true
let lastMessageId = 0

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const sentinelRect = sentinelRef.value.getBoundingClientRect()
  const scrollRect = scrollRef.value.getBoundingClientRect()
  return sentinelRect.top < scrollRect.bottom && sentinelRect.bottom > scrollRect.top
}

async function loadMore() {
  if (isLoading || !hasMessages) return //如果没有加载消息或者消息为空，结束
  isLoading = true

  let newMessages = []
  try {
    const res = await api.get('/api/friend/message/get_history/', {
      params: {
        last_message_id: lastMessageId,
        friend_id: props.friendId,
      }
    })
    const data = res.data
    if (data.result === 'success') {
      newMessages = data.messages //如果成功则存储消息
    }
  } catch (err) {
    console.log(err)
  } finally {
    isLoading = false

    if (newMessages.length === 0) { //如果没有新消息了就结束
      hasMessages = false
    } else {//否则需要将消息一条一条添加在最上面
      const oldHeight = scrollRef.value.scrollHeight //加载前存储一下旧高度，防止出现加载出 消息后窗口自动上滑的情况
      const oldTop = scrollRef.value.scrollTop

      for (const m of newMessages) { //'of' 枚举的是元素，'in'输出的是下标
        emit('pushFrontMessage', {
          role: 'ai',
          content: m.output,
          id: crypto.randomUUID(),
        })
        emit('pushFrontMessage', {
          role: 'user',
          content: m.user_message,
          id: crypto.randomUUID(),
        })
        lastMessageId = m.id//每次都跟新id
      }
      await nextTick()

      const newHeight = scrollRef.value.scrollHeight
      scrollRef.value.scrollTop = oldTop + newHeight - oldHeight //修改scrolltop的总长度，来抵着窗口的显示界面

      if (checkSentinelVisible()) {
        loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()

  observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            loadMore()
          }
        })
      },
      {root: null, rootMargin: '2px', threshold: 0}
  )

  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect
})

async function scrollToButtom() {
  await nextTick() //页面渲染完再滚动

  scrollRef.value.scrollTop = scrollRef.value.scrollHeight
}

defineExpose({
  scrollToButtom,
})
</script>

<template>
  <div ref="scroll-ref" class="absolute top-18 left-2 w-85 h-112 overflow-y-scroll no-scrollbar">
    <div ref="sentinel-ref" class="h-2 "></div>
    <Message
        v-for="message in history"
        :key="message.id"
        :message="message"
        :character="character"
    />
  </div>
</template>

<style scoped>
/* 隐藏 Chrome, Safari 和 Opera 的滚动条 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

/* 隐藏 IE, Edge 和 Firefox 的滚动条 */
.no-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>
