# WebSocket 连接状态修复文档

## 问题诊断

前端页面显示"未连接"的原因：
1. **后端 Binance WebSocket 连接失败或 Session closed 循环**：导致无数据推送给前端
2. **前端 MarketDetail.vue 缺少连接状态更新逻辑**：初始状态未显示"连接中"，重连逻辑不完善
3. **TradingViewWidget 未接收推送数据**：收到 K 线数据后未调用 `updateLiveCandle` 方法更新图表

## 修复方案

### 1. `app/services/market_service.py` - 后端优化

#### 关键修复点：

**a) 确保数据接收后立即推送**
```python
# 在消息处理循环中，添加推送日志
if message_count % 100 == 0:
    logger.debug(f"[DEBUG] 已处理并推送 {message_count} 条 K 线数据到前端客户端")
```

**b) 优化 `_broadcast_kline` 方法**
```python
async def _broadcast_kline(self, kline: Dict[str, Any]):
    """
    广播 K 线数据给所有连接的客户端（前端 /ws 客户端）
    
    关键修复：确保数据接收后立即推送给前端，不延迟
    """
    if not _active_connections:
        logger.debug(f"[DEBUG] 无活跃的前端连接，跳过推送")
        return
    
    # ... 发送逻辑 ...
    
    # 记录推送成功日志
    if success_count > 0:
        logger.debug(f"[BROADCAST] ✅ 成功推送 K 线数据到 {success_count} 个客户端")
```

**c) Session 管理（已在之前修复）**
- 在 `while self.is_running:` 循环内创建 `ClientSession` 和 `TCPConnector`
- 每次重连时重新创建，避免 Session closed 错误

**d) 无限重连机制（已在之前修复）**
- `_max_reconnect_attempts = 0`（无限重试）
- `_reconnect_delay = 5`（每 5 秒重试一次）

### 2. `src/components/MarketDetail.vue` - 前端优化

#### 关键修复点：

**a) 添加连接中状态**
```javascript
const wsConnecting = ref(false); // WebSocket 连接中状态（初始状态）
```

**b) 连接状态显示（三种状态）**
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

**c) 连接状态管理**
```javascript
const connectBackendWebSocket = () => {
  // 设置连接中状态
  wsConnecting.value = true;
  wsConnected.value = false;
  
  backendWS.onopen = () => {
    wsConnected.value = true;
    wsConnecting.value = false; // 连接成功，取消连接中状态
  };
  
  backendWS.onerror = () => {
    wsConnected.value = false;
    wsConnecting.value = false; // 连接失败，取消连接中状态
  };
  
  backendWS.onclose = () => {
    wsConnected.value = false;
    wsConnecting.value = false; // 连接关闭，取消连接中状态
  };
};
```

**d) 关键修复：TradingViewWidget 接收推送数据**
```javascript
backendWS.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'kline' && data.data) {
    const kline = data.data;
    
    // 检查当前交易对是否匹配
    const normalizedSymbol = normalizeSymbol(symbol.value);
    const klineSymbol = kline.symbol?.replace('/', '').replace('USDT', '').toUpperCase();
    
    // 如果交易对匹配，且时间周期匹配，则更新图表
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
};
```

**e) 重连机制（每 3 秒重试，最多 3 次）**
```javascript
const maxWsReconnectAttempts = 3;
const wsReconnectDelay = 3000; // 3秒

backendWS.onclose = (event) => {
  if (wsReconnectAttempts < maxWsReconnectAttempts) {
    wsReconnectAttempts++;
    wsReconnectTimer = setTimeout(() => {
      connectBackendWebSocket();
    }, wsReconnectDelay);
  }
};
```

**f) 连接中状态样式（动画效果）**
```css
.ws-status-indicator.connecting .ws-status-dot {
  background-color: #F0B90B;
  box-shadow: 0 0 4px rgba(240, 185, 11, 0.5);
  animation: pulse 1.5s ease-in-out infinite;
}

.ws-status-indicator.connecting .ws-status-text {
  color: #F0B90B;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
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

访问 `http://localhost:5173/`（HTTP 协议），导航到市场详情页面。

### 3. 检查连接状态

**前端 UI 状态指示器**：
- 🟢 **绿色圆点 + "已连接"**：WebSocket 连接正常
- 🟡 **黄色圆点 + "连接中..."**：正在连接（初始状态或重连中）
- 🔴 **红色圆点 + "未连接"**：连接断开

