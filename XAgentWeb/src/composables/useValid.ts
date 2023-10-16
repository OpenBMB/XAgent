export const useValidPhone = (str: string): boolean => {
  return /^1(\d){10}$/.test(str)
}

export const useValidEmail = (str: string): boolean => {
  return /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(str)
}
