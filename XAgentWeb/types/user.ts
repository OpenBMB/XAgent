export interface RoleInfo {
  roleName: string
  value: string
}

export interface UserInfo {
  id?: string | number
  user_id?: string | number
  mobile: number | string
  smsCode: string
  name: string
  corporation: string // Company or School
  industry: string
  position: string
  email: string
  emailCode: string
  avatar?: string
  desc?: string
  homePath?: string
  roles?: RoleInfo[]
  orgCode?: string
  token?: string
  userId?: string | number
  is_beta?: boolean
}

export enum RoleEnum {
  // super admin
  SUPER = 'super',

  // tester
  TEST = 'test',
}

export interface LoginInfo {
  multi_depart?: string | number
  userInfo?: object
  departs?: []
  tenantList?: []
  isLogin?: boolean
}
