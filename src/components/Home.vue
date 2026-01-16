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
      <div class="hero-section">
        <h1 class="hero-title">
          TruthFi<span class="gold-square"></span>
        </h1>
        <p class="hero-subtitle">{{ $t('home.slogan') }}</p>
      </div>
  
      <div class="trust-dashboard">
        <div class="dashboard-header">
          <span class="dash-title">{{ $t('home.platform_transparency') }}</span>
          <div class="audit-badge" @click="showAuditToast">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span>{{ $t('home.audited_by_certik') }}</span>
          </div>
        </div>
        
        <div class="data-grid">
          <div class="data-item treasury-item" @click="goToTreasury">
            <div class="data-label">
              {{ $t('home.treasury_tvl') }}
              <van-icon name="arrow" size="12" class="treasury-arrow" />
            </div>
            <div class="data-value" :class="{ 'flash-green': flashTVL }">$ {{ formatTVL(treasuryAmount) }}</div>
            <div class="data-sub text-green">{{ treasuryGrowth >= 0 ? '+' : '' }}{{ treasuryGrowth.toFixed(2) }}% (24h)</div>
          </div>
          <div class="data-item">
            <div class="data-label">{{ $t('home.total_payout') }}</div>
            <div class="data-value">$ {{ formatTVL(displayPayout) }}</div>
            <div class="data-sub">{{ $t('home.since_2025') }}</div>
          </div>
          <div class="data-item clickable-item" @click="goToChainExplorer">
            <div class="data-label">
              {{ $t('home.24h_txns') }}
              <van-icon name="arrow" size="12" class="gold-arrow" />
            </div>
            <div class="data-value" :class="{ 'flash-green': flashTxns }">{{ formatNumber(displayTxns) }}</div>
            <div class="data-sub">
              {{ $t('home.on_chain') }}
              <span class="activity-tag">+12%</span>
            </div>
          </div>
        </div>
      </div>
  
      <div class="quick-actions">
        <div 
          class="action-btn feature-btn" 
          :class="{ active: activeButton === 'deposit' }"
          @click="handleButtonClick('deposit', '/deposit')"
          @touchstart="activeButton = 'deposit'"
          @touchend="setTimeout(() => { activeButton = null }, 150)"
        >
          <div class="icon-circle">
            <van-icon name="down" class="rotate-icon" />
          </div>
          <span>{{ $t('home_btn.deposit') }}</span>
        </div>
  
        <div 
          class="action-btn feature-btn" 
          :class="{ active: activeButton === 'withdraw' }"
          @click="handleButtonClick('withdraw', '/withdraw')"
          @touchstart="activeButton = 'withdraw'"
          @touchend="setTimeout(() => { activeButton = null }, 150)"
        >
          <div class="icon-circle">
            <van-icon name="envelop-o" />
          </div>
          <span>{{ $t('home_btn.withdraw') }}</span>
        </div>
  
        <div 
          class="action-btn feature-btn" 
          :class="{ active: activeButton === 'earn' }"
          @click="handleButtonClick('earn', '/earn')"
          @touchstart="activeButton = 'earn'"
          @touchend="setTimeout(() => { activeButton = null }, 150)"
        >
          <div class="icon-circle">
            <van-icon name="gold-coin-o" />
          </div>
          <span>{{ $t('home_btn.earn') }}</span>
        </div>
  
        <div 
          class="action-btn feature-btn" 
          :class="{ active: activeButton === 'security' }"
          @click="handleButtonClick('security', '/security-center')"
          @touchstart="activeButton = 'security'"
          @touchend="setTimeout(() => { activeButton = null }, 150)"
        >
          <div class="icon-circle">
            <van-icon name="shield-o" />
          </div>
          <span>安全中心</span>
        </div>
      </div>
  
      <div class="market-section">
        <div class="section-header">
          <h3>{{ $t('home.market_overview') }}</h3>
          <span class="more-btn" @click="goToAllMarkets">{{ $t('home.all_markets') }} ></span>
        </div>
        
        <div class="market-list" v-if="marketList && marketList.length > 0">
          <div 
            v-for="coin in marketList" 
            :key="coin.name" 
            class="market-row"
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
           <van-loading color="#FCD535" size="24px" vertical>Loading Market Data...</van-loading>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, onActivated } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, Icon } from 'vant';
