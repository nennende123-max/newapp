# WebSocket 完整修复文档（最终版）

## 问题诊断

前端黑屏和"未连接"的原因：

1. **TradingViewWidget.vue TypeError**：`chart.CandleStickSeries is not a function`（拼写错误，应为 `addCandlestickSeries`）
2. **后端 Session closed 循环**：`aiohttp.ClientSession` 在重连时被过早关闭，导致无数据推送
3. **前端缺少 K 线数据更新逻辑**：收到 WebSocket 数据后未正确更新图表

## 修复方案

### 1. `app/services/market_service.py` - 后端优化

#### 关键修复点：

**a) Session 管理修复（解决 Session closed 错误）**
```python
while self.is_running:
    connector = None
    
    try:
        # ========== 关键修复：每次重连时重新创建 connector ==========
        connector = aiohttp.TCPConnector(ssl=False)
        
        # ========== 关键修复：使用 async with ClientSession() 确保 Session 不会过早关闭 ==========
        # 创建新的 session（确保每次重连时都是全新的 session）
        # 使用 async with 确保 Session 在 WebSocket 连接期间保持打开状态
        async with aiohttp.ClientSession(connector=connector) as session:
            # ========== 关键修复：在 session 的 async with 块内创建 WebSocket 连接 ==========
            # 确保 WebSocket 连接期间 Session 保持打开状态
            async with session.ws_connect(**ws_kwargs) as ws:
                # WebSocket 消息处理...
                async for msg in ws:
                    # 处理消息...
```

**b) 无限重连机制**
```python
_reconnect_delay = 5  # 重连延迟（秒）
_max_reconnect_attempts = 0  # 0 表示无限重试

# 在异常处理中：
except RuntimeError as e:
    # 专门捕获 RuntimeError（包括 Session closed）
    # 处理错误并重连...
except Exception as e:
    # 处理其他错误（timeout/SSL/connection refused）
    # 处理错误并重连...

if self.is_running:
    logger.info(f"[WS] 等待 {_reconnect_delay} 秒后重连...")
    await asyncio.sleep(_reconnect_delay)
```

**c) K 线数据解析和推送**
```python
async def _process_kline(self, kline_data):
    """
    处理真实的 K 线数据（核心逻辑）
    
    收到 WebSocket 数据后，解析 open/high/low/close/volume/time，
    更新数据库，并推送 JSON 格式给前端 /ws 客户端
    """
    # 解析币安 WebSocket 数据格式
    kline = {
        'symbol': symbol,                    # 交易对（如 BTC/USDT）
        'interval': interval,                 # 时间周期（如 1m, 1h）
        'timestamp': int(kline_data.get('t', 0)),  # 时间戳（毫秒）
        'open': float(kline_data.get('o', 0)),     # 开盘价
        'high': float(kline_data.get('h', 0)),    # 最高价
        'low': float(kline_data.get('l', 0)),     # 最低价
        'close': float(kline_data.get('c', 0)),   # 收盘价
        'volume': float(kline_data.get('v', 0)),  # 成交量
        'is_closed': is_closed               # 是否收盘
    }
    
    # 如果 K 线收盘，保存到数据库
    if is_closed:
        await KlineModel.upsert_klines([kline])
    
    # 广播给所有连接的客户端（包括未收盘的 K 线也推送，用于实时更新）
    await self._broadcast_kline(kline)

async def _broadcast_kline(self, kline: Dict[str, Any]):
    """广播 K 线数据给所有连接的客户端（前端 /ws 客户端）"""
    message = {
        'type': 'kline',
        'data': kline  # JSON 格式：包含 open/high/low/close/volume/timestamp
    }
    
    # 发送给所有活跃连接
    for ws in _active_connections:
        await ws.send_json(message)
```

### 2. `src/components/TradingViewWidget.vue` - 前端修复

#### 关键修复点：

**a) 修正 TypeError：使用正确的 addCandlestickSeries 方法**
```javascript
initChart() {
  try {
    // 创建图表实例
    this.chart = createChart(container, { /* ... */ });

    // ========== 关键修复：使用 this.chart.addCandlestickSeries()（不是 chart.CandleStickSeries）==========
    if (typeof this.chart.addCandlestickSeries !== 'function') {
      console.error('[TradingViewWidget] ❌ chart.addCandlestickSeries 不是函数');
      return;
    }

    // 创建 K 线系列
    this.candleSeries = this.chart.addCandlestickSeries({
      upColor: '#26a69a',        // 涨：绿色
      downColor: '#ef5350',      // 跌：红色
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });
  } catch (error) {
    console.error('[TradingViewWidget] ❌ 初始化图表失败:', error);
  }
}
```

