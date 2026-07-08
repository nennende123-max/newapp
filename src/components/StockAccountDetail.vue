<template>
  <div class="detail-page">
    <header class="detail-header">
      <button class="icon-btn" type="button" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="detail-title">股票账户</h1>
      <button class="icon-btn" type="button" @click="toggleAmountHidden">
        <van-icon :name="isAmountHidden ? 'closed-eye' : 'eye-o'" size="20" />
      </button>
    </header>

    <section class="hero-card">
      <div class="hero-label">股票总资产 (USDT)</div>
      <div class="hero-total">{{ money(detail.total) }}</div>
      <div class="hero-pnl" :class="pnlTone(detail.todayPnl)">
        今日收益 {{ signedMoney(detail.todayPnl) }} {{ isAmountHidden ? '' : signedPercent(detail.todayPnlPercent) }}
      </div>

      <div class="range-switch">
        <button
          v-for="r in ranges"
          :key="r.key"
          type="button"
          class="range-chip"
          :class="{ active: activeRange === r.key }"
          @click="activeRange = r.key"
        >{{ r.label }}</button>
      </div>
      <Sparkline :data="trendData" :color="detail.todayPnl >= 0 ? '#00B976' : '#EF4444'" />
    </section>

    <section class="list-section">
      <div class="section-head"><span class="section-title">股票持仓</span></div>
      <div class="stock-row" v-for="item in detail.holdings" :key="item.symbol">
        <div class="stock-left">
          <div class="stock-badge">{{ item.symbol.slice(0, 2) }}</div>
          <div class="stock-meta">
            <span class="stock-symbol">{{ item.symbol }}</span>
            <span class="stock-name">{{ item.name }}</span>
          </div>
        </div>
        <div class="stock-right">
          <span class="stock-value">{{ money(item.value) }}</span>
          <span class="stock-sub">
            {{ money(item.amount, 0) }} 股
            <em class="stock-change" :class="pnlTone(item.changePercent)">{{ signedPercent(item.changePercent) }}</em>
          </span>
        </div>
      </div>
    </section>

    <div class="bottom-actions">
      <button class="act-btn ghost" type="button" @click="showTransfer = true">划转</button>
      <button class="act-btn primary" type="button" @click="goTrade">交易</button>
    </div>

    <TransferModal v-model:show="showTransfer" default-from="stock" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { formatNumber } from '@/utils/format'
import { useAmountPrivacy } from '@/composables/useAmountPrivacy'
import { stockDetailMock } from '@/data/assetMock'
import Sparkline from './Sparkline.vue'
import TransferModal from './TransferModal.vue'

defineOptions({ name: 'StockAccountDetail' })

const router = useRouter()
const { isAmountHidden, toggleAmountHidden } = useAmountPrivacy()

const detail = stockDetailMock
const showTransfer = ref(false)
const ranges = [
  { key: '7d', label: '7天' },
  { key: '30d', label: '30天' }
]
const activeRange = ref('7d')
const trendData = computed(() => (activeRange.value === '7d' ? detail.trend7d : detail.trend30d))

const money = (value, digits = 2) => (isAmountHidden.value ? '****' : formatNumber(value, digits))
const signedMoney = (value, digits = 2) => {
  if (isAmountHidden.value) return '****'
  const sign = value >= 0 ? '+' : '-'
  return `${sign}${formatNumber(Math.abs(value), digits)}`
}
const signedPercent = (value) => `${value >= 0 ? '+' : ''}${formatNumber(value, 2)}%`
const pnlTone = (value) => (value >= 0 ? 'up' : 'down')

const goTrade = () => {
  // TODO: 若后续新增独立股票交易路由，替换为对应路由
  router.push('/stocks')
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f4f7fb;
  color: #1e293b;
  padding-bottom: 96px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 12px;
  background: #ffffff;
  border-bottom: 1px solid #e6ebf2;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #1e293b;
  cursor: pointer;
}

.detail-title { font-size: 17px; font-weight: 700; margin: 0; }

.hero-card {
  margin: 16px;
  padding: 20px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
}

.hero-label { font-size: 13px; color: #64748b; }
.hero-total { margin: 8px 0 4px; font-size: 30px; font-weight: 800; font-variant-numeric: tabular-nums; }
.hero-pnl { font-size: 13px; font-weight: 600; margin-bottom: 12px; }

.up { color: #00b976; }
.down { color: #ef4444; }

.range-switch { display: flex; gap: 8px; margin-bottom: 8px; }
.range-chip {
  padding: 5px 14px;
  border-radius: 999px;
  border: 1px solid #e6ebf2;
  background: #f8fafc;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.range-chip.active { background: #eef2ff; border-color: #8b5cf6; color: #6d28d9; }

.list-section {
  margin: 0 16px 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.section-head { margin-bottom: 12px; }
.section-title { font-size: 15px; font-weight: 700; }

.stock-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.stock-row:last-child { border-bottom: none; }

.stock-left { display: flex; align-items: center; gap: 12px; }
.stock-badge {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  color: #ffffff;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stock-meta { display: flex; flex-direction: column; gap: 2px; }
.stock-symbol { font-size: 15px; font-weight: 700; }
.stock-name { font-size: 12px; color: #94a3b8; }

.stock-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.stock-value { font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }
.stock-sub { font-size: 12px; color: #64748b; font-variant-numeric: tabular-nums; }
.stock-change { font-style: normal; margin-left: 4px; }

.bottom-actions {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  gap: 10px;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom));
  background: #ffffff;
  border-top: 1px solid #e6ebf2;
  max-width: 500px;
  margin: 0 auto;
}
.act-btn {
  flex: 1;
  height: 46px;
  border-radius: 12px;
  border: none;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}
.act-btn.ghost { background: #f1f5f9; color: #334155; }
.act-btn.primary { background: #fcd535; color: #111827; }

:global(html[data-theme='dark']) .detail-page {
  background: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
}

:global(html[data-theme='dark']) .detail-header,
:global(html[data-theme='dark']) .hero-card,
:global(html[data-theme='dark']) .list-section,
:global(html[data-theme='dark']) .bottom-actions {
  background: var(--color-bg-card) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .range-chip,
:global(html[data-theme='dark']) .act-btn.ghost {
  background: var(--color-bg-input) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-secondary) !important;
}

:global(html[data-theme='dark']) .range-chip.active {
  background: rgb(139 92 246 / 0.18) !important;
  border-color: rgb(139 92 246 / 0.38) !important;
  color: #C4B5FD !important;
}

:global(html[data-theme='dark']) .stock-row {
  border-color: var(--color-border) !important;
}

:global(html[data-theme='dark']) .hero-label,
:global(html[data-theme='dark']) .stock-name,
:global(html[data-theme='dark']) .stock-sub {
  color: var(--color-text-secondary) !important;
}
</style>