import { useMarketStore } from '@/stores/market';
import { useAssetStore } from '@/stores/assets';

// 修复点3：定义组件名称，配合 keep-alive 使用
defineOptions({
  name: 'Home'
});

const VanIcon = Icon;
  
const router = useRouter();
const { t } = useI18n();
const marketStore = useMarketStore();
const assetStore = useAssetStore();
  
// 存储上一次的价格，用于检测波动
const previousPrices = ref({});
  
const showAuditToast = () => {
  showToast({ message: t('home.redirecting_certik') });
};

// 1. 定义原始跑马灯数据 (不包含文字，只有核心数据)
const tickerData = [
  { 
    type: 'withdraw', 
    params: { user: '0x8a...9c', amount: '1,200', tx: '0x88...1a' } 
  },
  { 
    type: 'battle', 
    params: { user: '0xbb...21', amount: '500' } 
  },
  { 
    type: 'treasury', 
    params: { amount: '$240,000' } 
  },
  { 
    type: 'audit', 
    params: { id: '829' } 
  }
];

// 2. 生成动态翻译文本 (Computed)
// 当语言切换时，这个计算属性会自动重新执行
const tickerContent = computed(() => {
  const prefix = t('home.ticker.prefix');
  
  // 遍历数据，根据类型调用对应的翻译模板
  const messages = tickerData.map(item => {
    return t(`home.ticker.${item.type}`, item.params);
  });

  // 用分隔符拼接所有消息
  return `${prefix} ${messages.join(' \u00A0|\u00A0 ')}`; 
});

// 平台数据 - 目标值
const targetTVL = 142500000; // $142.5M
const targetPayout = 8200000; // $8.2M
const targetTxns = 45201;

// 显示值（直接显示最终值，不再从0开始）
const displayTVL = ref(targetTVL);
const displayPayout = ref(targetPayout);
const displayTxns = ref(targetTxns);
const tvlChange = ref(0.88);

// 国库资产 - 独立管理，模拟实时增长
const treasuryAmount = ref(142500000); // 初始值 $142.5M
const treasuryGrowth = ref(0.88); // 24h涨幅

// 闪烁动画状态
const flashTVL = ref(false);
const flashTxns = ref(false);

// 格式化 TVL（带千分位和单位）
const formatTVL = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K';
  }
  return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
};

// 格式化数字（带千分位）
const formatNumber = (value) => {
  return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
};

// 心跳模拟 - 微小浮动（真实交易所风格）
let heartbeatInterval = null;
const startHeartbeat = () => {
  heartbeatInterval = setInterval(() => {
    // TVL 微调：在当前值基础上微小浮动（±0.1% 到 ±0.3%）
    const tvlVariation = (Math.random() - 0.5) * 0.002; // -0.1% 到 +0.1%
    const newTVL = displayTVL.value * (1 + tvlVariation);
    displayTVL.value = Math.floor(newTVL);
    
    // 触发绿色闪烁
    flashTVL.value = true;
    setTimeout(() => {
      flashTVL.value = false;
    }, 300);
    
    // 24H TXNS 微调：在当前值基础上微小浮动（±50 到 ±200）
    const txnVariation = Math.floor((Math.random() - 0.5) * 200);
    displayTxns.value = Math.max(0, displayTxns.value + txnVariation);
    
    // 触发绿色闪烁
    flashTxns.value = true;
    setTimeout(() => {
      flashTxns.value = false;
    }, 300);
    
    // TVL 涨跌幅微调：在 0.5% 到 1.5% 之间微小浮动
    tvlChange.value = 0.88 + (Math.random() - 0.5) * 0.5;
  }, 4000 + Math.random() * 2000); // 每 4-6 秒随机更新一次
};

