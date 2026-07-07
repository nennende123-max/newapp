<template>
  <div class="earn-page">
    <main class="earn-content">
      <section class="asset-overview-card">
        <span class="overview-kicker">{{ t('miner.earn_assets') }}</span>
        <strong>{{ formatMoney(earnAssets) }} <small>USDT</small></strong>
        <div class="overview-stats">
          <div>
            <span>{{ t('miner.accumulated_earnings') }}</span>
            <b>{{ formatMoney(accumulatedEarnings) }} USDT</b>
          </div>
          <div>
            <span>{{ t('miner.today_earnings') }}</span>
            <b>{{ formatMoney(todayEstimatedInterest) }} USDT</b>
          </div>
        </div>
      </section>

      <div class="earn-tabs" role="tablist">
        <button
          type="button"
          :class="{ active: activeEarnTab === 'token' }"
          @click="activeEarnTab = 'token'"
        >
          {{ t('miner.token_earn') }}
        </button>
        <button
          type="button"
          :class="{ active: activeEarnTab === 'interest' }"
          @click="activeEarnTab = 'interest'"
        >
          {{ t('miner.interest_earn') }}
        </button>
      </div>

      <section v-if="activeEarnTab === 'token'" class="product-card">
        <div class="product-head">
          <div>
            <span class="status-badge">{{ t('miner.open') }}</span>
            <h1>{{ t('miner.crypto_earns_crypto') }}</h1>
            <p>{{ t('miner.crypto_earns_crypto_subtitle') }}</p>
          </div>
          <div class="apy-block">
            <strong>12% - 28%</strong>
            <span>{{ t('miner.est_apy') }}</span>
          </div>
        </div>

        <div class="product-highlight">
          <div>
            <span>{{ t('miner.reward_token') }}</span>
            <strong>{{ rewardToken }}</strong>
          </div>
          <div>
            <span>{{ t('miner.estimated_reward') }}</span>
            <strong>{{ formatToken(userEstimatedReward) }} {{ rewardToken }}</strong>
          </div>
        </div>

        <div class="meta-block">
          <span>{{ t('miner.cycle_label') }}</span>
          <div class="term-chips">
            <button
              v-for="term in termOptions"
              :key="term"
              type="button"
              :class="{ active: selectedTerm === term }"
              @click="selectedTerm = term"
            >
              {{ term }}{{ t('earn.days') }}
            </button>
          </div>
        </div>

        <div class="form-panel">
          <button class="selector-field" type="button" @click="openAssetSheet('token')">
            <span>{{ t('miner.select_asset') }}</span>
            <strong>{{ selectedStakeAsset }} <van-icon name="arrow" /></strong>
          </button>
          <label class="amount-field">
            <span>{{ t('miner.input_amount') }}</span>
            <input v-model="stakeAmount" type="number" inputmode="decimal" min="0" />
          </label>
          <div class="estimate-row">
            <span>{{ t('miner.estimated_reward') }}</span>
            <strong>{{ formatToken(userEstimatedReward) }} {{ rewardToken }}</strong>
          </div>
        </div>

        <button class="primary-action" type="button" @click="joinCryptoEarn">
          {{ t('miner.join_now') }}
        </button>
      </section>

      <section v-else class="product-card">
        <div class="product-head">
          <div>
            <span class="status-badge">{{ t('miner.open') }}</span>
            <h1>{{ t('miner.crypto_earns_interest') }}</h1>
            <p>{{ t('miner.crypto_earns_interest_subtitle') }}</p>
          </div>
          <div class="apy-block">
            <strong>0.6%</strong>
            <span>{{ t('miner.daily_rate') }}</span>
          </div>
        </div>

        <div class="interest-metrics">
          <div>
            <span>{{ t('miner.select_asset') }}</span>
            <strong>{{ depositAsset }}</strong>
          </div>
          <div>
            <span>{{ t('miner.estimated_apr') }}</span>
            <strong>219%</strong>
          </div>
          <div>
            <span>{{ t('miner.interest_method') }}</span>
            <strong>{{ t('miner.daily_interest') }}</strong>
          </div>
          <div>
            <span>{{ t('miner.today_estimated') }}</span>
            <strong>{{ formatAmount(todayEstimatedInterest) }} {{ depositAsset }}</strong>
          </div>
        </div>

        <div class="form-panel">
          <button class="selector-field" type="button" @click="openAssetSheet('interest')">
            <span>{{ t('miner.select_asset') }}</span>
            <strong>{{ depositAsset }} <van-icon name="arrow" /></strong>
          </button>
          <label class="amount-field">
            <span>{{ t('miner.subscribe_amount') }}</span>
            <input v-model="depositAmount" type="number" inputmode="decimal" min="0" />
          </label>
          <div class="estimate-row">
            <span>{{ t('miner.accumulated_interest') }}</span>
            <strong>{{ formatAmount(accumulatedInterest) }} {{ depositAsset }}</strong>
          </div>
        </div>

        <button class="primary-action" type="button" @click="subscribeInterestEarn">
          {{ t('miner.subscribe_now') }}
        </button>
      </section>

      <section class="records-card">
        <div class="records-head">
          <h2>{{ t('miner.my_income_records') }}</h2>
          <span>{{ activeEarnTab === 'token' ? t('miner.token_earn_records') : t('miner.interest_earn_records') }}</span>
        </div>

        <div v-if="currentRecords.length === 0" class="empty-state">
          <van-icon name="orders-o" />
          <strong>{{ t('miner.no_income_records') }}</strong>
        </div>

        <article v-for="record in visibleRecords" v-else :key="record.id" class="record-card">
          <div class="record-title">
            <strong>{{ record.typeLabel }}</strong>
            <span class="status-badge subtle">{{ record.statusLabel }}</span>
          </div>
          <div class="record-grid">
            <span>{{ activeEarnTab === 'token' ? t('miner.investment_asset') : t('miner.subscription_asset') }}</span>
            <b>{{ record.asset }}</b>
            <span>{{ activeEarnTab === 'token' ? t('miner.investment_amount') : t('miner.subscription_amount') }}</span>
            <b>{{ formatAmount(record.amount) }}</b>
            <span>{{ activeEarnTab === 'token' ? t('miner.reward_token') : t('miner.daily_rate') }}</span>
            <b>{{ activeEarnTab === 'token' ? rewardToken : '0.6%' }}</b>
            <span>{{ activeEarnTab === 'token' ? t('miner.estimated_reward') : t('miner.accumulated_interest') }}</span>
            <b>{{ record.rewardDisplay }}</b>
          </div>
        </article>

        <button
          v-if="currentRecords.length > 2"
          class="view-all-action"
          type="button"
          @click="showAllRecords = !showAllRecords"
        >
          {{ showAllRecords ? t('launchpad_subscribe.collapse') : t('launchpad_subscribe.view_all') }}
        </button>
      </section>
    </main>

    <van-popup
      v-model:show="showAssetSheet"
      position="bottom"
      round
      closeable
      class="asset-sheet"
      :overlay-style="{ background: 'rgba(0,0,0,0.35)' }"
    >
      <div class="sheet-handle"></div>
      <h2>{{ t('miner.select_asset') }}</h2>
      <div class="asset-list">
        <button
          v-for="asset in supportedStakeAssets"
          :key="asset"
          type="button"
          :class="{ active: currentSheetAsset === asset }"
          @click="selectAsset(asset)"
        >
          <span>
            <strong>{{ asset }}</strong>
            <small>{{ assetFullName(asset) }}</small>
          </span>
          <van-icon v-if="currentSheetAsset === asset" name="success" />
        </button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'

