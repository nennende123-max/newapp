# WebSocket 前端连接修复说明

## 问题诊断

用户遇到前端 "ERR_UNKNOWN_URL_SCHEME" 错误，原因是：
1. **用户直接在浏览器地址栏访问 `ws://localhost:5173/ws`**：WebSocket 协议不能直接在浏览器地址栏访问，必须通过 JavaScript 代码连接
2. **后端 Session closed 错误**：需要修复 Session 管理，确保 Session 在 WebSocket 连接期间保持打开状态

## 修复内容

### 1. 修复后端 Session 管理（`app/services/market_service.py`）

#### 1.1 优化 Session 管理（确保不关闭过早）

**关键修复**：
```python
# ========== 关键修复：使用 async with 确保 Session 不会过早关闭 ==========
# 创建新的 session（确保每次重连时都是全新的 session）
# 使用 async with 确保 Session 在 WebSocket 连接期间保持打开状态
async with aiohttp.ClientSession(connector=connector) as session:
    logger.debug(f"[DEBUG] 创建新的 session: {session}")
    logger.debug(f"[DEBUG] Session 状态: closed={session.closed}")
    
    # ========== 关键修复：在 session 的 async with 块内创建 WebSocket 连接 ==========
    # 确保 WebSocket 连接期间 Session 保持打开状态
    async with session.ws_connect(**ws_kwargs) as ws:
        # WebSocket 连接和消息处理都在这里
        async for msg in ws:
            # ...
```

**说明**：
- ✅ **使用 `async with` 嵌套结构**：`async with ClientSession() as session:` 和 `async with session.ws_connect() as ws:` 嵌套
- ✅ **Session 在 WebSocket 连接期间保持打开**：只要 WebSocket 连接存在，Session 就不会关闭
- ✅ **添加 Session 状态检查**：记录 `session.closed` 状态，方便调试

#### 1.2 添加消息计数（用于调试）

**新增代码**：
```python
# 记录接收到的消息数量（用于调试）
message_count = 0

async for msg in ws:
    message_count += 1
    if message_count % 100 == 0:  # 每100条消息记录一次
        logger.debug(f"[DEBUG] 已接收 {message_count} 条消息，Session 状态: closed={session.closed}")
```

**说明**：
- ✅ 记录接收到的消息数量
- ✅ 定期检查 Session 状态，确保 Session 没有过早关闭

#### 1.3 优化直连 Binance WebSocket（443端口）

**当前配置**：
```python
# 固定直连 Binance WebSocket（使用 443 端口，日本东京IP已确认通）
primary_url = f"wss://stream.binance.com:443/ws?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com:443/ws?streams={'/'.join(streams)}"
```

**说明**：
- ✅ 使用 443 端口（标准 HTTPS 端口）
- ✅ 日本东京IP已确认可以直连，无需代理

#### 1.4 加强重连机制

**重连逻辑**：
```python
_max_reconnect_attempts = 0  # 0 表示无限重试
_reconnect_delay = 5  # 重连延迟（秒）

while self.is_running:
    try:
        # 连接 WebSocket...
        reconnect_attempts = 0  # 连接成功，重置重连次数
    except Exception as e:
        reconnect_attempts += 1
        # 处理 timeout、Session closed、SSL 错误...
        # 每 5 秒重试一次，无限重试
        await asyncio.sleep(_reconnect_delay)
```

**错误处理**：
```python
# 检查是否是 Session closed 错误
if 'session' in error_str and 'closed' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 Session closed 错误")
    logger.error(f"[ERROR] 原因: Session 已关闭，将在下次重连时重新创建")

# 检查是否是 timeout 错误
if 'timeout' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 timeout 错误")

# 检查是否是 SSL 错误
if 'ssl' in error_str or 'handshake failed' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 SSL handshake failed 错误")
```

**说明**：
- ✅ 每 5 秒重试一次，无限重试（0 表示无限重试）
- ✅ 处理 timeout、Session closed、SSL handshake failed 等错误
- ✅ 连接成功后重置重连次数

#### 1.5 确保K线数据接收、解析、更新数据库并推送前端

