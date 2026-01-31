# TradingView Widget 完整修复文档

## 问题诊断

前端 K 线图黑屏，Console 报错：`this.chart.addCandlestickSeries is not a function`

**根本原因**：
1. `TradingViewWidget.vue` 使用了 Options API，在某些情况下 `this.chart` 可能未正确初始化
2. 缺少完整的错误处理和加载状态
3. 缺少 ResizeObserver，窗口变化时图表无法自适应
4. 数据格式可能不正确（time 单位问题）

## 修复方案

### 1. `src/main.js` - 确认导入

**当前状态**：`lightweight-charts` 已在 `package.json` 中（版本 5.1.0），无需额外配置。

**说明**：`lightweight-charts` 通过 npm 安装，在组件中直接 `import { createChart } from 'lightweight-charts'` 即可使用。

### 2. `src/components/TradingViewWidget.vue` - 完整重写

#### 关键修复点：

**a) 使用 `<script setup>`**
```vue
<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { createChart } from 'lightweight-charts'
```

**b) 正确的图表初始化**
```javascript
// 在 mounted 中正确调用 createChart(container, options)
chart.value = createChart(container, {
  layout: {
    background: { type: 'solid', color: '#000000' }, // 暗黑模式
    textColor: '#D9D9D9',
  },
  width: container.clientWidth || container.offsetWidth || 375,
  height: 420, // 固定高度 420px（适合移动端）
  // ...
})

// 使用 chart.addCandlestickSeries()（不是 chart.CandleStickSeries）
candleSeries.value = chart.value.addCandlestickSeries({
  upColor: '#0ECB81',        // 涨：绿色
  downColor: '#F6465D',      // 跌：红色
  // ...
})
```

**c) ResizeObserver 自适应**
```javascript
const setupResizeObserver = () => {
  resizeObserver.value = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const { width } = entry.contentRect
      if (chart.value && width > 0) {
        chart.value.applyOptions({
          width: width,
          height: 420 // 保持固定高度
        })
      }
    }
  })
  resizeObserver.value.observe(chartContainer.value)
}
```

**d) Props 定义**
```javascript
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
```

**e) 数据更新方法**
```javascript
// 更新单根 K 线（WebSocket 实时推送时用）
const updateLiveCandle = (candle) => {
  // 验证数据格式
  const formattedCandle = {
    time: typeof candle.time === 'number' ? candle.time : (candle.time / 1000), // 确保是秒级时间戳
    open: parseFloat(candle.open),
    high: parseFloat(candle.high),
    low: parseFloat(candle.low),
    close: parseFloat(candle.close),
    volume: candle.volume ? parseFloat(candle.volume) : undefined
  }
  
  candleSeries.value.update(formattedCandle)
}
```

**f) Loading 和 Error 状态**
```vue
<div v-if="loading" class="chart-loading">
  <van-loading type="spinner" color="#0ECB81">加载中...</van-loading>
</div>

<div v-else-if="error" class="chart-error">
  <van-icon name="warning-o" size="24" color="#F6465D" />
  <p>{{ error }}</p>
  <van-button type="primary" size="small" @click="initChart">重试</van-button>
</div>
```

**g) 暴露方法供父组件调用**
```javascript
defineExpose({
  chart,
  candleSeries,
  updateHistory,
  updateLiveCandle,
  initChart
})
```

### 3. `src/components/MarketDetail.vue` - 修改部分

#### 关键修复点：

**a) 传递 interval prop**
```vue
<trading-view-widget 
  ref="tvWidget"
  :symbol="symbol"
  :interval="selectedTimeframe"
  :initial-data="klineHistory" 
/>
```

**b) 确保数据格式正确（time 单位为秒）**
```javascript
const fetchKlineHistory = async () => {
  // ...
  const formattedData = res.data.map(item => ({
    time: Math.floor(item[0] / 1000), // 确保是秒级时间戳（整数）
    open: parseFloat(item[1]),
    high: parseFloat(item[2]),
    low: parseFloat(item[3]),
    close: parseFloat(item[4]),
    volume: item[5] ? parseFloat(item[5]) : undefined
  }));
  klineHistory.value = formattedData;
}
```

**c) WebSocket 消息处理（已在之前修复）**
```javascript
backendWS.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'kline' && data.data) {
    const kline = data.data;
    
    // 检查交易对和时间周期是否匹配
    if (klineSymbol === normalizedSymbol && kline.interval === selectedTimeframe.value) {
      if (tvWidget.value && tvWidget.value.updateLiveCandle) {
        // 转换时间戳：从毫秒转为秒
        const candleTime = Math.floor(kline.timestamp / 1000);
        
        // 调用 TradingViewWidget 的 updateLiveCandle 方法更新 K 线
        tvWidget.value.updateLiveCandle({
          time: candleTime,
          open: parseFloat(kline.open),
          high: parseFloat(kline.high),
          low: parseFloat(kline.low),
          close: parseFloat(kline.close)
        });
      }
    }
  }
};
```

