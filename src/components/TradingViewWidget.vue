<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-state">
      <van-loading type="spinner" color="var(--color-primary)">加载图表...</van-loading>
    </div>

    <div v-show="!loading && !error" ref="chartContainer" class="chart-container"></div>

    <div v-if="error" class="chart-state chart-error">
      <van-icon name="warning-o" size="28" />
      <p>{{ error }}</p>
      <van-button class="btn-cta retry-btn" size="small" @click="initChart">重试</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { createChart, CandlestickSeries } from 'lightweight-charts'
import { Loading as VanLoading, Icon as VanIcon, Button as VanButton } from 'vant'
import { getThemeColor } from '@/styles/theme'

const props = defineProps({
  initialData: {
    type: Array,
    default: () => []
  },
  symbol: {
    type: String,
    default: 'BTC/USDT'
  },
  interval: {
    type: String,
    default: '1h'
  }
})

const emit = defineEmits(['chart-ready', 'chart-error'])

const chartContainer = ref(null)
const chart = ref(null)
const candleSeries = ref(null)
const loading = ref(true)
const error = ref(null)
const resizeObserver = ref(null)
const themeObserver = ref(null)

const CHART_HEIGHT = 420

const normalizeTime = (time) => {
  if (typeof time !== 'number') return Math.floor(new Date(time).getTime() / 1000)
  return time > 10000000000 ? Math.floor(time / 1000) : time
}

const normalizeCandle = (item) => ({
  time: normalizeTime(item.time),
  open: Number(item.open),
  high: Number(item.high),
  low: Number(item.low),
  close: Number(item.close)
})

const validCandle = (item) => {
  if (!item || typeof item !== 'object') return false
  return ['time', 'open', 'high', 'low', 'close'].every((key) => item[key] !== undefined && item[key] !== null)
}

const fallbackData = () => {
  const now = Math.floor(Date.now() / 1000)
  const start = now - 60 * 60 * 80
  let price = props.symbol.toUpperCase().includes('ETH') ? 3100 : 92000

  return Array.from({ length: 80 }, (_, index) => {
    const open = price
    const wave = Math.sin(index / 4) * price * 0.002
    const drift = (Math.random() - 0.45) * price * 0.0016
    const close = Math.max(1, open + wave + drift)
    const high = Math.max(open, close) + price * (0.001 + Math.random() * 0.0015)
    const low = Math.min(open, close) - price * (0.001 + Math.random() * 0.0015)
    price = close

    return {
      time: start + index * 3600,
      open,
      high,
      low,
      close
    }
  })
}

const getChartWidth = () => {
  const container = chartContainer.value
  return Math.max(320, container?.clientWidth || container?.offsetWidth || window.innerWidth || 375)
}

const buildChart = () => {
  const container = chartContainer.value
  if (!container) {
    throw new Error('图表容器未就绪，请稍后重试')
  }

  if (chart.value) {
    chart.value.remove()
    chart.value = null
    candleSeries.value = null
  }

  chart.value = createChart(container, {
    width: getChartWidth(),
    height: CHART_HEIGHT,
    autoSize: false,
    layout: {
      background: { color: getThemeColor('--color-surface-2') },
      textColor: getThemeColor('--color-text-secondary'),
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    },
    grid: {
      vertLines: { color: getThemeColor('--color-border-subtle') },
      horzLines: { color: getThemeColor('--color-border-subtle') }
    },
    crosshair: {
      mode: 1
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
      borderColor: getThemeColor('--color-border'),
      rightOffset: 8,
      barSpacing: 9
    },
    rightPriceScale: {
      borderColor: getThemeColor('--color-border'),
      scaleMargins: {
        top: 0.12,
        bottom: 0.16
      }
    }
  })

  candleSeries.value = chart.value.addSeries(CandlestickSeries, {
    upColor: getThemeColor('--color-success'),
    downColor: getThemeColor('--color-danger'),
    borderVisible: false,
    wickUpColor: getThemeColor('--color-success'),
    wickDownColor: getThemeColor('--color-danger'),
    priceLineColor: getThemeColor('--color-primary'),
    lastValueVisible: true
  })
}

