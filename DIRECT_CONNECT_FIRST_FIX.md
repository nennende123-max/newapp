# WebSocket 直连优先修复说明

## 问题分析

1. **代理连接失败**：SOCKS5 10808 和 HTTP 10809 都失败，最终直连也失败
2. **连接策略不合理**：优先使用代理，但日本东京 IP 可以直连 Binance API
3. **缺少详细日志**：无法诊断连接失败的具体原因
4. **重连机制不完善**：没有明确的重连次数限制

## 修复内容

### 1. 修改代理配置（去掉 HTTP fallback）

**修改前**：
```python
PROXY_URL = os.getenv("PROXY_URL", "socks5://127.0.0.1:10808")
PROXY_FALLBACK_HTTP = "http://127.0.0.1:10809"  # HTTP 代理 fallback
```

**修改后**：
```python
PROXY_URL = os.getenv("PROXY_URL", "socks5://127.0.0.1:10808")  # SOCKS5 代理（fallback 使用）
# 移除了 PROXY_FALLBACK_HTTP
```

**说明**：
- 移除了 HTTP 代理 fallback
- 只保留 SOCKS5 代理作为 fallback 选项

### 2. 修改重连配置

**修改前**：
```python
_reconnect_delay = 3  # 重连延迟（秒）
```

**修改后**：
```python
_reconnect_delay = 5  # 重连延迟（秒）
_max_reconnect_attempts = 3  # 最大重连次数
```

**说明**：
- 重连延迟改为 5 秒
- 添加最大重连次数限制（3 次）

### 3. 新增 `_try_connect_websocket` 方法

**功能**：
- 测试 WebSocket 连接（带详细日志）
- 返回连接结果和错误信息
- 用于在启动时测试连接策略

**代码**：
```python
async def _try_connect_websocket(self, url: str, connector: Optional[Any], proxy_url: Optional[str] = None, proxy_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """尝试连接 WebSocket（带详细日志）"""
    try:
        logger.info(f"[WS] 尝试连接 WebSocket: {url}")
        # ... 连接逻辑 ...
        return True, None
    except Exception as e:
        error_msg = f"连接失败: {str(e)} (URL: {url})"
        logger.error(f"[WS] ❌ {error_msg}")
        return False, error_msg
```

### 4. 重写 `start_stream_safe` 方法 - 优先直连策略

#### 4.1 WebSocket URL 配置

**修改**：
```python
# 优先使用现货 WebSocket 端点（stream.binance.com）
primary_url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"
fallback_url = f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"
```

**说明**：
- 主要端点：`wss://stream.binance.com:9443/stream`（现货）
- 备用端点：`wss://fstream.binance.com/stream`（期货）
- 使用正确的币安组合流格式：`?streams=stream1/stream2/...`

#### 4.2 连接策略（优先直连）

**策略 1：优先直接连接**
```python
logger.info("[PROXY] 策略 1: 尝试直接连接币安 WebSocket（不使用代理）")
direct_connector = aiohttp.TCPConnector(ssl=False)
success, error = await self._try_connect_websocket(primary_url, direct_connector)

if success:
    logger.info("[PROXY] ✅ 直接连接成功，将使用直连模式")
    connector = direct_connector
    use_proxy = False
```

**策略 2：Fallback 到 SOCKS5 代理**
```python
if not success:
    logger.warning(f"[PROXY] ❌ 直接连接失败: {error}")
    logger.info("[PROXY] 策略 2: Fallback 到 SOCKS5 代理")
    
    # 检查 SOCKS5 代理可用性
    proxy_available = await self._check_proxy_available(PROXY_URL)
    if proxy_available:
        # 创建 SOCKS5 connector
        success, connector, error = await self._create_proxy_connector(PROXY_URL, 'socks5')
        # 测试连接
        test_success, test_error = await self._try_connect_websocket(primary_url, connector, PROXY_URL, 'socks5')
        if test_success:
            use_proxy = True
            proxy_type = 'socks5'
```

#### 4.3 详细日志打印

