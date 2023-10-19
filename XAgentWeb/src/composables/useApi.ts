import axios, { AxiosResponse } from 'axios'

type Result<T> = {
  success: boolean
  code: number
  message: string
  data: T
}

const httpService = axios.create({
  // baseURL: import.meta.env.BASE_URL,
  baseURL: '',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    // 'Content-Type': 'application/json',
  },
})

//test --- BASE_URL
const test = '//test ---//test ---//test ---//test ---'

httpService.interceptors.request.use((config) => {
  const token = useGetLocalCache(STORAGE_TOKEN)
  config.headers!.token = token

  // if (import.meta.env.VITE_MODE === 'production') {
  //   config.url = config.url?.replace('/api', '/account/v1')
  //   config.url = config.url?.replace('/api', '/chat/v1')
  // }
  return config
})
// const authStore = useAuthStoreOut()
httpService.interceptors.response.use(
  (res: AxiosResponse) => {
    const authStore = useAuthStore()
    const userStore = useUserStore()
    // 1009 无效token 1005 用户不存在  1008 无效的token 1017用户不存在
    if (res?.data.code === 1009 || res?.data.code === 1005 || res?.data.code === 1008 || res?.data?.code === 1017) {
      
      
      // authStore.clearLoginState()
      // userStore.clearUserInfo()
      // router.push('/')
      // return res?.data

      // 开发测试先注释掉
    }
    return res?.data
  },
  (err: any) => {
    console.log(err)
    return
  }
)

export const useCheckTokenRequest = (): Promise<Result<any>> => {
  const token = useGetLocalCache(STORAGE_TOKEN)
  return httpService.post('/api/check', { token })
}

export const useCheckPhoneRequest = (params: { mobile: string }) => {
  return httpService.post('/api/isExist', params)
}


export const useSignUpRequest = (params: any): Promise<Result<any>> => {
  return httpService.post('/api/register', params)
}

export const useSharedConvsRequest = (params: any): Promise<Result<any>> => {
  return httpService.post('/api/getSharedInteractions', params)
}

export const useLoginRequest = (params: { email: string; token: string }) => {
  return httpService.post('/api/login', params)
}

export const useRegisterRequest = (params: {
  email: string,
  name: string,
}) => {
  return httpService.post('/api/register', params)
}

export const useLogoutRequest = (): Promise<Result<any>> => {
  return httpService.get('/api/logout')
}

/**
 * 发送短信验证码
 * @param params
 * @param params.mobile string 手机号
 * @param params.scene number 场景类型，1-注册，2-登录
 * @returns
 */
export const useMobileCodeRequest = (params: { mobile: string | number; scene: number }) => {
  return httpService.post('/sendSmsCode', params)
}

export const useEmailCodeRequest = (params: { email: string }) => {
  return httpService.post('/sendEmailCode', params)
}

/**
 * 获取用户secret key
 */
export const useDetailRequest = (): Promise<Result<{ appKey: string; secretKey: string }>> => {
  return httpService.post('/key/details')
}

/**
 * 反馈
 * @param params
 * @param params.feedbackMsg 反馈意见
 * @returns
 */
export const useFeedbackRequest = (params: {
  messageId: string
  conversationId: string
  feedbackMsg?: string
  rating: 'THUMBS_UP' | 'THUMBS_DOWN' | 'THUMBS_NO'
  feedbackAction?: 'COPY' | 'REGENERATE'
}): Promise<Result<{}>> => {
  return httpService.post('/msg/feedback', params)
}

/**
 * 对话
 * @param params
 * @returns
 */
export const useChatRequest = (params: {
  chatMessage: Array<{ content: { pairs: string; type: 'TEXT' }; id: string; role: 'USER' | 'AI' }>
  conversationId: string
  parentMessageId: string
  generateType?: 'REGENERATE' | 'NORMAL'
}): Promise<Result<{ output: string; msgId: string; costTimeMillis: number }>> => {
  return httpService.post('/next', params)
}

/**
 * 调用概览
 * @returns
 */
export const useApiDetailsRequest = (): Promise<Result<{ balance: number; costAmount: number; failRate: string; totalCount: number }>> => {
  return httpService.post('/call/details')
}

export const useHistoryByIdRequest = (): Promise<Result<{ convInfoList: [] }>> => {
  const userStore = useUserStore()
  const userInfo = userStore.getUserInfo
  return httpService.post('/api/getAllInteractors', 
    { 
      user_id: userInfo?.user_id,
      token: userInfo?.token
    });
}

export const useHistoryListRequest = (): Promise<Result<any>> => {

  const userStore = useUserStore()
  const userInfo = userStore.getUserInfo

  return httpService.post('/api/getUserInteractions', 
    { 
      user_id: userInfo?.user_id,
      token: userInfo?.token,
      page_size: 10,
      page_num: 1
    });
}

/**
 *
 * @param params
 * @returns
 *
 */
export const useQueryChatRequest = (params: {
  convId: string
}): Promise<
  Result<{ msgInfos: { msgID: string; content: string; parentMsgID: string; feedbackMsg: string; role: string; rating: string }[] }>
> => {
  return httpService.post('/getMsgsByConvID', params)
}

export const useDeleteHistoryRequest = (params: object): Promise<Result<{}>> => {

  const userStore = useUserStore()
  const userInfo = userStore.getUserInfo

  return httpService.post('/api/deleteInteraction', {
    user_id: userInfo?.user_id,
    token: userInfo?.token,
    ...params
  });
}
