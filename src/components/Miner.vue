<template>
  <div class="earn-page">

    <!-- 顶部资产卡片 -->
    <div class="header-card">
      <div class="card-background"></div>
      <div class="card-content">
        <div class="asset-header">
          <span class="asset-label">{{ totalAssetsLabel }}</span>
          <van-icon 
            :name="showBalance ? 'eye-o' : 'closed-eye'" 
            class="eye-icon" 
            @click="showBalance = !showBalance"
          />
        </div>
        <div class="asset-value">
          {{ showBalance ? formatAssetValue(totalAssets) : '****' }} USDT
        </div>
        <div class="earnings-row">
          <span class="earnings-label">{{ totalProfitLabel }}</span>
          <span class="earnings-value">
            {{ showBalance ? formatAssetValue(totalProfit) : '****' }} USDT
          </span>
        </div>
      </div>
    </div>

    <!-- 金刚区导航 -->
    <div class="nav-grid">
      <div 
        v-for="nav in navItems" 
        :key="nav.key"
        class="nav-item"
        @click="handleNavClick(nav.key)"
      >
        <div class="nav-icon" :style="{ background: nav.bgColor }">
          <van-icon :name="nav.icon" />
        </div>
        <span class="nav-label">{{ nav.label }}</span>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="nav-header">
      <div class="top-nav-tabs">
        <div class="nav-item" :class="{ active: currentTab === 'mining' }" @click="changeTab('mining')">
          <van-icon name="cluster" /> {{ $t('mining') }}
        </div>
        <div class="nav-item" :class="{ active: currentTab === 'battle' }" @click="changeTab('battle')">
          <van-icon name="fire" /> {{ $t('battle') }}
        </div>
      </div>
    </div>

    <!-- 预测市场 Tab -->
    <div v-if="currentTab === 'battle'" class="tab-view prediction-main">
      <!-- 分类筛选胶囊 -->
      <div class="category-pills-container">
        <div class="category-pills">
          <div
            v-for="category in categoryOptions"
            :key="category.value"
            class="category-pill"
            :class="{ active: activeCategory === category.value }"
            @click="activeCategory = category.value"
          >
            {{ category.label }}
          </div>
        </div>
      </div>

      <!-- 事件流 -->
      <div class="prediction-feed">
        <div
          v-for="market in filteredMarkets"
          :key="market.id"
          class="prediction-card"
        >
          <!-- Header: 事件元数据 -->
          <div class="prediction-header">
            <div class="prediction-category">
              <img
                v-if="market.image && market.category === 'Crypto'"
                :src="market.image"
                :alt="market.category"
                class="category-icon-small"
                @error="handleImageError"
              />
              <span class="category-text">{{ getCategoryLabel(market.category) }}</span>
            </div>
            <div class="prediction-deadline">{{ market.endDate }}</div>
          </div>

          <!-- Body: 核心问题 -->
          <div class="prediction-body">
            <img
              :src="market.image"
              :alt="market.title"
              class="prediction-image"
              @error="handleImageError"
            />
            <div class="prediction-title">{{ t(market.titleKey) }}</div>
          </div>

          <!-- Action Row: YES/NO 按钮 -->
          <div class="prediction-actions">
            <div
              class="prediction-btn btn-yes"
              @click="openBetSheet(market, 'YES')"
            >
              <span class="btn-label">YES</span>
              <span class="btn-price">{{ Math.round(market.outcomes[0].price * 100) }}¢</span>
            </div>
            <div
              class="prediction-btn btn-no"
              @click="openBetSheet(market, 'NO')"
            >
              <span class="btn-label">NO</span>
              <span class="btn-price">{{ Math.round(market.outcomes[1].price * 100) }}¢</span>
            </div>
          </div>

          <!-- Footer: 市场数据 -->
          <div class="prediction-footer">
            <div class="prediction-stats">
              <span>{{ volumeLabel }} {{ market.volume }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 云挖矿 Tab -->
    <div v-else class="tab-view mining-view">
      <div class="mining-header-text">{{ $t('inst_power') }}</div>
      
      <div v-if="loading" class="loading-box">
        <van-loading color="#FCD535" vertical>{{ $t('update_db') }}</van-loading>
      </div>
      
      <div v-else class="miner-list">
        <div class="miner-card" v-for="m in minersFromDB" :key="m.id">
          <div class="m-top">
            <div class="m-icon-box">{{ m.name[0] }}</div>
            <div class="m-title">
              <h3>{{ m.name }}</h3>
              <span class="m-badge">{{ $t('safe_sla') }}</span>
            </div>
          </div>
          <div class="m-stats">
            <div class="s-item">
              <span class="l">{{ $t('daily_rate') }}</span>
              <span class="v text-gold">{{ m.rate }}%</span>
            </div>
            <div class="s-item">
              <span class="l">{{ $t('cycle') }}</span>
              <span class="v">{{ m.days }}D</span>
            </div>
            <div class="s-item">
              <span class="l">{{ $t('min_price') }}</span>
              <span class="v">${{ m.price }}</span>
            </div>
          </div>
          <button class="m-buy-btn" @click="confirmRent(m)">{{ $t('rent_btn') }}</button>
        </div>
      </div>
    </div>

    <!-- 下单抽屉 -->
    <van-popup
      v-model:show="showBetSheet"
      position="bottom"
      round
      :style="{ height: '60%' }"
      class="bet-sheet-popup"
    >
      <div class="bet-sheet-content" v-if="selectedMarket">
        <div class="bet-sheet-header">
          <div class="bet-sheet-title">
            Buy {{ selectedSide }} - {{ selectedMarket.title }}
          </div>
          <van-icon name="cross" @click="showBetSheet = false" class="close-icon" />
        </div>

        <div class="bet-sheet-body">
          <div class="bet-input-section">
            <div class="bet-input-label">Amount (USDT)</div>
            <van-field
              v-model="betAmount"
              type="number"
              placeholder="Enter amount"
              class="bet-amount-input"
            />
            <div class="bet-quick-amounts">
              <span
                v-for="quick in quickAmounts"
                :key="quick"
                class="quick-amount-btn"
                @click="betAmount = quick.toString()"
              >
                {{ quick }}
              </span>
            </div>
          </div>

          <div class="bet-info-section">
            <div class="bet-info-row">
              <span class="bet-info-label">Avg Price</span>
              <span class="bet-info-value">{{ getSelectedPrice() }}¢</span>
            </div>
            <div class="bet-info-row" v-if="betAmount && parseFloat(betAmount) > 0">
              <span class="bet-info-label">Est. Return</span>
              <span class="bet-info-value text-green">
                ${{ calculateEstReturn().toFixed(2) }} 
                <span class="return-percent">({{ calculateEstReturnPercent().toFixed(1) }}%)</span>
              </span>
            </div>
          </div>
        </div>

        <div class="bet-sheet-footer">
          <van-button
            class="buy-now-btn"
            type="primary"
            block
            :loading="isPlacingBet"
            @click="handlePlaceBet"
          >
            Buy Now
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 规则中心弹窗 -->
    <van-popup 
      v-model:show="showRulesPopup" 
      position="bottom" 
      round
      closeable
      class="dark-rules-popup"
      :close-on-click-overlay="true"
    >
      <div class="rules-content">
        <h3 class="rules-title">{{ $t('miner.rules_center') }}</h3>
        <div class="rules-body">
          <div class="rule-section">
            <h4 class="rule-section-title">{{ $t('miner.mining_rules') }}</h4>
            <p class="rule-section-text">{{ $t('miner.mining_rules_desc') }}</p>
          </div>
          <div class="rule-section">
            <h4 class="rule-section-title">{{ $t('miner.battle_rules') }}</h4>
            <p class="rule-section-text">{{ $t('miner.battle_rules_desc') }}</p>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, onActivated, onDeactivated } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, showConfirmDialog } from 'vant';
