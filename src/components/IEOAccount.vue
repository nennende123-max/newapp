<template>
  <div class="ieo-account-page">
    <header class="ieo-header">
      <button class="icon-button" type="button" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1>{{ t('assets.ieo_account_title') }}</h1>
      <div class="header-spacer"></div>
    </header>

    <main class="ieo-content">
      <section class="hero-panel">
        <div class="hero-kicker">{{ t('assets.ieo_account') }}</div>
        <div class="hero-title">{{ formatCurrency(totalValue) }} USDT</div>
        <div class="hero-subtitle">{{ t('assets.ieo_account_subtitle') }}</div>
        <div class="hero-stats">
          <div>
            <span>{{ t('assets.ieo_won_assets') }}</span>
            <strong>{{ accountAssets.length }}</strong>
          </div>
          <div>
            <span>{{ t('assets.ieo_distribution') }}</span>
            <strong>{{ formatNumber(totalAmount, 2) }}</strong>
          </div>
        </div>
      </section>

      <section class="asset-section">
        <div class="section-title">
          <h2>{{ t('assets.ieo_won_assets') }}</h2>
          <span>{{ t('assets.ieo_available_after_listing') }}</span>
        </div>

        <article v-for="asset in accountAssets" :key="asset.symbol" class="ieo-asset-card">
          <div class="asset-main">
            <div class="token-mark" :style="{ '--token-color': asset.color }">
              {{ asset.symbol.slice(0, 1) }}
            </div>
            <div>
              <div class="token-row">
                <strong>{{ asset.symbol }}</strong>
                <span>{{ asset.name }}</span>
              </div>
              <p>{{ t('assets.ieo_source_won') }}</p>
            </div>
          </div>

          <div class="asset-balance">
            <span>{{ t('assets.ieo_total_value') }}</span>
            <strong>{{ formatCurrency(asset.value) }} USDT</strong>
          </div>

          <div class="metric-grid">
            <div>
              <span>{{ t('assets.balance') || 'Balance' }}</span>
              <strong>{{ formatNumber(asset.amount, 2) }} {{ asset.symbol }}</strong>
            </div>
            <div>
              <span>{{ t('assets.price') || 'Price' }}</span>
              <strong>{{ formatCurrency(asset.priceUsdt) }} USDT</strong>
            </div>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAssetStore } from '@/stores/assets'

defineOptions({ name: 'IEOAccount' })

const router = useRouter()
const { t } = useI18n()
const assetStore = useAssetStore()

const demoAssets = [
  { symbol: 'NCAI', name: 'Neural Chain AI', amount: 22.22, priceUsdt: 0.18, color: '#f5b800' },
  { symbol: 'GMT', name: 'Green Metaverse Token', amount: 86.50, priceUsdt: 0.24, color: '#10b981' },
  { symbol: 'DFP', name: 'DeFi Protocol', amount: 222.22, priceUsdt: 0.06, color: '#6366f1' }
]

const accountAssets = computed(() => {
  const storedAssets = assetStore.ieoAssets || {}
  const merged = new Map(demoAssets.map(asset => [asset.symbol, { ...asset }]))

  Object.values(storedAssets).forEach((asset) => {
    const symbol = String(asset.symbol || '').toUpperCase()
    if (!symbol) return
    const fallback = merged.get(symbol) || {}
    merged.set(symbol, {
      ...fallback,
      symbol,
      name: asset.name || fallback.name || symbol,
      amount: Number(asset.amount) || 0,
      priceUsdt: Number(asset.priceUsdt) || fallback.priceUsdt || 0,
      color: fallback.color || '#f5b800'
    })
  })

  return Array.from(merged.values())
    .filter(asset => Number(asset.amount) > 0)
    .map(asset => ({
      ...asset,
      value: (Number(asset.amount) || 0) * (Number(asset.priceUsdt) || 0)
    }))
    .sort((a, b) => b.value - a.value)
})

const totalValue = computed(() => accountAssets.value.reduce((sum, asset) => sum + asset.value, 0))
const totalAmount = computed(() => accountAssets.value.reduce((sum, asset) => sum + Number(asset.amount || 0), 0))

