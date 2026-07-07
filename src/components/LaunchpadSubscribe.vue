<template>
  <div class="launchpad-subscribe-page">
    <van-nav-bar
      :title="t('launchpad_subscribe.title')"
      left-arrow
      fixed
      placeholder
      @click-left="router.back()"
    />

    <main class="subscribe-content">
      <section v-if="!walletState.connected" class="wallet-gate-card">
        <div>
          <strong>{{ t('launchpad_subscribe.connect_wallet_first') }}</strong>
          <span>{{ t('launchpad_subscribe.wallet_required_desc') }}</span>
        </div>
        <button class="ghost-action" :disabled="actionState.connecting" @click="connectWallet">
          {{ actionState.connecting ? t('common.loading') : t('connect') }}
        </button>
      </section>

      <section v-if="actionState.error" class="action-feedback error">
        {{ actionState.error }}
      </section>

      <section class="project-hero">
        <div class="project-mark">{{ project.logoText }}</div>
        <div class="project-copy">
          <div class="project-kicker">{{ t('launchpad_subscribe.live_project') }}</div>
          <h1>{{ project.name }}</h1>
          <div class="project-meta">
            <span>{{ project.ticker }}</span>
            <span>{{ project.tags.join(' / ') }}</span>
            <span>{{ t('launchpad_subscribe.participants') }} {{ formatInteger(participants) }}</span>
          </div>
        </div>
      </section>

      <section class="project-detail-card">
        <button class="detail-toggle" type="button" @click="introExpanded = !introExpanded">
          <span>{{ t('launchpad_subscribe.project_intro') }}</span>
          <van-icon :name="introExpanded ? 'arrow-up' : 'arrow-down'" />
        </button>
        <p :class="{ collapsed: !introExpanded }">
          {{ projectIntroText }}
        </p>
        <div class="tokenomics-preview">
          <div class="pie-chart" aria-label="Token allocation">
            <span>40%</span>
          </div>
          <div class="tokenomics-table">
            <div><span>{{ t('launchpad_subscribe.public_sale') }}</span><strong>40%</strong></div>
            <div><span>{{ t('launchpad_subscribe.ecosystem') }}</span><strong>35%</strong></div>
            <div><span>{{ t('launchpad_subscribe.team_unlock') }}</span><strong>25%</strong></div>
          </div>
        </div>
      </section>

      <section class="top-info-card">
        <div class="stage-row">
          <div>
            <span>{{ t('launchpad_subscribe.current_stage') }}</span>
            <strong>{{ t(`launchpad_subscribe.stage_${projectStage}`) }}</strong>
          </div>
          <div class="countdown-cell">
            <span>{{ timelineCountdown.label }}</span>
            <strong>{{ timelineCountdown.value }}</strong>
          </div>
        </div>
        <div class="stats-row">
          <div>
            <span>{{ t('launchpad.ido_price') }}</span>
            <strong>${{ formatNumber(subscriptionPrice, 3) }}</strong>
          </div>
          <div>
            <span>{{ t('launchpad.total_raise') }}</span>
            <strong>${{ formatCompact(totalRaise) }}</strong>
          </div>
          <div>
            <span>{{ t('launchpad_subscribe.participants') }}</span>
            <strong>{{ formatInteger(participants) }}</strong>
          </div>
        </div>
      </section>

      <section class="funding-card">
        <div class="funding-row">
          <span>{{ t('launchpad.progress') }}</span>
          <strong>{{ progress.toFixed(1) }}%</strong>
        </div>
        <div class="funding-bar">
          <div :style="{ width: progress + '%' }"></div>
        </div>
        <div class="funding-row muted">
          <span>{{ formatNumber(raisedAmount, 0) }} / {{ formatNumber(totalRaise, 0) }} USDT</span>
          <span>{{ formatInteger(tokenSupply) }} {{ project.ticker }}</span>
        </div>
      </section>

      <div class="mode-tabs" role="tablist">
        <button :class="{ active: activeMode === 'subscribe' }" @click="activeMode = 'subscribe'">
          {{ t('launchpad_subscribe.subscribe') }}
        </button>
        <button :class="{ active: activeMode === 'stake' }" @click="activeMode = 'stake'">
          {{ t('launchpad_subscribe.stake') }}
        </button>
      </div>

      <section v-if="activeMode === 'subscribe'" class="action-card">
        <label class="field-label">{{ t('launchpad_subscribe.subscription_amount') }}</label>
        <div class="amount-field">
          <input
            v-model="subscriptionAmount"
            type="number"
            inputmode="decimal"
            min="0"
            :placeholder="t('launchpad_subscribe.enter_amount')"
          />
          <span>USDT</span>
        </div>

        <div class="available-row">
          <span>{{ t('launchpad_subscribe.estimated_receive') }}</span>
          <strong>{{ formatNumber(userEstimatedTokens, 4) }} {{ project.ticker }}</strong>
        </div>
        <div class="available-row">
          <span>{{ t('launchpad_subscribe.available_allocation') }}</span>
          <strong>{{ formatNumber(directRemainingAllocation) }} USDT</strong>
        </div>
        <div class="available-row">
          <span>{{ t('launchpad_subscribe.wallet_balance') }}</span>
          <strong>{{ formatNumber(walletBalanceUSDT) }} USDT</strong>
        </div>
        <div class="available-row">
          <span>{{ t('launchpad_subscribe.subscribed_amount') }}</span>
          <strong>{{ formatNumber(userSubscriptionAmount) }} USDT</strong>
        </div>
        <div class="available-row lottery-ratio-row">
          <span>{{ t('launchpad_subscribe.simulated_win_ratio') }}</span>
          <strong>{{ simulatedWinRatio }}</strong>
        </div>

        <button class="primary-action" :disabled="!canConfirmSubscription" @click="confirmSubscription">
          {{ subscriptionButtonText }}
        </button>

        <section class="records-section">
          <div class="records-heading">
            <h2>{{ t('launchpad_subscribe.my_subscription_orders') }}</h2>
            <span v-if="displaySubscriptionOrders.length">{{ recordCountText2(displaySubscriptionOrders.length) }}</span>
          </div>
          <div v-if="displaySubscriptionOrders.length === 0" class="empty-record">
            {{ t('launchpad_subscribe.no_subscription_orders') }}
          </div>
          <div v-else class="record-stack">
            <div v-if="displaySubscriptionOrders.length > 2" class="stack-card ghost ghost-two"></div>
            <div v-if="displaySubscriptionOrders.length > 1" class="stack-card ghost ghost-one"></div>
            <article class="order-card stack-main">
              <div class="order-card-head">
                <strong>{{ orderTicker(latestSubscriptionOrder) }}</strong>
                <span class="status-badge" :class="orderStatusClass(compactOrderStatus(latestSubscriptionOrder))">
                  {{ t(`launchpad_subscribe.order_status_${compactOrderStatus(latestSubscriptionOrder)}`) }}
                </span>
              </div>
              <div v-if="compactOrderStatus(latestSubscriptionOrder) === 'won'" class="win-result">
                <span>{{ t('launchpad_subscribe.won_amount') }}</span>
                <strong>{{ formatTokenAmount(orderWonAmount(latestSubscriptionOrder)) }} {{ orderTicker(latestSubscriptionOrder) }}</strong>
              </div>
              <div class="record-grid compact-record-grid">
                <template v-if="compactOrderStatus(latestSubscriptionOrder) === 'pending_draw'">
                  <span>{{ t('launchpad_subscribe.payment_amount') }}</span>
                  <strong>{{ formatMoney2(latestSubscriptionOrder.amount) }} USDT</strong>
                  <span>{{ t('launchpad_subscribe.estimated_receive') }}</span>
                  <strong>{{ formatTokenAmount(latestSubscriptionOrder.tokenAmount) }} {{ orderTicker(latestSubscriptionOrder) }}</strong>
                </template>
                <template v-else-if="compactOrderStatus(latestSubscriptionOrder) === 'won'">
                  <span>{{ t('launchpad_subscribe.win_ratio') }}</span>
                  <strong class="ratio-value">{{ formatWinRatio(latestSubscriptionOrder) }}</strong>
                </template>
                <template v-else>
                  <span>{{ t('launchpad_subscribe.refund_amount') }}</span>
                  <strong>{{ formatMoney2(orderRefundAmount(latestSubscriptionOrder)) }} USDT</strong>
                  <span>{{ t('launchpad_subscribe.order_time') }}</span>
                  <strong>{{ formatDateTime(latestSubscriptionOrder.settledAt || latestSubscriptionOrder.timestamp) }}</strong>
                </template>
              </div>
            </article>
          </div>
          <button
            v-if="displaySubscriptionOrders.length > 1"
            class="view-all-action"
            type="button"
            @click="showSubscriptionRecordsSheet = true"
          >
            {{ viewAllLabel }}
          </button>
        </section>
      </section>

      <section v-else class="action-card">
        <label class="field-label">{{ t('launchpad_subscribe.select_staking_asset') }}</label>
        <button class="asset-select" type="button" @click="showStakeAssetMenu = true">
          <span>
            <strong>{{ selectedStakePool.asset }}</strong>
            <small>{{ selectedStakePool.name }}</small>
          </span>
          <span class="asset-select-meta">
            {{ formatNumber(selectedStakePool.balance, selectedStakePool.asset === 'USDT' ? 2 : 6) }} · {{ selectedStakePool.apy }}% {{ t('launchpad_subscribe.apy') }}
            <van-icon name="arrow" />
          </span>
        </button>

        <label class="field-label spaced">{{ t('launchpad_subscribe.enter_staking_amount') }}</label>
        <div class="amount-field">
          <input
            v-model="stakeAmount"
            type="number"
            inputmode="decimal"
            min="0"
            :placeholder="t('launchpad_subscribe.enter_stake_amount')"
          />
          <span>{{ selectedStakePool.asset }}</span>
        </div>
        <div class="available-row">
          <span>{{ t('launchpad_subscribe.available_asset', { asset: selectedStakePool.asset }) }}</span>
          <strong>{{ formatNumber(availableStakeBalance, selectedStakePool.asset === 'USDT' ? 2 : 6) }} {{ selectedStakePool.asset }}</strong>
        </div>
        <div class="available-row">
          <span>{{ t('launchpad_subscribe.estimated_rewards') }}</span>
          <strong>{{ formatNumber(estimatedRewardToken, 4) }} {{ project.ticker }}</strong>
        </div>

        <button class="primary-action" :disabled="!canConfirmStake" @click="confirmStake">
          {{ stakingButtonText }}
        </button>

        <section class="records-section">
          <div class="records-heading">
            <h2>{{ t('launchpad_subscribe.my_staking_records') }}</h2>
            <span v-if="stakingRecords.length">{{ recordCountText(stakingRecords.length) }}</span>
          </div>
          <div v-if="stakingRecords.length === 0" class="empty-record">
            {{ t('launchpad_subscribe.no_staking_records') }}
          </div>
          <div v-else class="record-stack stake-stack">
            <div v-if="stakingRecords.length > 2" class="stack-card ghost ghost-two"></div>
            <div v-if="stakingRecords.length > 1" class="stack-card ghost ghost-one"></div>
            <article class="order-card stack-main">
              <div class="order-card-head">
                <strong>{{ latestStakingRecord.asset }}</strong>
                <span class="status-badge active-stake">
                  {{ t('launchpad_subscribe.staking_status_active') }}
                </span>
              </div>
              <div class="record-grid compact-record-grid">
                <span>{{ t('launchpad_subscribe.status') }}</span>
                <strong>{{ t('launchpad_subscribe.staking_status_active') }}</strong>
                <span>{{ t('launchpad_subscribe.stake_amount') }}</span>
                <strong>{{ formatNumber(latestStakingRecord.amount, latestStakingRecord.asset === 'USDT' ? 2 : 6) }} {{ latestStakingRecord.asset }}</strong>
                <span>{{ t('launchpad_subscribe.start_time') }}</span>
                <strong>{{ formatDateTime(latestStakingRecord.createdAt) }}</strong>
                <span>{{ t('launchpad_subscribe.accumulated_rewards') }}</span>
                <strong>{{ formatNumber(recordReward(latestStakingRecord), 4) }} {{ latestStakingRecord.rewardTicker }}</strong>
              </div>
              <button
                class="compact-primary-action"
                type="button"
                :disabled="stakingPrimaryDisabled(latestStakingRecord)"
                @click="runStakingPrimaryAction(latestStakingRecord)"
              >
                {{ stakingPrimaryLabel(latestStakingRecord) }}
              </button>
            </article>
          </div>
          <button
            v-if="stakingRecords.length > 1"
            class="view-all-action"
            type="button"
            @click="showStakingRecordsSheet = true"
          >
            {{ viewAllLabel }}
          </button>
        </section>
      </section>
    </main>

    <van-popup
      v-model:show="showStakeAssetMenu"
      position="bottom"
      round
      closeable
      class="stake-asset-sheet"
      :overlay-style="{ background: 'rgba(0,0,0,0.35)' }"
    >
      <div class="sheet-handle"></div>
      <div class="sheet-title">{{ t('launchpad_subscribe.select_staking_asset') }}</div>
      <div class="asset-sheet-list">
        <button
          v-for="pool in stakingPools"
          :key="pool.asset"
          type="button"
          :class="{ active: selectedStakeAsset === pool.asset }"
          @click="selectStakeAsset(pool.asset)"
        >
          <span>
            <strong>{{ pool.asset }}</strong>
            <small>{{ pool.name }}</small>
          </span>
          <span>
            <strong>{{ formatNumber(pool.balance, pool.asset === 'USDT' ? 2 : 6) }}</strong>
            <small>{{ pool.apy }}% {{ t('launchpad_subscribe.apy') }}</small>
          </span>
          <van-icon v-if="selectedStakeAsset === pool.asset" name="success" />
        </button>
      </div>
    </van-popup>

    <van-popup
      v-model:show="showSubscriptionRecordsSheet"
      position="bottom"
      round
      closeable
      class="records-sheet"
      :overlay-style="{ background: 'rgba(0,0,0,0.35)' }"
    >
      <div class="sheet-handle"></div>
      <div class="sheet-title">{{ allSubscriptionOrdersTitle }}</div>
      <div class="sheet-record-list">
        <article v-for="order in displaySubscriptionOrders" :key="order.id" class="order-card">
          <div class="order-card-head">
            <strong>{{ orderTicker(order) }}</strong>
            <span class="status-badge" :class="orderStatusClass(compactOrderStatus(order))">
              {{ t(`launchpad_subscribe.order_status_${compactOrderStatus(order)}`) }}
            </span>
          </div>
          <div v-if="compactOrderStatus(order) === 'won'" class="win-result">
            <span>{{ t('launchpad_subscribe.won_amount') }}</span>
            <strong>{{ formatTokenAmount(orderWonAmount(order)) }} {{ orderTicker(order) }}</strong>
          </div>
          <div class="record-grid compact-record-grid">
            <template v-if="compactOrderStatus(order) === 'pending_draw'">
              <span>{{ t('launchpad_subscribe.payment_amount') }}</span>
              <strong>{{ formatMoney2(order.amount) }} USDT</strong>
              <span>{{ t('launchpad_subscribe.estimated_receive') }}</span>
              <strong>{{ formatTokenAmount(order.tokenAmount) }} {{ orderTicker(order) }}</strong>
            </template>
            <template v-else-if="compactOrderStatus(order) === 'won'">
              <span>{{ t('launchpad_subscribe.win_ratio') }}</span>
              <strong class="ratio-value">{{ formatWinRatio(order) }}</strong>
            </template>
            <template v-else>
              <span>{{ t('launchpad_subscribe.refund_amount') }}</span>
              <strong>{{ formatMoney2(orderRefundAmount(order)) }} USDT</strong>
              <span>{{ t('launchpad_subscribe.order_time') }}</span>
              <strong>{{ formatDateTime(order.settledAt || order.timestamp) }}</strong>
            </template>
          </div>
        </article>
      </div>
    </van-popup>

    <van-popup
      v-model:show="showStakingRecordsSheet"
      position="bottom"
      round
      closeable
      class="records-sheet"
      :overlay-style="{ background: 'rgba(0,0,0,0.35)' }"
    >
      <div class="sheet-handle"></div>
      <div class="sheet-title">{{ allStakingRecordsTitle }}</div>
      <div class="sheet-record-list">
        <article v-for="record in stakingRecords" :key="record.id" class="order-card">
          <div class="order-card-head">
            <strong>{{ record.asset }}</strong>
            <span class="status-badge active-stake">
              {{ t('launchpad_subscribe.staking_status_active') }}
            </span>
          </div>
          <div class="record-grid compact-record-grid">
            <span>{{ t('launchpad_subscribe.status') }}</span>
            <strong>{{ t('launchpad_subscribe.staking_status_active') }}</strong>
            <span>{{ t('launchpad_subscribe.stake_amount') }}</span>
            <strong>{{ formatNumber(record.amount, record.asset === 'USDT' ? 2 : 6) }} {{ record.asset }}</strong>
            <span>{{ t('launchpad_subscribe.start_time') }}</span>
            <strong>{{ formatDateTime(record.createdAt) }}</strong>
            <span>{{ t('launchpad_subscribe.accumulated_rewards') }}</span>
            <strong>{{ formatNumber(recordReward(record), 4) }} {{ record.rewardTicker }}</strong>
          </div>
        </article>
      </div>
    </van-popup>

    <van-popup v-model:show="showAuthModal" round class="authorization-modal">
      <div class="auth-panel">
        <div class="auth-icon">
          <van-icon name="shield-o" />
        </div>
        <h3>{{ t('launchpad_subscribe.auth_title') }}</h3>
        <p>{{ t('launchpad_subscribe.auth_desc') }}</p>
        <button class="primary-action" :disabled="isAuthorizing" @click="authorizeSession">
          {{ isAuthorizing ? t('launchpad_subscribe.waiting_signature') : t('launchpad_subscribe.authorize_session') }}
        </button>
        <button class="ghost-action full" @click="cancelAuthorization">{{ t('common.cancel') }}</button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { useAssetStore } from '@/stores/assets'
