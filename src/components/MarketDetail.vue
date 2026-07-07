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
            <path d="M669.6 849.6c8.8 8 22.4 7.2 30.4-1.6s7.2-22.4-1.6-30.4l-304-277.6 304-277.6c8.8-8 9.6-21.6 1.6-30.4s-21.6-9.6-30.4-1.6l-320 292.8c-4.4 4-6.4 9.6-6.4 15.2s2 11.2 6.4 15.2l320 292.8z" fill="var(--color-brand-legacy)"></path>
          </svg>
        </div>
      </template>

      <template #title>
        <div class="header-title" @click="showCoinDrawer = true">
          <span>{{ symbol }}/USDT</span>
          <van-icon name="arrow-down" size="12" class="coin-select-arrow" />
        </div>
      </template>

      <template #right>
        <div class="nav-actions">
          <van-icon
            :name="isFavorite ? 'star' : 'star-o'"
            class="nav-action-icon"
            :class="{ active: isFavorite }"
            @click="toggleFavorite"
          />
          <van-icon name="ellipsis" class="nav-action-icon" @click="handleMore" />
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
            <template v-if="isDataLoaded && currentPrice > 0">
              {{ formatPrice(currentPrice) }}
            </template>
            <template v-else>--</template>
          </div>
          <div class="price-change-badge" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
            <template v-if="isDataLoaded && currentTicker">
              {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
            </template>
            <template v-else>---</template>
          </div>
          <!-- WebSocket 连接状态指示器 -->
          <div class="ws-status-indicator" :class="{ 
            connected: wsConnected && !wsConnecting, 
            connecting: wsConnecting,
            disconnected: !wsConnected && !wsConnecting 
          }">
            <span class="ws-status-dot"></span>
            <span class="ws-status-text">
              {{ wsConnecting ? '连接中...' : (wsConnected ? '已连接' : '未连接') }}
            </span>
          </div>
        </div>
        
        <!-- 右侧：2x2 网格布局（使用真实数据，添加加载状态判断） -->
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_high') }}</div>
            <div class="stat-value">
              <template v-if="currentTicker && currentTicker.high">
                {{ formatPrice(currentTicker.high) }}
              </template>
              <template v-else>--</template>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_low') }}</div>
            <div class="stat-value">
              <template v-if="currentTicker && currentTicker.low">
                {{ formatPrice(currentTicker.low) }}
              </template>
              <template v-else>--</template>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_vol') }}</div>
            <div class="stat-value">
              <template v-if="currentTicker && currentTicker.volume">
                {{ formatVolume(currentTicker.volume) }} {{ symbol }}
              </template>
              <template v-else>--</template>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-label">{{ t('market.24h_amt') }}</div>
            <div class="stat-value">
              <template v-if="currentTicker && currentTicker.quoteVolume">
                {{ formatAmount(currentTicker.quoteVolume) }}
              </template>
              <template v-else>--</template>
            </div>
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
    <div class="chart-box" ref="chartBox">
      <!-- 左上角 OHLC -->
      <div class="ohlc-overlay">
        <span class="ohlc-item">O<b :class="candleUp ? 'up' : 'down'">{{ formatPrice(lastCandle.open) }}</b></span>
        <span class="ohlc-item">H<b class="up">{{ formatPrice(lastCandle.high) }}</b></span>
        <span class="ohlc-item">L<b class="down">{{ formatPrice(lastCandle.low) }}</b></span>
        <span class="ohlc-item">C<b :class="candleUp ? 'up' : 'down'">{{ formatPrice(lastCandle.close) }}</b></span>
      </div>

      <trading-view-widget 
        ref="tvWidget"
        :symbol="symbol"
        :interval="selectedTimeframe"
        :initial-data="klineHistory" 
      />

      <!-- 左下角全屏按钮 -->
      <button class="fullscreen-btn" type="button" aria-label="全屏" @click="toggleFullscreen">
        <van-icon name="expand-o" />
      </button>
    </div>

    <!-- 盘口和成交标签页 -->
    <van-tabs 
      v-model:active="activeTab" 
      background="transparent" 
      title-active-color="var(--color-brand-legacy)" 
      title-inactive-color="var(--color-text-secondary)" 
      line-width="40px" 
      line-height="2px" 
      color="var(--color-brand-legacy)" 
      :border="false"
      class="market-tabs"
    >
      <van-tab :title="t('market.orderbook')">
        <div class="orderbook-pro">
          <!-- 中间当前价 -->
          <div class="ob-current">
            <span class="ob-current-price" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
              {{ formatPrice(displayPrice) }}
            </span>
            <span class="ob-current-fiat">≈ {{ formatFiatPrice(displayPrice) }}</span>
            <span class="ob-current-time">更新 {{ lastUpdateTime }}</span>
          </div>

          <!-- 双栏盘口：左买盘 / 右卖盘 -->
          <div class="ob-columns">
            <!-- 买盘 -->
            <div class="ob-col ob-bids">
              <div class="ob-col-title bid">买盘</div>
              <div class="ob-col-head">
                <span>价格(USDT)</span>
                <span>数量({{ symbol }})</span>
              </div>
              <div
                v-for="(bid, i) in bidLevels"
                :key="'bid-' + i"
                class="ob-row"
                @click="handlePriceClick(bid.price, 'buy')"
              >
                <div class="ob-depth bid" :style="{ width: depthPct(bid.amount) + '%' }"></div>
                <span class="ob-price bid">{{ formatOrderPrice(bid.price) }}</span>
                <span class="ob-amt">{{ formatOrderAmount(bid.amount) }}</span>
              </div>
            </div>

            <!-- 卖盘 -->
            <div class="ob-col ob-asks">
              <div class="ob-col-title ask">卖盘</div>
              <div class="ob-col-head">
                <span>价格(USDT)</span>
                <span>数量({{ symbol }})</span>
              </div>
              <div
                v-for="(ask, i) in askLevels"
                :key="'ask-' + i"
                class="ob-row"
                @click="handlePriceClick(ask.price, 'sell')"
              >
                <div class="ob-depth ask" :style="{ width: depthPct(ask.amount) + '%' }"></div>
                <span class="ob-price ask">{{ formatOrderPrice(ask.price) }}</span>
                <span class="ob-amt">{{ formatOrderAmount(ask.amount) }}</span>
              </div>
            </div>
          </div>
        </div>
      </van-tab>

      <van-tab :title="t('market.recent_trades')">
        <div class="trades-container">
          <div class="trades-header">
            <span class="header-col time-col">{{ t('market.time') }}</span>
            <span class="header-col price-col">{{ t('market.price') }}(USDT)</span>
            <span class="header-col amount-col">{{ t('market.amount') }}({{ symbol }})</span>
          </div>
          <div class="trades-list">
            <div 
              v-for="(trade, index) in (trades || [])" 
              :key="'trade-' + index"
              class="trade-row"
            >
              <span class="trade-time">{{ formatTradeTime(trade?.time || new Date()) }}</span>
              <span class="trade-price" :class="{ buy: trade?.side === 'buy', sell: trade?.side === 'sell' }">
                {{ formatOrderPrice(trade?.price || 0) }}
              </span>
              <span class="trade-amount">{{ formatOrderAmount(trade?.amount || 0) }}</span>
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

