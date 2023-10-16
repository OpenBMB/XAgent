import { createApp } from 'vue'
import './assets/css/base.css'
import App from './App.vue'
import 'element-plus/theme-chalk/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { router, setupRouter } from './router/index'
import { setupRouteGuard } from './router/guard'
import { setupHighlightDirective } from './directives/highlight'
// import { setupClickOutsideDirective } from './directives/click-outside'
import JsonViewer from 'vue-json-viewer'

// Import JsonViewer as a Vue.js plugin

const start = async () => {
  const app = createApp(App)

  app.config.globalProperties.$ws_instance = null

  setupStore(app)
  setupRouter(app)
  setupRouteGuard(router)
  setupHighlightDirective(app)

  app.use(JsonViewer)
  
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }
  // setupClickOutsideDirective(app)

  await router.isReady()

  app.mount('#app', true)
}

start()
