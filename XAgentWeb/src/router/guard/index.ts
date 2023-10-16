import { createPermissionGuard } from './permission'
import { Router } from 'vue-router'

const createPageGuard = (router: Router) => {
  router.afterEach((to, from) => {
    useTitle(to.meta?.title as string)
  })
}

export function setupRouteGuard(router: Router) {
  createPageGuard(router)
  createPermissionGuard(router)
}
