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
  corporation: string //公司or学校
  industry: string //行业
  position: string //职位
  email: string //邮箱
  emailCode: string
  avatar?: string
  desc?: string
  homePath?: string
  roles?: RoleInfo[]
  orgCode?: string
  token?: string
  userId?: string | number
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
