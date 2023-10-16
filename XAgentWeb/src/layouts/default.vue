<template>
  <section class="layout">
    <router-view />
  </section>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
.layout {
  width: 100%;
  height: 100%;

  display: grid;
  grid-template-rows: 60px 1fr;

  background: #fafafa;
  border: 1px solid #e6e6e6;
  box-shadow: -4px 0 4px 0 rgba(0, 0, 0, 0.08);

  .main {
    display: grid;
    grid-template-rows: 60px 1fr;

    background: #fafafa;
    border: 1px solid #e6e6e6;
    box-shadow: -4px 0 4px 0 rgba(0, 0, 0, 0.08);

    overflow: hidden;
  }
}
</style>
