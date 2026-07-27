import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    watch: {
      ignored: ['**/src-tauri/target/**'],
    },
    proxy: {
      '/v1': { target: 'http://localhost:8001', changeOrigin: true },
      '/health': { target: 'http://localhost:8001', changeOrigin: true },
    },
  },
})