// 国库资产增长模拟 - 每3-5秒增加50-500
let treasuryInterval = null;
const startTreasuryGrowth = () => {
  treasuryInterval = setInterval(() => {
    // 随机增加 50-500
    const increase = Math.floor(Math.random() * 451) + 50;
    treasuryAmount.value += increase;
    
    // 触发绿色闪烁
    flashTVL.value = true;
    setTimeout(() => {
      flashTVL.value = false;
    }, 300);
    
    // 24h涨幅微调：在 0.5% 到 1.5% 之间微小浮动
    treasuryGrowth.value = 0.88 + (Math.random() - 0.5) * 0.5;
  }, 3000 + Math.random() * 2000); // 每 3-5 秒更新一次
};
  
// 定义要显示的币种列表
const coinSymbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX'];
  
// 将市场数据转换为 UI 格式（从 marketStore.tickers 动态获取）
const marketList = computed(() => {
  // 防御性检查：确保 coinSymbols 存在
  if (!coinSymbols || !Array.isArray(coinSymbols)) {
    return [];
  }
  
  return coinSymbols.map(symbol => {
    // 防御性检查：确保 symbol 存在
    if (!symbol) {
      return {
        name: '---',
        price: '---',
        rawPrice: 0,
        change: 0,
        vol: '---'
      };
    }
    
    const ticker = marketStore.getTicker(symbol);
    
    if (ticker && typeof ticker === 'object') {
      // 确保价格和涨跌幅是数字类型，增强类型检查
      const price = (typeof ticker.price === 'number' && isFinite(ticker.price)) 
        ? ticker.price 
        : (Number(ticker.price) || 0);
      const change = (typeof ticker.change === 'number' && isFinite(ticker.change)) 
        ? ticker.change 
        : (Number(ticker.change) || 0);
      
      // 格式化价格显示（保留2位小数）
      const formattedPrice = formatPrice(price);
      
      // 格式化成交量显示（USDT 成交量），防御性处理 quoteVolume
      const quoteVolume = (typeof ticker.quoteVolume === 'number' && isFinite(ticker.quoteVolume))
        ? ticker.quoteVolume
        : (Number(ticker.quoteVolume) || 0);
      const formattedVol = formatVolume(quoteVolume);
      
      return {
        name: symbol,
        price: formattedPrice,
        rawPrice: price, // 保存原始价格用于波动检测
        change: change, // 确保是数字类型
        vol: formattedVol
      };
    } else {
      // 数据未加载时显示占位符（完整的默认对象）
      return {
        name: symbol,
        price: '---',
        rawPrice: 0,
        change: 0,
        vol: '---'
      };
    }
  });
});
  
// 模拟推送通知函数（检查推送开关状态）
const triggerPushNotification = (message, icon = 'bell-o') => {
  // 检查推送通知是否开启
  const pushEnabled = localStorage.getItem('user_push_enabled') !== 'false';
  
  if (pushEnabled) {
    showToast({
      message: message,
      icon: icon,
      duration: 3000,
      position: 'top'
    });
  }
};
  
