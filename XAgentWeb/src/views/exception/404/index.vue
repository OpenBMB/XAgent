<template>
  <section class="exception flex-column">
    <div class="bg-text">
      404
      <img src="@/assets/images/404_images/404.svg" alt="" />
    </div>
    <span class="error-tip">
      Error： The page you are visiting does not exist
    </span>
    <div class="button" @click="goHome">
      Back Home
    </div>
  </section>
</template>

<script setup lang="ts">
const router = useRouter()
const goHome = () => {
  router.push('/playground')
}
</script>

<style scoped lang="scss">
.exception {
  width: 100vw;
  height: 100vh;
  // height: calc(100vh - 60px);
  background-image: linear-gradient(180deg, #f4f3f8 0%, #eaedf6 100%);

  .bg-text {
    margin: 140px 0 80px;
    font-family: MiSans-Semibold;
    font-size: 240px;
    color: rgba(119, 126, 145, 0.08);
    letter-spacing: 0;
    text-align: center;
    line-height: 320px;
    font-weight: 600;
    position: relative;
    img {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }
  }
  .error-tip {
    margin: 0 auto 40px;

    font-family: MiSans-Medium;
    font-size: 18px;
    color: #1c2848;
    line-height: 24px;
    font-weight: 500;
  }

  .button {
    cursor: pointer;
    margin: 0 auto;
    padding: 4px 25px;

    background: #3d4ac6;
    border-radius: 2px;

    font-family: PingFangSC-Regular;
    font-size: 20px;
    color: #ffffff;
    line-height: 48px;
  }
}
</style>