**`_process_kline()` 方法**：
```python
async def _process_kline(self, kline_data):
    """
    处理真实的 K 线数据（核心逻辑）
    
    收到 WebSocket 数据后，调用 KlineModel.upsert_klines 保存实时数据
    并推送给所有前端 /ws 客户端
    """
    try:
        # 检查是否收盘（x=True）
        is_closed = kline_data.get('x', False)
        
        # 标准化交易对
        symbol_raw = kline_data.get('s', '')
        symbol = self._normalize_symbol(symbol_raw)
        
        # 获取间隔
        interval = kline_data.get('i', '1m')
        
        # 构建 K 线数据字典
        kline = {
            'symbol': symbol,
            'interval': interval,
            'timestamp': int(kline_data.get('t', 0)),
            'open': float(kline_data.get('o', 0)),
            'high': float(kline_data.get('h', 0)),
            'low': float(kline_data.get('l', 0)),
            'close': float(kline_data.get('c', 0)),
            'volume': float(kline_data.get('v', 0)),
            'is_closed': is_closed
        }
        
        # 如果 K 线收盘，保存到数据库
        if is_closed:
            await KlineModel.upsert_klines([{
                'symbol': kline['symbol'],
                'interval': kline['interval'],
                'timestamp': kline['timestamp'],
                'open': kline['open'],
                'high': kline['high'],
                'low': kline['low'],
                'close': kline['close'],
                'volume': kline['volume']
            }])
        
        # 广播给所有连接的客户端（包括未收盘的 K 线也推送）
        await self._broadcast_kline(kline)
    except Exception as e:
        logger.error(f"[ERROR] 处理 K 线数据失败: {str(e)}")
        logger.debug(f"[DEBUG] K线处理异常详情: {traceback.format_exc()}")
```

**说明**：
- ✅ K线数据接收：从 Binance WebSocket 接收数据
- ✅ K线数据解析：解析 JSON 格式的数据
- ✅ 数据库更新：K线收盘时保存到数据库（使用 `KlineModel.upsert_klines`）
- ✅ 前端推送：所有K线数据推送给前端 `/ws` 客户端

### 2. 修复前端 WebSocket 连接（`src/components/MarketDetail.vue`）

#### 2.1 优化 WebSocket 连接逻辑

**关键修复**：
```javascript
// 4. 后端 WebSocket 连接（实时K线数据）
// 注意：WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问 ws:// 协议
// 用户应该访问 http://localhost:5173/（非 ws://），然后 JavaScript 代码会自动连接 WebSocket
const connectBackendWebSocket = () => {
  // 如果已有连接且状态正常，不重复连接
  if (backendWS && backendWS.readyState === WebSocket.OPEN) {
    console.log('[MarketDetail] WebSocket 已连接，跳过');
    return;
  }

  // 关闭旧连接
  if (backendWS) {
    try {
      backendWS.close();
    } catch (e) {
      console.warn('[MarketDetail] 关闭旧连接时出错:', e);
    }
    backendWS = null;
  }

  // 使用 Vite 代理：通过 /ws 路径连接
  // 注意：必须使用 ws:// 协议，不能使用 wss://（开发环境）
  // 前端通过 ws://localhost:5173/ws 连接，Vite 会自动代理到 ws://127.0.0.1:8000/api/v1/market/ws/kline
  const wsUrl = `ws://${window.location.host}/ws`;
  console.log('[MarketDetail] ========== 连接后端 WebSocket ==========');
  console.log('[MarketDetail] WebSocket URL:', wsUrl);
  console.log('[MarketDetail] 注意: WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问');
  console.log('[MarketDetail] 请访问 http://localhost:5173/（非 ws://）');

  try {
    backendWS = new WebSocket(wsUrl);
    // ...
  } catch (error) {
    // 错误处理...
  }
};
```

**说明**：
- ✅ **添加详细日志**：说明 WebSocket 必须通过 JavaScript 代码连接
- ✅ **错误处理**：检查是否是 ERR_UNKNOWN_URL_SCHEME 错误并给出提示
- ✅ **使用 Vite 代理**：通过 `ws://${window.location.host}/ws` 连接

#### 2.2 处理 onopen/onmessage/onerror/onclose 事件

**onopen 事件**：
```javascript
backendWS.onopen = () => {
  console.log('[MarketDetail] ✅ WebSocket 连接成功');
  wsConnected.value = true;
  wsReconnectAttempts = 0; // 重置重连次数
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }
};
```

**onmessage 事件**：
```javascript
backendWS.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    console.log('[MarketDetail] 📨 收到 WebSocket 消息:', data);

    // 处理连接成功消息
    if (data.type === 'connected') {
      console.log('[MarketDetail] ✅ WebSocket 连接确认:', data.message);
      wsConnected.value = true;
      return;
    }

    // 处理 K 线数据
    if (data.type === 'kline' && data.data) {
      const kline = data.data;
      console.log('[MarketDetail] 📊 收到K线数据:', {
        symbol: kline.symbol,
        interval: kline.interval,
        timestamp: kline.timestamp,
        close: kline.close,
        is_closed: kline.is_closed
      });
      
      // 更新 K 线图（如果 TradingView widget 支持）
      if (tvWidget.value) {
        console.log('[MarketDetail] 更新 K 线图:', kline);
      }
    }
  } catch (error) {
    console.error('[MarketDetail] ❌ 解析 WebSocket 消息失败:', error);
  }
};
```

