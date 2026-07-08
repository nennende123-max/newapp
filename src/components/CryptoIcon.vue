<template>
  <span
    class="crypto-icon"
    :class="[`crypto-icon--${variant}`, customClass]"
    :style="iconStyle"
    aria-hidden="true"
  >
    {{ initial }}
  </span>
</template>

<script setup>
import { computed } from 'vue';

const TOKEN_ICON_COLORS = {
  USDT: { bg: '#26A17B', text: '#FFFFFF' },
  BTC: { bg: '#F7931A', text: '#FFFFFF' },
  ETH: { bg: '#627EEA', text: '#FFFFFF' },
  BNB: { bg: '#F3BA2F', text: '#111827' },
  SOL: { bg: '#7C3AED', text: '#FFFFFF' },
  BEAT: { bg: '#FF5C67', text: '#FFFFFF' },
  NEW: { bg: '#14B8A6', text: '#FFFFFF' },
  AIC: { bg: '#3B82F6', text: '#FFFFFF' },
  MEME: { bg: '#F97316', text: '#FFFFFF' },
  ZRO: { bg: '#8B5CF6', text: '#FFFFFF' },
  DFV: { bg: '#64748B', text: '#FFFFFF' },
  GFX: { bg: '#22C55E', text: '#FFFFFF' },
  DOGE: { bg: '#C2A633', text: '#111827' },
  TRX: { bg: '#EF4444', text: '#FFFFFF' },
  XRP: { bg: '#334155', text: '#FFFFFF' },
  ADA: { bg: '#2563EB', text: '#FFFFFF' },
  AVAX: { bg: '#E84142', text: '#FFFFFF' },
  MATIC: { bg: '#8247E5', text: '#FFFFFF' },
  DOT: { bg: '#E6007A', text: '#FFFFFF' },
  LINK: { bg: '#2A5ADA', text: '#FFFFFF' },
  UNI: { bg: '#FF007A', text: '#FFFFFF' },
  ATOM: { bg: '#2E3148', text: '#FFFFFF' },
  LTC: { bg: '#345D9D', text: '#FFFFFF' },
  BCH: { bg: '#8DC351', text: '#111827' },
  XLM: { bg: '#475569', text: '#FFFFFF' },
  ALGO: { bg: '#111827', text: '#FFFFFF' },
  VET: { bg: '#15BDFF', text: '#FFFFFF' },
  FIL: { bg: '#0090FF', text: '#FFFFFF' },
  ICP: { bg: '#F97316', text: '#FFFFFF' },
  THETA: { bg: '#2AB8E6', text: '#FFFFFF' },
  EOS: { bg: '#111827', text: '#FFFFFF' },
  AAVE: { bg: '#B6509E', text: '#FFFFFF' },
  SFP: { bg: '#2563EB', text: '#FFFFFF' },
};

const props = defineProps({
  symbol: {
    type: String,
    default: '',
  },
  size: {
    type: Number,
    default: 44,
  },
  variant: {
    type: String,
    default: 'default',
  },
  customClass: {
    type: [String, Array, Object],
    default: '',
  },
});

const normalizedSymbol = computed(() => String(props.symbol || '').trim().toUpperCase());
const tokenColor = computed(() => TOKEN_ICON_COLORS[normalizedSymbol.value] || { bg: '#64748B', text: '#FFFFFF' });
const initial = computed(() => normalizedSymbol.value.charAt(0) || '?');

const iconStyle = computed(() => {
  const size = Number(props.size) || 44;
  return {
    '--crypto-icon-size': `${size}px`,
    '--crypto-icon-font-size': `${size <= 40 ? 15 : 16}px`,
    '--crypto-icon-bg': tokenColor.value.bg,
    '--crypto-icon-text': tokenColor.value.text,
  };
});
</script>

<style scoped>
.crypto-icon {
  display: inline-flex;
  width: var(--crypto-icon-size);
  height: var(--crypto-icon-size);
  flex: 0 0 var(--crypto-icon-size);
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--crypto-icon-bg);
  color: var(--crypto-icon-text);
  font-size: var(--crypto-icon-font-size);
  font-weight: 700;
  line-height: 1;
  text-align: center;
  font-variant-numeric: tabular-nums;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
  user-select: none;
}

.crypto-icon--compact {
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
}
</style>
