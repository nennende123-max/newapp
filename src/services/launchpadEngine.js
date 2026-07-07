import walletService from '@/services/walletService'
import { APP_MODES, getAppMode } from '@/config/appMode'

const signedScopes = new Set()

const toNumber = (value) => Number(value) || 0

const createResult = (ok, payload = {}) => ({
  ok,
  timestamp: new Date().toISOString(),
  ...payload
})

const getAssetPrice = (asset, assetStore) => {
  const fallback = { USDT: 1, USDC: 1, FDUSD: 1, ETH: 3100, BTC: 92000, BNB: 590 }
  return assetStore.priceMap?.[asset] || fallback[asset] || 1
}

const calculateStakeMetrics = ({ project, asset, amount, assetStore, pool }) => {
  const amountValue = toNumber(amount)
  const price = getAssetPrice(asset, assetStore)
  const amountUsdt = amountValue * price
  const now = Date.now()
  const stakingStartTime = toNumber(project?.stakingStartTime) || now
  const stakingEndTime = toNumber(project?.stakingEndTime) || (now + 30 * 24 * 60 * 60 * 1000)
  const listingTime = toNumber(project?.listingTime) || stakingEndTime
  const activeEnd = Math.min(now, stakingEndTime, listingTime)
  const activeSeconds = Math.max(0, (activeEnd - now) / 1000)
  const poolDurationSeconds = Math.max(1, (stakingEndTime - stakingStartTime) / 1000)
  const poolRewardAllocation = toNumber(pool?.poolRewardAllocation)
  const totalPoolStakeAmount = Math.max(1, toNumber(pool?.totalPoolStakeAmount) || amountValue)
  const userStakeShare = amountValue / totalPoolStakeAmount
  const timeRatio = Math.min(1, activeSeconds / poolDurationSeconds)
  const estimatedReward = poolRewardAllocation * userStakeShare * timeRatio
  const rewardPrice = toNumber(project?.price) || 1
  const dailyRate = 0.006
  return {
    amountUsdt,
    estimatedReward,
    finalRewardToken: 0,
    dailyRate,
    rewardPrice,
    dailyRewardToken: amountUsdt * dailyRate / rewardPrice,
    poolRewardAllocation,
    totalPoolStakeAmount,
    rewardTicker: pool?.rewardToken || project?.ticker || 'GMT',
    apy: toNumber(pool?.apy)
  }
}

class LaunchpadEngine {
  constructor() {
    this.subscriptionState = {
      records: [],
      lastResult: null
    }
    this.stakingState = {
      lastResult: null
    }
    this.rewardState = {
      lastClaim: null
    }
  }

  getWalletState() {
    return walletService.getWalletState()
  }

  async bootstrapWallet() {
    if (getAppMode() === APP_MODES.DEV && !walletService.getWalletState().connected) {
      await walletService.connectWallet()
    }
    return this.getWalletState()
  }

  async ensureWallet() {
    let state = walletService.getWalletState()
    if (!state.connected) {
      await walletService.connectWallet()
      state = walletService.getWalletState()
    }
    return state
  }

  async ensureSigned(scope, project) {
    const wallet = await this.ensureWallet()
    const key = `${wallet.address}:${scope}:${project?.ticker || 'PROJECT'}`
    if (signedScopes.has(key)) return wallet

    await walletService.signMessage(`TruthFi Subscription ${scope}: ${project?.ticker || 'PROJECT'}`)
    signedScopes.add(key)
    return wallet
  }

  ensureDevLiquidity(assetStore, asset, requiredAmount) {
    if (getAppMode() !== APP_MODES.DEV) return
    const amount = toNumber(requiredAmount)
    if (asset === 'USDT') {
      return
    }

    const current = assetStore.holdings?.[asset] || 0
    if (current < amount) {
      assetStore.holdings[asset] = amount + 1
    }
  }

  validateSubscription({ amount, assetStore, remainingAllocation }) {
    const value = toNumber(amount)
    const allocation = remainingAllocation === undefined
      ? assetStore.launchpadRemainingAllocation
      : toNumber(remainingAllocation)
    if (value <= 0) throw new Error('Invalid subscription amount')
    if (value > allocation) throw new Error('Subscription amount exceeds allocation')
    if ((assetStore.usdtBalance || 0) < value) throw new Error('Insufficient USDT balance')
  }

  async subscribe({ project, amount, assetStore, remainingAllocation }) {
    await this.ensureSigned('subscription', project)
    this.validateSubscription({ amount, assetStore, remainingAllocation })

    const success = assetStore.subscribeLaunchpad(project, amount, 'fixed')
    if (!success) throw new Error('Subscription failed')

    const records = Array.isArray(assetStore.idoRecords) ? assetStore.idoRecords : []
    const record = records[records.length - 1] || null
    this.subscriptionState.records = [...records]
    this.subscriptionState.lastResult = createResult(true, { record })
    return this.subscriptionState.lastResult
  }

  validateStake({ asset, amount, assetStore }) {
    const value = toNumber(amount)
    if (value <= 0) throw new Error('Invalid staking amount')
    const balance = asset === 'USDT' ? assetStore.usdtBalance : assetStore.getHolding(asset)
    if ((balance || 0) < value) throw new Error(`Insufficient ${asset} balance`)
  }

  async stake({ project, asset, amount, assetStore, pool }) {
    await this.ensureSigned('staking', project)
    this.ensureDevLiquidity(assetStore, asset, amount)
    this.validateStake({ asset, amount, assetStore })

    const metrics = calculateStakeMetrics({ project, asset, amount, assetStore, pool })
    const success = assetStore.addLaunchpadStake(project, asset, amount, metrics)
    if (!success) throw new Error('Staking failed')

    const position = this.getStakingPosition({ project, asset, assetStore })
    this.stakingState.lastResult = createResult(true, { position, metrics })
    return this.stakingState.lastResult
  }

  getStakingPosition({ project, asset, assetStore }) {
    const positions = Array.isArray(assetStore.launchpadStakingPositions)
      ? assetStore.launchpadStakingPositions
      : []
    if (!project && !asset) return positions
    return positions.find(position => (
      (!project || position.projectTicker === project.ticker) &&
      (!asset || position.asset === asset)
    )) || null
  }

  updatePosition({ positionId, patch, assetStore }) {
    const positions = Array.isArray(assetStore.launchpadStakingPositions)
      ? assetStore.launchpadStakingPositions
      : []
    const index = positions.findIndex(position => position.id === positionId)
    if (index < 0) return null
    positions[index] = {
      ...positions[index],
      ...patch,
      updatedAt: new Date().toISOString()
    }
    localStorage.setItem('launchpadStakingPositions', JSON.stringify(positions))
    return positions[index]
  }

  async claimRewards({ assetStore, positionId, rewardAmount }) {
    await this.ensureSigned('claim_rewards', { ticker: 'REWARD' })
    const rewards = toNumber(rewardAmount) || assetStore.launchpadTotalRewards
    const success = assetStore.claimLaunchpadRewards(positionId, rewards)
    if (!success) throw new Error('No claimable rewards')
    this.rewardState.lastClaim = createResult(true, {
      rewards
    })
    return this.rewardState.lastClaim
  }

  async earlyUnstake({ positionId, assetStore }) {
    await this.ensureSigned('early_unstake', { ticker: 'UNSTAKE' })
    const success = assetStore.earlyUnstakeLaunchpad(positionId)
    if (!success) throw new Error('Unstake failed')
    return createResult(true, { positionId })
  }
}

export const launchpadEngine = new LaunchpadEngine()
export default launchpadEngine