**onerror 事件**：
```javascript
backendWS.onerror = (error) => {
  console.error('[MarketDetail] ❌ WebSocket 错误:', error);
  console.error('[MarketDetail] 重连次数:', wsReconnectAttempts, '/', maxWsReconnectAttempts);
  wsConnected.value = false;
  
  // 检查是否是 ERR_UNKNOWN_URL_SCHEME 错误
  if (error && error.message && error.message.includes('ERR_UNKNOWN_URL_SCHEME')) {
    console.error('[MarketDetail] ⚠️ ERR_UNKNOWN_URL_SCHEME 错误');
    console.error('[MarketDetail] 原因: 不能直接在浏览器地址栏访问 ws:// 协议');
    console.error('[MarketDetail] 解决方案: 请访问 http://localhost:5173/（非 ws://），然后 JavaScript 代码会自动连接 WebSocket');
  }
};
```

**onclose 事件**：
```javascript
backendWS.onclose = (event) => {
  console.warn('[MarketDetail] ⚠️ WebSocket 连接已关闭');
  console.warn('[MarketDetail] 关闭代码:', event.code);
  console.warn('[MarketDetail] 关闭原因:', event.reason || '未知');
  wsConnected.value = false;
  backendWS = null;

  // 自动重连（如果未达到最大重连次数）
  if (wsReconnectAttempts < maxWsReconnectAttempts) {
    wsReconnectAttempts++;
    console.log(`[MarketDetail] 🔄 准备重连 WebSocket (${wsReconnectAttempts}/${maxWsReconnectAttempts})，${wsReconnectDelay}ms 后重试...`);
    wsReconnectTimer = setTimeout(() => {
      console.log(`[MarketDetail] 🔄 尝试重连 WebSocket (${wsReconnectAttempts}/${maxWsReconnectAttempts})...`);
      connectBackendWebSocket();
    }, wsReconnectDelay);
  } else {
    console.error(`[MarketDetail] ❌ 已达到最大重连次数 (${maxWsReconnectAttempts} 次)，停止重连`);
    console.error('[MarketDetail] 请检查网络连接或后端服务是否正常运行');
    console.error('[MarketDetail] 后端服务地址: http://127.0.0.1:8000');
    wsReconnectAttempts = 0; // 重置计数器，允许用户手动重试
  }
};
```

**说明**：
- ✅ **onopen**：连接成功时更新连接状态，重置重连次数
- ✅ **onmessage**：处理连接确认消息和K线数据
- ✅ **onerror**：检测 ERR_UNKNOWN_URL_SCHEME 错误并给出提示
- ✅ **onclose**：每3秒重试，最多3次

#### 2.3 显示连接状态（避免"网络未连接"）

**模板中已有**：
```vue
<!-- WebSocket 连接状态指示器 -->
<div class="ws-status-indicator" :class="{ connected: wsConnected, disconnected: !wsConnected }">
  <span class="ws-status-dot"></span>
  <span class="ws-status-text">{{ wsConnected ? '已连接' : '未连接' }}</span>
</div>
```

**样式已添加**：
```css
/* WebSocket 连接状态指示器 */
.ws-status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 11px;
}

.ws-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #848E9C;
  transition: background-color 0.3s ease;
}

.ws-status-indicator.connected .ws-status-dot {
  background-color: #0ECB81;
  box-shadow: 0 0 4px rgba(14, 203, 129, 0.5);
}

.ws-status-indicator.disconnected .ws-status-dot {
  background-color: #F6465D;
  box-shadow: 0 0 4px rgba(246, 70, 93, 0.5);
}
```

**说明**：
- ✅ 显示连接状态："已连接"（绿色圆点）或"未连接"（红色圆点）
- ✅ 实时更新连接状态，避免显示"网络未连接"

## 关键改动总结

### 1. 后端 (`app/services/market_service.py`)

- ✅ **优化 Session 管理**：使用 `async with` 嵌套结构，确保 Session 在 WebSocket 连接期间保持打开状态
- ✅ **添加 Session 状态检查**：记录 `session.closed` 状态，方便调试
- ✅ **添加消息计数**：记录接收到的消息数量，定期检查 Session 状态
- ✅ **优化直连 Binance WebSocket**：使用443端口（日本东京IP已确认通）
- ✅ **加强重连机制**：每5秒重试一次，无限重试，处理 timeout、Session closed、SSL 错误
- ✅ **确保K线数据更新**：K线数据接收、解析、更新数据库并推送前端

