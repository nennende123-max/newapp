import { defineStore } from 'pinia'
import * as walletApi from '@/api/wallet'
import * as tradeApi from '@/api/trade'
import { walletConnect } from '@/api/user'
import { useI18n } from 'vue-i18n'
import request from '@/utils/request'

// Helper function to load from localStorage (用于钱包连接状态和 BNB 开关状态)
const loadFromStorage = (key, defaultValue) => {
  try {
    const item = localStorage.getItem(key)
    if (item !== null) {
      // 对于布尔值，直接比较字符串
      if (typeof defaultValue === 'boolean') {
        return item === 'true'
      }
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
      userAssets: null, // 完整的资产数据（包括冻结余额）
      orders: [],
      transactionHistory: [],
      
      // IDO 认购记录数组（暂时保留，后续可迁移到 API）
      idoRecords: [],
      
      // BEAT 代币持仓（暂时保留，后续可迁移到 API）
      beatBalance: 0,
      
      // 账户权益相关（包含合约盈亏）
      equity: 0, // 账户权益 = 可用余额 + 冻结保证金 + 合约未实现盈亏
      futuresUnrealizedPnl: 0, // 合约未实现盈亏总计
      
      // 钱包连接状态 - 保留从 localStorage 读取
      isWalletConnected: loadFromStorage('isWalletConnected', false),
      walletAddress: loadFromStorage('walletAddress', ''),
      
      // BNB 支付开关状态 - 从 localStorage 读取，默认 true
      useBNBForFees: loadFromStorage('useBNBForFees', true),
      useBNBForInterest: loadFromStorage('useBNBForInterest', true),
      
      // 币种价格映射（全局公用）
      priceMap: priceMap,
      
      // 全局加载状态
      isLoading: false
    }
  },

  getters: {
    // 获取指定币种的持仓数量（优先从 userAssets 中获取）
    getHolding: (state) => (symbol) => {
      // 自动转大写，防止 symbol 大小写不匹配
      const key = symbol?.toUpperCase()
      
      // 优先从 userAssets 中获取（包含所有币种）
      if (state.userAssets && state.userAssets[key] !== undefined) {
        return state.userAssets[key] || 0
      }
      
      // 兼容旧代码：从 holdings 中获取
      return state.holdings[key] || 0
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

    // 计算 IEO 待解锁价值（动态数据）
    idoPendingValue: (state) => {
      // 从 IDO 记录中计算待解锁金额（动态数据，不再使用写死的 500）
      // TODO: 后续可以从 API 获取真实的待解锁金额
      return state.idoRecords.reduce((sum, record) => {
        // 假设有 pending 字段表示待解锁金额
        return sum + (record.pending || 0)
      }, 0)
    },

    // 统一计算所有子账户之和（用于确保数据一致性）
    // 注意：如果 equity 已设置，优先使用 equity（包含合约盈亏）
    totalPortfolioValue: (state) => {
      // 如果 equity 已设置且大于 0，优先使用 equity（包含合约未实现盈亏）
      if (state.equity > 0) {
        return state.equity
      }
      
      // 否则使用传统计算方式（兼容旧代码）
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
      
      // 动态计算 IEO 待解锁金额（不再使用写死的 500）
      const idoPending = state.idoRecords.reduce((sum, record) => {
        return sum + (record.pending || 0)
      }, 0)
      
      return spotValue + earnValue + idoPending
    },

    // 当前现货费率（根据 useBNBForFees 状态动态计算）
    currentSpotFeeRate: (state) => {
      // 如果开启 BNB 支付手续费，享受 25% 折扣：0.001 * 0.75 = 0.00075
      // 如果关闭，返回标准费率 0.001 (0.1%)
      return state.useBNBForFees ? 0.00075 : 0.001
    },

    // U 本位费率（根据 useBNBForFees 状态动态计算）
    currentFuturesFeeRate: (state) => {
      // 挂单费率：如果开启 BNB，享受 25% 折扣：0.0002 * 0.75 = 0.00015
      // 吃单费率：如果开启 BNB，享受 25% 折扣：0.0004 * 0.75 = 0.0003
      return {
        maker: state.useBNBForFees ? 0.00015 : 0.0002,  // 挂单费率 (0.015% 或 0.02%)
        taker: state.useBNBForFees ? 0.0003 : 0.0004    // 吃单费率 (0.03% 或 0.04%)
      }
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
        // 获取完整资产数据（包括冻结余额和账户权益）
        const [assetsResponse, ordersRes] = await Promise.all([
          request.get('/api/v1/assets/'), // 使用 /api/v1/assets/ 获取包含 equity 的数据
          tradeApi.getOrders()
        ])

        // 检查响应格式
        // /api/v1/assets/ 返回的格式：{ code: 200, data: { balance: 50000, equity: 51234.56, holdings: {...}, frozen: {...}, futures_unrealized_pnl: 1234.56 } }
        console.log('前端接收到的完整资产数据:', assetsResponse)
        
        // 处理响应数据
        let assetsData = null
        
        // 检查响应格式：axios 返回 { data: { code: 200, data: {...} } }
        if (assetsResponse && assetsResponse.data) {
          const response = assetsResponse.data
          
          // 检查后端返回的 code
          if (response.code === 200 && response.data) {
            assetsData = response.data
          } else {
            console.warn('⚠️ 后端返回错误:', response.message || '未知错误')
          }
        } else {
          console.warn('⚠️ 资产数据格式异常:', assetsResponse)
        }
        
        // 如果成功获取到数据，更新状态
        if (assetsData) {
          // 提取账户权益和合约盈亏
          this.equity = assetsData.equity || 0
          this.futuresUnrealizedPnl = assetsData.futures_unrealized_pnl || 0
          
          // 兼容旧格式：如果返回的是旧格式（直接是资产字典），则从 holdings 中提取
          let assets = {}
          if (assetsData.holdings) {
            // 新格式：从 holdings 和 frozen 中提取
            assets = { ...assetsData.holdings }
            // 添加冻结余额字段
            Object.keys(assetsData.frozen || {}).forEach(coin => {
              assets[`${coin}_frozen`] = assetsData.frozen[coin]
            })
          } else {
            // 旧格式：直接使用 data
            assets = assetsData
          }
          
          // 存储完整的资产数据（包括冻结余额）
          this.userAssets = { ...assets }
          
          // 提取 USDT 可用余额
          const balance = assets.USDT || 0
          
          // 全量提取所有币种的可用余额（排除 USDT 和冻结字段）
          const holdings = {}
          const supportedCoins = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC']
          
          supportedCoins.forEach(coin => {
            if (assets[coin] !== undefined) {
              holdings[coin] = assets[coin] || 0
            }
          })
          
          // 如果后端返回了其他币种，也一并添加（动态支持）
          Object.keys(assets).forEach(key => {
            // 排除 USDT、冻结字段（_frozen）和已处理的币种
            if (key !== 'USDT' && !key.endsWith('_frozen') && !supportedCoins.includes(key)) {
              holdings[key] = assets[key] || 0
            }
          })
          
          console.log('解析后的资产数据:', { 
            balance, 
            holdings, 
            equity: this.equity,
            futuresUnrealizedPnl: this.futuresUnrealizedPnl,
            frozen: { 
              USDT: assets.USDT_frozen || 0, 
              BTC: assets.BTC_frozen || 0,
              ETH: assets.ETH_frozen || 0,
            },
            fullAssets: assets
          })
          
          // 关键：确保将 API 返回的 balance 正确赋值给 state
          this.usdtBalance = balance
          this.holdings = holdings
          
          // 如果 holdings 中有 BEAT，也更新 beatBalance（兼容旧代码）
          if (holdings.BEAT !== undefined) {
            this.beatBalance = holdings.BEAT
          }
          
          // 调试确认：在赋值语句之后，立即打印确保数据真的存进去了
          console.log('✅ State更新后余额:', this.usdtBalance)
          console.log('✅ State更新后持仓:', this.holdings)
          console.log('✅ State更新后账户权益:', this.equity)
          console.log('✅ State更新后合约盈亏:', this.futuresUnrealizedPnl)
          console.log('✅ State更新后完整资产数据:', this.userAssets)
        } else {
          // 如果没有获取到数据，不要重置为 0，保留现有数据
          console.warn('⚠️ 未能获取到资产数据，保留现有状态')
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
        console.error('❌ Error initializing data:', error)
        console.error('错误详情:', error.response?.data || error.message)
        
        // 初始化失败时，不要重置为 0，保留现有数据
        // 这样可以避免因为网络问题或临时错误导致数据丢失
        // 只有在确认是认证失败（401）时才清除数据
        if (error.response?.status === 401) {
          console.warn('⚠️ 认证失败，清除数据')
          this.usdtBalance = 0
          this.holdings = {}
          this.orders = []
          this.transactionHistory = []
          this.equity = 0
          this.futuresUnrealizedPnl = 0
        } else {
          console.warn('⚠️ 数据加载失败，保留现有状态')
        }
      } finally {
        this.isLoading = false
      }
    },
    
    /**
     * 检查是否安装了 Web3 钱包
     * 在页面加载时调用，用于检测钱包是否可用
     */
    checkWalletInstalled() {
      return typeof window.ethereum !== 'undefined'
    },

    /**
     * 连接 Web3 钱包并完成认证
     * 参考币安 Web3 钱包的认证流程
     */
    async connectWallet() {
      try {
        // 1. 检查是否安装了 Web3 钱包（MetaMask、币安钱包等）
        // window.ethereum 是 Web3 钱包注入到浏览器的全局对象
        if (typeof window.ethereum === 'undefined') {
          throw new Error('请安装钱包')
        }

        // 2. 请求用户授权连接钱包
        // request 方法会弹出钱包授权窗口，用户需要点击"连接"或"授权"
        const accounts = await window.ethereum.request({
          method: 'eth_requestAccounts'
        });
        
        if (!accounts || accounts.length === 0) {
          throw new Error('没有检测到钱包地址');
        }
        // --- 到这里，address 已经在整个 connectWallet 内部“自由”了 ---
        const address = accounts[0];

        // 3. 获取 i18n 消息
        const { i18n } = await import('@/main');
        const message = i18n.global.t('auth.signMessage');

        // 4. 发起签名
        // 使用 personal_sign 方法请求用户签名消息
        // 用户需要在钱包中确认签名，签名后会返回签名结果（十六进制字符串）
        const signature = await window.ethereum.request({
          method: 'personal_sign',
          params: [message, address]
        });

        // 5. 将签名发送到后端进行验证
        // walletConnect 函数会调用 request.post('/api/v1/auth/connect', data)
        // 实际请求的 URL 是：http://127.0.0.1:8000/api/v1/auth/connect
        const response = await walletConnect({
          address: address,
          signature: signature,
          message: message
        });

        // 6. 检查响应格式，确保后端返回了正确的数据
        if (response.data && response.data.code === 200 && response.data.data) {
          // 8. 成功拿到后端返回的 JWT Token
          const token = response.data.data.token

          // 9. 将 Token 存入 localStorage
          // localStorage.setItem('token', ...) 用于持久化存储 Token
          // 即使关闭浏览器，Token 也会保留（直到用户清除浏览器数据）
          // 后续请求会自动从 localStorage 读取 Token 并添加到请求头
          localStorage.setItem('token', token)

          // 10. 保存钱包地址到 localStorage（可选，用于显示）
          localStorage.setItem('walletAddress', address)

          // 11. 更新 Store 状态
          this.isWalletConnected = true
          this.walletAddress = address
          saveToStorage('isWalletConnected', true)
          saveToStorage('walletAddress', address)

          // 12. 打印激活提示
          console.log('✅ 机构级账户已激活')
          console.log('钱包地址:', address)
          console.log('Token:', token)

          // 返回成功信息，包含地址和 token
          return {
            success: true,
            address: address,
            token: token
          }
        } else {
          throw new Error('认证失败：服务器返回异常')
        }

      } catch (error) {
        console.error('连接钱包失败:', error)
        
        // 如果是用户拒绝连接或签名，给出友好提示
        if (error.code === 4001) {
          throw new Error('用户拒绝了钱包连接请求')
        } else if (error.code === -32002) {
          throw new Error('钱包连接请求已在进行中，请稍候')
        } else {
          throw error
        }
      }
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
    /**
     * 充值操作
     * 调用后端 API 进行充值，成功后重新拉取余额
     * 
     * @param {number} amount - 充值金额
     * @param {string} currency - 币种，默认为 'USDT'
     * @returns {Promise<boolean>} 成功返回 true
     */
    async deposit(amount, currency = 'USDT') {
      this.isLoading = true
      try {
        // 调用后端 API 进行充值
        const res = await walletApi.deposit(amount, currency)
        
        // 检查响应格式
        if (res.data && res.data.code === 200 && res.data.data) {
          // 更新本地状态（可选，也可以等 initData 拉取）
          const assets = res.data.data
          this.usdtBalance = assets.USDT || this.usdtBalance
          if (assets.BTC !== undefined) this.holdings.BTC = assets.BTC
          if (assets.BEAT !== undefined) this.beatBalance = assets.BEAT
          
          // 重新拉取最新数据（确保数据一致性）
          await this.initData()
          return true
        } else {
          throw new Error(res.data?.message || res.message || '充值失败')
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
    /**
     * 提现操作
     * 调用后端 API 进行提现，成功后重新拉取余额
     * 
     * @param {number} amount - 提现金额
     * @param {string} currency - 币种，默认为 'USDT'
     * @returns {Promise<boolean>} 成功返回 true
     */
    async withdraw(amount, currency = 'USDT') {
      this.isLoading = true
      try {
        // 调用后端 API 进行提现
        const res = await walletApi.withdraw(amount, currency)
        
        // 检查响应格式
        if (res.data && res.data.code === 200 && res.data.data) {
          // 更新本地状态（可选，也可以等 initData 拉取）
          const assets = res.data.data
          this.usdtBalance = assets.USDT || this.usdtBalance
          if (assets.BTC !== undefined) this.holdings.BTC = assets.BTC
          if (assets.BEAT !== undefined) this.beatBalance = assets.BEAT
          
          // 重新拉取最新数据（确保数据一致性）
          await this.initData()
          return true
        } else {
          throw new Error(res.data?.message || res.message || '提现失败')
        }
      } catch (error) {
        console.error('Withdraw error:', error)
        // 如果是余额不足的错误，显示更友好的提示
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        }
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
    },

    /**
     * 切换 BNB 支付交易手续费开关
     * @param {boolean} value - 开关状态
     */
    toggleBNBForFees(value) {
      this.useBNBForFees = value
      // 同步写入 localStorage
      try {
        localStorage.setItem('useBNBForFees', value.toString())
      } catch (error) {
        console.error('Error saving useBNBForFees to localStorage:', error)
      }
    },

    /**
     * 切换 BNB 支付杠杆利息开关
     * @param {boolean} value - 开关状态
     */
    toggleBNBForInterest(value) {
      this.useBNBForInterest = value
      // 同步写入 localStorage
      try {
        localStorage.setItem('useBNBForInterest', value.toString())
      } catch (error) {
        console.error('Error saving useBNBForInterest to localStorage:', error)
      }
    }
  }
})

