import { ref } from 'vue'

// 全局金额隐藏状态（眼睛图标），跨页面共享并持久化到 localStorage
const STORAGE_KEY = 'asset_amount_hidden'
const MASK = '****'

const loadHidden = () => {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch (error) {
    return false
  }
}

// 单例响应式状态：所有调用方共享同一个 ref
const isAmountHidden = ref(loadHidden())

const persist = () => {
  try {
    localStorage.setItem(STORAGE_KEY, String(isAmountHidden.value))
  } catch (error) {
    /* ignore storage errors */
  }
}

const toggleAmountHidden = () => {
  isAmountHidden.value = !isAmountHidden.value
  persist()
}

const setAmountHidden = (value) => {
  isAmountHidden.value = !!value
  persist()
}

// 金额脱敏：隐藏时返回 ****，否则返回原值
const maskAmount = (value, mask = MASK) => {
  return isAmountHidden.value ? mask : value
}

export function useAmountPrivacy() {
  return {
    isAmountHidden,
    toggleAmountHidden,
    setAmountHidden,
    maskAmount
  }
}
