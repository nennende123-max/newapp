<template>
  <div class="position-item" @click="handleClick">
    <div class="item-header">
      <div class="symbol-info">
        <span class="symbol">{{ position.symbol }}</span>
        <span :class="['side-badge', position.side === 'LONG' ? 'long' : 'short']">
          {{ position.side === 'LONG' ? t('trade.long') : t('trade.short') }}
        </span>
      </div>
      <div class="action-icon">
        <van-icon name="ellipsis" />
      </div>
    </div>

    <div class="price-section">
      <div class="price-row">
        <span class="label">{{ t('trade.entry_price') }}</span>
        <span class="value">{{ formatPrice(position.entry_price || position.entryPrice) }}</span>
      </div>
      <div class="price-row">
        <span class="label">{{ t('tpsl.current_price') }}</span>
        <span class="value highlight">{{ formatPrice(position.current_price || position.currentPrice) }}</span>
      </div>
      <div class="price-row">
        <span class="label">{{ t('trade.unrealized_pnl') }}</span>
        <span :class="['value', 'pnl', getPnLClass(position.pnl || position.unrealized_pnl)]">
          {{ formatPnL(position.pnl || position.unrealized_pnl) }}
        </span>
      </div>
    </div>

    <div class="tpsl-section">
      <div class="tpsl-row">
        <span class="label">{{ t('tpsl.tp_price') }}</span>
        <span class="value tp">
          {{ formatTPSL(position.tp || position.take_profit || position.takeProfit) }}
        </span>
      </div>
      <div class="tpsl-row">
        <span class="label">{{ t('tpsl.sl_price') }}</span>
        <span class="value sl">
          {{ formatTPSL(position.sl || position.stop_loss || position.stopLoss) }}
        </span>
      </div>
    </div>

    <div class="details-section">
      <div class="detail-item">
        <span class="label">{{ t('trade.position_size') }}</span>
        <span class="value">{{ formatAmount(position.amount || position.size) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">{{ t('trade.select_leverage') }}</span>
        <span class="value">{{ position.leverage || position.leverage_ratio }}x</span>
      </div>
      <div class="detail-item">
        <span class="label">{{ t('trade.margin_amount') }}</span>
        <span class="value">{{ formatPrice(position.margin) }} USDT</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const props = defineProps({
  position: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])
const { t } = useI18n()

const handleClick = () => {
  emit('click', props.position)
}

const formatPrice = (price) => {
  if (!price) return '--'
  return parseFloat(price).toFixed(2)
}

const formatAmount = (amount) => {
  if (!amount) return '--'
  return parseFloat(amount).toFixed(4)
}

const formatPnL = (pnl) => {
  if (!pnl) return '0.00'
  const value = parseFloat(pnl)
  return value > 0 ? `+${value.toFixed(2)}` : value.toFixed(2)
}

const formatTPSL = (value) => {
  if (!value) return '--'
  return parseFloat(value).toFixed(2)
}

const getPnLClass = (pnl) => {
  if (!pnl) return ''
  const value = parseFloat(pnl)
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}
</script>

<style scoped>
.position-item {
  background: var(--color-bg-input);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.position-item:active {
  opacity: 0.8;
  transform: scale(0.98);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.symbol-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

.side-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.side-badge.long {
  background: rgb(var(--color-earn-rgb) / 0.15);
  color: var(--color-earn);
}

.side-badge.short {
  background: rgb(var(--color-loss-rgb) / 0.15);
  color: var(--color-loss);
}

.action-icon {
  color: var(--color-text-secondary);
  font-size: 18px;
}

.price-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

.value.highlight {
  color: var(--color-accent);
  font-size: 15px;
}

.value.pnl {
  font-size: 15px;
}

.value.pnl.positive {
  color: var(--color-earn);
}

.value.pnl.negative {
  color: var(--color-loss);
}

.tpsl-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 12px;
  background: rgb(var(--color-surface-rgb) / 0.5);
  border-radius: 8px;
  margin-bottom: 12px;
}

.tpsl-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tpsl-row .label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.tpsl-row .value {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.tpsl-row .value.tp {
  color: var(--color-earn);
}

.tpsl-row .value.sl {
  color: var(--color-loss);
}

.details-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item .label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.detail-item .value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}
</style>
