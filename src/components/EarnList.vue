<template>
  <div class="earn-list-page" :class="{ 'embedded-mode': isEmbedded }">
    <van-nav-bar
      v-if="!isEmbedded"
      :title="t('earn.title')"
      left-arrow
      @click-left="router.back()"
      fixed
      placeholder
      safe-area-inset-top
      :border="false"
      class="custom-nav-bar"
    />

    <div class="tools-section-wrapper">
      <div class="divider-line"></div>
      <div class="tools-section" :class="{ 'embedded-tools': isEmbedded }">
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
    </div>

    <!-- Section 1: Tabs -->
    <van-tabs
      :key="tabsKey"
      v-model:active="activeTab"
      background="transparent"
      title-active-color="#EAECEF"
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

    <div class="marketplace-content">
      <!-- Section 2: Simple Earn -->
      <section class="market-section">
        <h2 class="section-title">{{ t('earn.section_simple_earn') }}</h2>

        <div class="products-list">
          <div
            v-for="product in filteredSimpleEarn"
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
                <span class="coin-name">{{ product.symbol }}</span>
                <span v-if="product.bonusRate" class="bonus-rate">+{{ product.bonusRate }}%</span>
              </div>
              <div v-if="product.tieredRate" class="header-badge">
                {{ t('earn.tiered_annual_rate') }}
              </div>
            </div>

            <div class="product-row">
              <!-- Rate column (left, DIN) -->
              <div class="rate-column">
                <div class="apy-main">
                  <span class="apy-value num">{{ formatApy(getDisplayApy(product)) }}%</span>
                </div>
                <div class="apy-label">{{ t('earn.reference_annual') }}</div>
              </div>

              <!-- Tenure chips + action -->
              <div class="meta-column">
                <div v-if="hasMultipleTenures(product)" class="tenure-chips">
                  <button
                    v-for="option in product.tenureOptions"
                    :key="option.value"
                    type="button"
                    class="tenure-chip"
                    :class="{ active: getSelectedTenure(product) === option.value }"
                    @click.stop="selectTenure(product.id, option.value)"
                  >
                    <van-icon v-if="option.locked" name="lock" class="chip-lock" />
                    <span>{{ formatTenureLabel(option) }}</span>
                  </button>
                </div>
                <div v-else-if="product.tenureOptions?.length" class="tenure-single">
                  <span class="tenure-chip active static">
                    <van-icon v-if="product.tenureOptions[0].locked" name="lock" class="chip-lock" />
                    <span>{{ formatTenureLabel(product.tenureOptions[0]) }}</span>
                  </span>
                </div>
              </div>

              <van-button
                class="subscribe-btn btn-cta"
                @click.stop="goToSubscribe(product)"
              >
                {{ t('earn.subscribe') }}
              </van-button>
            </div>
          </div>

          <div v-if="filteredSimpleEarn.length === 0" class="empty-state compact">
            <van-empty :description="t('earn.no_products')" />
          </div>
        </div>
      </section>

      <!-- Section 3: Cloud Mining -->
      <section class="market-section">
        <h2 class="section-title">{{ t('earn.section_cloud_mining') }}</h2>

        <div class="products-list">
          <div
            v-for="miner in filteredCloudMining"
            :key="miner.id"
            class="product-card mining-card"
          >
            <div class="product-header">
              <div class="coin-info">
                <img
                  :src="getCoinIcon(miner.symbol)"
                  :alt="miner.symbol"
                  class="coin-icon"
                  @error="handleImageError"
                />
                <div class="coin-name-group">
                  <span class="coin-name">{{ miner.pair || `${miner.symbol}/USDT` }}</span>
                  <span class="mining-tag">{{ t('miner.cloud_mining') }}</span>
                </div>
              </div>
            </div>

            <div class="product-row mining-row">
              <div class="rate-column">
                <div class="apy-main">
                  <span class="est-apy-label">{{ t('earn.est_apy') }}</span>
                  <span class="apy-value num">{{ formatApy(miner.apy) }}%</span>
                </div>
              </div>

              <div class="meta-column mining-meta">
                <div class="miner-model">
                  <span class="meta-label">{{ t('earn.miner_model') }}</span>
                  <span class="meta-value">{{ miner.minerModel }}</span>
                </div>
                <div class="tenure-single">
                  <span class="tenure-chip static locked-only">
                    <van-icon name="lock" class="chip-lock" />
                    <span>{{ miner.term }}{{ t('earn.days_short') }}</span>
                  </span>
                </div>
              </div>

              <van-button
                class="rent-btn btn-cta"
                @click.stop="goToRent(miner)"
              >
                {{ t('earn.rent_now') }}
              </van-button>
            </div>
          </div>

          <div v-if="filteredCloudMining.length === 0" class="empty-state compact">
            <van-empty :description="t('earn.no_products')" />
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const route = useRoute();
const { t, locale } = useI18n();

const isEmbedded = computed(() => route.path === '/me' || route.query.from === 'me');
const tabsKey = ref(0);
const searchQuery = ref('');
const activeTab = ref(0);
const selectedTenures = reactive({});