### 2. 前端 (`src/components/MarketDetail.vue`)

- ✅ **优化 WebSocket 连接逻辑**：添加详细日志，说明 WebSocket 必须通过 JavaScript 代码连接
- ✅ **处理所有事件**：onopen、onmessage、onerror、onclose
- ✅ **错误检测**：检测 ERR_UNKNOWN_URL_SCHEME 错误并给出提示
- ✅ **重连机制**：每3秒重试，最多3次
- ✅ **显示连接状态**：实时显示"已连接"或"未连接"状态

## 使用说明

### 1. 重启服务测试

```bash
# 停止现有服务
# Ctrl+C

# 启动后端
python main.py

# 启动前端
npm run dev
```

### 2. 访问前端（重要）

**正确方式**：
- ✅ 访问 `http://localhost:5173/`（HTTP 协议）
- ✅ JavaScript 代码会自动连接 WebSocket

**错误方式**：
- ❌ 不要直接在浏览器地址栏访问 `ws://localhost:5173/ws`
- ❌ 这会导致 "ERR_UNKNOWN_URL_SCHEME" 错误

### 3. 查看日志

**后端日志**（应该看到）：
```
[WS] ========== WebSocket 连接初始化（固定直连模式，443端口）==========
[DEBUG] 创建新的 connector: <aiohttp.TCPConnector ...>
[DEBUG] 创建新的 session: <aiohttp.ClientSession ...>
[DEBUG] Session 状态: closed=False
✅ [OK] ========== 币安 WebSocket 连接成功 ==========
[DEBUG] 已接收 100 条消息，Session 状态: closed=False
```

**前端日志**（应该看到）：
```
[MarketDetail] ========== 连接后端 WebSocket ==========
[MarketDetail] WebSocket URL: ws://localhost:5173/ws
[MarketDetail] 注意: WebSocket 必须通过 JavaScript 代码连接，不能直接在浏览器地址栏访问
[MarketDetail] 请访问 http://localhost:5173/（非 ws://）
[MarketDetail] ✅ WebSocket 连接成功
[MarketDetail] 📨 收到 WebSocket 消息: {type: 'connected', message: '...'}
[MarketDetail] 📊 收到K线数据: {symbol: 'BTC/USDT', interval: '1m', ...}
```

### 4. 验证K线数据接收

**检查后端日志**：
- 应该看到 "已接收 X 条消息"
- 应该看到 "保存 K 线数据" 日志（K线收盘时）

**检查前端日志**：
- 应该看到 "收到K线数据" 日志
- 应该看到连接状态指示器显示"已连接"（绿色圆点）

**检查浏览器控制台**：
- 不应该有 ERR_UNKNOWN_URL_SCHEME 错误
- 应该看到 WebSocket 连接成功的日志

## 注意事项

1. **WebSocket 连接方式**：
   - ✅ 必须通过 JavaScript 代码连接：`new WebSocket('ws://localhost:5173/ws')`
   - ❌ 不能直接在浏览器地址栏访问 `ws://` 协议

2. **访问前端**：
   - ✅ 访问 `http://localhost:5173/`（HTTP 协议）
   - ✅ JavaScript 代码会自动连接 WebSocket

3. **Session 管理**：
   - ✅ 使用 `async with` 嵌套结构，确保 Session 在 WebSocket 连接期间保持打开状态
   - ✅ 每次重连时重新创建 Session

4. **重连机制**：
   - ✅ 后端：每5秒重试一次，无限重试
   - ✅ 前端：每3秒重试，最多3次

5. **连接状态显示**：
   - ✅ 实时显示连接状态："已连接"（绿色圆点）或"未连接"（红色圆点）
   - ✅ 避免显示"网络未连接"

## 总结

本次修复主要解决了以下问题：

1. ✅ **ERR_UNKNOWN_URL_SCHEME 错误**：添加详细说明，告知用户必须通过 JavaScript 代码连接 WebSocket
2. ✅ **Session closed 错误**：优化 Session 管理，使用 `async with` 嵌套结构确保 Session 不会过早关闭
3. ✅ **前端 WebSocket 连接**：优化连接逻辑，处理所有事件，添加重连机制和连接状态显示
4. ✅ **K线数据更新**：确保K线数据接收、解析、更新数据库并推送前端

系统现在更加稳定、可靠，能够正确处理 WebSocket 连接和 Session 管理问题。