import { useAssetStore } from '@/stores/assets';
import * as predictionApi from '@/api/prediction';

defineOptions({
  name: 'Miner'
});

// --- Router ---
const router = useRouter();

// --- i18n ---
const { t, locale } = useI18n();

// --- Pinia Store ---
const assetStore = useAssetStore();

// --- 状态变量 ---
const currentTab = ref('battle');
const loading = ref(false);
const showBalance = ref(true);
const showRulesPopup = ref(false);

// --- 预测市场相关状态 ---
const activeCategory = ref('All');
const markets = ref([]);
const showBetSheet = ref(false);
const selectedMarket = ref(null);
const selectedSide = ref('YES');
const betAmount = ref('');
const isPlacingBet = ref(false);

// 分类选项（使用国际化）
const categoryOptions = computed(() => [
  { label: t('miner.category_all'), value: 'All' },
  { label: t('miner.category_crypto'), value: 'Crypto' },
  { label: t('miner.category_macro'), value: 'Macro' },
  { label: t('miner.category_sports'), value: 'Sports' }
]);

// 快速金额选项
const quickAmounts = [10, 50, 100, 500];

// --- 资产数据 ---
// 使用 Store 中的预估总资产价值，确保与"我的"页面一致
const totalAssets = computed(() => assetStore.estimatedTotalValue);
const totalProfit = ref(342.80);

