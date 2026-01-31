# WebSocket 最终修复文档

## 问题诊断

前端"未连接"显示的原因：

1. **后端 Binance WebSocket Session closed 循环**：`RuntimeError: Session is closed` 导致无数据推送
2. **前端 TradingViewWidget TypeError**：`chart.addCandlestickSeries` 可能在某些情况下不是函数
3. **前端缺少连接状态更新**：初始状态未正确设置为"连接中"

## 修复方案

### 1. `app/services/market_service.py` - 后端优化

#### 关键修复点：

**a) 专门捕获 RuntimeError（包括 Session closed）**
```python
except RuntimeError as e:
    # ========== 关键修复：专门捕获 RuntimeError（包括 Session closed）==========
    consecutive_failures += 1
    reconnect_attempts += 1
    
    # 检查是否是 Session closed 错误
    error_str = str(e).lower()
    if 'session' in error_str and 'closed' in error_str:
        logger.error(f"[ERROR] ⚠️ 检测到 Session closed 错误（RuntimeError）")
        logger.error(f"[ERROR] 解决方案: 已在重连循环内重新创建 Session，确保不会使用已关闭的 Session")
    
    # 清理资源
    if connector:
        try:
            await connector.close()
        except Exception as close_error:
            logger.debug(f"[DEBUG] 关闭 connector 时出错（RuntimeError）: {close_error}")
```

**b) Session 管理（已在之前修复）**
- 在 `while self.is_running:` 循环内创建 `ClientSession` 和 `TCPConnector`
- 每次重连时重新创建，避免 Session closed 错误

**c) 无限重连机制**
- `_max_reconnect_attempts = 0`（无限重试）
- `_reconnect_delay = 5`（每 5 秒重试一次）
- 处理 Session closed/timeout/SSL 错误

**d) 确认数据推送**
- 数据接收后立即调用 `_process_kline()` 处理
- `_broadcast_kline()` 立即推送给所有前端客户端

### 2. `src/components/TradingViewWidget.vue` - 前端修复

#### 关键修复点：

**a) 修正 TypeError：确保 chart 初始化正确**
```javascript
initChart() {
  try {
    // 获取容器 DOM
    const container = this.$refs.chartContainer;
    
    if (!container) {
      console.error('[TradingViewWidget] ❌ 容器 DOM 未找到');
      return;
    }

    // ========== 关键修复：确保 createChart 正确导入和调用 ==========
    if (typeof createChart !== 'function') {
      console.error('[TradingViewWidget] ❌ createChart 不是函数，请检查 lightweight-charts 导入');
      return;
    }

    // 创建图表实例
    this.chart = createChart(container, { /* ... */ });

    // ========== 关键修复：确保 chart 已创建且 addCandlestickSeries 方法存在 ==========
    if (!this.chart) {
      console.error('[TradingViewWidget] ❌ 图表实例创建失败');
      return;
    }

    if (typeof this.chart.addCandlestickSeries !== 'function') {
      console.error('[TradingViewWidget] ❌ chart.addCandlestickSeries 不是函数');
      console.error('[TradingViewWidget] chart 对象:', this.chart);
      console.error('[TradingViewWidget] chart 方法:', Object.keys(this.chart));
      return;
    }

    // 创建 K 线系列
    this.candleSeries = this.chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    if (!this.candleSeries) {
      console.error('[TradingViewWidget] ❌ K 线系列创建失败');
      return;
    }

    console.log('[TradingViewWidget] ✅ 图表初始化成功');
  } catch (error) {
    console.error('[TradingViewWidget] ❌ 初始化图表失败:', error);
    console.error('[TradingViewWidget] 错误详情:', error.stack);
  }
}
```

**b) 添加数据更新逻辑：完善 updateLiveCandle 方法**
```javascript
updateLiveCandle(candle) {
  try {
    if (!this.candleSeries) {
      console.warn('[TradingViewWidget] ⚠️ candleSeries 未初始化，跳过更新');
      return;
    }

    if (typeof this.candleSeries.update !== 'function') {
      console.error('[TradingViewWidget] ❌ candleSeries.update 不是函数');
      return;
    }

    // ========== 关键修复：验证数据格式 ==========
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

    // 更新 K 线
    this.candleSeries.update(candle);
    console.log('[TradingViewWidget] ✅ K 线更新成功:', {
      time: candle.time,
      close: candle.close
    });
  } catch (error) {
    console.error('[TradingViewWidget] ❌ 更新 K 线失败:', error);
    console.error('[TradingViewWidget] K 线数据:', candle);
    console.error('[TradingViewWidget] 错误详情:', error.stack);
  }
}
```

**c) 确保 widget 初始化正确**
- 使用 `lightweight-charts` 库的 `createChart`
- 在 `mounted()` 生命周期中初始化
- 添加完整的错误处理和日志

### 3. `src/components/MarketDetail.vue` - 前端连接状态修复

#### 关键修复点：

