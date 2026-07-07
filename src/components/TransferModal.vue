<template>
  <van-popup
    :show="show"
    round
    position="bottom"
    :style="{ maxHeight: '80%' }"
    @update:show="(val) => emit('update:show', val)"
  >
    <div class="transfer-modal">
      <div class="tm-header">
        <span class="tm-title">划转</span>
        <van-icon name="cross" class="tm-close" @click="close" />
      </div>

      <div class="tm-body">
        <!-- 转出账户 -->
        <div class="tm-field">
          <span class="tm-label">转出账户</span>
          <div class="tm-options">
            <button
              v-for="acc in accounts"
              :key="'from-' + acc.key"
              type="button"
              class="tm-chip"
              :class="{ active: fromAccount === acc.key }"
              @click="fromAccount = acc.key"
            >{{ acc.label }}</button>
          </div>
        </div>

        <div class="tm-swap">
          <van-icon name="exchange" @click="swap" />
        </div>

        <!-- 转入账户 -->
        <div class="tm-field">
          <span class="tm-label">转入账户</span>
          <div class="tm-options">
            <button
              v-for="acc in accounts"
              :key="'to-' + acc.key"
              type="button"
              class="tm-chip"
              :class="{ active: toAccount === acc.key, disabled: acc.key === fromAccount }"
              :disabled="acc.key === fromAccount"
              @click="toAccount = acc.key"
            >{{ acc.label }}</button>
          </div>
        </div>

        <!-- 币种 -->
        <div class="tm-field">
          <span class="tm-label">币种</span>
          <div class="tm-options">
            <button
              v-for="coin in currencies"
              :key="coin"
              type="button"
              class="tm-chip"
              :class="{ active: currency === coin }"
              @click="currency = coin"
            >{{ coin }}</button>
          </div>
        </div>

        <!-- 数量 -->
        <div class="tm-field">
          <span class="tm-label">数量</span>
          <div class="tm-amount">
            <input
              v-model="amount"
              type="number"
              inputmode="decimal"
              class="tm-amount-input"
              placeholder="请输入划转数量"
            />
            <span class="tm-amount-unit">{{ currency }}</span>
          </div>
        </div>
      </div>

      <button type="button" class="tm-confirm" @click="confirm">确认划转</button>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import { transferAccounts, transferCurrencies } from '@/data/assetMock'

const props = defineProps({
  show: { type: Boolean, default: false },
  defaultFrom: { type: String, default: 'spot' }
})

const emit = defineEmits(['update:show'])

const accounts = transferAccounts
const currencies = transferCurrencies

const fromAccount = ref(props.defaultFrom || 'spot')
const toAccount = ref('futures')
const currency = ref('USDT')
const amount = ref('')

// 打开时根据默认转出账户初始化，并保证转入账户与转出账户不同
watch(
  () => props.show,
  (val) => {
    if (val) {
      fromAccount.value = props.defaultFrom || 'spot'
      toAccount.value = accounts.find((a) => a.key !== fromAccount.value)?.key || 'futures'
      currency.value = 'USDT'
      amount.value = ''
    }
  }
)

// 转出账户变化时，避免转入与转出相同
watch(fromAccount, (val) => {
  if (toAccount.value === val) {
    toAccount.value = accounts.find((a) => a.key !== val)?.key || val
  }
})

const swap = () => {
  const temp = fromAccount.value
  fromAccount.value = toAccount.value
  toAccount.value = temp
}

const close = () => emit('update:show', false)

const confirm = () => {
  const num = Number(amount.value)
  if (!num || num <= 0) {
    showToast('请输入有效的划转数量')
    return
  }
  // 仅做前端 mock，不提交真实接口
  showToast({ message: '划转成功', icon: 'success' })
  close()
}
</script>

<style scoped>
.transfer-modal {
  padding: 20px 16px calc(20px + env(safe-area-inset-bottom));
  background: #ffffff;
}

.tm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tm-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.tm-close {
  font-size: 20px;
  color: #94a3b8;
}

.tm-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tm-field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tm-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.tm-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tm-chip {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid #e6ebf2;
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tm-chip.active {
  background: #fff7e0;
  border-color: #f0b90b;
  color: #b7791f;
}

.tm-chip.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tm-swap {
  display: flex;
  justify-content: center;
  color: #f0b90b;
  font-size: 20px;
}

.tm-amount {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 14px;
  border: 1px solid #e6ebf2;
  border-radius: 12px;
  background: #f8fafc;
}

.tm-amount-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.tm-amount-unit {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
}

.tm-confirm {
  width: 100%;
  height: 50px;
  margin-top: 22px;
  border: none;
  border-radius: 12px;
  background: #fcd535;
  color: #111827;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.tm-confirm:active {
  opacity: 0.85;
}
</style>
