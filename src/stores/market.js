import { defineStore } from 'pinia'

export const useMarketStore = defineStore('market', {
  state: () => ({
    // Tickers data mapped by symbol (e.g., 'BTC', 'ETH')
    tickers: {},
    // WebSocket connection state
    ws: null,
    isConnected: false,
    reconnectTimer: null, // 重连定时器
    reconnectInterval: 5000 // 固定 5 秒重连间隔
  }),

  getters: {
    // Get ticker data for a specific symbol
    getTicker: (state) => (symbol) => {
      return state.tickers[symbol] || null
    },

    // Check if data is loaded for a symbol
    hasData: (state) => (symbol) => {
      return !!state.tickers[symbol]
    }
  },

  actions: {
    /**
     * Initialize WebSocket connection to Binance
     */
    initWebSocket() {
      // If already connected, don't reconnect
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        console.log('WebSocket already connected')
        return
      }

      // 清除之前的重连定时器
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
        this.reconnectTimer = null
      }

      try {
        // Binance WebSocket endpoint for combined streams
        // 使用 ticker 流替代 miniTicker，获取完整的 24h 涨跌幅数据
        // Format: stream1@ticker/stream2@ticker/...
        const streams = [
          'btcusdt@ticker',
          'ethusdt@ticker',
          'bnbusdt@ticker',
          'solusdt@ticker',
          'dogeusdt@ticker',
          'trxusdt@ticker'
        ].join('/')

        const wsUrl = `wss://stream.binance.com:9443/stream?streams=${streams}`
        
        console.log('Connecting to Binance WebSocket:', wsUrl)
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('Binance WebSocket connected')
          this.isConnected = true
          
          // 连接成功后清除重连定时器
          if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
          }
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            // Binance combined stream format: { stream: 'btcusdt@ticker', data: {...} }
            if (data.stream && data.data) {
              this.updateTicker(data.stream, data.data)
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnected = false
        }

        this.ws.onclose = () => {
          console.log('WebSocket closed')
          this.isConnected = false
          
          // 自动重连机制：固定 5 秒间隔
          this.scheduleReconnect()
        }
      } catch (error) {
        console.error('Failed to initialize WebSocket:', error)
        this.isConnected = false
        
        // 如果初始化失败，也尝试重连
        this.scheduleReconnect()
      }
    },

    /**
     * 安排重连（固定 5 秒间隔）
     */
    scheduleReconnect() {
      // 如果已经有重连定时器，先清除
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
      }

      console.log(`Scheduling reconnect in ${this.reconnectInterval}ms...`)
      
      this.reconnectTimer = setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...')
        this.initWebSocket()
      }, this.reconnectInterval)
    },

    /**
     * Update ticker data from WebSocket message
     * @param {string} stream - Stream name (e.g., 'btcusdt@ticker')
     * @param {Object} data - Binance ticker data
     */
    updateTicker(stream, data) {
      // Extract symbol from stream name (e.g., 'btcusdt@ticker' -> 'BTC')
      const symbol = stream.split('@')[0].replace('usdt', '').toUpperCase()
      
      // Map Binance ticker fields to our format
      // Binance ticker 流字段：
      // - c: 最新成交价 (Latest price)
      // - P: 24h 价格变动百分比 (Price change percent)
      // - p: 24h 价格变动值 (Price change)
      // - h: 24h 最高价 (High price)
      // - l: 24h 最低价 (Low price)
      // - v: 24h 成交量（基础资产）(Base asset volume)
      // - q: 24h 成交量（计价资产，USDT）(Quote asset volume)
      
      this.tickers[symbol] = {
        symbol: symbol,
        price: parseFloat(data.c) || 0,           // c: 最新成交价 -> price
        change: parseFloat(data.P) || 0,          // P: 24h涨跌幅百分比 -> change
        priceChange: parseFloat(data.p) || 0,     // p: 24h价格变动值（可选）
        high: parseFloat(data.h) || 0,            // h: 24h最高价
        low: parseFloat(data.l) || 0,             // l: 24h最低价
        volume: parseFloat(data.v) || 0,          // v: 24h成交量（基础资产）
        quoteVolume: parseFloat(data.q) || 0,     // q: 24h成交量（USDT）
        lastUpdate: Date.now()
      }
    },

    /**
     * Close WebSocket connection
     */
    closeWebSocket() {
      // 清除重连定时器
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
        this.reconnectTimer = null
      }
      
      if (this.ws) {
        this.ws.close()
        this.ws = null
        this.isConnected = false
      }
    },

    /**
     * 检查并确保 WebSocket 连接（用于组件挂载时调用）
     */
    ensureConnection() {
      // 如果未连接或连接已断开，则初始化连接
      if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        console.log('WebSocket not connected, initializing...')
        this.initWebSocket()
      }
    }
  }
})