import launchpadEngine from '@/services/launchpadEngine'
import { formatInteger, formatNumber } from '@/utils/format'

defineOptions({ name: 'LaunchpadSubscribe' })

const router = useRouter()
const route = useRoute()
const assetStore = useAssetStore()
const { t, locale } = useI18n()

const DAY = 24 * 60 * 60 * 1000

const toFiniteNumber = (value, fallback = 0) => {
  const number = Number(value)
  return Number.isFinite(number) ? number : fallback
}

const splitQueryList = (value, fallback = []) => {
  const raw = Array.isArray(value) ? value.join(',') : value
  const items = String(raw || '')
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
  return (items.length ? items : fallback)
    .filter((item, index, list) => item && list.indexOf(item) === index)
}

const parseTime = (value, fallback) => {
  if (!value) return fallback
  const timestamp = Number(value)
  if (Number.isFinite(timestamp)) return timestamp < 10000000000 ? timestamp * 1000 : timestamp
  const parsed = Date.parse(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

const activeMode = ref('subscribe')
const subscriptionAmount = ref('')
const stakeAmount = ref('')
const selectedStakeAsset = ref('USDT')
const progress = ref(0)
const now = ref(Date.now())
const introExpanded = ref(false)
const showStakeAssetMenu = ref(false)
const showSubscriptionRecordsSheet = ref(false)
const showStakingRecordsSheet = ref(false)
const showAuthModal = ref(false)
const isAuthorizing = ref(false)
const authResolver = ref(null)

const walletState = reactive({
  address: '',
  connected: false,
  authenticated: false,
  mode: 'dev'
})

const actionState = reactive({
  connecting: false,
  subscriptionLoading: false,
  stakingLoading: false,
  claimLoading: false,
  unstakeLoading: null,
  error: '',
  success: ''
})

const baseNow = Date.now()
const project = computed(() => ({
  name: route.query.name || 'GameMaster',
  ticker: route.query.ticker || 'GMT',
  logoText: route.query.logoText || 'GM',
  tags: splitQueryList(route.query.tags, ['GameFi']),
  performanceTags: splitQueryList(route.query.performanceTags),
  price: Math.max(0.000001, toFiniteNumber(route.query.price, 0.045)),
  targetRaise: Math.max(1, toFiniteNumber(route.query.targetRaise, 500000)),
  minAlloc: Math.max(0, toFiniteNumber(route.query.minAlloc, 100)),
  subscriptionStartTime: parseTime(route.query.subscriptionStartTime || route.query.startTime, baseNow - DAY),
  subscriptionEndTime: parseTime(route.query.subscriptionEndTime || route.query.endTime, baseNow + DAY),
  stakingStartTime: parseTime(route.query.stakingStartTime || route.query.startTime, baseNow - DAY),
  stakingEndTime: parseTime(route.query.stakingEndTime || route.query.endTime, baseNow + DAY),
  settlementTime: parseTime(route.query.settlementTime, baseNow + DAY * 2),
  listingTime: parseTime(route.query.listingTime, baseNow + DAY * 3),
  stakingPools: parseConfiguredPools(route.query.stakingPools)
})).value

const projectIntroText = computed(() => t('launchpad_subscribe.project_intro_body', {
  name: project.name,
  ticker: project.ticker
}))

let progressTimer = null
let clockTimer = null

function parseConfiguredPools(value) {
  if (!value) return null
  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed : null
  } catch (error) {
    return null
  }
}

const defaultPools = [
  { asset: 'USDT', name: 'Tether USD', apy: 18, rewardToken: project.ticker, poolRewardAllocation: 300000, totalPoolStakeAmount: 1200000 },
  { asset: 'USDC', name: 'USD Coin', apy: 17, rewardToken: project.ticker, poolRewardAllocation: 180000, totalPoolStakeAmount: 900000 },
  { asset: 'FDUSD', name: 'First Digital USD', apy: 16, rewardToken: project.ticker, poolRewardAllocation: 150000, totalPoolStakeAmount: 760000 },
  { asset: 'BNB', name: 'BNB', apy: 22, rewardToken: project.ticker, poolRewardAllocation: 500000, totalPoolStakeAmount: 2200 },
  { asset: 'ETH', name: 'Ethereum', apy: 20, rewardToken: project.ticker, poolRewardAllocation: 420000, totalPoolStakeAmount: 680 },
  { asset: 'BTC', name: 'Bitcoin', apy: 14, rewardToken: project.ticker, poolRewardAllocation: 250000, totalPoolStakeAmount: 48 }
]

const configuredPools = computed(() => {
  const source = Array.isArray(project.stakingPools) && project.stakingPools.length ? project.stakingPools : defaultPools
  return source.map(pool => {
    const asset = String(pool.asset || '').toUpperCase()
    return {
      asset,
      name: pool.name || asset,
      apy: toFiniteNumber(pool.apy, 0),
      rewardToken: pool.rewardToken || project.ticker,
      poolRewardAllocation: toFiniteNumber(pool.poolRewardAllocation, 0),
      totalPoolStakeAmount: Math.max(1, toFiniteNumber(pool.totalPoolStakeAmount, 1))
    }
  }).filter(pool => pool.asset)
})

const stakingPools = computed(() => configuredPools.value.map(pool => ({
  ...pool,
  balance: pool.asset === 'USDT' ? walletBalanceUSDT.value : Number(assetStore.getHolding(pool.asset)) || 0
})))

const selectedStakePool = computed(() => (
  stakingPools.value.find(pool => pool.asset === selectedStakeAsset.value) || stakingPools.value[0]
))

const subscriptionStartTime = computed(() => project.subscriptionStartTime)
const subscriptionEndTime = computed(() => project.subscriptionEndTime)
const stakingStartTime = computed(() => project.stakingStartTime)
const stakingEndTime = computed(() => project.stakingEndTime)
const settlementTime = computed(() => project.settlementTime)
const listingTime = computed(() => project.listingTime)
const subscriptionPrice = computed(() => project.price)
const totalRaise = computed(() => project.targetRaise)
const raisedAmount = computed(() => Math.round(totalRaise.value * progress.value / 100))
const tokenSupply = computed(() => Math.floor(totalRaise.value / subscriptionPrice.value))
const participants = computed(() => Math.round(18000 + (progress.value / 100) * 1500))
const walletBalanceUSDT = computed(() => Number(assetStore.usdtBalance) || 0)

const projectStage = computed(() => {
  const current = now.value
  if (current < Math.min(subscriptionStartTime.value, stakingStartTime.value)) return 'upcoming'
  if (current <= Math.max(subscriptionEndTime.value, stakingEndTime.value)) return 'active'
  if (current < settlementTime.value) return 'calculating'
  if (current < listingTime.value) return 'distributing'
  if (current < listingTime.value + DAY) return 'listed'
  return 'ended'
})

const canSubscribeNow = computed(() => now.value >= subscriptionStartTime.value && now.value <= subscriptionEndTime.value)
const canStakeNow = computed(() => now.value >= stakingStartTime.value && now.value <= stakingEndTime.value)
const isSettled = computed(() => now.value >= settlementTime.value || now.value >= listingTime.value)
const isListed = computed(() => now.value >= listingTime.value)

const timelineCountdown = computed(() => {
  if (projectStage.value === 'upcoming') {
    return { label: t('launchpad_subscribe.starts_in'), value: formatDuration(Math.min(subscriptionStartTime.value, stakingStartTime.value) - now.value) }
  }
  if (projectStage.value === 'active') {
    return { label: t('launchpad_subscribe.ends_in'), value: formatDuration(Math.max(subscriptionEndTime.value, stakingEndTime.value) - now.value) }
  }
  if (projectStage.value === 'calculating') {
    return { label: t('launchpad_subscribe.result_soon'), value: formatDuration(settlementTime.value - now.value) }
  }
  if (projectStage.value === 'distributing') {
    return { label: t('launchpad_subscribe.distribution_in'), value: formatDuration(listingTime.value - now.value) }
  }
  return { label: t('launchpad_subscribe.final_status'), value: t(`launchpad_subscribe.stage_${projectStage.value}`) }
})

const subscriptionOrders = computed(() => {
  assetStore.syncLaunchpadSettlements?.(now.value)
  const records = Array.isArray(assetStore.idoRecords) ? assetStore.idoRecords : []
  return records
    .filter(record => !record.name || record.name === project.name || record.ticker === project.ticker)
    .slice()
    .sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0))
})