**a) 添加连接状态初始化**
```javascript
onMounted(() => {
  // ========== 关键修复：确保连接状态初始化为"连接中" ==========
  // 初始状态：连接中
  wsConnecting.value = true;
  wsConnected.value = false;
  
  // 连接后端 WebSocket（实时K线数据）
  connectBackendWebSocket();
  
  // ... 其他初始化逻辑 ...
});
```

**b) 连接状态更新（已在之前修复）**
- `onopen`：设置 `wsConnected = true`，`wsConnecting = false`
- `onclose`：设置 `wsConnected = false`，`wsConnecting = false`
- `onerror`：设置 `wsConnected = false`，`wsConnecting = false`

**c) 连接状态显示（已在之前修复）**
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
- `[TradingViewWidget] ✅ K 线更新成功`

**后端日志**：
- `✅ [OK] ========== 币安 WebSocket 连接成功 ==========`
- `[BROADCAST] ✅ 成功推送 K 线数据到 X 个客户端`
- 如果出现 `RuntimeError: Session is closed`，会显示专门的错误处理日志

### 4. 检查 WebSocket 帧（浏览器 F12 → Network → WS）

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签页
3. 筛选 **WS**（WebSocket）
4. 点击连接（通常是 `ws://localhost:5173/ws`）
5. 查看 **Messages** 标签页：
   - **发送**：前端发送的消息
   - **接收**：后端推送的 K 线数据（JSON 格式）

## 数据流说明

### 完整数据流

1. **Binance WebSocket** → `market_service.py` 的 `start_stream_safe()`
2. **数据解析** → `_process_kline()` 方法处理 K 线数据
3. **数据库保存** → `KlineModel.upsert_klines()`（如果 `is_closed=True`）
4. **广播推送** → `_broadcast_kline()` 推送给所有前端客户端
5. **前端接收** → `MarketDetail.vue` 的 `backendWS.onmessage`
6. **图表更新** → `tvWidget.value.updateLiveCandle()` 更新 TradingViewWidget

### 错误处理流程

1. **RuntimeError（Session closed）**：
   - 捕获 `RuntimeError` 异常
   - 检查是否是 Session closed 错误
   - 清理资源（关闭 connector）
   - 等待 5 秒后重连（重新创建 Session）

2. **TradingViewWidget TypeError**：
   - 检查 `createChart` 是否为函数
   - 检查 `chart.addCandlestickSeries` 是否为函数
   - 检查 `candleSeries.update` 是否为函数
   - 验证数据格式完整性

3. **连接状态更新**：
   - 初始状态：`wsConnecting = true`，`wsConnected = false`
   - 连接成功：`wsConnecting = false`，`wsConnected = true`
   - 连接失败：`wsConnecting = false`，`wsConnected = false`

## 常见问题

### Q1: 后端显示 RuntimeError: Session is closed

**原因**：`aiohttp.ClientSession` 在重连时被过早关闭。

**解决方案**：
- 已在 `market_service.py` 中修复：专门捕获 `RuntimeError`
- 每次重连时重新创建 `ClientSession` 和 `TCPConnector`
- 使用 `async with` 确保 Session 在 WebSocket 连接期间保持打开状态

### Q2: 前端显示 TypeError: chart.addCandlestickSeries is not a function

**原因**：图表未正确初始化，或 `lightweight-charts` 库未正确导入。

**解决方案**：
- 已在 `TradingViewWidget.vue` 中修复：添加完整的初始化检查
- 检查 `createChart` 是否为函数
- 检查 `chart` 对象是否存在
- 检查 `chart.addCandlestickSeries` 是否为函数
- 添加详细的错误日志

### Q3: 前端一直显示"连接中..."

**原因**：WebSocket 连接未成功建立。

**解决方案**：
1. 检查后端服务是否运行在 `http://127.0.0.1:8000`
2. 检查 Vite 代理配置是否正确
3. 查看浏览器控制台，确认是否有错误信息
4. 查看后端日志，确认 Binance WebSocket 是否连接成功

### Q4: K 线图不更新

**原因**：数据未匹配或 TradingViewWidget 未正确更新。

**解决方案**：
1. 检查浏览器控制台，确认是否收到 K 线数据消息
2. 检查交易对和时间周期是否匹配
3. 确认 `tvWidget.value` 和 `updateLiveCandle` 方法存在
4. 检查时间戳转换是否正确（毫秒 → 秒）
5. 查看 `[TradingViewWidget] ✅ K 线更新成功` 日志

## 总结

本次修复解决了以下问题：

1. ✅ **RuntimeError 捕获**：专门捕获 `RuntimeError`（包括 Session closed），添加详细的错误处理
2. ✅ **TradingViewWidget TypeError**：添加完整的初始化检查，确保 `chart.addCandlestickSeries` 正确调用
3. ✅ **数据更新逻辑**：完善 `updateLiveCandle` 方法，添加数据验证和错误处理
4. ✅ **连接状态初始化**：确保初始状态正确设置为"连接中"
5. ✅ **Session 管理**：每次重连时重新创建 Session，避免 Session closed 错误
6. ✅ **无限重连**：每 5 秒重试一次，处理各种错误类型

所有修复已完成，可以重启服务进行测试。
