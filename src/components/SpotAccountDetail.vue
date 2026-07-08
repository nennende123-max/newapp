<template>
  <div class="detail-page">
    <header class="detail-header">
      <button class="icon-btn" type="button" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="detail-title">现货账户</h1>
      <button class="icon-btn" type="button" @click="toggleAmountHidden">
        <van-icon :name="isAmountHidden ? 'closed-eye' : 'eye-o'" size="20" />
      </button>
    </header>

    <section class="hero-card">
      <div class="hero-label">现货账户总资产 (USDT)</div>
      <div class="hero-total">{{ money(detail.total) }}</div>
      <div class="hero-pnl" :class="pnlTone(detail.todayPnl)">
        今日收益 {{ signedMoney(detail.todayPnl) }} {{ isAmountHidden ? '' : signedPercent(detail.todayPnlPercent) }}
      </div>
      <Sparkline :data="detail.trend" :color="detail.todayPnl >= 0 ? '#00B976' : '#EF4444'" />
    </section>

    <section class="balance-row">
      <div class="balance-item">
        <span class="bal-label">可用余额</span>
        <span class="bal-value">{{ money(detail.available) }}</span>
      </div>
      <div class="balance-item">
        <span class="bal-label">冻结余额</span>
        <span class="bal-value">{{ money(detail.frozen) }}</span>
      </div>
    </section>

    <section class="list-section">
      <div class="section-head">
        <span class="section-title">资产列表</span>
      </div>
      <div class="asset-row" v-for="asset in detail.assets" :key="asset.symbol">
        <div class="asset-left">
          <CryptoIcon :symbol="asset.symbol" :size="38" variant="compact" />
          <div class="coin-meta">
            <span class="coin-symbol">{{ asset.symbol }}</span>
            <span class="coin-name">{{ asset.name }}</span>
          </div>
        </div>
        <div class="asset-right">
          <span class="coin-amount">{{ money(asset.amount, 4) }}</span>
          <span class="coin-value">
            ≈ {{ money(asset.value) }}
            <em class="coin-change" :class="pnlTone(asset.changePercent)">{{ signedPercent(asset.changePercent) }}</em>
          </span>
        </div>
      </div>
    </section>

    <section class="list-section">
      <div class="section-head">
        <span class="section-title">交易记录 / 账单流水</span>
      </div>
      <div class="filter-bar">
        <button
          v-for="ft in historyTypes"
          :key="ft.key"
          type="button"
          class="filter-chip"
          :class="{ active: activeType === ft.key }"
          @click="activeType = ft.key"
        >{{ ft.label }}</button>
      </div>

      <div v-if="filteredHistory.length === 0" class="empty-hint">暂无记录</div>
      <div
        v-for="item in filteredHistory"
        :key="item.id"
        class="history-row"
        @click="openDetail(item)"
      >
        <div class="history-left">
          <span class="history-type">{{ item.typeLabel }}</span>
          <span class="history-time">{{ item.time }}</span>
        </div>
        <div class="history-right">
          <span class="history-amount" :class="item.signed === '+' ? 'up' : 'down'">
            {{ item.signed }}{{ money(item.amount, 4) }} {{ item.symbol }}
          </span>
          <van-icon name="arrow" size="14" color="#94A3B8" />
        </div>
      </div>
    </section>

    <div class="bottom-actions">
      <button class="act-btn ghost" type="button" @click="showTransfer = true">划转</button>
      <button class="act-btn ghost" type="button" @click="openDeposit('USDT')">充值</button>
      <button class="act-btn ghost" type="button" @click="openWithdraw('USDT')">提现</button>
      <button class="act-btn primary" type="button" @click="goTrade">交易</button>
    </div>

    <TransferModal v-model:show="showTransfer" default-from="spot" />

    <van-popup v-model:show="showBill" round position="bottom">
      <div class="bill-detail" v-if="currentBill">
        <div class="bill-head">
          <span class="bill-title">{{ currentBill.typeLabel }}明细</span>
          <van-icon name="cross" @click="showBill = false" />
        </div>
        <div class="bill-row"><span>类型</span><strong>{{ currentBill.typeLabel }}</strong></div>
        <div class="bill-row"><span>数量</span><strong>{{ currentBill.signed }}{{ money(currentBill.amount, 4) }} {{ currentBill.symbol }}</strong></div>
        <div class="bill-row"><span>时间</span><strong>{{ currentBill.time }}</strong></div>
        <div class="bill-row"><span>Tx Hash</span><strong class="tx">{{ currentBill.txHash }}</strong></div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { formatNumber } from '@/utils/format'
import { useAmountPrivacy } from '@/composables/useAmountPrivacy'
import { useAssetActions } from '@/composables/useAssetActions'
import { spotDetailMock, spotHistoryMock, historyTypes } from '@/data/assetMock'
import Sparkline from './Sparkline.vue'
import TransferModal from './TransferModal.vue'
import CryptoIcon from './CryptoIcon.vue'

