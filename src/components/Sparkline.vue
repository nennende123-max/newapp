<template>
  <svg class="sparkline" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" :stop-color="color" stop-opacity="0.28" />
        <stop offset="100%" :stop-color="color" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path :d="areaPath" :fill="`url(#${gradId})`" />
    <path :d="linePath" fill="none" :stroke="color" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  color: { type: String, default: '#00B976' },
  width: { type: Number, default: 320 },
  height: { type: Number, default: 96 }
})

const gradId = `spark-${Math.random().toString(36).slice(2, 9)}`

const points = computed(() => {
  const values = props.data && props.data.length ? props.data : [0, 0]
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const stepX = props.width / (values.length - 1 || 1)
  const pad = 8
  return values.map((v, i) => {
    const x = i * stepX
    const y = pad + (props.height - pad * 2) * (1 - (v - min) / range)
    return [x, y]
  })
})

const linePath = computed(() => {
  return points.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ')
})

const areaPath = computed(() => {
  if (!points.value.length) return ''
  const line = points.value.map((p) => `L${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ')
  const first = points.value[0]
  const last = points.value[points.value.length - 1]
  return `M${first[0].toFixed(1)} ${props.height} ${line} L${last[0].toFixed(1)} ${props.height} Z`
})
</script>

<style scoped>
.sparkline {
  width: 100%;
  height: 96px;
  display: block;
}
</style>
