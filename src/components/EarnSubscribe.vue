<template>
  <div class="earn-subscribe-page">
    <!-- 顶部导航栏 -->
    <div class="subscribe-header">
      <van-icon name="arrow-left" size="22" color="#FFFFFF" class="header-icon" @click="handleBack" />
      <div class="header-center">
        <span class="header-title">{{ symbol }} {{ t('earn.subscribe') }}</span>
      </div>
      <div class="header-actions">
        <van-icon name="question-o" class="action-icon" @click="showHelp" />
      </div>
    </div>

    <!-- 期限选择 -->
    <div class="term-section">
      <div class="section-label">{{ t('earn.term_days') }}</div>
      <div class="term-buttons">
        <div 
          class="term-btn"
          :class="{ active: selectedTerm === 0 }"
          @click="selectedTerm = 0"
        >
          {{ t('earn.flexible') }}
        </div>
        <div 
          class="term-btn"
          :class="{ active: selectedTerm === 30 }"
          @click="selectedTerm = 30"
        >
          30{{ t('earn.days') }}
        </div>
        <div 
          class="term-btn"
          :class="{ active: selectedTerm === 90 }"
          @click="selectedTerm = 90"
        >
          90{{ t('earn.days') }}
        </div>
      </div>
    </div>

    <!-- 申购金额输入 -->
    <div class="amount-section">
      <div class="section-label">{{ t('earn.subscribe_amount') }}</div>
      <div class="amount-input-wrapper" :class="{ 'focused': isInputFocused }">
        <input
          v-model="subscribeAmount"
          type="number"
          :placeholder="t('earn.enter_amount')"
          class="amount-input-field"
          autocomplete="off"
          @input="calculateEarnings"
          @focus="isInputFocused = true"
          @blur="isInputFocused = false"
        />
        <div class="amount-actions">
          <span class="max-btn" @click="setMaxAmount">{{ t('earn.max') }}</span>
          <span class="divider-line"></span>
          <div class="coin-badge">
            <img 
              :src="getCoinIcon(symbol)" 
              :alt="symbol"
              class="coin-icon-small"
              @error="handleImageError"
            />
            <span class="coin-symbol">{{ symbol }}</span>
          </div>
        </div>
      </div>
      <div class="available-balance">
        {{ t('earn.available_balance') }}: {{ formatBalance(availableBalance) }} {{ symbol }}
      </div>
    </div>

    <!-- 数量限制 -->
    <div class="limit-section">
      <div class="section-label">{{ t('earn.quantity_limit') }}</div>
      <div class="limit-info">
        <div class="limit-item">
          <span class="limit-label">{{ t('earn.min_investment') }}:</span>
          <span class="limit-value">{{ formatAmount(productData.minAmount) }} {{ symbol }}</span>
        </div>
        <div class="limit-item">
          <span class="limit-label">{{ t('earn.available_quota') }}:</span>
          <span class="limit-value">{{ formatLargeNumber(productData.maxAmount) }} {{ symbol }}</span>
        </div>
        <div class="limit-item">
          <span class="limit-label">{{ t('earn.individual_quota') }}:</span>
          <span class="limit-value">{{ formatLargeNumber(productData.maxAmount) }} {{ symbol }}</span>
        </div>
      </div>
    </div>

    <!-- 概览（收益计算器） -->
    <div class="overview-section">
      <div class="section-label">{{ t('earn.overview') }}</div>
      <div class="overview-content">
        <div class="overview-item">
          <span class="overview-label">{{ t('earn.real_time_apy') }}</span>
          <span class="overview-value apy-large">{{ productData.apy }}%</span>
        </div>
        <div class="overview-item">
          <span class="overview-label">{{ t('earn.estimated_daily') }}</span>
          <span class="overview-value earnings-large">{{ formatEarnings(estimatedDailyEarnings) }} {{ symbol }}</span>
        </div>
      </div>
      <div class="disclaimer">
        *{{ t('earn.apy_disclaimer') }}
      </div>
    </div>

    <!-- 协议确认 -->
    <div class="agreement-section">
      <van-checkbox 
        v-model="agreedToTerms" 
        shape="square" 
        class="agreement-checkbox"
        active-color="#F0B90B"
        icon-size="16px"
      >
        <span class="agreement-text">{{ t('earn.agreement_text') }}</span>
      </van-checkbox>
    </div>

    <!-- 确认按钮 -->
    <div class="confirm-section">
      <van-button 
        block
        class="confirm-btn"
        :class="{ 'enabled': isConfirmEnabled }"
        :disabled="!isConfirmEnabled"
        @click="handleConfirm"
      >
        {{ t('earn.confirm') }}
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAssetStore } from '@/stores/assets';
import { showToast } from 'vant';

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const assetStore = useAssetStore();

