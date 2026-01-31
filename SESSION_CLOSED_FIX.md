# Session is closed 错误修复说明

## 问题诊断

用户遇到 `RuntimeError: Session is closed` 错误，原因是：
1. **Session 关闭过早**：`aiohttp.ClientSession` 在重连循环外部创建，导致重连时使用已关闭的 Session
2. **Connector 复用问题**：connector 在循环外部创建，可能导致资源泄漏

## 修复内容

### 1. 修复 Session 管理（关键修复）

#### 1.1 在重连循环内部创建 Session

**修改前**（错误）：
```python
# connector 在循环外部创建
connector = aiohttp.TCPConnector(ssl=False)
current_url = primary_url

while self.is_running:
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            # 如果重连，connector 可能已关闭
            async with session.ws_connect(**ws_kwargs) as ws:
                # ...
```

**修改后**（正确）：
```python
current_url = primary_url

while self.is_running:
    # ========== 关键修复：在循环内部创建 connector 和 session ==========
    # 确保每次重连时都重新创建 Session，避免 "Session is closed" 错误
    connector = None
    session = None
    
    try:
        # ========== 关键修复：每次重连时重新创建 connector 和 session ==========
        # 创建新的 connector（禁用 SSL 验证以避免 SSL 默认错误）
        connector = aiohttp.TCPConnector(ssl=False)
        logger.debug(f"[DEBUG] 创建新的 connector: {connector}")
        
        # 创建新的 session（确保每次重连时都是全新的 session）
        async with aiohttp.ClientSession(connector=connector) as session:
            logger.debug(f"[DEBUG] 创建新的 session: {session}")
            
            async with session.ws_connect(**ws_kwargs) as ws:
                # ...
```

**说明**：
- ✅ **每次重连时重新创建 connector**：避免使用已关闭的 connector
- ✅ **每次重连时重新创建 session**：确保 session 是全新的，不会出现 "Session is closed" 错误
- ✅ **使用 `async with` 确保资源正确释放**：当 `async with` 块退出时，session 和 connector 会自动关闭

#### 1.2 添加资源清理逻辑

**新增代码**：
```python
except Exception as e:
    # ... 错误处理 ...
    
    # 清理资源
    if connector:
        try:
            await connector.close()
            logger.debug(f"[DEBUG] 已关闭 connector")
        except Exception as close_error:
            logger.debug(f"[DEBUG] 关闭 connector 时出错: {close_error}")
```

**说明**：
- ✅ 在异常处理中清理 connector 资源
- ✅ 确保 connector 正确关闭，避免资源泄漏

### 2. 改用443端口（日本东京IP已确认通）

**修改前**：
```python
primary_url = f"wss://stream.binance.com:9443/ws?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com:9443/ws?streams={'/'.join(streams)}"
```

**修改后**：
```python
# 固定直连 Binance WebSocket（使用 443 端口，日本东京IP已确认通）
# 主要端点：wss://stream.binance.com:443/ws
# 备用端点：wss://fstream.binance.com:443/ws（期货）
primary_url = f"wss://stream.binance.com:443/ws?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com:443/ws?streams={'/'.join(streams)}"
```

**说明**：
- ✅ 使用 443 端口（标准 HTTPS 端口）
- ✅ 日本东京IP已确认可以直连，无需代理

### 3. 加强无限重连机制

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
        # 处理各种错误...
        # 每 5 秒重试一次，无限重试
        await asyncio.sleep(_reconnect_delay)
```

**错误处理**：
```python
# 检查是否是 Session closed 错误
if 'session' in error_str and 'closed' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 Session closed 错误")
    logger.error(f"[ERROR] 原因: Session 已关闭，将在下次重连时重新创建")

# 检查是否是 SSL handshake failed 错误
if 'handshake failed' in error_str or 'handshake' in error_str:
    logger.error(f"[ERROR] ⚠️ 检测到 SSL handshake failed 错误")

# 检查是否是 Connect call failed 错误
if 'connect call failed' in error_str or ('connect' in error_str and 'failed' in error_str):
    logger.error(f"[ERROR] ⚠️ 检测到 Connect call failed 错误")
```

**说明**：
- ✅ 每 5 秒重试一次，无限重试（0 表示无限重试）
- ✅ 处理 Session closed、SSL handshake failed、Connect call failed 等错误
- ✅ 连接成功后重置重连次数

### 4. 添加详细调试日志

**日志配置**：
```python
import logging
import traceback

