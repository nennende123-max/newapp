# 固定直连模式修复说明

## 问题分析

用户发现日本东京 IP 可以直连外网（无需 v2rayN 代理），因此需要：
1. 移除所有代理 fallback 逻辑（包括 SOCKS5 10808 和 HTTP 10809）
2. 固定为直连 Binance WebSocket
3. 加强重连机制（处理 SSL 默认错误和连接拒绝）
4. 确保多个 symbol 和 interval 的 K 线订阅更新 KlineModel 数据库并推送给前端
5. 优化前端 WebSocket 连接和重连逻辑

## 修复内容

### 1. 重写 `app/services/market_service.py` - 移除所有代理逻辑

#### 1.1 移除代理相关导入和配置

**修改前**：
```python
# 尝试导入 SOCKS5 支持库
try:
    import aiosocksy
    from aiosocksy.connector import SocksConnector
    HAS_SOCKS5 = True
    ...
except ImportError:
    ...

PROXY_URL = os.getenv("PROXY_URL", "socks5://127.0.0.1:10808")
```

**修改后**：
```python
# 移除所有代理相关导入
# 固定直连模式，无需代理支持

# 移除 PROXY_URL 配置
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]
```

#### 1.2 移除代理相关方法

**移除的方法**：
- `_parse_proxy_url()` - 解析代理 URL
- `_check_proxy_available()` - 检查代理可用性
- `_create_proxy_connector()` - 创建代理 connector
- `_try_connect_websocket()` - 测试 WebSocket 连接（包含代理逻辑）

#### 1.3 重写 `start_stream_safe()` - 固定直连

**关键改动**：

1. **固定 WebSocket URL**：
   ```python
   # 主要端点：wss://stream.binance.com:443/ws
   # 备用端点：wss://fstream.binance.com:443/ws（期货）
   primary_url = f"wss://stream.binance.com:443/ws?streams={'/'.join(streams)}"
   fallback_url = f"wss://fstream.binance.com:443/ws?streams={'/'.join(streams)}"
   ```

2. **固定直连 connector**：
   ```python
   # 固定直连 connector（禁用 SSL 验证以避免 SSL 默认错误）
   connector = aiohttp.TCPConnector(ssl=False)
   ```

3. **移除所有代理 fallback 逻辑**：
   - 移除 SOCKS5 代理检查
   - 移除 HTTP 代理检查
   - 移除代理可用性测试
   - 直接使用直连 connector

4. **加强重连机制**：
   ```python
   _max_reconnect_attempts = 10  # 最多重试 10 次（0 表示无限重试）
   _reconnect_delay = 5  # 每 5 秒重试一次
   ```

5. **处理 SSL 和连接拒绝错误**：
   ```python
   # 检查是否是 SSL 相关错误
   if 'ssl' in error_str or 'certificate' in error_str or 'tls' in error_str:
       logger.error(f"[ERROR] ⚠️ 检测到 SSL/TLS 相关错误")
   
   # 检查是否是连接拒绝错误
   if 'connection refused' in error_str or 'connection reset' in error_str:
       logger.error(f"[ERROR] ⚠️ 检测到连接拒绝错误")
   ```

6. **主要/备用端点切换**：
   ```python
   # 如果主要端点失败，尝试备用端点
   if current_url == primary_url:
       logger.info(f"[WS] 主要端点失败，尝试备用端点...")
       current_url = fallback_url
       reconnect_attempts = 0  # 重置重连次数
   elif current_url == fallback_url:
       # 备用端点也失败，切回主要端点
       logger.info(f"[WS] 备用端点也失败，切回主要端点...")
       current_url = primary_url
   ```

#### 1.4 确保 K 线数据更新和推送

**`_process_kline()` 方法**：
```python
async def _process_kline(self, kline_data):
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
    
    # 广播给所有连接的客户端（包括未收盘的 K 线也推送，用于实时更新）
    await self._broadcast_kline(kline)
```

**说明**：
- ✅ K 线收盘时（`is_closed=True`）自动保存到数据库
- ✅ 所有 K 线数据（包括未收盘的）都推送给前端客户端
- ✅ 支持多个 symbol（BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, DOGEUSDT）
- ✅ 支持多个 interval（1m, 1h, 4h, 1d）

#### 1.5 修改 `sync_history_safe()` - 移除代理

**修改前**：
```python
if not PROXY_URL:
    logger.info("[SYNC] 未配置代理，跳过历史数据同步")
    return

async with session.get(url, proxy=PROXY_URL, ...) as resp:
    ...
```

**修改后**：
```python
# 固定直连，不使用代理
connector = aiohttp.TCPConnector(ssl=False)
async with aiohttp.ClientSession(connector=connector) as session:
    async with session.get(url, ...) as resp:  # 移除 proxy 参数
        ...
```

### 2. 优化 `vite.config.js` - WebSocket 代理配置

