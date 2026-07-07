import { defineStore } from 'pinia'
import * as walletApi from '@/api/wallet'
import * as tradeApi from '@/api/trade'
import request from '@/utils/request'
import walletService from '@/services/walletService'
import { isProdMode } from '@/config/appMode'

const shouldUseLocalData = () => {
  return import.meta.env.DEV || !isProdMode() || localStorage.getItem('TRUTHFI_FRONTEND_ONLY') === 'true'
}

// Helper function to load from localStorage (鐢ㄤ簬閽卞寘杩炴帴鐘舵€佸拰 BNB 寮€鍏崇姸鎬?
const loadFromStorage = (key, defaultValue) => {
  try {
    const item = localStorage.getItem(key)
    if (item !== null) {
      // 瀵逛簬甯冨皵鍊硷紝鐩存帴姣旇緝瀛楃涓?
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

// Helper function to save to localStorage (浠呯敤浜庨挶鍖呰繛鎺ョ姸鎬?
const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.error(`Error saving ${key} to localStorage:`, error)
  }
}

const withTimeout = (promise, ms, message, code = 'REQUEST_TIMEOUT') => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      const error = new Error(message)
      error.code = code
      reject(error)
    }, ms)

    Promise.resolve(promise)
      .then((value) => {
        clearTimeout(timer)
        resolve(value)
      })
      .catch((error) => {
        clearTimeout(timer)
        reject(error)
      })
  })
}

