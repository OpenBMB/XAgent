<template>
  <section class="demo-box flex-row">
    <HistorySidebar />
    <router-view />
  </section>
</template>

<script setup lang="ts">
import HistorySidebar from './components/HistorySidebar.vue'
import { onMounted } from 'vue';

onMounted(() => {
});

</script>

<style scoped lang="scss">
.demo-box {
  display: grid;
  grid-template-columns: 260px 1fr;
}

@media screen and (max-width: 1440px) {
  .demo-box .info .info-title {
    margin-left: 20%;
    justify-content: flex-start;
  }
  .demo-box .demo .demo-wrapper {
    display: grid;

    grid-template-columns: max-content auto;
    .demo-item {
      width: 100%;
    }
  }
}
</style>