// 从路由参数获取产品信息
const symbol = ref(route.query.symbol || 'USDT');
const productId = ref(route.query.id || 'usdt');

// 表单数据
const selectedTerm = ref(0);
const subscribeAmount = ref('');
const agreedToTerms = ref(false);
const isInputFocused = ref(false);

// 获取币种图标 URL
const getCoinIcon = (symbol) => {
  const iconMap = {
    'BTC': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
    'ETH': 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
    'USDT': 'https://assets.coingecko.com/coins/images/325/large/Tether.png',
    'BNB': 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png',
    'SFP': 'https://cryptologos.cc/logos/safepal-sfp-logo.png'
  };
  const upperSymbol = symbol.toUpperCase();
  // 如果 SFP 图标加载失败，使用备用地址
  if (upperSymbol === 'SFP') {
    return iconMap['SFP'] || 'https://assets.coingecko.com/coins/images/16010/large/safepal.png';
  }
  return iconMap[upperSymbol] || `https://assets.coingecko.com/coins/images/1/large/bitcoin.png`;
};

// 图片加载失败时的处理
const handleImageError = (event) => {
  event.target.style.display = 'none';
};

// Mock 产品数据（实际应该从 API 获取）
const productData = ref({
  symbol: symbol.value,
  apy: 2.07,
  bonusRate: 5,
  minAmount: 1,
  maxAmount: 100000000000,
  term: 0
});

// 可用余额（从 store 获取）
const availableBalance = computed(() => {
  if (symbol.value === 'USDT') {
    return assetStore.usdtBalance || 0;
  }
  // 其他币种从 holdings 获取
  return assetStore.getHolding(symbol.value) || 0;
});

// 计算预估每日收益
const estimatedDailyEarnings = computed(() => {
  const amount = parseFloat(subscribeAmount.value) || 0;
  if (amount === 0) return 0;
  
  const totalAPY = productData.value.apy + (productData.value.bonusRate || 0);
  const dailyRate = totalAPY / 365;
  return amount * dailyRate;
});

// 确认按钮是否可用
// 允许在余额不足时点击按钮，但在点击时弹出提示
const isConfirmEnabled = computed(() => {
  const amount = parseFloat(subscribeAmount.value) || 0;
  const hasValidAmount = amount > 0 && amount >= productData.value.minAmount;
  
  // 只要勾选了协议且金额合法，就启用按钮（余额不足会在点击时提示）
  return agreedToTerms.value && hasValidAmount;
});

// 设置最大金额
const setMaxAmount = () => {
  const max = Math.min(availableBalance.value, productData.value.maxAmount);
  subscribeAmount.value = max.toFixed(8).replace(/\.?0+$/, '');
  calculateEarnings();
};

// 计算收益（实时更新）
const calculateEarnings = () => {
  // 收益计算是响应式的，通过 computed 自动更新
};

// 格式化余额
const formatBalance = (value) => {
  if (!value || value === 0) return '0';
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  });
};

// 格式化金额
const formatAmount = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  });
};

// 格式化大数字
const formatLargeNumber = (value) => {
  if (value >= 1000000000) {
    return (value / 1000000000).toFixed(0) + 'B';
  } else if (value >= 1000000) {
    return (value / 1000000).toFixed(0) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(0) + 'K';
  }
  return value.toLocaleString('en-US');
};