// --- 国际化标签（确保响应式更新） ---
const totalAssetsLabel = computed(() => t('miner.total_assets'));
const totalProfitLabel = computed(() => t('miner.total_profit'));
const volumeLabel = computed(() => t('miner.volume'));

// --- 下注相关状态 ---
const pendingBet = ref(null);

// --- 金刚区导航 ---
const navItems = computed(() => [
  { 
    key: 'savings', 
    label: t('miner.stable_earn'), 
    icon: 'gem-o', 
    bgColor: 'linear-gradient(135deg, #FCD535 0%, #F0B90B 100%)' 
  },
  { 
    key: 'history', 
    label: t('miner.revenue_record'), 
    icon: 'bill-o', 
    bgColor: 'linear-gradient(135deg, #F6465D 0%, #FF6B7A 100%)' 
  },
  { 
    key: 'rules', 
    label: t('miner.rules_center'), 
    icon: 'info-o', 
    bgColor: 'linear-gradient(135deg, #627EEA 0%, #8B5CF6 100%)' 
  }
]);

// --- 筛选后的市场列表 ---
const filteredMarkets = computed(() => {
  if (activeCategory.value === 'All') {
    return markets.value;
  }
  return markets.value.filter(m => m.category === activeCategory.value);
});

// --- 矿机数据 ---
const minersFromDB = ref([
  { id: 1, name: 'Antminer S21', rate: 2.5, days: 30, price: 1000 },
  { id: 2, name: 'Avalon A14', rate: 3.2, days: 60, price: 2500 }
]);