// 后端 WebSocket 连接（用于实时K线数据）
let backendWS = null;
let wsReconnectAttempts = 0;
let wsReconnectTimer = null;
const maxWsReconnectAttempts = 3;
const wsReconnectDelay = 3000; // 3秒
const wsConnected = ref(false); // WebSocket 连接状态
const wsConnecting = ref(false); // WebSocket 连接中状态（初始状态）

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

// 币种列表（使用真实数据，移除 Mock）
const coinList = computed(() => {
  const symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC'];
  return symbols.map(sym => {
    const ticker = marketStore.getTicker(sym);
    // 使用真实数据，如果数据未加载则显示占位符
    return ticker ? 
      { symbol: sym, price: ticker.price, change: ticker.change } : 
      { symbol: sym, price: 0, change: 0 }; // 数据未加载时显示 0，而不是 Mock 数据
  });
});

// 从 Store 获取当前币种的 Ticker（使用真实数据，移除 Mock）
const currentTicker = computed(() => {
  // 从 Store 获取当前币种的实时数据
  return marketStore.getTicker(symbol.value);
});

// 从 currentTicker 计算价格和涨跌幅
const currentPrice = computed(() => currentTicker.value?.price || 0);
const priceChange = computed(() => currentTicker.value?.change || 0);
const isDataLoaded = computed(() => marketStore.hasData(symbol.value));

// 兼容性：保留 tickerData 别名（用于 watch）
const tickerData = currentTicker;

