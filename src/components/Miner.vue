<template>
  <div class="cloud-mining-page">

    <!-- Section 1: Summary cards -->
    <div class="summary-header">
      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-card-top">
            <span class="summary-label">{{ t('miner.cloud_total_assets') }}</span>
            <van-icon
              :name="showBalance ? 'eye-o' : 'closed-eye'"
              class="eye-icon"
              @click="showBalance = !showBalance"
            />
          </div>
          <div class="summary-value num">
            {{ showBalance ? formatAssetValue(cloudMiningAssets) : '****' }}
            <span class="summary-unit">USDT</span>
          </div>
        </div>
        <div class="summary-card">
          <span class="summary-label">{{ t('miner.cloud_total_earnings') }}</span>
          <div class="summary-value num text-earn">
            {{ showBalance ? formatAssetValue(totalProfit) : '****' }}
            <span class="summary-unit">USDT</span>
          </div>
        </div>
      </div>

      <!-- Quick access -->
      <div class="nav-grid">
        <div
          v-for="nav in navItems"
          :key="nav.key"
          class="nav-item"
          @click="handleNavClick(nav.key)"
        >
          <div class="nav-icon">
            <van-icon :name="nav.icon" />
          </div>
          <span class="nav-label">{{ nav.label }}</span>
        </div>
      </div>
    </div>

    <!-- Section 2: Institutional miner list -->
    <section class="miner-marketplace">
      <h2 class="section-title">{{ $t('inst_power') }}</h2>

      <div v-if="loading" class="loading-box">
        <van-loading color="#F0B90B" vertical>{{ $t('update_db') }}</van-loading>
      </div>

      <div v-else class="miner-list">
        <div v-for="m in minersFromDB" :key="m.id" class="miner-card">
          <div class="miner-card-header">
            <div class="miner-title-block">
              <h3 class="miner-name">{{ m.name }}</h3>
              <span class="miner-pair">{{ m.pair }}</span>
            </div>
            <span class="m-badge">{{ $t('safe_sla') }}</span>
          </div>

          <div class="miner-data-rows">
            <div class="data-row split">
              <div class="data-left">
                <span class="data-label">{{ t('miner.est_apy') }}</span>
                <span class="apy-value num">{{ m.rate }}%</span>
              </div>
              <div class="data-right">
                <span class="data-label">
                  <van-icon name="lock" class="lock-icon" />
                  {{ t('miner.cycle_label') }}
                </span>
                <span class="cycle-value num">{{ m.days }}{{ t('earn.days') }}</span>
              </div>
            </div>
            <div class="data-row full">
              <span class="data-label">{{ t('miner.min_purchase_price') }}</span>
              <span class="price-value num">${{ formatPrice(m.price) }}</span>
            </div>
          </div>

          <button class="m-buy-btn btn-cta" @click="confirmRent(m)">
            {{ t('earn.rent_now') }}
          </button>
        </div>
      </div>
    </section>

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
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, showConfirmDialog } from 'vant';

defineOptions({
  name: 'Miner'
});

const router = useRouter();
const route = useRoute();
const { t } = useI18n();

const loading = ref(false);
const showBalance = ref(true);
const showRulesPopup = ref(false);
const cloudMiningAssets = ref(1234.56);
const totalProfit = ref(342.8);

const navItems = computed(() => [
  {
    key: 'marketplace',
    label: t('miner.marketplace'),
    icon: 'shop-o'
  },
  {
    key: 'my_miners',
    label: t('miner.my_miners'),
    icon: 'cluster-o'
  },
  {
    key: 'history',
    label: t('miner.revenue_record'),
    icon: 'bill-o'
  }
]);

const minersFromDB = ref([
  { id: 1, name: 'Antminer S21', pair: 'BTC / USDT', rate: 2.5, days: 30, price: 1000 },
  { id: 2, name: 'Avalon A14', pair: 'BTC / USDT', rate: 3.2, days: 60, price: 2500 },
  { id: 3, name: 'Antminer S19 XP', pair: 'USDT', rate: 1.8, days: 90, price: 500 }
]);

