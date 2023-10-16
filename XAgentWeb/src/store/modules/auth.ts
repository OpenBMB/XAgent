interface AuthState {
  isLogin: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      isLogin: false,
      token: '',
    }
  },
  getters: {
    getLoginState(): boolean {
      return this.isLogin
    },
    getToken(): string {
      return this.token || useGetLocalCache<string>(STORAGE_TOKEN) || ''
    },
  },
  actions: {
    setLoginState(val: boolean) {
      this.isLogin = val
    },
    setLoginToken(val: string) {
      this.token = val
      useSetLocalCache<{ token: string }>(val, STORAGE_TOKEN)
    },
    clearLoginState() {
      this.isLogin = false
      useClearLocalCache(STORAGE_TOKEN)
      this.token = ''
    },

    async checkAuthAction() {
      const userInfo = useGetLocalCache<{ token: string }>(USER_INFO)
      if(!userInfo || !userInfo.token) return false;
      // const res = await useCheckTokenRequest();
      // const _isLogin = res?.success === true && res?.data === 'True';
      // this.isLogin = _isLogin;
      // if (!this.isLogin) this.clearLoginState()
      // return this.isLogin;
      return true;
    },
  },
})

export const useAuthStoreOut = () => {
  return useAuthStore()
}