// 24小时统计（基于 currentTicker，100% 使用真实数据，无 Mock fallback）
const stats = computed(() => {
  const ticker = currentTicker.value;
  // 如果数据未加载，返回空值（前端会显示占位符）
  if (!ticker) {
    return { 
      high24h: null, 
      low24h: null, 
      volume24h: null, 
      amount24h: null 
    };
  }
  // 100% 使用 marketStore.ticker 的真实数据，无任何 Mock fallback
  return {
    high24h: ticker.high || null,
    low24h: ticker.low || null,
    volume24h: ticker.volume || null,  // 实时从 marketStore.ticker 获取
    amount24h: ticker.quoteVolume || null  // 实时从 marketStore.ticker 获取
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

// ============================================================
//  盘口 / 成交 Mock 兜底数据
//  真实 WS/接口有数据时优先用真实数据，无数据时用 Mock，保证专业盘口观感
// ============================================================
const chartBox = ref(null);
const isFavorite = ref(false);

// 各币种缺省价（真实价未加载时用于生成 Mock 盘口）
const FALLBACK_PRICES = {
  BTC: 92000, ETH: 3200, BNB: 610, SOL: 190,
  DOGE: 0.16, TRX: 0.13, BEAT: 1.2, AIC: 0.8
};

// Mock 数量（固定，避免每次渲染抖动）
const MOCK_BID_AMOUNTS = [0.1254, 0.0831, 0.2467, 0.4123, 0.6789];
const MOCK_ASK_AMOUNTS = [0.1328, 0.0976, 0.2265, 0.3954, 0.6021];

// 用于 Mock 的基准价
const basePriceForMock = computed(() => {
  if (currentPrice.value > 0) return currentPrice.value;
  return FALLBACK_PRICES[symbol.value] || 100;
});

// 盘口中间展示的价格（真实优先）
const displayPrice = computed(() => currentPrice.value > 0 ? currentPrice.value : basePriceForMock.value);

// 价格档位步长（按价格量级自适应）
const priceStep = (base) => {
  if (base >= 1000) return 0.5;
  if (base >= 1) return 0.01;
  return 0.0001;
};

// 买盘 5 档：真实优先，否则 Mock（价格由高到低）
const bidLevels = computed(() => {
  const real = (orderBook.value.bids || []).filter(b => b && b.price).slice(0, 5);
  if (real.length >= 5) return real;
  const base = basePriceForMock.value;
  const step = priceStep(base);
  return MOCK_BID_AMOUNTS.map((amount, i) => ({ price: base - step * (i + 1), amount }));
});

// 卖盘 5 档：真实优先，否则 Mock（价格由低到高）
const askLevels = computed(() => {
  const real = (orderBook.value.asks || []).filter(a => a && a.price).slice(0, 5);
  if (real.length >= 5) return real;
  const base = basePriceForMock.value;
  const step = priceStep(base);
  return MOCK_ASK_AMOUNTS.map((amount, i) => ({ price: base + step * (i + 1), amount }));
});

// 深度条最大值（基于当前展示的档位）
const maxLevelVolume = computed(() => {
  const all = [...bidLevels.value, ...askLevels.value].map(x => x.amount || 0);
  return Math.max(...all, 0.0001);
});
const depthPct = (amount) => Math.min(100, Math.round((amount / maxLevelVolume.value) * 100));

// K 线左上角 OHLC（真实最后一根优先，否则 Mock）
const lastCandle = computed(() => {
  const h = klineHistory.value;
  if (Array.isArray(h) && h.length) {
    const c = h[h.length - 1];
    return { open: c.open, high: c.high, low: c.low, close: c.close };
  }
  const base = basePriceForMock.value;
  return { open: base * 0.9994, high: base * 1.0009, low: base * 0.9989, close: base };
});
const candleUp = computed(() => (lastCandle.value.close || 0) >= (lastCandle.value.open || 0));

const trades = computed(() => generateTrades(basePriceForMock.value));

const timeframes = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' }
];

// --- 工具函数 ---

// getMockPrice 函数已删除 - 使用真实数据

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
    // ========== 关键修复：使用 /klines 接口（从币安 REST API 获取最新数据）==========
    const res = await request.get('/api/v1/market/klines', {
      params: {
        symbol: symbol.value + 'USDT', // 使用标准格式，如 BTCUSDT
        interval: selectedTimeframe.value, 
        limit: 1000
      }
    });

    if (res.data && Array.isArray(res.data)) {
      // ========== 关键修复：确保数据格式正确（time 单位为秒）==========
      // /klines 接口返回格式：[[timestamp(ms), open, high, low, close, volume], ...]
      const formattedData = res.data.map(item => {
        // 兼容数组格式和对象格式
        if (Array.isArray(item)) {
          return {
            time: Math.floor(item[0] / 1000), // 毫秒转秒级时间戳（整数）
            open: parseFloat(item[1]),
            high: parseFloat(item[2]),
            low: parseFloat(item[3]),
            close: parseFloat(item[4]),
            volume: item[5] ? parseFloat(item[5]) : undefined // 可选：成交量
          };
        } else {
          // 兼容对象格式（如果后端返回对象格式）
          return {
            time: Math.floor((item.time || item.timestamp) / 1000),
            open: parseFloat(item.open),
            high: parseFloat(item.high),
            low: parseFloat(item.low),
            close: parseFloat(item.close),
            volume: item.volume ? parseFloat(item.volume) : undefined
          };
        }
      });
      klineHistory.value = formattedData;
      console.log('[Market] ✅ K-line history loaded from /klines:', formattedData.length, '条');
      console.log('[Market] 第一条数据:', formattedData[0]);
      
      // ========== 关键修复：如果有图表组件，立即更新历史数据 ==========
      if (tvWidget.value && tvWidget.value.updateHistory) {
        tvWidget.value.updateHistory(formattedData);
        console.log('[Market] ✅ 图表历史数据已更新');
      }
    }
  } catch (error) {
    console.error('[Market] ❌ 获取 K 线数据失败:', error);
    console.error('[Market] 请求 URL:', '/api/v1/market/klines');
    console.error('[Market] 请求参数:', {
      symbol: symbol.value + 'USDT',
      interval: selectedTimeframe.value,
      limit: 1000
    });
    if (error.response) {
      console.error('[Market] 响应状态:', error.response.status);
      console.error('[Market] 响应数据:', error.response.data);
    } else if (error.request) {
      console.error('[Market] 请求已发出但未收到响应，请检查：');
      console.error('[Market] 1. 后端服务是否运行在 http://127.0.0.1:8000');
      console.error('[Market] 2. Vite 代理配置是否正确');
      console.error('[Market] 3. 网络连接是否正常');
    }
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

// 3. 币安 WS 连接（订单簿）
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

// 4. 后端 WebSocket 连接（实时K线数据）
// 注意：WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问 ws:// 协议
// 用户应该访问 http://localhost:5173/（非 ws://），然后 JavaScript 代码会自动连接 WebSocket
const connectBackendWebSocket = () => {
  // 如果已有连接且状态正常，不重复连接
  if (backendWS && backendWS.readyState === WebSocket.OPEN) {
    console.log('[MarketDetail] ✅ WebSocket 已连接，跳过重复连接');
    return;
  }

  // 关闭旧连接
  if (backendWS) {
    try {
      backendWS.close();
    } catch (e) {
      console.warn('[MarketDetail] 关闭旧连接时出错:', e);
    }
    backendWS = null;
  }

  // 清除重连定时器
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }

  // ========== 关键修复：设置连接中状态 ==========
  wsConnecting.value = true;
  wsConnected.value = false;

  // 使用 Vite 代理：通过 /ws 路径连接，Vite 会自动代理到后端 /api/v1/market/ws/kline
  // 注意：必须使用 ws:// 协议，不能使用 wss://（开发环境）
  // 前端通过 ws://localhost:5173/ws 连接，Vite 会自动代理到 ws://127.0.0.1:8000/api/v1/market/ws/kline
  const wsUrl = `ws://${window.location.host}/ws`;
  console.log('[MarketDetail] ========== 连接后端 WebSocket ==========');
  console.log('[MarketDetail] WebSocket URL:', wsUrl);
  console.log('[MarketDetail] 注意: WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问');
  console.log('[MarketDetail] 请访问 http://localhost:5173/（非 ws://）');

  try {
    backendWS = new WebSocket(wsUrl);

    backendWS.onopen = () => {
      console.log('[MarketDetail] ✅ WebSocket 连接成功');
      // ========== 关键修复：更新状态为"已连接" ==========
      wsConnected.value = true;
      wsConnecting.value = false; // 连接成功，取消连接中状态
      wsReconnectAttempts = 0; // 重置重连次数
      if (wsReconnectTimer) {
        clearTimeout(wsReconnectTimer);
        wsReconnectTimer = null;
      }
      
      // ========== 关键修复：发送订阅 Binance K 线流消息 ==========
      // 订阅格式：{ "method": "SUBSCRIBE", "params": [symbol + "@kline_" + interval], "id": 1 }
      const subscribeMessage = {
        method: "SUBSCRIBE",
        params: [
          `${symbol.value.toLowerCase()}usdt@kline_${selectedTimeframe.value}`
        ],
        id: 1
      };
      
      try {
        backendWS.send(JSON.stringify(subscribeMessage));
        console.log('[MarketDetail] 📤 已发送订阅消息:', subscribeMessage);
        console.log('[MarketDetail] 📡 WebSocket 状态: 已连接，等待接收 K 线数据...');
      } catch (error) {
        console.error('[MarketDetail] ❌ 发送订阅消息失败:', error);
      }
    };

    backendWS.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[MarketDetail] 📨 收到 WebSocket 消息:', data);

        // ========== 关键修复：处理连接成功消息，更新状态为"已连接" ==========
        if (data.type === 'connected') {
          console.log('[MarketDetail] ✅ WebSocket 连接确认:', data.message);
          wsConnected.value = true;
          wsConnecting.value = false; // 连接成功，取消连接中状态
          console.log('[MarketDetail] 📡 WebSocket 状态: 已连接，等待接收 K 线数据...');
          return;
        }

        // ========== 关键修复：处理 K 线数据并立即更新 TradingViewWidget ==========
        // 支持两种数据格式：
        // 1. 后端推送格式：{ type: 'kline', data: { symbol, interval, timestamp, open, high, low, close, volume } }
        // 2. Binance 原始格式：{ stream: 'btcusdt@kline_1m', data: { k: { s, i, t, o, h, l, c, v, x } } }
        let kline = null;
        
        if (data.type === 'kline' && data.data) {
          // 后端推送格式：{ type: 'kline', data: { symbol, interval, time, open, high, low, close, volume, is_closed } }
          kline = {
            symbol: data.data.symbol || '',
            interval: data.data.interval || '',
            timestamp: data.data.time || data.data.timestamp || 0,  // 后端推送 time（毫秒）
            time: data.data.time || data.data.timestamp || 0,  // 兼容字段
            open: parseFloat(data.data.open || 0),
            high: parseFloat(data.data.high || 0),
            low: parseFloat(data.data.low || 0),
            close: parseFloat(data.data.close || 0),
            volume: parseFloat(data.data.volume || 0),
            is_closed: data.data.is_closed || false
          };
          console.log('[MarketDetail] 📊 收到K线数据（后端格式）:', {
            symbol: kline.symbol,
            interval: kline.interval,
            timestamp: kline.timestamp,
            close: kline.close,
            volume: kline.volume,
            is_closed: kline.is_closed
          });
        } else if (data.stream && data.stream.includes('@kline_') && data.data && data.data.k) {
          // Binance 原始格式（如果后端直接转发）
          const klineData = data.data.k;
          kline = {
            symbol: klineData.s?.replace('USDT', '/USDT') || '',
            interval: klineData.i || '',
            timestamp: klineData.t || 0,
            time: klineData.t || 0,
            open: parseFloat(klineData.o || 0),
            high: parseFloat(klineData.h || 0),
            low: parseFloat(klineData.l || 0),
            close: parseFloat(klineData.c || 0),
            volume: parseFloat(klineData.v || 0),
            is_closed: klineData.x || false
          };
          console.log('[MarketDetail] 📊 收到K线数据（Binance格式）:', {
            symbol: kline.symbol,
            interval: kline.interval,
            timestamp: kline.timestamp,
            close: kline.close,
            is_closed: kline.is_closed
          });
        }
        
        if (kline) {
          // ========== 关键修复：更新 marketStore 的 ticker 数据（实时更新 stats）==========
          // 检查当前交易对是否匹配
          const normalizedSymbol = normalizeSymbol(symbol.value);
          const klineSymbol = kline.symbol?.replace('/', '').replace('USDT', '').toUpperCase();
          
          // 如果交易对匹配，更新 marketStore 的 ticker 数据
          if (klineSymbol === normalizedSymbol) {
            // 更新 marketStore 的 ticker，这样 stats 计算属性会自动更新
            const ticker = marketStore.getTicker(normalizedSymbol);
            if (ticker) {
              // 更新价格和统计数据
              ticker.price = parseFloat(kline.close);
              ticker.high = Math.max(ticker.high || 0, parseFloat(kline.high));
              ticker.low = Math.min(ticker.low || Infinity, parseFloat(kline.low)) || ticker.low || 0;
              ticker.volume = (ticker.volume || 0) + parseFloat(kline.volume || 0);
              ticker.lastUpdate = Date.now();
            }
          }
          
          // ========== 关键修复：处理 K 线数据并更新图表 ==========
          // 如果交易对匹配，且时间周期匹配，则更新图表
          if (klineSymbol === normalizedSymbol && kline.interval === selectedTimeframe.value) {
            // ========== 关键修复：确保 tvWidget 存在且已初始化 ==========
            if (!tvWidget.value) {
              console.warn('[MarketDetail] ⚠️ TradingViewWidget ref 未找到，等待组件初始化...');
              return;
            }
            
            // ========== 关键修复：确保 updateLiveCandle 方法存在 ==========
            if (typeof tvWidget.value.updateLiveCandle !== 'function') {
              console.warn('[MarketDetail] ⚠️ TradingViewWidget.updateLiveCandle 不是函数，等待组件初始化...');
              console.warn('[MarketDetail] tvWidget.value:', tvWidget.value);
              console.warn('[MarketDetail] 可用方法:', Object.keys(tvWidget.value || {}));
              return;
            }
            
            // ========== 关键修复：转换时间戳和数据格式 ==========
            // 后端发送的 time 是毫秒级时间戳（unix_ms），TradingView 需要秒级时间戳
            const candleTime = Math.floor((kline.time || kline.timestamp) / 1000);
            
            // ========== 关键修复：调用 TradingViewWidget 的 updateLiveCandle 方法更新 K 线 ==========
            // 数据格式：{time: number(秒), open: number, high: number, low: number, close: number, volume?: number}
            try {
              tvWidget.value.updateLiveCandle({
                time: candleTime,
                open: parseFloat(kline.open),
                high: parseFloat(kline.high),
                low: parseFloat(kline.low),
                close: parseFloat(kline.close),
                volume: kline.volume ? parseFloat(kline.volume) : undefined
              });
              
              console.log('[MarketDetail] ✅ 已更新 K 线图:', {
                symbol: kline.symbol,
                interval: kline.interval,
                time: candleTime,
                close: kline.close,
                volume: kline.volume
              });
            } catch (updateError) {
              console.error('[MarketDetail] ❌ 更新 K 线图失败:', updateError);
              console.error('[MarketDetail] K 线数据:', kline);
            }
          } else {
            console.log('[MarketDetail] ⚠️ K线数据交易对或时间周期不匹配，跳过更新:', {
              klineSymbol,
              normalizedSymbol,
              klineInterval: kline.interval,
              selectedTimeframe: selectedTimeframe.value
            });
          }
        }
      } catch (error) {
        console.error('[MarketDetail] ❌ 解析 WebSocket 消息失败:', error);
        console.error('[MarketDetail] 消息内容:', event.data);
      }
    };

    backendWS.onerror = (error) => {
      console.error('[MarketDetail] ❌ WebSocket 错误:', error);
      console.error('[MarketDetail] 重连次数:', wsReconnectAttempts, '/', maxWsReconnectAttempts);
      wsConnected.value = false;
      wsConnecting.value = false; // 连接失败，取消连接中状态
      
      // 检查是否是 ERR_UNKNOWN_URL_SCHEME 错误
      if (error && error.message && error.message.includes('ERR_UNKNOWN_URL_SCHEME')) {
        console.error('[MarketDetail] ⚠️ ERR_UNKNOWN_URL_SCHEME 错误');
        console.error('[MarketDetail] 原因: 不能直接在浏览器地址栏访问 ws:// 协议');
        console.error('[MarketDetail] 解决方案: 请访问 http://localhost:5173/（非 ws://），然后 JavaScript 代码会自动连接 WebSocket');
      }
    };

    backendWS.onclose = (event) => {
      console.warn('[MarketDetail] ⚠️ WebSocket 连接已关闭');
      console.warn('[MarketDetail] 关闭代码:', event.code);
      console.warn('[MarketDetail] 关闭原因:', event.reason || '未知');
      wsConnected.value = false;
      wsConnecting.value = false; // 连接关闭，取消连接中状态
      backendWS = null;

      // 自动重连（如果未达到最大重连次数）
      if (wsReconnectAttempts < maxWsReconnectAttempts) {
        wsReconnectAttempts++;
        console.log(`[MarketDetail] 🔄 准备重连 WebSocket (${wsReconnectAttempts}/${maxWsReconnectAttempts})，${wsReconnectDelay}ms 后重试...`);
        wsReconnectTimer = setTimeout(() => {
          console.log(`[MarketDetail] 🔄 尝试重连 WebSocket (${wsReconnectAttempts}/${maxWsReconnectAttempts})...`);
          connectBackendWebSocket();
        }, wsReconnectDelay);
      } else {
        console.error(`[MarketDetail] ❌ 已达到最大重连次数 (${maxWsReconnectAttempts} 次)，停止重连`);
        console.error('[MarketDetail] 请检查网络连接或后端服务是否正常运行');
        console.error('[MarketDetail] 后端服务地址: http://127.0.0.1:8000');
        wsReconnectAttempts = 0; // 重置计数器，允许用户手动重试
      }
    };
  } catch (error) {
    console.error('[MarketDetail] ❌ 创建 WebSocket 连接失败:', error);
    wsConnected.value = false;
    wsConnecting.value = false; // 连接失败，取消连接中状态
    
    // 检查是否是 ERR_UNKNOWN_URL_SCHEME 错误
    if (error && error.message && error.message.includes('ERR_UNKNOWN_URL_SCHEME')) {
      console.error('[MarketDetail] ⚠️ ERR_UNKNOWN_URL_SCHEME 错误');
      console.error('[MarketDetail] 原因: 不能直接在浏览器地址栏访问 ws:// 协议');
      console.error('[MarketDetail] 解决方案: 请访问 http://localhost:5173/（非 ws://），然后 JavaScript 代码会自动连接 WebSocket');
    }
    
    // 连接失败时也触发重连逻辑
    if (wsReconnectAttempts < maxWsReconnectAttempts) {
      wsReconnectAttempts++;
      console.log(`[MarketDetail] 🔄 准备重连 WebSocket (${wsReconnectAttempts}/${maxWsReconnectAttempts})，${wsReconnectDelay}ms 后重试...`);
      wsReconnectTimer = setTimeout(() => {
        console.log(`[MarketDetail] 🔄 尝试重连 WebSocket (${wsReconnectAttempts}/${maxWsReconnectAttempts})...`);
        connectBackendWebSocket();
      }, wsReconnectDelay);
    }
  }
};

