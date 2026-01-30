<template>
  <div class="position-item" @click="handleClick">
    <!-- Header -->
    <div class="item-header">
      <div class="symbol-info">
        <span class="symbol">{{ position.symbol }}</span>
        <span :class="['side-badge', position.side === 'LONG' ? 'long' : 'short']">
          {{ position.side === 'LONG' ? '做多' : '做空' }}
        </span>
      </div>
      <div class="action-icon">
        <van-icon name="ellipsis" />
      </div>
    </div>

    <!-- Price & PnL -->
    <div class="price-section">
      <div class="price-row">
        <span class="label">开仓均价</span>
        <span class="value">{{ formatPrice(position.entry_price || position.entryPrice) }}</span>
      </div>
      <div class="price-row">
        <span class="label">当前价格</span>
        <span class="value highlight">{{ formatPrice(position.current_price || position.currentPrice) }}</span>
      </div>
      <div class="price-row">
        <span class="label">未实现盈亏</span>
        <span :class="['value', 'pnl', getPnLClass(position.pnl || position.unrealized_pnl)]">
          {{ formatPnL(position.pnl || position.unrealized_pnl) }}
        </span>
      </div>
    </div>

    <!-- TP/SL Display (Local Memory) -->
    <div class="tpsl-section">
      <div class="tpsl-row">
        <span class="label">止盈 (TP)</span>
        <span class="value tp">
          {{ formatTPSL(position.tp || position.take_profit || position.takeProfit) }}
        </span>
      </div>
      <div class="tpsl-row">
        <span class="label">止损 (SL)</span>
        <span class="value sl">
          {{ formatTPSL(position.sl || position.stop_loss || position.stopLoss) }}
        </span>
      </div>
    </div>

    <!-- Position Details -->
    <div class="details-section">
      <div class="detail-item">
        <span class="label">仓位数量</span>
        <span class="value">{{ formatAmount(position.amount || position.size) }}</span>
      </div>
      <div class="detail-item">
        <span class="label">杠杆倍数</span>
        <span class="value">{{ position.leverage || position.leverage_ratio }}x</span>
      </div>
      <div class="detail-item">
        <span class="label">保证金</span>
        <span class="value">{{ formatPrice(position.margin) }} USDT</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  position: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

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
  background: #141414;
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.symbol-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
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
  background: rgba(50, 215, 75, 0.15);
  color: #32D74B;
}

.side-badge.short {
  background: rgba(255, 69, 58, 0.15);
  color: #FF453A;
}

.action-icon {
  color: #8E8E93;
  font-size: 18px;
}

.price-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 12px;
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.value {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

.value.highlight {
  color: #D4AF37;
  font-size: 15px;
}

.value.pnl {
  font-size: 15px;
}

.value.pnl.positive {
  color: #32D74B;
}

.value.pnl.negative {
  color: #FF453A;
}

.tpsl-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 12px;
  background: rgba(28, 28, 30, 0.5);
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
  color: #8E8E93;
}

.tpsl-row .value {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.tpsl-row .value.tp {
  color: #32D74B;
}

.tpsl-row .value.sl {
  color: #FF453A;
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
  color: #8E8E93;
}

.detail-item .value {
  font-size: 13px;
  font-weight: 600;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}
</style>
