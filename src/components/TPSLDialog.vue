<template>
  <van-popup
    v-model:show="show"
    position="bottom"
    round
    :style="{ background: 'var(--color-bg-card)', maxHeight: '75vh' }"
  >
    <div class="tpsl-dialog">
      <div class="dialog-header">
        <div class="header-title">{{ t('tpsl.title') }}</div>
        <van-icon name="cross" @click="handleClose" class="close-icon" />
      </div>

      <div v-if="position" class="position-info">
        <div class="info-row">
          <span class="label">{{ t('tpsl.position') }}</span>
          <span class="value">{{ position.symbol }}</span>
        </div>
        <div class="info-row">
          <span class="label">{{ t('tpsl.side') }}</span>
          <span :class="['value', position.side === 'LONG' ? 'text-green' : 'text-red']">
            {{ position.side === 'LONG' ? t('tpsl.long') : t('tpsl.short') }}
          </span>
        </div>
        <div class="info-row">
          <span class="label">{{ t('tpsl.current_price') }}</span>
          <span class="value price">{{ formatPrice(position.current_price || position.currentPrice) }}</span>
        </div>
      </div>

      <div class="form-section">
        <div class="form-item">
          <div class="form-label">
            <span>{{ t('tpsl.tp_price') }}</span>
            <span class="hint">{{ t('tpsl.tp_hint') }}</span>
          </div>
          <van-field
            v-model="form.tp"
            type="number"
            :placeholder="t('tpsl.tp_placeholder')"
            class="custom-field"
          />
        </div>

        <div class="form-item">
          <div class="form-label">
            <span>{{ t('tpsl.sl_price') }}</span>
            <span class="hint">{{ t('tpsl.sl_hint') }}</span>
          </div>
          <van-field
            v-model="form.sl"
            type="number"
            :placeholder="t('tpsl.sl_placeholder')"
            class="custom-field"
          />
        </div>
      </div>

      <div v-if="hasLocalMemory" class="memory-indicator">
        <van-icon name="warning-o" />
        <span>{{ t('tpsl.restored') }}</span>
      </div>

      <div class="action-buttons">
        <van-button class="btn-cancel" @click="handleClose">
          {{ t('common.cancel') }}
        </van-button>
        <van-button
          class="btn-confirm"
          :loading="loading"
          @click="handleConfirm"
        >
          {{ t('common.confirm') }}
        </van-button>
      </div>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAssetStore } from '@/stores/assets'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'

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
const { t } = useI18n()
const loading = ref(false)
const hasLocalMemory = ref(false)

const form = ref({
  tp: '',
  sl: ''
})

const getTPSLStorageKey = (symbol) => {
  if (!symbol) return null
  const normalizedSymbol = symbol.replace('/USDT', '').replace('USDT', '').toUpperCase()
  return `tpsl_mem_${normalizedSymbol}`
}

watch(() => props.show, (val) => {
  if (val && props.position) {
    const key = getTPSLStorageKey(props.position.symbol)
    const saved = localStorage.getItem(key)

    if (saved) {
      try {
        const data = JSON.parse(saved)
        form.value.tp = data.tp || ''
        form.value.sl = data.sl || ''
        hasLocalMemory.value = true
        console.log(`[TP/SL Memory] Loaded from localStorage: ${key}`, data)
      } catch (error) {
        console.error('[TP/SL Memory] Parse error:', error)
        hasLocalMemory.value = false
        form.value.tp = props.position.tp || props.position.take_profit || props.position.takeProfit || ''
        form.value.sl = props.position.sl || props.position.stop_loss || props.position.stopLoss || ''
      }
    } else {
      hasLocalMemory.value = false
      form.value.tp = props.position.tp || props.position.take_profit || props.position.takeProfit || ''
      form.value.sl = props.position.sl || props.position.stop_loss || props.position.stopLoss || ''
    }
  } else if (!val) {
    hasLocalMemory.value = false
  }
})

const handleClose = () => {
  emit('update:show', false)
}

const handleConfirm = async () => {
  if (!props.position) return

  const tp = parseFloat(form.value.tp)
  const sl = parseFloat(form.value.sl)

  if (!tp && !sl) {
    showToast(t('tpsl.at_least_one'))
    return
  }

  if (tp && isNaN(tp)) {
    showToast(t('tpsl.tp_invalid'))
    return
  }

  if (sl && isNaN(sl)) {
    showToast(t('tpsl.sl_invalid'))
    return
  }

  loading.value = true

  try {
    const key = getTPSLStorageKey(props.position.symbol)
    localStorage.setItem(key, JSON.stringify({
      tp: form.value.tp,
      sl: form.value.sl,
      timestamp: Date.now()
    }))
    console.log(`[TP/SL Memory] Saved to localStorage: ${key}`, { tp: form.value.tp, sl: form.value.sl })

    await assetStore.setTPSL({
      positionId: props.position.id,
      tp: tp || null,
      sl: sl || null
    })

    showToast(t('tpsl.success'))
    emit('success')
    handleClose()
  } catch (error) {
    console.error('[TP/SL] Set error:', error)
    showToast(error.message || t('tpsl.failed_local_saved'))
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
  background: var(--color-bg-card);
  color: var(--color-text-primary);
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
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.3s ease;
}

.close-icon:active {
  color: var(--color-text-primary);
}

.position-info {
  background: var(--color-bg-input);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
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
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.label {
  font-size: 13px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.value {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.value.price {
  font-variant-numeric: tabular-nums;
}

.text-green {
  color: var(--color-earn);
}

.text-red {
  color: var(--color-loss);
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
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.custom-field {
  background: var(--color-bg-input);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 15px;
  color: var(--color-text-primary);
  transition: all 0.3s ease;
}

.custom-field:focus {
  border-color: var(--color-accent);
}

:deep(.van-field__control) {
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

:deep(.van-field__control::placeholder) {
  color: var(--color-text-secondary);
}

.memory-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgb(var(--color-brand-rgb) / 0.1);
  border: 1px solid rgb(var(--color-brand-rgb) / 0.3);
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
  color: var(--color-accent);
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
  background: var(--color-surface-muted);
  color: var(--color-text-primary);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
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
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent) 100%);
  color: var(--color-text-on-accent);
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
  background: var(--color-bg-card);
}
</style>