**连接初始化日志**：
```python
logger.info(f"[WS] ========== WebSocket 连接初始化 ==========")
logger.info(f"[WS] 订阅流: {len(streams)} 个流（{len(SYMBOLS)} 个交易对 × {len(WS_INTERVALS)} 个间隔）")
logger.info(f"[WS] 主要端点: {primary_url}")
logger.info(f"[WS] 备用端点: {fallback_url}")
```

**连接策略确定日志**：
```python
logger.info(f"[WS] ========== 连接策略确定 ==========")
logger.info(f"[WS] 使用代理: {'是' if use_proxy else '否'}")
if use_proxy:
    logger.info(f"[WS] 代理类型: {proxy_type.upper()}")
    logger.info(f"[WS] 代理地址: {current_proxy_url}")
logger.info(f"[WS] WebSocket URL: {current_url}")
logger.info(f"[WS] ========================================")
```

**错误日志**：
```python
except Exception as e:
    logger.error(f"❌ [ERROR] WebSocket 连接断开")
    logger.error(f"[ERROR] URL: {current_url}")
    logger.error(f"[ERROR] 失败次数: {consecutive_failures}, 重连次数: {reconnect_attempts}")
    logger.error(f"[ERROR] 异常类型: {type(e).__name__}")
    logger.error(f"[ERROR] 异常信息: {str(e)}")
```

#### 4.4 重连机制

**重连逻辑**：
```python
reconnect_attempts = 0
consecutive_failures = 0
max_failures_before_mock = 3
_max_reconnect_attempts = 3

while self.is_running:
    try:
        # 连接 WebSocket...
        reconnect_attempts = 0  # 连接成功，重置重连次数
    except Exception as e:
        reconnect_attempts += 1
        consecutive_failures += 1
        
        # 如果重连次数超过限制，切换到模拟数据模式
        if reconnect_attempts >= _max_reconnect_attempts:
            logger.warning(f"[MOCK] 重连次数达到上限 ({_max_reconnect_attempts} 次)...")
            # 生成模拟数据 10 秒
            reconnect_attempts = 0  # 重置重连次数
        
        # 等待 5 秒后重连
        logger.info(f"[WS] 等待 {_reconnect_delay} 秒后重连...")
        await asyncio.sleep(_reconnect_delay)
```

**说明**：
- 每 5 秒重试一次
- 最多重试 3 次
- 如果重连次数达到上限，切换到模拟数据模式 10 秒
- 然后重新尝试连接

### 5. 数据库更新机制

**在 `_process_kline` 方法中**：
```python
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
```

**说明**：
- K 线收盘时（`is_closed=True`）自动保存到数据库
- 使用 `KlineModel.upsert_klines()` 方法
- 支持多个间隔（1m, 1h, 4h, 1d）

## 工作流程

### 启动流程

1. **构建 WebSocket URL**：
   - 订阅所有交易对的所有间隔（5 个交易对 × 4 个间隔 = 20 个流）
   - 主要端点：`wss://stream.binance.com:9443/stream`
   - 备用端点：`wss://fstream.binance.com/stream`

2. **连接策略选择**：
   - **策略 1**：尝试直接连接（不使用代理）
     - 成功 → 使用直连模式
     - 失败 → 继续策略 2
   - **策略 2**：Fallback 到 SOCKS5 代理
     - 检查代理可用性
     - 创建 SOCKS5 connector
     - 测试连接
     - 成功 → 使用 SOCKS5 代理
     - 失败 → 继续使用直连（至少尝试）

3. **WebSocket 连接**：
   - 使用选定的 connector 连接币安 WebSocket
   - 接收实时 K 线数据

4. **数据接收和保存**：
   - 接收实时 K 线数据
   - K 线收盘时保存到数据库
   - 广播给前端连接的客户端

### 重连流程

1. **连接失败**：
   - 记录详细错误日志（URL、异常类型、异常信息）
   - 增加重连次数和失败次数

2. **重连判断**：
   - 如果重连次数 < 3：等待 5 秒后重连
   - 如果重连次数 >= 3：切换到模拟数据模式 10 秒，然后重置重连次数

3. **模拟数据模式**：
   - 生成模拟 K 线数据
   - 广播给前端
   - 10 秒后重新尝试连接真实网络

## 关键改动总结

