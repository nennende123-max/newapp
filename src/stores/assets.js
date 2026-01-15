import { defineStore } from 'pinia'
import * as walletApi from '@/api/wallet'
import * as tradeApi from '@/api/trade'

// Helper function to load from localStorage (仅用于钱包连接状态)
const loadFromStorage = (key, defaultValue) => {
  try {
    const item = localStorage.getItem(key)
    if (item !== null) {
      return JSON.parse(item)
    }
  } catch (error) {
    console.error(`Error loading ${key} from localStorage:`, error)
  }
  return defaultValue
}

// Helper function to save to localStorage (仅用于钱包连接状态)
const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.error(`Error saving ${key} to localStorage:`, error)
  }
}

export const useAssetStore = defineStore('assets', {
  state: () => {
    // 币种价格映射（全局公用价格数据源）
    const priceMap = {
      USDT: 1.00,
      BTC: 92000.00,
      BEAT: 2.85,
      ZEC: 45.20,
      AIC: 0.85,
      MEME: 0.0025
    }
    
    return {
      // 资金和订单数据 - 初始值设为空或0，通过 initData() 从 API 获取
      usdtBalance: 0,
      holdings: {},
      orders: [],
      transactionHistory: [],
      
      // IDO 认购记录数组（暂时保留，后续可迁移到 API）
      idoRecords: [],
      
      // BEAT 代币持仓（暂时保留，后续可迁移到 API）
      beatBalance: 0,
      
      // 钱包连接状态 - 保留从 localStorage 读取
      isWalletConnected: loadFromStorage('isWalletConnected', false),
      walletAddress: loadFromStorage('walletAddress', ''),
      
      // 币种价格映射（全局公用）
      priceMap: priceMap,
      
      // 全局加载状态
      isLoading: false
    }
  },

  getters: {
    // 获取指定币种的持仓数量
    getHolding: (state) => (symbol) => {
      return state.holdings[symbol] || 0
    },

    // 获取所有持仓列表（用于 Me.vue 显示）
    getAllHoldings: (state) => {
      return Object.keys(state.holdings).map(symbol => ({
        symbol,
        balance: state.holdings[symbol]
      }))
    },

    // 计算预估总资产价值（USDT）
    estimatedTotalValue: (state) => {
      let total = 0
      
      // 1. USDT 余额（USDT 价格为 1）
      total += state.usdtBalance * (state.priceMap.USDT || 1)
      
      // 2. BEAT 代币价值
      total += state.beatBalance * (state.priceMap.BEAT || 0)
      
      // 3. 所有持仓币种的价值
      Object.keys(state.holdings).forEach(symbol => {
        const balance = state.holdings[symbol] || 0
        const price = state.priceMap[symbol] || 0
        total += balance * price
      })
      
      return total
    },

    // 计算现货账户价值（USDT余额 + 持仓总值，排除BEAT）
    spotAccountValue: (state) => {
      let total = state.usdtBalance || 0
      
      // 计算所有持仓币种的价值（排除BEAT，因为BEAT在赚币账户）
      Object.keys(state.holdings).forEach(symbol => {
        if (symbol === 'BEAT') return
        const balance = state.holdings[symbol] || 0
        const price = state.priceMap[symbol] || 0
        total += balance * price
      })
      
      return total
    },

    // 计算赚币账户价值（BEAT余额 + IEO冻结估算）
    earnAccountValue: (state) => {
      const beatValue = (state.beatBalance || 0) * (state.priceMap['BEAT'] || 0)
      // IEO 冻结估算：从 IDO 记录中计算
      const idoFrozen = state.idoRecords.reduce((sum, record) => {
        return sum + (record.amount || 0)
      }, 0)
      return beatValue + idoFrozen
    },

    // 计算 IEO 待解锁价值（模拟数据，可后续扩展）
    idoPendingValue: (state) => {
      // 模拟待解锁金额
      return 500.00
    },

    // 统一计算所有子账户之和（用于确保数据一致性）
    totalPortfolioValue: (state) => {
      // 直接计算，避免 getter 访问顺序问题
      let spotValue = state.usdtBalance || 0
      Object.keys(state.holdings).forEach(symbol => {
        if (symbol === 'BEAT') return
        const balance = state.holdings[symbol] || 0
        const price = state.priceMap[symbol] || 0
        spotValue += balance * price
      })
      
      const beatValue = (state.beatBalance || 0) * (state.priceMap['BEAT'] || 0)
      const idoFrozen = state.idoRecords.reduce((sum, record) => {
        return sum + (record.amount || 0)
      }, 0)
      const earnValue = beatValue + idoFrozen
      
      const idoPending = 500.00 // 模拟待解锁金额
      
      return spotValue + earnValue + idoPending
    }
  },

  actions: {
    /**
     * 初始化数据 - App 启动时唯一获取数据的入口
     * 从 API 获取资产和订单数据
     */
    async initData() {
      this.isLoading = true
      try {
        // 并行获取资产和订单数据
        const [assetsRes, ordersRes] = await Promise.all([
          walletApi.getAssets(),
          tradeApi.getOrders()
        ])

        // 检查响应格式
        if (assetsRes.code === 200 && assetsRes.data) {
          this.usdtBalance = assetsRes.data.balance || 0
          this.holdings = assetsRes.data.holdings || {}
        }

        if (ordersRes.code === 200 && ordersRes.data) {
          this.orders = ordersRes.data || []
        }

        // 获取交易历史（从 localStorage 读取，因为 wallet.js 的 deposit/withdraw 会写入）
        // 注意：这里暂时保留从 localStorage 读取，后续可以迁移到 API
        try {
          const txHistory = localStorage.getItem('txHistory')
          if (txHistory) {
            this.transactionHistory = JSON.parse(txHistory)
          }
        } catch (error) {
          console.error('Error loading transaction history:', error)
          this.transactionHistory = []
        }

      } catch (error) {
        console.error('Error initializing data:', error)
        // 初始化失败时使用默认值
        this.usdtBalance = 0
        this.holdings = {}
        this.orders = []
        this.transactionHistory = []
      } finally {
        this.isLoading = false
      }
    },
    
    /**
     * 连接钱包（模拟）
     */
    async connectWallet() {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 生成模拟地址
      const mockAddress = '0x' + Array.from({ length: 40 }, () => 
        Math.floor(Math.random() * 16).toString(16)
      ).join('')
      
      this.isWalletConnected = true
      this.walletAddress = mockAddress
      saveToStorage('isWalletConnected', true)
      saveToStorage('walletAddress', mockAddress)
      
      return mockAddress
    },
    
    /**
     * 断开钱包连接
     */
    disconnectWallet() {
      this.isWalletConnected = false
      this.walletAddress = ''
      saveToStorage('isWalletConnected', false)
      saveToStorage('walletAddress', '')
    },

    /**
     * 重置测试数据
     */
    resetTestData() {
      localStorage.removeItem('userBalance')
      localStorage.removeItem('userHoldings')
      localStorage.removeItem('userOrders')
      localStorage.removeItem('userIDORecords')
      localStorage.removeItem('txHistory')
      localStorage.removeItem('beatBalance')
      localStorage.removeItem('isWalletConnected')
      localStorage.removeItem('walletAddress')
      location.reload()
    },

    /**
     * 充值 USDT
     * @param {number} amount - 充值金额
     * @returns {Promise<boolean>} - 成功返回 true
     */
    async deposit(amount) {
      this.isLoading = true
      try {
        const res = await walletApi.deposit(amount)
        
        if (res.code === 200) {
          // 重新拉取最新数据
          await this.initData()
          return true
        } else {
          throw new Error(res.msg || '充值失败')
        }
      } catch (error) {
        console.error('Deposit error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 提现 USDT
     * @param {number} amount - 提现金额
     * @returns {Promise<boolean>} - 成功返回 true
     */
    async withdraw(amount) {
      this.isLoading = true
      try {
        const res = await walletApi.withdraw(amount)
        
        if (res.code === 200) {
          // 重新拉取最新数据
          await this.initData()
          return true
        } else {
          throw new Error(res.msg || '提现失败')
        }
      } catch (error) {
        console.error('Withdraw error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 创建订单（限价单）
     * @param {Object} order - 订单对象
     * @param {string} order.symbol - 币种符号
     * @param {string} order.type - 'BUY' 或 'SELL'
     * @param {number} order.price - 订单价格
     * @param {number} order.amount - 订单数量
     * @returns {Promise<boolean>} - 成功返回 true
     */
    async createOrder(order) {
      this.isLoading = true
      try {
        const { symbol, type, price, amount } = order
        
        // 转换格式：type 'BUY'/'SELL' -> side 'buy'/'sell'
        const side = type.toLowerCase()
        
        const res = await tradeApi.submitOrder({
          symbol,
          side,
          price,
          amount
        })
        
        if (res.code === 200) {
          // 重新拉取最新数据
          await this.initData()
          return true
        } else {
          throw new Error(res.msg || '下单失败')
        }
      } catch (error) {
        console.error('Create order error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 取消订单
     * @param {number|string} orderId - 订单ID
     * @returns {Promise<boolean>} - 成功返回 true
     */
    async cancelOrder(orderId) {
      this.isLoading = true
      try {
        const res = await tradeApi.cancelOrder(orderId)
        
        if (res.code === 200) {
          // 重新拉取最新数据
          await this.initData()
          return true
        } else {
          throw new Error(res.msg || '撤单失败')
        }
      } catch (error) {
        console.error('Cancel order error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 添加交易历史记录（保留用于 IDO 等场景）
     * @param {Object} record - 交易记录对象
     */
    addTransaction(record) {
      const now = new Date()
      const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
      const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
      
      const transaction = {
        id: Date.now() + Math.random(),
        time: `${dateStr} ${timeStr}`,
        type: record.type,
        amount: record.amount,
        status: record.status || '成功',
        tx_id: record.tx_id || null,
        chain_name: record.chain_name || null,
        project_name: record.project_name || null,
        price: record.price || null,
        total_cost: record.total_cost || record.amount || null,
        token_amount: record.token_amount || null
      }
      
      this.transactionHistory.unshift(transaction)
      
      // 保存到 localStorage（因为 wallet.js 的 API 会写入，这里同步更新）
      try {
        const txHistory = JSON.parse(localStorage.getItem('txHistory') || '[]')
        txHistory.unshift(transaction)
        localStorage.setItem('txHistory', JSON.stringify(txHistory))
      } catch (error) {
        console.error('Error saving transaction history:', error)
      }
    },

    /**
     * 参与 IDO 认购（暂时保留，后续可迁移到 API）
     * @param {Object} project - 项目对象
     * @returns {boolean} - 成功返回 true
     */
    joinIDO(project) {
      // 检查是否已经认购过该项目
      const alreadyJoined = this.idoRecords.some(record => 
        record.name === project.name || record.ticker === project.ticker
      )
      
      if (alreadyJoined) {
        return false
      }
      
      const allocationAmount = project.minAlloc || 100
      
      if (this.usdtBalance < allocationAmount) {
        return false
      }
      
      this.usdtBalance -= allocationAmount
      
      const record = {
        id: Date.now() + Math.random(),
        name: project.name,
        ticker: project.ticker || '',
        price: project.price || 0,
        amount: allocationAmount,
        timestamp: new Date().toISOString()
      }
      
      this.idoRecords.push(record)
      
      const exchangeRate = 10
      const beatAmount = allocationAmount * exchangeRate
      this.beatBalance += beatAmount
      
      this.addTransaction({
        type: '认购',
        amount: -allocationAmount,
        status: '成功',
        project_name: project.name || 'Unknown Project',
        price: project.price || 0.1,
        total_cost: allocationAmount,
        token_amount: beatAmount
      })
      
      return true
    },

    /**
     * 交易操作（立即成交，用于市价单或测试）
     * @param {string} type - 'BUY' 或 'SELL'
     * @param {string} symbol - 币种符号
     * @param {number} amount - 交易数量
     * @param {number} price - 交易价格
     * @returns {boolean} - 成功返回 true
     */
    trade(type, symbol, amount, price) {
      const totalCost = amount * price

      if (type === 'BUY') {
        if (this.usdtBalance < totalCost) {
          return false
        }
        
        this.usdtBalance -= totalCost
        if (!this.holdings[symbol]) {
          this.holdings[symbol] = 0
        }
        this.holdings[symbol] += amount
        return true
      } 
      
      else if (type === 'SELL') {
        const currentHolding = this.holdings[symbol] || 0
        if (currentHolding < amount) {
          return false
        }
        
        this.holdings[symbol] -= amount
        if (this.holdings[symbol] <= 0) {
          delete this.holdings[symbol]
        }
        this.usdtBalance += totalCost
        return true
      }
      
      return false
    }
  }
})

