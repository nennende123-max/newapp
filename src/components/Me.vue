<template>
    <div class="me-page">
    <!-- 顶部导航 -->
      <div class="top-nav">
        <div class="user-profile" @click="router.push('/profile')">
        <div class="avatar-circle">
          <van-icon name="manager" color="#000" />
        </div>
          <span class="username">User_8829</span>
        </div>
        <div class="top-icons">
        <van-icon 
          :name="isPrivacyMode ? 'eye-o' : 'eye'" 
          size="20" 
          class="icon-right" 
          @click="togglePrivacyMode"
        />
          <van-icon name="service-o" size="20" class="icon-right" @click="router.push('/support')" />
          <van-icon name="setting-o" size="20" class="icon-right" @click="router.push('/settings')" />
        </div>
      </div>
  
    <!-- Tab 栏 -->
    <van-tabs 
      v-model:active="activeTab" 
      background="transparent" 
      title-active-color="#fff" 
      title-inactive-color="#8E8E93" 
      line-width="20px" 
      line-height="3px" 
      color="#D4AF37" 
      :border="false" 
      class="asset-tabs"
    >
      <van-tab :title="$t('assets.overview')"></van-tab>
      <van-tab :title="$t('assets.spot')"></van-tab>
      <van-tab :title="$t('assets.earn')"></van-tab>
      </van-tabs>
  
    <!-- 资产卡片 -->
      <div class="asset-card">
      <!-- 钱包连接状态 -->
      <div v-if="!assetStore.isWalletConnected" class="wallet-status">
        <div class="wallet-status-header">
          <van-icon name="warning-o" />
          <span>{{ $t('wallet.wallet_connected') === '钱包已连接' ? '钱包未连接' : 'Wallet Not Connected' }}</span>
        </div>
        <div class="wallet-address-display">
          <span class="address-label">{{ $t('wallet.wallet_address') }}:</span>
          <span class="address-value">Not Connected</span>
        </div>
        <button class="connect-wallet-btn" @click="handleConnectWallet">
          <van-icon name="wallet-o" />
          <span>{{ $t('connect') }}</span>
        </button>
      </div>
      
      <div v-else class="wallet-status connected">
        <div class="wallet-status-header">
          <van-icon name="success" color="#0ECB81" />
          <span>{{ $t('wallet.wallet_connected') }}</span>
        </div>
        <div class="wallet-address-display">
          <span class="address-label">{{ $t('wallet.wallet_address') }}:</span>
          <span class="address-value">{{ formatAddress(assetStore.walletAddress) }}</span>
        </div>
      </div>

      <div class="total-assets-container">
        <div class="assets-label">{{ $t('wallet.est_total_value') }}</div>
        <div class="assets-main">
          <span class="total-amount">{{ displayTotalValue }}</span>
          <span class="profit-badge" v-if="assetStore.isWalletConnected">{{ displayTodayPnL }} {{ displayTodayPnLPercent }}</span>
        </div>
        <div class="legal-currency">≈ ¥ {{ displayTotalValueCNY }}</div>
      </div>
  
        <div class="action-grid">
        <div class="action-btn primary" @click="handleDeposit">
          <span class="btn-text">{{ $t('wallet.deposit') }}</span>
        </div>
        <div class="action-btn secondary" @click="handleWithdraw">
          <span class="btn-text">{{ $t('wallet.withdraw') }}</span>
        </div>
      </div>
  
      <!-- 邀请返佣 Banner -->
      <div class="referral-banner" @click="toReferral">
        <div class="referral-info">
          <div class="ref-title">{{ $t('wallet.referral_title') }}</div>
          <div class="ref-desc">{{ $t('wallet.referral_desc') }} <span class="highlight">40%</span> {{ $t('wallet.referral_rebate') }}</div>
        </div>
        <div class="referral-action">
          <span class="earned-text">{{ $t('wallet.referral_earned') }} $120.50</span>
          <van-icon name="arrow" size="14" color="#848E9C" />
        </div>
      </div>
  
      <!-- Test Reset Button - Hidden for better UX -->
      <div class="test-reset-section" style="display: none;">
        <button class="reset-test-btn" @click="handleResetTestData">
          Reset Test Data
        </button>
      </div>
    </div>

    <!-- Tab 0: Overview (概览) - 资产分析看板 -->
    <div v-if="activeTab === 0" class="overview-content">
      <!-- 账户资产分布 -->
      <div class="allocation-section">
        <div class="allocation-title">{{ $t('wallet.account_breakdown') }}</div>
        <div class="allocation-list">
          <!-- 现货账户 -->
          <div class="allocation-item">
            <div class="allocation-left">
              <div class="allocation-icon spot-icon">
                <van-icon name="balance-o" color="#000000" size="22" />
              </div>
              <div class="allocation-info">
                <span class="allocation-name">{{ $t('wallet.spot_account') }}</span>
                <span class="allocation-desc">{{ $t('assets.spot') }}</span>
              </div>
            </div>
            <div class="allocation-right">
              <span class="allocation-amount">{{ displaySpotValue }}</span>
            </div>
          </div>

          <!-- 赚币账户 -->
          <div class="allocation-item">
            <div class="allocation-left">
              <div class="allocation-icon earn-icon">
                <van-icon name="balance-o" color="#FFFFFF" size="22" />
              </div>
              <div class="allocation-info">
                <span class="allocation-name">{{ $t('wallet.earn_account') }}</span>
                <span class="allocation-desc">{{ $t('assets.earn') }}</span>
              </div>
            </div>
            <div class="allocation-right">
              <span class="allocation-amount">{{ displayEarnValue }}</span>
            </div>
          </div>

          <!-- IEO 待解锁 -->
          <div class="allocation-item">
            <div class="allocation-left">
              <div class="allocation-icon ido-icon">
                <van-icon name="lock" color="#FFFFFF" size="22" />
              </div>
              <div class="allocation-info">
                <span class="allocation-name">{{ $t('wallet.ieo_locked') }}</span>
                <span class="allocation-desc">{{ $t('assets.ido_pending_desc') || '待解锁资产' }}</span>
              </div>
            </div>
            <div class="allocation-right">
              <span class="allocation-amount">{{ displayIDOValue }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 1: Spot (现货) - 币种列表 -->
    <div v-if="activeTab === 1" class="spot-content">
      <!-- 工具栏 -->
      <div class="tools-bar">
        <div class="convert-bnb">
          <span>{{ $t('assets.convert_small') }}</span>
          <van-icon name="arrow" />
      </div>
        <div class="history-btn" @click="goToHistory">
          <van-icon name="bill-o" />
          <span>{{ $t('history.title') }}</span>
        </div>
      </div>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <div class="hide-small" @click="toggleHideSmall">
          <div class="radio-circle" :class="{ checked: hideSmallBalances }"></div>
          <span>{{ $t('assets.hide_zero') }}</span>
        </div>
        <van-field
          v-model="searchQuery"
          :placeholder="$t('assets.search_placeholder')"
          class="search-field"
          left-icon="search"
        />
      </div>
  
      <!-- 币种列表 -->
      <div class="coin-list">
        <div v-if="!assetStore.isWalletConnected && filteredAndSortedAssets.length === 0" class="empty-state">
          <van-icon name="wallet-o" size="48" color="#8E8E93" />
          <p class="empty-text">请连接钱包以查看资产</p>
        </div>
        <div 
          v-else
          class="coin-item" 
          v-for="asset in filteredAndSortedAssets" 
          :key="asset.symbol"
        >
          <div class="coin-left">
            <div class="coin-icon" :class="asset.symbol.toLowerCase()">
              <img v-if="asset.iconUrl" :src="asset.iconUrl" :alt="asset.symbol" />
              <span v-else>{{ asset.symbol[0] }}</span>
            </div>
            <div class="coin-info">
              <span class="coin-name">{{ asset.symbol }}</span>
              <span class="coin-fullname">{{ getFullName(asset.symbol) }}</span>
            </div>
          </div>
          
          <div class="coin-right">
            <span class="coin-balance">{{ displayBalance(asset.balance) }}</span>
            <span class="coin-price">{{ displayValue(asset.value) }} USDT</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Earn 标签下的内容 -->
    <div v-else-if="activeTab === 2" class="earn-content">
      <EarnList />
      </div>
    </div>
  </template>
  
  <script setup>
import { ref, computed, onMounted, watch, onActivated, onDeactivated } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import { useAssetStore } from '@/stores/assets';
import EarnList from './EarnList.vue';

defineOptions({
  name: 'Me'
});

/**
 * Asset 接口定义
 * @typedef {Object} Asset
 * @property {string} symbol - 币种符号，如 "BTC"
 * @property {string} fullName - 币种全名，如 "Bitcoin"
 * @property {string} iconUrl - 图标链接
 * @property {number} balance - 持仓数量
 * @property {number} priceUsdt - 当前单价（USDT）
 * @property {number} [value] - 总价值 = balance * priceUsdt (computed)
 */

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const assetStore = useAssetStore();

// Tab 状态 - 默认选中 Overview
const activeTab = ref(0);

// 状态管理
const isPrivacyMode = ref(false);
const hideSmallBalances = ref(false);
const searchQuery = ref('');

// 币种价格映射已移至 Store，使用全局公用的价格数据源
// 通过 assetStore.priceMap 访问

// 币种全名映射
const fullNameMap = {
  USDT: t('assets.usdt'),
  BTC: t('assets.btc'),
  BEAT: t('assets.beat'),
  ZEC: t('assets.zec'),
  AIC: t('assets.aic'),
  MEME: t('assets.meme')
};

// 从 Store 获取资产列表（包含 USDT 余额和所有持仓）
const rawAssets = computed(() => {
  const assets = []
  
  // 添加 USDT（从 usdtBalance 获取，实时响应式）
  if (assetStore.usdtBalance > 0) {
    assets.push({
      symbol: 'USDT',
      fullName: fullNameMap['USDT'],
      iconUrl: '',
      balance: assetStore.usdtBalance,
      priceUsdt: assetStore.priceMap['USDT'] || 1
    })
  }
  
  // 添加 BEAT（从 beatBalance 获取，实时响应式）
  if (assetStore.beatBalance > 0) {
    assets.push({
      symbol: 'BEAT',
      fullName: fullNameMap['BEAT'],
      iconUrl: '',
      balance: assetStore.beatBalance,
      priceUsdt: assetStore.priceMap['BEAT'] || 0
    })
  }
  
  // 添加所有持仓币种（排除 BEAT，因为已经单独处理）
  Object.keys(assetStore.holdings).forEach(symbol => {
    // 跳过 BEAT，因为已经从 beatBalance 获取
    if (symbol === 'BEAT') return
    
    const balance = assetStore.holdings[symbol]
    if (balance > 0) {
      assets.push({
        symbol,
        fullName: fullNameMap[symbol] || symbol,
        iconUrl: '',
        balance,
        priceUsdt: assetStore.priceMap[symbol] || 0
      })
    }
  })
  
  return assets
});

// 计算每个资产的总价值
const assetsWithValue = computed(() => {
  return rawAssets.value.map(asset => ({
    ...asset,
    value: asset.balance * asset.priceUsdt
  }));
});

// 智能排序：按价值从大到小
const sortedAssets = computed(() => {
  const sorted = [...assetsWithValue.value];
  sorted.sort((a, b) => b.value - a.value); // 降序排列
      return sorted;
    });
    
// 过滤和排序后的资产列表（核心逻辑）
const filteredAndSortedAssets = computed(() => {
  let filtered = sortedAssets.value;

  // 搜索过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.trim().toUpperCase();
    filtered = filtered.filter(asset => 
      asset.symbol.toUpperCase().includes(query) || 
      asset.fullName.toUpperCase().includes(query)
    );
  }

  // 隐藏小额资产
  if (hideSmallBalances.value) {
    filtered = filtered.filter(asset => asset.value >= 1);
  }

  return filtered;
});

