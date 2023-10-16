declare interface Fn<T = any, R = T> {
  (...arg: T[]): R
}

export interface AxiosResponse<T = any> {
  data: T
}

export {}