defineOptions({ name: 'SpotAccountDetail' })

const router = useRouter()
const { isAmountHidden, toggleAmountHidden } = useAmountPrivacy()
const { openDeposit, openWithdraw } = useAssetActions()

const detail = spotDetailMock
const activeType = ref('all')
const showTransfer = ref(false)
const showBill = ref(false)
const currentBill = ref(null)

const money = (value, digits = 2) => (isAmountHidden.value ? '****' : formatNumber(value, digits))
const signedMoney = (value, digits = 2) => {
  if (isAmountHidden.value) return '****'
  const sign = value >= 0 ? '+' : '-'
  return `${sign}${formatNumber(Math.abs(value), digits)}`
}
const signedPercent = (value) => `${value >= 0 ? '+' : ''}${formatNumber(value, 2)}%`
const pnlTone = (value) => (value >= 0 ? 'up' : 'down')

const filteredHistory = computed(() => {
  if (activeType.value === 'all') return spotHistoryMock
  return spotHistoryMock.filter((h) => h.type === activeType.value)
})

const openDetail = (item) => {
  currentBill.value = item
  showBill.value = true
}

const goTrade = () => {
  // TODO: 若后续新增独立现货交易路由，替换为对应路由
  router.push('/trade')
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

.detail-title {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
}

.hero-card {
  margin: 16px;
  padding: 20px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
}

.hero-label {
  font-size: 13px;
  color: #64748b;
}

.hero-total {
  margin: 8px 0 4px;
  font-size: 30px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.hero-pnl {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.up { color: #00b976; }
.down { color: #ef4444; }

.balance-row {
  display: flex;
  gap: 12px;
  margin: 0 16px 16px;
}

.balance-item {
  flex: 1;
  padding: 16px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bal-label {
  font-size: 12px;
  color: #64748b;
}

.bal-value {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.list-section {
  margin: 0 16px 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.section-head {
  margin-bottom: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
}

.asset-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.asset-row:last-child { border-bottom: none; }

.asset-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.coin-badge {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  color: #ffffff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.coin-meta { display: flex; flex-direction: column; gap: 2px; }
.coin-symbol { font-size: 15px; font-weight: 700; }
.coin-name { font-size: 12px; color: #94a3b8; }

.asset-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.coin-amount { font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }
.coin-value { font-size: 12px; color: #64748b; font-variant-numeric: tabular-nums; }
.coin-change { font-style: normal; margin-left: 4px; }

.filter-bar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.filter-chip {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid #e6ebf2;
  background: #f8fafc;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.filter-chip.active { background: #fff7e0; border-color: #f0b90b; color: #b7791f; }

.history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
}
.history-row:last-child { border-bottom: none; }
.history-left { display: flex; flex-direction: column; gap: 2px; }
.history-type { font-size: 14px; font-weight: 600; }
.history-time { font-size: 12px; color: #94a3b8; }
.history-right { display: flex; align-items: center; gap: 6px; }
.history-amount { font-size: 14px; font-weight: 700; font-variant-numeric: tabular-nums; }

.empty-hint { padding: 20px 0; text-align: center; color: #94a3b8; font-size: 13px; }

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

.bill-detail { padding: 20px 16px calc(20px + env(safe-area-inset-bottom)); }
.bill-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.bill-title { font-size: 17px; font-weight: 700; }
.bill-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
.bill-row span { color: #64748b; }
.bill-row .tx { font-size: 12px; word-break: break-all; text-align: right; max-width: 60%; }

:global(html[data-theme='dark']) .detail-page,
:global(html[data-theme='dark']) .bill-detail {
  background: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
}

:global(html[data-theme='dark']) .detail-header,
:global(html[data-theme='dark']) .hero-card,
:global(html[data-theme='dark']) .balance-item,
:global(html[data-theme='dark']) .list-section,
:global(html[data-theme='dark']) .bottom-actions {
  background: var(--color-bg-card) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .filter-chip,
:global(html[data-theme='dark']) .act-btn.ghost {
  background: var(--color-bg-input) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-secondary) !important;
}

:global(html[data-theme='dark']) .filter-chip.active {
  background: rgb(var(--color-primary-rgb) / 0.14) !important;
  border-color: var(--color-primary-border) !important;
  color: var(--color-primary) !important;
}

:global(html[data-theme='dark']) .asset-row,
:global(html[data-theme='dark']) .history-row,
:global(html[data-theme='dark']) .bill-row {
  border-color: var(--color-border) !important;
}

:global(html[data-theme='dark']) .coin-value,
:global(html[data-theme='dark']) .coin-name,
:global(html[data-theme='dark']) .history-time,
:global(html[data-theme='dark']) .bill-row span {
  color: var(--color-text-secondary) !important;
}
</style>