const demoSubscriptionOrders = computed(() => {
  const ticker = project.ticker
  const price = subscriptionPrice.value || 1
  const baseTime = now.value
  return [
    {
      id: `demo-won-${ticker}`,
      name: project.name,
      ticker,
      amount: 128,
      tokenAmount: 128 / price,
      wonTokenAmount: 22.22,
      finalTokenAmount: 22.22,
      refundAmount: 0,
      winRatio: 0.186,
      status: 'won',
      settled: true,
      timestamp: new Date(baseTime - 1000 * 60 * 28).toISOString(),
      settledAt: new Date(baseTime - 1000 * 60 * 18).toISOString(),
      demo: true
    },
    {
      id: `demo-pending-${ticker}`,
      name: project.name,
      ticker,
      amount: 88,
      tokenAmount: 88 / price,
      wonTokenAmount: 0,
      finalTokenAmount: 0,
      refundAmount: 0,
      winRatio: 0,
      status: 'pending_draw',
      settled: false,
      timestamp: new Date(baseTime - 1000 * 60 * 55).toISOString(),
      demo: true
    },
    {
      id: `demo-not-won-${ticker}`,
      name: project.name,
      ticker,
      amount: 66,
      tokenAmount: 66 / price,
      wonTokenAmount: 0,
      finalTokenAmount: 0,
      refundAmount: 66,
      winRatio: 0,
      status: 'not_won',
      settled: true,
      timestamp: new Date(baseTime - 1000 * 60 * 90).toISOString(),
      settledAt: new Date(baseTime - 1000 * 60 * 32).toISOString(),
      demo: true
    }
  ]
})

