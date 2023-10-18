<script setup lang="ts"></script>

<template><router-view /></template>

<!-- <script setup lang="ts">
import { ElMessage } from 'element-plus';

const router = useRouter()
const userStore = useUserStore()
const authStore = useAuthStore()

const DEFAULT_ACCOUNT = 'admin'
const DEFAULT_PSWD = 'xagent-admin'

const param = {
  email: DEFAULT_ACCOUNT,
  token:  DEFAULT_PSWD,
}

const res: any = await useLoginRequest(param);

if (res?.success) {
  userStore.setUserInfo(res?.data)
  authStore.setLoginState(true)
  authStore.setLoginToken(res?.data?.token)
  router.push({ path: '/playground' });
} else {
  ElMessage({ type: 'error', message: (res?.message || 'Login failed') })
}
</script> -->


<style>
#app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
