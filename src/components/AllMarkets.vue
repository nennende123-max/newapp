<template>
  <div class="all-markets-page">
    <!-- 顶部导航栏 -->
    <div class="markets-header">
      <van-icon name="arrow-left" class="header-back" @click="router.back()" />
      <div class="search-wrapper">
        <van-icon name="search" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          :placeholder="t('market.search_placeholder')"
          autocomplete="off"
        />
        <van-icon 
          v-if="searchQuery" 
          name="clear" 
          class="clear-icon" 
          @click="searchQuery = ''"
        />
      </div>
    </div>

    <!-- 二级分类 Tabs -->
    <div class="category-tabs">
      <div 
        v-for="tab in categoryTabs" 
        :key="tab.key"
        class="category-tab"
        :class="{ active: activeCategory === tab.key }"
        @click="activeCategory = tab.key"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 可排序表头 -->
    <div class="table-header">
      <div class="header-col name-col" @click="handleSort('name')">
        <span>{{ t('market.name_vol') }}</span>
        <span class="sort-icon" v-if="sortField === 'name'">
          {{ sortOrder === 'asc' ? '▲' : '▼' }}
        </span>
      </div>
      <div class="header-col price-col" @click="handleSort('price')">
        <span>{{ t('market.last_price') }}</span>
        <span class="sort-icon" v-if="sortField === 'price'">
          {{ sortOrder === 'asc' ? '▲' : '▼' }}
        </span>
      </div>
      <div class="header-col change-col" @click="handleSort('change')">
        <span>{{ t('market.24h_chg') }}</span>
        <span class="sort-icon" v-if="sortField === 'change'">
          {{ sortOrder === 'asc' ? '▲' : '▼' }}
        </span>
      </div>
    </div>

    <!-- 行情列表 -->
    <div 
      class="markets-list"
      @scroll="handleScroll"
      ref="listContainer"
    >
      <div 
        v-for="coin in displayedMarkets" 
        :key="coin.symbol"
        class="market-item"
        @click="goToMarket(coin.symbol)"
      >
        <!-- 第一列：币种信息 (40%) -->
        <div class="coin-info-col">
          <CryptoIcon :symbol="coin.symbol" :size="40" variant="compact" />
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

      <!-- 加载更多提示 -->
      <div v-if="isLoading" class="loading-more">
        <van-loading type="spinner" size="16px" color="var(--color-brand)">加载中...</van-loading>
      </div>
      <div v-if="hasMore === false && displayedMarkets.length > 0" class="no-more">
        没有更多了
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useMarketStore } from '@/stores/market';
import { showToast } from 'vant';
import CryptoIcon from './CryptoIcon.vue';

const router = useRouter();
const { t } = useI18n();
const marketStore = useMarketStore();

// 搜索查询
const searchQuery = ref('');

// 分类 Tabs
const categoryTabs = [
  { key: 'favorites', label: '自选' },
  { key: 'spot', label: '现货' },
  { key: 'futures', label: '合约' },
  { key: 'new', label: '新币' }
];

const activeCategory = ref('spot');

// 排序状态
const sortField = ref('change'); // 'name', 'price', 'change'
const sortOrder = ref('desc'); // 'asc', 'desc'

// 分页状态
const pageSize = 20;
const currentPage = ref(1);
const isLoading = ref(false);
const hasMore = ref(true);
const listContainer = ref(null);