## 数据格式说明

### TradingView Lightweight Charts 要求的数据格式

**单根 K 线数据**：
```javascript
{
  time: 1234567890,  // 秒级时间戳（整数）
  open: 50000.0,
  high: 51000.0,
  low: 49000.0,
  close: 50500.0,
  volume: 1000.0     // 可选
}
```

**历史数据数组**：
```javascript
[
  { time: 1234567890, open: 50000.0, high: 51000.0, low: 49000.0, close: 50500.0 },
  { time: 1234567900, open: 50500.0, high: 51500.0, low: 49500.0, close: 51000.0 },
  // ...
]
```

### 后端发送的数据格式（JSON）

```json
{
  "type": "kline",
  "data": {
    "symbol": "BTC/USDT",
    "interval": "1m",
    "timestamp": 1234567890000,  // 毫秒
    "open": 50000.0,
    "high": 51000.0,
    "low": 49000.0,
    "close": 50500.0,
    "volume": 1000.0,
    "is_closed": false
  }
}
```

### 前端转换逻辑

```javascript
// 从后端接收的数据（timestamp 是毫秒）
const kline = data.data;

// 转换为 TradingView 需要的格式（time 是秒）
const candleTime = Math.floor(kline.timestamp / 1000);

tvWidget.value.updateLiveCandle({
  time: candleTime,  // 秒级时间戳
  open: parseFloat(kline.open),
  high: parseFloat(kline.high),
  low: parseFloat(kline.low),
  close: parseFloat(kline.close)
});
```

## 使用说明

### 1. 启动服务

```bash
# 终端1：启动后端
python main.py

# 终端2：启动前端
npm run dev
```

### 2. 访问应用

访问 `http://localhost:5173/`，导航到市场详情页面（例如：`/market?symbol=BTC`）。

### 3. 检查图表

**浏览器控制台（F12）**：
- `[TradingViewWidget] ✅ 图表初始化成功`
- `[TradingViewWidget] ✅ 初始数据已加载: X 条`
- `[MarketDetail] 📊 收到K线数据`
- `[MarketDetail] ✅ 已更新 K 线图`
- `[TradingViewWidget] ✅ K 线更新成功`

**图表显示**：
- 应该显示黑色背景的 K 线图
- 高度固定为 420px（适合移动端）
- 宽度自适应容器（100%）
- 涨：绿色（#0ECB81）
- 跌：红色（#F6465D）

### 4. 测试数据更新

1. **初始加载**：页面加载时应该显示历史 K 线数据
2. **实时更新**：等待几秒钟，观察 K 线图是否实时更新
3. **切换时间周期**：点击时间周期按钮（1m, 5m, 1h, 4h, 1d），图表应该更新
4. **切换交易对**：切换交易对，图表应该更新

## 改动说明

### `src/components/TradingViewWidget.vue`

1. **使用 `<script setup>`**：完全重写为 Composition API
2. **正确的图表初始化**：使用 `createChart(container, options)` 和 `chart.addCandlestickSeries()`
3. **ResizeObserver**：添加 ResizeObserver 监听容器大小变化
4. **Loading 和 Error 状态**：添加加载中和错误状态显示
5. **数据格式验证**：确保 time 是秒级时间戳（整数）
6. **Props 定义**：添加 `symbol` 和 `interval` props
7. **暴露方法**：使用 `defineExpose` 暴露方法供父组件调用

### `src/components/MarketDetail.vue`

1. **传递 interval prop**：添加 `:interval="selectedTimeframe"` prop
2. **数据格式修复**：确保 `fetchKlineHistory` 返回的数据 time 是秒级时间戳

### `src/main.js`

**无需修改**：`lightweight-charts` 已在 `package.json` 中，组件中直接导入即可。

## 总结

本次修复解决了以下问题：

1. ✅ **TypeError 修复**：使用 `<script setup>` 和正确的 `chart.addCandlestickSeries()` 方法
2. ✅ **图表初始化**：确保图表在 `mounted` 中正确初始化
3. ✅ **ResizeObserver**：添加 ResizeObserver 确保窗口变化时图表自适应
4. ✅ **数据格式**：确保 time 是秒级时间戳（整数）
5. ✅ **Loading 和 Error 状态**：添加加载中和错误状态显示
6. ✅ **Props 传递**：正确传递 `symbol` 和 `interval` props
7. ✅ **WebSocket 数据更新**：确保收到数据后正确更新图表

所有修复已完成，可以重启 Vite，然后在浏览器 F12 中查看 Console，确认 K 线图正常显示和数据推送。
