<!-- <IconsSend @click="sendMessage" /> -->
<template>
  <div class="loading flex-row flex-center">
    <i></i>
    <i></i>
    <i></i>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
.loading {
  gap: 2px;

  i {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #ffffff;
    opacity:0.8;

    animation: loadingDot steps(3) 1.5s infinite;

    &:nth-of-type(2) {
      //   opacity: 0.6;
      animation: loadingDot steps(3) 1.5s 0.5s infinite;
    }
    &:nth-of-type(3) {
      //   opacity: 0.2;
      animation: loadingDot steps(3) 1.5s 1s infinite;
    }
  }
}
</style>
