<template>
  <div class="chart-wrapper">
    <!-- Loading 状态 -->
    <div v-if="loading" class="chart-loading">
      <van-loading type="spinner" color="#0ECB81">加载中...</van-loading>
    </div>
    
    <!-- Error 状态 -->
    <div v-else-if="error" class="chart-error">
      <van-icon name="warning-o" size="24" color="#F6465D" />
      <p>{{ error }}</p>
      <van-button type="primary" size="small" @click="initChart">重试</van-button>
    </div>
    
    <!-- 图表容器 -->
    <div 
      v-else
      ref="chartContainer" 
      class="chart-container"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
// ========== 关键修复：正确导入 createChart（addCandlestickSeries 是 chart 实例的方法，不需要单独导入）==========
import { createChart } from 'lightweight-charts'
import { Loading as VanLoading, Icon as VanIcon, Button as VanButton } from 'vant'

// Props
const props = defineProps({
  // 初始历史数据 (数组: [{time, open, high, low, close, volume?}, ...])
  initialData: {
    type: Array,
    default: () => []
  },
  // 当前显示的交易对名称
  symbol: {
    type: String,
    default: 'BTC/USDT'
  },
  // 时间周期（如 1m, 5m, 1h, 1d）
  interval: {
    type: String,
    default: '1h'
  }
})

// Emits
const emit = defineEmits(['chart-ready', 'chart-error'])

// Refs
const chartContainer = ref(null)
const chart = ref(null)
const candleSeries = ref(null)
const loading = ref(true)
const error = ref(null)
const resizeObserver = ref(null)

// ========== 初始化图表 ==========
const initChart = async () => {
  try {
    loading.value = true
    error.value = null

    // 等待 DOM 渲染完成
    await nextTick()

    const container = chartContainer.value
    if (!container) {
      console.warn('[TradingViewWidget] ⚠️ 图表容器未找到，等待 DOM 渲染...')
      // 如果容器不存在，等待一段时间后重试
      setTimeout(() => {
        if (chartContainer.value) {
          initChart()
        } else {
          error.value = '图表容器未找到，请刷新页面重试'
          loading.value = false
        }
      }, 100)
      return
    }

    // 检查 createChart 是否可用
    if (typeof createChart !== 'function') {
      throw new Error('createChart 不是函数，请检查 lightweight-charts 导入')
    }

    // 如果图表已存在，先销毁
    if (chart.value) {
      chart.value.remove()
      chart.value = null
      candleSeries.value = null
    }

    // ========== 关键修复：创建图表实例 ==========
    // 宽度 100%（自适应容器），高度 420px（适合移动端）
    // 获取容器实际宽度
    const containerWidth = container.clientWidth || container.offsetWidth || window.innerWidth || 375
    const containerHeight = 420 // 固定高度 420px（适合移动端）
    
    chart.value = createChart(container, {
      layout: {
        background: { type: 'solid', color: '#000000' }, // 暗黑模式背景
        textColor: '#D9D9D9', // 文字颜色
      },
      grid: {
        vertLines: { color: '#2B2B43' },
        horzLines: { color: '#2B2B43' },
      },
      width: containerWidth,
      height: containerHeight,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: '#2B2B43',
      },
      rightPriceScale: {
        borderColor: '#2B2B43',
      },
    })
    
    console.log('[TradingViewWidget] 图表容器大小:', {
      width: containerWidth,
      height: containerHeight,
      containerClientWidth: container.clientWidth,
      containerOffsetWidth: container.offsetWidth
    })

    if (!chart.value) {
      throw new Error('图表实例创建失败')
    }

    // ========== 关键修复：使用 chart.addCandlestickSeries()（不是 chart.CandleStickSeries）==========
    if (typeof chart.value.addCandlestickSeries !== 'function') {
      throw new Error('chart.addCandlestickSeries 不是函数')
    }

    // 创建 K 线系列（暗黑模式，价格线绿色/红色）
    candleSeries.value = chart.value.addCandlestickSeries({
      upColor: '#0ECB81',        // 涨：绿色
      downColor: '#F6465D',      // 跌：红色
      borderVisible: false,
      wickUpColor: '#0ECB81',
      wickDownColor: '#F6465D',
    })

    if (!candleSeries.value) {
      throw new Error('K 线系列创建失败')
    }

    console.log('[TradingViewWidget] ✅ 图表初始化成功')

    // 如果有初始数据，立即填充
    if (props.initialData && props.initialData.length > 0) {
      const formattedData = props.initialData.map(item => ({
        time: typeof item.time === 'number' ? item.time : (item.time / 1000), // 确保是秒级时间戳
        open: parseFloat(item.open),
        high: parseFloat(item.high),
        low: parseFloat(item.low),
        close: parseFloat(item.close),
        volume: item.volume ? parseFloat(item.volume) : undefined
      }))
      
      candleSeries.value.setData(formattedData)
      console.log('[TradingViewWidget] ✅ 初始数据已加载:', formattedData.length, '条')
    }

    // 设置 resize observer，确保窗口变化时图表自适应
    setupResizeObserver()

    loading.value = false
    emit('chart-ready', chart.value)
  } catch (err) {
    console.error('[TradingViewWidget] ❌ 初始化图表失败:', err)
    error.value = err.message || '图表初始化失败'
    loading.value = false
    emit('chart-error', err)
  }
}

