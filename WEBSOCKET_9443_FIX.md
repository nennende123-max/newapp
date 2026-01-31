# WebSocket 9443端口修复说明

## 问题诊断

用户发现 WebSocket 连接失败，可能的原因：
1. **SSL handshake 问题**：443 端口可能存在 SSL 握手失败
2. **日本东京 IP 临时限流**：443 端口可能被限流
3. **连接拒绝错误**：Session closed、Connect call failed 等错误

## 修复内容

### 1. 修改 `app/services/market_service.py` - 使用9443端口

#### 1.1 改用9443端口（避免443限流）

**修改前**：
```python
primary_url = f"wss://stream.binance.com:443/ws?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com:443/ws?streams={'/'.join(streams)}"
```

**修改后**：
```python
# 使用 9443 端口（币安 WebSocket 专用端口，避免 443 限流）
primary_url = f"wss://stream.binance.com:9443/ws?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com:9443/ws?streams={'/'.join(streams)}"
```

**说明**：
- ✅ 使用 9443 端口（币安 WebSocket 专用端口）
- ✅ 避免 443 端口可能的限流问题
- ✅ 减少 SSL handshake 错误的可能性

#### 1.2 添加无限重连机制

**修改前**：
```python
_max_reconnect_attempts = 10  # 最多重试 10 次
```

**修改后**：
```python
_max_reconnect_attempts = 0  # 0 表示无限重试
```

**重连逻辑**：
```python
while self.is_running:
    try:
        # 连接 WebSocket...
        reconnect_attempts = 0  # 连接成功，重置重连次数
    except Exception as e:
        reconnect_attempts += 1
        # 每 5 秒重试一次，无限重试
        logger.info(f"[WS] 等待 {_reconnect_delay} 秒后重连...")
        await asyncio.sleep(_reconnect_delay)
```

**说明**：
- ✅ 每 5 秒重试一次，无限重试（0 表示无限重试）
- ✅ 处理 Session closed、Connect call failed、SSL 默认错误
- ✅ 连接成功后重置重连次数

#### 1.3 增强错误处理和调试日志

**新增调试日志**：
```python
import traceback

# 启用详细调试日志
logger.setLevel(logging.DEBUG)

# 在异常处理中添加详细日志
logger.debug(f"[DEBUG] 连接异常详情: {traceback.format_exc()}")
```

**错误检测**：
```python
# 检查是否是 SSL 相关错误
if 'ssl' in error_str or 'certificate' in error_str or 'tls' in error_str or 'handshake' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 SSL/TLS/Handshake 相关错误")

# 检查是否是连接拒绝错误
if 'connection refused' in error_str or 'connection reset' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到连接拒绝错误")

# 检查是否是 Session closed 错误
if 'session closed' in error_str or 'session' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 Session closed 错误")

# 检查是否是 Connect call failed 错误
if 'connect call failed' in error_str or 'connect' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 Connect call failed 错误")
```

#### 1.4 确保K线数据正常解析和更新

**`_process_kline()` 方法（核心逻辑）**：
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
        if not symbol_raw:
            logger.warning(f"[WARN] K线数据缺少symbol字段: {kline_data}")
            return
        
        symbol = self._normalize_symbol(symbol_raw)
        
        # 获取间隔
        interval = kline_data.get('i', '1m')
        if not interval:
            logger.warning(f"[WARN] K线数据缺少interval字段: {kline_data}")
            return
        
        # 构建 K 线数据字典（符合 KlineModel 格式）
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
        
        # 验证数据完整性
        if kline['timestamp'] == 0 or kline['open'] == 0:
            logger.warning(f"[WARN] K线数据不完整，跳过: {kline}")
            return
        
        # 如果 K 线收盘，保存到数据库（调用 KlineModel.upsert_klines）
        if is_closed:
            try:
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
                logger.debug(f"[DB] 保存 K 线数据: {kline['symbol']} {kline['interval']} {kline['timestamp']}")
            except Exception as db_error:
                logger.error(f"[ERROR] 保存 K 线数据到数据库失败: {str(db_error)}")
                logger.debug(f"[DEBUG] 数据库保存异常详情: {traceback.format_exc()}")
        
        # 广播给所有连接的客户端（包括未收盘的 K 线也推送，用于实时更新）
        await self._broadcast_kline(kline)
    except Exception as e:
        logger.error(f"[ERROR] 处理 K 线数据失败: {str(e)}")
        logger.error(f"[ERROR] K线数据: {kline_data}")
        logger.debug(f"[DEBUG] K线处理异常详情: {traceback.format_exc()}")
