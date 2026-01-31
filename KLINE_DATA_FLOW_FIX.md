# K 线数据流完整修复文档

## 问题诊断

前端 K 线图黑屏的原因：

1. **后端订阅流确认**：已确认订阅的是 `@kline` K 线流（不是 `@depth` 盘口数据）
2. **数据格式问题**：推送的数据格式需要优化，确保符合前端 TradingViewWidget 要求
3. **前端数据处理**：需要确保正确接收和转换数据格式

## 修复方案

### 1. `app/services/market_service.py` - 后端优化

#### 关键修复点：

**a) 确认订阅 @kline K 线流（不是 @depth）**
```python
# ========== 关键修复：构建 WebSocket URL，订阅 K 线流（不是 @depth 盘口数据）==========
streams = []
for symbol in SYMBOLS:
    for interval in WS_INTERVALS:
        # ========== 关键修复：订阅 @kline K 线流（不是 @depth 盘口数据）==========
        # 币安 WebSocket 流格式：btcusdt@kline_1m
        stream_name = f"{symbol.lower()}@kline_{interval}"
        streams.append(stream_name)
        logger.debug(f"[DEBUG] 订阅 K 线流: {stream_name}")

# URL 格式：wss://stream.binance.com:443/ws?streams=btcusdt@kline_1m/btcusdt@kline_1h/...
streams_path = '/'.join(streams)
primary_url = f"wss://stream.binance.com:443/ws?streams={streams_path}"
```

**b) 解析 K 线数据（time, open, high, low, close, volume）**
```python
async def _process_kline(self, kline_data):
    """
    处理真实的 K 线数据（核心逻辑）
    
    解析币安 WebSocket 返回的 K 线数据：
    {
        's': 'BTCUSDT',  # symbol
        'i': '1m',       # interval
        't': 1234567890, # timestamp (ms)
        'o': '50000.0',  # open
        'h': '51000.0',  # high
        'l': '49000.0',  # low
        'c': '50500.0',  # close
        'v': '1000.0',   # volume
        'x': True        # is_closed
    }
    """
    # 构建 K 线数据字典
    kline = {
        'symbol': symbol,
        'interval': interval,
        'timestamp': int(kline_data.get('t', 0)),  # 时间戳（毫秒）
        'open': float(kline_data.get('o', 0)),
        'high': float(kline_data.get('h', 0)),
        'low': float(kline_data.get('l', 0)),
        'close': float(kline_data.get('c', 0)),
        'volume': float(kline_data.get('v', 0)),
        'is_closed': is_closed
    }
    
    # 如果 K 线收盘，保存到数据库
    if is_closed:
        await KlineModel.upsert_klines([kline])
    
    # 广播给所有连接的客户端
    await self._broadcast_kline(kline)
```

**c) 推送 JSON 格式给前端（{time: unix_ms, open: float, high: float, low: float, close: float, volume: float}）**
```python
async def _broadcast_kline(self, kline: Dict[str, Any]):
    """
    广播 K 线数据给所有连接的客户端（前端 /ws 客户端）
    
    推送格式：{type: 'kline', data: {time: unix_ms, open: float, high: float, low: float, close: float, volume: float}}
    """
    # ========== 关键修复：推送格式符合前端要求 ==========
    # 前端 TradingViewWidget 需要的数据格式：{time: unix_ms, open: float, high: float, low: float, close: float, volume: float}
    # 注意：这里 time 保持为毫秒，前端会转换为秒级时间戳
    message = {
        'type': 'kline',
        'data': {
            'symbol': kline.get('symbol'),
            'interval': kline.get('interval'),
            'time': kline.get('timestamp'),  # 毫秒级时间戳（unix_ms）
            'open': float(kline.get('open', 0)),
            'high': float(kline.get('high', 0)),
            'low': float(kline.get('low', 0)),
            'close': float(kline.get('close', 0)),
            'volume': float(kline.get('volume', 0)),
            'is_closed': kline.get('is_closed', False)
        }
    }
    
    # 发送给所有活跃连接
    for ws in _active_connections:
        await ws.send_json(message)
```

**d) Session 管理（已在之前修复）**
```python
while self.is_running:
    connector = None
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.ws_connect(**ws_kwargs) as ws:
                # WebSocket 消息处理...
```

**e) 无限重连（每 5 秒重试）**
```python
_reconnect_delay = 5  # 重连延迟（秒）
_max_reconnect_attempts = 0  # 0 表示无限重试

if self.is_running:
    logger.info(f"[WS] 等待 {_reconnect_delay} 秒后重连...")
    await asyncio.sleep(_reconnect_delay)
```

### 2. `src/components/TradingViewWidget.vue` - 前端修复

#### 关键修复点：