const formatNumber = (value, digits = 2) => Number(value || 0).toLocaleString('en-US', {
  minimumFractionDigits: digits,
  maximumFractionDigits: digits
})

const formatCurrency = (value) => Number(value || 0).toLocaleString('en-US', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})
</script>

<style scoped>
.ieo-account-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 0%, rgb(var(--color-brand-rgb) / 0.14), transparent 30%),
    linear-gradient(180deg, var(--color-bg) 0%, var(--color-surface-muted) 100%);
  color: var(--color-text-primary);
  padding-bottom: 28px;
}

.ieo-header {
  height: 56px;
  padding: 0 16px;
  display: grid;
  grid-template-columns: 40px 1fr 40px;
  align-items: center;
  background: color-mix(in srgb, var(--color-bg-card) 88%, transparent);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  backdrop-filter: blur(16px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.ieo-header h1 {
  margin: 0;
  text-align: center;
  font-size: 17px;
  font-weight: 800;
  letter-spacing: 0;
}

.icon-button {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--color-text-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.header-spacer {
  width: 36px;
  height: 36px;
}

.ieo-content {
  padding: 14px 16px 0;
}

.hero-panel {
  padding: 22px 20px;
  border-radius: 18px;
  background:
    linear-gradient(135deg, #111827 0%, #172033 52%, #0f172a 100%);
  color: #ffffff;
  box-shadow: 0 18px 36px rgb(15 23 42 / 0.18);
  overflow: hidden;
  position: relative;
}

.hero-panel::after {
  content: '';
  position: absolute;
  right: -54px;
  top: -70px;
  width: 180px;
  height: 180px;
  border-radius: 999px;
  background: rgb(var(--color-brand-rgb) / 0.28);
}

.hero-kicker,
.hero-subtitle,
.hero-stats span,
.asset-balance span,
.metric-grid span,
.asset-main p,
.section-title span {
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 500;
}

.hero-kicker {
  color: rgb(255 255 255 / 0.68);
}

.hero-title {
  margin-top: 10px;
  font-size: 32px;
  line-height: 1.05;
  font-weight: 850;
  font-variant-numeric: tabular-nums;
  position: relative;
  z-index: 1;
}

.hero-subtitle {
  margin-top: 8px;
  color: rgb(255 255 255 / 0.62);
}

.hero-stats {
  margin-top: 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.hero-stats div {
  padding: 12px;
  border-radius: 14px;
  background: rgb(255 255 255 / 0.08);
  border: 1px solid rgb(255 255 255 / 0.08);
}

.hero-stats span {
  display: block;
  color: rgb(255 255 255 / 0.58);
}

.hero-stats strong {
  display: block;
  margin-top: 6px;
  font-size: 18px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.asset-section {
  margin-top: 18px;
}

.section-title {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.section-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 850;
}

.ieo-asset-card {
  padding: 16px;
  border-radius: 16px;
  background: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  box-shadow: 0 12px 28px rgb(15 23 42 / 0.07);
}

.ieo-asset-card + .ieo-asset-card {
  margin-top: 12px;
}

.asset-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.token-mark {
  width: 46px;
  height: 46px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--token-color), color-mix(in srgb, var(--token-color) 62%, #ffffff));
  color: #ffffff;
  font-size: 18px;
  font-weight: 850;
  box-shadow: 0 10px 22px color-mix(in srgb, var(--token-color) 26%, transparent);
}

.token-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.token-row strong {
  font-size: 18px;
  font-weight: 850;
}

.token-row span {
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 600;
}

.asset-main p {
  margin: 4px 0 0;
}

.asset-balance {
  margin-top: 16px;
  padding: 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgb(var(--color-brand-rgb) / 0.12), rgb(var(--color-brand-rgb) / 0.03));
  border: 1px solid rgb(var(--color-brand-rgb) / 0.16);
}

.asset-balance span,
.metric-grid span {
  display: block;
  margin-bottom: 6px;
}

.asset-balance strong {
  font-size: 22px;
  font-weight: 850;
  font-variant-numeric: tabular-nums;
}

.metric-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.metric-grid div {
  min-width: 0;
  padding: 12px;
  border-radius: 14px;
  background: var(--color-surface-muted);
}

.metric-grid strong {
  display: block;
  font-size: 13px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