// 断开后端 WebSocket
const disconnectBackendWebSocket = () => {
  if (backendWS) {
    backendWS.close();
    backendWS = null;
  }
  wsConnected.value = false;
  wsConnecting.value = false; // 断开连接，取消连接中状态
  wsReconnectAttempts = 0;
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }
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

// 收藏交易对（本地持久化）
const favKey = (sym) => `market_fav_${sym}`;
const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value;
  try {
    if (isFavorite.value) localStorage.setItem(favKey(symbol.value), '1');
    else localStorage.removeItem(favKey(symbol.value));
  } catch (e) { /* ignore */ }
  showToast({ message: isFavorite.value ? '已加入自选' : '已取消自选', icon: isFavorite.value ? 'star' : 'star-o' });
};

const handleMore = () => showToast('更多功能开发中');

// K 线图全屏
const toggleFullscreen = () => {
  const el = chartBox.value;
  if (!el) return;
  try {
    if (document.fullscreenElement) {
      document.exitFullscreen?.();
    } else if (el.requestFullscreen) {
      el.requestFullscreen();
    } else if (el.webkitRequestFullscreen) {
      el.webkitRequestFullscreen();
    } else {
      showToast('当前环境不支持全屏');
    }
  } catch (e) {
    showToast('全屏切换失败');
  }
};

