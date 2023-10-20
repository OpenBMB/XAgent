import { Fn } from '@vueuse/core'
import type { VNode, VNodeChild, ComponentPublicInstance, FunctionalComponent, PropType as VuePropType } from 'vue'

declare global {
  interface ViteEnv {
    VITE_PUBLIC_PATH: string
    IS_PROD: string
  }

  declare type Nullable<T> = T | null
  declare type Recordable<T = any> = Record<string, T>

  interface Window {
    MathJax: {
      typeset(): any
    }
    IS_PROD: string
  }
}

declare module '@/assets/data/data.js'

declare module 'vue' {
  export type JSXComponent<Props = any> = { new (): ComponentPublicInstance<Props> } | FunctionalComponent<Props>
}

declare module 'tinymce'

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  const Component: DefineComponent<{}, {}, any>
  export default Component
}