// 格式化收益
const formatEarnings = (value) => {
  if (value === 0) return '0';
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 4,
    maximumFractionDigits: 8
  });
};

// 返回上一页 - 根据来源决定返回路径
const handleBack = () => {
  const { from, activeTab } = route.query;

  if (from === 'me') {
    // 如果来自"我"页面，则带参数跳回，确保 Me 页面知道该打开哪个 Tab
    router.push({ path: '/me', query: { tab: activeTab || 'earn' } });
  } else {
    // 否则返回默认的理财独立页面
    router.push('/earn');
  }
};

// 显示帮助信息
const showHelp = () => {
  showToast({
    message: t('earn.help_tooltip') || '帮助信息',
    icon: 'info',
    duration: 2000
  });
};

// 确认申购
const handleConfirm = () => {
  if (!isConfirmEnabled.value) {
    // 如果按钮禁用，显示相应提示
    const amount = parseFloat(subscribeAmount.value) || 0;
    if (!agreedToTerms.value) {
      showToast({
        message: t('earn.please_agree') || '请先同意协议',
        icon: 'fail',
        duration: 2000
      });
    } else if (amount <= 0 || amount < productData.value.minAmount) {
      showToast({
        message: t('earn.invalid_amount') || '请输入有效金额',
        icon: 'fail',
        duration: 2000
      });
    }
    return;
  }

  const amount = parseFloat(subscribeAmount.value);
  
  // 检查余额是否足够
  if (amount > availableBalance.value) {
    showToast({
      message: t('earn.insufficient_balance') || '余额不足',
      icon: 'fail',
      duration: 2000
    });
    return;
  }
  
  // TODO: 调用 API 提交申购
  showToast({
    message: t('earn.subscribe_success'),
    icon: 'success',
    duration: 2000
  });

  // 延迟返回，根据来源决定返回路径
  setTimeout(() => {
    const { from, activeTab } = route.query;
    if (from === 'me') {
      // 如果来自"我"页面，则带参数跳回，确保 Me 页面知道该打开哪个 Tab
      router.push({ path: '/me', query: { tab: activeTab || 'earn' } });
    } else {
      // 否则返回默认的理财独立页面
      router.push('/earn');
    }
  }, 2000);
};

// 初始化产品数据（根据 symbol 匹配）
onMounted(() => {
  // 这里可以根据 productId 从 API 获取真实数据
  // 目前使用 Mock 数据
  const mockProducts = {
    'sfp': { apy: 1.04, bonusRate: null, minAmount: 0.01, maxAmount: 100000000000 },
    'btc': { apy: 0.01, bonusRate: 0.25, minAmount: 0.0001, maxAmount: 100000000000 },
    'usdt': { apy: 2.07, bonusRate: 5, minAmount: 1, maxAmount: 100000000000 },
    'bnb': { apy: 0.32, bonusRate: null, minAmount: 0.01, maxAmount: 100000000000 },
    'eth': { apy: 1.5, bonusRate: 2, minAmount: 0.001, maxAmount: 100000000000 }
  };

  const product = mockProducts[productId.value.toLowerCase()] || mockProducts['usdt'];
  productData.value = {
    ...product,
    symbol: symbol.value
  };
});
</script>