// --- Watchers ---

// 1. 监听 URL symbol 变化
watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = normalizeSymbol(newSymbol);
    localStorage.setItem('selectedSymbol', symbol.value);
  }
});

// 币种变化时同步自选状态
watch(symbol, (sym) => {
  try { isFavorite.value = localStorage.getItem(favKey(sym)) === '1'; } catch (e) { isFavorite.value = false; }
}, { immediate: true });

// 2. 监听时间周期变化 -> 刷新 K 线
watch(selectedTimeframe, () => {
  fetchKlineHistory();
});

// 3. 监听 Symbol 变化 -> 刷新所有数据
watch(() => symbol.value, (newSymbol) => {
  // 关闭旧 WS
  if (binanceWS) { binanceWS.close(); binanceWS = null; }
  
  // 重新连接后端 WebSocket（如果需要）
  if (backendWS && backendWS.readyState === WebSocket.OPEN) {
    // WebSocket 已连接，不需要重连（后端会推送所有symbol的数据）
    console.log('[MarketDetail] Symbol 变化，WebSocket 保持连接');
  } else {
    // WebSocket 未连接，尝试连接
    connectBackendWebSocket();
  }
  
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

// 5. 监听实时 Ticker -> 更新 K 线最后一位（使用真实数据）
watch(currentTicker, (newTicker) => {
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
  
  // ========== 关键修复：确保连接状态初始化为"连接中" ==========
  // 初始状态：连接中
  wsConnecting.value = true;
  wsConnected.value = false;
  
  // 3. 连接后端 WebSocket（实时K线数据）
  connectBackendWebSocket();
  
  // 4. 首次加载数据
  fetchOrderBook();
  fetchKlineHistory();
  
  // 5. 定时轮询盘口（作为 WS 的备用）
  orderBookInterval = setInterval(() => {
    if (!useDirectBinance) fetchOrderBook();
  }, 3000);
});

onUnmounted(() => {
  if (orderBookInterval) clearInterval(orderBookInterval);
  if (binanceWS) binanceWS.close();
  disconnectBackendWebSocket(); // 断开后端 WebSocket
});

// 最新成交：真实数据接入前使用 Mock 兜底，保证列表非空且交互可用
const MOCK_TRADE_AMOUNTS = [0.0231, 0.1042, 0.0875, 0.0456, 0.0678, 0.1523, 0.0312, 0.0891, 0.2104, 0.0567, 0.0743, 0.1288];
const generateTrades = (basePrice) => {
  const base = basePrice || FALLBACK_PRICES[symbol.value] || 100;
  const step = priceStep(base);
  const now = Date.now();
  return MOCK_TRADE_AMOUNTS.map((amount, i) => {
    const side = i % 2 === 0 ? 'buy' : 'sell';
    const offset = (i % 3) * step;
    const price = side === 'buy' ? base - offset : base + offset;
    return { side, price, amount, time: new Date(now - i * 3500) };
  });
};
</script>

<style scoped>
.market-detail-page {
  background-color: var(--color-bg);
  min-height: 100vh;
  padding-bottom: 100px; /* 为底部操作栏留出空间，防止内容被遮挡 */
  color: var(--color-text-primary);
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
  fill: var(--color-brand-legacy) !important; /* 金色返回键 */
}

/* 3. 确保导航栏整体背景为 App 纯黑 */
:deep(.van-nav-bar) {
  background-color: var(--color-bg) !important;
  border-bottom: none !important;
}

:deep(.van-nav-bar__title) {
  color: var(--color-text-primary) !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}

.header-title {
  color: var(--color-text-primary) !important;
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
  background-color: rgb(var(--color-border-rgb) / 0.05);
}

/* 选择币种的箭头设为灰色 */
.coin-select-arrow {
  margin-left: 4px;
  color: var(--color-text-secondary) !important; /* 灰色 */
}

/* 当前价格区 - 币安风格 */
.price-section {
  padding: 20px 16px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
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
  color: var(--color-earn);
}
.current-price-large.down {
  color: var(--color-loss);
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

/* WebSocket 连接状态指示器 */
.ws-status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 11px;
}

.ws-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-surface-muted);
  transition: background-color 0.3s ease;
}