const simpleEarnProducts = ref([
  {
    id: 'usdt',
    symbol: 'USDT',
    bonusRate: 5,
    tieredRate: true,
    tenureOptions: [
      { value: 0, apy: 2.07, locked: false },
      { value: 30, apy: 4.5, locked: true },
      { value: 90, apy: 6.8, locked: true }
    ]
  },
  {
    id: 'eth',
    symbol: 'ETH',
    bonusRate: 2,
    tieredRate: false,
    tenureOptions: [
      { value: 0, apy: 1.5, locked: false },
      { value: 30, apy: 2.8, locked: true },
      { value: 90, apy: 4.2, locked: true }
    ]
  },
  {
    id: 'btc',
    symbol: 'BTC',
    bonusRate: 0.25,
    tieredRate: true,
    tenureOptions: [
      { value: 0, apy: 0.01, locked: false }
    ]
  },
  {
    id: 'bnb',
    symbol: 'BNB',
    bonusRate: null,
    tieredRate: false,
    tenureOptions: [
      { value: 30, apy: 0.32, locked: true }
    ]
  },
  {
    id: 'sfp',
    symbol: 'SFP',
    bonusRate: null,
    tieredRate: false,
    tenureOptions: [
      { value: 0, apy: 1.04, locked: false }
    ]
  }
]);

const cloudMiningProducts = ref([
  {
    id: 'btc-mining',
    symbol: 'BTC',
    pair: 'BTC/USDT',
    minerModel: 'Antminer S21',
    apy: 2.5,
    term: 30
  },
  {
    id: 'usdt-mining',
    symbol: 'USDT',
    pair: 'USDT',
    minerModel: 'Antminer S19 XP',
    apy: 1.8,
    term: 90
  }
]);

const filterByTab = (items, getApy, getFlexible) => {
  if (activeTab.value === 0) {
    return [...items].sort((a, b) => getApy(b) - getApy(a));
  }
  if (activeTab.value === 1) {
    return items.filter(item => getFlexible(item));
  }
  return items.filter(item => getApy(item) > 1);
};

const filterBySearch = (items, getSymbol) => {
  if (!searchQuery.value) return items;
  const query = searchQuery.value.toLowerCase();
  return items.filter(item => getSymbol(item).toLowerCase().includes(query));
};

const getProductApy = (product) => {
  const tenure = getSelectedTenure(product);
  const option = product.tenureOptions?.find(o => o.value === tenure);
  return (option?.apy ?? 0) + (product.bonusRate || 0);
};

const isFlexibleProduct = (product) => {
  return product.tenureOptions?.some(o => o.value === 0 && !o.locked);
};

const filteredSimpleEarn = computed(() => {
  const tabbed = filterByTab(simpleEarnProducts.value, getProductApy, isFlexibleProduct);
  return filterBySearch(tabbed, p => p.symbol);
});

const filteredCloudMining = computed(() => {
  const tabbed = filterByTab(
    cloudMiningProducts.value,
    m => m.apy,
    m => m.term <= 30
  );
  return filterBySearch(tabbed, m => m.symbol + (m.pair || ''));
});

const hasMultipleTenures = (product) => (product.tenureOptions?.length ?? 0) > 1;

const getSelectedTenure = (product) => {
  if (selectedTenures[product.id] !== undefined) {
    return selectedTenures[product.id];
  }
  return product.tenureOptions?.[0]?.value ?? 0;
};

const getDisplayApy = (product) => {
  const tenure = getSelectedTenure(product);
  const option = product.tenureOptions?.find(o => o.value === tenure);
  return option?.apy ?? 0;
};

const selectTenure = (productId, value) => {
  selectedTenures[productId] = value;
};

const formatApy = (value) => {
  const n = Number(value);
  if (Number.isInteger(n)) return String(n);
  return n.toFixed(2);
};

const formatTenureLabel = (option) => {
  if (option.value === 0) return t('earn.flexible');
  return `${option.value}${t('earn.days')}`;
};

const goToSubscribe = (product) => {
  const isFromMePage = route.path === '/me';
  const term = getSelectedTenure(product);
  router.push({
    path: '/earn/subscribe',
    query: {
      symbol: product.symbol,
      id: product.id,
      term: String(term),
      from: isFromMePage ? 'me' : 'list',
      activeTab: isFromMePage ? 'earn' : undefined
    }
  });
};

const goToRent = (miner) => {
  router.push({
    path: '/miner',
    query: { tab: 'mining', minerId: miner.id }
  });
};

const handleSort = () => {
  console.log('Sort clicked');
};

const handleHistory = () => {
  router.push('/history');
};

const getCoinIcon = (symbol) => {
  const iconMap = {
    BTC: 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
    ETH: 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
    USDT: 'https://assets.coingecko.com/coins/images/325/large/Tether.png',
    BNB: 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png',
    SFP: 'https://assets.coingecko.com/coins/images/16010/large/safepal.png'
  };
  return iconMap[symbol.toUpperCase()] || iconMap.BTC;
};

const handleImageError = (event) => {
  event.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
};

const updatePageTitle = () => {
  document.title = t('earn.title') || 'Earn';
};