const displaySubscriptionOrders = computed(() => {
  const byStatus = new Set(subscriptionOrders.value.map(order => compactOrderStatus(order)))
  const supplements = demoSubscriptionOrders.value.filter(order => !byStatus.has(compactOrderStatus(order)))
  return [...subscriptionOrders.value, ...supplements]
    .sort((a, b) => {
      const rank = { won: 0, pending_draw: 1, not_won: 2 }
      const statusDiff = (rank[compactOrderStatus(a)] ?? 9) - (rank[compactOrderStatus(b)] ?? 9)
      if (statusDiff !== 0) return statusDiff
      return new Date(b.timestamp || 0) - new Date(a.timestamp || 0)
    })
})

const latestSubscriptionOrder = computed(() => displaySubscriptionOrders.value[0] || null)

const userSubscriptionAmount = computed(() => subscriptionOrders.value.reduce((sum, order) => sum + (Number(order.amount) || 0), 0))
const directAllocationLimit = computed(() => Math.max(project.minAlloc * 10, 999))
const directRemainingAllocation = computed(() => Math.max(0, directAllocationLimit.value - userSubscriptionAmount.value))
const userEstimatedTokens = computed(() => (Number(subscriptionAmount.value) || 0) / subscriptionPrice.value)
const userFinalTokens = computed(() => calculateFinalSubscription(Number(subscriptionAmount.value) || 0).finalTokens)
const userRefundAmount = computed(() => calculateFinalSubscription(Number(subscriptionAmount.value) || 0).refund)
const simulatedWinRatio = computed(() => {
  const amount = Number(subscriptionAmount.value) || Math.max(1, Number(project.minAlloc) || 100)
  const base = amount / Math.max(1, directAllocationLimit.value)
  const ratio = Math.min(0.368, Math.max(0.086, base * 1.8 + 0.064))
  return `${(ratio * 100).toFixed(2)}%`
})

const canConfirmSubscription = computed(() => {
  const amount = Number(subscriptionAmount.value) || 0
  return walletState.connected &&
    canSubscribeNow.value &&
    !actionState.subscriptionLoading &&
    amount > 0 &&
    amount <= walletBalanceUSDT.value &&
    amount <= directRemainingAllocation.value
})

const subscriptionButtonText = computed(() => {
  if (actionState.subscriptionLoading) return t('common.loading')
  if (now.value < subscriptionStartTime.value) return t('launchpad_subscribe.not_started')
  if (now.value > subscriptionEndTime.value) return t('launchpad_subscribe.subscription_closed')
  return t('launchpad_subscribe.confirm_subscription')
})

const availableStakeBalance = computed(() => selectedStakePool.value?.balance || 0)
const estimatedRewardToken = computed(() => estimateStakeReward({
  amount: Number(stakeAmount.value) || 0,
  pool: selectedStakePool.value,
  startTime: now.value
}))

const canConfirmStake = computed(() => {
  const amount = Number(stakeAmount.value) || 0
  return walletState.connected &&
    canStakeNow.value &&
    !actionState.stakingLoading &&
    amount > 0 &&
    amount <= availableStakeBalance.value
})

const stakingButtonText = computed(() => {
  if (actionState.stakingLoading) return t('common.loading')
  if (now.value < stakingStartTime.value) return t('launchpad_subscribe.not_started')
  if (now.value > stakingEndTime.value) return t('launchpad_subscribe.staking_closed')
  return t('launchpad_subscribe.confirm_staking_asset', { asset: selectedStakePool.value.asset })
})

const stakingRecords = computed(() => {
  assetStore.syncLaunchpadDailyRewards?.(now.value)
  const records = Array.isArray(assetStore.launchpadStakingPositions) ? assetStore.launchpadStakingPositions : []
  return records
    .filter(record => !record.projectTicker || record.projectTicker === project.ticker)
    .slice()
    .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0))
})
const latestStakingRecord = computed(() => stakingRecords.value[0] || null)

const isZhLocale = computed(() => String(locale.value || '').toLowerCase().startsWith('zh'))

const safeTranslate = (key, zhText, enText) => {
  const translated = t(key)
  return translated === key ? (isZhLocale.value ? zhText : enText) : translated
}

const viewAllLabel = computed(() => safeTranslate('launchpad_subscribe.view_all', '查看全部', 'View All'))
const allSubscriptionOrdersTitle = computed(() => safeTranslate('launchpad_subscribe.all_subscription_orders', '全部认购记录', 'All Subscription Orders'))
const allStakingRecordsTitle = computed(() => safeTranslate('launchpad_subscribe.all_staking_records', '全部质押记录', 'All Staking Records'))
const recordCountText = (count) => (isZhLocale.value ? `共 ${count} 笔` : `${count} total`)

const recordCountText2 = (count) => (isZhLocale.value ? `共 ${count} 笔` : `${count} records`)

const orderTicker = (order) => order?.ticker || project.ticker

const formatMoney2 = (value) => formatNumber(Number(value) || 0, 2)

const formatTokenAmount = (value) => formatNumber(Number(value) || 0, 2)

const orderWonAmount = (order) => {
  if (!order) return 0
  if (order.status === 'won') return Number(order.wonTokenAmount || order.finalTokenAmount || 0) || 0
  return 0
}

const compactOrderStatus = (order) => {
  if (!order) return 'pending_draw'
  if (order.status === 'won') return 'won'
  if (order.status === 'not_won' || order.status === 'refunded') return 'not_won'
  if (order.settled && orderWonAmount(order) <= 0) return 'not_won'
  return 'pending_draw'
}

const orderRefundAmount = (order) => {
  const explicitRefund = Number(order?.refundAmount)
  if (Number.isFinite(explicitRefund) && explicitRefund > 0) return explicitRefund
  if (compactOrderStatus(order) === 'not_won') return Number(order?.amount) || 0
  return 0
}

function calculateFinalSubscription(amount) {
  if (amount <= 0) return { finalTokens: 0, refund: 0 }
  const projectedRaisedAmount = Math.max(raisedAmount.value, userSubscriptionAmount.value + amount)
  if (projectedRaisedAmount <= totalRaise.value) {
    return { finalTokens: amount / subscriptionPrice.value, refund: 0 }
  }
  const share = amount / projectedRaisedAmount
  const finalUsdt = totalRaise.value * share
  return {
    finalTokens: finalUsdt / subscriptionPrice.value,
    refund: Math.max(0, amount - finalUsdt)
  }
}

function estimateStakeReward({ amount, pool, startTime }) {
  if (!pool || amount <= 0) return 0
  const activeEnd = Math.min(now.value, stakingEndTime.value, listingTime.value)
  const activeSeconds = Math.max(0, (activeEnd - startTime) / 1000)
  const poolDurationSeconds = Math.max(1, (stakingEndTime.value - stakingStartTime.value) / 1000)
  const userStakeShare = amount / Math.max(1, pool.totalPoolStakeAmount)
  const timeRatio = Math.min(1, activeSeconds / poolDurationSeconds)
  return pool.poolRewardAllocation * userStakeShare * timeRatio
}

function recordReward(record) {
  if (!record || record.status === 'claimed' || record.status === 'unlocked') return 0
  const pool = configuredPools.value.find(item => item.asset === record.asset) || selectedStakePool.value
  const liveReward = estimateStakeReward({
    amount: Number(record.amount) || 0,
    pool,
    startTime: Date.parse(record.createdAt || record.userStakeStartTime || new Date())
  })
  return isListed.value ? Number(record.finalRewardToken || record.claimableReward || liveReward) || 0 : liveReward
}

function formatStakingFinalReward(record) {
  if (!isSettled.value) return t('launchpad_subscribe.calculating')
  return `${formatNumber(recordReward(record), 4)} ${record.rewardTicker || project.ticker}`
}

