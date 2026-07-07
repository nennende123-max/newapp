<template>
  <div class="home-page">

    <div class="ticker-container">
      <div class="ticker-wrapper">
        <div class="ticker-content">
          {{ tickerContent }}
        </div>
      </div>
    </div>

    <div class="scroll-content">
      <!-- 品牌展示区 -->
      <div class="brand-section">
        <div class="brand-row">
          <span class="brand-logo"></span>
          <h1 class="brand-name">TruthFi</h1>
        </div>
        <p class="brand-subtitle">{{ $t('home.slogan') }}</p>
        <div class="chain-pill">
          <span class="chain-dot"></span>
          <span class="chain-text">链上实况 · <em>0x8a...</em> 已验证</span>
        </div>
      </div>

      <!-- 平台透明度卡片 -->
      <div class="transparency-card">
        <div class="card-head">
          <span class="card-title">{{ $t('home.platform_transparency') }}</span>
          <div class="cert-badge" @touchend.prevent="showAuditToast" @click="showAuditToast">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span>CertiK Audited</span>
          </div>
        </div>

        <div class="metrics-row">
          <!-- 左：资产储备 -->
          <div class="metric-col reserve-col" @touchend.prevent="goToTreasury" @click="goToTreasury">
            <div class="metric-label">
              {{ $t('home.treasury_tvl') }}
              <van-icon name="info-o" class="info-ic" />
            </div>
            <div class="metric-value" :class="{ 'flash-green': flashTVL }">${{ formatTVL(treasuryAmount) }}</div>
            <div class="metric-change up">+{{ treasuryGrowth.toFixed(2) }}% (24h)</div>
          </div>

          <div class="metric-divider"></div>

          <!-- 右：储备健康 -->
          <div class="metric-col health-col">
            <div class="metric-label">
              储备健康
              <van-icon name="info-o" class="info-ic" />
            </div>
            <div class="metric-value health up">{{ reserveHealth.toFixed(1) }}%</div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: reserveHealth + '%' }"></div>
            </div>
            <div class="activity-label">链上活动 24H</div>
            <svg class="sparkline" viewBox="0 0 120 30" preserveAspectRatio="none">
              <defs>
                <linearGradient id="homeSpark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="var(--color-success)" stop-opacity="0.28" />
                  <stop offset="100%" stop-color="var(--color-success)" stop-opacity="0" />
                </linearGradient>
              </defs>
              <path :d="sparkAreaPath" fill="url(#homeSpark)" />
              <path :d="sparkLinePath" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
        </div>

        <!-- 两个小数据卡片 -->
        <div class="sub-cards">
          <div class="sub-card">
            <span class="sub-card-label">{{ $t('home.total_payout') }}</span>
            <span class="sub-card-value">${{ formatTVL(displayPayout) }}</span>
          </div>
          <div class="sub-card clickable" @touchend.prevent="goToChainExplorer" @click="goToChainExplorer">
            <span class="sub-card-label">链上交易</span>
            <span class="sub-card-value" :class="{ 'flash-green': flashTxns }">{{ formatNumber(displayTxns) }}</span>
          </div>
        </div>

        <!-- 底部状态说明 -->
        <div class="status-row">
          <div class="status-item">
            <van-icon name="shield-o" />
            <span>链上可验证</span>
          </div>
          <div class="status-item">
            <van-icon name="underway-o" />
            <span>15秒同步</span>
          </div>
          <div class="status-item">
            <van-icon name="records" />
            <span>持续审计</span>
          </div>
        </div>
      </div>

      <!-- 快捷操作区 -->
      <div class="quick-actions">
        <div
          class="action-btn feature-btn"
          :class="{ active: activeButton === 'deposit' }"
          @click="handleButtonClick('deposit', '/deposit')"
          @touchstart="activeButton = 'deposit'"
          @touchend.prevent="handleButtonClick('deposit', '/deposit')"
        >
          <div class="icon-square">
            <svg class="qa-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 15V4.5" />
              <path d="m7.5 9 4.5-4.5L16.5 9" />
              <path d="M5 19.5h14" />
            </svg>
          </div>
          <span>{{ $t('home_btn.deposit') }}</span>
        </div>

        <div
          class="action-btn feature-btn"
          :class="{ active: activeButton === 'withdraw' }"
          @click="handleButtonClick('withdraw', '/withdraw')"
          @touchstart="activeButton = 'withdraw'"
          @touchend.prevent="handleButtonClick('withdraw', '/withdraw')"
        >
          <div class="icon-square">
            <svg class="qa-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 4.5V15" />
              <path d="m7.5 10.5 4.5 4.5 4.5-4.5" />
              <path d="M5 19.5h14" />
            </svg>
          </div>
          <span>{{ $t('home_btn.withdraw') }}</span>
        </div>

        <div
          class="action-btn feature-btn"
          :class="{ active: activeButton === 'earn' }"
          @click="handleButtonClick('earn', '/earn')"
          @touchstart="activeButton = 'earn'"
          @touchend.prevent="handleButtonClick('earn', '/earn')"
        >
          <div class="icon-square">
            <svg class="qa-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="8" />
              <path d="M8.8 8 12 11.6 15.2 8" />
              <path d="M12 11.6V16" />
              <path d="M9.6 12.6h4.8" />
              <path d="M9.6 14.4h4.8" />
            </svg>
          </div>
          <span>{{ $t('home_btn.earn') }}</span>
        </div>

        <div
          class="action-btn feature-btn"
          :class="{ active: activeButton === 'security' }"
          @click="handleButtonClick('security', '/security-center')"
          @touchstart="activeButton = 'security'"
          @touchend.prevent="handleButtonClick('security', '/security-center')"
        >
          <div class="icon-square">
            <svg class="qa-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 3.2 19 6v5.2c0 4.4-3 7.6-7 8.6-4-1-7-4.2-7-8.6V6l7-2.8Z" />
              <path d="M12 9.3v5" />
              <path d="M9.5 11.8h5" />
            </svg>
          </div>
          <span>{{ $t('home_btn.security_center') }}</span>
        </div>
      </div>

      <!-- 市场概览 -->
      <div class="market-section">
        <div class="section-header">
          <h3>{{ $t('home.market_overview') }}</h3>
          <span class="more-btn" @touchend.prevent="goToAllMarkets" @click="goToAllMarkets">{{ $t('home.all_markets') }} ></span>
        </div>

        <div class="market-list" v-if="marketList && marketList.length > 0">
          <div
            v-for="coin in marketList"
            :key="coin.name"
            class="market-row"
            @touchend.prevent="goTrade(coin)"
            @click="goTrade(coin)"
          >
            <div class="row-left">
              <div class="coin-icon-box" :class="coin.name.toLowerCase()">{{ coin.name[0] }}</div>
              <div class="coin-meta">
                <span class="coin-name">{{ coin.name }} <span class="perp-tag">PERP</span></span>
                <span class="coin-vol">Vol {{ coin.vol }}</span>
              </div>
            </div>
            <div class="row-right">
              <span class="price">{{ coin.price }}</span>
              <div class="change-box" :class="Number(coin.change) >= 0 ? 'bg-green' : 'bg-red'">
                {{ Number(coin.change) >= 0 ? '+' : '' }}{{ Number(coin.change).toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>
        <div v-else class="market-list-placeholder">
          <van-loading color="var(--color-brand-legacy)" size="24px" vertical>Loading Market Data...</van-loading>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, onActivated, onDeactivated } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, Icon } from 'vant';
