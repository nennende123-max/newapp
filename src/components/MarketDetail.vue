<template>
  <div class="market-detail-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      :title="symbol + '/USDT'"
      fixed
      placeholder
      :border="false"
      class="force-custom-nav-bar"
    >
      <template #left>
        <div class="force-custom-back" @click="$router.back()">
          <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" class="back-svg-icon">
            <path d="M669.6 849.6c8.8 8 22.4 7.2 30.4-1.6s7.2-22.4-1.6-30.4l-304-277.6 304-277.6c8.8-8 9.6-21.6 1.6-30.4s-21.6-9.6-30.4-1.6l-320 292.8c-4.4 4-6.4 9.6-6.4 15.2s2 11.2 6.4 15.2l320 292.8z" fill="#FCD535"></path>
          </svg>
        </div>
      </template>

      <template #title>
        <div class="header-title" @click="showCoinDrawer = true">
          <span>{{ symbol }}/USDT</span>
          <van-icon name="arrow-down" size="12" class="coin-select-arrow" />
        </div>
      </template>
    </van-nav-bar>

    <!-- 币种切换抽屉 -->
    <van-popup
      v-model:show="showCoinDrawer"
      position="left"
      :style="{ width: '70%', height: '100%' }"
      class="coin-drawer-popup"
    >
      <div class="coin-drawer">
        <!-- 抽屉头部 -->
        <div class="drawer-header">
          <span class="drawer-title">{{ t('market.switch_symbol') }}</span>
          <van-icon name="cross" class="drawer-close" @click="showCoinDrawer = false" />
        </div>

        <!-- 币种列表 -->
        <div class="coin-list">
          <div
            v-for="coin in coinList"
            :key="coin.symbol"
            class="coin-item"
            :class="{ active: coin.symbol === symbol }"
            @click="handleSwitchCoin(coin.symbol)"
          >
            <div class="coin-left">
              <div class="coin-symbol">{{ coin.symbol }}</div>
              <div class="coin-pair">{{ coin.symbol }}/USDT</div>
            </div>
            <div class="coin-right">
              <div class="coin-price" :class="{ up: coin.change >= 0, down: coin.change < 0 }">
                {{ formatCoinPrice(coin.price) }}
              </div>
              <div class="coin-change" :class="{ up: coin.change >= 0, down: coin.change < 0 }">
                {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
              </div>
            </div>
            <van-icon v-if="coin.symbol === symbol" name="success" class="coin-check" />
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 当前价格区 - 币安风格 -->
    <div class="price-section">
      <div class="price-header">
        <!-- 左侧：大价格 + 涨跌幅Badge -->
        <div class="price-left">
          <div class="current-price-large" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
            {{ formatPrice(currentPrice) }}
          </div>
          <div class="price-change-badge" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
            <template v-if="isDataLoaded">
              {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
            </template>
            <template v-else>---</template>
          </div>
        </div>
        
        <!-- 右侧：2x2 网格布局 -->
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_high') }}</div>
            <div class="stat-value">{{ formatPrice(stats.high24h) }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_low') }}</div>
            <div class="stat-value">{{ formatPrice(stats.low24h) }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_vol') }}</div>
            <div class="stat-value">{{ formatVolume(stats.volume24h) }} {{ symbol }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_amt') }}</div>
            <div class="stat-value">{{ formatAmount(stats.amount24h) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- K线图控制栏 - 币安风格 -->
    <div class="chart-toolbar">
      <div class="timeframe-tabs">
        <div 
          v-for="tf in timeframes" 
          :key="tf.value"
          class="timeframe-btn"
          :class="{ active: selectedTimeframe === tf.value }"
          @click="selectedTimeframe = tf.value"
        >
          {{ tf.label }}
        </div>
      </div>
      <div class="toolbar-actions">
        <van-icon name="setting-o" class="toolbar-icon" @click="handleSettings" />
        <van-icon name="bars" class="toolbar-icon" @click="handleIndicators" />
      </div>
    </div>

    <!-- K 线图区域 -->
    <div class="chart-box">
      <trading-view-widget 
        ref="tvWidget"
        :symbol="symbol"
        :initial-data="klineHistory" 
        theme="dark"
      />
    </div>

    <!-- 盘口和成交标签页 -->
    <van-tabs 
      v-model:active="activeTab" 
      background="transparent" 
      title-active-color="#FCD535" 
      title-inactive-color="#8E8E93" 
      line-width="40px" 
      line-height="2px" 
      color="#FCD535" 
      :border="false"
      class="market-tabs"
    >
      <van-tab :title="t('market.orderbook')">
        <div class="orderbook-container">
          <!-- 卖单区域 -->
          <div class="orderbook-section asks-section">
            <div 
              v-for="(ask, index) in (orderBook.asks || [])" 
              :key="'ask-' + (ask.priceStr || ask.price || index)"
              class="orderbook-row ask-row"
              @click="handlePriceClick(ask.price || ask.priceStr || 0, 'sell')"
            >
              <div class="depth-bar ask-depth" :style="{ '--percent': getDepthWidth(ask.amount || 0) + '%' }"></div>
              <div class="row-content">
                <span class="price ask-price">{{ formatOrderPrice(ask.price || parseFloat(ask.priceStr) || 0) }}</span>
                <span class="amount">{{ formatOrderAmount(ask.amount || parseFloat(ask.amountStr) || 0) }}</span>
              </div>
            </div>
          </div>

          <!-- 当前价格 - 币安风格 -->
          <div class="current-price-row">
            <div class="price-main-info">
              <span class="current-price-text" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
                {{ formatPrice(currentPrice) }}
              </span>
              <span class="price-fiat">≈ {{ formatFiatPrice(currentPrice) }}</span>
              <!-- 调试：显示最后更新时间戳（闪烁效果） -->
              <small 
                :style="{ 
                  display: 'block', 
                  fontSize: '10px', 
                  color: '#8E8E93', 
                  marginTop: '2px',
                  animation: 'blink 1s infinite'
                }">
                更新: {{ lastUpdateTime }}
              </small>
            </div>
          </div>

          <!-- 买单区域 -->
          <div class="orderbook-section bids-section">
            <div 
              v-for="(bid, index) in (orderBook.bids || [])" 
              :key="'bid-' + (bid.priceStr || bid.price || index)"
              class="orderbook-row bid-row"
              @click="handlePriceClick(bid.price || bid.priceStr || 0, 'buy')"
            >
              <div class="depth-bar bid-depth" :style="{ '--percent': getDepthWidth(bid.amount || 0) + '%' }"></div>
              <div class="row-content">
                <span class="price bid-price">{{ formatOrderPrice(bid.price || parseFloat(bid.priceStr) || 0) }}</span>
                <span class="amount">{{ formatOrderAmount(bid.amount || parseFloat(bid.amountStr) || 0) }}</span>
              </div>
            </div>
          </div>
        </div>
      </van-tab>

      <van-tab :title="t('market.recent_trades')">
        <div class="trades-container">
          <div class="trades-header">
            <span class="header-col price-col">{{ t('market.price') }}</span>
            <span class="header-col amount-col">{{ t('market.amount') }}</span>
            <span class="header-col time-col">{{ t('market.time') }}</span>
          </div>
          <div class="trades-list">
            <div 
              v-for="(trade, index) in (trades || [])" 
              :key="'trade-' + index"
              class="trade-row"
            >
              <span class="trade-price" :class="{ buy: trade?.side === 'buy', sell: trade?.side === 'sell' }">
                {{ formatPrice(trade?.price || 0) }}
              </span>
              <span class="trade-amount">{{ formatOrderAmount(trade?.amount || 0) }}</span>
              <span class="trade-time">{{ formatTradeTime(trade?.time || new Date()) }}</span>
            </div>
          </div>
        </div>
      </van-tab>
    </van-tabs>

    <!-- 底部操作栏 - 币安风格 -->
    <div class="bottom-action-bar">
      <van-button 
        class="action-btn buy-btn"
        @click="goToTrade('buy')"
      >
        {{ t('market.buy') }}
      </van-button>
      <van-button 
        class="action-btn sell-btn"
        @click="goToTrade('sell')"
      >
        {{ t('market.sell') }}
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import TradingViewWidget from './TradingViewWidget.vue';
import { useMarketStore } from '@/stores/market';
import { storeToRefs } from 'pinia';
import request from '@/utils/request';

// 定义组件名称
defineOptions({
  name: 'MarketDetail'
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const marketStore = useMarketStore();

// --- 状态定义 ---
const tvWidget = ref(null);
const klineHistory = ref([]); // K 线历史数据
const showCoinDrawer = ref(false); // 币种切换抽屉
const activeTab = ref(0); // 标签页状态
const orderBook = ref({ bids: [], asks: [] }); // 盘口数据
const maxVolume = ref(1000);
const lastUpdateTime = ref(new Date().toLocaleTimeString());
const selectedTimeframe = ref('1h'); // 默认时间周期
const marketType = ref(route.query.type === 'spot' ? 'spot' : 'futures');

// Binance WebSocket 变量
let binanceWS = null;
let useDirectBinance = false;
let orderBookInterval = null;

// 从 Store 提取响应式数据 (合并提取，更简洁)
// 注意：确保 store 里确实有 currentKline 字段，如果没有，请去 store 里加上，或者暂时注释掉 currentKline
const { depths, currentKline } = storeToRefs(marketStore);

// --- 计算属性 ---

// Symbol 规范化
const normalizeSymbol = (sym) => {
  if (!sym) return 'BTC';
  let normalized = sym
    .replace(/^BINANCE:/i, '')
    .replace(/USDT/i, '')
    .replace(/\//g, '')
    .toUpperCase();
  return (!normalized || normalized.length === 0) ? 'BTC' : normalized;
};

// 获取默认 Symbol
const getDefaultSymbol = () => {
  if (route.query.symbol) return normalizeSymbol(route.query.symbol);
  const savedSymbol = localStorage.getItem('selectedSymbol');
  return savedSymbol ? normalizeSymbol(savedSymbol) : 'BTC';
};

const symbol = ref(getDefaultSymbol());

// 转换为后端/API需要的格式 (如 BINANCE:BTCUSDT)
const tradingViewFormat = computed(() => `BINANCE:${symbol.value}USDT`);

// 币种列表
const coinList = computed(() => {
  const symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC'];
  return symbols.map(sym => {
    const ticker = marketStore.getTicker(sym);
    return ticker ? 
      { symbol: sym, price: ticker.price, change: ticker.change } : 
      { symbol: sym, price: getMockPrice(sym), change: (Math.random() - 0.5) * 10 };
  });
});

// 从 Store 获取当前币种的 Ticker
const tickerData = computed(() => marketStore.getTicker(symbol.value));
const currentPrice = computed(() => tickerData.value?.price || 0);
const priceChange = computed(() => tickerData.value?.change || 0);
const isDataLoaded = computed(() => marketStore.hasData(symbol.value));

// 24小时统计
const stats = computed(() => {
  const ticker = tickerData.value;
  if (!ticker) return { high24h: 0, low24h: 0, volume24h: 0, amount24h: 0 };
  return {
    high24h: ticker.high || 0,
    low24h: ticker.low || 0,
    volume24h: ticker.volume || 0,
    amount24h: ticker.quoteVolume || 0
  };
});

// 计算深度条最大值
const maxOrderVolume = computed(() => {
  const safeAsks = Array.isArray(orderBook.value.asks) ? orderBook.value.asks : [];
  const safeBids = Array.isArray(orderBook.value.bids) ? orderBook.value.bids : [];
  
  const allAmounts = [...safeAsks, ...safeBids].map(item => {
    // 兼容数组格式 [price, amount] 和对象格式 {amount: ...}
    return typeof item === 'object' && item !== null 
      ? (item.amount || parseFloat(item[1]) || 0)
      : (parseFloat(item[1]) || 0);
  });
  
  return allAmounts.length > 0 ? Math.max(...allAmounts, 1) : 1000;
});

const trades = computed(() => generateTrades(currentPrice.value));

const timeframes = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' }
];

// --- 工具函数 ---

const getMockPrice = (sym) => {
  const mockPrices = { 'BTC': 92000, 'ETH': 3100, 'BNB': 710, 'SOL': 142, 'BEAT': 0.05 };
  return mockPrices[sym] || 100;
};

// 辅助：获取当前时间周期的起始时间戳（用于对齐 K 线）
// 修复了“每秒画一根线”的 Bug
const getCandleStartTime = (interval) => {
  const nowSeconds = Math.floor(Date.now() / 1000);
  let seconds = 60; // 默认 1m
  if (interval === '5m') seconds = 5 * 60;
  else if (interval === '15m') seconds = 15 * 60;
  else if (interval === '1h') seconds = 60 * 60;
  else if (interval === '4h') seconds = 4 * 60 * 60;
  else if (interval === '1d') seconds = 24 * 60 * 60;
  
  // 取余数向下取整，对齐时间网格
  return nowSeconds - (nowSeconds % seconds);
};

const formatPrice = (val) => val ? Number(val).toLocaleString('en-US', { maximumFractionDigits: val >= 1 ? 2 : 6 }) : '---';
const formatCoinPrice = (val) => formatPrice(val);
const formatVolume = (val) => val > 1000 ? (val/1000).toFixed(2)+'K' : val?.toFixed(2);
const formatAmount = (val) => val > 1000 ? (val/1000).toFixed(0)+'K' : val?.toFixed(0);
const formatFiatPrice = (val) => val ? '¥' + (val * 7.2).toFixed(0) : '¥---';
const formatOrderPrice = (val) => Number(val).toFixed(2);
const formatOrderAmount = (val) => Number(val).toFixed(4);
const formatTradeTime = (date) => date.toTimeString().slice(0, 8);
const getDepthWidth = (amount) => (amount / maxOrderVolume.value) * 100;

const formatOrderBookData = (list) => {
  if (!Array.isArray(list)) return [];
  return list.map(item => {
    const p = Array.isArray(item) ? item[0] : (item.price || item[0]);
    const a = Array.isArray(item) ? item[1] : (item.amount || item.quantity || item[1]);
    return {
      price: parseFloat(p),
      amount: parseFloat(a),
      priceStr: String(p),
      amountStr: String(a)
    };
  });
};

// --- 核心业务逻辑函数 (提前定义，防止 watcher 调用时未定义) ---

// 1. 获取 K 线历史
const fetchKlineHistory = async () => {
  try {
    const res = await request.get('/api/v1/market/kline', {
      params: {
        symbol: tradingViewFormat.value, 
        interval: selectedTimeframe.value, 
        limit: 1000
      }
    });

    if (res.data && Array.isArray(res.data)) {
      const formattedData = res.data.map(item => ({
        time: item[0] / 1000, 
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
      }));
      klineHistory.value = formattedData;
      console.log('[Market] K-line history loaded:', formattedData.length);
    }
  } catch (error) {
    console.error('[Market] Failed to fetch kline:', error);
  }
};

// 2. 获取订单簿 (修复了 Symbol 写死的问题)
const fetchOrderBook = () => {
  if (useDirectBinance && binanceWS?.readyState === WebSocket.OPEN) return;

  request.get('/api/v1/market/orderbook', {
    params: {
      symbol: `${symbol.value}USDT`, // 【修正】这里必须是动态的！
      limit: 20
    }
  }).then(res => {
    const newData = res.data || { bids: [], asks: [] };
    let newBids = formatOrderBookData(newData.bids);
    let newAsks = formatOrderBookData(newData.asks);
    
    // 排序 & 截取
    newBids.sort((a, b) => b.price - a.price);
    newAsks.sort((a, b) => a.price - b.price);
    
    orderBook.value.bids = newBids.slice(0, 20);
    orderBook.value.asks = newAsks.slice(0, 20);
    lastUpdateTime.value = new Date().toLocaleTimeString();
    
    useDirectBinance = false;
  }).catch(err => {
    console.error('Orderbook fetch error:', err);
    if (!useDirectBinance) connectBinanceWebSocket();
  });
};

// 兼容旧名
const loadOrderBook = fetchOrderBook;

// 3. 币安 WS 连接
const connectBinanceWebSocket = () => {
  if (binanceWS) binanceWS.close();
  
  const cleanSymbol = symbol.value.toLowerCase() + 'usdt';
  const wsUrl = `wss://stream.binance.com:9443/ws/${cleanSymbol}@depth20@100ms`;
  
  try {
    binanceWS = new WebSocket(wsUrl);
    binanceWS.onopen = () => { useDirectBinance = true; };
    binanceWS.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.bids && data.asks) {
        let newBids = formatOrderBookData(data.bids).sort((a, b) => b.price - a.price).slice(0, 20);
        let newAsks = formatOrderBookData(data.asks).sort((a, b) => a.price - b.price).slice(0, 20);
        orderBook.value.bids = newBids;
        orderBook.value.asks = newAsks;
        lastUpdateTime.value = new Date().toLocaleTimeString();
      }
    };
    binanceWS.onerror = () => { useDirectBinance = false; };
  } catch (e) { console.error(e); }
};

// --- 事件处理 ---

const handleSwitchCoin = (newSymbol) => {
  if (newSymbol === symbol.value) { showCoinDrawer.value = false; return; }
  const normalized = normalizeSymbol(newSymbol);
  symbol.value = normalized;
  localStorage.setItem('selectedSymbol', normalized);
  router.replace({ path: route.path, query: { ...route.query, symbol: normalized } });
  showCoinDrawer.value = false;
  showToast({ message: `${normalized}/USDT`, icon: 'success' });
};

const handlePriceClick = (price, side) => {
  router.push({ path: '/trade', query: { symbol: symbol.value, side, price } });
};

const goToTrade = (side) => {
  router.push({ path: '/trade/detail', query: { symbol: symbol.value, side, type: marketType.value } });
};

const handleIndicators = () => showToast(t('market.indicators_coming_soon'));
const handleSettings = () => showToast(t('market.settings_coming_soon'));

// --- Watchers ---

// 1. 监听 URL symbol 变化
watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = normalizeSymbol(newSymbol);
    localStorage.setItem('selectedSymbol', symbol.value);
  }
});

// 2. 监听时间周期变化 -> 刷新 K 线
watch(selectedTimeframe, () => {
  fetchKlineHistory();
});

// 3. 监听 Symbol 变化 -> 刷新所有数据
watch(() => symbol.value, (newSymbol) => {
  // 关闭旧 WS
  if (binanceWS) { binanceWS.close(); binanceWS = null; }
  
  // 尝试从 Store 获取深度
  const normalized = normalizeSymbol(newSymbol);
  const depthData = depths.value[normalized];
  
  if (depthData) {
    // ... Store 逻辑 (省略部分重复代码，核心是更新 orderBook) ...
    // 这里为了简洁，直接调用 fetchOrderBook 重新获取也是一种保底策略
    fetchOrderBook(); 
  } else {
    fetchOrderBook();
  }
  
  // 必须重新拉取 K 线
  fetchKlineHistory();
});

// 4. 监听 Store 的实时深度更新 (WebSocket)
watch(depths, (newDepths) => {
  const normalized = normalizeSymbol(symbol.value);
  const data = newDepths[normalized];
  if (data && data.bids) {
    let newBids = formatOrderBookData(data.bids).sort((a, b) => b.price - a.price).slice(0, 20);
    let newAsks = formatOrderBookData(data.asks).sort((a, b) => a.price - b.price).slice(0, 20);
    orderBook.value.bids = newBids;
    orderBook.value.asks = newAsks;
  }
}, { deep: true });

// 5. 【修复】监听实时 Ticker -> 更新 K 线最后一位
watch(tickerData, (newTicker) => {
  if (newTicker && tvWidget.value) {
    const currentPrice = parseFloat(newTicker.price);
    
    // 【核心修复】计算当前 K 线的“起始时间戳”，而不是当前秒数
    // 这样才能保证是更新“当前这根” K 线，而不是画新线
    const candleTime = getCandleStartTime(selectedTimeframe.value);
    
    tvWidget.value.updateLiveCandle({
       time: candleTime,
       close: currentPrice,
       open: currentPrice, // 暂用当前价填充，为了视觉流畅
       high: currentPrice,
       low: currentPrice
    });
  }
});

// --- 生命周期 ---

onMounted(() => {
  // 1. 修正 Symbol
  const saved = getDefaultSymbol();
  if (symbol.value !== saved) symbol.value = saved;
  
  // 2. 初始化 WS
  if (!marketStore.isConnected) marketStore.initWebSocket();
  
  // 3. 首次加载数据
  fetchOrderBook();
  fetchKlineHistory();
  
  // 4. 定时轮询盘口（作为 WS 的备用）
  orderBookInterval = setInterval(() => {
    if (!useDirectBinance) fetchOrderBook();
  }, 3000);
});

onUnmounted(() => {
  if (orderBookInterval) clearInterval(orderBookInterval);
  if (binanceWS) binanceWS.close();
});

// 模拟成交数据 (Mock)
const generateTrades = (basePrice) => {
  if (!basePrice) return [];
  return Array(15).fill(0).map((_, i) => ({
    time: new Date(Date.now() - i * 10000),
    side: Math.random() > 0.5 ? 'buy' : 'sell',
    price: basePrice * (1 + (Math.random() - 0.5) * 0.002),
    amount: Math.random() * 2
  }));
};
</script>

<style scoped>
.market-detail-page {
  background-color: #000000;
  min-height: 100vh;
  padding-bottom: 100px; /* 为底部操作栏留出空间，防止内容被遮挡 */
  color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
  display: flex;
  flex-direction: column;
}

/* ========== 全局最高优先级 CSS 注入 ========== */

/* 1. 彻底抹除 Vant 默认箭头的痕迹 */
:deep(.van-nav-bar .van-icon-arrow-left), 
:deep(.van-nav-bar__arrow) {
  display: none !important; /* 物理消失 */
}

/* 2. 定义我们的自定义返回键样式 */
.force-custom-back {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 40px !important;
  height: 44px !important;
  margin-left: -12px !important; /* 抵消 Vant 的默认边距 */
  cursor: pointer !important;
  transition: opacity 0.2s ease !important;
  z-index: 9999 !important; /* 最高优先级 */
}

.force-custom-back:active {
  opacity: 0.7 !important;
}

.back-svg-icon {
  width: 24px !important;
  height: 24px !important;
  fill: #FCD535 !important; /* 金色返回键 */
}

/* 3. 确保导航栏整体背景为 App 纯黑 */
:deep(.van-nav-bar) {
  background-color: #0E0E0E !important;
  border-bottom: none !important;
}

:deep(.van-nav-bar__title) {
  color: #FFFFFF !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}

.header-title {
  color: #FFFFFF !important;
  font-size: 18px !important;
  font-weight: 700 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s ease;
  padding: 4px 8px;
  border-radius: 4px;
}

.header-title:active {
  opacity: 0.7;
  background-color: rgba(255, 255, 255, 0.05);
}

/* 选择币种的箭头设为灰色 */
.coin-select-arrow {
  margin-left: 4px;
  color: #8E8E93 !important; /* 灰色 */
}

/* 当前价格区 - 币安风格 */
.price-section {
  padding: 20px 16px;
  background-color: #000000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}
.price-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}
.price-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.current-price-large {
  font-size: 36px;
  font-weight: 700;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  letter-spacing: -0.5px;
}
.current-price-large.up {
  color: #0ECB81;
}
.current-price-large.down {
  color: #F6465D;
}
.price-change-badge {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  width: fit-content;
}
.price-change-badge.up {
  background-color: rgba(14, 203, 129, 0.15);
  color: #0ECB81;
}
.price-change-badge.down {
  background-color: rgba(246, 70, 93, 0.15);
  color: #F6465D;
}

/* 24小时数据概览 - 2x2网格 */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 16px;
  flex-shrink: 0;
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.stat-label {
  font-size: 11px;
  color: #8E8E93;
  font-weight: 400;
  line-height: 1.2;
}
.stat-value {
  font-size: 13px;
  color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  line-height: 1.3;
  word-break: break-all;
}

/* K线图控制栏 - 币安风格 */
.chart-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: #000000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}
.timeframe-tabs {
  display: flex;
  gap: 0;
  align-items: center;
  flex: 1;
}
.timeframe-btn {
  padding: 6px 12px;
  font-size: 13px;
  color: #8E8E93;
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-weight: 500;
  position: relative;
  border-radius: 0;
}
.timeframe-btn.active {
  color: #FFFFFF;
  font-weight: 600;
}
.timeframe-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 12px;
  right: 12px;
  height: 2px;
  background-color: #FCD535;
  border-radius: 1px;
}
.timeframe-btn:active {
  opacity: 0.7;
}
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 12px;
}
.toolbar-icon {
  font-size: 18px;
  color: #8E8E93;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px;
}
.toolbar-icon:active {
  color: #FFFFFF;
  opacity: 0.8;
}

/* K 线图区域 */
.chart-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 450px; /* 固定高度，与 TradingView 容器一致 */
  width: 100%;
  overflow: hidden;
  background-color: #000000;
  min-height: 450px;
  margin: 0; /* 移除多余的 margin */
  padding: 0; /* 移除多余的 padding */
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .chart-wrapper {
    height: 50vh; /* 移动端使用视口高度 */
    min-height: 50vh;
  }
}

/* Chart container styles - TradingView widget handles its own styling */

/* 盘口和成交标签页 */
.market-tabs {
  margin-top: 0; /* 确保紧贴 K 线图下方 */
  padding-top: 0;
  background-color: #000000;
}
:deep(.market-tabs .van-tab) {
  font-size: 13px;
  font-weight: 500;
  padding: 12px 16px;
}
:deep(.market-tabs .van-tabs__content) {
  background-color: #000000;
}

/* 盘口容器 */
.orderbook-container {
  background-color: #000000;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.orderbook-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow-y: auto;
  max-height: 300px;
}

.asks-section {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.bids-section {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* 盘口行 - 原生 App 风格紧凑布局 */
.orderbook-row {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  min-height: 24px;
  height: 24px;
  line-height: 24px;
  cursor: pointer;
  transition: background-color 0.15s ease;
  overflow: hidden;
}
.orderbook-row:hover {
  background-color: rgba(255, 255, 255, 0.02);
}
.orderbook-row:active {
  background-color: rgba(255, 255, 255, 0.03);
}

/* 深度条 - 透明渐变风格 */
.depth-bar {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: var(--percent, 0%);
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  z-index: 0;
}
/* 卖单深度条：从右向左延伸（红色透明渐变） */
.ask-depth {
  background: linear-gradient(to left, rgba(246, 70, 93, 0.15) 0%, rgba(246, 70, 93, 0.05) 100%);
}
/* 买单深度条：从右向左延伸（绿色透明渐变） */
.bid-depth {
  background: linear-gradient(to left, rgba(14, 203, 129, 0.15) 0%, rgba(14, 203, 129, 0.05) 100%);
}

.row-content {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0;
  height: 100%;
  gap: 12px;
}

.price {
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  font-size: 13px;
  line-height: 24px;
  flex: 0 0 auto;
}

.ask-price {
  color: #F6465D;
  font-weight: 600;
  text-shadow: 0 0 6px rgba(246, 70, 93, 0.4);
}

.bid-price {
  color: #0ECB81;
  font-weight: 600;
  text-shadow: 0 0 6px rgba(14, 203, 129, 0.4);
}

.amount {
  color: #EAECEF;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-size: 13px;
  line-height: 24px;
  text-align: right;
  flex: 1;
  min-width: 0;
}

/* 当前价格行 - 原生 App 风格 */
.current-price-row {
  padding: 8px 12px;
  text-align: center;
  background-color: #111111;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}
.price-main-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.current-price-text {
  font-size: 18px;
  font-weight: 700;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}
.current-price-text.up {
  color: #0ECB81;
}
.current-price-text.down {
  color: #F6465D;
}
.price-fiat {
  font-size: 11px;
  color: #848E9C;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
}

/* 成交列表容器 */
.trades-container {
  background-color: #000000;
  min-height: 400px;
}

.trades-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #111111;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 12px;
  color: #848E9C;
  font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
}

.header-col {
  flex: 1;
}

.price-col {
  text-align: left;
}

.amount-col {
  text-align: right;
}

.time-col {
  text-align: right;
  flex: 0 0 70px;
}

.trades-list {
  display: flex;
  flex-direction: column;
}

.trade-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  min-height: 24px;
  height: 24px;
  line-height: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  transition: background-color 0.2s ease;
  gap: 12px;
}

.trade-row:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.trade-price {
  flex: 0 0 auto;
  text-align: left;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  font-size: 13px;
}

.trade-price.buy {
  color: #0ECB81;
}

.trade-price.sell {
  color: #F6465D;
}

.trade-amount {
  flex: 1;
  text-align: right;
  color: #EAECEF;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-size: 13px;
  min-width: 0;
}

.trade-time {
  flex: 0 0 70px;
  text-align: right;
  color: #848E9C;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-size: 11px;
}

/* 底部操作栏 - 原生 App 风格固定悬浮 */
.bottom-action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 12px;
  padding: 8px 16px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  background-color: #1E2329;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.4);
}
.action-btn {
  flex: 1;
  height: 40px;
  font-size: 14px;
  font-weight: 700;
  border-radius: 4px;
  border: none;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
}
.buy-btn {
  background-color: #0ECB81;
  color: #FFFFFF;
}
.buy-btn:active {
  opacity: 0.85;
  transform: scale(0.98);
}
.sell-btn {
  background-color: #F6465D;
  color: #FFFFFF;
}
.sell-btn:active {
  opacity: 0.85;
  transform: scale(0.98);
}

/* 币种切换抽屉 - 强制深色主题 */
:deep(.coin-drawer-popup) {
  background-color: rgba(0, 0, 0, 0.7) !important;
  backdrop-filter: blur(10px);
}

:deep(.coin-drawer-popup .van-popup) {
  background-color: #1E2329 !important;
  color: #FFFFFF !important;
}

:deep(.coin-drawer-popup .van-popup__content) {
  background-color: #1E2329 !important;
  color: #FFFFFF !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
}

.coin-drawer {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #1E2329 !important;
  color: #FFFFFF !important;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background-color: #1E2329 !important;
  flex-shrink: 0;
}

.drawer-title {
  font-size: 18px;
  font-weight: 600;
  color: #FFFFFF !important;
}

.drawer-close {
  font-size: 20px;
  color: #8E8E93 !important;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px;
}

.drawer-close:active {
  color: #FFFFFF !important;
}

.coin-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  background-color: #1E2329 !important;
  -webkit-overflow-scrolling: touch;
}

.coin-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
  background-color: transparent !important;
}

.coin-item:active {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

.coin-item.active {
  background-color: rgba(252, 213, 53, 0.1) !important;
}

.coin-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.coin-symbol {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF !important;
}

.coin-pair {
  font-size: 12px;
  color: #8E8E93 !important;
}

.coin-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  margin-right: 24px;
}

.coin-price {
  font-size: 15px;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  font-variant-numeric: tabular-nums;
}

.coin-price.up {
  color: #0ECB81 !important;
}

.coin-price.down {
  color: #F6465D !important;
}

.coin-change {
  font-size: 12px;
  font-weight: 500;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  font-variant-numeric: tabular-nums;
}

.coin-change.up {
  color: #0ECB81 !important;
}

.coin-change.down {
  color: #F6465D !important;
}

.coin-check {
  position: absolute;
  right: 16px;
  font-size: 18px;
  color: #FCD535 !important;
}

/* 闪烁动画用于时间戳 */
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>