defineOptions({ name: 'Miner' })

const { t } = useI18n()

const DAY_SECONDS = 86400
const now = ref(Date.now())
const activeEarnTab = ref('token')
const showAssetSheet = ref(false)
const showAllRecords = ref(false)
const assetSheetMode = ref('token')
const selectedStakeAsset = ref('USDT')
const stakeAmount = ref(100)
const selectedTerm = ref(15)
const campaignStartTime = ref(Date.now() - 6 * 60 * 60 * 1000)
const stakeStartTime = ref(Date.now() - 2 * 60 * 60 * 1000)
const stakeEndTime = ref(Date.now() + 15 * 24 * 60 * 60 * 1000)
const rewardToken = ref('NEW')
const rewardPoolAmount = ref(600000)
const totalPoolStakeAmount = ref(1200000)
const principalLocked = ref(0)
const depositAsset = ref('USDT')
const depositAmount = ref(1000)
const dailyRate = ref(0.006)
const interestStartTime = ref(Date.now() - 4 * 60 * 60 * 1000)
const interestEndTime = ref(Date.now() + 30 * 24 * 60 * 60 * 1000)
const earnCryptoRecords = reactive([])
const earnInterestRecords = reactive([])
const supportedStakeAssets = ['USDT', 'BNB', 'ETH', 'BTC', 'SOL']
const termOptions = [7, 15, 30]

let timer = null

