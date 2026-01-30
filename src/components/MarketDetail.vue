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
    <div class="chart-container">
      <TradingViewWidget :symbol="symbol" :interval="selectedTimeframe" />
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
              :key="'ask-' + (ask[0] || index)"
              class="orderbook-row ask-row"
              @click="handlePriceClick(ask[0], 'sell')"
            >
              <div class="depth-bar ask-depth" :style="{ '--percent': getDepthWidth(ask[1] || 0) + '%' }"></div>
              <div class="row-content">
                <span class="price ask-price">{{ formatOrderPrice(ask[0] || 0) }}</span>
                <span class="amount">{{ formatOrderAmount(ask[1] || 0) }}</span>
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
            </div>
          </div>

          <!-- 买单区域 -->
          <div class="orderbook-section bids-section">
            <div 
              v-for="(bid, index) in (orderBook.bids || [])" 
              :key="'bid-' + (bid[0] || index)"
              class="orderbook-row bid-row"
              @click="handlePriceClick(bid[0], 'buy')"
            >
              <div class="depth-bar bid-depth" :style="{ '--percent': getDepthWidth(bid[1] || 0) + '%' }"></div>
              <div class="row-content">
                <span class="price bid-price">{{ formatOrderPrice(bid[0] || 0) }}</span>
                <span class="amount">{{ formatOrderAmount(bid[1] || 0) }}</span>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import TradingViewWidget from './TradingViewWidget.vue';
import { useMarketStore } from '@/stores/market';
import request from '@/utils/request';

// 定义组件名称，用于 KeepAlive 识别
defineOptions({
  name: 'MarketDetail'
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const marketStore = useMarketStore();

// 获取 URL 里的 symbol，如果没有则默认显示 BTC
const symbol = ref(route.query.symbol || 'BTC');

// 获取交易类型（现货或合约），如果没有则默认为合约
const marketType = ref(route.query.type === 'spot' ? 'spot' : 'futures');

// 币种切换抽屉
const showCoinDrawer = ref(false);

// 币种列表数据（从市场 store 获取实时数据）
const coinList = computed(() => {
  const symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC'];
  return symbols.map(sym => {
    const ticker = marketStore.getTicker(sym);
    if (ticker) {
      return {
        symbol: sym,
        price: ticker.price,
        change: ticker.change
      };
    } else {
      // 如果没有实时数据，使用模拟数据
      return {
        symbol: sym,
        price: getMockPrice(sym),
        change: (Math.random() - 0.5) * 10 // 模拟涨跌幅
      };
    }
  });
});

// 模拟价格（当没有实时数据时使用）
const getMockPrice = (sym) => {
  const mockPrices = {
    'BTC': 92000,
    'ETH': 3100,
    'BNB': 710,
    'SOL': 142,
    'DOGE': 0.14,
    'TRX': 0.12,
    'BEAT': 0.05,
    'AIC': 0.08
  };
  return mockPrices[sym] || 100;
};

// 格式化币种价格
const formatCoinPrice = (price) => {
  if (!price || price === 0) return '---';
  if (price >= 1000) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  } else if (price >= 1) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
  } else {
    return price.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 6 });
  }
};

// 切换币种
const handleSwitchCoin = (newSymbol) => {
  if (newSymbol === symbol.value) {
    showCoinDrawer.value = false;
    return;
  }

  // 更新 symbol
  symbol.value = newSymbol;
  
  // 更新 URL 参数（无刷新切换），保持 type 参数
  router.replace({
    path: route.path,
    query: {
      ...route.query,
      symbol: newSymbol,
      type: marketType.value // 保持交易类型
    }
  });

  // 关闭抽屉
  showCoinDrawer.value = false;

  // 显示切换成功提示
  showToast({
    message: `${newSymbol}/USDT`,
    icon: 'success',
    duration: 1500
  });
};

// 监听路由变化
watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
    // 当 symbol 变化时，重新加载订单簿数据
    loadOrderBook();
  }
});