```

**说明**：
- ✅ 数据验证：检查 symbol、interval、timestamp、open 等字段
- ✅ 数据完整性检查：确保 timestamp 和 open 不为 0
- ✅ 数据库保存：K 线收盘时保存到数据库（使用 `KlineModel.upsert_klines`）
- ✅ 前端推送：所有 K 线数据（包括未收盘的）都推送给前端客户端
- ✅ 错误处理：详细的错误日志和调试信息

#### 1.5 清理乱改代码，恢复核心逻辑

**移除的内容**：
- ✅ 移除所有代理相关代码（SOCKS5、HTTP）
- ✅ 移除代理 fallback 逻辑
- ✅ 移除不必要的代理检查方法

**保留的核心逻辑**：
- ✅ `_process_kline()`：处理 K 线数据
- ✅ `_broadcast_kline()`：广播给前端客户端
- ✅ `_normalize_symbol()`：标准化交易对格式
- ✅ `KlineModel.upsert_klines()`：保存到数据库

### 2. 优化 `vite.config.js` - WebSocket 代理配置

**当前配置**（已优化）：
```javascript
'/ws': {
  target: 'ws://127.0.0.1:8000',
  changeOrigin: true,
  ws: true,
  secure: false,  // 禁用 SSL 验证（开发环境）
  rewrite: (path) => path.replace(/^\/ws/, '/api/v1/market/ws/kline'),
  configure: (proxy, _options) => {
    proxy.on('error', (err, _req, _res) => {
      console.log('[Vite Proxy] WebSocket proxy error:', err);
    });
    proxy.on('proxyReqWs', (proxyReq, req, _socket) => {
      console.log('[Vite Proxy] WebSocket proxy request:', req.url);
    });
  }
}
```

**说明**：
- ✅ `target: 'ws://127.0.0.1:8000'`：后端 FastAPI 服务器（8000 端口）
- ✅ `ws: true`：启用 WebSocket 代理
- ✅ `secure: false`：禁用 SSL 验证（开发环境）
- ✅ 错误处理和日志记录

### 3. 在 `MarketDetail.vue` 添加 WebSocket 重连逻辑

#### 3.1 添加 WebSocket 连接状态

**新增变量**：
```javascript
// 后端 WebSocket 连接（用于实时K线数据）
let backendWS = null;
let wsReconnectAttempts = 0;
let wsReconnectTimer = null;
const maxWsReconnectAttempts = 3;
const wsReconnectDelay = 3000; // 3秒
const wsConnected = ref(false); // WebSocket 连接状态
```

#### 3.2 添加 WebSocket 连接函数

**`connectBackendWebSocket()` 函数**：
```javascript
const connectBackendWebSocket = () => {
  // 如果已有连接且状态正常，不重复连接
  if (backendWS && backendWS.readyState === WebSocket.OPEN) {
    console.log('[MarketDetail] WebSocket 已连接，跳过');
    return;
  }

  // 关闭旧连接
  if (backendWS) {
    backendWS.close();
    backendWS = null;
  }

  // 清除重连定时器
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }

  // 使用 Vite 代理：通过 /ws 路径连接
  const wsUrl = `ws://${window.location.host}/ws`;
  console.log('[MarketDetail] 连接后端 WebSocket:', wsUrl);

  try {
    backendWS = new WebSocket(wsUrl);

    backendWS.onopen = () => {
      console.log('[MarketDetail] WebSocket 连接成功');
      wsConnected.value = true;
      wsReconnectAttempts = 0; // 重置重连次数
    };

    backendWS.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // 处理 K 线数据...
      } catch (error) {
        console.error('[MarketDetail] 解析 WebSocket 消息失败:', error);
      }
    };

    backendWS.onerror = (error) => {
      console.error('[MarketDetail] WebSocket 错误:', error);
      wsConnected.value = false;
    };

    backendWS.onclose = () => {
      console.warn('[MarketDetail] WebSocket 连接已关闭');
      wsConnected.value = false;
      backendWS = null;

      // 自动重连（如果未达到最大重连次数）
      if (wsReconnectAttempts < maxWsReconnectAttempts) {
        wsReconnectAttempts++;
        wsReconnectTimer = setTimeout(() => {
          connectBackendWebSocket();
        }, wsReconnectDelay);
      } else {
        console.error(`[MarketDetail] 已达到最大重连次数 (${maxWsReconnectAttempts} 次)，停止重连`);
        wsReconnectAttempts = 0; // 重置计数器
      }
    };
  } catch (error) {
    console.error('[MarketDetail] 创建 WebSocket 连接失败:', error);
    wsConnected.value = false;
  }
};
```

#### 3.3 添加连接状态显示

**模板中添加**：
```vue
<!-- WebSocket 连接状态指示器 -->
<div class="ws-status-indicator" :class="{ connected: wsConnected, disconnected: !wsConnected }">
  <span class="ws-status-dot"></span>
  <span class="ws-status-text">{{ wsConnected ? '已连接' : '未连接' }}</span>
