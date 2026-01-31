import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: true,          // 允许外部访问（0.0.0.0）
    port: 5173,
    proxy: {
      // WebSocket 代理：将 /ws 代理到后端 FastAPI 服务器（端口8000）
      // 前端通过 ws://localhost:5173/ws 连接，Vite 会自动代理到 ws://127.0.0.1:8000/api/v1/market/ws/kline
      // 注意：WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问 ws:// 协议
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/ws/, '/api/v1/market/ws/kline'),  // 确保是 /kline 而非 /depth
        configure: (proxy) => {
          proxy.on('error', (err) => console.error('[Proxy] WS错误:', err));
          proxy.on('open', () => console.log('[Proxy] WS连接成功 - 确认后端订阅@kline，非@depth'));
        }
      },
      // HTTP API 代理
      '/api': {
        target: 'http://127.0.0.1:8000',  // 后端 FastAPI 服务器（端口8000）
        changeOrigin: true,
        secure: false  // 禁用 SSL 验证（开发环境）
      }
    }
  },
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})