.ws-status-indicator.connected .ws-status-dot {
  background-color: var(--color-earn);
  box-shadow: 0 0 4px rgb(var(--color-earn-rgb) / 0.5);
}

.ws-status-indicator.connecting .ws-status-dot {
  background-color: var(--color-brand);
  box-shadow: 0 0 4px rgb(var(--color-brand-rgb) / 0.5);
  animation: pulse 1.5s ease-in-out infinite;
}

.ws-status-indicator.disconnected .ws-status-dot {
  background-color: var(--color-loss);
  box-shadow: 0 0 4px rgb(var(--color-loss-rgb) / 0.5);
}

.ws-status-text {
  color: var(--color-text-muted);
  font-size: 11px;
  transition: color 0.3s ease;
}

.ws-status-indicator.connected .ws-status-text {
  color: var(--color-earn);
}

.ws-status-indicator.connecting .ws-status-text {
  color: var(--color-brand);
}

.ws-status-indicator.disconnected .ws-status-text {
  color: var(--color-loss);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
.price-change-badge.up {
  background-color: rgb(var(--color-earn-rgb) / 0.15);
  color: var(--color-earn);
}
.price-change-badge.down {
  background-color: rgb(var(--color-loss-rgb) / 0.15);
  color: var(--color-loss);
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
  color: var(--color-text-secondary);
  font-weight: 400;
  line-height: 1.2;
}
.stat-value {
  font-size: 13px;
  color: var(--color-text-primary);
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
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
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
  color: var(--color-text-secondary);
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
  color: var(--color-text-primary);
  font-weight: 600;
}
.timeframe-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 12px;
  right: 12px;
  height: 2px;
  background-color: var(--color-brand-legacy);
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
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px;
}
.toolbar-icon:active {
  color: var(--color-text-primary);
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
  background-color: var(--color-bg);
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
  background-color: var(--color-bg);
}
:deep(.market-tabs .van-tab) {
  font-size: 13px;
  font-weight: 500;
  padding: 12px 16px;
}
:deep(.market-tabs .van-tabs__content) {
  background-color: var(--color-bg);
}