**b) 添加数据更新逻辑：处理推送的 K 线数据**
```javascript
// 2. 更新单根 K 线（WebSocket 实时推送时用）
updateLiveCandle(candle) {
  try {
    if (!this.candleSeries) {
      console.warn('[TradingViewWidget] ⚠️ candleSeries 未初始化，跳过更新');
      return;
    }

    // 验证数据格式（确保包含 open/high/low/close/time）
    if (!candle || typeof candle !== 'object') {
      console.error('[TradingViewWidget] ❌ 无效的 K 线数据:', candle);
      return;
    }

    // 确保必要字段存在
    if (candle.time === undefined || candle.open === undefined || 
        candle.high === undefined || candle.low === undefined || candle.close === undefined) {
      console.error('[TradingViewWidget] ❌ K 线数据缺少必要字段:', candle);
      return;
    }

    // 更新 K 线（相当于 widget.updateBar(data)）
    this.candleSeries.update(candle);
    console.log('[TradingViewWidget] ✅ K 线更新成功');
  } catch (error) {
    console.error('[TradingViewWidget] ❌ 更新 K 线失败:', error);
  }
}
```

**c) 确保 widget 初始化正确**
```javascript
import { createChart } from 'lightweight-charts';  // 使用 lightweight-charts 库

mounted() {
  // 1. 初始化图表
  this.initChart();
  
  // 2. 如果有初始数据，立即填充
  if (this.initialData.length > 0) {
    this.candleSeries.setData(this.initialData);
  }
}
```

### 3. `src/components/MarketDetail.vue` - 前端 WebSocket 连接

#### 关键修复点：

**a) 添加 WebSocket 连接**
```javascript
const connectBackendWebSocket = () => {
  // ========== 关键修复：设置连接中状态 ==========
  wsConnecting.value = true;
  wsConnected.value = false;

  // 使用 Vite 代理：通过 /ws 路径连接
  const wsUrl = `ws://${window.location.host}/ws`;
  
  try {
    backendWS = new WebSocket(wsUrl);

    // ========== 关键修复：处理 onopen 更新状态为"已连接" ==========
    backendWS.onopen = () => {
      console.log('[MarketDetail] ✅ WebSocket 连接成功');
      wsConnected.value = true;
      wsConnecting.value = false; // 连接成功，取消连接中状态
      wsReconnectAttempts = 0; // 重置重连次数
    };

    // ========== 关键修复：处理 onmessage 更新 K 线图表 ==========
    backendWS.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 处理连接成功消息
        if (data.type === 'connected') {
          wsConnected.value = true;
          wsConnecting.value = false;
          return;
        }

        // 处理 K 线数据
        if (data.type === 'kline' && data.data) {
          const kline = data.data;
          
          // 检查交易对和时间周期是否匹配
          const normalizedSymbol = normalizeSymbol(symbol.value);
          const klineSymbol = kline.symbol?.replace('/', '').replace('USDT', '').toUpperCase();
          
          if (klineSymbol === normalizedSymbol && kline.interval === selectedTimeframe.value) {
            if (tvWidget.value && tvWidget.value.updateLiveCandle) {
              // 转换时间戳：从毫秒转为秒（TradingView 需要秒级时间戳）
              const candleTime = Math.floor(kline.timestamp / 1000);
              
              // 调用 TradingViewWidget 的 updateLiveCandle 方法更新 K 线
              tvWidget.value.updateLiveCandle({
                time: candleTime,
                open: parseFloat(kline.open),
                high: parseFloat(kline.high),
                low: parseFloat(kline.low),
                close: parseFloat(kline.close)
              });
              
              console.log('[MarketDetail] ✅ 已更新 K 线图');
            }
          }
        }
      } catch (error) {
        console.error('[MarketDetail] ❌ 解析 WebSocket 消息失败:', error);
      }
    };

    // ========== 关键修复：处理 onclose 显示"未连接"并重连 ==========
    backendWS.onclose = (event) => {
      console.warn('[MarketDetail] ⚠️ WebSocket 连接已关闭');
      wsConnected.value = false;
      wsConnecting.value = false; // 连接关闭，取消连接中状态
      backendWS = null;

      // 自动重连（每 3 秒重试，最多 3 次）
      if (wsReconnectAttempts < maxWsReconnectAttempts) {
        wsReconnectAttempts++;
        wsReconnectTimer = setTimeout(() => {
          connectBackendWebSocket();
        }, wsReconnectDelay);
      }
    };
  } catch (error) {
    console.error('[MarketDetail] ❌ 创建 WebSocket 连接失败:', error);
  }
};
```

**b) 连接状态显示**
```vue
<div class="ws-status-indicator" :class="{ 
  connected: wsConnected && !wsConnecting, 
  connecting: wsConnecting,
  disconnected: !wsConnected && !wsConnecting 
}">
  <span class="ws-status-dot"></span>
  <span class="ws-status-text">
    {{ wsConnecting ? '连接中...' : (wsConnected ? '已连接' : '未连接') }}
  </span>