// 监听价格变化，检测波动并触发推送
watch(marketList, (newList, oldList) => {
  // 只在有旧数据时进行比较（避免初始化时触发）
  if (!oldList || oldList.length === 0) {
    // 初始化 previousPrices
    newList.forEach(coin => {
      if (coin.rawPrice > 0) {
        previousPrices.value[coin.name] = coin.rawPrice;
      }
    });
    return;
  }
  
  // 检测价格波动（变化超过 2%）
  newList.forEach(coin => {
    if (coin.rawPrice > 0 && previousPrices.value[coin.name]) {
      const oldPrice = previousPrices.value[coin.name];
      const priceChange = Math.abs((coin.rawPrice - oldPrice) / oldPrice);
      
      // 如果价格变化超过 2%，触发推送通知
      if (priceChange >= 0.02) {
        const changePercent = ((coin.rawPrice - oldPrice) / oldPrice * 100).toFixed(2);
        const direction = coin.rawPrice > oldPrice ? '上涨' : '下跌';
        
        triggerPushNotification(
          `${coin.name}/USDT ${direction} ${Math.abs(changePercent)}%`,
          coin.rawPrice > oldPrice ? 'arrow-up' : 'arrow-down'
        );
      }
      
      // 更新上一次的价格
      previousPrices.value[coin.name] = coin.rawPrice;
    } else if (coin.rawPrice > 0) {
      // 首次记录价格
      previousPrices.value[coin.name] = coin.rawPrice;
    }
  });
}, { deep: true });
  
// 格式化价格（统一保留2位小数）- 增强防御性编程
const formatPrice = (price) => {
  // 类型检查：如果传入的不是有效数字，直接返回 '---'
  if (price === null || price === undefined || price === '' || price === 0) {
    return '---';
  }
  
  const numPrice = Number(price);
  if (isNaN(numPrice) || !isFinite(numPrice)) {
    return '---';
  }
  
  // 统一保留2位小数，防止 toFixed 报错
  try {
    return numPrice.toFixed(2);
  } catch (error) {
    console.error('formatPrice error:', error);
    return '---';
  }
};
  
// 格式化成交量 - 增强防御性编程
const formatVolume = (volume) => {
  // 类型检查：如果传入的不是有效数字，直接返回 '---'
  if (volume === null || volume === undefined || volume === '' || volume === 0) {
    return '---';
  }
  
  const numVolume = Number(volume);
  if (isNaN(numVolume) || !isFinite(numVolume)) {
    return '---';
  }
  
  // 防止 toFixed 报错
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
  // 跳转到行情详情页，并通过 URL 参数传递币种名称
  // 例如：/market?symbol=BTC
  router.push({ path: '/market', query: { symbol: coin.name } });
};
  
// 跳转到全部行情页
const goToAllMarkets = () => {
  router.push({ path: '/all-markets' });
};

// 跳转到国库详情页
const goToTreasury = () => {
  router.push({ path: '/treasury' });
};

// 跳转到链上监控页
const goToChainExplorer = () => {
  router.push({ path: '/chain-explorer' });
};

// 功能按钮选中状态
const activeButton = ref(null);

// 处理按钮点击
const handleButtonClick = (btnType, path) => {
  activeButton.value = btnType;
  
  if (btnType === 'security') {
    // 安全中心按钮：跳转到安全中心页面
    router.push('/security-center');
  } else {
    // 充值、提现、理财直接跳转
    router.push(path);
  }
  
  // 点击后短暂保持选中状态，然后清除
  setTimeout(() => {
    activeButton.value = null;
  }, 300);
};
  
// 初始化 WebSocket 连接和心跳模拟 - 异步初始化优化
onMounted(async () => {
  // 等待 Vue 完成首屏 DOM 挂载后再启动 WebSocket 通讯
  await nextTick();
  
  // 修复点4：使用 setTimeout 0 确保主线程不被阻塞，解决页面卡死黑屏
  setTimeout(() => {
    try {
      // 初始化 WebSocket 连接
      marketStore.initWebSocket();
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
    
    // 直接显示最终值，不再从0开始滚动
    displayTVL.value = targetTVL;
    displayPayout.value = targetPayout;
    displayTxns.value = targetTxns;
    
    // 立即启动心跳模拟（真实交易所风格）
    startHeartbeat();
    
    // 启动国库资产增长模拟
    startTreasuryGrowth();
  }, 0);
});

// 页面被激活时（Keep-Alive）
onActivated(() => {
  // 确保 WebSocket 连接是活跃的
  if (!marketStore.isConnected) {
    marketStore.initWebSocket();
  }
});

// 页面卸载时清理定时器
onUnmounted(() => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }
  if (treasuryInterval) {
    clearInterval(treasuryInterval);
  }
});
</script>
  