/* 盘口容器 */
.orderbook-container {
  background-color: var(--color-bg);
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
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.bids-section {
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  background-color: rgb(var(--color-border-rgb) / 0.02);
}
.orderbook-row:active {
  background-color: rgb(var(--color-border-rgb) / 0.03);
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
  background: linear-gradient(to left, rgb(var(--color-loss-rgb) / 0.15) 0%, rgb(var(--color-loss-rgb) / 0.05) 100%);
}
/* 买单深度条：从右向左延伸（绿色透明渐变） */
.bid-depth {
  background: linear-gradient(to left, rgb(var(--color-earn-rgb) / 0.15) 0%, rgb(var(--color-earn-rgb) / 0.05) 100%);
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
  color: var(--color-loss);
  font-weight: 600;
  text-shadow: 0 0 6px rgb(var(--color-loss-rgb) / 0.4);
}

.bid-price {
  color: var(--color-earn);
  font-weight: 600;
  text-shadow: 0 0 6px rgb(var(--color-earn-rgb) / 0.4);
}

.amount {
  color: var(--color-text-primary);
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
  background-color: var(--color-bg);
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.05);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  color: var(--color-earn);
}
.current-price-text.down {
  color: var(--color-loss);
}
.price-fiat {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
}

/* 成交列表容器 */
.trades-container {
  background-color: var(--color-bg);
  min-height: 400px;
}

.trades-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  font-size: 12px;
  color: var(--color-text-muted);
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
  text-align: left;
  flex: 0 0 72px;
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
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.03);
  transition: background-color 0.2s ease;
  gap: 12px;
}

.trade-row:hover {
  background-color: rgb(var(--color-border-rgb) / 0.02);
}

.trade-price {
  flex: 1;
  text-align: left;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  font-size: 13px;
}

.trade-price.buy {
  color: var(--color-earn);
}

.trade-price.sell {
  color: var(--color-loss);
}

.trade-amount {
  flex: 1;
  text-align: right;
  color: var(--color-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  font-size: 13px;
  min-width: 0;
}

.trade-time {
  flex: 0 0 72px;
  text-align: left;
  color: var(--color-text-muted);
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
  background-color: var(--color-bg-elevated);
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.08);
  z-index: 100;
  box-shadow: 0 -2px 12px rgb(var(--color-shadow-rgb) / 0.4);
}
.action-btn {
  flex: 1;
  height: 52px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', 'Arial', 'DIN Alternate', sans-serif;
  letter-spacing: 0.5px;
}
.buy-btn {
  background: linear-gradient(180deg, rgb(var(--color-earn-rgb) / 0.18) 0%, rgb(var(--color-earn-rgb) / 0.10) 100%);
  border: 1px solid rgb(var(--color-earn-rgb) / 0.40) !important;
  color: var(--color-earn) !important;
}
.buy-btn:active {
  opacity: 0.85;
  transform: scale(0.98);
}
.sell-btn {
  background: linear-gradient(180deg, rgb(var(--color-loss-rgb) / 0.18) 0%, rgb(var(--color-loss-rgb) / 0.10) 100%);
  border: 1px solid rgb(var(--color-loss-rgb) / 0.40) !important;
  color: var(--color-loss) !important;
}
.sell-btn:active {
  opacity: 0.85;
  transform: scale(0.98);
}