// 总资产计算（使用 Store 中的统一计算逻辑，确保与"赚币"页面一致）
// 优先使用 totalPortfolioValue 确保数据一致性
const totalValue = computed(() => {
  return assetStore.totalPortfolioValue;
});

// 显示总资产（支持脱敏和钱包连接状态）
const displayTotalValue = computed(() => {
  // 如果钱包未连接，显示 "---"
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return totalValue.value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
});

// 显示人民币价值（支持脱敏和钱包连接状态）
const displayTotalValueCNY = computed(() => {
  // 如果钱包未连接，显示 "---"
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return (totalValue.value * 7.2).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
});

// 显示余额（支持脱敏和钱包连接状态）
const displayBalance = (balance) => {
  // 如果钱包未连接，显示 "---"
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return balance.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  });
};

// 显示价值（支持脱敏和钱包连接状态）
const displayValue = (value) => {
  // 如果钱包未连接，显示 "---"
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 格式化地址显示（截断）
const formatAddress = (address) => {
  if (!address) return 'Not Connected';
  if (address.length <= 10) return address;
  return `${address.slice(0, 4)}...${address.slice(-4)}`;
};

// 连接钱包
const handleConnectWallet = async () => {
  try {
    await assetStore.connectWallet();
    // 连接成功提示已在 store 中处理
  } catch (error) {
    console.error('Failed to connect wallet:', error);
  }
};

// 获取币种全名
const getFullName = (symbol) => {
  return fullNameMap[symbol] || symbol;
};

// 切换隐私模式
const togglePrivacyMode = () => {
  isPrivacyMode.value = !isPrivacyMode.value;
};

// 切换隐藏小额资产
const toggleHideSmall = () => {
  hideSmallBalances.value = !hideSmallBalances.value;
};

// 操作按钮 - 路由跳转
const handleDeposit = () => {
  if (!assetStore.isWalletConnected) {
    showToast({ 
      message: '请先连接钱包', 
      icon: 'fail',
      duration: 2000
    });
    return;
  }
  router.push('/deposit');
};

const handleWithdraw = () => {
  if (!assetStore.isWalletConnected) {
    showToast({ 
      message: '请先连接钱包', 
      icon: 'fail',
      duration: 2000
    });
    return;
  }
  router.push('/withdraw');
};

const handleTransfer = () => {
  if (!assetStore.isWalletConnected) {
    showToast({ message: '请先连接钱包', icon: 'fail' });
    return;
  }
  showToast({ message: '转账功能即将上线', icon: 'smile-o' });
};


// Reset test data
const handleResetTestData = () => {
  assetStore.resetTestData();
};

// 跳转到历史记录页面
const goToHistory = () => {
  router.push('/history');
};

// 切换到现货标签页
const switchToSpotTab = () => {
  activeTab.value = 1;
};

// 跳转到赚币页面
const goToMiner = () => {
  router.push('/miner');
};

// 跳转到 IEO 页面
const goToIDO = () => {
  router.push('/ido');
};

// 跳转到邀请返佣页面
const toReferral = () => {
  router.push('/referral');
};

// 处理 PnL 卡片点击（可扩展为跳转到详细页面）
const handlePnLCardClick = () => {
  // 可以跳转到详细的盈亏分析页面
  // router.push('/pnl-detail');
};

// 使用 Store 中的统一计算逻辑，确保数据一致性
const spotAccountValue = computed(() => {
  return assetStore.spotAccountValue;
});

const earnAccountValue = computed(() => {
  return assetStore.earnAccountValue;
});

const idoPendingValue = computed(() => {
  return assetStore.idoPendingValue;
});

// 今日盈亏（模拟数据）
const todayPnL = computed(() => {
  // 模拟今日盈亏：+420.50 USDT
  return 420.50;
});

const todayPnLPercent = computed(() => {
  // 模拟今日盈亏百分比：+1.25%
  return 1.25;
});

// 显示今日盈亏
const displayTodayPnL = computed(() => {
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  const sign = todayPnL.value >= 0 ? '+' : '';
  return `${sign}$${Math.abs(todayPnL.value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
});

// 显示今日盈亏百分比
const displayTodayPnLPercent = computed(() => {
  if (!assetStore.isWalletConnected) {
    return '';
  }
  if (isPrivacyMode.value) {
    return '';
  }
  const sign = todayPnLPercent.value >= 0 ? '+' : '';
  return `${sign}${Math.abs(todayPnLPercent.value).toFixed(2)}%`;
});

// 显示现货账户价值
const displaySpotValue = computed(() => {
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return spotAccountValue.value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }) + ' USDT';
});

// 显示赚币账户价值
const displayEarnValue = computed(() => {
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return earnAccountValue.value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }) + ' USDT';
});

// 显示 IEO 待解锁价值
const displayIDOValue = computed(() => {
  if (!assetStore.isWalletConnected) {
    return '---';
  }
  if (isPrivacyMode.value) {
    return '****';
  }
  return idoPendingValue.value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }) + ' USDT';
});

// 根据 query 参数自动切换 Tab 的函数
const applyTabFromQuery = () => {
  if (route.query.tab === 'earn') {
    activeTab.value = 2; // Tab 2 是"理财"Tab
  } else if (route.query.tab === 'spot') {
    activeTab.value = 1; // Tab 1 是"现货"Tab
  } else if (route.query.tab === 'overview') {
    activeTab.value = 0; // Tab 0 是"概览"Tab
  }
};

// 初始化时检查 URL 参数
onMounted(() => {
  applyTabFromQuery();
});

// 监听路由变化，防止在当前页跳转时不更新
watch(() => route.query.tab, (newTab) => {
  if (newTab) {
    applyTabFromQuery();
  }
});

// 如果使用了 keep-alive，需要在激活时也检查
onActivated(() => {
  applyTabFromQuery();
    });
    </script>
  
  <style scoped>
  /* 页面容器 */
  .me-page {
  background-color: #000000;
    min-height: 100vh;
  padding-bottom: 80px;
  color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
  }
  
  /* 1. 顶部导航 */
  .top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 16px 10px;
  }
  .user-profile {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: opacity 0.3s ease;
  }
  .user-profile:active {
    opacity: 0.7;
  }
  .avatar-circle {
    width: 28px;
    height: 28px;
  background-color: #FCD535;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .username {
    font-weight: 600;
    font-size: 16px;
  color: #FFFFFF;
  }
  .top-icons {
    display: flex;
    gap: 16px;
  color: #FFFFFF;
}
.icon-right {
  cursor: pointer;
  transition: opacity 0.3s ease;
}
.icon-right:active {
  opacity: 0.7;
  }
  
  /* 2. Tabs */
  .asset-tabs {
    margin-bottom: 10px;
  }
  :deep(.van-tab) {
    font-size: 15px;
    font-weight: 500;
    padding: 0 10px;
  }
  
  /* 3. 资产卡片 */
  .asset-card {
    padding: 0 16px 12px 16px;
    margin-bottom: 20px;
  }

/* 钱包状态显示 */
.wallet-status {
  background: #1C1C1E;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.wallet-status.connected {
  border-color: rgba(14, 203, 129, 0.3);
  background: rgba(14, 203, 129, 0.05);
}

.wallet-status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
}

.wallet-status-header .van-icon {
  font-size: 18px;
}

.wallet-address-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
}

.address-label {
  color: #8E8E93;
}

.address-value {
  color: #FFFFFF;
  font-family: 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}

.connect-wallet-btn {
  width: 100%;
  height: 44px;
  background: #FCD535;
  color: #000000;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.connect-wallet-btn:active {
  opacity: 0.8;
}

.connect-wallet-btn .van-icon {
  font-size: 18px;
  }
  /* 预估总资产容器 */
  .total-assets-container {
    margin-bottom: 12px;
  }

  .assets-label {
    color: #8E8E93;
    font-size: 12px;
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }

  .assets-main {
    display: flex;
    align-items: baseline;
    gap: 0;
    margin-bottom: 4px;
  }

  .total-amount {
    font-size: 32px;
    font-weight: bold;
    font-family: 'DIN Alternate', sans-serif;
    font-variant-numeric: tabular-nums;
    color: #FFFFFF;
    line-height: 1.2;
    display: inline-block;
  }

  .profit-badge {
    font-size: 13px;
    font-weight: 600;
    color: #0ECB81;
    margin-left: 12px;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    display: inline-block;
    vertical-align: baseline;
  }

  .legal-currency {
    color: #848E9C;
    font-size: 14px;
    margin-top: 4px;
  }
  
  /* 按钮组 */
  .action-grid {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    margin-top: 0;
  }
  .action-btn {
    flex: 1;
    height: 44px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 4px;
  border-radius: 8px;
    font-weight: 600;
    font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.action-btn:active {
  opacity: 0.8;
}
.action-btn:disabled,
.action-btn[disabled] {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* 邀请返佣 Banner */
.referral-banner {
  margin: 16px;
  padding: 16px;
  background: linear-gradient(90deg, #1C1C1E 0%, #2C2C2E 100%);
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(252, 213, 53, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.referral-banner:active {
  opacity: 0.8;
  transform: scale(0.98);
}

.referral-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ref-title {
  color: #FFFFFF;
  font-size: 15px;
  font-weight: 700;
  margin: 0;
}

.ref-desc {
  color: #848E9C;
  font-size: 12px;
  margin: 0;
}

.ref-desc .highlight {
  color: #FCD535;
  font-weight: 700;
}

.referral-action {
  display: flex;
  align-items: center;
  gap: 4px;
}

.earned-text {
  color: #FCD535;
  font-size: 13px;
  font-weight: 600;
}

/* Test Reset Section */
.test-reset-section {
  margin-top: 12px;
  text-align: center;
}
.reset-test-btn {
  background-color: rgba(246, 70, 93, 0.2);
  color: #F6465D;
  border: 1px solid rgba(246, 70, 93, 0.3);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.reset-test-btn:active {
  opacity: 0.7;
  background-color: rgba(246, 70, 93, 0.3);
}

  .primary {
  background-color: #FCD535;
    color: #1E2329;
  }
  .secondary {
  background-color: #2B3139;
    color: #EAECEF;
  }

/* Overview 内容区域 */
.overview-content {
  padding: 0 16px 20px;
}

/* 盈亏分析卡片 */
.pnl-card {
  /* 保留原有的布局属性 */
  border-radius: 12px;
  padding: 24px 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  
  /* 新的背景设置：极简线条 */
  background-color: #1C1C1E; /* 保持底色 */
  
  /* 使用纯线条 SVG (Stroke only, No fill) */
  background-image: url("data:image/svg+xml,%3Csvg width='100%25' height='100%25' viewBox='0 0 400 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 45 C40 45 60 25 100 30 C150 35 180 15 230 20 C280 25 320 5 400 10' fill='none' stroke='%230ECB81' stroke-width='2' stroke-opacity='0.3' stroke-linecap='round' /%3E%3C/svg%3E");
  
  background-repeat: no-repeat;
  background-position: bottom center;
  background-size: 100% 100%; /* 拉伸以适应卡片宽度 */
}

.pnl-card:active {
  background-color: #252A32;
  transform: scale(0.98);
}

.pnl-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.pnl-label {
  font-size: 13px;
  color: #8E8E93;
  font-weight: 500;
}

.pnl-content {
  position: relative;
  z-index: 1;
}

.pnl-value {
  display: flex;
  align-items: baseline;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.pnl-value.positive .pnl-amount {
  color: #0ECB81;
}

.pnl-value.positive .pnl-percentage {
  color: #0ECB81;
}

.pnl-amount {
  font-size: 28px;
  font-weight: 700;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  font-variant-numeric: tabular-nums;
}

.pnl-percentage {
  font-size: 16px;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  font-variant-numeric: tabular-nums;
}

/* 账户资产分布 */
.allocation-section {
  margin-top: 8px;
}

.allocation-title {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 12px;
  padding: 0 4px;
}

.allocation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.allocation-item {
  background-color: #1C1C1E;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.allocation-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.05) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.allocation-item:active {
  background-color: #252A32;
  opacity: 0.85;
  transform: scale(0.98);
  border-color: rgba(212, 175, 55, 0.2);
}

.allocation-item:active::before {
  opacity: 1;
}

.allocation-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.allocation-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.allocation-icon.spot-icon {
  background: linear-gradient(135deg, #FCD535 0%, #F7B500 100%);
  box-shadow: 0 2px 8px rgba(252, 213, 53, 0.2), inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

/* 确保 Vant 图标字体正确加载 */
.allocation-icon :deep(.van-icon),
.allocation-icon :deep([class*="van-icon"]) {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
  font-style: normal !important;
  font-weight: normal !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
}

.allocation-icon.earn-icon {
  background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2), inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.allocation-icon.ido-icon {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF4757 100%);
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2), inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.allocation-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.allocation-name {
  font-size: 15px;
  font-weight: 600;
  color: #FFFFFF;
}

.allocation-desc {
  font-size: 12px;
  color: #8E8E93;
}

.allocation-right {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px; /* 确保与左侧图标高度对齐 */
  flex: 1;
  justify-content: flex-end;
}

.allocation-amount {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  font-variant-numeric: tabular-nums;
}


/* Spot 内容区域 */
.spot-content {
  padding: 0;
}

/* Earn 内容区域 */
.earn-content {
  padding: 0;
  margin-top: 0;
  width: 100%;
  display: block;
}
:deep(.van-empty) {
  color: #8E8E93;
}
:deep(.van-empty__description) {
  color: #8E8E93;
  }
  
  /* 4. 工具栏 */
  .tools-bar {
    padding: 0 16px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }
  .convert-bnb {
    background-color: #1C1C1E;
    padding: 10px 12px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #EAECEF;
    font-size: 13px;
    flex: 1;
  }
  .history-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #FCD535;
    cursor: pointer;
    padding: 10px 14px;
    background-color: rgba(252, 213, 53, 0.1);
    border-radius: 8px;
    transition: all 0.2s ease;
    white-space: nowrap;
  }
  .history-btn:active,
  .referral-btn:active {
    opacity: 0.8;
    background-color: rgba(252, 213, 53, 0.15);
  }
  .history-btn .van-icon,
  .referral-btn .van-icon {
    font-size: 16px;
  }
  
  .referral-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #FCD535;
    cursor: pointer;
    padding: 10px 14px;
    background-color: rgba(252, 213, 53, 0.1);
    border-radius: 8px;
    transition: all 0.2s ease;
    white-space: nowrap;
  }
  
  /* 5. 搜索栏 */
  .search-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    margin-bottom: 16px;
  gap: 12px;
  }
  .hide-small {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #8E8E93;
    font-size: 13px;
  cursor: pointer;
  transition: opacity 0.3s ease;
}
.hide-small:active {
  opacity: 0.7;
  }
  .radio-circle {
  width: 16px;
  height: 16px;
  border: 2px solid #5E5E5E;
    border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
}
.radio-circle.checked {
  border-color: #FCD535;
  background-color: #FCD535;
}
.radio-circle.checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  background-color: #1E2329;
    border-radius: 50%;
  }
.search-field {
  flex: 1;
  background: #1C1C1E;
  border-radius: 8px;
  height: 40px;
}
:deep(.search-field .van-field__control) {
  color: #FFFFFF;
  font-size: 14px;
  background: transparent;
}
:deep(.search-field .van-field__control::placeholder) {
  color: #8E8E93;
}
:deep(.search-field .van-field__left-icon) {
  color: #8E8E93;
  }
  
  /* 6. 列表样式 */
  .coin-list {
    display: flex;
    flex-direction: column;
  }

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state .van-icon {
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  color: #8E8E93;
  font-size: 14px;
  margin: 0;
  }
  .coin-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
  border-bottom: 1px solid #141414;
  transition: background-color 0.2s ease;
}
.coin-item:active {
  background-color: rgba(255, 255, 255, 0.05);
  }
  .coin-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .coin-icon {
  width: 40px;
  height: 40px;
    border-radius: 50%;
  background-color: #2B3139;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
  font-size: 16px;
  color: #FFFFFF;
  overflow: hidden;
}
.coin-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
/* 币种图标颜色 */
  .coin-icon.usdt { background: #26A17B; }
  .coin-icon.btc { background: #F7931A; }
.coin-icon.beat { background: #FF6B6B; }
.coin-icon.zec { background: #ECB244; }
.coin-icon.aic { background: #4ECDC4; }
.coin-icon.meme { background: #95E1D3; }
  
  .coin-info {
    display: flex;
    flex-direction: column;
  gap: 4px;
  }
  .coin-name {
    font-size: 16px;
    font-weight: 500;
    color: #EAECEF;
  font-variant-numeric: tabular-nums;
  }
  .coin-fullname {
    font-size: 12px;
  color: #8E8E93;
  }
  .coin-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  gap: 4px;
  }
  .coin-balance {
    font-size: 16px;
    color: #EAECEF;
    font-weight: 500;
  font-family: 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  }
  .coin-price {
    font-size: 12px;
  color: #8E8E93;
  font-family: 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  }
  </style>