# ========== 配置日志 ==========
logging.basicConfig(
    level=logging.DEBUG,  # 启用DEBUG级别日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 确保DEBUG级别日志被打印
```

**详细调试日志**：
```python
# 在异常处理中添加详细日志
logger.debug(f"[DEBUG] WebSocket error: {e}")
logger.debug(f"[DEBUG] 连接异常详情: {traceback.format_exc()}")

# 在关键步骤添加调试日志
logger.debug(f"[DEBUG] 创建新的 connector: {connector}")
logger.debug(f"[DEBUG] 创建新的 session: {session}")
logger.debug(f"[DEBUG] WebSocket 连接参数: {ws_kwargs}")
logger.debug(f"[DEBUG] 处理K线数据: symbol={symbol}, interval={interval}, timestamp={kline['timestamp']}, is_closed={is_closed}")
```

**说明**：
- ✅ 启用 DEBUG 级别日志
- ✅ 使用 `traceback.format_exc()` 打印完整堆栈跟踪
- ✅ 在关键步骤添加调试日志，方便排查问题

### 5. 确保K线订阅更新数据库并推送前端

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
- ✅ K线收盘时（`is_closed=True`）自动保存到数据库
- ✅ 所有K线数据（包括未收盘的）都推送给前端客户端
- ✅ 支持多个symbol（BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, DOGEUSDT）
- ✅ 支持多个interval（1m, 1h, 4h, 1d）

## 关键改动总结

### 1. Session 管理修复（核心修复）

- ✅ **在重连循环内部创建 connector 和 session**：确保每次重连时都是全新的
- ✅ **使用 `async with` 确保资源正确释放**：当块退出时自动关闭
- ✅ **添加资源清理逻辑**：在异常处理中清理 connector 资源

### 2. 端口变更

- ✅ **改用443端口**：日本东京IP已确认通，无需代理

### 3. 无限重连机制

- ✅ **每5秒重试一次，无限重试**：0 表示无限重试
- ✅ **处理各种错误**：Session closed、SSL handshake failed、Connect call failed

### 4. 详细调试日志

- ✅ **启用DEBUG级别日志**：`logging.basicConfig(level=logging.DEBUG)`
- ✅ **使用 `traceback.format_exc()`**：打印完整堆栈跟踪
- ✅ **在关键步骤添加调试日志**：方便排查问题

### 5. K线数据更新

- ✅ **K线收盘时保存到数据库**：使用 `KlineModel.upsert_klines`
- ✅ **所有K线数据推送给前端**：包括未收盘的K线也推送

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

### 2. 测试直连（使用 wscat）

```bash
# 测试单个流
wscat -c "wss://stream.binance.com:443/ws/btcusdt@kline_1m"

# 测试组合流
wscat -c "wss://stream.binance.com:443/ws?streams=btcusdt@kline_1m/ethusdt@kline_1m"
```

**预期输出**：
```
Connected (press CTRL+C to quit)
< {"stream":"btcusdt@kline_1m","data":{"e":"kline","E":1234567890,"s":"BTCUSDT","k":{...}}}
```

### 3. 查看日志

**后端日志**（应该看到）：
```
[WS] ========== WebSocket 连接初始化（固定直连模式，443端口）==========
[WS] 主要端点: wss://stream.binance.com:443/ws?streams=...
[DEBUG] 创建新的 connector: <aiohttp.TCPConnector ...>
[DEBUG] 创建新的 session: <aiohttp.ClientSession ...>
✅ [OK] ========== 币安 WebSocket 连接成功 ==========
```

**如果连接失败**（应该看到详细调试信息）：
```
[ERROR] ========== WebSocket 连接断开 ==========
[ERROR] 异常类型: RuntimeError
[ERROR] 异常信息: Session is closed
[DEBUG] WebSocket error: Session is closed
[DEBUG] 连接异常详情: Traceback (most recent call last):
  ...
[ERROR] ⚠️ 检测到 Session closed 错误
[ERROR] 原因: Session 已关闭，将在下次重连时重新创建
```

### 4. 验证K线数据更新

**检查数据库**：
- K线收盘时应该保存到数据库
- 使用 SQLite 工具查看 `data/kline.db` 文件

**检查前端推送**：
- 前端连接的 `/ws` 客户端应该收到K线数据
- 查看浏览器控制台，应该看到K线数据消息

## 注意事项

1. **Session 管理**：
   - ✅ 每次重连时都重新创建 Session
   - ✅ 使用 `async with` 确保资源正确释放
   - ✅ 在异常处理中清理 connector 资源

2. **443端口**：
   - ✅ 使用标准 HTTPS 端口
   - ✅ 日本东京IP已确认可以直连

3. **无限重连**：
   - ✅ 每5秒重试一次，无限重试
   - ✅ 处理 Session closed、SSL handshake failed、Connect call failed 等错误

4. **调试日志**：
   - ✅ 启用 DEBUG 级别日志
   - ✅ 使用 `traceback.format_exc()` 打印完整堆栈跟踪
   - ✅ 如果连接失败，查看详细调试信息

5. **K线数据更新**：
   - ✅ K线收盘时自动保存到数据库
   - ✅ 所有K线数据推送给前端客户端
   - ✅ 支持多个symbol和interval

## 总结

本次修复主要解决了 `RuntimeError: Session is closed` 错误：

1. ✅ **修复Session管理**：在重连循环内部创建 Session，确保每次重连时都是全新的
2. ✅ **改用443端口**：日本东京IP已确认通，无需代理
3. ✅ **加强无限重连**：每5秒重试一次，处理各种错误
4. ✅ **添加详细调试日志**：使用 `traceback.format_exc()` 打印完整堆栈跟踪
5. ✅ **确保K线数据更新**：K线收盘时保存到数据库，所有K线数据推送给前端

系统现在更加稳定、可靠，能够正确处理 Session 关闭和重连问题。
