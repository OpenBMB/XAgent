import react from '@vitejs/plugin-react'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv, UserConfigExport } from 'vite'

import AutoImport from 'unplugin-auto-import/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Icons from 'unplugin-icons/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'
import banner from 'vite-plugin-banner'

import { resolve } from 'path'
import { createHtmlPlugin } from 'vite-plugin-html'

function pathResolve(dir: string) {
  // const path = resolve(process.cwd(), '.', dir)
  const path = resolve(__dirname, dir)
  return path
}

const isProduction = process.env.type === 'prod'

process.env.VITE_MODE = isProduction ? 'production' : 'development'


export default defineConfig(({ command, mode }) => {
  console.log('command', command, 'mode', mode)
  console.log()
  return {
    base: '/',
    resolve: {
      alias: [
        { find: /\/@\//, replacement: pathResolve('src') + '/' },
        { find: /\/#\//, replacement: pathResolve('types') + '/' },
        { find: /@\//, replacement: pathResolve('src') + '/' },
      ],
    },
    plugins: [
      vue(),
      react(),
      banner(`build package in ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()} !`),
      AutoImport({
        resolvers: [ElementPlusResolver()],
        imports: ['vue', '@vueuse/core', 'vue-router', 'pinia'],
        dirs: ['./src/components/**/*', './src/composables/**', './src/store/**', './types/**'],
        vueTemplate: true,
      }),
      Components({
        dts: true,
        resolvers: [ElementPlusResolver({ importStyle: true }), IconsResolver({ prefix: 'icon' })],
      }),
      Icons(),
      createHtmlPlugin({
        inject: { data: { title: 'X-Agent' } },
      }),
    ],

    // Define global constants replacement method. Each item will be defined globally in the development environment and statically replaced during building.
    define: {
      BASE_URL: JSON.stringify('/'),
    },
    server: {
      proxy: {
        '/api': {
          target: loadEnv(mode, process.cwd()).VITE_BACKEND_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/\/api/, ''),
        },
        '/workspace': {
          target: loadEnv(mode, process.cwd()).VITE_BACKEND_URL,
          changeOrigin: true
        },
      },
    },
    build: {
      cssTarget: 'chrome80',
      minify: 'terser',
      terserOptions: {
        compress: {
          keep_infinity: true,
          // drop_console: process.env.type === 'prod',
          drop_console: false,
          drop_debugger: true,
        },
      },
      chunkSizeWarningLimit: 2000,
    },
    esbuild: {
      // drop: process.env.type === 'prod' ? ['console', 'debugger'] : [],
      drop: process.env.type === 'prod' ? ['debugger'] : [],
    },
  }
}) as UserConfigExport