// Mock 市场数据（扩展版，包含更多币种）
const allMarkets = ref([
  { symbol: 'BTC', pair: '/USDT', price: 92000, change_percent: 2.35, volume_24h: 28500000000, flashState: null },
  { symbol: 'ETH', pair: '/USDT', price: 3100, change_percent: 1.85, volume_24h: 15200000000, flashState: null },
  { symbol: 'SOL', pair: '/USDT', price: 142, change_percent: 5.20, volume_24h: 3200000000, flashState: null },
  { symbol: 'BNB', pair: '/USDT', price: 710, change_percent: -0.45, volume_24h: 1800000000, flashState: null },
  { symbol: 'DOGE', pair: '/USDT', price: 0.14, change_percent: 3.15, volume_24h: 850000000, flashState: null },
  { symbol: 'PEPE', pair: '/USDT', price: 0.000012, change_percent: 8.50, volume_24h: 420000000, flashState: null },
  { symbol: 'TRX', pair: '/USDT', price: 0.12, change_percent: -1.20, volume_24h: 380000000, flashState: null },
  { symbol: 'XRP', pair: '/USDT', price: 0.58, change_percent: 0.85, volume_24h: 1200000000, flashState: null },
  { symbol: 'ADA', pair: '/USDT', price: 0.48, change_percent: -0.65, volume_24h: 280000000, flashState: null },
  { symbol: 'AVAX', pair: '/USDT', price: 36.5, change_percent: 4.20, volume_24h: 520000000, flashState: null },
  { symbol: 'MATIC', pair: '/USDT', price: 0.85, change_percent: 2.10, volume_24h: 450000000, flashState: null },
  { symbol: 'DOT', pair: '/USDT', price: 6.8, change_percent: -0.30, volume_24h: 320000000, flashState: null },
  { symbol: 'LINK', pair: '/USDT', price: 14.2, change_percent: 1.50, volume_24h: 280000000, flashState: null },
  { symbol: 'UNI', pair: '/USDT', price: 7.5, change_percent: 3.20, volume_24h: 180000000, flashState: null },
  { symbol: 'ATOM', pair: '/USDT', price: 9.2, change_percent: -0.80, volume_24h: 150000000, flashState: null },
  { symbol: 'LTC', pair: '/USDT', price: 95, change_percent: 1.20, volume_24h: 420000000, flashState: null },
  { symbol: 'BCH', pair: '/USDT', price: 420, change_percent: -0.50, volume_24h: 180000000, flashState: null },
  { symbol: 'XLM', pair: '/USDT', price: 0.12, change_percent: 0.60, volume_24h: 120000000, flashState: null },
  { symbol: 'ALGO', pair: '/USDT', price: 0.18, change_percent: 1.80, volume_24h: 95000000, flashState: null },
  { symbol: 'VET', pair: '/USDT', price: 0.03, change_percent: 2.50, volume_24h: 88000000, flashState: null },
  { symbol: 'FIL', pair: '/USDT', price: 4.8, change_percent: -1.20, volume_24h: 150000000, flashState: null },
  { symbol: 'ICP', pair: '/USDT', price: 12.5, change_percent: 0.40, volume_24h: 98000000, flashState: null },
  { symbol: 'THETA', pair: '/USDT', price: 1.2, change_percent: 1.60, volume_24h: 75000000, flashState: null },
  { symbol: 'EOS', pair: '/USDT', price: 0.75, change_percent: -0.90, volume_24h: 110000000, flashState: null },
  { symbol: 'AAVE', pair: '/USDT', price: 95, change_percent: 2.80, volume_24h: 180000000, flashState: null }
]);

// 筛选后的市场数据
const filteredMarkets = computed(() => {
  let result = [...allMarkets.value];

  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.trim().toUpperCase();
    result = result.filter(coin => 
      coin.symbol.toUpperCase().includes(query) || 
      coin.pair.toUpperCase().includes(query)
    );
  }

  // 分类过滤（这里简化处理，实际应该根据分类返回不同数据）
  switch (activeCategory.value) {
    case 'favorites':
      // 自选：返回前10个
      result = result.slice(0, 10);
      break;
    case 'spot':
      // 现货：返回所有
      break;
    case 'futures':
      // 合约：返回所有（实际应该过滤合约币种）
      break;
    case 'new':
      // 新币：返回后10个（模拟新币）
      result = result.slice(-10);
      break;
  }

  return result;
});