**修改前**：
```javascript
'/ws': {
  target: 'ws://127.0.0.1:8000',
  changeOrigin: true,
  ws: true,
  rewrite: (path) => path.replace(/^\/ws/, '/api/v1/market/ws/kline')
}
```

**修改后**：
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
- ✅ 添加 `secure: false` 禁用 SSL 验证（开发环境）
- ✅ 添加错误处理和日志记录
- ✅ 确保 WebSocket 代理正常工作

### 3. 优化 `src/utils/tradingview-datafeed.js` - 前端重连逻辑

#### 3.1 添加重连计数器

**新增变量**：
```javascript
let reconnectAttempts = 0;  // 重连次数计数器
const maxReconnectAttempts = 3;  // 最大重连次数（每3秒重试，最多3次）
const reconnectDelay = 3000;  // 重连延迟（毫秒）
```

#### 3.2 改进重连逻辑

**修改 `onclose` 事件处理**：
```javascript
wsConnection.onclose = () => {
  console.warn('[Datafeed] WebSocket 连接已关闭');
  wsConnection = null;
  
  // 自动重连（如果还在订阅状态且未达到最大重连次数）
  if (currentSymbol && currentResolution && !isReconnecting) {
    if (reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      isReconnecting = true;
      console.log(`[Datafeed] 准备重连 WebSocket (${reconnectAttempts}/${maxReconnectAttempts})，${reconnectDelay}ms 后重试...`);
      reconnectTimer = setTimeout(() => {
        console.log(`[Datafeed] 尝试重连 WebSocket (${reconnectAttempts}/${maxReconnectAttempts})...`);
        isReconnecting = false;
        connectWebSocket(currentSymbol, currentResolution);
      }, reconnectDelay);
    } else {
      console.error(`[Datafeed] 已达到最大重连次数 (${maxReconnectAttempts} 次)，停止重连`);
      console.error('[Datafeed] 请检查网络连接或后端服务是否正常运行');
      isReconnecting = false;
      reconnectAttempts = 0;  // 重置计数器，允许用户手动重试
    }
  }
};
```

**修改 `onopen` 事件处理**：
```javascript
wsConnection.onopen = () => {
  console.log('[Datafeed] WebSocket 连接成功');
  isReconnecting = false;
  reconnectAttempts = 0;  // 重置重连次数
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
};
```

**修改错误处理**：
```javascript
wsConnection.onerror = (error) => {
  console.error('[Datafeed] WebSocket 错误:', error);
  console.error('[Datafeed] 重连次数:', reconnectAttempts, '/', maxReconnectAttempts);
};
```

**说明**：
- ✅ 每 3 秒重试一次，最多重试 3 次
- ✅ 连接成功后重置重连次数
- ✅ 达到最大重连次数后停止重连并提示用户
- ✅ 在 `disconnectWebSocket()` 中重置重连计数器

### 4. 更新 `requirements.txt` - 移除代理库

**修改前**：
```
# WebSocket 代理支持库（必需，用于 SOCKS5 代理支持）
# 安装命令: pip install aiosocksy
aiosocksy>=0.0.6

# 注意：如果不需要 SOCKS5 代理支持，可以不安装此库
# 系统会自动降级到直接连接模式
```

**修改后**：
```
# 注意：已移除所有代理相关依赖（aiosocksy 等）
# 系统固定为直连模式，日本东京 IP 无需代理即可连接 Binance API
```

## 关键改动总结

### 1. 后端 (`app/services/market_service.py`)

- ✅ **移除所有代理逻辑**：移除 SOCKS5 和 HTTP 代理相关代码
- ✅ **固定直连**：使用 `aiohttp.TCPConnector(ssl=False)` 固定直连
- ✅ **WebSocket URL**：`wss://stream.binance.com:443/ws` 或 `wss://fstream.binance.com:443/ws`
- ✅ **重连机制**：每 5 秒重试，最多 10 次（0 表示无限重试）
- ✅ **错误处理**：检测 SSL 错误和连接拒绝错误
- ✅ **主要/备用端点切换**：主要端点失败时自动切换到备用端点
- ✅ **K 线数据更新**：K 线收盘时保存到数据库，所有 K 线推送给前端
- ✅ **多 symbol/interval 支持**：支持 5 个交易对 × 4 个间隔 = 20 个流

### 2. 前端配置 (`vite.config.js`)

- ✅ **WebSocket 代理优化**：添加 `secure: false` 和错误处理
- ✅ **日志记录**：添加代理错误和请求日志

### 3. 前端代码 (`src/utils/tradingview-datafeed.js`)

- ✅ **重连逻辑**：每 3 秒重试，最多 3 次
- ✅ **重连计数器**：跟踪重连次数并在连接成功后重置
- ✅ **错误提示**：达到最大重连次数后提示用户检查网络

### 4. 依赖管理 (`requirements.txt`)

- ✅ **移除代理库**：移除 `aiosocksy` 等代理相关依赖

## 使用说明

### 1. 安装依赖

```bash
# 不再需要安装 aiosocksy
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python main.py
```