// ========== 设置 Resize Observer ==========
const setupResizeObserver = () => {
  // 清理旧的 observer
  if (resizeObserver.value) {
    resizeObserver.value.disconnect()
    resizeObserver.value = null
  }

  if (!chartContainer.value || !chart.value) {
    return
  }

  // ========== 关键修复：使用 ResizeObserver 监听容器大小变化，确保图表自适应 ==========
  resizeObserver.value = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const { width } = entry.contentRect
      if (chart.value && width > 0) {
        // 宽度自适应容器，高度保持固定 420px
        chart.value.applyOptions({
          width: width,
          height: 420 // 保持固定高度 420px（适合移动端）
        })
        console.log('[TradingViewWidget] 图表大小已更新（ResizeObserver）:', { width, height: 420 })
      }
    }
  })

  resizeObserver.value.observe(chartContainer.value)
  
  // 注意：窗口 resize 监听器在 onMounted 中添加，避免重复
}

// ========== 窗口大小变化处理（自适应大小，避免黑屏）==========
const handleResize = () => {
  if (chart.value && chartContainer.value) {
    const width = chartContainer.value.clientWidth || chartContainer.value.offsetWidth
    if (width > 0) {
      // Lightweight Charts 使用 applyOptions 而不是 resize()
      chart.value.applyOptions({
        width: width,
        height: 420 // 保持固定高度 420px
      })
      console.log('[TradingViewWidget] 图表大小已自适应:', { width, height: 420 })
    }
  }
}

// ========== 更新整个历史数据（切换币种或初始化时用）==========
const updateHistory = (data) => {
  if (!candleSeries.value || !data || !Array.isArray(data)) {
    console.warn('[TradingViewWidget] ⚠️ 无法更新历史数据: candleSeries 未初始化或数据无效')
    return
  }

  try {
    const formattedData = data.map(item => ({
      time: typeof item.time === 'number' ? item.time : (item.time / 1000), // 确保是秒级时间戳
      open: parseFloat(item.open),
      high: parseFloat(item.high),
      low: parseFloat(item.low),
      close: parseFloat(item.close),
      volume: item.volume ? parseFloat(item.volume) : undefined
    }))

    candleSeries.value.setData(formattedData)
    console.log('[TradingViewWidget] ✅ 历史数据已更新:', formattedData.length, '条')
  } catch (err) {
    console.error('[TradingViewWidget] ❌ 更新历史数据失败:', err)
  }
}

// ========== 更新单根 K 线（WebSocket 实时推送时用）==========
const updateLiveCandle = (candle) => {
  if (!candleSeries.value) {
    console.warn('[TradingViewWidget] ⚠️ candleSeries 未初始化，跳过更新')
    return
  }

  try {
    // 验证数据格式（匹配格式，确保实时）
    if (!candle || typeof candle !== 'object') {
      console.error('[TradingViewWidget] ❌ 无效的 K 线数据:', candle)
      return
    }

    // 确保必要字段存在（验证格式）
    if (candle.time === undefined || candle.open === undefined || 
        candle.high === undefined || candle.low === undefined || 
        candle.close === undefined || candle.volume === undefined) {
      console.warn('[TradingViewWidget] ⚠️ 忽略无效数据（缺少必要字段）:', candle)
      return
    }

    // 格式化数据（确保 time 是秒级时间戳）
    const formattedCandle = {
      time: typeof candle.time === 'number' ? candle.time : (candle.time / 1000),
      open: parseFloat(candle.open),
      high: parseFloat(candle.high),
      low: parseFloat(candle.low),
      close: parseFloat(candle.close),
      volume: candle.volume ? parseFloat(candle.volume) : undefined
    }

    // 更新 K 线（相当于 widget.updateBar(data)）
    candleSeries.value.update(formattedCandle)
    console.log('[TradingViewWidget] ✅ K 线更新成功（实时）:', {
      time: formattedCandle.time,
      close: formattedCandle.close,
      volume: formattedCandle.volume
    })
  } catch (err) {
    console.error('[TradingViewWidget] ❌ 更新 K 线失败:', err)
    console.error('[TradingViewWidget] K 线数据:', candle)
  }
}