const activeSeconds = computed(() => {
  return Math.max(0, (Math.min(now.value, stakeEndTime.value) - stakeStartTime.value) / 1000)
})

const durationSeconds = computed(() => {
  return Math.max(1, (stakeEndTime.value - campaignStartTime.value) / 1000)
})

const userEstimatedReward = computed(() => {
  const userShare = Number(stakeAmount.value) / Number(totalPoolStakeAmount.value)
  const timeRatio = Math.min(1, activeSeconds.value / durationSeconds.value)
  return Number(rewardPoolAmount.value) * userShare * timeRatio
})

const userFinalReward = computed(() => {
  return now.value >= stakeEndTime.value ? userEstimatedReward.value : 0
})

const interestActiveSeconds = computed(() => {
  return Math.max(0, (Math.min(now.value, interestEndTime.value) - interestStartTime.value) / 1000)
})

const todayEstimatedInterest = computed(() => {
  return Number(depositAmount.value) * Number(dailyRate.value)
})

const accumulatedInterest = computed(() => {
  return Number(depositAmount.value) * Number(dailyRate.value) * (interestActiveSeconds.value / DAY_SECONDS)
})

const finalInterest = computed(() => {
  return now.value >= interestEndTime.value ? accumulatedInterest.value : 0
})

const earnAssets = computed(() => {
  return Number(principalLocked.value) + Number(depositAmount.value)
})

const accumulatedEarnings = computed(() => {
  return accumulatedInterest.value + (userEstimatedReward.value * 0.045)
})

const earnRecords = computed(() => {
  const cryptoRecords = earnCryptoRecords.map(record => ({
    ...record,
    kind: 'token',
    typeLabel: t('miner.crypto_earns_crypto'),
    rewardDisplay: `${formatToken(userFinalReward.value || userEstimatedReward.value)} ${rewardToken.value}`,
    statusLabel: now.value >= stakeEndTime.value ? t('miner.unlockable') : t('miner.active')
  }))
  const interestRecords = earnInterestRecords.map(record => ({
    ...record,
    kind: 'interest',
    typeLabel: t('miner.crypto_earns_interest'),
    rewardDisplay: `${formatAmount(finalInterest.value || accumulatedInterest.value)} ${record.asset}`,
    statusLabel: now.value >= interestEndTime.value ? t('miner.claimable') : t('miner.active')
  }))
  return [...cryptoRecords, ...interestRecords]
})

const currentRecords = computed(() => (
  earnRecords.value.filter(record => record.kind === activeEarnTab.value)
))

const visibleRecords = computed(() => (
  showAllRecords.value ? currentRecords.value : currentRecords.value.slice(0, 2)
))

const currentSheetAsset = computed(() => (
  assetSheetMode.value === 'interest' ? depositAsset.value : selectedStakeAsset.value
))

const formatMoney = (value) => {
  return Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatToken = (value) => {
  return Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4
  })
}

const formatAmount = (value) => {
  return Number(value || 0).toLocaleString('en-US', {
    maximumFractionDigits: 6
  })
}

const assetFullName = (asset) => ({
  USDT: 'Tether USD',
  BNB: 'BNB',
  ETH: 'Ethereum',
  BTC: 'Bitcoin',
  SOL: 'Solana'
}[asset] || asset)

const openAssetSheet = (mode = activeEarnTab.value) => {
  assetSheetMode.value = mode
  showAssetSheet.value = true
}

const selectAsset = (asset) => {
  if (assetSheetMode.value === 'interest') {
    depositAsset.value = asset
  } else {
    selectedStakeAsset.value = asset
  }
  showAssetSheet.value = false
}

const joinCryptoEarn = () => {
  principalLocked.value += Number(stakeAmount.value)
  earnCryptoRecords.unshift({
    id: `crypto-${Date.now()}`,
    asset: selectedStakeAsset.value,
    amount: Number(stakeAmount.value),
    term: selectedTerm.value
  })
  showToast({ message: t('miner.join_success'), icon: 'success' })
}

const subscribeInterestEarn = () => {
  earnInterestRecords.unshift({
    id: `interest-${Date.now()}`,
    asset: depositAsset.value,
    amount: Number(depositAmount.value)
  })
  showToast({ message: t('miner.subscribe_success'), icon: 'success' })
}

