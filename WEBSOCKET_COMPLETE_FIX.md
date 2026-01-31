# WebSocket 完整修复文档

## 问题诊断

1. **前端 ERR_UNKNOWN_URL_SCHEME 错误**：用户直接在浏览器地址栏访问 `ws://localhost:5173/ws`，但 WebSocket 必须通过 JavaScript 代码在 HTTP 页面内连接。
2. **后端 Session closed 循环**：`aiohttp.ClientSession` 在重连时被过早关闭，导致 `RuntimeError: Session is closed` 错误。
3. **WebSocket 连接不稳定**：缺少详细日志和错误处理，难以诊断连接问题。

## 修复方案

### 1. `app/services/market_service.py` - 后端 WebSocket 服务

#### 关键修复点：

**a) Session 管理修复（解决 Session closed 错误）**
```python
# 关键修复：在 while self.is_running 循环内部创建 connector 和 session
# 确保每次重连时都重新创建，避免使用已关闭的 Session
while self.is_running:
    connector = None
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.ws_connect(**ws_kwargs) as ws:
                # WebSocket 消息处理...
    except Exception as e:
        # 错误处理和重连逻辑...
        if connector:
            await connector.close()  # 显式关闭 connector
```

**b) 固定直连 Binance WebSocket（443端口）**
```python
# 固定直连，移除所有代理逻辑
primary_url = f"wss://stream.binance.com:443/ws?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com:443/ws?streams={'/'.join(streams)}"
```

**c) 无限重连机制**
```python
_max_reconnect_attempts = 0  # 0 表示无限重试
_reconnect_delay = 5  # 每 5 秒重试一次
```

**d) 详细日志记录**
```python
# 启用 DEBUG 级别日志
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

# 详细异常日志
logger.debug(f"[DEBUG] 连接异常详情: {traceback.format_exc()}")

# 特定错误检测
if 'session' in error_str and 'closed' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 Session closed 错误")
```

**e) K 线数据处理和数据库更新**
```python
async def _process_kline(self, kline_data):
    # 处理 K 线数据
    # 如果 is_closed=True，保存到数据库
    if is_closed:
        await KlineModel.upsert_klines([kline_dict])
    
    # 广播给所有前端客户端（包括未收盘的 K 线也推送）
    await self._broadcast_kline(kline)
```

### 2. `vite.config.js` - 前端 WebSocket 代理配置

#### 关键修复点：

**a) WebSocket 代理配置**
```javascript
'/ws': {
  target: 'ws://127.0.0.1:8000',  // 后端 FastAPI 服务器（端口8000）
  changeOrigin: true,
  ws: true,  // 启用 WebSocket 代理
  secure: false,  // 禁用 SSL 验证（开发环境）
  rewrite: (path) => path.replace(/^\/ws/, '/api/v1/market/ws/kline'),
  configure: (proxy, _options) => {
    // 增强的代理事件监听
    proxy.on('error', (err) => {
      console.error('[Vite Proxy] ❌ WebSocket proxy error:', err);
    });
    proxy.on('proxyReqWs', (proxyReq, req) => {
      console.log('[Vite Proxy] ✅ WebSocket proxy request:', req.url);
    });
  }
}
```

**说明**：
- 前端通过 `ws://localhost:5173/ws` 连接
- Vite 自动代理到 `ws://127.0.0.1:8000/api/v1/market/ws/kline`
- 支持 WebSocket 升级协议

### 3. `src/components/MarketDetail.vue` - 前端 WebSocket 连接逻辑

#### 关键修复点：