function formatDailyStakeReward(record) {
  const dailyReward = Number(record?.dailyRewardToken) || ((Number(record?.amountUsdt) || 0) * 0.006 / subscriptionPrice.value)
  return `${formatNumber(dailyReward, 4)} ${record?.rewardTicker || project.ticker}`
}

function orderStatus(order) {
  if (order.status === 'won') return 'won'
  if (order.status === 'not_won') return 'not_won'
  if (order.status === 'pending_draw') return 'pending_draw'
  if (order.status === 'refunded') return 'refunded'
  if (isListed.value) return 'completed'
  if (isSettled.value) return 'distribution'
  if (now.value > subscriptionEndTime.value) return 'waiting'
  return 'subscribing'
}

function stakingRecordStatus(record) {
  if (record.status === 'unlocked') return 'unlocked'
  if (record.status === 'claimed') return 'claimed'
  if (isListed.value) return 'claimable'
  if (now.value > stakingEndTime.value) return 'settling'
  return 'active'
}

function orderStatusClass(status) {
  return {
    won: 'won',
    pending_draw: 'pending',
    not_won: 'muted',
    completed: 'success',
    listed: 'success',
    claimable: 'success',
    refunded: 'danger',
    unlocked: 'success',
    claimed: 'muted',
    waiting: 'warning',
    settling: 'warning',
    distribution: 'warning'
  }[status] || ''
}

function formatFinalTokens(order) {
  if (!isSettled.value) return t('launchpad_subscribe.calculating')
  const finalTokens = Number(order.wonTokenAmount || order.finalTokenAmount || order.tokenAmount) || 0
  return `${formatNumber(finalTokens, 4)} ${order.ticker || project.ticker}`
}

function formatWinRatio(order) {
  const ratio = Number(order.winRatio) || (compactOrderStatus(order) === 'won' ? 0.186 : 0)
  return `${(ratio * 100).toFixed(2)}%`
}

function formatDuration(ms) {
  const safeMs = Math.max(0, ms)
  const totalSeconds = Math.floor(safeMs / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  return [hours, minutes, seconds].map(value => String(value).padStart(2, '0')).join(':')
}

function formatDateTime(value) {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const resetWalletState = () => {
  walletState.address = ''
  walletState.connected = false
  walletState.authenticated = false
  walletState.mode = 'dev'
}

const syncWalletState = () => {
  try {
    const state = launchpadEngine.getWalletState() || {}
    walletState.address = state.address || ''
    walletState.connected = Boolean(state.connected)
    walletState.authenticated = Boolean(state.authenticated)
    walletState.mode = state.mode || 'dev'
  } catch (error) {
    console.warn('[LaunchpadSubscribe] wallet state sync failed:', error)
    resetWalletState()
  }
}

const setFeedback = ({ success = '', error = '' } = {}) => {
  actionState.success = success
  actionState.error = error
}

const runAction = async (loadingKey, action) => {
  actionState[loadingKey] = true
  setFeedback()
  try {
    const result = await action()
    syncWalletState()
    return result
  } catch (error) {
    const message = error.message || t('common.error')
    setFeedback({ error: message })
    showToast({ message, icon: 'fail' })
    return null
  } finally {
    actionState[loadingKey] = false
  }
}

const formatCompact = (value) => {
  const number = Number(value) || 0
  if (number >= 1000000) return `${(number / 1000000).toFixed(1)}M`
  if (number >= 1000) return `${(number / 1000).toFixed(0)}K`
  return number.toString()
}

const initializeMockSubscriptionBalances = () => {
  if ((assetStore.usdtBalance || 0) <= 0) {
    assetStore.usdtBalance = 10000
  }
  const defaults = { ETH: 1.25, BTC: 0.18, BNB: 12, USDC: 5000, FDUSD: 3500 }
  Object.entries(defaults).forEach(([asset, amount]) => {
    if (!assetStore.holdings[asset]) {
      assetStore.holdings[asset] = amount
    }
  })
}

const normalizeProgress = (value) => {
  const number = toFiniteNumber(value, NaN)
  if (!Number.isFinite(number)) return 84
  return Math.min(100, Math.max(0, number))
}

const initializeFundingModel = () => {
  const queryProgress = route.query.progress
  const queryRaised = toFiniteNumber(route.query.raised, NaN)
  if (queryProgress !== undefined) {
    progress.value = normalizeProgress(queryProgress)
    return
  }
  if (Number.isFinite(queryRaised) && totalRaise.value > 0) {
    progress.value = normalizeProgress((queryRaised / totalRaise.value) * 100)
    return
  }
  progress.value = 84
}

const connectWallet = async () => {
  const result = await runAction('connecting', async () => {
    await assetStore.connectWallet()
    return launchpadEngine.getWalletState()
  })
  if (result) {
    setFeedback({ success: t('auth.connectSuccess') })
    showToast({ message: t('auth.connectSuccess'), icon: 'success' })
  }
  return Boolean(result)
}

const ensureWalletConnected = async () => {
  if (walletState.connected || assetStore.isWalletConnected) {
    syncWalletState()
    return true
  }
  return connectWallet()
}

const ensureAuthorization = async () => {
  if (sessionStorage.getItem('truthfi_launchpad_authorized') === 'true') return true
  showAuthModal.value = true
  return new Promise(resolve => {
    authResolver.value = resolve
  })
}

const authorizeSession = async () => {
  if (isAuthorizing.value) return
  isAuthorizing.value = true
  try {
    await launchpadEngine.ensureSigned('authorization', project)
    sessionStorage.setItem('truthfi_launchpad_authorized', 'true')
    showAuthModal.value = false
    authResolver.value?.(true)
    authResolver.value = null
    showToast({ message: t('launchpad_subscribe.authorization_completed'), icon: 'success' })
  } catch (error) {
    showToast({ message: error.message || t('launchpad_subscribe.authorization_failed'), icon: 'fail' })
    authResolver.value?.(false)
    authResolver.value = null
    showAuthModal.value = false
  } finally {
    isAuthorizing.value = false
  }
}

const cancelAuthorization = () => {
  showAuthModal.value = false
  authResolver.value?.(false)
  authResolver.value = null
}

const confirmSubscription = async () => {
  if (!(await ensureWalletConnected())) return
  if (!canConfirmSubscription.value) {
    showToast({ message: t('launchpad_subscribe.invalid_subscription_amount'), icon: 'fail' })
    return
  }
  const authorized = await ensureAuthorization()
  if (!authorized) return

  const amount = Number(subscriptionAmount.value)
  const result = await runAction('subscriptionLoading', async () => {
    return launchpadEngine.subscribe({
      project: {
        ...project,
        directRemainingAllocation: directRemainingAllocation.value,
        subscriptionPrice: subscriptionPrice.value,
        raisedAmount: raisedAmount.value,
        totalRaise: totalRaise.value,
        settlementTime: settlementTime.value,
        listingTime: listingTime.value
      },
      amount,
      assetStore,
      remainingAllocation: directRemainingAllocation.value
    })
  })
  if (result?.ok) {
    subscriptionAmount.value = ''
    setFeedback({ success: t('launchpad_subscribe.subscription_success') })
    showToast({ message: t('launchpad_subscribe.subscription_success'), icon: 'success' })
  }
}

const confirmStake = async () => {
  if (!(await ensureWalletConnected())) return
  if (!canConfirmStake.value) {
    showToast({ message: t('launchpad_subscribe.invalid_staking_amount'), icon: 'fail' })
    return
  }
  const authorized = await ensureAuthorization()
  if (!authorized) return

  const pool = selectedStakePool.value
  const result = await runAction('stakingLoading', async () => {
    return launchpadEngine.stake({
      project: {
        ...project,
        stakingStartTime: stakingStartTime.value,
        stakingEndTime: stakingEndTime.value,
        listingTime: listingTime.value
      },
      asset: pool.asset,
      amount: Number(stakeAmount.value),
      assetStore,
      pool
    })
  })
  if (result?.ok) {
    stakeAmount.value = ''
    setFeedback({ success: t('launchpad_subscribe.staking_success') })
    showToast({ message: t('launchpad_subscribe.staking_success'), icon: 'success' })
  }
}

const claimRewards = async (positionId) => {
  if (!(await ensureWalletConnected())) return
  const authorized = await ensureAuthorization()
  if (!authorized) return
  const result = await runAction('claimLoading', async () => {
    return launchpadEngine.claimRewards({ assetStore, positionId, rewardAmount: recordReward(stakingRecords.value.find(record => record.id === positionId)) })
  })
  if (result?.ok) {
    setFeedback({ success: t('launchpad_subscribe.rewards_claimed') })
    showToast({ message: t('launchpad_subscribe.rewards_claimed'), icon: 'success' })
  }
}

const unlockPrincipal = async (positionId) => {
  if (!(await ensureWalletConnected())) return
  const authorized = await ensureAuthorization()
  if (!authorized) return
  actionState.unstakeLoading = positionId
  setFeedback()
  try {
    const result = await launchpadEngine.earlyUnstake({ positionId, assetStore })
    syncWalletState()
    setFeedback({ success: t('launchpad_subscribe.unlock_success') })
    showToast({ message: t('launchpad_subscribe.unlock_success'), icon: 'success' })
    return result
  } catch (error) {
    const message = error.message || t('launchpad_subscribe.unstake_failed')
    setFeedback({ error: message })
    showToast({ message, icon: 'fail' })
  } finally {
    actionState.unstakeLoading = null
  }
}

const canClaimStakeRecord = (record) => isListed.value && stakingRecordStatus(record) !== 'claimed' && recordReward(record) > 0
const canUnlockPrincipal = (record) => isListed.value && stakingRecordStatus(record) !== 'unlocked'

const stakingPrimaryLabel = (record) => {
  if (canClaimStakeRecord(record)) return t('launchpad_subscribe.claim_rewards')
  if (canUnlockPrincipal(record)) return t('launchpad_subscribe.unlock_principal')
  return t('launchpad_subscribe.stake_more')
}

const stakingPrimaryDisabled = (record) => {
  if (canClaimStakeRecord(record)) return Boolean(actionState.claimLoading)
  if (canUnlockPrincipal(record)) return actionState.unstakeLoading === record.id
  return !canStakeNow.value
}

const runStakingPrimaryAction = (record) => {
  if (canClaimStakeRecord(record)) {
    claimRewards(record.id)
    return
  }
  if (canUnlockPrincipal(record)) {
    unlockPrincipal(record.id)
    return
  }
  prepareStakeMore(record.asset)
}

const prepareStakeMore = (asset) => {
  selectedStakeAsset.value = asset
  activeMode.value = 'stake'
}

const selectStakeAsset = (asset) => {
  selectedStakeAsset.value = asset
  showStakeAssetMenu.value = false
}

const startProgressTimer = () => {
  if (progressTimer) clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    if (progress.value >= 100) return
    progress.value = normalizeProgress(progress.value + (Math.random() * 0.16 + 0.04))
  }, 2600)
}

