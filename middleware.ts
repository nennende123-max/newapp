/**
 * Content Security Policy (CSP) 中间件配置
 * 用于动态生成 CSP 策略，根据环境变量在开发/生产环境中应用不同的安全策略
 */

/**
 * 生成 CSP 策略字符串
 * @param isDevelopment 是否为开发环境
 * @returns CSP 策略字符串
 */
export function generateCSPPolicy(isDevelopment: boolean = false): string {
  // 基础 CSP 指令
  const directives: Record<string, string[]> = {
    'default-src': ["'self'", 'https://*'],
    'script-src': [
      "'self'",
      "'unsafe-inline'", // 允许内联脚本（Vue 模板需要）
      'https://s3.tradingview.com',
      'https://www.tradingview.com',
    ],
    'connect-src': [
      "'self'",
      'ws:',
      'wss:',
      'https://data.tradingview.com',
      'wss://ws.binance.com',
      'http://127.0.0.1:8000', // 本地后端 API
      'https://api.binance.com',
      'https://stream.binance.com',
      'https://fstream.binance.com',
    ],
    'frame-src': ['https://www.tradingview.com'],
    'img-src': ["'self'", 'data:', 'https:'], // 允许所有 HTTPS 图片资源
    'font-src': ["'self'", 'data:', 'https://fonts.gstatic.com'],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://*'],
  }

  // 仅在开发环境下添加 'unsafe-eval'（用于 HMR 热更新）
  if (isDevelopment) {
    directives['script-src'].push("'unsafe-eval'")
  }

  // 将指令对象转换为 CSP 字符串
  const cspString = Object.entries(directives)
    .map(([directive, sources]) => `${directive} ${sources.join(' ')}`)
    .join('; ')

  return cspString
}

/**
 * 获取当前环境的 CSP 策略
 * 根据 NODE_ENV 环境变量自动判断是否为开发环境
 */
export function getCSPPolicy(): string {
  const isDevelopment = process.env.NODE_ENV === 'development'
  return generateCSPPolicy(isDevelopment)
}

/**
 * Vite 插件：自动注入 CSP 响应头
 * 使用方法：在 vite.config.ts 中导入并添加到 plugins 数组
 */
export function cspMiddleware() {
  return {
    name: 'csp-middleware',
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        const cspPolicy = getCSPPolicy()
        res.setHeader('Content-Security-Policy', cspPolicy)
        next()
      })
    },
  }
}

// 默认导出 CSP 策略字符串（用于 vite.config.js 或 index.html）
export default getCSPPolicy()
