<template>
  <div class="earn-list-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      :title="t('earn.title')"
      left-arrow
      @click-left="router.back()"
      fixed
      placeholder
      safe-area-inset-top
      :border="false"
      class="custom-nav-bar"
    />

    <div class="tools-section">
      <van-field
        v-model="searchQuery"
        :placeholder="t('earn.search_placeholder')"
        class="search-field"
        left-icon="search"
        clearable
      />
      <div class="search-actions">
        <van-icon name="sort" class="action-icon" @click="handleSort" />
        <van-icon name="clock" class="action-icon" @click="handleHistory" />
      </div>
    </div>

    <van-tabs 
      :key="tabsKey"
      v-model:active="activeTab" 
      background="transparent" 
      title-active-color="#F0B90B" 
      title-inactive-color="#848E9C" 
      line-width="30px" 
      line-height="2px" 
      color="#F0B90B" 
      :border="false"
      class="earn-tabs"
    >
      <van-tab :title="t('earn.tab.hot')"></van-tab>
      <van-tab :title="t('earn.tab.safe')"></van-tab>
      <van-tab :title="t('earn.tab.high_yield')"></van-tab>
    </van-tabs>

    <div class="products-list">
      <div 
        v-for="product in filteredProducts" 
        :key="product.id"
        class="product-card"
      >
        <div class="product-header">
          <div class="coin-info">
            <img 
              :src="getCoinIcon(product.symbol)" 
              :alt="product.symbol"
              class="coin-icon"
              @error="handleImageError"
            />
            <div class="coin-name-group">
              <span class="coin-name">{{ product.symbol }}</span>
              <span v-if="product.bonusRate" class="bonus-rate">+{{ product.bonusRate }}%</span>
            </div>
          </div>
          <div v-if="product.tieredRate" class="header-badge">
            {{ t('earn.tiered_annual_rate') }}
          </div>
        </div>

        <div class="product-body">
          <div class="apy-main">
            <span class="apy-value">{{ product.apy }}%</span>
            <span v-if="product.bonusRate" class="apy-bonus">+{{ product.bonusRate }}%</span>
          </div>
          <div class="apy-label">{{ t('earn.reference_annual') }}</div>
        </div>

        <div class="product-footer">
          <div class="term-tag">
            {{ product.term === 0 ? t('earn.flexible') : `${product.term}${t('earn.days')}` }}
          </div>
          <van-button 
            class="subscribe-btn"
            @click.stop="goToSubscribe(product)"
          >
            {{ t('earn.subscribe') }}
          </van-button>
        </div>
      </div>

      <div v-if="filteredProducts.length === 0" class="empty-state">
        <van-empty :description="t('earn.no_products')" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const route = useRoute();
const { t, locale } = useI18n();

// 强制更新 key，用于强制重新渲染 Tab 组件
const tabsKey = ref(0);

// 搜索和筛选
const searchQuery = ref('');
const activeTab = ref(0);

// Mock 产品数据
const products = ref([
  {
    id: 'sfp',
    symbol: 'SFP',
    apy: 1.04,
    bonusRate: null,
    term: 0, // 0 表示活期
    tieredRate: false,
    minAmount: 0.01,
    maxAmount: 100000000000
  },
  {
    id: 'btc',
    symbol: 'BTC',
    apy: 0.01,
    bonusRate: 0.25,
    term: 0,
    tieredRate: true,
    minAmount: 0.0001,
    maxAmount: 100000000000
  },
  {
    id: 'usdt',
    symbol: 'USDT',
    apy: 2.07,
    bonusRate: 5,
    term: 0,
    tieredRate: true,
    minAmount: 1,
    maxAmount: 100000000000
  },
  {
    id: 'bnb',
    symbol: 'BNB',
    apy: 0.32,
    bonusRate: null,
    term: 30,
    tieredRate: false,
    minAmount: 0.01,
    maxAmount: 100000000000
  },
  {
    id: 'eth',
    symbol: 'ETH',
    apy: 1.5,
    bonusRate: 2,
    term: 90,
    tieredRate: false,
    minAmount: 0.001,
    maxAmount: 100000000000
  }
]);

// 根据 Tab 筛选产品
const filteredByTab = computed(() => {
  if (activeTab.value === 0) {
    // 热门：按 APY 排序
    return [...products.value].sort((a, b) => (b.apy + (b.bonusRate || 0)) - (a.apy + (a.bonusRate || 0)));
  } else if (activeTab.value === 1) {
    // 保本：活期产品
    return products.value.filter(p => p.term === 0);
  } else {
    // 高收益：APY > 1%
    return products.value.filter(p => (p.apy + (p.bonusRate || 0)) > 1);
  }
});

// 根据搜索关键词筛选
const filteredProducts = computed(() => {
  if (!searchQuery.value) {
    return filteredByTab.value;
  }
  const query = searchQuery.value.toLowerCase();
  return filteredByTab.value.filter(p => 
    p.symbol.toLowerCase().includes(query)
  );
});

// 跳转到申购页面
const goToSubscribe = (product) => {
  // 检查当前是否在 Me.vue 页面（通过路由路径判断）
  const isFromMePage = route.path === '/me';
  
  router.push({
    path: '/earn/subscribe',
    query: {
      symbol: product.symbol,
      id: product.id,
      from: isFromMePage ? 'me' : 'list',
      activeTab: isFromMePage ? 'earn' : undefined
    }
  });
};