const startClockTimer = () => {
  if (clockTimer) clearInterval(clockTimer)
  clockTimer = setInterval(() => {
    now.value = Date.now()
  }, 1000)
}

const hydrateWalletState = async () => {
  try {
    await launchpadEngine.bootstrapWallet()
  } catch (error) {
    console.warn('[LaunchpadSubscribe] wallet bootstrap skipped:', error)
  } finally {
    syncWalletState()
    if (walletState.connected && !assetStore.isWalletConnected) {
      assetStore.isWalletConnected = true
      assetStore.walletAddress = walletState.address
    }
  }
}

onMounted(() => {
  initializeFundingModel()
  initializeMockSubscriptionBalances()
  syncWalletState()
  startProgressTimer()
  startClockTimer()
  hydrateWalletState()
})

onUnmounted(() => {
  if (progressTimer) clearInterval(progressTimer)
  if (clockTimer) clearInterval(clockTimer)
})
</script>

<style scoped>
.launchpad-subscribe-page {
  --lp-yellow: var(--color-primary);
  --lp-yellow-soft: var(--color-primary-soft);
  --lp-yellow-text: var(--color-text-on-accent);
  --lp-bg: var(--color-bg);
  --lp-card: var(--color-bg-card);
  --lp-border: var(--color-border);
  --lp-text: var(--color-text-primary);
  --lp-muted: var(--color-text-secondary);
  --lp-subtle: var(--color-text-muted);
  --lp-soft: var(--color-surface-1);
  --lp-soft-strong: var(--color-surface-muted);
  min-height: 100vh;
  background: var(--lp-bg);
  color: var(--lp-text);
  font-variant-numeric: tabular-nums;
}

.launchpad-subscribe-page,
.launchpad-subscribe-page * {
  box-sizing: border-box;
}

.subscribe-content {
  padding: 12px 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.project-hero,
.top-info-card,
.funding-card,
.action-card,
.wallet-gate-card,
.action-feedback {
  background: var(--lp-card);
  border: 1px solid var(--lp-border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
}

.project-hero {
  min-height: 88px;
  max-height: 112px;
  display: flex;
  gap: 12px;
  padding: 16px;
  align-items: center;
}

.project-mark {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--lp-yellow);
  color: var(--lp-yellow-text);
  font-weight: 800;
  font-size: 18px;
  flex: 0 0 auto;
}

.project-copy {
  min-width: 0;
  flex: 1;
}

.project-kicker {
  color: var(--lp-yellow);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
}

.project-copy h1 {
  margin: 2px 0 0;
  font-size: 20px;
  line-height: 1.2;
  font-weight: 700;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 7px;
}

.project-meta span {
  max-width: 100%;
  font-size: 12px;
  color: var(--lp-muted);
  background: var(--lp-soft);
  border-radius: 999px;
  padding: 3px 7px;
  white-space: nowrap;
}

.project-detail-card {
  padding: 14px 16px;
  background: var(--lp-card);
  border: 1px solid var(--lp-border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
}

.detail-toggle {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--lp-text);
  font-size: 15px;
  font-weight: 800;
}

.project-detail-card p {
  margin: 10px 0 0;
  color: var(--lp-muted);
  font-size: 13px;
  line-height: 1.5;
}

.project-detail-card p.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tokenomics-preview {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
}

.pie-chart {
  width: 68px;
  height: 68px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: conic-gradient(var(--lp-yellow) 0 40%, var(--lp-soft-strong) 40% 75%, var(--lp-border) 75% 100%);
  color: var(--lp-text);
  font-size: 14px;
  font-weight: 800;
}

.tokenomics-table {
  display: grid;
  gap: 7px;
}

.tokenomics-table div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  color: var(--lp-muted);
  font-size: 12px;
}

.tokenomics-table strong {
  color: var(--lp-text);
}

.top-info-card {
  min-height: 112px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stage-row,
.stats-row {
  display: grid;
  gap: 10px;
}

.stage-row {
  grid-template-columns: 1fr auto;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--lp-border);
}

.stats-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stage-row > div,
.stats-row > div {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-row > div + div {
  padding-left: 10px;
  border-left: 1px solid var(--lp-border);
}

.stage-row span,
.stats-row span,
.available-row span,
.record-grid span,
.asset-select small,
.asset-select-meta,
.asset-sheet-list small {
  color: var(--lp-muted);
  font-size: 12px;
  font-weight: 400;
}

.stage-row strong,
.stats-row strong {
  min-width: 0;
  color: var(--lp-text);
  font-size: 15px;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.countdown-cell strong {
  color: var(--lp-yellow);
  font-size: 17px;
  font-weight: 700;
}

.funding-card {
  min-height: 86px;
  padding: 13px 14px 12px;
}

.funding-row,
.available-row,
.wallet-gate-card,
.order-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.funding-row {
  color: var(--lp-text);
  font-size: 15px;
  font-weight: 700;
}

.funding-row strong {
  font-size: 16px;
  font-weight: 700;
}

.funding-row.muted {
  margin-top: 7px;
  color: var(--lp-muted);
  font-size: 12px;
  font-weight: 500;
}

.funding-bar {
  height: 8px;
  margin-top: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--lp-soft-strong);
}

.funding-bar > div {
  height: 100%;
  border-radius: inherit;
  background: var(--lp-yellow);
  transition: width 600ms ease;
}

.mode-tabs {
  height: 48px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 4px;
  border-radius: 14px;
  background: var(--lp-card);
  border: 1px solid var(--lp-border);
}

.mode-tabs button {
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--lp-muted);
  font-size: 15px;
  font-weight: 700;
}

.mode-tabs button.active {
  background: var(--lp-yellow);
  color: var(--lp-yellow-text);
}

.action-card,
.wallet-gate-card,
.action-feedback {
  padding: 16px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  color: var(--lp-muted);
  font-size: 13px;
  font-weight: 500;
}

.field-label.spaced {
  margin-top: 14px;
}

.amount-field {
  height: 58px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: var(--lp-soft);
  border: 1px solid var(--lp-border);
  border-radius: 12px;
}

.amount-field:focus-within {
  border-color: var(--lp-yellow);
  box-shadow: 0 0 0 2px rgb(var(--color-primary-rgb) / 0.10);
}

.amount-field input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--lp-text);
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

.amount-field input::placeholder {
  color: var(--lp-subtle);
  font-size: 18px;
  font-weight: 600;
}

.amount-field span {
  color: var(--lp-text);
  font-size: 15px;
  font-weight: 700;
}

.available-row {
  min-height: 30px;
  margin-top: 6px;
}

.available-row:first-of-type {
  margin-top: 12px;
}

.available-row strong {
  color: var(--lp-text);
  text-align: right;
  font-size: 15px;
  font-weight: 600;
}

.lottery-ratio-row {
  min-height: 38px;
  margin-top: 10px;
  padding: 0 12px;
  border-radius: 12px;
  background: var(--lp-yellow-soft);
  border: 1px solid var(--color-primary-border);
}

.lottery-ratio-row span {
  color: var(--lp-text);
  font-weight: 700;
}