**浏览器控制台（F12）**：
- `[MarketDetail] ✅ WebSocket 连接成功`
- `[MarketDetail] 📨 收到 WebSocket 消息`
- `[MarketDetail] 📊 收到K线数据`
- `[MarketDetail] ✅ 已更新 K 线图`

**后端日志**：
- `✅ [OK] ========== 币安 WebSocket 连接成功 ==========`
- `[BROADCAST] ✅ 成功推送 K 线数据到 X 个客户端`

### 4. 检查 WebSocket 帧（浏览器 F12 → Network → WS）

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签页
3. 筛选 **WS**（WebSocket）
4. 点击连接（通常是 `ws://localhost:5173/ws`）
5. 查看 **Messages** 标签页：
   - **发送**：前端发送的消息（如心跳）
   - **接收**：后端推送的 K 线数据（JSON 格式）

### 5. 测试数据流动

1. **初始连接**：页面加载时，状态应显示"连接中..."，然后变为"已连接"
2. **K 线更新**：等待几秒钟，观察 K 线图是否实时更新
3. **重连测试**：停止后端服务（Ctrl+C），观察前端是否自动重连（每 3 秒重试，最多 3 次）
4. **数据匹配**：切换交易对或时间周期，确认只有匹配的数据才会更新图表

## 数据流说明

### 完整数据流

1. **Binance WebSocket** → `market_service.py` 的 `start_stream_safe()`
2. **数据解析** → `_process_kline()` 方法处理 K 线数据
3. **数据库保存** → `KlineModel.upsert_klines()`（如果 `is_closed=True`）
4. **广播推送** → `_broadcast_kline()` 推送给所有前端客户端
5. **前端接收** → `MarketDetail.vue` 的 `backendWS.onmessage`
6. **图表更新** → `tvWidget.value.updateLiveCandle()` 更新 TradingViewWidget

### 数据格式转换

**后端发送给前端**：
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

**前端更新 TradingViewWidget**：
```javascript
tvWidget.value.updateLiveCandle({
  time: 1234567890,  // 秒（从毫秒转换）
  open: 50000.0,
  high: 51000.0,
  low: 49000.0,
  close: 50500.0
});
```

## 常见问题

### Q1: 前端一直显示"连接中..."

**原因**：WebSocket 连接未成功建立。

**解决方案**：
1. 检查后端服务是否运行在 `http://127.0.0.1:8000`
2. 检查 Vite 代理配置是否正确
3. 查看浏览器控制台，确认是否有错误信息
4. 查看后端日志，确认 Binance WebSocket 是否连接成功

### Q2: 前端显示"已连接"但 K 线图不更新

**原因**：数据未匹配或 TradingViewWidget 未正确更新。

**解决方案**：
1. 检查浏览器控制台，确认是否收到 K 线数据消息
2. 检查交易对和时间周期是否匹配：
   - `klineSymbol === normalizedSymbol`
   - `kline.interval === selectedTimeframe.value`
3. 确认 `tvWidget.value` 和 `updateLiveCandle` 方法存在
4. 检查时间戳转换是否正确（毫秒 → 秒）

### Q3: 后端日志显示推送成功但前端未收到

**原因**：前端 WebSocket 连接未正确注册。

**解决方案**：
1. 检查 `app/api/endpoints/market.py` 的 `/ws/kline` 端点是否正确注册客户端
2. 检查 `_active_connections` 集合是否包含前端连接
3. 查看后端日志中的 `[BROADCAST]` 消息，确认推送的客户端数量

### Q4: 后端显示 Session closed 错误

**原因**：`aiohttp.ClientSession` 在重连时被过早关闭。

**解决方案**：
- 已在 `market_service.py` 中修复：每次重连时重新创建 Session
- 确保 `async with aiohttp.ClientSession()` 在循环内部

## 总结

本次修复解决了以下问题：

1. ✅ **连接状态显示**：添加"连接中"状态，初始状态更清晰
2. ✅ **数据推送优化**：确保数据接收后立即推送给前端
3. ✅ **TradingViewWidget 更新**：收到 K 线数据后立即调用 `updateLiveCandle` 更新图表
4. ✅ **数据匹配**：只有匹配的交易对和时间周期才会更新图表
5. ✅ **重连机制**：每 3 秒重试，最多 3 次，状态显示更清晰
6. ✅ **日志优化**：添加详细的推送日志，便于调试

所有修复已完成，可以重启服务进行测试。