### 1. 连接策略
- ✅ **优先直连**：因为日本东京 IP 可直连 Binance API
- ✅ **Fallback 到 SOCKS5**：如果直连失败，使用 SOCKS5 代理
- ✅ **移除 HTTP fallback**：不再使用 HTTP 代理

### 2. WebSocket URL
- ✅ **主要端点**：`wss://stream.binance.com:9443/stream`（现货）
- ✅ **备用端点**：`wss://fstream.binance.com/stream`（期货）
- ✅ **正确格式**：使用 `?streams=stream1/stream2/...` 格式

### 3. 重连机制
- ✅ **重连延迟**：5 秒
- ✅ **最大重连次数**：3 次
- ✅ **模拟数据兜底**：重连次数达到上限后切换到模拟数据模式

### 4. 详细日志
- ✅ **连接初始化日志**：显示订阅流数量、端点 URL
- ✅ **连接策略日志**：显示使用的连接方式（直连/代理）
- ✅ **错误日志**：显示 URL、异常类型、异常信息、重连次数

### 5. 数据库更新
- ✅ **自动保存**：K 线收盘时自动保存到数据库
- ✅ **多间隔支持**：支持 1m, 1h, 4h, 1d 四个间隔

## 使用说明

### 1. 安装依赖

```bash
pip install aiosocksy
```

### 2. 配置代理（可选）

在 `.env` 文件中：
```bash
# SOCKS5 代理（fallback 使用）
PROXY_URL=socks5://127.0.0.1:10808

# 或不使用代理（优先直连）
# 不设置 PROXY_URL 或设置为空
```

### 3. 启动服务

```bash
python main.py
```

### 4. 查看日志

启动时会看到详细的连接日志：
```
[WS] ========== WebSocket 连接初始化 ==========
[WS] 订阅流: 20 个流（5 个交易对 × 4 个间隔）
[WS] 主要端点: wss://stream.binance.com:9443/stream?streams=...
[WS] 备用端点: wss://fstream.binance.com/stream?streams=...
[PROXY] 策略 1: 尝试直接连接币安 WebSocket（不使用代理）
[WS] 尝试连接 WebSocket: wss://stream.binance.com:9443/stream?streams=...
[WS] 直接连接（不使用代理）
[WS] ✅ WebSocket 连接成功: wss://stream.binance.com:9443/stream?streams=...
[PROXY] ✅ 直接连接成功，将使用直连模式
[WS] ========== 连接策略确定 ==========
[WS] 使用代理: 否
[WS] WebSocket URL: wss://stream.binance.com:9443/stream?streams=...
[WS] ========================================
```

## 测试场景

### 场景 1：直连成功
- 预期：使用直连模式
- 日志：`[PROXY] ✅ 直接连接成功，将使用直连模式`

### 场景 2：直连失败，SOCKS5 成功
- 预期：Fallback 到 SOCKS5 代理
- 日志：
  ```
  [PROXY] ❌ 直接连接失败: ...
  [PROXY] 策略 2: Fallback 到 SOCKS5 代理
  [PROXY] ✅ SOCKS5 代理连接成功，将使用: socks5://127.0.0.1:10808
  ```

### 场景 3：所有连接都失败
- 预期：使用直连 connector，持续重试
- 日志：
  ```
  [PROXY] ❌ 直接连接失败
  [PROXY] ❌ SOCKS5 代理不可用
  [WS] 等待 5 秒后重连...
  ```

## 注意事项

1. **优先直连**：
   - 因为日本东京 IP 可以直连 Binance API
   - 如果直连成功，不会使用代理

2. **SOCKS5 代理**：
   - 只有在直连失败时才会使用
   - 需要安装 `aiosocksy` 库

3. **重连机制**：
   - 每 5 秒重试一次
   - 最多重试 3 次
   - 达到上限后切换到模拟数据模式 10 秒

4. **WebSocket URL 格式**：
   - 使用正确的币安组合流格式
   - 主要端点：`wss://stream.binance.com:9443/stream?streams=...`
   - 备用端点：`wss://fstream.binance.com/stream?streams=...`

5. **数据库更新**：
   - K 线收盘时自动保存
   - 支持多个间隔（1m, 1h, 4h, 1d）