.lottery-ratio-row strong {
  color: var(--lp-text);
  font-weight: 900;
}

.primary-action,
.ghost-action {
  border: 0;
  border-radius: 11px;
  font-weight: 800;
  min-height: 48px;
}

.primary-action {
  width: 100%;
  margin-top: 14px;
  background: var(--lp-yellow);
  color: var(--lp-yellow-text);
  font-size: 15px;
}

.primary-action:disabled {
  opacity: 1;
  background: var(--lp-soft-strong);
  color: var(--lp-muted);
}

.ghost-action {
  padding: 0 14px;
  color: var(--lp-text);
  background: var(--lp-soft);
  border: 1px solid var(--lp-border);
}

.ghost-action.full {
  width: 100%;
  margin-top: 10px;
}

.asset-select {
  width: 100%;
  min-height: 60px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--lp-border);
  background: var(--lp-soft);
  color: var(--lp-text);
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
  gap: 12px;
}

.asset-select span {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.asset-select strong {
  font-size: 15px;
  font-weight: 700;
}

.asset-select-meta {
  flex: 0 0 auto;
  align-items: flex-end;
  text-align: right;
}

.asset-select-meta :deep(.van-icon) {
  display: inline-block;
  margin-left: 4px;
  vertical-align: -1px;
}

.records-section {
  margin-top: 16px;
}

.records-heading {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.records-heading h2 {
  margin: 0;
  font-size: 17px;
  line-height: 1.2;
  font-weight: 700;
}

.records-heading span {
  color: var(--lp-muted);
  font-size: 12px;
  font-weight: 500;
}

.empty-record {
  padding: 14px;
  text-align: center;
  color: var(--lp-muted);
  background: var(--lp-soft);
  border-radius: 12px;
  font-size: 13px;
}

.record-stack {
  position: relative;
  min-height: 174px;
  margin-bottom: 2px;
}

.record-stack.stake-stack {
  min-height: 214px;
}

.stack-card {
  position: absolute;
  left: 10px;
  right: 10px;
  height: 64px;
  border: 1px solid var(--lp-border);
  border-radius: 14px;
  background: var(--lp-card);
  box-shadow: var(--shadow-sm);
}

.stack-card.ghost-one {
  bottom: 8px;
  opacity: 0.78;
}

.stack-card.ghost-two {
  bottom: 0;
  left: 20px;
  right: 20px;
  opacity: 0.46;
}

.order-card {
  padding: 14px;
  background: var(--lp-card);
  border: 1px solid var(--lp-border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
}

.stack-main {
  position: relative;
  z-index: 1;
}

.sheet-record-list .order-card + .order-card {
  margin-top: 10px;
}

.order-card-head strong {
  min-width: 0;
  font-size: 16px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  height: 22px;
  display: inline-flex;
  align-items: center;
  padding: 0 8px;
  border-radius: 999px;
  color: var(--lp-muted);
  background: var(--lp-soft-strong);
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.success {
  color: var(--color-earn);
  background: rgb(var(--color-earn-rgb) / 0.12);
}

.status-badge.won {
  color: var(--lp-text);
  background: var(--lp-yellow-soft);
  border: 1px solid var(--color-primary-border);
  box-shadow: 0 5px 14px rgb(var(--color-primary-rgb) / 0.18);
  font-weight: 800;
}

.status-badge.pending {
  color: var(--lp-text);
  background: var(--lp-yellow-soft);
  border: 1px solid var(--color-primary-border);
}

.status-badge.active-stake {
  color: var(--color-earn);
  background: rgb(var(--color-earn-rgb) / 0.12);
  border: 1px solid rgb(var(--color-earn-rgb) / 0.28);
}

.status-badge.warning {
  color: var(--lp-text);
  background: var(--lp-yellow-soft);
}

.status-badge.danger {
  color: var(--color-loss);
  background: rgb(var(--color-loss-rgb) / 0.12);
}

.status-badge.muted {
  opacity: 0.78;
}

.record-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 12px;
  align-items: center;
}

.compact-record-grid {
  margin-top: 14px;
  gap: 10px 14px;
}

.compact-record-grid span {
  font-size: 12px;
}

.compact-record-grid strong {
  font-size: 14px;
}

.ratio-value {
  color: var(--lp-text) !important;
  font-weight: 800 !important;
}

.record-grid strong {
  color: var(--lp-text);
  text-align: right;
  font-size: 14px;
  font-weight: 600;
}

.win-result {
  margin-top: 10px;
  padding: 14px;
  border-radius: 14px;
  background:
    radial-gradient(circle at 88% 10%, rgb(var(--color-primary-rgb) / 0.22), transparent 34%),
    linear-gradient(180deg, var(--lp-yellow-soft) 0%, var(--lp-card) 100%);
  border: 1px solid var(--color-primary-border);
  color: var(--lp-text);
  box-shadow: 0 10px 24px rgb(var(--color-primary-rgb) / 0.13);
}

.win-result span {
  display: block;
  color: var(--lp-muted);
  font-size: 12px;
  font-weight: 700;
}

.win-result strong {
  display: block;
  margin-top: 5px;
  color: var(--lp-text);
  font-size: 22px;
  line-height: 1.12;
  font-weight: 900;
}

.compact-primary-action {
  width: 100%;
  height: 38px;
  margin-top: 12px;
  border: 0;
  border-radius: 10px;
  background: var(--lp-yellow);
  color: var(--lp-yellow-text);
  font-size: 13px;
  font-weight: 700;
}

.compact-primary-action:disabled {
  opacity: 1;
  background: var(--lp-soft-strong);
  color: var(--lp-muted);
}

.view-all-action {
  width: 100%;
  height: 40px;
  margin-top: 10px;
  border: 0;
  border-radius: 10px;
  background: var(--lp-yellow-soft);
  color: var(--lp-text);
  font-size: 13px;
  font-weight: 700;
}

.wallet-gate-card span {
  display: block;
  margin-top: 3px;
  color: var(--lp-muted);
  font-size: 12px;
}

.action-feedback {
  color: var(--color-loss);
  font-size: 13px;
  font-weight: 700;
}

.stake-asset-sheet {
  max-height: 70vh;
  overflow: hidden;
  border-radius: 20px 20px 0 0;
  background: var(--lp-card);
  padding-bottom: env(safe-area-inset-bottom);
}

.records-sheet {
  max-height: 75vh;
  overflow: hidden;
  border-radius: 20px 20px 0 0;
  background: var(--lp-card);
  padding-bottom: env(safe-area-inset-bottom);
}

.sheet-record-list {
  max-height: calc(75vh - 58px);
  overflow-y: auto;
  padding: 0 16px 16px;
}

.sheet-handle {
  width: 40px;
  height: 4px;
  margin: 10px auto 8px;
  border-radius: 999px;
  background: var(--lp-border);
}

.sheet-title {
  padding: 0 20px 12px;
  color: var(--lp-text);
  font-size: 17px;
  font-weight: 700;
}

.asset-sheet-list {
  max-height: calc(70vh - 58px);
  overflow-y: auto;
  padding: 0 16px 16px;
}

.asset-sheet-list button {
  width: 100%;
  min-height: 64px;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-bottom-color: var(--lp-border);
  border-radius: 12px;
  background: var(--lp-card);
  color: var(--lp-text);
  display: grid;
  grid-template-columns: 1fr auto 20px;
  gap: 12px;
  align-items: center;
  text-align: left;
}

.asset-sheet-list button.active {
  border-color: var(--lp-yellow);
  background: var(--lp-yellow-soft);
}

.asset-sheet-list span {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.asset-sheet-list strong {
  font-size: 15px;
  font-weight: 700;
}

.asset-sheet-list :deep(.van-icon) {
  color: var(--lp-yellow);
}

.authorization-modal {
  width: min(88vw, 380px);
  background: transparent;
}

.auth-panel {
  padding: 20px;
  border-radius: 14px;
  background: var(--lp-card);
  color: var(--lp-text);
  border: 1px solid var(--lp-border);
  box-shadow: var(--shadow-lg);
  text-align: center;
}

.auth-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgb(var(--color-primary-rgb) / 0.12);
  color: var(--lp-yellow);
  font-size: 22px;
}

.auth-panel h3 {
  margin: 0;
  font-size: 18px;
}

.auth-panel p {
  margin: 10px 0 0;
  color: var(--lp-muted);
  font-size: 13px;
  line-height: 1.5;
}

:global(html[data-theme='dark']) .launchpad-subscribe-page {
  --lp-bg: #070d19;
  --lp-card: rgb(19 28 43 / 0.92);
  --lp-panel: rgb(14 22 36 / 0.94);
  --lp-panel-soft: rgb(28 40 59 / 0.74);
  --lp-border: rgb(92 111 139 / 0.24);
  --lp-border-strong: rgb(243 186 47 / 0.28);
  --lp-text: #f4f7fb;
  --lp-muted: #9ca9bd;
  --lp-subtle: #6f7d93;
  --lp-yellow-soft: rgb(var(--color-primary-rgb) / 0.16);
  --lp-yellow-text: #121722;
  background:
    radial-gradient(circle at 78% 2%, rgb(var(--color-primary-rgb) / 0.12), transparent 28%),
    linear-gradient(180deg, #0a1220 0%, #070d19 48%, #050914 100%);
}

:global(html[data-theme='dark']) .launchpad-subscribe-page :deep(.van-nav-bar) {
  --van-nav-bar-background: rgb(13 21 34 / 0.94);
  --van-nav-bar-title-text-color: var(--lp-text);
  --van-nav-bar-icon-color: var(--lp-yellow);
  border-bottom: 1px solid rgb(92 111 139 / 0.18);
  box-shadow: 0 10px 28px rgb(0 0 0 / 0.22);
  backdrop-filter: blur(16px);
}

:global(html[data-theme='dark']) .subscribe-content {
  max-width: 520px;
  margin: 0 auto;
  padding: 14px 18px 26px;
  gap: 14px;
}

:global(html[data-theme='dark']) .project-hero,
:global(html[data-theme='dark']) .top-info-card,
:global(html[data-theme='dark']) .funding-card,
:global(html[data-theme='dark']) .action-card,
:global(html[data-theme='dark']) .wallet-gate-card,
:global(html[data-theme='dark']) .action-feedback,
:global(html[data-theme='dark']) .project-detail-card {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgb(255 255 255 / 0.035), rgb(255 255 255 / 0)),
    var(--lp-card);
  border: 1px solid var(--lp-border);
  border-radius: 16px;
  box-shadow:
    0 18px 42px rgb(0 0 0 / 0.26),
    inset 0 1px 0 rgb(255 255 255 / 0.035);
}

:global(html[data-theme='dark']) .project-hero::after,
:global(html[data-theme='dark']) .action-card::after,
:global(html[data-theme='dark']) .funding-card::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at 92% 0%, rgb(var(--color-primary-rgb) / 0.10), transparent 34%);
}

:global(html[data-theme='dark']) .project-mark {
  background:
    radial-gradient(circle at 30% 22%, rgb(255 255 255 / 0.28), transparent 32%),
    linear-gradient(145deg, var(--lp-yellow) 0%, var(--color-primary-hover) 100%);
  box-shadow: 0 12px 28px rgb(var(--color-primary-rgb) / 0.22);
}

:global(html[data-theme='dark']) .project-kicker,
:global(html[data-theme='dark']) .countdown-cell strong {
  color: var(--lp-yellow);
}

:global(html[data-theme='dark']) .project-meta span,
:global(html[data-theme='dark']) .empty-record {
  background: var(--lp-panel-soft);
  color: var(--lp-muted);
  border: 1px solid rgb(255 255 255 / 0.035);
}

:global(html[data-theme='dark']) .stage-row,
:global(html[data-theme='dark']) .stats-row > div + div {
  border-color: rgb(92 111 139 / 0.18);
}

:global(html[data-theme='dark']) .funding-card {
  padding: 14px 18px 16px;
}

:global(html[data-theme='dark']) .funding-bar {
  height: 9px;
  background: rgb(255 255 255 / 0.06);
  box-shadow: inset 0 1px 2px rgb(0 0 0 / 0.34);
}

:global(html[data-theme='dark']) .funding-bar > div {
  background: linear-gradient(90deg, #f6c64a 0%, #f3ba2f 58%, #ffe08a 100%);
  box-shadow:
    0 0 18px rgb(var(--color-primary-rgb) / 0.34),
    inset 0 1px 0 rgb(255 255 255 / 0.42);
}

:global(html[data-theme='dark']) .mode-tabs {
  height: 66px;
  padding: 7px;
  border-radius: 18px;
  background: rgb(14 22 36 / 0.9);
  border-color: rgb(92 111 139 / 0.22);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.035), 0 12px 28px rgb(0 0 0 / 0.18);
}

:global(html[data-theme='dark']) .mode-tabs button {
  border-radius: 13px;
  color: #aeb9cb;
  transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

:global(html[data-theme='dark']) .mode-tabs button.active {
  background: linear-gradient(180deg, #f6c64a 0%, #edb526 100%);
  color: #101723;
  box-shadow: 0 10px 24px rgb(var(--color-primary-rgb) / 0.26);
}

:global(html[data-theme='dark']) .action-card {
  padding: 18px;
}

:global(html[data-theme='dark']) .field-label {
  color: #c9d3e3;
  font-weight: 650;
}

:global(html[data-theme='dark']) .amount-field,
:global(html[data-theme='dark']) .asset-select {
  min-height: 68px;
  padding: 0 18px;
  border-radius: 16px;
  background: rgb(9 16 29 / 0.72);
  border-color: rgb(92 111 139 / 0.32);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / 0.035),
    0 8px 20px rgb(0 0 0 / 0.12);
}

:global(html[data-theme='dark']) .amount-field:focus-within,
:global(html[data-theme='dark']) .asset-select:focus-visible {
  border-color: rgb(var(--color-primary-rgb) / 0.62);
  box-shadow:
    0 0 0 3px rgb(var(--color-primary-rgb) / 0.10),
    0 12px 28px rgb(0 0 0 / 0.18);
}

:global(html[data-theme='dark']) .amount-field input {
  color: var(--lp-text);
  font-size: 21px;
}

:global(html[data-theme='dark']) .amount-field input::placeholder {
  color: #6f7f99;
}

:global(html[data-theme='dark']) .amount-field span,
:global(html[data-theme='dark']) .available-row strong {
  color: #f7fafc;
}

:global(html[data-theme='dark']) .available-row {
  min-height: 38px;
  padding: 2px 0;
}

:global(html[data-theme='dark']) .lottery-ratio-row {
  min-height: 58px;
  margin-top: 14px;
  padding: 0 14px;
  border-radius: 14px;
  background:
    radial-gradient(circle at 86% 18%, rgb(var(--color-primary-rgb) / 0.16), transparent 32%),
    rgb(var(--color-primary-rgb) / 0.10);
  border-color: var(--lp-border-strong);
}

:global(html[data-theme='dark']) .lottery-ratio-row span,
:global(html[data-theme='dark']) .lottery-ratio-row strong {
  color: #fff6d6;
}

:global(html[data-theme='dark']) .primary-action {
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f6c64a 0%, #e8ad20 100%);
  color: #101723;
  box-shadow: 0 14px 28px rgb(var(--color-primary-rgb) / 0.24);
}

:global(html[data-theme='dark']) .primary-action:disabled {
  background: rgb(35 48 68 / 0.82);
  color: #8796ad;
  box-shadow: none;
}

:global(html[data-theme='dark']) .records-section {
  margin-top: 20px;
}

:global(html[data-theme='dark']) .records-heading {
  margin-bottom: 12px;
}

:global(html[data-theme='dark']) .records-heading h2 {
  color: var(--lp-text);
  font-size: 20px;
  font-weight: 850;
}

:global(html[data-theme='dark']) .order-card,
:global(html[data-theme='dark']) .stack-card {
  background:
    linear-gradient(180deg, rgb(255 255 255 / 0.035), rgb(255 255 255 / 0)),
    rgb(12 20 34 / 0.82);
  border-color: rgb(92 111 139 / 0.22);
  box-shadow:
    0 16px 36px rgb(0 0 0 / 0.22),
    inset 0 1px 0 rgb(255 255 255 / 0.035);
}

:global(html[data-theme='dark']) .order-card {
  padding: 18px;
  border-radius: 16px;
}

:global(html[data-theme='dark']) .order-card-head strong {
  color: #ffffff;
  font-size: 18px;
}

:global(html[data-theme='dark']) .status-badge {
  background: rgb(var(--color-primary-rgb) / 0.12);
  color: #fff1bd;
  border: 1px solid rgb(var(--color-primary-rgb) / 0.28);
}

:global(html[data-theme='dark']) .win-result {
  border-radius: 16px;
  background:
    radial-gradient(circle at 84% 12%, rgb(var(--color-primary-rgb) / 0.18), transparent 35%),
    linear-gradient(135deg, rgb(255 255 255 / 0.055) 0%, rgb(var(--color-primary-rgb) / 0.09) 100%);
  border-color: rgb(var(--color-primary-rgb) / 0.34);
}

:global(html[data-theme='dark']) .compact-record-grid {
  gap: 13px 16px;
}

:global(html[data-theme='dark']) .record-grid strong,
:global(html[data-theme='dark']) .ratio-value {
  color: #f7fafc !important;
}

:global(html[data-theme='dark']) .view-all-action,
:global(html[data-theme='dark']) .compact-primary-action {
  border-radius: 13px;
  background: rgb(var(--color-primary-rgb) / 0.14);
  color: #fff1bd;
  border: 1px solid rgb(var(--color-primary-rgb) / 0.18);
}

:global(html[data-theme='dark']) .view-all-action {
  height: 46px;
  margin-top: 14px;
}

@media (max-width: 390px) {
  .subscribe-content {
    padding-left: 12px;
    padding-right: 12px;
  }
}
</style>