/* 币种切换抽屉 - 强制深色主题 */
:deep(.coin-drawer-popup) {
  background-color: rgb(var(--color-shadow-rgb) / 0.7) !important;
  backdrop-filter: blur(10px);
}

:deep(.coin-drawer-popup .van-popup) {
  background-color: var(--color-bg-elevated) !important;
  color: var(--color-text-primary) !important;
}

:deep(.coin-drawer-popup .van-popup__content) {
  background-color: var(--color-bg-elevated) !important;
  color: var(--color-text-primary) !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
}

.coin-drawer {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-elevated) !important;
  color: var(--color-text-primary) !important;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  background-color: var(--color-bg-elevated) !important;
  flex-shrink: 0;
}

.drawer-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary) !important;
}

.drawer-close {
  font-size: 20px;
  color: var(--color-text-secondary) !important;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 4px;
}

.drawer-close:active {
  color: var(--color-text-primary) !important;
}

.coin-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  background-color: var(--color-bg-elevated) !important;
  -webkit-overflow-scrolling: touch;
}

.coin-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
  background-color: transparent !important;
}

.coin-item:active {
  background-color: rgb(var(--color-border-rgb) / 0.05) !important;
}

.coin-item.active {
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.1) !important;
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
  color: var(--color-text-primary) !important;
}

.coin-pair {
  font-size: 12px;
  color: var(--color-text-secondary) !important;
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
  color: var(--color-earn) !important;
}

.coin-price.down {
  color: var(--color-loss) !important;
}

.coin-change {
  font-size: 12px;
  font-weight: 500;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  font-variant-numeric: tabular-nums;
}

.coin-change.up {
  color: var(--color-earn) !important;
}

.coin-change.down {
  color: var(--color-loss) !important;
}

.coin-check {
  position: absolute;
  right: 16px;
  font-size: 18px;
  color: var(--color-brand-legacy) !important;
}

/* 闪烁动画用于时间戳 */
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ========== 顶部右侧操作图标（收藏 / 更多） ========== */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-right: 2px;
}
.nav-action-icon {
  font-size: 20px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s ease, transform 0.15s ease;
}
.nav-action-icon:active {
  transform: scale(0.9);
}
.nav-action-icon.active {
  color: var(--color-brand-legacy);
}

/* ========== K 线容器 + 叠加层 ========== */
.chart-box {
  position: relative;
  width: 100%;
  background-color: var(--color-bg);
  flex-shrink: 0;
}
.ohlc-overlay {
  position: absolute;
  top: 8px;
  left: 12px;
  z-index: 5;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 11px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-muted);
  pointer-events: none;
  background: rgb(var(--color-bg-rgb, 255 255 255) / 0.0);
}
.ohlc-item {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.ohlc-item b {
  font-weight: 600;
}
.ohlc-item b.up { color: var(--color-earn); }
.ohlc-item b.down { color: var(--color-loss); }

.fullscreen-btn {
  position: absolute;
  left: 12px;
  bottom: 12px;
  z-index: 5;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.12);
  background: var(--color-surface-2, rgb(var(--color-border-rgb) / 0.06));
  color: var(--color-text-secondary);
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}
.fullscreen-btn:active {
  opacity: 0.7;
}

/* ========== 专业双栏盘口 ========== */
.orderbook-pro {
  background-color: var(--color-bg);
  padding: 4px 0 12px;
  min-height: 360px;
}

/* 中间当前价 */
.ob-current {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 12px 12px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.06);
}
.ob-current-price {
  font-size: 24px;
  font-weight: 800;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.ob-current-price.up { color: var(--color-earn); }
.ob-current-price.down { color: var(--color-loss); }
.ob-current-fiat {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}
.ob-current-time {
  font-size: 11px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

/* 双栏 */
.ob-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  column-gap: 0;
  padding-top: 8px;
}
.ob-col {
  min-width: 0;
  padding: 0 12px;
}
.ob-col.ob-bids {
  border-right: 1px solid rgb(var(--color-border-rgb) / 0.07);
}
.ob-col-title {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
}
.ob-col-title.bid { color: var(--color-earn); }
.ob-col-title.ask { color: var(--color-loss); }
.ob-col-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: var(--color-text-muted);
  padding-bottom: 6px;
  gap: 8px;
}
.ob-col-head span:last-child { text-align: right; }

.ob-row {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 30px;
  gap: 8px;
  cursor: pointer;
  overflow: hidden;
}
.ob-row:active {
  background-color: rgb(var(--color-border-rgb) / 0.04);
}
.ob-depth {
  position: absolute;
  top: 2px;
  bottom: 2px;
  z-index: 0;
  border-radius: 3px;
  pointer-events: none;
  transition: width 0.25s ease;
}
/* 买盘深度：从右向左 */
.ob-depth.bid {
  right: 0;
  background: rgb(var(--color-earn-rgb) / 0.12);
}
/* 卖盘深度：从左向右 */
.ob-depth.ask {
  left: 0;
  background: rgb(var(--color-loss-rgb) / 0.12);
}
.ob-price {
  position: relative;
  z-index: 1;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}
.ob-price.bid { color: var(--color-earn); }
.ob-price.ask { color: var(--color-loss); }
.ob-amt {
  position: relative;
  z-index: 1;
  font-size: 12px;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
  text-align: right;
}

/* 小屏适配 */
@media (max-width: 360px) {
  .ob-col { padding: 0 8px; }
  .ob-price { font-size: 12px; }
  .ob-amt { font-size: 11px; }
}
</style>
