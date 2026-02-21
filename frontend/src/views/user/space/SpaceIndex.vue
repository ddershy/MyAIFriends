<script setup>
import {useRoute, useRouter} from "vue-router";

const route = useRoute()//取当前url相关信息
// const router = useRouter()//操作页面前进或后退

</script>

<template>
个人空间：{{ route.params.user_id}} <!--从网址上取参数，{{写参数}}-->
</template>

<style scoped>

</style>