<style scoped>
.home-page {
  background-color: #0E0E0E;
  color: #fff;
  min-height: 100vh;
}
  
/* --- 1. 纯 CSS 跑马灯样式 (核心修改) --- */
.ticker-container {
  width: 100%;
  height: 40px;
  background: #161A1E;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  overflow: hidden; /* 隐藏超出部分 */
  display: flex;
  align-items: center;
}
  
.ticker-wrapper {
  width: 100%;
  overflow: hidden;
}
  
.ticker-content {
  display: inline-block;
  white-space: nowrap; /* 强制不换行 */
  padding-left: 100%; /* 从最右侧开始 */
  color: #FCD535;
  font-size: 12px;
  /* 应用动画：25秒滚完一圈，匀速，无限循环 */
  animation: marquee 25s linear infinite;
}
  
/* 定义滚动动画 */
@keyframes marquee {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(-100%, 0); /* 向左平移自身宽度的 100% */
  }
}
  
.scroll-content {
  padding: 20px 16px;
  /* 确保底部有足够空间给 TabBar */
  padding-bottom: 80px; 
}

/* 加载占位符样式 */
.market-list-placeholder {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
  
/* 2. Hero Section */
.hero-section {
  margin-bottom: 24px;
}
.hero-title {
  font-size: 32px; 
  font-weight: 900;
  margin: 0;
  letter-spacing: -1px;
  line-height: 1.2;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  gap: 8px;
}
.gold-square {
  width: 12px;
  height: 12px;
  background-color: #F0B90B;
  display: inline-block;
  flex-shrink: 0;
}
.hero-subtitle {
  color: #8E8E93;
  font-size: 13px;
  margin: 8px 0 0 0;
  font-weight: 400;
}
  
/* 3. 信任仪表盘 */
.trust-dashboard {
  background: #1E2329;
  border-radius: 12px; 
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #2B3139;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-left: 0; /* 确保与下方数据块严格左对齐 */
}
.dash-title {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: 0.3px;
}
.audit-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #0ECB81;
  background: rgba(14, 203, 129, 0.15);
  padding: 6px 12px;
  border-radius: 20px; 
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s ease;
}
.audit-badge:active {
  opacity: 0.8;
}
  