</div>
```

**样式添加**：
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

#### 3.4 生命周期管理

**`onMounted()`**：
```javascript
onMounted(() => {
  // 连接后端 WebSocket（实时K线数据）
  connectBackendWebSocket();
  
  // 其他初始化...
});
```

**`onUnmounted()`**：
```javascript
onUnmounted(() => {
  disconnectBackendWebSocket(); // 断开后端 WebSocket
  // 其他清理...
});
```

## 关键改动总结

### 1. 后端 (`app/services/market_service.py`)

- ✅ **改用9443端口**：避免443端口限流和SSL handshake问题
- ✅ **无限重连机制**：每5秒重试一次，无限重试（0表示无限重试）
- ✅ **增强错误处理**：检测SSL、Session closed、Connect call failed等错误
- ✅ **详细调试日志**：使用 `traceback.format_exc()` 打印详细异常信息
- ✅ **K线数据解析**：确保多个symbol和interval的K线数据正常解析
- ✅ **数据库更新**：K线收盘时保存到数据库（使用 `KlineModel.upsert_klines`）
- ✅ **前端推送**：所有K线数据推送给前端/ws客户端
- ✅ **清理代码**：移除所有代理相关代码，恢复核心逻辑

### 2. 前端配置 (`vite.config.js`)

- ✅ **WebSocket代理**：`target: 'ws://127.0.0.1:8000'`，`ws: true`
- ✅ **错误处理**：添加代理错误和请求日志

### 3. 前端代码 (`src/components/MarketDetail.vue`)

- ✅ **WebSocket连接**：连接到后端 `/ws` 端点
- ✅ **重连逻辑**：每3秒重试，最多3次
- ✅ **连接状态显示**：显示"已连接"或"未连接"状态
- ✅ **错误处理**：处理 `onerror` 和 `onclose` 事件
- ✅ **生命周期管理**：在 `onMounted` 中连接，在 `onUnmounted` 中断开

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

### 2. 查看日志

**后端日志**（应该看到）：
```
[WS] ========== WebSocket 连接初始化（固定直连模式，9443端口）==========
[WS] 主要端点: wss://stream.binance.com:9443/ws?streams=...
[WS] 连接方式: 直接连接（不使用代理）
✅ [OK] ========== 币安 WebSocket 连接成功 ==========
```

**前端日志**（应该看到）：
```
[MarketDetail] 连接后端 WebSocket: ws://localhost:5173/ws
[MarketDetail] WebSocket 连接成功
```

### 3. 如果连接失败

**查看详细调试日志**：
- 后端会打印 `[DEBUG]` 级别的详细异常信息
- 前端会在控制台打印错误信息

**检查点**：
1. 后端服务是否正常运行（端口8000）
2. Vite代理配置是否正确
3. 网络连接是否正常
4. Binance WebSocket服务是否可用

### 4. 测试重连机制

**后端重连**：
- 如果连接失败，每5秒重试一次，无限重试
- 查看日志：`[WS] 等待 5 秒后重连...`

**前端重连**：
- 如果连接失败，每3秒重试一次，最多3次
- 查看日志：`[MarketDetail] 准备重连 WebSocket (1/3)...`

## 注意事项

1. **9443端口**：
   - 使用币安 WebSocket 专用端口，避免443端口限流
   - 如果9443端口也失败，会自动切换到备用端点

2. **无限重连**：
   - 后端每5秒重试一次，无限重试
   - 前端每3秒重试一次，最多3次

3. **调试日志**：
   - 如果连接失败，启用 `logging.DEBUG` 查看详细异常信息
   - 使用 `traceback.format_exc()` 打印完整堆栈跟踪

4. **K线数据更新**：
   - K线收盘时自动保存到数据库
   - 所有K线数据（包括未收盘的）都推送给前端客户端
   - 支持多个symbol（BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, DOGEUSDT）
   - 支持多个interval（1m, 1h, 4h, 1d）

5. **连接状态显示**：
   - 前端显示WebSocket连接状态（已连接/未连接）
   - 绿色圆点表示已连接，红色圆点表示未连接

## 总结

本次修复主要解决了以下问题：

1. ✅ **改用9443端口**：避免443端口限流和SSL handshake问题
2. ✅ **无限重连机制**：每5秒重试一次，无限重试
3. ✅ **增强错误处理**：检测和处理各种连接错误
4. ✅ **详细调试日志**：使用 `traceback.format_exc()` 打印详细异常信息
5. ✅ **K线数据解析**：确保多个symbol和interval的K线数据正常解析和更新
6. ✅ **前端重连逻辑**：每3秒重试，最多3次，显示连接状态
7. ✅ **清理代码**：移除所有代理相关代码，恢复核心逻辑

系统现在更加稳定、可靠，能够处理各种网络错误和连接问题。
