# K线图黑屏和"未连接"问题修复总结

## 问题诊断

### 1. 后端订阅问题
- **问题**：后端可能订阅了 `@depth` 深度数据而非 `@kline` K线数据
- **状态**：✅ **已修复** - 代码已正确订阅 `@kline_` 流

### 2. 前端 TypeError 问题
- **问题**：`TypeError: this.chart.initChart is not a function` 或 `this.chart.addCandlestickSeries is not a function`
- **原因**：
  - `initChart` 是组件方法，不是 `chart` 实例的方法
  - 图表容器可能未在 DOM 渲染完成前初始化
- **状态**：✅ **已修复** - 添加了容器存在性检查和重试逻辑

### 3. 数据更新问题
- **问题**：K线数据接收后未更新 `CandlestickSeries`
- **原因**：
  - `tvWidget.value` 可能未初始化
  - `updateLiveCandle` 方法可能不存在
  - 交易对或时间周期匹配逻辑可能有问题
- **状态**：✅ **已修复** - 添加了完整的数据验证和方法存在性检查

### 4. 连接状态更新问题
- **问题**：WebSocket 连接状态未同步更新
- **状态**：✅ **已修复** - 连接状态管理已完善

## 修复内容

### 1. `app/services/market_service.py`

#### 关键修复点：
1. **确保订阅 K 线流**：
   ```python
   # 第157行：明确订阅 @kline 流
   stream_name = f"{symbol.lower()}@kline_{interval}"
   
   # 第253行：跳过非 K 线流
   if '@kline_' not in stream_name.lower():
       logger.debug(f"[DEBUG] 跳过非 K 线流: {stream_name}")
       continue
   ```

2. **数据推送格式**：
   ```python
   # 第622-632行：推送标准 JSON 格式
   kline_data = {
       'symbol': kline.get('symbol'),
       'interval': kline.get('interval'),
       'time': int(kline.get('timestamp', 0)),  # 毫秒级时间戳
       'open': float(kline.get('open', 0)),
       'high': float(kline.get('high', 0)),
       'low': float(kline.get('low', 0)),
       'close': float(kline.get('close', 0)),
       'volume': float(kline.get('volume', 0)),
       'is_closed': kline.get('is_closed', False)
   }
   ```

3. **Session 管理**：
   ```python
   # 第210行：在重连循环内创建新的 Session
   async with aiohttp.ClientSession(connector=connector) as session:
       async with session.ws_connect(**ws_kwargs) as ws:
           # WebSocket 连接逻辑
   ```

4. **无限重连机制**：
   ```python
   # 第46行：无限重试
   _max_reconnect_attempts = 0  # 0 表示无限重试
   ```

### 2. `src/components/TradingViewWidget.vue`

#### 关键修复点：
1. **图表初始化检查**：
   ```javascript
   // 第69-81行：添加容器存在性检查
   const container = chartContainer.value
   if (!container) {
     console.warn('[TradingViewWidget] ⚠️ 图表容器未找到，等待 DOM 渲染...')
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
   ```

2. **正确的图表创建**：
   ```javascript
   // 第92-111行：使用 createChart 和 addCandlestickSeries
   chart.value = createChart(container, {
     width: containerWidth,
     height: containerHeight,
     // ... 配置
   })
   
   candleSeries.value = chart.value.addCandlestickSeries({
     upColor: '#0ECB81',
     downColor: '#F6465D',
     // ... 配置
   })
   ```

3. **数据格式转换**：
   ```javascript
   // 第264-271行：确保 time 是秒级时间戳
   const formattedCandle = {
     time: typeof candle.time === 'number' ? candle.time : (candle.time / 1000),
     open: parseFloat(candle.open),
     high: parseFloat(candle.high),
     low: parseFloat(candle.low),
     close: parseFloat(candle.close),
     volume: candle.volume ? parseFloat(candle.volume) : undefined
   }
   ```

4. **ResizeObserver**：
   ```javascript
   // 第173-203行：实现响应式图表大小调整
   resizeObserver.value = new ResizeObserver((entries) => {
     for (const entry of entries) {
       const { width } = entry.contentRect
       if (chart.value && width > 0) {
         chart.value.applyOptions({
           width: width,
           height: 420
         })
       }
     }
   })
   ```

### 3. `src/components/MarketDetail.vue`

#### 关键修复点：
1. **WebSocket 连接状态管理**：
   ```javascript
   // 第299-300行：连接状态定义
   const wsConnected = ref(false);
   const wsConnecting = ref(false);
   
   // 第562-572行：连接成功时更新状态
   backendWS.onopen = () => {
     wsConnected.value = true;
     wsConnecting.value = false;
     wsReconnectAttempts = 0;
   }
   ```

