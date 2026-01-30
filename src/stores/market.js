import { defineStore } from 'pinia'

export const useMarketStore = defineStore('market', {
  state: () => ({
    // Tickers data mapped by symbol (e.g., 'BTC', 'ETH')
    tickers: {},
    // Order book depth data mapped by symbol (e.g., 'BTC', 'ETH')
    depths: {},
    // WebSocket connection state
    ws: null,
    isConnected: false,
    reconnectTimer: null, // 重连定时器
    reconnectInterval: 5000, // 固定 5 秒重连间隔
    // 模拟行情定时器（降级方案）
    mockTickerTimer: null,
    // 连接失败计数（用于判断是否需要启动降级方案）
    connectionFailureCount: 0,
    // 是否使用降级方案
    useFallback: false
  }),

  getters: {
    // Get ticker data for a specific symbol
    getTicker: (state) => (symbol) => {
      return state.tickers[symbol] || null
    },

    // Check if data is loaded for a symbol
    hasData: (state) => (symbol) => {
      return !!state.tickers[symbol]
    },
    
    // Get depth data for a specific symbol (case-insensitive)
    getDepth: (state) => (symbol) => {
      // Normalize symbol: remove '/' and convert to uppercase (e.g., 'BTC/USDT' -> 'BTC')
      const normalizedSymbol = symbol.replace('/', '').replace('USDT', '').toUpperCase()
      return state.depths[normalizedSymbol] || null
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
        // 使用 ticker 流获取 24h 涨跌幅，并增加 depth 流获取盘口深度数据
        // 注意：WebSocket 需要小写、无前缀的 symbol（如 btcusdt）
        const baseSymbols = ['btc', 'eth', 'bnb', 'sol', 'doge', 'trx', 'beat', 'aic'];
        const streams = [];
        
        baseSymbols.forEach(symbol => {
          // 清理 symbol：移除 BINANCE: 前缀（如果有），转换为小写，确保格式正确
          const cleanSymbol = symbol
            .replace(/^BINANCE:/i, '')  // 移除 BINANCE: 前缀（不区分大小写）
            .replace(/\//g, '')          // 移除斜杠
            .toLowerCase();              // 转换为小写
          
          streams.push(`${cleanSymbol}usdt@ticker`);
          streams.push(`${cleanSymbol}usdt@depth20@100ms`); // 20 档深度，100ms 更新
        });

        const wsUrl = `wss://stream.binance.com:9443/stream?streams=${streams.join('/')}`
        
        // DEBUG: 记录 WebSocket 订阅的 symbol
        console.log('[MarketStore] Subscribing to WebSocket streams:', {
          baseSymbols: baseSymbols,
          streams: streams,
          wsUrl: wsUrl
        });
        
        // 本地开发环境下降低日志级别
        if (process.env.NODE_ENV === 'development') {
          // 静默处理，不打印连接日志
        } else {
          console.log('Connecting to Binance WebSocket:', wsUrl)
        }
        
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('Binance WebSocket connected')
          this.isConnected = true
          
          // 连接成功后重置失败计数和停止降级方案
          this.connectionFailureCount = 0
          if (this.useFallback) {
            this.stopMockTicker()
            this.useFallback = false
          }
          
          // 连接成功后清除重连定时器
          if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
          }
        }

        this.ws.onmessage = (event) => {
          try {
            // DEBUG: Log raw WebSocket message
            console.log('WS Message Received:', event.data)
            
            const data = JSON.parse(event.data)
            
            // DEBUG: Log parsed data structure
            console.log('WS Parsed Data:', {
              stream: data.stream,
              hasData: !!data.data,
              dataKeys: data.data ? Object.keys(data.data) : null
            })
            
            // Binance combined stream format: { stream: 'btcusdt@ticker', data: {...} }
            if (data.stream && data.data) {
              if (data.stream.includes('@ticker')) {
                console.log('Processing ticker update:', data.stream, data.data)
                this.updateTicker(data.stream, data.data)
              } else if (data.stream.includes('@depth')) {
                console.log('Processing depth update:', data.stream, {
                  asksCount: data.data.asks?.length || 0,
                  bidsCount: data.data.bids?.length || 0,
                  sampleAsk: data.data.asks?.[0],
                  sampleBid: data.data.bids?.[0]
                })
                this.updateDepth(data.stream, data.data)
              }
            } else {
              console.warn('WS Message format unexpected:', data)
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          // 立即停止重连
          if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
          }
          
          this.isConnected = false
          
          // 打印绿色提示信息
          console.log('%c[INFO] 网络受限，已切换至本地模拟行情', 'color: #00ff00; font-weight: bold;')
          
          // 如果还没有启动降级方案，立即启动
          if (!this.useFallback) {
            this.startMockTicker()
          }
        }

        this.ws.onclose = (event) => {
          const wasConnected = this.isConnected
          this.isConnected = false
          
          // 如果关闭时未正常连接过（即连接失败），立即启动降级方案
          if (!wasConnected && !this.useFallback) {
            // 停止重连
            if (this.reconnectTimer) {
              clearTimeout(this.reconnectTimer)
              this.reconnectTimer = null
            }
            
            // 打印绿色提示信息
            console.log('%c[INFO] 网络受限，已切换至本地模拟行情', 'color: #00ff00; font-weight: bold;')
            
            // 立即启动模拟行情
            this.startMockTicker()
          } else if (wasConnected && !this.useFallback) {
            // 如果之前连接成功过，尝试重连
            this.scheduleReconnect()
          }
        }
      } catch (error) {
        this.isConnected = false
        
        // 停止重连
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer)
          this.reconnectTimer = null
        }
        
        // 打印绿色提示信息
        console.log('%c[INFO] 网络受限，已切换至本地模拟行情', 'color: #00ff00; font-weight: bold;')
        
        // 立即启动降级方案
        if (!this.useFallback) {
          this.startMockTicker()
        }
      }
    },

    /**
     * 安排重连（固定 5 秒间隔）
     */
    scheduleReconnect() {
      // 如果已经使用降级方案，不再重连
      if (this.useFallback) {
        return
      }
      
      // 如果已经有重连定时器，先清除
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
      }

      // 本地开发环境下降低日志级别
      if (process.env.NODE_ENV === 'development') {
        // 静默处理，不打印日志
      } else {
        console.log(`Scheduling reconnect in ${this.reconnectInterval}ms...`)
      }
      
      this.reconnectTimer = setTimeout(() => {
        if (process.env.NODE_ENV === 'development') {
          // 静默处理，不打印日志
        } else {
          console.log('Attempting to reconnect WebSocket...')
        }
        this.initWebSocket()
      }, this.reconnectInterval)
    },

    /**
     * 启动模拟行情定时器（降级方案）
     * 每1秒随机微调价格，确保UI上的数字还在动
     */
    async startMockTicker() {
      // 如果已经在运行，不重复启动
      if (this.mockTickerTimer) {
        return
      }
      
      this.useFallback = true
      
      // 尝试从 mock_prices.json 读取基础价格
      let jsonPrices = {}
      try {
        const response = await fetch('/mock_prices.json')
        if (response.ok) {
          jsonPrices = await response.json()
        }
      } catch (error) {
        // 如果读取失败，使用默认价格
        console.warn('无法读取 mock_prices.json，使用默认价格')
      }
      
      // 初始化基础价格（如果还没有数据）
      const baseSymbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC']
      // 如果从 JSON 读取失败，使用默认价格
      const defaultPrices = {
        'BTC': 92000,
        'ETH': 3100,
        'BNB': 590,
        'SOL': 145,
        'DOGE': 0.12,
        'TRX': 0.15,
        'BEAT': 1.2,
        'AIC': 2.0
      }
      
      // 合并价格（优先使用 JSON 中的价格）
      const basePrices = { ...defaultPrices, ...jsonPrices }
      
      // 确保每个币种都有初始数据
      baseSymbols.forEach(symbol => {
        if (!this.tickers[symbol]) {
          const basePrice = basePrices[symbol] || 100
          this.tickers[symbol] = {
            symbol: symbol,
            price: basePrice,
            change: 0,
            priceChange: 0,
            high: basePrice,
            low: basePrice,
            volume: 0,
            quoteVolume: 0,
            lastUpdate: Date.now()
          }
        }
      })
      
      // 启动定时器：每1秒更新一次价格
      this.mockTickerTimer = setInterval(() => {
        baseSymbols.forEach(symbol => {
          const ticker = this.tickers[symbol]
          if (ticker) {
            // 随机微调价格（±0.01% 范围内）
            const changePercent = (Math.random() - 0.5) * 0.0002 // -0.01% 到 +0.01%
            const newPrice = ticker.price * (1 + changePercent)
            
            // 更新价格和涨跌幅
            const basePrice = basePrices[symbol] || ticker.price
            ticker.price = newPrice
            ticker.change = changePercent * 100 // 转换为百分比
            ticker.priceChange = newPrice - basePrice
            ticker.lastUpdate = Date.now()
            
            // 更新最高价和最低价
            if (newPrice > ticker.high) {
              ticker.high = newPrice
            }
            if (newPrice < ticker.low) {
              ticker.low = newPrice
            }
          }
        })
      }, 1000) // 每1秒更新一次
      
      console.log('✅ 模拟行情定时器已启动（降级方案）')
    },

    /**
     * 停止模拟行情定时器
     */
    stopMockTicker() {
      if (this.mockTickerTimer) {
        clearInterval(this.mockTickerTimer)
        this.mockTickerTimer = null
        console.log('✅ 模拟行情定时器已停止')
      }
    },

    /**
     * Update ticker data from WebSocket message
     * @param {string} stream - Stream name (e.g., 'btcusdt@ticker')
     * @param {Object} data - Binance ticker data
     */
    updateTicker(stream, data) {
      // Extract symbol from stream name (e.g., 'btcusdt@ticker' -> 'BTC')
      const symbol = stream.split('@')[0].replace('usdt', '').toUpperCase()
      
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
     * Update depth data from WebSocket message
     * @param {string} stream - Stream name (e.g., 'btcusdt@depth20')
     * @param {Object} data - Binance depth data
     */
    updateDepth(stream, data) {
      // Extract symbol from stream (e.g., 'btcusdt@depth20@100ms' -> 'btcusdt')
      const streamSymbol = stream.split('@')[0].toLowerCase() // Keep lowercase for matching
      const symbol = streamSymbol.replace('usdt', '').toUpperCase() // Convert to uppercase for storage (e.g., 'BTC')
      
      // DEBUG: Log symbol matching
      console.log('[MarketStore] updateDepth - Stream:', stream, 'Extracted symbol:', symbol, 'Stream symbol:', streamSymbol);
      
      // Normalize data format: convert to array format [[price, quantity], ...] for consistency
      this.depths[symbol] = {
        asks: data.asks.map(item => [parseFloat(item[0]), parseFloat(item[1])]),
        bids: data.bids.map(item => [parseFloat(item[0]), parseFloat(item[1])])
      }
      
      // DEBUG: Log update result
      console.log('[MarketStore] Depth updated for', symbol, ':', {
        bidsCount: this.depths[symbol].bids.length,
        asksCount: this.depths[symbol].asks.length,
        sampleBid: this.depths[symbol].bids[0],
        sampleAsk: this.depths[symbol].asks[0]
      });
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
      
      // 停止模拟行情定时器
      this.stopMockTicker()
      this.useFallback = false
      this.connectionFailureCount = 0
      
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