**a) 确认 addCandlestickSeries() 调用正确**
```javascript
// ========== 关键修复：正确导入 createChart（addCandlestickSeries 是 chart 实例的方法，不需要单独导入）==========
import { createChart } from 'lightweight-charts'

// 创建图表实例
chart.value = createChart(container, {
  width: container.clientWidth || container.offsetWidth || 375,
  height: 420, // 固定高度 420px（适合移动端）
  // ...
})

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
```

**b) 设置图表大小（width: '100%', height: '420px'）**
```javascript
chart.value = createChart(container, {
  width: container.clientWidth || container.offsetWidth || 375,
  height: 420, // 固定高度 420px（适合移动端）
  // ...
})

// ResizeObserver 确保窗口变化时图表自适应
resizeObserver.value = new ResizeObserver((entries) => {
  for (const entry of entries) {
    const { width } = entry.contentRect
    if (chart.value && width > 0) {
      chart.value.applyOptions({
        width: width,
        height: 420 // 保持固定高度 420px
      })
    }
  }
})
```

**c) 添加 onmessage 处理推送 K 线数据（series.update(bar) 或 setData(bars)）**
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
  
  // 更新 K 线（相当于 series.update(bar)）
  candleSeries.value.update(formattedCandle)
}

// 更新整个历史数据（切换币种或初始化时用）
const updateHistory = (data) => {
  const formattedData = data.map(item => ({
    time: typeof item.time === 'number' ? item.time : (item.time / 1000),
    open: parseFloat(item.open),
    high: parseFloat(item.high),
    low: parseFloat(item.low),
    close: parseFloat(item.close),
    volume: item.volume ? parseFloat(item.volume) : undefined
  }))
  
  // 设置数据（相当于 series.setData(bars)）
  candleSeries.value.setData(formattedData)
}
```

**d) 初始加载历史 K 线（从 API 或数据库 fetch）**
```javascript
// 在 mounted 中初始化图表
onMounted(() => {
  initChart()
})

// 监听 props.initialData 变化
watch(() => props.initialData, (newData) => {
  if (newData && newData.length > 0 && candleSeries.value) {
    updateHistory(newData)
  }
}, { deep: true })
```

**e) 添加主题/价格线（green/red）**
```javascript
candleSeries.value = chart.value.addCandlestickSeries({
  upColor: '#0ECB81',        // 涨：绿色
  downColor: '#F6465D',      // 跌：红色
  borderVisible: false,
  wickUpColor: '#0ECB81',
  wickDownColor: '#F6465D',
})
```

### 3. `src/components/MarketDetail.vue` - 前端 WebSocket 处理

#### 关键修复点：

**a) 确保传递 symbol/interval 到 TradingViewWidget**
```vue
<trading-view-widget 
  ref="tvWidget"
  :symbol="symbol"
  :interval="selectedTimeframe"
  :initial-data="klineHistory" 
/>
```

**b) 处理 ws onmessage 更新状态"已连接"并转发数据到图表**
```javascript
backendWS.onopen = () => {
  console.log('[MarketDetail] ✅ WebSocket 连接成功');
  // ========== 关键修复：更新状态为"已连接" ==========
  wsConnected.value = true;
  wsConnecting.value = false;
  wsReconnectAttempts = 0;
  console.log('[MarketDetail] 📡 WebSocket 状态: 已连接，等待接收 K 线数据...');
};

backendWS.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    
    // 处理连接成功消息
    if (data.type === 'connected') {
      wsConnected.value = true;
      wsConnecting.value = false;
      return;
    }
    
    // ========== 关键修复：处理 K 线数据并转发到图表 ==========
    if (data.type === 'kline' && data.data) {
      const kline = data.data;
      
      // 检查交易对和时间周期是否匹配
      const normalizedSymbol = normalizeSymbol(symbol.value);
      const klineSymbol = kline.symbol?.replace('/', '').replace('USDT', '').toUpperCase();
      
      if (klineSymbol === normalizedSymbol && kline.interval === selectedTimeframe.value) {
        if (tvWidget.value && tvWidget.value.updateLiveCandle) {
          // ========== 关键修复：转换时间戳和数据格式 ==========
          // 后端发送的 time 是毫秒级时间戳（unix_ms），TradingView 需要秒级时间戳
          const candleTime = Math.floor((kline.time || kline.timestamp) / 1000);
          
          // ========== 关键修复：调用 TradingViewWidget 的 updateLiveCandle 方法更新 K 线 ==========
          tvWidget.value.updateLiveCandle({
            time: candleTime,
            open: parseFloat(kline.open),
            high: parseFloat(kline.high),
            low: parseFloat(kline.low),
            close: parseFloat(kline.close),
            volume: kline.volume ? parseFloat(kline.volume) : undefined
          });
          
          console.log('[MarketDetail] ✅ 已更新 K 线图');
        }
      }
    }
  } catch (error) {
    console.error('[MarketDetail] ❌ 解析 WebSocket 消息失败:', error);
  }
};
```

## 数据格式说明

### 后端发送给前端（JSON 格式）

```json
{
  "type": "kline",
  "data": {
    "symbol": "BTC/USDT",
    "interval": "1m",
    "time": 1234567890000,  // 毫秒级时间戳（unix_ms）
    "open": 50000.0,
    "high": 51000.0,
    "low": 49000.0,
    "close": 50500.0,
    "volume": 1000.0,
    "is_closed": false
  }
}
```

### 前端更新 TradingViewWidget

```javascript
// 前端接收数据后转换格式
const candleTime = Math.floor(kline.time / 1000); // 毫秒转秒