// 监听 symbol 变化，重新加载订单簿数据
watch(() => symbol.value, () => {
  loadOrderBook();
});

// 从市场 store 获取实时数据
const tickerData = computed(() => {
  return marketStore.getTicker(symbol.value);
});

// 当前价格和涨跌幅（从 store 读取）
const currentPrice = computed(() => {
  return tickerData.value?.price || 0;
});

const priceChange = computed(() => {
  return tickerData.value?.change || 0;
});

// 24小时统计数据（从 store 读取）
const stats = computed(() => {
  const ticker = tickerData.value;
  if (!ticker) {
    return {
      high24h: 0,
      low24h: 0,
      volume24h: 0,
      amount24h: 0
    };
  }
  
  return {
    high24h: ticker.high || 0,
    low24h: ticker.low || 0,
    volume24h: ticker.volume || 0,
    amount24h: ticker.quoteVolume || 0
  };
});

// 检查数据是否已加载
const isDataLoaded = computed(() => {
  return marketStore.hasData(symbol.value);
});

// 时间周期
const timeframes = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' }
];
const selectedTimeframe = ref('1h');

// 计算所有订单中的最大数量（用于深度条计算）
const maxOrderVolume = computed(() => {
  // 确保 orderBook.bids 和 orderBook.asks 是数组
  const safeAsks = Array.isArray(orderBook.value.asks) ? orderBook.value.asks : [];
  const safeBids = Array.isArray(orderBook.value.bids) ? orderBook.value.bids : [];
  
  // 从数组格式 [price, quantity] 中提取数量
  const allAsks = safeAsks.map(a => parseFloat(a[1]) || 0);
  const allBids = safeBids.map(b => parseFloat(b[1]) || 0);
  const allAmounts = [...allAsks, ...allBids];
  if (allAmounts.length === 0) return 1; // 避免除零
  return Math.max(...allAmounts, 1);
});

// 计算深度条宽度（基于全局最大挂单量）
const getDepthWidth = (amount) => {
  if (!amount || amount === 0 || !maxOrderVolume.value) return 0;
  return (amount / maxOrderVolume.value) * 100;
};

// 格式化法币价格（CNY）
const formatFiatPrice = (price) => {
  if (!price || price === 0) return '¥---';
  // 假设 1 USDT ≈ 7.2 CNY
  const cnyPrice = price * 7.2;
  return `¥${cnyPrice.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })}`;
};

// 点击价格行
const handlePriceClick = (price, side) => {
  router.push({ 
    path: '/trade', 
    query: { 
      symbol: symbol.value,
      side: side,
      price: price
    } 
  });
};

// 指标设置
const handleIndicators = () => {
  showToast({ message: t('market.indicators_coming_soon'), duration: 2000 });
};

// 图表设置
const handleSettings = () => {
  showToast({ message: t('market.settings_coming_soon'), duration: 2000 });
};

// 标签页状态
const activeTab = ref(0);

// 盘口数据（从 API 获取）
const orderBook = ref({
  bids: [],
  asks: []
});
const maxVolume = ref(1000);

// 从后端 API 加载订单簿数据
const fetchOrderBook = () => {
  request.get('/api/v1/market/orderbook', {
    params: {
      symbol: 'BTCUSDT',
      limit: 20
    }
  }).then(res => {
    orderBook.value = res.data || { bids: [], asks: [] };
    
    // 计算最大数量（用于深度条）
    if (orderBook.value.bids && orderBook.value.asks) {
      const allAmounts = [
        ...(orderBook.value.bids || []).map(b => parseFloat(b[1]) || 0),
        ...(orderBook.value.asks || []).map(a => parseFloat(a[1]) || 0)
      ];
      maxVolume.value = allAmounts.length > 0 ? Math.max(...allAmounts, 1) : 1000;
    }
    
    console.log('Orderbook fetched:', orderBook.value);
  }).catch(err => {
    console.error('Orderbook error:', err);
    orderBook.value = { bids: [], asks: [] };
  });
};

