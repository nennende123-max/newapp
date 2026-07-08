<template>
  <div class="markets-section">
    <!-- 椤堕儴閫夐」鍗?-->
    <div class="markets-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ t(tab.labelKey) }}
      </div>
    </div>

    <!-- 琛屾儏鍒楄〃 -->
    <div class="markets-list">
      <div 
        v-for="(coin, index) in filteredMarkets" 
        :key="coin.symbol"
        class="market-item"
        @click="goToMarket(coin.symbol)"
      >
        <!-- 绗竴鍒楋細甯佺淇℃伅 (40%) -->
        <div class="coin-info-col">
          <span v-if="showRank" class="rank-number">{{ coin.rank }}</span>
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

        <!-- 绗簩鍒楋細鏈€鏂颁环鏍?(30%) -->
        <div class="price-col">
          <span 
            class="price-value"
            :class="{ 'flash-green': coin.flashState === 'up', 'flash-red': coin.flashState === 'down' }"
          >
            {{ formatPrice(coin.price) }}
          </span>
        </div>

        <!-- 绗笁鍒楋細娑ㄨ穼骞呮寜閽?(30%) -->
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
import { useI18n } from 'vue-i18n';
import CryptoIcon from './CryptoIcon.vue';

const props = defineProps({
  limit: {
    type: Number,
    default: null // null 琛ㄧず涓嶉檺鍒?
  }
});

const router = useRouter();
const marketStore = useMarketStore();
const { t } = useI18n();

// 閫夐」鍗￠厤缃?
const tabs = [
  { key: 'favorites', labelKey: 'market.favorites' },
  { key: 'hot', labelKey: 'market.hot' },
  { key: 'gainers', labelKey: 'market.gainers' },
  { key: 'losers', labelKey: 'market.losers' },
  { key: 'volume', labelKey: 'market.volume' }
]

const activeTab = ref('hot');

// 鏄惁鏄剧ず鎺掑悕
const showRank = computed(() => {
  return activeTab.value === 'gainers' || activeTab.value === 'losers';
});

// Mock 甯傚満鏁版嵁
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

// 浠锋牸鍙樺寲鐩戝惉锛堟ā鎷熷疄鏃舵洿鏂帮級
let priceUpdateInterval = null;

// 鏍规嵁 Tab 绛涢€夋暟鎹?
const filteredMarkets = computed(() => {
  let result = [...markets.value];
  
  switch (activeTab.value) {
    case 'favorites':
      // 鑷€夛細鏄剧ず鍓?涓?
      result = result.slice(0, 5);
      break;
    case 'hot':
      // 鐑棬锛氭寜鎴愪氦閲忔帓搴?
      result = result.sort((a, b) => b.volume_24h - a.volume_24h);
      break;
    case 'gainers':
      // 娑ㄥ箙姒滐細鎸夋定骞呴檷搴?
      result = result.sort((a, b) => b.change_percent - a.change_percent);
      result.forEach((coin, index) => {
        coin.rank = index + 1;
      });
      break;
    case 'losers':
      // 璺屽箙姒滐細鎸夎穼骞呭崌搴?
      result = result.sort((a, b) => a.change_percent - b.change_percent);
      result.forEach((coin, index) => {
        coin.rank = index + 1;
      });
      break;
    case 'volume':
      // 24h Vol锛氭寜鎴愪氦閲忔帓搴?
      result = result.sort((a, b) => b.volume_24h - a.volume_24h);
      break;
  }
  
  // 濡傛灉璁剧疆浜?limit锛屽彧杩斿洖鍓?N 鏉?
  if (props.limit && props.limit > 0) {
    result = result.slice(0, props.limit);
  }
  
  return result;
});

// 鏍煎紡鍖栦环鏍?
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

// 鏍煎紡鍖栨垚浜ら噺
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

// 璺宠浆鍒板競鍦鸿鎯?
const goToMarket = (symbol) => {
  router.push({
    path: '/market',
    query: { symbol }
  });
};

// 妯℃嫙浠锋牸鏇存柊锛堣Е鍙戦棯鐑佹晥鏋滐級
const simulatePriceUpdate = () => {
  markets.value.forEach(coin => {
    // 闅忔満鍐冲畾鏄惁鏇存柊浠锋牸
    if (Math.random() > 0.7) {
      const oldPrice = coin.price;
      const variation = (Math.random() - 0.5) * 0.02; // 卤1% 娉㈠姩
      coin.price = oldPrice * (1 + variation);
      
      // 鍒ゆ柇娑ㄨ穼骞惰Е鍙戦棯鐑?
      if (coin.price > oldPrice) {
        coin.flashState = 'up';
      } else if (coin.price < oldPrice) {
        coin.flashState = 'down';
      }
      
      // 300ms 鍚庢仮澶?
      setTimeout(() => {
        coin.flashState = null;
      }, 300);
    }
  });
};

// 鍒濆鍖?
onMounted(() => {
  // 鍒濆鍖?WebSocket锛堝鏋滆繕娌℃湁锛?
  if (!marketStore.isConnected) {
    marketStore.initWebSocket();
  }
  
  // 妯℃嫙浠锋牸鏇存柊锛堟瘡 3-5 绉掞級
  priceUpdateInterval = setInterval(() => {
    simulatePriceUpdate();
  }, 3500 + Math.random() * 2000);
});

// 娓呯悊
onUnmounted(() => {
  if (priceUpdateInterval) {
    clearInterval(priceUpdateInterval);
  }
});
</script>

<style scoped>
/* 鍏ㄥ眬寮哄埗鏃犺‖绾垮瓧浣?*/
.markets-section {
  width: 100%;
  background-color: var(--color-bg);
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

.markets-section * {
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 椤堕儴閫夐」鍗?*/
.markets-tabs {
  display: flex;
  gap: 0;
  padding: 12px 16px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
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
  color: var(--color-text-muted);
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
  color: var(--color-text-primary);
  font-weight: 700;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 16px;
  right: 16px;
  height: 2px;
  background-color: var(--color-brand);
  border-radius: 1px;
}

.tab-item:active {
  opacity: 0.7;
}

/* 琛屾儏鍒楄〃 */
.markets-list {
  display: flex;
  flex-direction: column;
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

/* 绗竴鍒楋細甯佺淇℃伅 (40%) */
.coin-info-col {
  flex: 0 0 40%;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rank-number {
  font-size: 12px;
  color: var(--color-text-muted);
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

/* 绗簩鍒楋細鏈€鏂颁环鏍?(30%) */
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

/* 绗笁鍒楋細娑ㄨ穼骞呮寜閽?(30%) */
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
</style>