export const useAssetStore = defineStore('assets', {
  state: () => {
    // 甯佺浠锋牸鏄犲皠锛堝叏灞€鍏敤浠锋牸鏁版嵁婧愶級
    const priceMap = {
      USDT: 1.00,
      USDC: 1.00,
      FDUSD: 1.00,
      BTC: 92000.00,
      BEAT: 2.85,
      ZEC: 45.20,
      AIC: 0.85,
      MEME: 0.0025
    }
    
    return {
      // 璧勯噾鍜岃鍗曟暟鎹?- 鍒濆鍊艰涓虹┖鎴?锛岄€氳繃 initData() 浠?API 鑾峰彇
      usdtBalance: 0,
      holdings: {},
      userAssets: null, // 瀹屾暣鐨勮祫浜ф暟鎹紙鍖呮嫭鍐荤粨浣欓锛?
      orders: [],
      transactionHistory: [],
      
      // IDO 璁よ喘璁板綍鏁扮粍锛堟殏鏃朵繚鐣欙紝鍚庣画鍙縼绉诲埌 API锛?
      idoRecords: Array.isArray(loadFromStorage('userIDORecords', []))
        ? loadFromStorage('userIDORecords', [])
        : [],
      ieoAssets: loadFromStorage('ieoAssets', {}),
      launchpadStakingPositions: Array.isArray(loadFromStorage('launchpadStakingPositions', []))
        ? loadFromStorage('launchpadStakingPositions', [])
        : [],
      
      // BEAT 浠ｅ竵鎸佷粨锛堟殏鏃朵繚鐣欙紝鍚庣画鍙縼绉诲埌 API锛?
      beatBalance: 0,
      
      // 璐︽埛鏉冪泭鐩稿叧锛堝寘鍚悎绾︾泩浜忥級
      equity: 0, // 璐︽埛鏉冪泭 = 鍙敤浣欓 + 鍐荤粨淇濊瘉閲?+ 鍚堢害鏈疄鐜扮泩浜?
      futuresUnrealizedPnl: 0, // 鍚堢害鏈疄鐜扮泩浜忔€昏
      
      // 閽卞寘杩炴帴鐘舵€?- 淇濈暀浠?localStorage 璇诲彇
      isWalletConnected: loadFromStorage('isWalletConnected', false),
      walletAddress: loadFromStorage('walletAddress', ''),
      
      // BNB 鏀粯寮€鍏崇姸鎬?- 浠?localStorage 璇诲彇锛岄粯璁?true
      useBNBForFees: loadFromStorage('useBNBForFees', true),
      useBNBForInterest: loadFromStorage('useBNBForInterest', true),
      
      // 甯佺浠锋牸鏄犲皠锛堝叏灞€鍏敤锛?
      priceMap: priceMap,
      
      // 鍏ㄥ眬鍔犺浇鐘舵€?
      isLoading: false,
      
      // 鎸佷粨鍒楄〃锛堢敤浜庡悓姝ワ級
      positions: []
    }
  },

  getters: {
    // 鑾峰彇鎸囧畾甯佺鐨勬寔浠撴暟閲忥紙浼樺厛浠?userAssets 涓幏鍙栵級
    getHolding: (state) => (symbol) => {
      // 鑷姩杞ぇ鍐欙紝闃叉 symbol 澶у皬鍐欎笉鍖归厤
      const key = symbol?.toUpperCase()
      
      // 浼樺厛浠?userAssets 涓幏鍙栵紙鍖呭惈鎵€鏈夊竵绉嶏級
      if (state.userAssets && state.userAssets[key] !== undefined) {
        return state.userAssets[key] || 0
      }
      
      // 鍏煎鏃т唬鐮侊細浠?holdings 涓幏鍙?
      return state.holdings[key] || 0
    },

    // 鑾峰彇鎵€鏈夋寔浠撳垪琛紙鐢ㄤ簬 Me.vue 鏄剧ず锛?
    getAllHoldings: (state) => {
      return Object.keys(state.holdings).map(symbol => ({
        symbol,
        balance: state.holdings[symbol]
      }))
    },

    // 璁＄畻棰勪及鎬昏祫浜т环鍊硷紙USDT锛?
    estimatedTotalValue: (state) => {
      let total = 0
      
      // 1. USDT 浣欓锛圲SDT 浠锋牸涓?1锛?
      total += state.usdtBalance * (state.priceMap.USDT || 1)
      
      // 2. BEAT 浠ｅ竵浠峰€?
      total += state.beatBalance * (state.priceMap.BEAT || 0)
      
      // 3. 鎵€鏈夋寔浠撳竵绉嶇殑浠峰€?
      Object.keys(state.holdings).forEach(symbol => {
        const balance = state.holdings[symbol] || 0
        const price = state.priceMap[symbol] || 0
        total += balance * price
      })
      
      return total
    },

    // 璁＄畻鐜拌揣璐︽埛浠峰€硷紙USDT浣欓 + 鎸佷粨鎬诲€硷紝鎺掗櫎BEAT锛?
    spotAccountValue: (state) => {
      let total = state.usdtBalance || 0
      
      // 璁＄畻鎵€鏈夋寔浠撳竵绉嶇殑浠峰€硷紙鎺掗櫎BEAT锛屽洜涓築EAT鍦ㄨ禋甯佽处鎴凤級
      Object.keys(state.holdings).forEach(symbol => {
        if (symbol === 'BEAT') return
        const balance = state.holdings[symbol] || 0
        const price = state.priceMap[symbol] || 0
        total += balance * price
      })
      
      return total
    },

    // 璁＄畻璧氬竵璐︽埛浠峰€硷紙BEAT浣欓 + IEO鍐荤粨浼扮畻锛?
    earnAccountValue: (state) => {
      const beatValue = (state.beatBalance || 0) * (state.priceMap['BEAT'] || 0)
      // IEO 鍐荤粨浼扮畻锛氫粠 IDO 璁板綍涓绠?
      const idoRecords = Array.isArray(state.idoRecords) ? state.idoRecords : []
      const idoFrozen = idoRecords.reduce((sum, record) => {
        return sum + (record.amount || 0)
      }, 0)
      return beatValue + idoFrozen
    },

    // 璁＄畻 IEO 寰呰В閿佷环鍊硷紙鍔ㄦ€佹暟鎹級
    idoPendingValue: (state) => {
      // 浠?IDO 璁板綍涓绠楀緟瑙ｉ攣閲戦锛堝姩鎬佹暟鎹紝涓嶅啀浣跨敤鍐欐鐨?500锛?
      // TODO: 鍚庣画鍙互浠?API 鑾峰彇鐪熷疄鐨勫緟瑙ｉ攣閲戦
      const idoRecords = Array.isArray(state.idoRecords) ? state.idoRecords : []
      return idoRecords.reduce((sum, record) => {
        // 鍋囪鏈?pending 瀛楁琛ㄧず寰呰В閿侀噾棰?
        return sum + (record.pending || 0)
      }, 0)
    },

    // 缁熶竴璁＄畻鎵€鏈夊瓙璐︽埛涔嬪拰锛堢敤浜庣‘淇濇暟鎹竴鑷存€э級
    // 娉ㄦ剰锛氬鏋?equity 宸茶缃紝浼樺厛浣跨敤 equity锛堝寘鍚悎绾︾泩浜忥級
    launchpadStakingValue: (state) => {
      const positions = Array.isArray(state.launchpadStakingPositions) ? state.launchpadStakingPositions : []
      return positions.reduce((sum, position) => {
        return sum + (Number(position.amountUsdt) || 0)
      }, 0)
    },

    launchpadTotalRewards: (state) => {
      const positions = Array.isArray(state.launchpadStakingPositions) ? state.launchpadStakingPositions : []
      return positions.reduce((sum, position) => {
        return sum + (Number(position.claimableReward) || 0)
      }, 0)
    },

    launchpadRemainingAllocation: (state) => {
      const baseAllocation = 999
      const positions = Array.isArray(state.launchpadStakingPositions) ? state.launchpadStakingPositions : []
      const boostAllocation = positions.reduce((sum, position) => {
        return sum + ((Number(position.amountUsdt) || 0) * (Number(position.boostRate) || 0))
      }, 0)
      const idoRecords = Array.isArray(state.idoRecords) ? state.idoRecords : []
      const used = idoRecords.reduce((sum, record) => sum + (Number(record.amount) || 0), 0)
      return Math.max(0, baseAllocation + boostAllocation - used)
    },

    totalPortfolioValue: (state) => {
      // 濡傛灉 equity 宸茶缃笖澶т簬 0锛屼紭鍏堜娇鐢?equity锛堝寘鍚悎绾︽湭瀹炵幇鐩堜簭锛?
      if (state.equity > 0) {
        return state.equity
      }
      
      // 鍚﹀垯浣跨敤浼犵粺璁＄畻鏂瑰紡锛堝吋瀹规棫浠ｇ爜锛?
      let spotValue = state.usdtBalance || 0
      Object.keys(state.holdings).forEach(symbol => {
        if (symbol === 'BEAT') return
        const balance = state.holdings[symbol] || 0
        const price = state.priceMap[symbol] || 0
        spotValue += balance * price
      })
      
      const beatValue = (state.beatBalance || 0) * (state.priceMap['BEAT'] || 0)
      const idoRecords = Array.isArray(state.idoRecords) ? state.idoRecords : []
      const idoFrozen = idoRecords.reduce((sum, record) => {
        return sum + (record.amount || 0)
      }, 0)
      const earnValue = beatValue + idoFrozen
      
      // 鍔ㄦ€佽绠?IEO 寰呰В閿侀噾棰濓紙涓嶅啀浣跨敤鍐欐鐨?500锛?
      const idoPending = idoRecords.reduce((sum, record) => {
        return sum + (record.pending || 0)
      }, 0)
      
      return spotValue + earnValue + idoPending
    },

    // 褰撳墠鐜拌揣璐圭巼锛堟牴鎹?useBNBForFees 鐘舵€佸姩鎬佽绠楋級
    currentSpotFeeRate: (state) => {
      // 濡傛灉寮€鍚?BNB 鏀粯鎵嬬画璐癸紝浜彈 25% 鎶樻墸锛?.001 * 0.75 = 0.00075
      // 濡傛灉鍏抽棴锛岃繑鍥炴爣鍑嗚垂鐜?0.001 (0.1%)
      return state.useBNBForFees ? 0.00075 : 0.001
    },

    // U 鏈綅璐圭巼锛堟牴鎹?useBNBForFees 鐘舵€佸姩鎬佽绠楋級
    currentFuturesFeeRate: (state) => {
      // 鎸傚崟璐圭巼锛氬鏋滃紑鍚?BNB锛屼韩鍙?25% 鎶樻墸锛?.0002 * 0.75 = 0.00015
      // 鍚冨崟璐圭巼锛氬鏋滃紑鍚?BNB锛屼韩鍙?25% 鎶樻墸锛?.0004 * 0.75 = 0.0003
      return {
        maker: state.useBNBForFees ? 0.00015 : 0.0002,  // 鎸傚崟璐圭巼 (0.015% 鎴?0.02%)
        taker: state.useBNBForFees ? 0.0003 : 0.0004    // 鍚冨崟璐圭巼 (0.03% 鎴?0.04%)
      }
    }
  },

  actions: {
    // 鍚屾鎸佷粨鍒楄〃
    syncPositions(positions) {
      this.positions = [...positions];
      console.log('[AssetsStore] Assets synced:', this.positions);
    },
    
    /**
     * 鍒濆鍖栨暟鎹?- App 鍚姩鏃跺敮涓€鑾峰彇鏁版嵁鐨勫叆鍙?
     * 浠?API 鑾峰彇璧勪骇鍜岃鍗曟暟鎹?
     */
    async initData() {
      this.isLoading = true
      try {
        if (shouldUseLocalData()) {
          const localBalance = Number(loadFromStorage('userBalance', 10000))
          const localHoldings = loadFromStorage('userHoldings', {
            BTC: 0.05,
            ETH: 1.2,
            BNB: 5,
            SOL: 30,
            BEAT: 120
          })
          const localOrdersRes = await tradeApi.getOrders()
          const localOrdersEnvelope = localOrdersRes?.data || localOrdersRes

          this.usdtBalance = Number.isFinite(localBalance) ? localBalance : 10000
          this.holdings = localHoldings && typeof localHoldings === 'object' ? { ...localHoldings } : {}
          this.beatBalance = this.holdings.BEAT || this.beatBalance || 0
          this.userAssets = {
            USDT: this.usdtBalance,
            ...this.holdings
          }
          this.equity = this.usdtBalance
          this.futuresUnrealizedPnl = 0
          this.orders = Array.isArray(localOrdersEnvelope?.data) ? localOrdersEnvelope.data : []

          const txHistory = loadFromStorage('txHistory', [])
          this.transactionHistory = Array.isArray(txHistory) ? txHistory : []
          return
        }

        // 骞惰鑾峰彇璧勪骇鍜岃鍗曟暟鎹?
        // 鑾峰彇瀹屾暣璧勪骇鏁版嵁锛堝寘鎷喕缁撲綑棰濆拰璐︽埛鏉冪泭锛?
        const [assetsResponse, ordersRes] = await Promise.all([
          request.get('/api/v1/assets/'), // 浣跨敤 /api/v1/assets/ 鑾峰彇鍖呭惈 equity 鐨勬暟鎹?
          tradeApi.getOrders()
        ])

        // 妫€鏌ュ搷搴旀牸寮?
        // /api/v1/assets/ 杩斿洖鐨勬牸寮忥細{ code: 200, data: { balance: 50000, equity: 51234.56, holdings: {...}, frozen: {...}, futures_unrealized_pnl: 1234.56 } }
        console.log('鍓嶇鎺ユ敹鍒扮殑瀹屾暣璧勪骇鏁版嵁:', assetsResponse)
        
        // 澶勭悊鍝嶅簲鏁版嵁
        let assetsData = null
        
        // 妫€鏌ュ搷搴旀牸寮忥細axios 杩斿洖 { data: { code: 200, data: {...} } }
        if (assetsResponse && assetsResponse.data) {
          const response = assetsResponse.data
          
          // 妫€鏌ュ悗绔繑鍥炵殑 code
          if (response.code === 200 && response.data) {
            assetsData = response.data
          } else {
            console.warn('鈿狅笍 鍚庣杩斿洖閿欒:', response.message || '鏈煡閿欒')
          }
        } else {
          console.warn('鈿狅笍 璧勪骇鏁版嵁鏍煎紡寮傚父:', assetsResponse)
        }
        
        // 濡傛灉鎴愬姛鑾峰彇鍒版暟鎹紝鏇存柊鐘舵€?
        if (assetsData) {
          // 鎻愬彇璐︽埛鏉冪泭鍜屽悎绾︾泩浜?
          this.equity = assetsData.equity || 0
          this.futuresUnrealizedPnl = assetsData.futures_unrealized_pnl || 0
          
          // 鍏煎鏃ф牸寮忥細濡傛灉杩斿洖鐨勬槸鏃ф牸寮忥紙鐩存帴鏄祫浜у瓧鍏革級锛屽垯浠?holdings 涓彁鍙?
          let assets = {}
          if (assetsData.holdings) {
            // 鏂版牸寮忥細浠?holdings 鍜?frozen 涓彁鍙?
            assets = { ...assetsData.holdings }
            // 娣诲姞鍐荤粨浣欓瀛楁
            Object.keys(assetsData.frozen || {}).forEach(coin => {
              assets[`${coin}_frozen`] = assetsData.frozen[coin]
            })
          } else {
            // 鏃ф牸寮忥細鐩存帴浣跨敤 data
            assets = assetsData
          }
          
          // 瀛樺偍瀹屾暣鐨勮祫浜ф暟鎹紙鍖呮嫭鍐荤粨浣欓锛?
          this.userAssets = { ...assets }
          
          // 鎻愬彇 USDT 鍙敤浣欓
          const balance = assets.USDT || 0
          
          // 鍏ㄩ噺鎻愬彇鎵€鏈夊竵绉嶇殑鍙敤浣欓锛堟帓闄?USDT 鍜屽喕缁撳瓧娈碉級
          const holdings = {}
          const supportedCoins = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC']
          
          supportedCoins.forEach(coin => {
            if (assets[coin] !== undefined) {
              holdings[coin] = assets[coin] || 0
            }
          })
          
          // 濡傛灉鍚庣杩斿洖浜嗗叾浠栧竵绉嶏紝涔熶竴骞舵坊鍔狅紙鍔ㄦ€佹敮鎸侊級
          Object.keys(assets).forEach(key => {
            // 鎺掗櫎 USDT銆佸喕缁撳瓧娈碉紙_frozen锛夊拰宸插鐞嗙殑甯佺
            if (key !== 'USDT' && !key.endsWith('_frozen') && !supportedCoins.includes(key)) {
              holdings[key] = assets[key] || 0
            }
          })
          
          console.log('瑙ｆ瀽鍚庣殑璧勪骇鏁版嵁:', { 
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
          
          // 鍏抽敭锛氱‘淇濆皢 API 杩斿洖鐨?balance 姝ｇ‘璧嬪€肩粰 state
          this.usdtBalance = balance
          this.holdings = holdings
          
          // 濡傛灉 holdings 涓湁 BEAT锛屼篃鏇存柊 beatBalance锛堝吋瀹规棫浠ｇ爜锛?
          if (holdings.BEAT !== undefined) {
            this.beatBalance = holdings.BEAT
          }
          
          // 璋冭瘯纭锛氬湪璧嬪€艰鍙ヤ箣鍚庯紝绔嬪嵆鎵撳嵃纭繚鏁版嵁鐪熺殑瀛樿繘鍘讳簡
          console.log('鉁?State鏇存柊鍚庝綑棰?', this.usdtBalance)
          console.log('鉁?State鏇存柊鍚庢寔浠?', this.holdings)
          console.log('鉁?State鏇存柊鍚庤处鎴锋潈鐩?', this.equity)
          console.log('鉁?State鏇存柊鍚庡悎绾︾泩浜?', this.futuresUnrealizedPnl)
          console.log('鉁?State鏇存柊鍚庡畬鏁磋祫浜ф暟鎹?', this.userAssets)
        } else {
          // 濡傛灉娌℃湁鑾峰彇鍒版暟鎹紝涓嶈閲嶇疆涓?0锛屼繚鐣欑幇鏈夋暟鎹?
          console.warn('Unable to load asset data; keeping current state')
        }

        if (ordersRes.code === 200 && ordersRes.data) {
          this.orders = ordersRes.data || []
        }

        // 鑾峰彇浜ゆ槗鍘嗗彶锛堜粠 localStorage 璇诲彇锛屽洜涓?wallet.js 鐨?deposit/withdraw 浼氬啓鍏ワ級
        // 娉ㄦ剰锛氳繖閲屾殏鏃朵繚鐣欎粠 localStorage 璇诲彇锛屽悗缁彲浠ヨ縼绉诲埌 API
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
        console.error('鉂?Error initializing data:', error)
        console.error('閿欒璇︽儏:', error.response?.data || error.message)
        
        // 鍒濆鍖栧け璐ユ椂锛屼笉瑕侀噸缃负 0锛屼繚鐣欑幇鏈夋暟鎹?
        // 杩欐牱鍙互閬垮厤鍥犱负缃戠粶闂鎴栦复鏃堕敊璇鑷存暟鎹涪澶?
        // 鍙湁鍦ㄧ‘璁ゆ槸璁よ瘉澶辫触锛?01锛夋椂鎵嶆竻闄ゆ暟鎹?
        if (error.response?.status === 401) {
          console.warn('Authentication failed; clearing asset state')
          this.usdtBalance = 0
          this.holdings = {}
          this.orders = []
          this.transactionHistory = []
          this.equity = 0
          this.futuresUnrealizedPnl = 0
        } else {
          console.warn('Asset data load failed; keeping current state')
        }
      } finally {
        this.isLoading = false
      }
    },
    
    /**
     * 妫€鏌ユ槸鍚﹀畨瑁呬簡 Web3 閽卞寘
     * 鍦ㄩ〉闈㈠姞杞芥椂璋冪敤锛岀敤浜庢娴嬮挶鍖呮槸鍚﹀彲鐢?
     */
    checkWalletInstalled() {
      return walletService.checkWalletInstalled()
    },

    /**
     * 杩炴帴 Web3 閽卞寘骞跺畬鎴愯璇?
     * 鍙傝€冨竵瀹?Web3 閽卞寘鐨勮璇佹祦绋?
     * 
     * 娉ㄦ剰锛氭鏂规硶浠呭湪鐢ㄦ埛涓诲姩鐐瑰嚮"杩炴帴閽卞寘"鎸夐挳鏃惰皟鐢?
     * 涓嶈鍦ㄩ〉闈㈠姞杞芥椂鑷姩璋冪敤锛岄伩鍏嶆湭瀹夎閽卞寘鏃堕绻佹姤閿?
     */
    async connectWallet() {
      try {
        const { i18n } = await import('@/main')
        const message = i18n.global.t('auth.signMessage')
        const session = await walletService.createSession(message)

        if (session.token) {
          localStorage.setItem('token', session.token)
        }
        localStorage.setItem('walletAddress', session.address)

        this.isWalletConnected = true
        this.walletAddress = session.address
        saveToStorage('isWalletConnected', true)
        saveToStorage('walletAddress', session.address)

        return {
          success: true,
          address: session.address,
          token: session.token,
          mode: session.mode,
          authenticated: session.authenticated
        }
      } catch (error) {
        if (error.code === 4001) {
          throw new Error('User rejected wallet authorization')
        } else if (error.code === -32002) {
          throw new Error('Wallet request is already pending. Please check your wallet.')
        }
        throw error
      }
    },
    
    /**
     * 鏂紑閽卞寘杩炴帴
     */
    disconnectWallet() {
      walletService.disconnect()
      this.isWalletConnected = false
      this.walletAddress = ''
      localStorage.removeItem('token')
      saveToStorage('isWalletConnected', false)
      saveToStorage('walletAddress', '')
    },

    /**
     * 閲嶇疆娴嬭瘯鏁版嵁
     */
    resetTestData() {
      localStorage.removeItem('userBalance')
      localStorage.removeItem('userHoldings')
      localStorage.removeItem('userOrders')
      localStorage.removeItem('userIDORecords')
      localStorage.removeItem('launchpadStakingPositions')
      localStorage.removeItem('txHistory')
      localStorage.removeItem('beatBalance')
      localStorage.removeItem('isWalletConnected')
      localStorage.removeItem('walletAddress')
      location.reload()
    },

    /**
     * 鍏呭€?USDT
     * @param {number} amount - 鍏呭€奸噾棰?
     * @returns {Promise<boolean>} - 鎴愬姛杩斿洖 true
     */
    /**
     * 鍏呭€兼搷浣?
     * 璋冪敤鍚庣 API 杩涜鍏呭€硷紝鎴愬姛鍚庨噸鏂版媺鍙栦綑棰?
     * 
     * @param {number} amount - 鍏呭€奸噾棰?
     * @param {string} currency - 甯佺锛岄粯璁や负 'USDT'
     * @returns {Promise<boolean>} 鎴愬姛杩斿洖 true
     */
    async deposit(amount, currency = 'USDT') {
      this.isLoading = true
      try {
        // 璋冪敤鍚庣 API 杩涜鍏呭€?
        const res = await walletApi.deposit(amount, currency)
        
        // 妫€鏌ュ搷搴旀牸寮?
        if (res.data && res.data.code === 200 && res.data.data) {
          // 鏇存柊鏈湴鐘舵€侊紙鍙€夛紝涔熷彲浠ョ瓑 initData 鎷夊彇锛?
          const assets = res.data.data
          this.usdtBalance = assets.USDT || this.usdtBalance
          if (assets.BTC !== undefined) this.holdings.BTC = assets.BTC
          if (assets.BEAT !== undefined) this.beatBalance = assets.BEAT
          
          // 閲嶆柊鎷夊彇鏈€鏂版暟鎹紙纭繚鏁版嵁涓€鑷存€э級
          await this.initData()
          return true
        } else {
          throw new Error(res.data?.message || res.message || 'Deposit failed')
        }
      } catch (error) {
        console.error('Deposit error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 鎻愮幇 USDT
     * @param {number} amount - 鎻愮幇閲戦
     * @returns {Promise<boolean>} - 鎴愬姛杩斿洖 true
     */
    /**
     * 鎻愮幇鎿嶄綔
     * 璋冪敤鍚庣 API 杩涜鎻愮幇锛屾垚鍔熷悗閲嶆柊鎷夊彇浣欓
     * 
     * @param {number} amount - 鎻愮幇閲戦
     * @param {string} currency - 甯佺锛岄粯璁や负 'USDT'
     * @returns {Promise<boolean>} 鎴愬姛杩斿洖 true
     */
    async withdraw(amount, currency = 'USDT') {
      this.isLoading = true
      try {
        // 璋冪敤鍚庣 API 杩涜鎻愮幇
        const res = await walletApi.withdraw(amount, currency)
        
        // 妫€鏌ュ搷搴旀牸寮?
        if (res.data && res.data.code === 200 && res.data.data) {
          // 鏇存柊鏈湴鐘舵€侊紙鍙€夛紝涔熷彲浠ョ瓑 initData 鎷夊彇锛?
          const assets = res.data.data
          this.usdtBalance = assets.USDT || this.usdtBalance
          if (assets.BTC !== undefined) this.holdings.BTC = assets.BTC
          if (assets.BEAT !== undefined) this.beatBalance = assets.BEAT
          
          // 閲嶆柊鎷夊彇鏈€鏂版暟鎹紙纭繚鏁版嵁涓€鑷存€э級
          await this.initData()
          return true
        } else {
          throw new Error(res.data?.message || res.message || '鎻愮幇澶辫触')
        }
      } catch (error) {
        console.error('Withdraw error:', error)
        // 濡傛灉鏄綑棰濅笉瓒崇殑閿欒锛屾樉绀烘洿鍙嬪ソ鐨勬彁绀?
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        }
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 鍒涘缓璁㈠崟锛堥檺浠峰崟锛?
     * @param {Object} order - 璁㈠崟瀵硅薄
     * @param {string} order.symbol - 甯佺绗﹀彿
     * @param {string} order.type - 'BUY' 鎴?'SELL'
     * @param {number} order.price - 璁㈠崟浠锋牸
     * @param {number} order.amount - 璁㈠崟鏁伴噺
     * @returns {Promise<boolean>} - 鎴愬姛杩斿洖 true
     */
    async createOrder(order) {
      this.isLoading = true
      try {
        const { symbol, type, price, amount } = order
        
        // 杞崲鏍煎紡锛歵ype 'BUY'/'SELL' -> side 'buy'/'sell'
        const side = type.toLowerCase()
        
        const res = await tradeApi.submitOrder({
          symbol,
          side,
          price,
          amount
        })
        
        const responseData = res?.data || res
        if (responseData?.code === 200) {
          // 閲嶆柊鎷夊彇鏈€鏂版暟鎹?
          await this.initData()
          return true
        } else {
          throw new Error(responseData?.msg || responseData?.message || '涓嬪崟澶辫触')
        }
      } catch (error) {
        console.error('Create order error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 鍙栨秷璁㈠崟
     * @param {number|string} orderId - 璁㈠崟ID
     * @returns {Promise<boolean>} - 鎴愬姛杩斿洖 true
     */
    async cancelOrder(orderId) {
      this.isLoading = true
      try {
        const res = await tradeApi.cancelOrder(orderId)
        
        const responseData = res?.data || res
        if (responseData?.code === 200) {
          // 閲嶆柊鎷夊彇鏈€鏂版暟鎹?
          await this.initData()
          return true
        } else {
          throw new Error(responseData?.msg || responseData?.message || '鎾ゅ崟澶辫触')
        }
      } catch (error) {
        console.error('Cancel order error:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 娣诲姞浜ゆ槗鍘嗗彶璁板綍锛堜繚鐣欑敤浜?IDO 绛夊満鏅級
     * @param {Object} record - 浜ゆ槗璁板綍瀵硅薄
     */
    addTransaction(record) {
      if (!Array.isArray(this.transactionHistory)) {
        this.transactionHistory = []
      }
      const now = new Date()
      const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
      const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
      
      const transaction = {
        id: Date.now() + Math.random(),
        time: `${dateStr} ${timeStr}`,
        type: record.type,
        amount: record.amount,
        status: record.status || '鎴愬姛',
        tx_id: record.tx_id || null,
        chain_name: record.chain_name || null,
        project_name: record.project_name || null,
        price: record.price || null,
        total_cost: record.total_cost || record.amount || null,
        token_amount: record.token_amount || null
      }
      
      this.transactionHistory.unshift(transaction)
      
      // 淇濆瓨鍒?localStorage锛堝洜涓?wallet.js 鐨?API 浼氬啓鍏ワ紝杩欓噷鍚屾鏇存柊锛?
      try {
        const txHistory = JSON.parse(localStorage.getItem('txHistory') || '[]')
        txHistory.unshift(transaction)
        localStorage.setItem('txHistory', JSON.stringify(txHistory))
      } catch (error) {
        console.error('Error saving transaction history:', error)
      }
    },

    /**
     * 鍙備笌 IDO 璁よ喘锛堟殏鏃朵繚鐣欙紝鍚庣画鍙縼绉诲埌 API锛?
     * @param {Object} project - 椤圭洰瀵硅薄
     * @returns {boolean} - 鎴愬姛杩斿洖 true
     */
    joinIDO(project) {
      if (!Array.isArray(this.idoRecords)) {
        this.idoRecords = []
      }
      // 妫€鏌ユ槸鍚﹀凡缁忚璐繃璇ラ」鐩?
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
        type: '璁よ喘',
        amount: -allocationAmount,
        status: '鎴愬姛',
        project_name: project.name || 'Unknown Project',
        price: project.price || 0.1,
        total_cost: allocationAmount,
        token_amount: beatAmount
      })
      
      return true
    },

    subscribeLaunchpad(project, amount, mode = 'fixed') {
      if (!Array.isArray(this.idoRecords)) {
        this.idoRecords = []
      }
      const subscribeAmount = Number(amount) || 0
      if (subscribeAmount <= 0) return false
      if (this.usdtBalance < subscribeAmount) return false
      const directLimit = Number(project?.directRemainingAllocation)
      const remainingLimit = Number.isFinite(directLimit) ? directLimit : this.launchpadRemainingAllocation
      if (subscribeAmount > remainingLimit) return false

      this.usdtBalance -= subscribeAmount

      const subscriptionPrice = Number(project?.subscriptionPrice || project?.price) || 0
      const tokenAmount = subscriptionPrice ? subscribeAmount / subscriptionPrice : subscribeAmount * 10
      const raisedAmount = Number(project?.raisedAmount) || 0
      const totalRaise = Number(project?.totalRaise || project?.targetRaise) || 0
      const projectedRaisedAmount = Math.max(raisedAmount, subscribeAmount)
      const isOversubscribed = totalRaise > 0 && projectedRaisedAmount > totalRaise
      const finalUsdt = isOversubscribed ? totalRaise * (subscribeAmount / projectedRaisedAmount) : subscribeAmount
      const finalTokenAmount = subscriptionPrice ? finalUsdt / subscriptionPrice : tokenAmount
      const refundAmount = Math.max(0, subscribeAmount - finalUsdt)
      const record = {
        id: Date.now() + Math.random(),
        name: project?.name || 'Launchpad Project',
        ticker: project?.ticker || '',
        price: subscriptionPrice,
        amount: subscribeAmount,
        mode: mode === 'boosted' ? 'stake' : mode,
        pending: subscribeAmount,
        tokenAmount,
        estimatedTokenAmount: tokenAmount,
        finalTokenAmount,
        refundAmount,
        wonTokenAmount: 0,
        winRatio: 0,
        settled: false,
        settlementTime: project?.settlementTime || null,
        listingTime: project?.listingTime || null,
        status: 'pending_draw',
        timestamp: new Date().toISOString()
      }

      this.idoRecords.push(record)
      saveToStorage('userIDORecords', this.idoRecords)
      this.addTransaction({
        type: '认购',
        amount: -subscribeAmount,
        status: '成功',
        project_name: record.name,
        price: record.price,
        total_cost: subscribeAmount,
        token_amount: tokenAmount
      })

      return true
    },

    addLaunchpadStake(project, asset, amount, metrics = {}) {
      const stakeAmount = Number(amount) || 0
      if (stakeAmount <= 0) return false
      if (!Array.isArray(this.launchpadStakingPositions)) {
        this.launchpadStakingPositions = []
      }

      const price = this.priceMap[asset] || 1
      const amountUsdt = Number(metrics.amountUsdt) || stakeAmount * price
      if (asset === 'USDT') {
        if (this.usdtBalance < stakeAmount) return false
        this.usdtBalance -= stakeAmount
      } else {
        const current = this.holdings[asset] || 0
        if (current < stakeAmount) return false
        this.holdings[asset] = current - stakeAmount
      }

      const existing = this.launchpadStakingPositions.find(position => (
        position.projectTicker === (project?.ticker || '') && position.asset === asset
      ))

      if (existing) {
        existing.amount += stakeAmount
        existing.amountUsdt += amountUsdt
        existing.claimableReward += Number(metrics.estimatedReward) || 0
        existing.finalRewardToken = (Number(existing.finalRewardToken) || 0) + (Number(metrics.finalRewardToken) || 0)
        existing.poolRewardAllocation = Number(metrics.poolRewardAllocation) || existing.poolRewardAllocation
        existing.totalPoolStakeAmount = Number(metrics.totalPoolStakeAmount) || existing.totalPoolStakeAmount
        existing.status = 'active'
        existing.updatedAt = new Date().toISOString()
      } else {
        this.launchpadStakingPositions.push({
          id: Date.now() + Math.random(),
          projectName: project?.name || 'Launchpad Project',
          projectTicker: project?.ticker || '',
          rewardTicker: metrics.rewardTicker || project?.ticker || 'GMT',
          asset,
          amount: stakeAmount,
          amountUsdt,
          stakingStartTime: project?.stakingStartTime || null,
          stakingEndTime: project?.stakingEndTime || null,
          listingTime: project?.listingTime || null,
          userStakeStartTime: new Date().toISOString(),
          userStakeEndTime: null,
          claimableReward: Number(metrics.estimatedReward) || 0,
          finalRewardToken: Number(metrics.finalRewardToken) || 0,
          dailyRate: Number(metrics.dailyRate) || 0.006,
          rewardPrice: Number(metrics.rewardPrice || project?.price) || 1,
          dailyRewardToken: amountUsdt * (Number(metrics.dailyRate) || 0.006) / (Number(metrics.rewardPrice || project?.price) || 1),
          rewardTime: '00:00',
          lastRewardAt: new Date().toISOString(),
          poolRewardAllocation: Number(metrics.poolRewardAllocation) || 0,
          totalPoolStakeAmount: Number(metrics.totalPoolStakeAmount) || 1,
          apy: Number(metrics.apy) || 0,
          status: 'active',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
      }

      saveToStorage('launchpadStakingPositions', this.launchpadStakingPositions)
      this.addTransaction({
        type: 'Launchpad Stake',
        amount: -amountUsdt,
        status: '成功',
        project_name: project?.name || 'Launchpad Project',
        total_cost: amountUsdt
      })
      return true
    },

    creditIEOAsset(symbol, amount, meta = {}) {
      const ticker = String(symbol || '').toUpperCase()
      const quantity = Number(amount) || 0
      if (!ticker || quantity <= 0) return false
      if (!this.ieoAssets || typeof this.ieoAssets !== 'object') {
        this.ieoAssets = {}
      }
      const current = this.ieoAssets[ticker] || { symbol: ticker, amount: 0, name: meta.name || ticker, source: 'IEO' }
      this.ieoAssets[ticker] = {
        ...current,
        symbol: ticker,
        name: meta.name || current.name || ticker,
        amount: (Number(current.amount) || 0) + quantity,
        updatedAt: new Date().toISOString(),
        status: meta.status || 'won'
      }
      saveToStorage('ieoAssets', this.ieoAssets)
      return true
    },

    syncLaunchpadSettlements(nowValue = Date.now()) {
      if (!Array.isArray(this.idoRecords)) return
      let changed = false
      this.idoRecords = this.idoRecords.map(record => {
        if (record.settled) return record
        const settlementTime = record.settlementTime ? new Date(record.settlementTime).getTime() : nowValue
        if (Number.isFinite(settlementTime) && nowValue < settlementTime) {
          return { ...record, status: record.status || 'pending_draw' }
        }
        const finalTokenAmount = Number(record.finalTokenAmount ?? record.tokenAmount) || 0
        const estimatedTokenAmount = Number(record.estimatedTokenAmount ?? record.tokenAmount) || 0
        const refundAmount = Math.max(0, Number(record.refundAmount) || 0)
        if (refundAmount > 0) {
          this.usdtBalance += refundAmount
        }
        if (finalTokenAmount > 0) {
          this.creditIEOAsset(record.ticker, finalTokenAmount, { name: record.name, status: 'won' })
        }
        changed = true
        return {
          ...record,
          status: finalTokenAmount > 0 ? 'won' : 'not_won',
          wonTokenAmount: finalTokenAmount,
          winRatio: estimatedTokenAmount > 0 ? finalTokenAmount / estimatedTokenAmount : 0,
          settled: true,
          settledAt: new Date(nowValue).toISOString()
        }
      })
      if (changed) {
        saveToStorage('userIDORecords', this.idoRecords)
      }
    },

    syncLaunchpadDailyRewards(nowValue = Date.now()) {
      if (!Array.isArray(this.launchpadStakingPositions)) return
      let changed = false
      const dayMs = 24 * 60 * 60 * 1000
      this.launchpadStakingPositions = this.launchpadStakingPositions.map(position => {
        if (position.status !== 'active') return position
        const lastRewardAt = new Date(position.lastRewardAt || position.createdAt || nowValue).getTime()
        const elapsedDays = Math.floor((nowValue - lastRewardAt) / dayMs)
        if (elapsedDays <= 0) return position
        const amountUsdt = Number(position.amountUsdt) || 0
        const dailyRate = Number(position.dailyRate) || 0.006
        const rewardPrice = Number(position.rewardPrice) || 1
        const rewardToken = amountUsdt * dailyRate * elapsedDays / rewardPrice
        if (rewardToken > 0) {
          this.creditIEOAsset(position.rewardTicker, rewardToken, { name: position.projectName, status: 'staking_reward' })
          changed = true
        }
        return {
          ...position,
          claimableReward: (Number(position.claimableReward) || 0) + rewardToken,
          finalRewardToken: (Number(position.finalRewardToken) || 0) + rewardToken,
          dailyRewardToken: amountUsdt * dailyRate / rewardPrice,
          lastRewardAt: new Date(lastRewardAt + elapsedDays * dayMs).toISOString(),
          updatedAt: new Date(nowValue).toISOString()
        }
      })
      if (changed) {
        saveToStorage('launchpadStakingPositions', this.launchpadStakingPositions)
      }
    },

    claimLaunchpadRewards(positionId = null, rewardAmount = null) {
      if (!Array.isArray(this.launchpadStakingPositions)) {
        this.launchpadStakingPositions = []
      }
      const targetPositions = positionId
        ? this.launchpadStakingPositions.filter(position => position.id === positionId)
        : this.launchpadStakingPositions
      const totalReward = Number(rewardAmount) || targetPositions.reduce((sum, position) => {
        return sum + (Number(position.finalRewardToken || position.claimableReward) || 0)
      }, 0)
      if (totalReward <= 0) return false

      const rewardTicker = targetPositions[0]?.rewardTicker || 'BEAT'
      this.holdings[rewardTicker] = (this.holdings[rewardTicker] || 0) + totalReward
      this.launchpadStakingPositions = this.launchpadStakingPositions.map(position => ({
        ...position,
        claimableReward: !positionId || position.id === positionId ? 0 : position.claimableReward,
        finalRewardToken: !positionId || position.id === positionId ? 0 : position.finalRewardToken,
        status: !positionId || position.id === positionId ? 'claimed' : position.status,
        updatedAt: new Date().toISOString()
      }))
      saveToStorage('launchpadStakingPositions', this.launchpadStakingPositions)
      this.addTransaction({
        type: 'Claim Rewards',
        amount: totalReward,
        status: '成功',
        project_name: 'Launchpad Staking',
        token_amount: totalReward
      })
      return true
    },

    earlyUnstakeLaunchpad(positionId) {
      if (!Array.isArray(this.launchpadStakingPositions)) {
        this.launchpadStakingPositions = []
      }
      const position = this.launchpadStakingPositions.find(item => item.id === positionId)
      if (!position) return false

      if (position.asset === 'USDT') {
        this.usdtBalance += position.amount
      } else {
        this.holdings[position.asset] = (this.holdings[position.asset] || 0) + position.amount
      }

      position.status = 'unlocked'
      position.userStakeEndTime = new Date().toISOString()
      this.launchpadStakingPositions = this.launchpadStakingPositions.filter(item => item.id !== positionId)
      saveToStorage('launchpadStakingPositions', this.launchpadStakingPositions)
      this.addTransaction({
        type: 'Unlock Principal',
        amount: position.amountUsdt,
        status: '成功',
        project_name: position.projectName,
        total_cost: position.amountUsdt
      })
      return true
    },

    /**
     * 浜ゆ槗鎿嶄綔锛堢珛鍗虫垚浜わ紝鐢ㄤ簬甯備环鍗曟垨娴嬭瘯锛?
     * @param {string} type - 'BUY' 鎴?'SELL'
     * @param {string} symbol - 甯佺绗﹀彿
     * @param {number} amount - 浜ゆ槗鏁伴噺
     * @param {number} price - 浜ゆ槗浠锋牸
     * @returns {boolean} - 鎴愬姛杩斿洖 true
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
     * 鍒囨崲 BNB 鏀粯浜ゆ槗鎵嬬画璐瑰紑鍏?
     * @param {boolean} value - 寮€鍏崇姸鎬?
     */
    toggleBNBForFees(value) {
      this.useBNBForFees = value
      // 鍚屾鍐欏叆 localStorage
      try {
        localStorage.setItem('useBNBForFees', value.toString())
      } catch (error) {
        console.error('Error saving useBNBForFees to localStorage:', error)
      }
    },

    /**
     * 鍒囨崲 BNB 鏀粯鏉犳潌鍒╂伅寮€鍏?
     * @param {boolean} value - 寮€鍏崇姸鎬?
     */
    toggleBNBForInterest(value) {
      this.useBNBForInterest = value
      // 鍚屾鍐欏叆 localStorage
      try {
        localStorage.setItem('useBNBForInterest', value.toString())
      } catch (error) {
        console.error('Error saving useBNBForInterest to localStorage:', error)
      }
    },

    /**
     * 璁剧疆姝㈢泩姝㈡崯 (TP/SL)
     * @param {Object} params - { positionId, tp, sl }
     * @returns {Promise<boolean>} - 鎴愬姛杩斿洖 true
     */
    async setTPSL(params) {
      try {
        // 璋冪敤鍚庣 API 璁剧疆 TP/SL
        const res = await request.post('/api/v1/futures/positions/tpsl', params)
        
        // 妫€鏌ュ搷搴旀牸寮?
        if (res.success || res.code === 200) {
          // 鎵嬪姩鏇存柊鏈湴 positions 鏁扮粍涓殑瀵瑰簲瀛楁
          const target = this.positions.find(p => p.id === params.positionId)
          if (target) {
            // 鍚屾鏇存柊鎵€鏈夊彲鑳界殑瀛楁鍚嶏紙鍏煎涓嶅悓鏍煎紡锛?
            target.tp = params.tp
            target.take_profit = params.tp
            target.takeProfit = params.tp
            target.sl = params.sl
            target.stop_loss = params.sl
            target.stopLoss = params.sl
            
            console.log('[TP/SL] Updated position:', target)
          }
          
          return true
        } else {
          throw new Error(res.message || res.msg || '璁剧疆澶辫触')
        }
      } catch (error) {
        console.error('[TP/SL] Set error:', error)
        
        // 鍗充娇 API 澶辫触锛屼篃灏濊瘯鏇存柊鏈湴鏁版嵁锛堜娇鐢?localStorage 浣滀负 fallback锛?
        const target = this.positions.find(p => p.id === params.positionId)
        if (target) {
          target.tp = params.tp
          target.take_profit = params.tp
          target.takeProfit = params.tp
          target.sl = params.sl
          target.stop_loss = params.sl
          target.stopLoss = params.sl
          
          console.log('[TP/SL] Updated position locally (API failed):', target)
        }
        
        throw error
      }
    }
  }
})


