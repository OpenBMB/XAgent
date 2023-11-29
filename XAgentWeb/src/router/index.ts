import type { App } from 'vue'
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Login from '../views/login/login.vue'
import Layout from '/@/layouts/default.vue'
import Chat from '../views/playground/chat.vue';

const moduleRoute: any[] = []
const modules = import.meta.glob('./modules/**/*.ts', { eager: true })

Object.keys(modules).forEach((key) => {
  const mod = (modules as Recordable)[key].default || {}
  const modList = Array.isArray(mod) ? [...mod] : [mod]
  moduleRoute.push(...modList)
})

const PAGE_NOT_FOUND = 'page_not_found'

const PAGE_NOT_FOUND_ROUTE = {
  name: PAGE_NOT_FOUND,
  path: '/:path(.*)*',
  meta: { requireAuth: false },
  // component: Layout,
  children: [
    {
      path: '/:path(.*)*',
      name: PAGE_NOT_FOUND,
      component: () => import('../views/exception/404/index.vue'),
      meta: {},
    },
  ],
}

const routes: Readonly<RouteRecordRaw[]> = [
  {
    path: '/',
    redirect: '/playground',
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requireAuth: false },
  },
  { 
    name: 'SharedTalks',
    path: '/share',
    component: Layout,
    meta: {
      requireAuth: true,
      isBetaOnly: false,
    },
    children: [
      {
        name: 'SharedTalks',
        path: '/share',
        component: () => import('/@/views/playground/layout.vue'),
        children: [
          {
            name: 'SharedTalks',
            path: '/share',
            title: 'Our Shared Talks ｜ X-Agent',
            component: () => import('/@/views/playground/share.vue'),
          },
        ]
      }
    ]
  },
  {
    name: 'Playground',
    component: Layout,
    path: '/playground',
    meta: { 
      title: 'Demo Playground ｜ X-Agent',
    },
    children: [
      {
        name: 'Playground',
        path: '/playground',
        component: () => import('/@/views/playground/layout.vue'),
        children: [
          {
            path: '/playground',
            name: 'Playground',
            component: () => import('../views/playground/index.vue'),
            meta: {
              title: 'Demo Playground ｜ X-Agent',
              isBetaOnly: true,
            },
          },
          {
            name: 'viewTalk',
            path: '/playground/chat/:mode?/:id?',
            component: Chat,
            meta: {
              title: 'View Talk ｜ X-Agent',
              isBetaOnly: false,
            },
          },
          {
            name: 'newtalk',
            path: '/playground/chat/:mode',
            component: Chat,
            meta: {
              title: 'New Talk ｜ X-Agent',
              isBetaOnly: true,
            },
          },
        ],
      },
    ],
  },
  {
    name: 'Mobile',
    path: '/mobile',
    component: () => import('/@/views/exception/mobile.vue'),
    meta: {
      title: 'X-Agent',
      requireAuth: false,
    },
  },
  ...moduleRoute,
  PAGE_NOT_FOUND_ROUTE,
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export function setupRouter(app: App<Element>) {
  app.use(router)
}

export { router }