// --- 格式化资产值（支持国际化） ---
const formatAssetValue = (value) => {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}${t('miner.ten_thousand')}`;
  }
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

const formatPrice = (value) => {
  return Number(value).toLocaleString('en-US', { maximumFractionDigits: 0 });
};

const handleNavClick = (key) => {
  switch (key) {
    case 'marketplace':
      router.push('/earn');
      break;
    case 'my_miners':
      showToast(t('miner.my_miners'));
      break;
    case 'history':
      router.push('/history');
      break;
    default:
      break;
  }
};

const confirmRent = (miner) => {
  showConfirmDialog({
    title: t('earn.rent_now'),
    message: `${miner.name} · $${formatPrice(miner.price)}`,
    confirmButtonColor: '#F0B90B'
  })
    .then(() => showToast({ message: t('miner.mining_rules_desc'), icon: 'success' }))
    .catch(() => {});
};

const loadMiners = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 400);
};

onMounted(() => {
  loadMiners();
  if (route.query.minerId) {
    const id = Number(route.query.minerId);
    if (minersFromDB.value.some(m => m.id === id || String(m.id) === route.query.minerId)) {
      // miner deep-link from earn page
    }
  }
});

onActivated(() => {
  loadMiners();
});
</script>

<style scoped>
.cloud-mining-page {
  background: var(--color-bg, #0B0E11);
  min-height: 100vh;
  padding: 16px;
  padding-bottom: 80px;
  color: var(--color-text-primary, #EAECEF);
  font-family: var(--font-ui);
}

/* Section 1: Summary */
.summary-header {
  margin-bottom: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.summary-card {
  background: var(--color-bg-elevated, #1E2329);
  border-radius: var(--radius-card, 16px);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.05));
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
}

.summary-label {
  font-size: 11px;
  color: var(--color-text-secondary, #848E9C);
  font-weight: 500;
  line-height: 1.3;
}

.eye-icon {
  font-size: 16px;
  color: var(--color-text-secondary, #848E9C);
  flex-shrink: 0;
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: var(--font-number);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.summary-value.text-earn {
  color: var(--color-earn, #0ECB81);
}

.summary-unit {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary, #848E9C);
  margin-left: 2px;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.nav-grid .nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.nav-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-button, 8px);
  background: var(--color-bg-elevated, #1E2329);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary, #EAECEF);
  font-size: 20px;
}

.nav-label {
  font-size: 11px;
  color: var(--color-text-secondary, #848E9C);
  text-align: center;
  line-height: 1.3;
}

/* Section 2: Marketplace */
.miner-marketplace {
  margin-top: 4px;
}

.section-title {
  margin: 0 0 14px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary, #EAECEF);
}

.loading-box {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.miner-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.miner-card {
  background: var(--color-bg-elevated, #1E2329);
  border-radius: var(--radius-card, 16px);
  padding: 16px;
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.05));
}

.miner-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 14px;
}

.miner-title-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.miner-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

.miner-pair {
  font-size: 12px;
  color: var(--color-text-secondary, #848E9C);
  font-weight: 500;
}

.m-badge {
  font-size: 10px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--color-text-secondary, #848E9C);
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
  white-space: nowrap;
}

.miner-data-rows {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
}

.data-row.split {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
}

.data-row.full {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.06));
}

.data-left,
.data-right {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.data-right {
  align-items: flex-end;
  text-align: right;
}

.data-label {
  font-size: 11px;
  color: var(--color-text-secondary, #848E9C);
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.lock-icon {
  font-size: 11px;
}

.apy-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-earn, #0ECB81);
  font-family: var(--font-number);
  font-variant-numeric: tabular-nums;
}

.cycle-value,
.price-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary, #EAECEF);
  font-family: var(--font-number);
  font-variant-numeric: tabular-nums;
}

.m-buy-btn {
  width: 100%;
  background: var(--color-brand, #F0B90B);
  border: none;
  padding: 12px;
  border-radius: var(--radius-button, 8px);
  font-weight: 700;
  font-size: 14px;
  color: #000;
  cursor: pointer;
}

.m-buy-btn:active {
  opacity: 0.85;
}

.num {
  font-family: var(--font-number);
  font-variant-numeric: tabular-nums;
}

.text-earn {
  color: var(--color-earn, #0ECB81);
}

/* Rules popup */
.dark-rules-popup {
  background-color: #1E2329 !important;
  color: #EAECEF !important;
  max-height: 60% !important;
}

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
  color: var(--color-brand, #F0B90B);
  margin: 20px 0;
  padding: 0 20px;
}

.rules-body {
  padding: 0 20px 40px;
  font-size: 14px;
  line-height: 1.6;
  color: #848E9C;
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

:deep(.van-icon) {
  font-family: 'vant-icon', sans-serif !important;
}
</style>