onMounted(() => {
  timer = setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.earn-page {
  --earn-bg: var(--color-bg);
  --earn-card: var(--color-bg-card);
  --earn-panel: var(--color-surface-1);
  --earn-soft: var(--color-surface-muted);
  --earn-yellow: var(--color-primary);
  --earn-yellow-soft: var(--color-primary-soft);
  --earn-yellow-text: var(--color-text-on-accent);
  --earn-text: var(--color-text-primary);
  --earn-muted: var(--color-text-secondary);
  --earn-subtle: var(--color-text-muted);
  --earn-border: var(--color-border);
  --earn-success: var(--color-earn);
  min-height: 100vh;
  padding-bottom: calc(76px + env(safe-area-inset-bottom));
  background: var(--earn-bg);
  color: var(--earn-text);
  font-family: var(--font-ui);
  font-variant-numeric: tabular-nums;
}

.earn-page,
.earn-page * {
  box-sizing: border-box;
}

.earn-page button,
.earn-page input {
  appearance: none;
  -webkit-appearance: none;
  font: inherit;
}

.earn-page button {
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.earn-content {
  width: 100%;
  max-width: 520px;
  margin: 0 auto;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.asset-overview-card {
  min-height: 148px;
  padding: 20px;
  border-radius: 20px;
  color: var(--color-text-primary);
  background:
    radial-gradient(circle at 85% 15%, rgb(var(--color-primary-rgb) / 0.28), transparent 34%),
    linear-gradient(145deg, var(--color-bg-card) 0%, var(--color-surface-1) 52%, var(--color-bg) 100%);
  border: 1px solid var(--earn-border);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.overview-kicker {
  display: block;
  color: var(--earn-muted);
  font-size: 12px;
  font-weight: 500;
}

.asset-overview-card > strong {
  display: block;
  margin-top: 10px;
  font-size: 25px;
  line-height: 1.15;
  font-weight: 700;
  letter-spacing: 0;
}

.asset-overview-card small {
  font-size: 13px;
  color: var(--earn-muted);
}

.overview-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 20px;
}

.overview-stats div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.overview-stats span {
  color: var(--earn-muted);
  font-size: 12px;
  font-weight: 400;
}

.overview-stats b {
  color: var(--earn-yellow);
  font-size: 14px;
  font-weight: 700;
}

.earn-tabs {
  height: 48px;
  padding: 4px;
  border: 1px solid var(--earn-border);
  border-radius: 14px;
  background: var(--earn-card);
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.earn-tabs button {
  border: 0;
  border-radius: 11px;
  background: transparent;
  color: var(--earn-muted);
  font-size: 14px;
  font-weight: 700;
}

.earn-tabs button.active {
  background: var(--earn-yellow);
  color: var(--earn-yellow-text);
}

.product-card,
.records-card {
  padding: 18px;
  border: 1px solid var(--earn-border);
  border-radius: 18px;
  background: var(--earn-card);
  box-shadow: var(--shadow-card);
}

.product-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: start;
}

.product-head h1 {
  margin: 10px 0 0;
  font-size: 22px;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: 0;
}

.product-head p {
  margin: 7px 0 0;
  color: var(--earn-muted);
  font-size: 13px;
  line-height: 1.55;
}

.status-badge {
  height: 22px;
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 0 8px;
  border-radius: 999px;
  background: rgb(var(--color-earn-rgb) / 0.12);
  color: var(--earn-success);
  font-size: 11px;
  font-weight: 700;
}

.status-badge.subtle {
  color: var(--earn-muted);
  background: var(--earn-soft);
}

.apy-block {
  text-align: right;
}

.apy-block strong {
  display: block;
  color: var(--earn-success);
  font-size: 24px;
  line-height: 1.1;
  font-weight: 700;
  white-space: nowrap;
}

.apy-block span {
  color: var(--earn-muted);
  font-size: 12px;
}

.product-highlight,
.estimate-row,
.selector-field {
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.product-highlight {
  min-height: 72px;
  margin-top: 16px;
  padding: 14px;
  border-radius: 16px;
  background: linear-gradient(180deg, var(--earn-card) 0%, var(--earn-panel) 100%);
  border: 1px solid var(--earn-border);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.product-highlight div {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.product-highlight span,
.estimate-row span,
.selector-field span,
.amount-field span,
.interest-metrics span,
.record-grid span {
  color: var(--earn-muted);
  font-size: 12px;
  font-weight: 400;
}

.product-highlight strong,
.estimate-row strong,
.selector-field strong,
.interest-metrics strong,
.record-grid b {
  color: var(--earn-text);
  font-size: 15px;
  font-weight: 600;
  min-width: 0;
  overflow-wrap: anywhere;
}

.meta-block {
  margin-top: 16px;
}

.meta-block > span {
  display: block;
  color: var(--earn-muted);
  font-size: 12px;
  margin-bottom: 8px;
}

.term-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.term-chips button {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid var(--earn-border);
  background: var(--earn-panel);
  color: var(--earn-text);
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
}

.term-chips button.active {
  border-color: var(--earn-yellow);
  background: var(--earn-yellow-soft);
  color: var(--earn-text);
}

.interest-metrics {
  margin-top: 14px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.interest-metrics div {
  min-height: 58px;
  padding: 10px;
  border-radius: 12px;
  background: var(--earn-panel);
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-panel {
  margin-top: 16px;
  padding: 14px;
  border-radius: 16px;
  background: var(--earn-panel);
  border: 1px solid var(--earn-border);
}

.selector-field {
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  color: var(--earn-text);
}

.amount-field {
  min-height: 54px;
  margin-top: 8px;
  padding: 8px 0;
  border-top: 1px solid var(--earn-border);
  border-bottom: 1px solid var(--earn-border);
  display: grid;
  grid-template-columns: 1fr minmax(90px, 44%);
  gap: 12px;
  align-items: center;
}

.amount-field input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--earn-text);
  text-align: right;
  font-size: 20px;
  font-weight: 700;
  min-width: 0;
}

.estimate-row {
  padding-top: 8px;
}

.primary-action {
  width: 100%;
  height: 48px;
  margin-top: 16px;
  border: 0;
  border-radius: 12px;
  background: var(--earn-yellow);
  color: var(--earn-yellow-text);
  font-size: 15px;
  font-weight: 800;
  box-shadow: 0 10px 22px rgb(var(--color-primary-rgb) / 0.24);
}

.primary-action:active,
.term-chips button:active,
.selector-field:active,
.asset-list button:active {
  transform: translateY(1px);
}

.records-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.records-head h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
}

.records-head span {
  color: var(--earn-muted);
  font-size: 12px;
}

.empty-state {
  margin-top: 12px;
  min-height: 112px;
  border-radius: 14px;
  background: linear-gradient(180deg, var(--earn-card) 0%, var(--earn-panel) 100%);
  color: var(--earn-muted);
  display: grid;
  place-items: center;
  align-content: center;
  gap: 8px;
}

.empty-state :deep(.van-icon) {
  font-size: 24px;
  color: var(--earn-subtle);
}

.empty-state strong {
  font-size: 13px;
  font-weight: 600;
}

.record-card {
  margin-top: 10px;
  padding: 14px;
  border-radius: 14px;
  background: var(--earn-panel);
  border: 1px solid var(--earn-border);
}

.record-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.record-title > strong {
  font-size: 15px;
  font-weight: 700;
}

.record-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 7px 12px;
}

.record-grid b {
  text-align: right;
}

.view-all-action {
  width: 100%;
  height: 38px;
  margin-top: 10px;
  border: 0;
  border-radius: 10px;
  background: var(--earn-yellow-soft);
  color: var(--earn-text);
  font-size: 13px;
  font-weight: 700;
}

.asset-sheet {
  max-height: 70vh;
  overflow: hidden;
  border-radius: 20px 20px 0 0;
  background: var(--earn-card);
  padding-bottom: env(safe-area-inset-bottom);
}

.sheet-handle {
  width: 40px;
  height: 4px;
  margin: 10px auto 8px;
  border-radius: 999px;
  background: var(--earn-border);
}

.asset-sheet h2 {
  margin: 0;
  padding: 0 20px 12px;
  font-size: 17px;
  font-weight: 700;
}

.asset-list {
  max-height: calc(70vh - 58px);
  overflow-y: auto;
  padding: 0 16px 16px;
}

.asset-list button {
  width: 100%;
  min-height: 64px;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-bottom-color: var(--earn-border);
  border-radius: 12px;
  background: var(--earn-card);
  color: var(--earn-text);
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: left;
}

.asset-list button.active {
  border-color: var(--earn-yellow);
  background: var(--earn-yellow-soft);
}

.asset-list span {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.asset-list strong {
  font-size: 15px;
  font-weight: 700;
}

.asset-list small {
  color: var(--earn-muted);
  font-size: 12px;
}

.asset-list :deep(.van-icon) {
  color: var(--earn-yellow);
}

@media (max-width: 390px) {
  .earn-content {
    padding: 14px 14px 18px;
  }

  .product-head {
    grid-template-columns: 1fr;
  }

  .apy-block {
    text-align: left;
  }

  .product-highlight {
    grid-template-columns: 1fr;
  }
}
</style>