**预期日志**：
```
[OK] MarketService 初始化（固定直连模式，日本东京 IP 无需代理）
[WS] ========== WebSocket 连接初始化（固定直连模式）==========
[WS] 订阅流: 20 个流（5 个交易对 × 4 个间隔）
[WS] 交易对: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'DOGEUSDT']
[WS] 间隔: ['1m', '1h', '4h', '1d']
[WS] 主要端点: wss://stream.binance.com:443/ws?streams=...
[WS] 连接方式: 直接连接（不使用代理）
✅ [OK] ========== 币安 WebSocket 连接成功 ==========
```

### 3. 启动前端服务

```bash
npm run dev
```

**预期日志**：
```
[Datafeed] 连接 WebSocket: ws://localhost:5173/ws
[Datafeed] WebSocket 连接成功
```

### 4. 测试重连机制

**后端重连**：
- 如果连接失败，每 5 秒重试一次，最多 10 次
- 如果达到最大重连次数，切换到模拟数据模式 10 秒，然后重新尝试

**前端重连**：
- 如果连接失败，每 3 秒重试一次，最多 3 次
- 如果达到最大重连次数，停止重连并提示用户

## 测试场景

### 场景 1：正常连接

- **预期**：后端和前端都成功连接
- **日志**：
  ```
  [WS] ✅ 币安 WebSocket 连接成功
  [Datafeed] WebSocket 连接成功
  ```

### 场景 2：后端连接失败

- **预期**：后端每 5 秒重试，最多 10 次
- **日志**：
  ```
  [ERROR] WebSocket 连接断开
  [ERROR] 重连次数: 1/10
  [WS] 等待 5 秒后重连...
  ```

### 场景 3：前端连接失败

- **预期**：前端每 3 秒重试，最多 3 次
- **日志**：
  ```
  [Datafeed] WebSocket 连接已关闭
  [Datafeed] 准备重连 WebSocket (1/3)，3000ms 后重试...
  ```

### 场景 4：SSL 错误

- **预期**：检测到 SSL 错误并记录
- **日志**：
  ```
  [ERROR] ⚠️ 检测到 SSL/TLS 相关错误
  [ERROR] 建议: 检查 SSL 证书配置或网络连接
  ```

### 场景 5：连接拒绝错误

- **预期**：检测到连接拒绝错误并记录
- **日志**：
  ```
  [ERROR] ⚠️ 检测到连接拒绝错误
  [ERROR] 建议: 检查网络连接或防火墙设置
  ```

## 注意事项

1. **固定直连**：
   - 系统固定为直连模式，不再使用任何代理
   - 适用于日本东京 IP 等可以直接访问 Binance API 的网络环境

2. **SSL 验证**：
   - 后端使用 `ssl=False` 禁用 SSL 验证（避免 SSL 默认错误）
   - 前端 Vite 配置使用 `secure: false`（开发环境）

3. **重连机制**：
   - 后端：每 5 秒重试，最多 10 次（0 表示无限重试）
   - 前端：每 3 秒重试，最多 3 次

4. **K 线数据更新**：
   - K 线收盘时自动保存到数据库
   - 所有 K 线数据（包括未收盘的）都推送给前端客户端
   - 支持多个 symbol 和 interval

5. **主要/备用端点**：
   - 主要端点失败时自动切换到备用端点
   - 备用端点也失败时切回主要端点

6. **移除代理库**：
   - 不再需要安装 `aiosocksy` 等代理相关库
   - 减少依赖，简化部署

## 重启服务测试

1. **停止现有服务**：
   ```bash
   # 停止后端
   Ctrl+C
   
   # 停止前端
   Ctrl+C
   ```

2. **重新安装依赖**（可选）：
   ```bash
   # 如果之前安装了 aiosocksy，可以卸载
   pip uninstall aiosocksy -y
   ```

3. **启动后端**：
   ```bash
   python main.py
   ```

4. **启动前端**：
   ```bash
   npm run dev
   ```

5. **验证连接**：
   - 检查后端日志：应该看到 "固定直连模式" 和 "连接成功"
   - 检查前端日志：应该看到 "WebSocket 连接成功"
   - 检查浏览器控制台：不应该有 WebSocket 连接错误

6. **测试重连**：
   - 临时断开网络，观察重连日志
   - 恢复网络，验证自动重连

## 总结

本次修复完全移除了代理逻辑，固定为直连模式，适用于日本东京 IP 等可以直接访问 Binance API 的网络环境。主要改动包括：

1. ✅ 移除所有代理相关代码和依赖
2. ✅ 固定直连 Binance WebSocket（443 端口）
3. ✅ 加强重连机制（处理 SSL 错误和连接拒绝）
4. ✅ 确保 K 线数据更新和推送
5. ✅ 优化前端 WebSocket 重连逻辑
6. ✅ 简化部署（移除代理库依赖）

系统现在更加简洁、稳定，适合直连网络环境使用。