tvWidget.value.updateLiveCandle({
  time: candleTime,  // 秒级时间戳
  open: parseFloat(kline.open),
  high: parseFloat(kline.high),
  low: parseFloat(kline.low),
  close: parseFloat(kline.close),
  volume: kline.volume ? parseFloat(kline.volume) : undefined
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

### 3. 检查数据流

**后端日志**：
- `[DEBUG] 订阅 K 线流: btcusdt@kline_1m`
- `[DEBUG] 订阅 K 线流: btcusdt@kline_1h`
- `✅ [OK] ========== 币安 WebSocket 连接成功 ==========`
- `[DEBUG] 处理K线数据: symbol=BTC/USDT, interval=1m, timestamp=...`
- `[BROADCAST] ✅ 成功推送 K 线数据到 X 个客户端`

**浏览器控制台（F12）**：
- `[MarketDetail] ✅ WebSocket 连接成功`
- `[MarketDetail] 📡 WebSocket 状态: 已连接，等待接收 K 线数据...`
- `[MarketDetail] 📨 收到 WebSocket 消息`
- `[MarketDetail] 📊 收到K线数据`
- `[MarketDetail] ✅ 已更新 K 线图`
- `[TradingViewWidget] ✅ K 线更新成功`

### 4. 检查 WebSocket 帧（浏览器 F12 → Network → WS）

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签页
3. 筛选 **WS**（WebSocket）
4. 点击连接（通常是 `ws://localhost:5173/ws`）
5. 查看 **Messages** 标签页：
   - **发送**：前端发送的消息
   - **接收**：后端推送的 K 线数据（JSON 格式，包含 time/open/high/low/close/volume）

## 改动说明

### `app/services/market_service.py`

1. **订阅流确认**：添加日志确认订阅的是 `@kline` K 线流（不是 `@depth`）
2. **数据解析**：确保正确解析币安 WebSocket 返回的 K 线数据（time, open, high, low, close, volume）
3. **推送格式优化**：推送格式改为 `{time: unix_ms, open: float, high: float, low: float, close: float, volume: float}`
4. **Session 管理**：在重连循环内创建 Session，避免 Session closed 错误
5. **无限重连**：每 5 秒重试一次，处理各种错误类型

### `src/components/TradingViewWidget.vue`

1. **导入确认**：确认 `createChart` 正确导入（`addCandlestickSeries` 是 chart 实例的方法）
2. **图表大小**：宽度 100%，高度 420px（适合移动端）
3. **数据更新**：`updateLiveCandle` 使用 `series.update(bar)`，`updateHistory` 使用 `series.setData(bars)`
4. **初始加载**：监听 `props.initialData` 变化，自动加载历史 K 线
5. **主题设置**：涨绿色（#0ECB81），跌红色（#F6465D）

### `src/components/MarketDetail.vue`

1. **Props 传递**：确保传递 `symbol` 和 `interval` 到 TradingViewWidget
2. **WebSocket 状态**：`onopen` 更新状态为"已连接"
3. **数据转发**：`onmessage` 处理 K 线数据并转发到图表
4. **时间戳转换**：确保从毫秒转换为秒级时间戳

## 总结

本次修复解决了以下问题：

1. ✅ **订阅流确认**：确认订阅的是 `@kline` K 线流（不是 `@depth` 盘口数据）
2. ✅ **数据格式优化**：推送格式符合前端要求（{time: unix_ms, open: float, high: float, low: float, close: float, volume: float}）
3. ✅ **前端数据处理**：确保正确接收和转换数据格式
4. ✅ **图表初始化**：确认 `addCandlestickSeries()` 调用正确
5. ✅ **数据更新**：使用 `series.update(bar)` 和 `series.setData(bars)` 更新图表
6. ✅ **WebSocket 状态**：正确处理连接状态和数据转发

所有修复已完成，可以重启后端和 Vite，然后在浏览器 F12 中查看 Console，确认 K 线数据推送和图表渲染正常（币种实时 Binance 数据）。
