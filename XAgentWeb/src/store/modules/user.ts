import { LoginInfo, RoleEnum, UserInfo } from '/#/user'

interface UserState {
  userInfo: Nullable<UserInfo>
  token?: string
  roleList: RoleEnum[]
  dictItems?: []
  sessionTimeout?: boolean
  lastUpdateTime: number
  tenantid?: string | number
  loginInfo?: Nullable<LoginInfo>
  showKey: boolean
  showSecret: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => {
    return {
      // 用户信息
      userInfo: useGetLocalCache<UserInfo>(USER_INFO) || null,
      roleList: [],
      lastUpdateTime: 0,
      showKey: false,
      showSecret: false,
    }
  },
  getters: {
    getUserInfo(): UserInfo {
      return this.userInfo || useGetLocalCache<UserInfo>(USER_INFO) || {}
    },
  },

  actions: {
    setUserInfo(val: UserInfo) {
      this.userInfo = val
      useSetLocalCache<UserInfo>(val, USER_INFO)
    },
    clearUserInfo() {
      useClearLocalCache(USER_INFO)
      this.userInfo = null
    },

    setShowKey(val: boolean) {
      this.showKey = val
    },
    setShowSecret(val: boolean) {
      this.showSecret = val
    },
  },
})

// export function useUserStoreWithout() {
//   return useUserStore(store)
// }
