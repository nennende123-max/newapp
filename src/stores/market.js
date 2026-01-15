import { defineStore } from 'pinia'

export const useMarketStore = defineStore('market', {
  state: () => ({
    // Tickers data mapped by symbol (e.g., 'BTC', 'ETH')
    tickers: {},
    // WebSocket connection state
    ws: null,
    isConnected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5
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

      try {
        // Binance WebSocket endpoint for combined streams
        // Format: stream1@miniTicker/stream2@miniTicker/...
        const streams = [
          'btcusdt@miniTicker',
          'ethusdt@miniTicker',
          'bnbusdt@miniTicker',
          'solusdt@miniTicker',
          'dogeusdt@miniTicker',
          'trxusdt@miniTicker'
        ].join('/')

        const wsUrl = `wss://stream.binance.com:9443/stream?streams=${streams}`
        
        console.log('Connecting to Binance WebSocket:', wsUrl)
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('Binance WebSocket connected')
          this.isConnected = true
          this.reconnectAttempts = 0
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            // Binance combined stream format: { stream: 'btcusdt@miniTicker', data: {...} }
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
          
          // Attempt to reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000) // Exponential backoff, max 30s
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
            
            setTimeout(() => {
              this.initWebSocket()
            }, delay)
          } else {
            console.error('Max reconnection attempts reached')
          }
        }
      } catch (error) {
        console.error('Failed to initialize WebSocket:', error)
        this.isConnected = false
      }
    },

    /**
     * Update ticker data from WebSocket message
     * @param {string} stream - Stream name (e.g., 'btcusdt@miniTicker')
     * @param {Object} data - Binance ticker data
     */
    updateTicker(stream, data) {
      // Extract symbol from stream name (e.g., 'btcusdt@miniTicker' -> 'BTC')
      const symbol = stream.split('@')[0].replace('usdt', '').toUpperCase()
      
      // Map Binance fields to our format
      // Binance miniTicker fields:
      // - c: Close price (last price)
      // - P: Price change percent (24h)
      // - h: High price (24h)
      // - l: Low price (24h)
      // - v: Base asset volume (24h)
      // - q: Quote asset volume (24h) - USDT volume
      
      this.tickers[symbol] = {
        symbol: symbol,
        price: parseFloat(data.c) || 0,           // Close price (current price)
        change: parseFloat(data.P) || 0,           // Price change percent (24h)
        high: parseFloat(data.h) || 0,             // High price (24h)
        low: parseFloat(data.l) || 0,              // Low price (24h)
        volume: parseFloat(data.v) || 0,           // Base asset volume (24h)
        quoteVolume: parseFloat(data.q) || 0,      // Quote asset volume (USDT, 24h)
        lastUpdate: Date.now()
      }
    },

    /**
     * Close WebSocket connection
     */
    closeWebSocket() {
      if (this.ws) {
        this.ws.close()
        this.ws = null
        this.isConnected = false
      }
    }
  }
})

