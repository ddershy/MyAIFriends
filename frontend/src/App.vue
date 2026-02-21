<script setup>

import NavBar from "@/components/navbar/NavBar.vue";
</script>

<template>
  <NavBar>
    <RouterView />  <!-- 根据index.js的组件开始匹配，将组件渲染在这里-->
  </NavBar>
</template>

<style scoped>

</style>
