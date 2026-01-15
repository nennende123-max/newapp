<template>
  <div class="markets-section">
    <!-- 顶部选项卡 -->
    <div class="markets-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 行情列表 -->
    <div class="markets-list">
      <div 
        v-for="(coin, index) in filteredMarkets" 
        :key="coin.symbol"
        class="market-item"
        @click="goToMarket(coin.symbol)"
      >
        <!-- 第一列：币种信息 (40%) -->
        <div class="coin-info-col">
          <span v-if="showRank" class="rank-number">{{ coin.rank }}</span>
          <img 
            :src="getCoinIcon(coin.symbol)" 
            :alt="coin.symbol"
            class="coin-logo"
            @error="handleImageError"
          />
          <div class="coin-details">
            <div class="coin-name-row">
              <span class="coin-symbol-text">{{ coin.symbol }}</span>
            </div>
            <div class="coin-meta-row">
              <span class="coin-pair">{{ coin.pair }}</span>
              <span class="coin-vol">Vol {{ formatVolume(coin.volume_24h) }}</span>
            </div>
          </div>
        </div>

        <!-- 第二列：最新价格 (30%) -->
        <div class="price-col">
          <span 
            class="price-value"
            :class="{ 'flash-green': coin.flashState === 'up', 'flash-red': coin.flashState === 'down' }"
          >
            {{ formatPrice(coin.price) }}
          </span>
        </div>

        <!-- 第三列：涨跌幅按钮 (30%) -->
        <div class="change-col">
          <div 
            class="change-btn"
            :class="{ 
              'positive': coin.change_percent > 0, 
              'negative': coin.change_percent < 0,
              'neutral': coin.change_percent === 0
            }"
          >
            {{ coin.change_percent >= 0 ? '+' : '' }}{{ coin.change_percent.toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMarketStore } from '@/stores/market';

const props = defineProps({
  limit: {
    type: Number,
    default: null // null 表示不限制
  }
});

const router = useRouter();
const marketStore = useMarketStore();

// 选项卡配置
const tabs = [
  { key: 'favorites', label: '自选' },
  { key: 'hot', label: '热门' },
  { key: 'gainers', label: '涨幅榜' },
  { key: 'losers', label: '跌幅榜' },
  { key: 'volume', label: '24h Vol' }
];

const activeTab = ref('hot');

// 是否显示排名
const showRank = computed(() => {
  return activeTab.value === 'gainers' || activeTab.value === 'losers';
});

// Mock 市场数据
const markets = ref([
  { rank: 1, symbol: 'BTC', pair: '/USDT', price: 92000, change_percent: 2.35, volume_24h: 28500000000, flashState: null },
  { rank: 2, symbol: 'ETH', pair: '/USDT', price: 3100, change_percent: 1.85, volume_24h: 15200000000, flashState: null },
  { rank: 3, symbol: 'SOL', pair: '/USDT', price: 142, change_percent: 5.20, volume_24h: 3200000000, flashState: null },
  { rank: 4, symbol: 'BNB', pair: '/USDT', price: 710, change_percent: -0.45, volume_24h: 1800000000, flashState: null },
  { rank: 5, symbol: 'DOGE', pair: '/USDT', price: 0.14, change_percent: 3.15, volume_24h: 850000000, flashState: null },
  { rank: 6, symbol: 'PEPE', pair: '/USDT', price: 0.000012, change_percent: 8.50, volume_24h: 420000000, flashState: null },
  { rank: 7, symbol: 'TRX', pair: '/USDT', price: 0.12, change_percent: -1.20, volume_24h: 380000000, flashState: null },
  { rank: 8, symbol: 'XRP', pair: '/USDT', price: 0.58, change_percent: 0.85, volume_24h: 1200000000, flashState: null },
  { rank: 9, symbol: 'ADA', pair: '/USDT', price: 0.48, change_percent: -0.65, volume_24h: 280000000, flashState: null },
  { rank: 10, symbol: 'AVAX', pair: '/USDT', price: 36.5, change_percent: 4.20, volume_24h: 520000000, flashState: null }
]);

// 价格变化监听（模拟实时更新）
let priceUpdateInterval = null;

// 根据 Tab 筛选数据
const filteredMarkets = computed(() => {
  let result = [...markets.value];
  
  switch (activeTab.value) {
    case 'favorites':
      // 自选：显示前5个
      result = result.slice(0, 5);
      break;
    case 'hot':
      // 热门：按成交量排序
      result = result.sort((a, b) => b.volume_24h - a.volume_24h);
      break;
    case 'gainers':
      // 涨幅榜：按涨幅降序
      result = result.sort((a, b) => b.change_percent - a.change_percent);
      result.forEach((coin, index) => {
        coin.rank = index + 1;
      });
      break;
    case 'losers':
      // 跌幅榜：按跌幅升序
      result = result.sort((a, b) => a.change_percent - b.change_percent);
      result.forEach((coin, index) => {
        coin.rank = index + 1;
      });
      break;
    case 'volume':
      // 24h Vol：按成交量排序
      result = result.sort((a, b) => b.volume_24h - a.volume_24h);
      break;
  }
  
  // 如果设置了 limit，只返回前 N 条
  if (props.limit && props.limit > 0) {
    result = result.slice(0, props.limit);
  }
  
  return result;
});

// 格式化价格
const formatPrice = (price) => {
  if (!price || price === 0) return '---';
  
  if (price >= 1000) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  } else if (price >= 1) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    });
  } else if (price >= 0.0001) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 4,
      maximumFractionDigits: 6
    });
  } else {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 6,
      maximumFractionDigits: 8
    });
  }
};