// 兼容旧代码的 loadOrderBook 函数
const loadOrderBook = fetchOrderBook;

// 盘口数据生成函数（保留作为后备方案，但不再使用）
const generateOrderBook = (basePrice) => {
  const asks = [];
  const bids = [];
  const maxVolume = 1000;
  
  // 生成卖单（价格从高到低，倒序显示）
  for (let i = 0; i < 10; i++) {
    asks.push({
      price: basePrice * (1 + (10 - i) * 0.001),
      amount: Math.random() * 50 + 10
    });
  }
  
  // 生成买单（价格从低到高，正序显示）
  for (let i = 0; i < 10; i++) {
    bids.push({
      price: basePrice * (1 - (i + 1) * 0.001),
      amount: Math.random() * 50 + 10
    });
  }
  
  return { asks, bids, maxVolume };
};

// 最新成交数据生成函数（使用计算属性，当价格更新时自动更新）
const generateTrades = (basePrice) => {
  const trades = [];
  const now = new Date();
  
  if (basePrice === 0) {
    return trades;
  }
  
  for (let i = 0; i < 20; i++) {
    const time = new Date(now.getTime() - i * 30000); // 每30秒一笔
    const side = Math.random() > 0.5 ? 'buy' : 'sell';
    const price = basePrice * (1 + (Math.random() - 0.5) * 0.002);
    const amount = Math.random() * 5 + 0.1;
    
    trades.push({
      time,
      side,
      price,
      amount
    });
  }
  
  return trades;
};

const trades = computed(() => {
  const data = generateTrades(currentPrice.value);
  return Array.isArray(data) ? data : [];
});

// 格式化价格（处理空值）
const formatPrice = (value) => {
  if (!value || value === 0) return '---';
  
  // 根据价格大小选择不同的格式化方式
  if (value >= 1000) {
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  } else if (value >= 1) {
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    });
  } else {
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 4,
      maximumFractionDigits: 6
    });
  }
};

// 格式化成交量（处理空值）
const formatVolume = (value) => {
  if (!value || value === 0) return '---';
  
  if (value >= 1000000000) {
    return (value / 1000000000).toFixed(2) + 'B';
  } else if (value >= 1000000) {
    return (value / 1000000).toFixed(2) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(2) + 'K';
  }
  return value.toFixed(2);
};

// 格式化盘口价格
const formatOrderPrice = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 格式化盘口数量
const formatOrderAmount = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 4,
    maximumFractionDigits: 4
  });
};

// 格式化成交时间
const formatTradeTime = (date) => {
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// 格式化金额
const formatAmount = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(0) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(0) + 'K';
  }
  return value.toFixed(0);
};


// 跳转到交易页面
const goToTrade = (side) => {
  // 跳转到交易子页面（从K线页进入），传递交易类型
  router.push({
    path: '/trade/detail',
    query: {
      symbol: symbol.value,
      side: side,
      type: marketType.value // 传递交易类型（spot 或 futures）
    }
  });
};

// 订单簿刷新定时器
let orderBookInterval = null;

// 初始化 WebSocket 连接（如果尚未连接）
onMounted(() => {
  if (!marketStore.isConnected) {
    marketStore.initWebSocket();
  }
  // 加载订单簿数据
  fetchOrderBook();
  
  // 定时刷新订单簿数据（每3秒）
  orderBookInterval = setInterval(() => {
    fetchOrderBook();
  }, 3000);
});

// 组件卸载时清理定时器
onUnmounted(() => {
  if (orderBookInterval) {
    clearInterval(orderBookInterval);
    orderBookInterval = null;
  }
});
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
.chart-container {
  flex: 1;
  background-color: #000000;
  overflow: hidden;
  min-height: 400px;
}
/* Chart container styles - TradingView widget handles its own styling */

/* 盘口和成交标签页 */
.market-tabs {
  margin-top: 0;
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
</style>