<style scoped>
/* 全局强制无衬线字体 */
.earn-subscribe-page {
  background-color: #0B0E11;
  min-height: 100vh;
  padding-bottom: 100px;
  color: #FFFFFF;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

.earn-subscribe-page,
.earn-subscribe-page * {
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 顶部导航栏 */
.subscribe-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #111111;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-icon {
  font-size: 22px;
  color: #FFFFFF !important;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.header-icon:active {
  opacity: 0.7;
}

.header-center {
  flex: 1;
  text-align: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #FFFFFF;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon {
  font-size: 16px;
  color: #848E9C;
  cursor: pointer;
  transition: color 0.2s ease;
}

.action-icon:active {
  color: #FFFFFF;
}

/* 通用区块样式 */
.term-section,
.amount-section,
.limit-section,
.overview-section {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.section-label {
  font-size: 12px;
  color: #848E9C;
  margin-bottom: 12px;
  font-weight: 500;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

/* 期限选择 */
.term-buttons {
  display: flex;
  gap: 12px;
}

.term-btn {
  flex: 1;
  padding: 12px 16px;
  background-color: #1E2329;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #848E9C;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.term-btn.active {
  background-color: #F0B90B;
  color: #000000;
  border-color: #F0B90B;
}

.term-btn:active {
  opacity: 0.8;
}

/* 金额输入 - 容器化设计 */
.amount-input-wrapper {
  position: relative;
  background-color: #2B3139;
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 56px;
  justify-content: center;
}

.amount-input-wrapper.focused {
  border-color: #F0B90B;
  background-color: #2B3139;
}

.amount-input-field {
  width: 100%;
  background-color: transparent;
  border: none;
  outline: none;
  font-size: 32px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  font-variant-numeric: tabular-nums;
  padding: 0;
  margin: 0;
  line-height: 1.2;
}

.amount-input-field::placeholder {
  color: #848E9C;
  font-size: 20px;
  font-weight: 500;
}

.amount-actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-top: 4px;
  gap: 12px;
}

.max-btn {
  font-size: 13px;
  color: #F0B90B;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 12px;
  background-color: rgba(240, 185, 11, 0.15);
  border-radius: 4px;
  transition: all 0.2s ease;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  min-height: 28px;
  display: flex;
  align-items: center;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.max-btn:active {
  opacity: 0.8;
  background-color: rgba(240, 185, 11, 0.25);
  transform: scale(0.98);
}

.divider-line {
  width: 1px;
  height: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.coin-badge {
  display: flex;
  align-items: center;
  gap: 6px;
}

.coin-icon-small {
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background-color: rgba(255, 255, 255, 0.1);
  display: block;
}

.coin-symbol {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.available-balance {
  font-size: 12px;
  color: #848E9C;
  margin-top: 8px;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

/* 数量限制 */
.limit-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.limit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 8px;
}

.limit-label {
  color: #848E9C;
  font-size: 13px;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.limit-value {
  color: #EAECEF;
  font-size: 14px;
  font-weight: 700;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  font-variant-numeric: tabular-nums;
}

/* 概览 */
.overview-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.overview-label {
  font-size: 12px;
  color: #848E9C;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.overview-value {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
  font-variant-numeric: tabular-nums;
}

.overview-value.apy-large {
  font-size: 24px;
  font-weight: 700;
  color: #0ECB81;
}

.overview-value.earnings-large {
  font-size: 18px;
  font-weight: 700;
  color: #0ECB81;
}

.disclaimer {
  font-size: 11px;
  color: #848E9C;
  line-height: 1.4;
  margin-top: 8px;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

/* 协议确认 */
.agreement-section {
  padding: 20px 16px;
}

.agreement-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

:deep(.agreement-checkbox .van-checkbox__icon) {
  margin-top: 2px;
  border-color: rgba(255, 255, 255, 0.3);
  background-color: transparent;
  font-size: 16px;
}

:deep(.agreement-checkbox .van-checkbox__icon--checked) {
  background-color: #F0B90B !important;
  border-color: #F0B90B !important;
}

:deep(.agreement-checkbox .van-checkbox__icon--checked .van-icon) {
  color: #000000 !important;
  font-size: 16px;
}

:deep(.agreement-checkbox .van-checkbox__icon:not(.van-checkbox__icon--checked) .van-icon) {
  color: rgba(255, 255, 255, 0.3);
  font-size: 16px;
}

.agreement-text {
  font-size: 13px;
  color: #848E9C;
  line-height: 1.5;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

/* 确认按钮 */
.confirm-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background-color: #0B0E11;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.confirm-btn {
  height: 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  border: none;
  transition: all 0.2s ease;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.confirm-btn:not(.enabled) {
  background-color: #1E2329;
  color: #848E9C;
  cursor: not-allowed;
}

.confirm-btn.enabled {
  background-color: #F0B90B;
  color: #000000;
}

.confirm-btn.enabled:active {
  opacity: 0.85;
  transform: scale(0.98);
}
</style>

