<template>
  <van-popup
    v-model:show="show"
    position="bottom"
    round
    :style="{ background: '#1C1C1E', maxHeight: '75vh' }"
  >
    <div class="tpsl-dialog">
      <!-- Header -->
      <div class="dialog-header">
        <div class="header-title">设置止盈止损</div>
        <van-icon name="cross" @click="handleClose" class="close-icon" />
      </div>

      <!-- Position Info -->
      <div v-if="position" class="position-info">
        <div class="info-row">
          <span class="label">持仓</span>
          <span class="value">{{ position.symbol }}</span>
        </div>
        <div class="info-row">
          <span class="label">方向</span>
          <span :class="['value', position.side === 'LONG' ? 'text-green' : 'text-red']">
            {{ position.side === 'LONG' ? '做多' : '做空' }}
          </span>
        </div>
        <div class="info-row">
          <span class="label">当前价格</span>
          <span class="value price">{{ formatPrice(position.current_price || position.currentPrice) }}</span>
        </div>
      </div>

      <!-- Form -->
      <div class="form-section">
        <div class="form-item">
          <div class="form-label">
            <span>止盈价格 (TP)</span>
            <span class="hint">价格达到后自动平仓获利</span>
          </div>
          <van-field
            v-model="form.tp"
            type="number"
            placeholder="输入止盈价格"
            class="custom-field"
          />
        </div>

        <div class="form-item">
          <div class="form-label">
            <span>止损价格 (SL)</span>
            <span class="hint">价格达到后自动平仓止损</span>
          </div>
          <van-field
            v-model="form.sl"
            type="number"
            placeholder="输入止损价格"
            class="custom-field"
          />
        </div>
      </div>

      <!-- Local Memory Indicator -->
      <div v-if="hasLocalMemory" class="memory-indicator">
        <van-icon name="warning-o" />
        <span>已从本地记忆恢复</span>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <van-button
          class="btn-cancel"
          @click="handleClose"
        >
          取消
        </van-button>
        <van-button
          class="btn-confirm"
          :loading="loading"
          @click="handleConfirm"
        >
          确认
        </van-button>
      </div>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useAssetStore } from '@/stores/assets'
import { showToast } from 'vant'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  position: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:show', 'success'])

const assetStore = useAssetStore()
const loading = ref(false)
const hasLocalMemory = ref(false)

const form = ref({
  tp: '',
  sl: ''
})

// Helper function to get localStorage key (consistent with TradeSubPage.vue)
const getTPSLStorageKey = (symbol) => {
  if (!symbol) return null
  const normalizedSymbol = symbol.replace('/USDT', '').replace('USDT', '').toUpperCase()
  return `tpsl_mem_${normalizedSymbol}`
}

// Watch for dialog open/close and load saved values
watch(() => props.show, (val) => {
  if (val && props.position) {
    // Load from localStorage (Local Memory)
    const key = getTPSLStorageKey(props.position.symbol)
    const saved = localStorage.getItem(key)
    
    if (saved) {
      try {
        const data = JSON.parse(saved)
        // FORCE overwrite the form with saved local data
        form.value.tp = data.tp || ''
        form.value.sl = data.sl || ''
        hasLocalMemory.value = true
        console.log(`[TP/SL Memory] Loaded from localStorage: ${key}`, data)
      } catch (error) {
        console.error('[TP/SL Memory] Parse error:', error)
        hasLocalMemory.value = false
        // Fallback to current position values
        form.value.tp = props.position.tp || props.position.take_profit || props.position.takeProfit || ''
        form.value.sl = props.position.sl || props.position.stop_loss || props.position.stopLoss || ''
      }
    } else {
      hasLocalMemory.value = false
      // Load from current position
      form.value.tp = props.position.tp || props.position.take_profit || props.position.takeProfit || ''
      form.value.sl = props.position.sl || props.position.stop_loss || props.position.stopLoss || ''
    }
  } else if (!val) {
    // Reset on close
    hasLocalMemory.value = false
  }
})

const handleClose = () => {
  emit('update:show', false)
}

const handleConfirm = async () => {
  if (!props.position) return

  // Validate input
  const tp = parseFloat(form.value.tp)
  const sl = parseFloat(form.value.sl)

  if (!tp && !sl) {
    showToast('请至少设置止盈或止损价格')
    return
  }

  if (tp && isNaN(tp)) {
    showToast('止盈价格格式错误')
    return
  }

  if (sl && isNaN(sl)) {
    showToast('止损价格格式错误')
    return
  }

  loading.value = true

  try {
    // Save to localStorage BEFORE API call (Local Memory)
    const key = getTPSLStorageKey(props.position.symbol)
    localStorage.setItem(key, JSON.stringify({ 
      tp: form.value.tp, 
      sl: form.value.sl,
      timestamp: Date.now()
    }))
    console.log(`[TP/SL Memory] Saved to localStorage: ${key}`, { tp: form.value.tp, sl: form.value.sl })

    // Call API to set TP/SL
    await assetStore.setTPSL({
      positionId: props.position.id,
      tp: tp || null,
      sl: sl || null
    })

    showToast('设置成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('[TP/SL] Set error:', error)
    showToast(error.message || '设置失败，但已保存到本地')
    // Even if API fails, we keep the local memory
  } finally {
    loading.value = false
  }
}

const formatPrice = (price) => {
  if (!price) return '--'
  return parseFloat(price).toFixed(2)
}
</script>

<style scoped>
.tpsl-dialog {
  padding: 20px;
  background: #1C1C1E;
  color: #FFFFFF;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.close-icon {
  font-size: 20px;
  color: #8E8E93;
  cursor: pointer;
  transition: color 0.3s ease;
}

.close-icon:active {
  color: #FFFFFF;
}

.position-info {
  background: #141414;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.label {
  font-size: 13px;
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.value {
  font-size: 15px;
  font-weight: 600;
  color: #FFFFFF;
}

.value.price {
  font-variant-numeric: tabular-nums;
}

.text-green {
  color: #32D74B;
}

.text-red {
  color: #FF453A;
}

.form-section {
  margin-bottom: 20px;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.form-label > span:first-child {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  margin-bottom: 4px;
}

.hint {
  font-size: 12px;
  color: #8E8E93;
}

.custom-field {
  background: #141414;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 15px;
  color: #FFFFFF;
  transition: all 0.3s ease;
}

.custom-field:focus {
  border-color: #D4AF37;
}

:deep(.van-field__control) {
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

:deep(.van-field__control::placeholder) {
  color: #8E8E93;
}

.memory-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #D4AF37;
}

.memory-indicator .van-icon {
  font-size: 16px;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  height: 48px;
  border-radius: 8px;
  background: #2C2C2E;
  color: #FFFFFF;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-cancel:active {
  opacity: 0.7;
  transform: scale(0.98);
}

.btn-confirm {
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #D4AF37 0%, #C5A059 100%);
  color: #000000;
  border: none;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-confirm:active {
  opacity: 0.8;
  transform: scale(0.98);
}

:deep(.van-popup) {
  background: #1C1C1E;
}
</style>