// 排序后的市场数据
const sortedMarkets = computed(() => {
  const result = [...filteredMarkets.value];
  
  result.sort((a, b) => {
    let aVal, bVal;
    
    switch (sortField.value) {
      case 'name':
        // 按成交量排序
        aVal = a.volume_24h;
        bVal = b.volume_24h;
        break;
      case 'price':
        aVal = a.price;
        bVal = b.price;
        break;
      case 'change':
      default:
        aVal = a.change_percent;
        bVal = b.change_percent;
        break;
    }
    
    if (sortOrder.value === 'asc') {
      return aVal - bVal;
    } else {
      return bVal - aVal;
    }
  });
  
  return result;
});

// 当前显示的市场数据（分页）
const displayedMarkets = computed(() => {
  return sortedMarkets.value.slice(0, currentPage.value * pageSize);
});

// 处理排序
const handleSort = (field) => {
  if (sortField.value === field) {
    // 切换排序方向
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    // 新的排序字段
    sortField.value = field;
    sortOrder.value = field === 'change' ? 'desc' : 'asc';
  }
  // 重置分页
  currentPage.value = 1;
  hasMore.value = true;
};

// 处理滚动（上拉加载）
const handleScroll = (event) => {
  const target = event.target;
  const scrollTop = target.scrollTop;
  const scrollHeight = target.scrollHeight;
  const clientHeight = target.clientHeight;
  
  // 距离底部 100px 时加载更多
  if (scrollHeight - scrollTop - clientHeight < 100 && !isLoading.value && hasMore.value) {
    loadMore();
  }
};

// 加载更多
const loadMore = () => {
  if (isLoading.value) return;
  
  isLoading.value = true;
  
  // 模拟网络延迟
  setTimeout(() => {
    const totalItems = sortedMarkets.value.length;
    const currentItems = displayedMarkets.value.length;
    
    if (currentItems >= totalItems) {
      hasMore.value = false;
    } else {
      currentPage.value += 1;
    }
    
    isLoading.value = false;
  }, 500);
};

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
    'AVAX': 'https://assets.coingecko.com/coins/images/12559/large/avalanche-avax-logo.png',
    'MATIC': 'https://assets.coingecko.com/coins/images/4713/large/matic-token-icon.png',
    'DOT': 'https://assets.coingecko.com/coins/images/12171/large/polkadot.png',
    'LINK': 'https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png',
    'UNI': 'https://assets.coingecko.com/coins/images/12504/large/uniswap-uni.png',
    'ATOM': 'https://assets.coingecko.com/coins/images/1481/large/cosmos_hub.png',
    'LTC': 'https://assets.coingecko.com/coins/images/2/large/litecoin.png',
    'BCH': 'https://assets.coingecko.com/coins/images/780/large/bitcoin-cash.png',
    'XLM': 'https://assets.coingecko.com/coins/images/100/large/Stellar_symbol_black_RGB.png',
    'ALGO': 'https://assets.coingecko.com/coins/images/4380/large/download.png',
    'VET': 'https://assets.coingecko.com/coins/images/116/large/VeChain-logo-2019.png',
    'FIL': 'https://assets.coingecko.com/coins/images/12817/large/filecoin.png',
    'ICP': 'https://assets.coingecko.com/coins/images/14495/large/icp.png',
    'THETA': 'https://assets.coingecko.com/coins/images/2538/large/theta-token-logo.png',
    'EOS': 'https://assets.coingecko.com/coins/images/738/large/eos-eos-logo.png',
    'AAVE': 'https://assets.coingecko.com/coins/images/12645/large/AAVE.png'
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
let priceUpdateInterval = null;

const simulatePriceUpdate = () => {
  allMarkets.value.forEach(coin => {
    if (Math.random() > 0.7) {
      const oldPrice = coin.price;
      const variation = (Math.random() - 0.5) * 0.02;
      coin.price = oldPrice * (1 + variation);
      
      if (coin.price > oldPrice) {
        coin.flashState = 'up';
      } else if (coin.price < oldPrice) {
        coin.flashState = 'down';
      }
      
      setTimeout(() => {
        coin.flashState = null;
      }, 300);
    }
  });
};

