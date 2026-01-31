import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// CSP 策略字符串（与 index.html meta 标签保持一致）
const cspPolicy = "default-src 'self' https://* ws: wss:; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://s3.tradingview.com https://www.tradingview.com; style-src 'self' 'unsafe-inline' https://*; img-src 'self' data: https://*; font-src 'self' data: https://at.alicdn.com https://fonts.gstatic.com; connect-src 'self' ws: wss: https://data.tradingview.com wss://stream.binance.com https://api.binance.com; frame-src https://www.tradingview.com; worker-src 'self' blob:;"

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: true,          // 允许外部访问（0.0.0.0）
    port: 5173,
    // 添加 CSP 响应头（使用 middleware.ts 的逻辑，仅在开发环境启用 unsafe-eval）
    headers: {
      'Content-Security-Policy': cspPolicy
    },
    proxy: {
      // WebSocket 代理：根据指令要求，将 /ws 代理到 Binance WebSocket
      // 前端通过 ws://localhost:5173/ws 连接，Vite 会自动代理到 wss://stream.binance.com:9443
      // 注意：WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问 ws:// 协议
      '/ws': {
        target: 'wss://stream.binance.com:9443',
        ws: true,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.error('[Proxy] ❌ WS代理错误:', err);
            console.error('[Proxy] 检查 Binance WebSocket 连接: wss://stream.binance.com:9443');
          });
          proxy.on('open', (socket) => {
            console.log('[Proxy] ✅ WS连接成功 - 直接连接 Binance WebSocket');
            console.log('[Proxy] WebSocket 目标: wss://stream.binance.com:9443');
          });
          proxy.on('proxyReqWs', (proxyReq, req, socket) => {
            console.log(`[Proxy] 📤 WS请求: ${req.url} -> ${proxyReq.path}`);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log(`[Proxy] 📥 WS响应: ${req.url} -> ${proxyRes.statusCode}`);
          });
        }
      },
      // HTTP API 代理：将 /api 代理到后端 FastAPI 服务器
      // 注意：后端路由已有 /api/v1/market 前缀，所以不需要 rewrite
      // 前端请求 /api/v1/market/klines -> 后端 http://127.0.0.1:8000/api/v1/market/klines
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.error('[Proxy] ❌ API代理错误:', err);
            console.error('[Proxy] 请确保后端服务运行在 http://127.0.0.1:8000');
            console.error('[Proxy] 检查: 1. 后端服务是否启动 2. 端口是否正确 3. CORS 配置');
          });
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log(`[Proxy] 📤 转发请求: ${req.method} ${req.url} -> ${proxyReq.path}`);
            console.log(`[Proxy] 请求头:`, JSON.stringify(req.headers, null, 2));
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log(`[Proxy] 📥 响应: ${req.url} -> ${proxyRes.statusCode}`);
          });
        }
      }
    }
  },
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      // 使用 Vue runtime build，避免构建时 eval
      'vue': 'vue/dist/vue.runtime.esm-bundler.js'
    }
  }
})