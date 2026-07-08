<template>
  <div class="detail-page">
    <header class="detail-header">
      <button class="icon-btn" type="button" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="detail-title">IEO 账户</h1>
      <button class="icon-btn" type="button" @click="toggleAmountHidden">
        <van-icon :name="isAmountHidden ? 'closed-eye' : 'eye-o'" size="20" />
      </button>
    </header>

    <section class="hero-card">
      <div class="hero-stats">
        <div class="stat">
          <span class="stat-label">待解锁资产 (USDT)</span>
          <span class="stat-value">{{ money(detail.pendingUnlock) }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">已中签资产 (USDT)</span>
          <span class="stat-value">{{ money(detail.wonAssets) }}</span>
        </div>
      </div>
    </section>

    <section class="list-section">
      <div class="section-head"><span class="section-title">IEO 项目仓位</span></div>

      <div class="ieo-row" v-for="p in detail.projects" :key="p.id">
        <div class="ieo-left">
          <span class="ieo-name">{{ p.name }}</span>
          <span class="ieo-sub">
            <template v-if="p.status === 'won'">中签数量 {{ money(p.amount, 0) }}</template>
            <template v-else-if="p.status === 'pending'">认购数量 {{ money(p.amount, 0) }}</template>
            <template v-else>已自动退款 {{ money(p.refund) }} USDT</template>
          </span>
        </div>
        <div class="ieo-right">
          <span v-if="p.status === 'won'" class="ieo-value">{{ money(p.value) }} USDT</span>
          <span class="status-badge" :class="p.status">{{ statusLabel(p.status) }}</span>
        </div>
      </div>
    </section>

    <div class="bottom-actions">
      <button class="act-btn ghost" type="button" @click="showTransfer = true">划转</button>
      <button class="act-btn primary" type="button" @click="router.push('/ido')">去打新</button>
    </div>

    <TransferModal v-model:show="showTransfer" default-from="ieo" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { formatNumber } from '@/utils/format'
import { useAmountPrivacy } from '@/composables/useAmountPrivacy'
import { ieoDetailMock } from '@/data/assetMock'
import TransferModal from './TransferModal.vue'

defineOptions({ name: 'IeoAccountDetail' })

const router = useRouter()
const { isAmountHidden, toggleAmountHidden } = useAmountPrivacy()

const detail = ieoDetailMock
const showTransfer = ref(false)

const money = (value, digits = 2) => (isAmountHidden.value ? '****' : formatNumber(value, digits))

const statusLabel = (status) => {
  if (status === 'won') return '已中签'
  if (status === 'pending') return '待中签'
  return '未中签 / 已退款'
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

.hero-stats { display: flex; gap: 16px; }
.stat { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.stat-label { font-size: 12px; color: #64748b; }
.stat-value { font-size: 22px; font-weight: 800; font-variant-numeric: tabular-nums; }

.list-section {
  margin: 0 16px 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.section-head { margin-bottom: 12px; }
.section-title { font-size: 15px; font-weight: 700; }

.ieo-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}
.ieo-row:last-child { border-bottom: none; }

.ieo-left { display: flex; flex-direction: column; gap: 4px; }
.ieo-name { font-size: 15px; font-weight: 700; }
.ieo-sub { font-size: 12px; color: #94a3b8; }

.ieo-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.ieo-value { font-size: 14px; font-weight: 700; font-variant-numeric: tabular-nums; }

.status-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.status-badge.won { background: #e6f9f1; color: #00b976; }
.status-badge.pending { background: #fff3e0; color: #f59e0b; }
.status-badge.failed { background: #f1f5f9; color: #94a3b8; }

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

:global(html[data-theme='dark']) .act-btn.ghost,
:global(html[data-theme='dark']) .status-badge.failed {
  background: var(--color-bg-input) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-secondary) !important;
}

:global(html[data-theme='dark']) .status-badge.won {
  background: rgb(16 185 129 / 0.14) !important;
  color: #34D399 !important;
}

:global(html[data-theme='dark']) .status-badge.pending {
  background: rgb(var(--color-primary-rgb) / 0.14) !important;
  color: var(--color-primary) !important;
}

:global(html[data-theme='dark']) .ieo-row {
  border-color: var(--color-border) !important;
}

:global(html[data-theme='dark']) .stat-label,
:global(html[data-theme='dark']) .ieo-sub {
  color: var(--color-text-secondary) !important;
}
</style>
