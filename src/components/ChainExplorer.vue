<template>
  <div class="chain-monitor-page">
    <header class="monitor-header">
      <button class="icon-button" type="button" :aria-label="t('common.cancel')" @click="handleBack">
        <van-icon name="arrow-left" />
      </button>

      <div class="header-copy">
        <h1>{{ t('monitor.title') }}</h1>
        <div class="live-row">
          <span class="live-dot"></span>
          <strong>{{ t('monitor.live') }}</strong>
          <span>{{ t('monitor.auto_refreshing') }}</span>
          <span>{{ t('monitor.last_updated', { time: lastUpdatedLabel }) }}</span>
        </div>
      </div>

      <button
        class="refresh-button"
        type="button"
        :class="{ refreshing: isRefreshing }"
        :aria-label="t('monitor.refresh')"
        @click="handleManualRefresh"
      >
        <van-icon name="replay" />
      </button>
    </header>

    <section class="metrics-grid">
      <div class="metric-card">
        <span>{{ t('monitor.gas') }}</span>
        <strong>{{ currentGas }} <small>Gwei</small></strong>
      </div>
      <div class="metric-card">
        <span>{{ t('monitor.block_height') }}</span>
        <strong>{{ formatInteger(blockHeight) }}</strong>
      </div>
      <div class="metric-card">
        <span>{{ t('monitor.net_flow') }}</span>
        <strong>{{ formatFiat(netFlowUsd) }} <small>USD</small></strong>
      </div>
    </section>

    <section class="terminal-panel">
      <div class="terminal-titlebar">
        <div>
          <h2>{{ t('monitor.table_title') }}</h2>
          <p>{{ t('monitor.table_subtitle') }}</p>
        </div>
        <span class="stream-pill">{{ t('monitor.stream_count', { count: transactions.length }) }}</span>
      </div>

      <div class="tx-table" role="table">
        <div class="tx-header" role="row">
          <div role="columnheader">{{ t('monitor.time') }}</div>
          <div role="columnheader">{{ t('monitor.type') }}</div>
          <div role="columnheader">{{ t('monitor.hash') }}</div>
          <div role="columnheader">{{ t('monitor.amount') }}</div>
          <div role="columnheader">{{ t('monitor.status_label') }}</div>
        </div>

        <transition-group name="tx-insert" tag="div" class="tx-body">
          <div
            v-for="tx in transactions"
            :key="tx.id"
            class="tx-row"
            :class="[`status-${tx.status}`, { fresh: tx.isFresh }]"
            role="row"
          >
            <div class="tx-time" role="cell">{{ formatTime(tx.createdAt) }}</div>

            <div class="tx-type" :class="`type-${tx.type}`" role="cell">
              <van-icon :name="typeMeta[tx.type].icon" />
              <span>{{ t(typeMeta[tx.type].labelKey) }}</span>
            </div>

            <div class="tx-hash" role="cell" :title="tx.hash">
              <span>{{ shortHash(tx.hash) }}</span>
            </div>

            <div class="tx-amount" role="cell">
              <strong>{{ formatCrypto(tx.amount.value, tx.amount.asset) }}</strong>
              <small>{{ formatFiat(tx.fiatValue) }} USD</small>
            </div>

            <div class="tx-status" role="cell">
              <span class="status-badge" :class="`badge-${tx.status}`">
                {{ t(statusMeta[tx.status].labelKey) }}
              </span>
            </div>
          </div>
        </transition-group>

        <div v-if="transactions.length === 0" class="empty-state">
          <van-icon name="orders-o" />
          <span>{{ t('monitor.empty') }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { formatInteger } from '@/utils/format'

defineOptions({ name: 'ChainExplorer' })

const router = useRouter()
const { t, locale } = useI18n()

const TX_TYPES = ['deposit', 'withdraw', 'internal_transfer']
const TX_STATUSES = ['pending', 'confirming', 'confirmed', 'failed', 'dropped']
const ASSETS = ['ETH', 'SOL', 'BTC', 'USDT']

const typeMeta = {
  deposit: { labelKey: 'monitor.deposit', icon: 'arrow-down' },
  withdraw: { labelKey: 'monitor.withdraw', icon: 'arrow-up' },
  internal_transfer: { labelKey: 'monitor.internal_transfer', icon: 'exchange' }
}

const statusMeta = {
  pending: { labelKey: 'monitor.status.pending' },
  confirming: { labelKey: 'monitor.status.confirming' },
  confirmed: { labelKey: 'monitor.status.confirmed' },
  failed: { labelKey: 'monitor.status.failed' },
  dropped: { labelKey: 'monitor.status.dropped' }
}

const assetConfig = {
  ETH: { min: 0.05, max: 240, decimals: 5, price: 3100 },
  SOL: { min: 4, max: 6000, decimals: 3, price: 140 },
  BTC: { min: 0.001, max: 7, decimals: 6, price: 92000 },
  USDT: { min: 50, max: 420000, decimals: 2, price: 1 }
}

const transactions = ref([])
const currentGas = ref(24)
const blockHeight = ref(18293000)
const netFlowUsd = ref(45200000)
const lastUpdatedAt = ref(Date.now())
const isRefreshing = ref(false)

let streamTimer = null
let gasTimer = null
let blockTimer = null
let freshTimers = []
let txIndex = 0

const lastUpdatedLabel = computed(() => formatTime(lastUpdatedAt.value))

const randomItem = (items) => items[Math.floor(Math.random() * items.length)]

const randomBetween = (min, max, decimals = 2) => {
  return Number((Math.random() * (max - min) + min).toFixed(decimals))
}

const generateFullHash = () => {
  const chars = '0123456789abcdef'
  const body = Array.from({ length: 64 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
  return `0x${body}`
}

const generateAmount = (asset) => {
  const config = assetConfig[asset]
  return randomBetween(config.min, config.max, config.decimals)
}

const createTransaction = () => {
  const asset = randomItem(ASSETS)
  const value = generateAmount(asset)
  const fiatValue = value * assetConfig[asset].price
  const type = randomItem(TX_TYPES)
  const direction = type === 'withdraw' ? -1 : 1

  return {
    id: `${Date.now()}-${txIndex++}`,
    createdAt: Date.now(),
    type,
    hash: generateFullHash(),
    amount: { value, asset },
    fiatValue,
    status: 'pending',
    isFresh: true,
    index: txIndex,
    direction
  }
}

const pushTransaction = () => {
  const tx = createTransaction()
  transactions.value.unshift(tx)
  netFlowUsd.value += tx.fiatValue * tx.direction
  lastUpdatedAt.value = Date.now()

  if (transactions.value.length > 60) {
    transactions.value.pop()
  }

  freshTimers.push(setTimeout(() => {
    tx.isFresh = false
  }, 900))

  advanceTransaction(tx)
}

const advanceTransaction = (tx) => {
  freshTimers.push(setTimeout(() => {
    if (tx.status !== 'pending') return
    tx.status = 'confirming'
    lastUpdatedAt.value = Date.now()
  }, randomBetween(900, 1800, 0)))

  freshTimers.push(setTimeout(() => {
    if (tx.status !== 'confirming') return
    const roll = Math.random()
    if (roll < 0.78) tx.status = 'confirmed'
    else if (roll < 0.9) tx.status = 'failed'
    else tx.status = 'dropped'
    lastUpdatedAt.value = Date.now()
  }, randomBetween(2600, 5200, 0)))
}

const startStream = () => {
  const next = () => {
    pushTransaction()
    streamTimer = setTimeout(next, randomBetween(1100, 2400, 0))
  }
  next()
}

const startMetrics = () => {
  gasTimer = setInterval(() => {
    currentGas.value = Math.floor(randomBetween(18, 36, 0))
    lastUpdatedAt.value = Date.now()
  }, 2200)

  blockTimer = setInterval(() => {
    blockHeight.value += Math.floor(randomBetween(1, 4, 0))
    lastUpdatedAt.value = Date.now()
  }, 1600)
}

const handleManualRefresh = async () => {
  if (isRefreshing.value) return
  isRefreshing.value = true
  try {
    pushTransaction()
    currentGas.value = Math.floor(randomBetween(18, 36, 0))
    blockHeight.value += Math.floor(randomBetween(1, 4, 0))
    lastUpdatedAt.value = Date.now()
    showToast({ message: t('monitor.refresh_success'), icon: 'success', duration: 1400 })
  } finally {
    setTimeout(() => {
      isRefreshing.value = false
    }, 450)
  }
}

const formatTime = (time) => {
  return new Date(time).toLocaleTimeString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatFiat = (value) => {
  const absolute = Math.abs(Number(value) || 0)
  const sign = Number(value) < 0 ? '-' : ''
  if (absolute >= 1000000) return `${sign}$${(absolute / 1000000).toFixed(2)}M`
  if (absolute >= 1000) return `${sign}$${(absolute / 1000).toFixed(1)}K`
  return `${sign}$${absolute.toFixed(2)}`
}

const formatCrypto = (value, asset) => {
  const decimals = assetConfig[asset]?.decimals ?? 4
  return `${Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: Math.min(decimals, 2),
    maximumFractionDigits: decimals
  })} ${asset}`
}

const shortHash = (hash) => `${hash.slice(0, 8)}...${hash.slice(-6)}`

const handleBack = () => {
  router.back()
}

onMounted(() => {
  for (let index = 0; index < 8; index += 1) {
    freshTimers.push(setTimeout(pushTransaction, index * 180))
  }
  startStream()
  startMetrics()
})

onUnmounted(() => {
  if (streamTimer) clearTimeout(streamTimer)
  if (gasTimer) clearInterval(gasTimer)
  if (blockTimer) clearInterval(blockTimer)
  freshTimers.forEach(timer => clearTimeout(timer))
  freshTimers = []
})
</script>

<style scoped>
.chain-monitor-page {
  min-height: 100vh;
  padding-bottom: 22px;
  color: var(--color-text-primary);
  background:
    linear-gradient(180deg, rgb(var(--color-primary-rgb) / 0.06) 0, rgb(var(--color-primary-rgb) / 0) 240px),
    var(--color-surface-1);
}

.monitor-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 40px 1fr 40px;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  background: rgb(var(--color-surface-2-rgb) / 0.92);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(18px);
}

.icon-button,
.refresh-button {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  color: var(--color-text-primary);
  background: var(--color-surface-1);
}

.refresh-button.refreshing {
  animation: spin 0.9s linear infinite;
}

.header-copy {
  min-width: 0;
}

.header-copy h1 {
  margin: 0;
  font-size: 18px;
  line-height: 1.25;
  font-weight: 850;
}

.live-row {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-items: center;
  margin-top: 5px;
  color: var(--color-text-secondary);
  font-size: 11px;
}

.live-row strong {
  color: var(--color-success);
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--color-success);
  box-shadow: 0 0 0 5px rgb(var(--color-success-rgb) / 0.12);
  animation: pulse 1.6s ease-in-out infinite;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px;
}

.metric-card,
.terminal-panel {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.metric-card {
  min-width: 0;
  padding: 15px;
  border-radius: 16px;
}

.metric-card span {
  display: block;
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 750;
}

.metric-card strong {
  display: block;
  margin-top: 7px;
  font-size: 19px;
  font-weight: 850;
  font-variant-numeric: tabular-nums;
}

.metric-card small {
  color: var(--color-text-secondary);
  font-size: 11px;
}

.terminal-panel {
  margin: 0 16px;
  overflow: hidden;
  border-radius: 18px;
}

.terminal-titlebar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
}

.terminal-titlebar h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 850;
}

.terminal-titlebar p {
  margin: 4px 0 0;
  color: var(--color-text-secondary);
  font-size: 12px;
}

.stream-pill {
  flex: 0 0 auto;
  padding: 7px 10px;
  border-radius: 999px;
  color: var(--color-success);
  background: rgb(var(--color-success-rgb) / 0.1);
  border: 1px solid rgb(var(--color-success-rgb) / 0.18);
  font-size: 11px;
  font-weight: 800;
}

.tx-table {
  overflow-x: auto;
}

.tx-header,
.tx-row {
  min-width: 760px;
  display: grid;
  grid-template-columns: 96px 170px minmax(210px, 1fr) 170px 130px;
  align-items: center;
}

.tx-header {
  min-height: 42px;
  padding: 0 16px;
  color: var(--color-text-muted);
  background: var(--color-surface-1);
  border-bottom: 1px solid var(--color-border);
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.03em;
}

.tx-body {
  display: block;
}

.tx-row {
  min-height: 58px;
  padding: 0 16px;
  border-bottom: 1px solid var(--color-border-subtle);
  transition: background 220ms ease, opacity 220ms ease;
}

.tx-row.fresh {
  background: rgb(var(--color-primary-rgb) / 0.1);
}

.tx-row.status-dropped {
  opacity: 0.58;
}

.tx-time,
.tx-hash,
.tx-amount,
.tx-status,
.tx-type {
  min-width: 0;
  font-size: 12px;
}

.tx-time,
.tx-hash {
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

.tx-hash span {
  display: inline-block;
  max-width: 100%;
  padding: 5px 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
  border-radius: 8px;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border-subtle);
  white-space: nowrap;
}

.tx-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 800;
}