// ========== WebSocket 消息处理（如果组件需要独立连接）==========
const handleWebSocketMessage = (event) => {
  try {
    const data = JSON.parse(event.data)
    
    // 验证格式：确保包含所有必要字段
    if (data.time && data.open && data.high && data.low && data.close && data.volume) {
      console.log('[TradingViewWidget] 收到实时Binance K线:', data)
      updateLiveCandle(data)  // 更新图表
    } else {
      console.warn('[TradingViewWidget] 忽略无效数据:', data)
    }
  } catch (err) {
    console.error('[TradingViewWidget] ❌ WebSocket 消息解析失败:', err)
  }
}

// ========== 监听 props 变化 ==========
watch(() => props.initialData, (newData) => {
  if (newData && newData.length > 0 && candleSeries.value) {
    updateHistory(newData)
  }
}, { deep: true })

watch(() => props.symbol, () => {
  // 切换交易对时，可以重新初始化图表（可选）
  // 或者只更新数据
  console.log('[TradingViewWidget] 交易对已切换:', props.symbol)
})

watch(() => props.interval, () => {
  // 切换时间周期时，可以重新初始化图表（可选）
  console.log('[TradingViewWidget] 时间周期已切换:', props.interval)
})

// ========== WebSocket 连接（可选，如果组件需要独立连接）==========
let wsConnection = null

// ========== 初始化 WebSocket 连接（可选）==========
const initWebSocket = () => {
  // 如果已经有连接，先关闭
  if (wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
  
  // 连接后端 WebSocket（通过 Vite 代理）
  const wsUrl = `ws://${window.location.host}/ws`
  try {
    wsConnection = new WebSocket(wsUrl)
    
    wsConnection.onopen = () => {
      console.log('[TradingViewWidget] ✅ WebSocket 连接成功')
    }
    
    wsConnection.onmessage = handleWebSocketMessage
    
    wsConnection.onerror = (error) => {
      console.error('[TradingViewWidget] ❌ WebSocket 错误:', error)
    }
    
    wsConnection.onclose = () => {
      console.log('[TradingViewWidget] ⚠️ WebSocket 连接关闭')
      wsConnection = null
    }
  } catch (err) {
    console.error('[TradingViewWidget] ❌ WebSocket 连接失败:', err)
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  // ========== 关键修复：在 mounted 中调用 initChart（不是 this.chart.initChart）==========
  // initChart 是组件的方法，不是 chart 实例的方法
  // 确保图表在 DOM 渲染完成后初始化
  initChart()
  
  // 添加窗口 resize 监听器（自适应）
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  // 清理 resize observer
  if (resizeObserver.value) {
    resizeObserver.value.disconnect()
    resizeObserver.value = null
  }

  // 移除窗口大小监听（自适应）
  window.removeEventListener('resize', handleResize)
  
  // 关闭 WebSocket 连接（如果存在）
  if (wsConnection) {
    try {
      wsConnection.close()
      wsConnection = null
    } catch (err) {
      console.error('[TradingViewWidget] 关闭 WebSocket 连接失败:', err)
    }
  }

  // 销毁图表
  if (chart.value) {
    try {
      chart.value.remove()
    } catch (err) {
      console.error('[TradingViewWidget] 销毁图表失败:', err)
    }
    chart.value = null
    candleSeries.value = null
  }
})

// ========== 暴露方法供父组件调用 ==========
// ========== 关键修复：暴露的方法供父组件调用（不是 this.chart.initChart）==========
defineExpose({
  chart,              // 图表实例（可选，用于高级操作）
  candleSeries,       // K 线系列实例（可选）
  updateHistory,      // 更新历史数据方法
  updateLiveCandle,   // 更新单根 K 线方法
  initChart,          // 重新初始化图表方法（不是 this.chart.initChart）
  handleResize,       // 窗口大小变化处理方法（自适应）
  initWebSocket       // 初始化 WebSocket 连接方法（可选）
})
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 420px; /* 固定高度 420px（适合移动端）*/
  background-color: #000000;
  overflow: hidden;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #D9D9D9;
}

.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #F6465D;
  gap: 12px;
  padding: 20px;
  text-align: center;
}

.chart-error p {
  margin: 0;
  font-size: 14px;
}
</style>
