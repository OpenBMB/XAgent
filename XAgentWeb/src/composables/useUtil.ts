import { BasicKeys } from '/#/store'

export const useWindowOpen = (url: string) => {
  window.open(url, 'blank')
}

/**
 * 获取localStorage
 * @param key
 * @returns
 */
export const useGetLocalCache = <T = any>(key: BasicKeys): T => {
  const cache = localStorage.getItem(key)
  if (!cache) return null as T
  try {
    // TODO: 加解密 crypto-js
    const data = JSON.parse(cache)
    if (data) return data as T
  } catch {
    return null as T
  }
  return null as T
}

/**
 * 设置localStorage
 * @param val
 */
export const useSetLocalCache = <T>(val: any, key: BasicKeys) => {
  // if (typeof val === 'string') {
  //   localStorage.setItem(key, val)
  // } else {
  localStorage.setItem(key, JSON.stringify(val))
  // }
}

/**
 * 清楚指定key
 * @param key
 */
export const useClearLocalCache = (key?: BasicKeys) => {
  if (!key) {
    localStorage.clear()
  } else {
    localStorage.removeItem(key)
  }
}

export const useIsMac = () => {
  return /macintosh|mac os x/i.test(navigator.userAgent)
}

export const useCheckAuth = async () => {
  const auth = useAuthStore()
  // auth.getLoginState
  // const isLogin = useLogin()
  // const isShowLogin = useShowLogin()
  // const token = localStorage.getItem(STORAGE_TOKEN)

  // if (!token || !isLogin.value) {
  //   isShowLogin.value = true
  //   return false
  // }
  const isLogin = auth.getLoginState
  if (isLogin) return true

  const res = await useGetLocalCache(STORAGE_TOKEN)
  return res
}

export const useNavigateTo = (url: string) => {
  const router = useRouter()
  console.log(router)
  router.push({ path: url })
}

/**
 * 添加水印
 * @param selector
 */
export const useInitWaterMark = (selector: string, text: string, options: any = {}) => {
  const textCanvas = document.createElement('canvas')
  const textCtx = textCanvas.getContext('2d') as CanvasRenderingContext2D
  // const text: TextMetrics = textCtx.measureText(userInfo.value.name as string)
  textCanvas.width = 150
  textCanvas.height = 120
  textCanvas.style.width = `150px`
  textCanvas.style.height = `120px`
  // document.body.append(textCanvas)
  textCtx.rotate((-15 * Math.PI) / 180)
  textCtx.font = '12px 微软雅黑'
  textCtx.fillStyle = '#Ebebeb'
  textCtx?.fillText(text, 10, 120)

  const canvas = document.querySelector(selector) as HTMLCanvasElement
  canvas.width = window.innerWidth - 240
  canvas.height = window.innerHeight - 120
  const context: any = canvas.getContext('2d') as CanvasRenderingContext2D
  context.rect(0, 0, canvas.width, canvas.height)
  context.fillStyle = context.createPattern(textCanvas, 'repeat')
  context.fill()
}

export const useAsset = (path: string): string => {
  const assets: { [x: string]: any } = import.meta.glob('../assets/images/**', { eager: true, import: 'default' })
  return assets[`../assets/images` + path]
}

export const useCreateCopyDom = (id: string): string => {
  const div = document.createElement('div')
  div.id = id
  div.classList.add('copy-btn')
  const svg = `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M14.1667 14.1667V17.5H2.5V5.83333H5.83333V2.5H17.5V14.1667H14.1667ZM15.8333 4.16667H7.5V5.83333H14.1667V12.5H15.8333V4.16667ZM4.16667 7.5H12.5V15.8333H4.16667V7.5Z" fill="white" fill-opacity="0.85"></path></svg>`
  div.innerHTML = svg
  return div.outerHTML
}