const applyChartTheme = () => {
  if (!chart.value) return

  chart.value.applyOptions({
    layout: {
      background: { color: getThemeColor('--color-surface-2') },
      textColor: getThemeColor('--color-text-secondary'),
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    },
    grid: {
      vertLines: { color: getThemeColor('--color-border-subtle') },
      horzLines: { color: getThemeColor('--color-border-subtle') }
    },
    timeScale: {
      borderColor: getThemeColor('--color-border')
    },
    rightPriceScale: {
      borderColor: getThemeColor('--color-border')
    }
  })

  candleSeries.value?.applyOptions({
    upColor: getThemeColor('--color-success'),
    downColor: getThemeColor('--color-danger'),
    wickUpColor: getThemeColor('--color-success'),
    wickDownColor: getThemeColor('--color-danger'),
    priceLineColor: getThemeColor('--color-primary')
  })
}

const setChartData = (data = props.initialData) => {
  if (!candleSeries.value) return

  const source = Array.isArray(data) && data.length > 0 ? data : fallbackData()
  const formattedData = source
    .filter(validCandle)
    .map(normalizeCandle)
    .filter((item) => Number.isFinite(item.open) && Number.isFinite(item.high) && Number.isFinite(item.low) && Number.isFinite(item.close))
    .sort((a, b) => a.time - b.time)

  if (formattedData.length === 0) {
    candleSeries.value.setData(fallbackData())
  } else {
    candleSeries.value.setData(formattedData)
  }

  chart.value?.timeScale().fitContent()
}

const setupResizeObserver = () => {
  if (resizeObserver.value) {
    resizeObserver.value.disconnect()
    resizeObserver.value = null
  }

  if (!chartContainer.value || !chart.value) return

  resizeObserver.value = new ResizeObserver(() => {
    handleResize()
  })
  resizeObserver.value.observe(chartContainer.value)
}

const setupThemeObserver = () => {
  if (themeObserver.value) {
    themeObserver.value.disconnect()
    themeObserver.value = null
  }

  themeObserver.value = new MutationObserver(() => {
    applyChartTheme()
  })
  themeObserver.value.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme', 'style']
  })
}

const initChart = async () => {
  try {
    loading.value = true
    error.value = null
    await nextTick()
    await new Promise((resolve) => requestAnimationFrame(resolve))

    buildChart()
    setChartData()
    setupResizeObserver()
    setupThemeObserver()

    loading.value = false
    emit('chart-ready', chart.value)
  } catch (err) {
    loading.value = false
    error.value = err?.message || '图表初始化失败，请重试'
    emit('chart-error', err)
  }
}

const updateHistory = (data) => {
  if (!candleSeries.value) return
  setChartData(data)
}

const updateLiveCandle = (candle) => {
  if (!candleSeries.value || !validCandle(candle)) return
  candleSeries.value.update(normalizeCandle(candle))
}

const handleResize = () => {
  if (!chart.value || !chartContainer.value) return
  chart.value.applyOptions({
    width: getChartWidth(),
    height: CHART_HEIGHT
  })
}

const initWebSocket = () => {}

watch(() => props.initialData, (newData) => {
  if (candleSeries.value) updateHistory(newData)
}, { deep: true })

watch(() => [props.symbol, props.interval], () => {
  if (candleSeries.value && (!props.initialData || props.initialData.length === 0)) {
    setChartData()
  }
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  resizeObserver.value?.disconnect()
  resizeObserver.value = null
  themeObserver.value?.disconnect()
  themeObserver.value = null
  window.removeEventListener('resize', handleResize)

  if (chart.value) {
    chart.value.remove()
    chart.value = null
    candleSeries.value = null
  }
})

defineExpose({
  chart,
  candleSeries,
  updateHistory,
  updateLiveCandle,
  initChart,
  handleResize,
  initWebSocket
})
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 420px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: var(--color-surface-2);
  color: var(--color-text-secondary);
  text-align: center;
  z-index: 2;
}

.chart-error {
  color: var(--color-danger);
}

.chart-error p {
  margin: 0;
  font-size: 14px;
  color: var(--color-danger);
}

.retry-btn {
  min-width: 72px;
  border-radius: 8px;
}
</style>
