<template>
  <section class="demo-box flex-row">
    <HistorySidebar />
    <section class="container-box">
      <router-view />
    </section>
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
  width: 100vw;
  max-width: 100vw;
  display: grid;
  grid-template-columns: 260px 1fr;

  .container-box {
    position: relative;
    background-color: rgb(236, 237, 245);
    width: 100%;
    max-width: calc(100vw - 260px);
    display: flex;
    flex-direction: column;
    align-items: center;

    .news,
    .ability,
    .feature {
      gap: 24px;
      width: calc(100% / 3);
    }
  }
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