// --- 格式化资产值（支持国际化） ---
const formatAssetValue = (value) => {
  if (value >= 10000) {
    return (value / 10000).toFixed(2) + t('miner.ten_thousand');
  }
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// --- 金刚区导航点击处理 ---
const handleNavClick = (key) => {
  switch (key) {
    case 'savings':
      router.push('/earn');
      break;
    case 'history':
      router.push('/history');
      break;
    case 'rules':
      showRulesPopup.value = true;
      break;
  }
};

// --- 预测市场相关方法 ---
const loadMarkets = async () => {
  try {
    const res = await predictionApi.getMarkets(activeCategory.value);
    if (res.code === 200) {
      markets.value = res.data || [];
    }
  } catch (error) {
    console.error('Failed to load markets:', error);
    markets.value = [];
  }
};

const getCategoryLabel = (category) => {
  const labelMap = {
    'Crypto': t('miner.category_crypto'),
    'Politics': t('miner.category_politics'),
    'Sports': t('miner.category_sports'),
    'Macro': t('miner.category_macro')
  };
  return labelMap[category] || category;
};

const openBetSheet = (market, side) => {
  selectedMarket.value = market;
  selectedSide.value = side;
  betAmount.value = '';
  showBetSheet.value = true;
};

const getSelectedPrice = () => {
  if (!selectedMarket.value) return '0';
  const outcome = selectedMarket.value.outcomes.find(o => o.side === selectedSide.value);
  return outcome ? Math.round(outcome.price * 100) : '0';
};

const calculateEstReturn = () => {
  if (!selectedMarket.value || !betAmount.value || parseFloat(betAmount.value) <= 0) {
    return 0;
  }
  const amount = parseFloat(betAmount.value);
  const outcome = selectedMarket.value.outcomes.find(o => o.side === selectedSide.value);
  if (!outcome) return 0;
  
  // 计算：投入 amount USDT，以 price 的价格买入，可以获得 amount / price 份代币
  // 如果预测正确，每份代币价值 $1，总收益为 amount / price
  const shares = amount / outcome.price;
  const maxReturn = shares * 1.0;
  return maxReturn;
};

const calculateEstReturnPercent = () => {
  if (!betAmount.value || parseFloat(betAmount.value) <= 0) {
    return 0;
  }
  const amount = parseFloat(betAmount.value);
  const estReturn = calculateEstReturn();
  const profit = estReturn - amount;
  return (profit / amount) * 100;
};

const handlePlaceBet = async () => {
  if (!betAmount.value || parseFloat(betAmount.value) <= 0) {
    showToast({
      message: '请输入有效金额',
      icon: 'fail'
    });
    return;
  }

  const amount = parseFloat(betAmount.value);
  
  if (assetStore.usdtBalance < amount) {
    showToast({
      message: '余额不足',
      icon: 'fail'
    });
    return;
  }

  isPlacingBet.value = true;
  try {
    const res = await predictionApi.placePredictionBet(
      selectedMarket.value.id,
      selectedSide.value,
      amount
    );

    if (res.code === 200) {
      showBetSheet.value = false;
      showToast({
        message: '下注成功',
        icon: 'success'
      });
      
      // 刷新资产数据
      await assetStore.initData();
      
      // 刷新市场列表（可选，因为价格可能会变化）
      await loadMarkets();
    } else {
      throw new Error(res.msg || '下注失败');
    }
  } catch (error) {
    console.error('Place bet error:', error);
    showToast({
      message: error.message || '下注失败，请重试',
      icon: 'fail'
    });
  } finally {
    isPlacingBet.value = false;
  }
};

const handleImageError = (event) => {
  event.target.style.display = 'none';
};

// --- Tab 切换 ---
const changeTab = (tab) => { 
  currentTab.value = tab; 
  if (tab === 'battle') {
    loadMarkets();
  } else {
    // 模拟加载矿机数据
    loading.value = true;
    setTimeout(() => { loading.value = false; }, 800);
  }
};

// 监听分类变化，重新加载市场
watch(activeCategory, () => {
  if (currentTab.value === 'battle') {
    loadMarkets();
  }
});

// 监听语言变化，确保分类标签和格式化函数响应式更新
watch(locale, () => {
  // 语言切换时，Vue 会自动重新渲染模板中的 t() 调用
  // 由于 markets 数据中的 titleKey 不会改变，只需要确保响应式更新即可
  // 如果需要，可以强制重新加载市场数据以确保一致性
  if (currentTab.value === 'battle') {
    // 重新加载市场数据以确保翻译键正确应用
    loadMarkets();
  }
});

const confirmRent = (miner) => {
  showConfirmDialog({ 
    title: 'Confirm', 
    message: `Rent ${miner.name} for $${miner.price}?`, 
    confirmButtonColor: '#FCD535' 
  })
  .then(() => showToast('Mining Plan Activated!'))
  .catch(() => {});
};

// 初始化函数
const initializePage = () => {
  if (currentTab.value === 'battle') {
    loadMarkets();
  }
};

onMounted(() => {
  initializePage();
});

// Keep-alive 激活时
onActivated(() => {
  initializePage();
});

// Keep-alive 停用时清理
onDeactivated(() => {
  // 可以在这里清理定时器等资源
});
</script>

<style scoped>
/* 全局样式 */
.earn-page { 
  background: #0E0E0E; 
  min-height: 100vh; 
  padding: 16px; 
  color: #fff; 
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important; 
  padding-bottom: 80px; 
}

.earn-page * {
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 顶部资产卡片 */
.header-card {
  position: relative;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  min-height: 120px;
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #1C1C1E 0%, #2B3139 50%, #1C1C1E 100%);
  opacity: 0.9;
}

.card-background::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(252, 213, 53, 0.15) 0%, transparent 70%);
  border-radius: 50%;
}

