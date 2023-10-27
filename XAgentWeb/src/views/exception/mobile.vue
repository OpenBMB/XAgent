<template>
  <div class="exception-mobile flex-row">
    <div class="logo flex-row flex-center">
      <img src="@/assets/images/public/logo.png"
      alt="" width="35" height="35" />
    </div>
    <span>API Open Platform</span>

    <!-- Try out on desktop -->
    <p class="tip">Please visit and try out on PC</p>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss">
.exception-mobile {
  padding: 12px;
  align-items: center;
  // flex-direction: column;
  // justify-content: center;
  // align-items: center;
  gap: 6px;

  margin-left: 8px;
  font-family: PingFangSC-Semibold;
  color: #1c2848;
  line-height: 40px;
  font-weight: 600;

  .logo {
    width: 33px;
    height: 33px;
    background: #3d4ac6;
    border-radius: 83.33px;

    img {
      width: 35px;
      height: 35px;
      border-radius: 50%;
    }
  }
  .tip {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
}
</style>