.tx-type .van-icon {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: var(--color-surface-1);
}

.type-deposit {
  color: var(--color-success);
}

.type-withdraw {
  color: var(--color-danger);
}

.type-internal_transfer {
  color: var(--color-primary-hover);
}

.tx-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.tx-amount strong {
  font-size: 13px;
}

.tx-amount small {
  color: var(--color-text-muted);
  font-size: 10px;
}

.tx-status {
  text-align: right;
}

.status-badge {
  display: inline-flex;
  justify-content: center;
  min-width: 90px;
  padding: 7px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 850;
}

.badge-pending,
.badge-dropped {
  color: var(--color-text-secondary);
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
}

.badge-confirming {
  color: var(--color-primary-hover);
  background: rgb(var(--color-primary-rgb) / 0.12);
  border: 1px solid rgb(var(--color-primary-rgb) / 0.24);
}

.badge-confirmed {
  color: var(--color-success);
  background: rgb(var(--color-success-rgb) / 0.1);
  border: 1px solid rgb(var(--color-success-rgb) / 0.2);
}

.badge-failed {
  color: var(--color-danger);
  background: rgb(var(--color-danger-rgb) / 0.1);
  border: 1px solid rgb(var(--color-danger-rgb) / 0.2);
}

.empty-state {
  display: grid;
  place-items: center;
  gap: 8px;
  padding: 42px 16px;
  color: var(--color-text-secondary);
}

.empty-state .van-icon {
  font-size: 28px;
}

.tx-insert-enter-active {
  transition: all 260ms ease;
}

.tx-insert-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.45;
  }
}

@media (max-width: 720px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .monitor-header {
    align-items: start;
  }

  .tx-header,
  .tx-row {
    min-width: 700px;
    grid-template-columns: 90px 150px minmax(190px, 1fr) 150px 120px;
  }
}
</style>