import { useMarketStore } from '@/stores/market';
import { useAssetStore } from '@/stores/assets';
import { useAssetActions } from '@/composables/useAssetActions';

defineOptions({
  name: 'Home'
});

const VanIcon = Icon;

const router = useRouter();
const { t } = useI18n();
const marketStore = useMarketStore();
const assetStore = useAssetStore();
const { openDeposit, openWithdraw } = useAssetActions();

const showAuditToast = () => {
  showToast({ message: t('home.redirecting_certik') });
};

// 跑马灯数据
const tickerData = [
  { type: 'withdraw', params: { user: '0x8a...9c', amount: '1,200', tx: '0x88...1a' } },
  { type: 'battle', params: { user: '0xbb...21', amount: '500' } },
  { type: 'treasury', params: { amount: '$240,000' } },
  { type: 'audit', params: { id: '829' } }
];

const tickerContent = computed(() => {
  const prefix = t('home.ticker.prefix');
  const messages = tickerData.map(item => t(`home.ticker.${item.type}`, item.params));
  return `${prefix} ${messages.join(' \u00A0|\u00A0 ')}`;
});

// 平台数据 - 目标值
const targetTVL = 142500000; // $142.5M
const targetPayout = 8200000; // $8.2M
const targetTxns = 45183;

const displayTVL = ref(targetTVL);
const displayPayout = ref(targetPayout);
const displayTxns = ref(targetTxns);
const tvlChange = ref(0.64);