// 格式化成交量
const formatVolume = (volume) => {
  if (!volume || volume === 0) return '$---';
  
  if (volume >= 1000000000) {
    return '$' + (volume / 1000000000).toFixed(2) + 'B';
  } else if (volume >= 1000000) {
    return '$' + (volume / 1000000).toFixed(2) + 'M';
  } else if (volume >= 1000) {
    return '$' + (volume / 1000).toFixed(2) + 'K';
  }
  return '$' + volume.toFixed(2);
};

// 获取币种图标
const getCoinIcon = (symbol) => {
  const iconMap = {
    'BTC': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
    'ETH': 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
    'SOL': 'https://assets.coingecko.com/coins/images/4128/large/solana.png',
    'BNB': 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png',
    'DOGE': 'https://assets.coingecko.com/coins/images/5/large/dogecoin.png',
    'PEPE': 'https://assets.coingecko.com/coins/images/29850/large/pepe-token.jpeg',
    'TRX': 'https://assets.coingecko.com/coins/images/1094/large/tron-logo.png',
    'XRP': 'https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png',
    'ADA': 'https://assets.coingecko.com/coins/images/975/large/cardano.png',
    'AVAX': 'https://assets.coingecko.com/coins/images/12559/large/avalanche-avax-logo.png'
  };
  return iconMap[symbol.toUpperCase()] || 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png';
};

// 图片加载失败处理
const handleImageError = (event) => {
  event.target.style.display = 'none';
};

// 跳转到市场详情
const goToMarket = (symbol) => {
  router.push({
    path: '/market',
    query: { symbol }
  });
};

// 模拟价格更新（触发闪烁效果）
const simulatePriceUpdate = () => {
  markets.value.forEach(coin => {
    // 随机决定是否更新价格
    if (Math.random() > 0.7) {
      const oldPrice = coin.price;
      const variation = (Math.random() - 0.5) * 0.02; // ±1% 波动
      coin.price = oldPrice * (1 + variation);
      
      // 判断涨跌并触发闪烁
      if (coin.price > oldPrice) {
        coin.flashState = 'up';
      } else if (coin.price < oldPrice) {
        coin.flashState = 'down';
      }
      
      // 300ms 后恢复
      setTimeout(() => {
        coin.flashState = null;
      }, 300);
    }
  });
};

// 初始化
onMounted(() => {
  // 初始化 WebSocket（如果还没有）
  if (!marketStore.isConnected) {
    marketStore.initWebSocket();
  }
  
  // 模拟价格更新（每 3-5 秒）
  priceUpdateInterval = setInterval(() => {
    simulatePriceUpdate();
  }, 3500 + Math.random() * 2000);
});

// 清理
onUnmounted(() => {
  if (priceUpdateInterval) {
    clearInterval(priceUpdateInterval);
  }
});
</script>

<style scoped>
/* 全局强制无衬线字体 */
.markets-section {
  width: 100%;
  background-color: #0B0E11;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

.markets-section * {
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 顶部选项卡 */
.markets-tabs {
  display: flex;
  gap: 0;
  padding: 12px 16px;
  background-color: #111111;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.markets-tabs::-webkit-scrollbar {
  display: none;
}

.tab-item {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #848E9C;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  position: relative;
  margin-right: 8px;
}

.tab-item:last-child {
  margin-right: 0;
}

.tab-item.active {
  color: #FFFFFF;
  font-weight: 700;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 16px;
  right: 16px;
  height: 2px;
  background-color: #F0B90B;
  border-radius: 1px;
}

.tab-item:active {
  opacity: 0.7;
}

/* 行情列表 */
.markets-list {
  display: flex;
  flex-direction: column;
}

.market-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background-color 0.2s ease;
  min-height: 60px;
}

.market-item:active {
  background-color: rgba(255, 255, 255, 0.03);
}

/* 第一列：币种信息 (40%) */
.coin-info-col {
  flex: 0 0 40%;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rank-number {
  font-size: 12px;
  color: #848E9C;
  font-weight: 500;
  min-width: 20px;
  text-align: left;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.coin-logo {
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background-color: rgba(255, 255, 255, 0.1);
}

.coin-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.coin-name-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.coin-symbol-text {
  font-size: 15px;
  font-weight: 600;
  color: #FFFFFF;
  line-height: 1.2;
}

.coin-meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: #848E9C;
  line-height: 1.2;
}

.coin-pair {
  color: #848E9C;
}

.coin-vol {
  color: #848E9C;
}

/* 第二列：最新价格 (30%) */
.price-col {
  flex: 0 0 30%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 8px;
}

.price-value {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
}

.price-value.flash-green {
  color: #0ECB81 !important;
  animation: flashGreen 0.3s ease;
}

.price-value.flash-red {
  color: #F6465D !important;
  animation: flashRed 0.3s ease;
}

@keyframes flashGreen {
  0% {
    color: #0ECB81;
  }
  50% {
    color: #32D74B;
  }
  100% {
    color: #FFFFFF;
  }
}

@keyframes flashRed {
  0% {
    color: #F6465D;
  }
  50% {
    color: #FF6B7A;
  }
  100% {
    color: #FFFFFF;
  }
}

/* 第三列：涨跌幅按钮 (30%) */
.change-col {
  flex: 0 0 30%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-left: 8px;
}

.change-btn {
  width: 70px;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 700;
  text-align: center;
  white-space: nowrap;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  transition: all 0.2s ease;
}

.change-btn.positive {
  background-color: #0ECB81;
  color: #FFFFFF;
}

.change-btn.negative {
  background-color: #F6465D;
  color: #FFFFFF;
}

.change-btn.neutral {
  background-color: #2B3139;
  color: #848E9C;
}
</style>