// 初始化
onMounted(() => {
  if (!marketStore.isConnected) {
    marketStore.initWebSocket();
  }
  
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
.all-markets-page {
  width: 100%;
  height: 100vh;
  background-color: var(--color-bg);
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.all-markets-page * {
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 顶部导航栏 */
.markets-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  flex-shrink: 0;
}

.header-back {
  font-size: 20px;
  color: var(--color-brand);
  cursor: pointer;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.header-back:active {
  opacity: 0.7;
}

.search-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  background-color: var(--color-surface-muted);
  border-radius: 20px;
  padding: 8px 16px;
  gap: 8px;
}

.search-icon {
  font-size: 16px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background-color: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--color-text-primary);
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

.clear-icon {
  font-size: 16px;
  color: var(--color-text-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.2s ease;
}

.clear-icon:active {
  color: var(--color-text-primary);
}

/* 二级分类 Tabs */
.category-tabs {
  display: flex;
  gap: 0;
  padding: 12px 16px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
  flex-shrink: 0;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.category-tab {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  position: relative;
  margin-right: 8px;
}

.category-tab:last-child {
  margin-right: 0;
}

.category-tab.active {
  color: var(--color-text-primary);
  font-weight: 700;
}

.category-tab.active::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 16px;
  right: 16px;
  height: 2px;
  background-color: var(--color-brand);
  border-radius: 1px;
}

.category-tab:active {
  opacity: 0.7;
}

/* 可排序表头 */
.table-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  font-size: 12px;
  color: var(--color-text-muted);
  font-weight: 500;
  flex-shrink: 0;
}

.header-col {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: color 0.2s ease;
  user-select: none;
}

.header-col:active {
  color: var(--color-text-primary);
}

.header-col.name-col {
  flex: 0 0 40%;
}

.header-col.price-col {
  flex: 0 0 30%;
  justify-content: flex-start;
  padding-left: 8px;
}

.header-col.change-col {
  flex: 0 0 30%;
  justify-content: flex-end;
  padding-left: 8px;
}

.sort-icon {
  font-size: 10px;
  color: var(--color-brand);
  line-height: 1;
}

/* 行情列表 */
.markets-list {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.market-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  cursor: pointer;
  transition: background-color 0.2s ease;
  min-height: 60px;
}

.market-item:active {
  background-color: rgb(var(--color-border-rgb) / 0.03);
}

/* 第一列：币种信息 (40%) */
.coin-info-col {
  flex: 0 0 40%;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.coin-logo {
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background-color: rgb(var(--color-border-rgb) / 0.1);
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
  color: var(--color-text-primary);
  line-height: 1.2;
}

.coin-meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: var(--color-text-muted);
  line-height: 1.2;
}

.coin-pair {
  color: var(--color-text-muted);
}

.coin-vol {
  color: var(--color-text-muted);
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
  color: var(--color-text-primary);
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
}

.price-value.flash-green {
  color: var(--color-earn) !important;
  animation: flashGreen 0.3s ease;
}

.price-value.flash-red {
  color: var(--color-loss) !important;
  animation: flashRed 0.3s ease;
}

@keyframes flashGreen {
  0% {
    color: var(--color-earn);
  }
  50% {
    color: var(--color-earn);
  }
  100% {
    color: var(--color-text-primary);
  }
}

@keyframes flashRed {
  0% {
    color: var(--color-loss);
  }
  50% {
    color: var(--color-loss);
  }
  100% {
    color: var(--color-text-primary);
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
  background-color: var(--color-earn);
  color: var(--color-text-primary);
}

.change-btn.negative {
  background-color: var(--color-loss);
  color: var(--color-text-primary);
}

.change-btn.neutral {
  background-color: var(--color-surface-muted);
  color: var(--color-text-muted);
}

/* 加载更多 */
.loading-more,
.no-more {
  padding: 20px;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 12px;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 确保 Vant 图标字体不被全局字体覆盖 */
:deep(.van-icon),
:deep([class*="van-icon"]),
.van-icon,
[class*="van-icon"] {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
  font-style: normal !important;
  font-weight: normal !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
}

/* 返回按钮图标 */
.header-back {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
}

/* 搜索图标 */
.search-icon,
.clear-icon {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
}
</style>
