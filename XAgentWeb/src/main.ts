import { createApp } from 'vue'
import App from './App.vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { router, setupRouter } from './router/index'
import { setupRouteGuard } from './router/guard'
import { setupHighlightDirective } from './directives/highlight'
// import { setupClickOutsideDirective } from './directives/click-outside'
import JsonViewer from 'vue-json-viewer'
import VueViewer from 'v-viewer';
import useReactInsideVue from './react/index.jsx';
import 'viewerjs/dist/viewer.css';
import 'element-plus/theme-chalk/index.css'
import './assets/css/base.css'

let env = import.meta.env.VITE_MODE
if (env == 'production') {
  console.log = ()=>{}
}
// Import JsonViewer as a Vue.js plugin

const start = async () => {
  const app = createApp(App)
  app.directive('react', (el, binding) => {
    useReactInsideVue(binding.value, el)
});

  setupStore(app)
  setupRouter(app)
  setupRouteGuard(router)
  setupHighlightDirective(app)

  app.use(JsonViewer)
  app.use(VueViewer);
  
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }
  // setupClickOutsideDirective(app)

  // Load when the router is ready( https://next.router.vuejs.org/api/#isready)
  await router.isReady()
  
  app.mount('#app', true)
}

start()