**a) WebSocket 连接函数**
```javascript
const connectBackendWebSocket = () => {
  // 使用 Vite 代理：通过 /ws 路径连接
  const wsUrl = `ws://${window.location.host}/ws`;
  backendWS = new WebSocket(wsUrl);
  
  backendWS.onopen = () => {
    console.log('[MarketDetail] ✅ WebSocket 连接成功');
    wsConnected.value = true;
    wsReconnectAttempts = 0;
  };
  
  backendWS.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // 处理 K 线数据
    if (data.type === 'kline' && data.data) {
      // 更新 K 线图
    }
  };
  
  backendWS.onerror = (error) => {
    // 检查 ERR_UNKNOWN_URL_SCHEME 错误
    if (error.message && error.message.includes('ERR_UNKNOWN_URL_SCHEME')) {
      console.error('[MarketDetail] ⚠️ ERR_UNKNOWN_URL_SCHEME 错误');
      console.error('[MarketDetail] 原因: 不能直接在浏览器地址栏访问 ws:// 协议');
      console.error('[MarketDetail] 解决方案: 请访问 http://localhost:5173/（非 ws://）');
    }
  };
  
  backendWS.onclose = (event) => {
    // 自动重连（每 3 秒重试，最多 3 次）
    if (wsReconnectAttempts < maxWsReconnectAttempts) {
      wsReconnectAttempts++;
      wsReconnectTimer = setTimeout(() => {
        connectBackendWebSocket();
      }, wsReconnectDelay);
    }
  };
};
```

**b) 重连配置**
```javascript
const maxWsReconnectAttempts = 3;  // 最多重试 3 次
const wsReconnectDelay = 3000;     // 每 3 秒重试一次
```

**c) 连接状态显示**
```vue
<!-- WebSocket 连接状态指示器 -->
<div class="ws-status-indicator" :class="{ connected: wsConnected, disconnected: !wsConnected }">
  <span class="ws-status-dot"></span>
  <span class="ws-status-text">{{ wsConnected ? '已连接' : '未连接' }}</span>
</div>
```

**d) 生命周期管理**
```javascript
onMounted(() => {
  connectBackendWebSocket();  // 组件挂载时连接
});

onUnmounted(() => {
  disconnectBackendWebSocket();  // 组件卸载时断开
});

// 监听 symbol 变化，重新连接
watch(symbol, () => {
  if (!backendWS || backendWS.readyState !== WebSocket.OPEN) {
    connectBackendWebSocket();
  }
});
```

### 4. `src/main.js` - Vue 应用初始化

#### 确认配置：

```javascript
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)      // Pinia 状态管理
app.use(i18n)       // 国际化
app.use(router)     // 路由
app.use(Vant)       // Vant UI 组件库
app.mount('#app')
```

**说明**：`main.js` 已经正确配置，无需修改。

## 使用说明

### 1. 启动后端服务

```bash
# 激活虚拟环境（如果使用）
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 启动 FastAPI 服务（端口 8000）
python main.py
```

### 2. 启动前端服务

```bash
# 安装依赖（如果尚未安装）
npm install

# 启动 Vite 开发服务器（端口 5173）
npm run dev
```

### 3. 访问应用

**重要**：必须访问 `http://localhost:5173/`（HTTP 协议），**不能**直接在浏览器地址栏访问 `ws://localhost:5173/ws`。

WebSocket 连接会通过 JavaScript 代码自动建立。

### 4. 检查连接状态

1. **前端控制台**：打开浏览器开发者工具（F12），查看 Console 标签页
   - 应该看到 `[MarketDetail] ✅ WebSocket 连接成功`
   - 如果看到 `ERR_UNKNOWN_URL_SCHEME`，说明用户直接访问了 `ws://` URL

2. **后端日志**：查看后端终端输出
   - 应该看到 `✅ [OK] ========== 币安 WebSocket 连接成功 ==========`
   - 如果看到 `Session closed` 错误，说明 Session 管理有问题

3. **UI 状态指示器**：在页面顶部查看 WebSocket 连接状态
   - 绿色圆点 + "已连接"：连接正常
   - 红色圆点 + "未连接"：连接断开

## 测试步骤

1. **启动服务**
   ```bash
   # 终端1：启动后端
   python main.py
   
   # 终端2：启动前端
   npm run dev
   ```

2. **访问页面**
   - 打开浏览器，访问 `http://localhost:5173/`
   - 导航到市场详情页面（例如：`/market?symbol=BTC`）