.card-content {
  position: relative;
  z-index: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.asset-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.asset-label {
  font-size: 12px;
  color: #848E9C;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.eye-icon {
  font-size: 18px;
  color: #FCD535;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.eye-icon:active {
  opacity: 0.7;
}

.asset-value {
  font-size: 28px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.earnings-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.earnings-label {
  font-size: 12px;
  color: #848E9C;
}

.earnings-value {
  font-size: 16px;
  font-weight: 600;
  color: #FCD535;
  font-family: 'DIN', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
  font-variant-numeric: tabular-nums;
}

/* 金刚区导航 */
.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.nav-item:active {
  transform: scale(0.95);
}

.nav-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.nav-label {
  font-size: 11px;
  color: #EAECEF;
  font-weight: 500;
  text-align: center;
}

/* 顶部通知 */
.top-notification { 
  position: fixed; 
  top: 60px; 
  left: 50%; 
  transform: translateX(-50%); 
  background: #1C1C1E; 
  padding: 10px 20px; 
  border-radius: 30px; 
  border: 1px solid #FCD535; 
  z-index: 9999; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  box-shadow: 0 4px 20px rgba(252, 213, 53, 0.15); 
}
.notif-glow { 
  position: absolute; 
  inset: 0; 
  border-radius: 30px; 
  box-shadow: 0 0 15px rgba(252, 213, 53, 0.2); 
  pointer-events: none; 
}
.nav-slide-enter-active, .nav-slide-leave-active { 
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); 
}
.nav-slide-enter-from, .nav-slide-leave-to { 
  opacity: 0; 
  transform: translate(-50%, -20px); 
}

/* 导航头 */
.nav-header { 
  margin-bottom: 20px; 
}
.top-nav-tabs { 
  display: flex; 
  background: #1C1C1E; 
  padding: 4px; 
  border-radius: 12px; 
}
.nav-item { 
  flex: 1; 
  text-align: center; 
  padding: 12px 0; 
  font-size: 14px; 
  color: #8E8E93; 
  border-radius: 8px; 
  font-weight: 700; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  gap: 8px; 
  transition: all 0.2s; 
}
.top-nav-tabs .nav-item.active { 
  background: #2B3139; 
  color: #FCD535; 
}

/* 预测市场样式 */
.prediction-main {
  padding: 0;
}

/* 分类筛选胶囊 */
.category-pills-container {
  padding: 12px 0;
  margin-bottom: 16px;
  background: #0E0E0E;
  position: sticky;
  top: 0;
  z-index: 10;
}

.category-pills {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding: 0 16px;
}

.category-pills::-webkit-scrollbar {
  display: none;
}

.category-pill {
  padding: 8px 16px;
  background: #1C1C1E;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: #FFFFFF;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.category-pill:active {
  transform: scale(0.95);
}

.category-pill.active {
  background: #FCD535;
  color: #000000;
  font-weight: 600;
}

/* 事件流 */
.prediction-feed {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 16px 20px;
}

.prediction-card {
  background: #1C1C1E;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}

.prediction-card:active {
  background: #252A32;
  transform: scale(0.99);
}

/* Header: 事件元数据 */
.prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.prediction-category {
  display: flex;
  align-items: center;
  gap: 6px;
}

.category-icon-small {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  object-fit: cover;
}

.category-text {
  font-size: 11px;
  color: #848E9C;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.prediction-deadline {
  font-size: 11px;
  color: #848E9C;
  font-weight: 400;
}

/* Body: 核心问题 */
.prediction-body {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.prediction-image {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
}

.prediction-title {
  flex: 1;
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.4;
  letter-spacing: -0.3px;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* Action Row: YES/NO 按钮 */
.prediction-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.prediction-btn {
  flex: 1;
  height: 44px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  font-weight: 700;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.btn-yes {
  background: rgba(14, 203, 129, 0.15);
  color: #0ECB81;
}

.btn-no {
  background: rgba(246, 70, 93, 0.15);
  color: #F6465D;
}

.prediction-btn:active {
  transform: scale(0.98);
}

.btn-label {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.btn-price {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* Footer: 市场数据 */
.prediction-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.prediction-stats {
  font-size: 12px;
  color: #848E9C;
  font-variant-numeric: tabular-nums;
}

.prediction-comments {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #848E9C;
}

/* 下单抽屉样式 */
.bet-sheet-popup {
  background: #1C1C1E;
}

:deep(.bet-sheet-popup .van-popup) {
  background: #1C1C1E;
}

.bet-sheet-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.bet-sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.bet-sheet-title {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  flex: 1;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.close-icon {
  font-size: 20px;
  color: #848E9C;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-icon:active {
  color: #FFFFFF;
}

.bet-sheet-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.bet-input-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bet-input-label {
  font-size: 13px;
  color: #848E9C;
  font-weight: 500;
}

.bet-amount-input {
  background: #141414;
  border-radius: 8px;
}

:deep(.bet-amount-input .van-field__control) {
  color: #FFFFFF;
  font-size: 18px;
  font-weight: 600;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

:deep(.bet-amount-input .van-field__body) {
  background: #141414;
}

.bet-quick-amounts {
  display: flex;
  gap: 8px;
}

.quick-amount-btn {
  padding: 6px 12px;
  background: #141414;
  border-radius: 6px;
  font-size: 12px;
  color: #848E9C;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.quick-amount-btn:active {
  background: #252A32;
  color: #FCD535;
}

.bet-info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #141414;
  border-radius: 8px;
}

.bet-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bet-info-label {
  font-size: 13px;
  color: #848E9C;
}

.bet-info-value {
  font-size: 15px;
  font-weight: 600;
  color: #FFFFFF;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.text-green {
  color: #0ECB81;
}

.return-percent {
  font-size: 13px;
  opacity: 0.8;
}

.bet-sheet-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.buy-now-btn {
  height: 48px;
  background: #FCD535;
  color: #000000;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 16px;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

:deep(.buy-now-btn .van-button__content) {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.buy-now-btn:active {
  opacity: 0.85;
  transform: scale(0.98);
}

/* Mining Styles */
.mining-header-text { 
  font-size: 20px; 
  font-weight: 900; 
  margin-bottom: 20px; 
  color: #FCD535; 
  text-transform: uppercase; 
  letter-spacing: -0.5px; 
}
.loading-box { 
  display: flex; 
  justify-content: center; 
  padding: 40px; 
}
.miner-card { 
  background: #1C1C1E; 
  border-radius: 20px; 
  padding: 20px; 
  border: 1px solid #2B3139; 
  margin-bottom: 16px; 
  position: relative; 
  overflow: hidden; 
}
.m-top { 
  display: flex; 
  align-items: center; 
  gap: 15px; 
  margin-bottom: 18px; 
}
.m-icon-box { 
  width: 46px; 
  height: 46px; 
  background: #FCD535; 
  color: #000; 
  border-radius: 12px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-weight: 900; 
  font-size: 20px; 
  box-shadow: 0 4px 10px rgba(252, 213, 53, 0.2); 
}
.m-title h3 { 
  margin: 0; 
  font-size: 16px; 
  font-weight: 800; 
  color: #fff; 
  margin-bottom: 4px; 
}
.m-badge { 
  font-size: 10px; 
  background: rgba(142, 142, 147, 0.2); 
  color: #8E8E93; 
  padding: 2px 6px; 
  border-radius: 4px; 
  font-weight: 600; 
}
.m-stats { 
  display: flex; 
  justify-content: space-between; 
  background: #0E0E0E; 
  padding: 14px; 
  border-radius: 10px; 
  margin-bottom: 18px; 
}
.s-item { 
  display: flex; 
  flex-direction: column; 
  gap: 4px; 
}
.s-item .l { 
  font-size: 10px; 
  color: #5E5E5E; 
  font-weight: 700; 
  text-transform: uppercase; 
}
.s-item .v { 
  font-size: 15px; 
  font-weight: 800; 
  color: #EAECEF; 
}
.m-buy-btn { 
  width: 100%; 
  background: #FCD535; 
  border: none; 
  padding: 14px; 
  border-radius: 12px; 
  font-weight: 900; 
  font-size: 15px; 
  color: #000; 
  cursor: pointer; 
  transition: opacity 0.2s; 
}
.m-buy-btn:active { 
  opacity: 0.8; 
}

/* Menu Overlay */
.menu-overlay { 
  position: fixed; 
  inset: 0; 
  background: rgba(0,0,0,0.85); 
  backdrop-filter: blur(8px); 
  z-index: 20000; 
  display: flex; 
  align-items: flex-end; 
}
.menu-sheet { 
  width: 100%; 
  background: #1C1C1E; 
  border-radius: 24px 24px 0 0; 
  padding: 12px 20px 40px 20px; 
  box-sizing: border-box; 
  border-top: 1px solid #2B3139; 
  animation: sheetUp 0.3s cubic-bezier(0.2, 0.9, 0.3, 1); 
}
@keyframes sheetUp { 
  from { transform: translateY(100%); } 
  to { transform: translateY(0); } 
}
.menu-indicator { 
  width: 40px; 
  height: 4px; 
  background: #2B3139; 
  border-radius: 2px; 
  margin: 0 auto 20px auto; 
}
.menu-title-row { 
  display: flex; 
  justify-content: space-between; 
  font-weight: 800; 
  font-size: 18px; 
  color: #FCD535; 
  margin-bottom: 20px; 
  align-items: center; 
}
.coin-list { 
  max-height: 60vh; 
  overflow-y: auto; 
}
.coin-item { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 16px; 
  background: #2B3139; 
  border-radius: 16px; 
  margin-bottom: 10px; 
  transition: background 0.2s; 
  border: 1px solid transparent; 
}
.coin-item.active { 
  border-color: #FCD535; 
  background: rgba(252, 213, 53, 0.05); 
}
.ci-left { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
}
.ci-icon { 
  width: 32px; 
  height: 32px; 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  color: #fff; 
  font-weight: bold; 
  font-size: 14px; 
  text-shadow: 0 1px 2px rgba(0,0,0,0.3); 
}
.ci-info { 
  display: flex; 
  flex-direction: column; 
}
.ci-info .name { 
  font-weight: 800; 
  font-size: 14px; 
  color: #fff; 
}
.ci-info .full { 
  font-size: 11px; 
  color: #8E8E93; 
  font-weight: 600; 
}

/* 规则中心弹窗 - 暗黑风格 */
.dark-rules-popup {
  background-color: #1E2329 !important;
  color: #EAECEF !important;
  max-height: 60% !important;
}

/* 关闭按钮颜色 */
:deep(.dark-rules-popup .van-popup__close-icon) {
  color: #FFFFFF !important;
}

.rules-content {
  padding: 0;
}

.rules-title {
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  color: #FCD535;
  margin: 20px 0;
  padding: 0 20px;
}

.rules-body {
  padding: 0 20px 40px;
  font-size: 14px;
  line-height: 1.6;
  color: #848E9C;
}

.rule-section {
  margin-bottom: 24px;
}

.rule-section:last-child {
  margin-bottom: 0;
}

.rule-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 12px;
}

.rule-section-text {
  font-size: 14px;
  color: #848E9C;
  line-height: 1.6;
  margin: 0;
}

.text-green { color: #0ECB81 !important; } 
.text-red { color: #F6465D !important; } 
.text-gold { color: #FCD535 !important; }

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

/* 金刚区图标 */
.nav-icon :deep(.van-icon) {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
}

/* Tab 切换图标 */
.top-nav-tabs .nav-item :deep(.van-icon) {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
}

/* 眼睛图标 */
.eye-icon {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
}

/* 关闭图标 */
.close-icon {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
}
</style>