watch(() => locale.value, () => {
  tabsKey.value += 1;
  updatePageTitle();
});

onActivated(() => {
  tabsKey.value += 1;
  updatePageTitle();
});

onMounted(() => {
  updatePageTitle();
});
</script>

<style scoped>
.earn-list-page {
  background-color: var(--color-bg, #0B0E11);
  min-height: 100vh;
  padding-bottom: 80px;
  color: var(--color-text-primary, #EAECEF);
  font-family: var(--font-ui);
  width: 100%;
  box-sizing: border-box;
}

.earn-list-page.embedded-mode {
  min-height: auto;
  padding-bottom: 0;
}

.embedded-mode :deep(.van-nav-bar__placeholder) {
  display: none !important;
  height: 0 !important;
}

.custom-nav-bar {
  --van-nav-bar-background: var(--color-bg, #0B0E11);
  --van-nav-bar-title-text-color: #FFFFFF;
  --van-nav-bar-icon-color: var(--color-brand, #F0B90B);
  --van-nav-bar-height: 46px;
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  font-weight: 700;
  font-size: 18px;
}

.tools-section-wrapper {
  background-color: var(--color-bg, #0B0E11);
  position: sticky;
  top: 46px;
  z-index: 99;
}

.divider-line {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(240, 185, 11, 0.35), transparent);
}

.tools-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 16px 8px;
}

.embedded-mode .tools-section-wrapper {
  position: relative;
  top: 0;
}

.search-field {
  flex: 1;
  background-color: var(--color-bg-elevated, #1E2329);
  border-radius: var(--radius-input, 12px);
}

:deep(.search-field .van-field__control) {
  color: #FFFFFF;
  font-size: 14px;
}

.search-actions {
  display: flex;
  gap: 12px;
}

.action-icon {
  font-size: 20px;
  color: var(--color-text-secondary, #848E9C);
}

.earn-tabs {
  background-color: var(--color-bg, #0B0E11);
  padding: 0 16px;
}

:deep(.earn-tabs .van-tabs__wrap) {
  border-bottom: 1px solid var(--color-border, rgba(255, 255, 255, 0.08));
}

:deep(.earn-tabs .van-tab) {
  font-size: 14px;
  font-weight: 500;
  padding: 12px 0;
}

:deep(.earn-tabs .van-tabs__line) {
  background-color: var(--color-brand, #F0B90B);
  height: 2px;
}

.marketplace-content {
  padding: 0 16px 16px;
}

.market-section {
  margin-top: 20px;
}

.section-title {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary, #EAECEF);
  letter-spacing: 0.02em;
}

.products-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-card {
  background-color: var(--color-bg-elevated, #1E2329);
  border-radius: var(--radius-card, 16px);
  padding: 14px 16px;
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.05));
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.coin-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.coin-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.08);
}

.coin-name {
  font-size: 15px;
  font-weight: 700;
  color: #FFFFFF;
}

.coin-name-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mining-tag {
  font-size: 11px;
  color: var(--color-text-secondary, #848E9C);
}

.bonus-rate {
  font-size: 11px;
  color: var(--color-earn, #0ECB81);
  background: rgba(14, 203, 129, 0.12);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-number);
  font-variant-numeric: tabular-nums;
}

.header-badge {
  font-size: 10px;
  color: var(--color-text-secondary, #848E9C);
  background: rgba(255, 255, 255, 0.08);
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.product-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.mining-row {
  align-items: center;
}

.rate-column {
  flex-shrink: 0;
  width: 72px;
  text-align: left;
}

.apy-main {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  line-height: 1.1;
}

.est-apy-label {
  font-size: 10px;
  color: var(--color-text-secondary, #848E9C);
  font-weight: 500;
}

.apy-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-earn, #0ECB81);
  font-family: var(--font-number);
  font-variant-numeric: tabular-nums;
}

.apy-label {
  margin-top: 4px;
  font-size: 10px;
  color: var(--color-text-secondary, #848E9C);
  line-height: 1.3;
}

.meta-column {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mining-meta {
  gap: 8px;
}

.miner-model {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 10px;
  color: var(--color-text-secondary, #848E9C);
}

.meta-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary, #EAECEF);
}

.tenure-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tenure-single {
  display: flex;
}

.tenure-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary, #848E9C);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tenure-chip.static {
  cursor: default;
}

.tenure-chip.active {
  border-color: var(--color-brand, #F0B90B);
  background: rgba(240, 185, 11, 0.12);
  color: var(--color-brand, #F0B90B);
}

.chip-lock {
  font-size: 10px;
}

.subscribe-btn,
.rent-btn {
  flex-shrink: 0;
  min-width: 64px;
  height: 32px;
  padding: 0 12px;
  border-radius: var(--radius-button, 8px) !important;
  font-size: 12px;
  font-weight: 700;
}

:deep(.subscribe-btn .van-button__content),
:deep(.rent-btn .van-button__content) {
  padding: 0;
}

.empty-state.compact {
  padding: 24px 0;
}

:deep(.van-icon),
:deep([class*='van-icon']) {
  font-family: 'vant-icon', 'vant-iconfont', sans-serif !important;
}
</style>
