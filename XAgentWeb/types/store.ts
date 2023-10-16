import { UserInfo } from './user'
import { USER_INFO } from '/@/composables/useEnums'
export interface BasicConst {
  [USER_INFO]: UserInfo
  [STORAGE_TOKEN]: string
  [HISTORY_TALK]: string
}

export type BasicKeys = keyof BasicConst