.data-grid {
  display: flex;
  flex-direction: row;
  gap: 16px; 
}
.data-item {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.data-label {
  font-size: 12px;
  color: #848E9C;
  margin-bottom: 8px;
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.treasury-item {
  cursor: pointer;
  transition: opacity 0.2s ease;
}
.treasury-item:active {
  opacity: 0.7;
}
.treasury-arrow {
  color: #FCD535;
  opacity: 0.6;
}
  
/* 让数据块看起来可以点击 */
.clickable-item {
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  padding: 4px; /* 增加一点内边距用于按压反馈 */
  margin: -4px; /* 抵消内边距，保持位置不变 */
}

.clickable-item:active {
  background-color: rgba(255, 255, 255, 0.05);
}

.gold-arrow {
  color: #FCD535;
  margin-left: 4px;
  opacity: 0.8;
}

/* 活跃度标签 */
.activity-tag {
  color: #0ECB81;
  background: rgba(14, 203, 129, 0.1);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 10px;
  margin-left: 4px;
}
.data-value {
  font-size: 22px; 
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'DIN Alternate', 'DIN', 'Roboto', 'Helvetica Neue', 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  margin-bottom: 4px;
  transition: color 0.3s ease;
}

/* 绿色闪烁效果 */
.data-value.flash-green {
  color: #0ECB81 !important;
  animation: flashGreen 0.3s ease;
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
.data-sub {
  font-size: 11px;
  color: #848E9C;
  font-weight: 400;
}
.text-green { 
  color: #0ECB81; 
  font-weight: 500;
}
  
/* 4. 快捷操作 - 金刚区 */
/* 金刚区容器：改为 Grid 布局 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 强制分为4列，每列等宽 */
  gap: 8px; /* 列间距 */
  padding: 0 12px; /* 整体内边距 */
  margin-bottom: 24px;
}

/* 单个按钮容器 */
.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px; /* 图标与文字的间距 */
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:active {
  transform: scale(0.95);
  opacity: 0.8;
}

/* 图标圆角矩形背景 */
.icon-circle {
  width: 56px; /* 稍微加大尺寸 */
  height: 56px;
  border-radius: 18px; /* 更加圆润的圆角 (Superellipse感) */
  display: flex;
  justify-content: center;
  align-items: center;
  background: #2B3139; /* 维持深灰色背景 */
  color: #EAECEF;
  /* 增加立体感 */
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

/* 选中/激活状态 */
.feature-btn:active .icon-circle {
  background: #363c45;
  border-color: rgba(252, 213, 53, 0.3); /* 点击时金边 */
}

/* 图标大小 */
.icon-circle .van-icon {
  font-size: 26px; /* 放大图标 */
  font-weight: 600;
}

/* 图标微调 */
.rotate-icon {
  transform: rotate(180deg); /* 向下箭头代表充值 */
}

/* 文字标签 */
.action-btn span {
  font-size: 13px; /* 微调字体 */
  color: #8E8E93; /* 次要文字颜色 */
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* 功能按钮选中状态 */
.feature-btn.active .icon-circle {
  background: #FCD535 !important;
  color: #000000 !important;
}
  
.feature-btn.active span {
  color: #FCD535;
}
  
/* 未选中状态 */
.feature-btn:not(.active) .icon-circle {
  background: #2B3139;
  color: #EAECEF;
}
  
.feature-btn:not(.active) span {
  color: #8E8E93;
}
  
/* 5. 行情列表 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}
.more-btn {
  font-size: 12px;
  color: #8E8E93;
  cursor: pointer;
  transition: opacity 0.2s ease, color 0.2s ease;
  user-select: none;
}
.more-btn:active {
  opacity: 0.7;
  color: #F0B90B;
}
  
.market-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05); 
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.market-row:active {
  background-color: rgba(255, 255, 255, 0.05);
}
.row-left { display: flex; align-items: center; gap: 12px; }
  
.coin-icon-box {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: #2B3139;
  display: flex; justify-content: center; align-items: center;
  font-weight: bold; color: #fff; font-size: 14px;
}
.coin-icon-box.btc { background: #F7931A; }
.coin-icon-box.eth { background: #627EEA; }
.coin-icon-box.bnb { background: #F3BA2F; }
/* ... 原有的 btc, eth, bnb ... */

.coin-icon-box.sol { background: #9945FF; }  /* Solana 紫色 */
.coin-icon-box.doge { background: #C2A633; } /* Doge 狗狗币黄 */
.coin-icon-box.trx { background: #FF0013; }  /* Tron 红色 */
  
.coin-meta { display: flex; flex-direction: column; gap: 2px; }
.coin-name { 
  font-size: 16px; font-weight: 600; color: #fff; 
  display: flex; align-items: center; gap: 6px;
}
.perp-tag {
  font-size: 9px; background: rgba(255,255,255,0.1); color: #8E8E93; 
  padding: 2px 4px; border-radius: 3px; font-weight: normal;
}
.coin-vol { font-size: 12px; color: #5E5E5E; }
  
.row-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.price { 
  font-size: 16px; font-weight: 600; color: #fff; 
  font-family: 'DIN Alternate', sans-serif;
}
.change-box {
  font-size: 12px; font-weight: 600;
  padding: 4px 8px; border-radius: 4px;
  min-width: 60px; text-align: center;
}
.bg-green { background: #0ECB81; color: #fff; }
.bg-red { background: #F6465D; color: #fff; }
</style>