</div>
```

**c) 生命周期管理**
```javascript
onMounted(() => {
  // ========== 关键修复：确保连接状态初始化为"连接中" ==========
  wsConnecting.value = true;
  wsConnected.value = false;
  
  // 连接后端 WebSocket（实时K线数据）
  connectBackendWebSocket();
  
  // 首次加载数据
  fetchKlineHistory();
});
```

## 数据格式说明

### 后端发送给前端（JSON 格式）

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

### 前端更新 TradingViewWidget

```javascript
tvWidget.value.updateLiveCandle({
  time: 1234567890,  // 秒（从毫秒转换）
  open: 50000.0,
  high: 51000.0,
  low: 49000.0,
  close: 50500.0
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

### 3. 检查连接状态

**前端 UI**：
- 🟡 **黄色圆点 + "连接中..."**：初始状态或重连中
- 🟢 **绿色圆点 + "已连接"**：WebSocket 连接正常
- 🔴 **红色圆点 + "未连接"**：连接断开

**浏览器控制台（F12）**：
- `[MarketDetail] ========== 连接后端 WebSocket ==========`
- `[MarketDetail] ✅ WebSocket 连接成功`
- `[TradingViewWidget] ✅ 图表初始化成功`
- `[MarketDetail] 📨 收到 WebSocket 消息`
- `[MarketDetail] 📊 收到K线数据`
- `[MarketDetail] ✅ 已更新 K 线图`
- `[TradingViewWidget] ✅ K 线更新成功`

**后端日志**：
- `✅ [OK] ========== 币安 WebSocket 连接成功 ==========`
- `[DEBUG] 处理K线数据: symbol=BTC/USDT, interval=1m, timestamp=...`
- `[BROADCAST] ✅ 成功推送 K 线数据到 X 个客户端`

### 4. 检查 WebSocket 帧（浏览器 F12 → Network → WS）

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签页
3. 筛选 **WS**（WebSocket）
4. 点击连接（通常是 `ws://localhost:5173/ws`）
5. 查看 **Messages** 标签页：
   - **发送**：前端发送的消息
   - **接收**：后端推送的 K 线数据（JSON 格式，包含 open/high/low/close/volume/timestamp）

## 改动说明

### `app/services/market_service.py`

1. **Session 管理**：在 `while self.is_running:` 循环内创建 `ClientSession` 和 `TCPConnector`，每次重连时重新创建
2. **RuntimeError 捕获**：专门捕获 `RuntimeError`（包括 Session closed），添加详细的错误处理
3. **数据解析**：确保正确解析币安 WebSocket 数据（open/high/low/close/volume/time）
4. **数据推送**：确保数据接收后立即推送给前端客户端（JSON 格式）

### `src/components/TradingViewWidget.vue`

1. **修正 TypeError**：使用 `this.chart.addCandlestickSeries()`（不是 `chart.CandleStickSeries`）
2. **数据更新逻辑**：完善 `updateLiveCandle` 方法，验证数据格式（确保包含 open/high/low/close/time）
3. **Widget 初始化**：确保在 `mounted()` 生命周期中正确初始化，使用 `lightweight-charts` 库

### `src/components/MarketDetail.vue`

1. **WebSocket 连接**：添加 `new WebSocket('ws://localhost:5173/ws')` 连接逻辑
2. **onopen 处理**：更新状态为"已连接"
3. **onmessage 处理**：解析 K 线数据并更新图表
4. **onclose 处理**：显示"未连接"并重连（每 3 秒重试，最多 3 次）
5. **连接状态初始化**：在 `onMounted()` 中设置初始状态为"连接中"

## 总结

本次修复解决了以下问题：

1. ✅ **TradingViewWidget TypeError**：修正为 `this.chart.addCandlestickSeries()`（不是 `chart.CandleStickSeries`）
2. ✅ **后端 Session closed 循环**：在重连循环内重新创建 Session，避免 Session closed 错误
3. ✅ **数据解析和推送**：确保正确解析 open/high/low/close/volume/time，并推送 JSON 格式给前端
4. ✅ **前端 K 线数据更新**：添加完整的 WebSocket 连接和数据更新逻辑
5. ✅ **连接状态显示**：添加"连接中"/"已连接"/"未连接"三种状态显示
6. ✅ **重连机制**：每 3 秒重试，最多 3 次

所有修复已完成，可以重启后端和 Vite，然后在浏览器 F12 中查看 Console，确认 K 线数据推送和图表刷新正常。
