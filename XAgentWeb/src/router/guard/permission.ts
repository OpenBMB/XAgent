import { Router } from 'vue-router'
export const createPermissionGuard = (router: Router) => {
  const authStore = useAuthStoreOut()

  router.beforeEach(async (to, from, next) => {
    // next()
    // return
    const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent)
    if (isMobile && to.path !== '/mobile') {
      // 当前设备是移动设备
      next('/mobile')
      return
    }

    if (!isMobile && to.path === '/mobile') {
      next('/playground')
      return
    }

    const userStore = useUserStore()
    const userInfo = userStore.getUserInfo
    
    const isLogin = authStore.getLoginState
    const token = authStore.getToken
    
    const isBetaUser = userInfo?.is_beta === true;
    
    if (token) {
      if (isLogin) {
            if(to.path === '/login') {
              next(isBetaUser ? '/playground' : '/share')
            } else if(isBetaUser) {
              next()
              // to.path === '/share' ? next('/playground') : next()
            } else {
              to.meta.isBetaOnly === true ? next('/share') : next()
            }

      } else {
        const loginState = await authStore.checkAuthAction().catch(() => next('/404'))
        if (loginState) {
          
            if(to.path === '/login') {
              next(isBetaUser ? '/playground' : '/share')
            } else if(isBetaUser) {
              next()
              // to.path === '/share' ? next('/playground') : next()
            } else {
              to.meta.isBetaOnly === true ? next('/share') : next()
            }

        } else {
          to.path === '/login' ? next() : next('/login')
        }
      }
    } else {
      if (to.meta.requireAuth === false && to.path !== '/login') {
        next()
      } else {
        to.path === '/login' ? next() : next('/login')
      }
    }
  })
}