// 排序功能
const handleSort = () => {
  console.log('Sort clicked');
};

// 历史记录
const handleHistory = () => {
  router.push('/history');
};


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
  event.target.style.display = 'block';
  event.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
  event.target.style.backgroundImage = 'none';
  const symbol = event.target.alt || '?';
  event.target.alt = symbol;
};

// 设置页面标题
const updatePageTitle = () => {
  document.title = t('earn.title') || 'Earn';
};

// 监听语言变化，强制更新 Tab 组件和页面标题
watch(() => locale.value, () => {
  tabsKey.value += 1;
  updatePageTitle();
}, { immediate: false });

onActivated(() => {
  tabsKey.value += 1;
  updatePageTitle();
});

onMounted(() => {
  tabsKey.value = 0;
  updatePageTitle();
});
</script>

<style scoped>
/* 全局强制无衬线字体 */
.earn-list-page {
  background-color: #000000;
  min-height: 100vh;
  /* 增加底部内边距，防止内容被底部 TabBar 遮挡 */
  padding-bottom: 80px;
  color: #FFFFFF;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
  width: 100%;
  box-sizing: border-box;
}

/* 自定义导航栏 */
.custom-nav-bar {
  --van-nav-bar-background: #000000;
  --van-nav-bar-title-text-color: #FFFFFF;
  --van-nav-bar-icon-color: #FCD535;
  --van-nav-bar-height: 46px;
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  font-weight: 700 !important;
  font-size: 18px !important;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

.earn-list-page,
.earn-list-page *,
.product-card,
.product-card *,
.data-value,
.apy-value,
.apy-bonus,
.coin-name,
.bonus-rate,
.term-tag,
.subscribe-btn {
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 工具栏容器 */
.tools-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 16px 8px;
  background-color: #000000;
  position: sticky;
  top: 46px;
  z-index: 99;
  width: 100%;
  box-sizing: border-box;
}

.search-field {
  flex: 1;
  background-color: #1E2329;
  border-radius: 8px;
}

:deep(.search-field .van-field__control) {
  color: #FFFFFF;
  font-size: 14px;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

:deep(.search-field .van-field__left-icon) {
  color: #848E9C;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon {
  font-size: 20px;
  color: #848E9C;
  cursor: pointer;
  transition: color 0.2s ease;
}

.action-icon:active {
  color: #F0B90B;
}

/* Tab 栏 */
.earn-tabs {
  background-color: #000000;
  padding: 0 16px;
  margin-top: 0;
  width: 100%;
  box-sizing: border-box;
}

:deep(.earn-tabs .van-tabs__wrap) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

:deep(.earn-tabs .van-tab) {
  font-size: 14px;
  font-weight: 500;
  padding: 12px 0;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

:deep(.earn-tabs .van-tabs__line) {
  background-color: #F0B90B;
  height: 2px;
}

/* 产品列表 */
.products-list {
  padding: 16px;
  padding-top: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
}

/* 产品卡片 - 三层架构 */
.product-card {
  background-color: #1E2329;
  border-radius: 8px;
  padding: 16px 20px;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  box-sizing: border-box;
}

.product-card:active {
  background-color: #252A32;
  transform: scale(0.98);
}

/* Header: 币种信息 + 右侧标签 */
.product-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 12px;
}

.coin-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.coin-icon {
  width: 32px;
  height: 32px;
  min-width: 32px;
  min-height: 32px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background-color: rgba(255, 255, 255, 0.1);
  display: block;
}

.coin-name-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coin-name {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.2;
}

.bonus-rate {
  font-size: 12px;
  color: #0ECB81;
  background-color: rgba(14, 203, 129, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  line-height: 1.2;
}

.header-badge {
  font-size: 10px;
  color: #B8BCC8;
  background-color: rgba(255, 255, 255, 0.12);
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  font-weight: 500;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

/* Body: APY 核心展示 */
.product-body {
  width: 100%;
  text-align: left;
}

.apy-main {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
  line-height: 1;
}

.apy-value {
  font-size: 32px;
  font-weight: 700;
  color: #0ECB81;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
  line-height: 1;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.apy-bonus {
  font-size: 16px;
  font-weight: 600;
  color: #0ECB81;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.apy-label {
  font-size: 12px;
  color: #848E9C;
  font-weight: 400;
  line-height: 1.4;
}

/* Footer: 期限标签 + 申购按钮 */
.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-top: auto;
  gap: 12px;
}

.term-tag {
  padding: 4px 10px;
  background-color: rgba(255, 255, 255, 0.1);
  color: #848E9C;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  line-height: 1.4;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

.subscribe-btn {
  width: 90px;
  height: 32px;
  background-color: #F0B90B;
  color: #1E2329;
  border: none;
  border-radius: 18px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s ease;
  padding: 0;
  margin: 0;
  flex-shrink: 0;
  margin-left: auto;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif !important;
}

:deep(.subscribe-btn .van-button__content) {
  padding: 0;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.subscribe-btn:active {
  opacity: 0.85;
  transform: scale(0.95);
}

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

:deep(.empty-state .van-empty__description) {
  color: #848E9C;
}
</style>