2. **K 线数据更新逻辑**：
   ```javascript
   // 第607-640行：完整的数据验证和更新逻辑
   if (klineSymbol === normalizedSymbol && kline.interval === selectedTimeframe.value) {
     // 确保 tvWidget 存在且已初始化
     if (!tvWidget.value) {
       console.warn('[MarketDetail] ⚠️ TradingViewWidget ref 未找到，等待组件初始化...');
       return;
     }
     
     // 确保 updateLiveCandle 方法存在
     if (typeof tvWidget.value.updateLiveCandle !== 'function') {
       console.warn('[MarketDetail] ⚠️ TradingViewWidget.updateLiveCandle 不是函数，等待组件初始化...');
       return;
     }
     
     // 转换时间戳并更新图表
     const candleTime = Math.floor((kline.time || kline.timestamp) / 1000);
     tvWidget.value.updateLiveCandle({
       time: candleTime,
       open: parseFloat(kline.open),
       high: parseFloat(kline.high),
       low: parseFloat(kline.low),
       close: parseFloat(kline.close),
       volume: kline.volume ? parseFloat(kline.volume) : undefined
     });
   }
   ```

3. **连接状态显示**：
   ```vue
   <!-- 第83-92行：WebSocket 状态指示器 -->
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

## 测试步骤

1. **重启后端服务**：
   ```bash
   # 停止当前服务
   # 重新启动 FastAPI 服务
   python main.py
   ```

2. **重启前端 Vite 服务**：
   ```bash
   # 停止当前服务
   # 重新启动 Vite 开发服务器
   npm run dev
   ```

3. **浏览器测试**：
   - 访问 `http://localhost:5173/`（**不是** `ws://localhost:5173/ws`）
   - 打开浏览器开发者工具（F12）
   - 查看 Console 标签页，确认：
     - WebSocket 连接成功日志
     - K 线数据接收日志
     - 图表初始化成功日志
   - 查看 Network 标签页，确认 WebSocket 连接状态为 "101 Switching Protocols"
   - 查看 K 线图是否正常显示（不再是黑屏）

4. **验证数据流**：
   - 后端日志应显示：
     - `[WS] ✅ 币安 WebSocket 连接成功`
     - `[DEBUG] 订阅 K 线流: btcusdt@kline_1m`
     - `[BROADCAST] ✅ 成功推送 K 线数据到 X 个客户端`
   - 前端 Console 应显示：
     - `[MarketDetail] ✅ WebSocket 连接成功`
     - `[MarketDetail] 📊 收到K线数据`
     - `[MarketDetail] ✅ 已更新 K 线图`
     - `[TradingViewWidget] ✅ K 线更新成功`

## 预期结果

1. ✅ 后端成功连接到 Binance WebSocket（`wss://stream.binance.com:443/ws`）
2. ✅ 后端订阅了正确的 K 线流（`@kline_` 而不是 `@depth`）
3. ✅ 前端 WebSocket 连接状态显示为"已连接"
4. ✅ K 线图正常显示，不再是黑屏
5. ✅ 实时 K 线数据正常更新
6. ✅ 图表大小自适应页面宽度（固定高度 420px）

## 故障排除

### 如果仍然显示"未连接"：
1. 检查后端服务是否正常运行（`http://localhost:8000/docs`）
2. 检查 Vite 代理配置（`vite.config.js` 中的 `/ws` 代理）
3. 检查浏览器 Console 是否有错误信息
4. 检查后端日志是否有连接错误

### 如果 K 线图仍然是黑屏：
1. 检查 `TradingViewWidget.vue` 是否正确导入 `lightweight-charts`
2. 检查浏览器 Console 是否有 `TypeError` 错误
3. 检查 `tvWidget.value` 是否正确初始化
4. 检查 K 线数据格式是否正确（time 应为秒级时间戳）

### 如果数据不更新：
1. 检查后端是否成功接收 Binance 数据（查看后端日志）
2. 检查交易对匹配逻辑（`klineSymbol === normalizedSymbol`）
3. 检查时间周期匹配逻辑（`kline.interval === selectedTimeframe.value`）
4. 检查 `updateLiveCandle` 方法是否正确调用

## 关键代码位置

- **后端 WebSocket 订阅**：`app/services/market_service.py` 第157行
- **后端数据推送**：`app/services/market_service.py` 第607-640行
- **前端图表初始化**：`src/components/TradingViewWidget.vue` 第61-170行
- **前端数据更新**：`src/components/MarketDetail.vue` 第607-640行
- **前端连接状态**：`src/components/MarketDetail.vue` 第83-92行
