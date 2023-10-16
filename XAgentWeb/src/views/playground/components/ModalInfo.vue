<template>
   <div class="border"></div>
</template>
  
<script setup lang="ts">
  import { ref } from 'vue'
  const props = defineProps(['list'])
</script>

<style scoped lang="scss">
  .border{
    height: 200px;
    width: 200px;
    background-color: aqua;
  }
</style>