3. **检查连接**
   - 查看浏览器控制台，确认 WebSocket 连接成功
   - 查看后端日志，确认 Binance WebSocket 连接成功
   - 查看页面上的连接状态指示器

4. **测试重连**
   - 停止后端服务（Ctrl+C）
   - 观察前端是否自动重连（每 3 秒重试，最多 3 次）
   - 重新启动后端服务
   - 观察前端是否成功重连

5. **测试 K 线数据**
   - 等待几秒钟，观察 K 线图是否更新
   - 查看浏览器控制台，确认收到 K 线数据消息
   - 查看后端日志，确认 K 线数据已保存到数据库

## 常见问题

### Q1: 前端显示 "ERR_UNKNOWN_URL_SCHEME"

**原因**：用户直接在浏览器地址栏访问了 `ws://localhost:5173/ws`。

**解决方案**：
1. 访问 `http://localhost:5173/`（HTTP 协议）
2. WebSocket 连接会通过 JavaScript 代码自动建立
3. 不要直接在浏览器地址栏访问 `ws://` URL

### Q2: 后端显示 "RuntimeError: Session is closed"

**原因**：`aiohttp.ClientSession` 在重连时被过早关闭。

**解决方案**：
- 已在 `market_service.py` 中修复：每次重连时重新创建 `ClientSession` 和 `TCPConnector`
- 使用 `async with` 确保 Session 在 WebSocket 连接期间保持打开状态

### Q3: 前端显示 "网络未连接"

**原因**：WebSocket 连接失败或后端服务未启动。

**解决方案**：
1. 检查后端服务是否运行在 `http://127.0.0.1:8000`
2. 检查 Vite 代理配置是否正确
3. 查看浏览器控制台和后端日志，确认错误原因
4. 前端会自动重连（每 3 秒重试，最多 3 次）

### Q4: K 线图没有数据

**原因**：数据库中没有历史数据，或 WebSocket 连接未建立。

**解决方案**：
1. 等待后端同步历史数据（启动时会自动同步）
2. 检查数据库文件是否存在且可访问
3. 查看后端日志，确认历史数据同步是否成功
4. 检查 WebSocket 连接是否正常

## 技术细节

### WebSocket 连接流程

1. **前端**：`MarketDetail.vue` 调用 `connectBackendWebSocket()`
2. **Vite 代理**：将 `ws://localhost:5173/ws` 代理到 `ws://127.0.0.1:8000/api/v1/market/ws/kline`
3. **后端**：`app/api/endpoints/market.py` 的 `/ws/kline` 端点处理 WebSocket 连接
4. **后端服务**：`market_service.py` 的 `start_stream_safe()` 连接 Binance WebSocket
5. **数据流**：Binance → `market_service.py` → `KlineModel` → 前端客户端

### 数据格式

**后端发送给前端**：
```json
{
  "type": "kline",
  "data": {
    "symbol": "BTC/USDT",
    "interval": "1m",
    "timestamp": 1234567890000,
    "open": 50000.0,
    "high": 51000.0,
    "low": 49000.0,
    "close": 50500.0,
    "volume": 1000.0,
    "is_closed": true
  }
}
```

**数据库存储格式**：
```python
{
  'symbol': 'BTC/USDT',
  'interval': '1m',
  'timestamp': 1234567890000,  # 毫秒
  'open': 50000.0,
  'high': 51000.0,
  'low': 49000.0,
  'close': 50500.0,
  'volume': 1000.0
}
```

## 总结

本次修复解决了以下问题：

1. ✅ **前端 ERR_UNKNOWN_URL_SCHEME 错误**：通过正确的 JavaScript WebSocket 连接和用户提示解决
2. ✅ **后端 Session closed 错误**：通过每次重连时重新创建 Session 解决
3. ✅ **WebSocket 连接不稳定**：通过无限重连机制和详细日志解决
4. ✅ **K 线数据更新**：确保实时数据保存到数据库并推送给前端
5. ✅ **连接状态显示**：添加 UI 状态指示器，方便用户查看连接状态

所有修复已完成，可以重启服务进行测试。