// 资产储备 - 独立管理，模拟实时增长
const treasuryAmount = ref(142500000);
const treasuryGrowth = ref(0.64);

// 储备健康度
const reserveHealth = ref(98.7);

// 链上活动 24H 迷你折线图数据
const sparkData = [8, 12, 9, 15, 13, 18, 16, 21, 19, 24, 22, 27];

const buildSparkPoints = () => {
  const w = 120;
  const h = 30;
  const pad = 3;
  const min = Math.min(...sparkData);
  const max = Math.max(...sparkData);
  const range = max - min || 1;
  const step = w / (sparkData.length - 1);
  return sparkData.map((v, i) => {
    const x = i * step;
    const y = pad + (h - pad * 2) * (1 - (v - min) / range);
    return [x, y];
  });
};

const sparkLinePath = computed(() => {
  return buildSparkPoints().map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
});

const sparkAreaPath = computed(() => {
  const pts = buildSparkPoints();
  const line = pts.map(p => `L${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  return `M${pts[0][0].toFixed(1)} 30 ${line} L${pts[pts.length - 1][0].toFixed(1)} 30 Z`;
});

// 闪烁动画状态
const flashTVL = ref(false);
const flashTxns = ref(false);

const formatTVL = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K';
  }
  return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
};

const formatNumber = (value) => {
  return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
};

// 心跳模拟
let heartbeatInterval = null;
const startHeartbeat = () => {
  heartbeatInterval = setInterval(() => {
    const tvlVariation = (Math.random() - 0.5) * 0.002;
    const newTVL = displayTVL.value * (1 + tvlVariation);
    displayTVL.value = Math.floor(newTVL);

    flashTVL.value = true;
    setTimeout(() => { flashTVL.value = false; }, 300);

    const txnVariation = Math.floor((Math.random() - 0.5) * 120);
    displayTxns.value = Math.max(0, displayTxns.value + txnVariation);

    flashTxns.value = true;
    setTimeout(() => { flashTxns.value = false; }, 300);

    tvlChange.value = 0.64 + (Math.random() - 0.5) * 0.4;
  }, 4000 + Math.random() * 2000);
};

// 资产储备增长模拟
let treasuryInterval = null;
const startTreasuryGrowth = () => {
  treasuryInterval = setInterval(() => {
    const increase = Math.floor(Math.random() * 451) + 50;
    treasuryAmount.value += increase;

    flashTVL.value = true;
    setTimeout(() => { flashTVL.value = false; }, 300);

    treasuryGrowth.value = 0.64 + (Math.random() - 0.5) * 0.4;
  }, 3000 + Math.random() * 2000);
};

// 首页只展示 BTC / ETH / BNB
const coinSymbols = ['BTC', 'ETH', 'BNB'];

const marketList = computed(() => {
  if (!coinSymbols || !Array.isArray(coinSymbols)) {
    return [];
  }

  return coinSymbols.map(symbol => {
    if (!symbol) {
      return { name: '---', price: '---', rawPrice: 0, change: 0, vol: '---' };
    }

    const ticker = marketStore.getTicker(symbol);

    if (ticker && typeof ticker === 'object') {
      const price = (typeof ticker.price === 'number' && isFinite(ticker.price))
        ? ticker.price
        : (Number(ticker.price) || 0);
      const change = (typeof ticker.change === 'number' && isFinite(ticker.change))
        ? ticker.change
        : (Number(ticker.change) || 0);

      const formattedPrice = formatPrice(price);

      const quoteVolume = (typeof ticker.quoteVolume === 'number' && isFinite(ticker.quoteVolume))
        ? ticker.quoteVolume
        : (Number(ticker.quoteVolume) || 0);
      const formattedVol = formatVolume(quoteVolume);

      return {
        name: symbol,
        price: formattedPrice,
        rawPrice: price,
        change: change,
        vol: formattedVol
      };
    } else {
      return { name: symbol, price: '---', rawPrice: 0, change: 0, vol: '---' };
    }
  });
});

const formatPrice = (price) => {
  if (price === null || price === undefined || price === '' || price === 0) {
    return '---';
  }
  const numPrice = Number(price);
  if (isNaN(numPrice) || !isFinite(numPrice)) {
    return '---';
  }
  try {
    return numPrice.toFixed(2);
  } catch (error) {
    console.error('formatPrice error:', error);
    return '---';
  }
};

const formatVolume = (volume) => {
  if (volume === null || volume === undefined || volume === '' || volume === 0) {
    return '---';
  }
  const numVolume = Number(volume);
  if (isNaN(numVolume) || !isFinite(numVolume)) {
    return '---';
  }
  try {
    if (numVolume >= 1000000000) {
      return (numVolume / 1000000000).toFixed(2) + 'B';
    } else if (numVolume >= 1000000) {
      return (numVolume / 1000000).toFixed(2) + 'M';
    } else if (numVolume >= 1000) {
      return (numVolume / 1000).toFixed(2) + 'K';
    } else {
      return numVolume.toFixed(2);
    }
  } catch (error) {
    console.error('formatVolume error:', error);
    return '---';
  }
};

const goTrade = (coin) => {
  router.push({ path: '/market', query: { symbol: coin.name } });
};

const goToAllMarkets = () => {
  router.push({ path: '/all-markets' });
};

const goToTreasury = () => {
  router.push({ path: '/treasury' });
};

const goToChainExplorer = () => {
  router.push({ path: '/chain-explorer' });
};

const activeButton = ref(null);

const handleButtonClick = (btnType, path) => {
  activeButton.value = btnType;

  if (btnType === 'deposit') {
    openDeposit('USDT');
  } else if (btnType === 'withdraw') {
    openWithdraw('USDT');
  } else if (btnType === 'security') {
    router.push('/security-center');
  } else {
    router.push(path);
  }

  setTimeout(() => {
    activeButton.value = null;
  }, 300);
};

const clearAllIntervals = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }
  if (treasuryInterval) {
    clearInterval(treasuryInterval);
    treasuryInterval = null;
  }
};

const initializeData = () => {
  displayTVL.value = targetTVL;
  displayPayout.value = targetPayout;
  displayTxns.value = targetTxns;

  startHeartbeat();
  startTreasuryGrowth();
};

onMounted(async () => {
  await nextTick();
  setTimeout(() => {
    try {
      marketStore.initWebSocket();
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
    initializeData();
  }, 0);
});

onActivated(() => {
  if (!marketStore.isConnected || !marketStore.ws || marketStore.ws.readyState !== WebSocket.OPEN) {
    marketStore.initWebSocket();
  }
  if (!heartbeatInterval || !treasuryInterval) {
    initializeData();
  }
});

onDeactivated(() => {
  clearAllIntervals();
});

onUnmounted(() => {
  clearAllIntervals();
});
</script>

<style scoped>
.home-page {
  background: var(--color-surface-1);
  color: var(--color-text-primary);
  min-height: 100vh;
}

/* 跑马灯 */
.ticker-container {
  width: 100%;
  height: 40px;
  background: var(--color-surface-2);
  border-bottom: 1px solid var(--color-border-subtle);
  overflow: hidden;
  display: flex;
  align-items: center;
}

.ticker-wrapper {
  width: 100%;
  overflow: hidden;
}

.ticker-content {
  display: inline-block;
  white-space: nowrap;
  padding-left: 100%;
  color: var(--color-primary-hover);
  font-size: 12px;
  font-weight: 600;
  animation: marquee 25s linear infinite;
}

@keyframes marquee {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-100%, 0); }
}

.scroll-content {
  padding: 20px 16px 84px;
}

/* 品牌展示区 */
.brand-section {
  margin-bottom: 18px;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: var(--color-brand);
  box-shadow: 0 0 0 4px rgb(var(--color-primary-rgb) / 0.12);
  flex-shrink: 0;
}

.brand-name {
  margin: 0;
  font-size: 30px;
  font-weight: 900;
  line-height: 1.1;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

.brand-subtitle {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.chain-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 5px 10px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 999px;
}

.chain-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-success);
  box-shadow: 0 0 0 3px rgb(var(--color-success-rgb) / 0.15);
}

.chain-text {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.chain-text em {
  font-style: normal;
  color: var(--color-text-primary);
  font-weight: 600;
}

/* 平台透明度卡片 */
.transparency-card {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  padding: 18px;
  margin-bottom: 18px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.cert-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-success);
  background: rgb(var(--color-success-rgb) / 0.1);
  border: 1px solid rgb(var(--color-success-rgb) / 0.2);
  padding: 5px 10px;
  border-radius: 999px;
  cursor: pointer;
}

.cert-badge:active { opacity: 0.8; }

.metrics-row {
  display: flex;
  align-items: stretch;
  gap: 16px;
}

.metric-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.metric-divider {
  width: 1px;
  background: var(--color-border-subtle);
  align-self: stretch;
}

.reserve-col { cursor: pointer; }
.reserve-col:active { opacity: 0.7; }

.metric-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.info-ic {
  font-size: 12px;
  color: var(--color-text-muted);
}

.metric-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text-primary);
  font-family: 'DIN Alternate', 'Roboto', 'PingFang SC', sans-serif;
  font-variant-numeric: tabular-nums;
  line-height: 1.15;
  transition: color 0.3s ease;
}

.metric-value.health { color: var(--color-success); }

.metric-value.flash-green {
  color: var(--color-success) !important;
}

.metric-change {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 500;
}

.up { color: var(--color-success); }

/* 进度条 */
.progress-track {
  margin-top: 8px;
  height: 6px;
  width: 100%;
  background: rgb(var(--color-success-rgb) / 0.12);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-success);
  border-radius: 999px;
}

.activity-label {
  margin-top: 10px;
  font-size: 11px;
  color: var(--color-text-muted);
}

.sparkline {
  width: 100%;
  height: 30px;
  margin-top: 4px;
  display: block;
}

/* 小数据卡片 */
.sub-cards {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.sub-card {
  flex: 1;
  min-width: 0;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border-subtle);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sub-card.clickable { cursor: pointer; }
.sub-card.clickable:active { background: var(--color-surface-muted); }

.sub-card-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.sub-card-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
}

.sub-card-value.flash-green { color: var(--color-success) !important; }

/* 状态说明 */
.status-row {
  display: flex;
  align-items: center;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border-subtle);
}

.status-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-size: 11px;
  color: var(--color-text-muted);
  position: relative;
}

.status-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 12px;
  background: var(--color-border-subtle);
}

.status-item .van-icon {
  font-size: 13px;
}

/* 快捷操作区 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  padding: 16px 10px;
  margin-bottom: 18px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:active {
  transform: scale(0.95);
  opacity: 0.85;
}

.icon-square {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  transition: all 0.2s ease;
}

.icon-square .van-icon {
  font-size: 24px;
}

/* 精致线性图标（充值/提现/理财/安全中心） */
.icon-square .qa-icon {
  width: 25px;
  height: 25px;
  display: block;
  color: inherit;
}

.rotate-icon {
  transform: rotate(180deg);
}

.action-btn span {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.feature-btn.active .icon-square {
  background: rgb(var(--color-primary-rgb) / 0.14);
  border-color: var(--color-primary-border);
  color: var(--color-primary-hover);
}

.feature-btn.active span {
  color: var(--color-primary-hover);
}

/* 市场概览 */
.market-section {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  padding: 18px 0 4px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 0 18px;
}

.section-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.more-btn {
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  user-select: none;
}

.more-btn:active {
  opacity: 0.7;
  color: var(--color-primary);
}

.market-list-placeholder {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.market-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 18px;
  border-bottom: 1px solid var(--color-border-subtle);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.market-row:last-child { border-bottom: none; }

.market-row:active {
  background: var(--color-surface-1);
}

.row-left { display: flex; align-items: center; gap: 12px; }

.coin-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-surface-muted);
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: #fff;
  font-size: 15px;
  flex-shrink: 0;
}

.coin-icon-box.btc { background: var(--color-coin-btc); }
.coin-icon-box.eth { background: var(--color-coin-eth); }
.coin-icon-box.bnb { background: var(--color-accent); }

.coin-meta { display: flex; flex-direction: column; gap: 3px; }

.coin-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.perp-tag {
  font-size: 9px;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  padding: 1px 4px;
  border-radius: 4px;
  font-weight: normal;
}

.coin-vol { font-size: 12px; color: var(--color-text-muted); }

.row-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }

.price {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
}

.change-box {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 8px;
  min-width: 62px;
  text-align: center;
  color: var(--color-text-inverse);
}

.bg-green { background: var(--color-success); }
.bg-red { background: var(--color-danger); }

@media (max-width: 380px) {
  .brand-name { font-size: 27px; }
  .metric-value { font-size: 21px; }
  .metrics-row { gap: 12px; }
  .icon-square { width: 48px; height: 48px; }
}
</style>
