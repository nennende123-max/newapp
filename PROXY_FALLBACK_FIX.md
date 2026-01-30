# WebSocket 代理 Fallback 机制修复说明

## 问题分析

1. **代理端口配置错误**：之前使用 HTTP 代理端口 `10809`，但 v2rayN 的 SOCKS5 端口是 `10808`
2. **缺少 Fallback 机制**：如果 SOCKS5 代理失败，没有自动尝试 HTTP 代理或直连
3. **代理检测不完善**：没有在连接前检查代理是否可用

## 修复内容

### 1. 修改代理配置默认值

**修改前**：
```python
PROXY_URL = os.getenv("PROXY_URL")  # 默认 None
```

**修改后**：
```python
PROXY_URL = os.getenv("PROXY_URL", "socks5://127.0.0.1:10808")  # 默认使用 SOCKS5
PROXY_FALLBACK_HTTP = "http://127.0.0.1:10809"  # HTTP 代理 fallback
```

**说明**：
- 默认使用 SOCKS5 代理（`socks5://127.0.0.1:10808`），匹配 v2rayN 默认配置
- 如果环境变量未设置，自动使用 SOCKS5
- 定义 HTTP 代理作为 fallback 选项

### 2. 添加 `requirements.txt`

创建了 `requirements.txt` 文件，包含：
```
aiosocksy>=0.0.6
```

**安装命令**：
```bash
pip install aiosocksy
```

### 3. 新增 `_create_proxy_connector` 方法

**功能**：
- 创建代理 connector（不实际连接，只创建对象）
- 支持 SOCKS5 和 HTTP 两种代理类型
- 返回创建结果、connector 对象和错误信息

**代码逻辑**：
```python
async def _create_proxy_connector(self, proxy_url: str, proxy_type: str) -> Tuple[bool, Optional[Any], Optional[str]]:
    """创建代理 connector（不实际连接，只创建）"""
    if proxy_type == 'socks5':
        if HAS_SOCKS5 and SOCKS5_LIB == "aiosocksy":
            connector = SocksConnector.from_url(proxy_url)
            return True, connector, None
    elif proxy_type == 'http':
        connector = aiohttp.TCPConnector(ssl=False)
        return True, connector, None
```

### 4. 重写 `start_stream_safe` 方法 - Fallback 机制

**三层 Fallback 策略**：

#### 策略 1：优先尝试 SOCKS5 代理
```python
# 检查 SOCKS5 代理是否可用
proxy_available = await self._check_proxy_available(PROXY_URL)
if proxy_available:
    success, connector, error = await self._create_proxy_connector(PROXY_URL, 'socks5')
    if success:
        use_proxy = True
        proxy_type = 'socks5'
```

#### 策略 2：Fallback 到 HTTP 代理
```python
# 如果 SOCKS5 失败，尝试 HTTP 代理
if not use_proxy:
    proxy_available = await self._check_proxy_available(PROXY_FALLBACK_HTTP)
    if proxy_available:
        success, connector, error = await self._create_proxy_connector(PROXY_FALLBACK_HTTP, 'http')
        if success:
            use_proxy = True
            proxy_type = 'http'
```

#### 策略 3：Fallback 到直接连接
```python
# 如果代理都失败，直接连接（不使用代理）
if not use_proxy:
    connector = aiohttp.TCPConnector(ssl=False)
    use_proxy = False
```

### 5. 多间隔 K 线订阅

**代码**：
```python
# 订阅所有交易对的所有间隔
streams = []
for symbol in SYMBOLS:
    for interval in WS_INTERVALS:  # ["1m", "1h", "4h", "1d"]
        streams.append(f"{symbol.lower()}@kline_{interval}")

url = f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"
```

**说明**：
- 订阅 5 个交易对 × 4 个间隔 = 20 个流
- 确保前端请求 `interval=1h` 时有实时数据

### 6. 数据库更新机制

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
- 只有当 K 线收盘（`is_closed=True`）时才保存到数据库
- 使用 `KlineModel.upsert_klines()` 方法，自动处理重复数据

### 7. 重连机制

**错误处理**：
```python
consecutive_failures = 0
max_failures_before_mock = 3

while self.is_running:
    try:
        # 尝试连接 WebSocket
        async with session.ws_connect(**ws_kwargs) as ws:
            consecutive_failures = 0  # 重置失败计数
            # 接收消息...
    except Exception as e:
        consecutive_failures += 1
        # 如果连续失败 3 次，切换到模拟数据模式 10 秒
        if consecutive_failures >= max_failures_before_mock:
            # 生成模拟数据...
            consecutive_failures = 0  # 重置计数，重新尝试
```

**说明**：
- 连接失败时自动重试（每 3 秒一次）
- 连续失败 3 次后，切换到模拟数据模式 10 秒
- 然后重新尝试连接真实网络

## 工作流程

### 启动流程

1. **读取配置**：
   - 默认使用 `socks5://127.0.0.1:10808`（v2rayN SOCKS5 端口）
   - 如果环境变量设置了 `PROXY_URL`，使用环境变量的值

2. **代理检测和选择**：
   - 策略 1：检查 SOCKS5 代理是否可用
     - 可用 → 创建 SOCKS5 connector，使用 SOCKS5 代理
     - 不可用 → 继续策略 2
   - 策略 2：检查 HTTP 代理是否可用
     - 可用 → 创建 HTTP connector，使用 HTTP 代理
     - 不可用 → 继续策略 3
   - 策略 3：直接连接（不使用代理）

3. **WebSocket 连接**：
   - 使用选定的 connector 连接币安 WebSocket
   - 订阅所有交易对的所有间隔（1m, 1h, 4h, 1d）

4. **数据接收和保存**：
   - 接收实时 K 线数据
   - K 线收盘时保存到数据库
   - 广播给前端连接的客户端

## 关键改动总结

### 1. 代理配置
- ✅ 默认使用 SOCKS5：`socks5://127.0.0.1:10808`
- ✅ 定义 HTTP fallback：`http://127.0.0.1:10809`

### 2. Fallback 机制
- ✅ 三层策略：SOCKS5 → HTTP → 直连
- ✅ 自动检测代理可用性
- ✅ 智能选择最佳连接方式

### 3. 多间隔支持
- ✅ 订阅 1m, 1h, 4h, 1d 四个间隔
- ✅ 确保前端请求 `interval=1h` 时有数据

### 4. 数据库更新
- ✅ K 线收盘时自动保存
- ✅ 使用 `KlineModel.upsert_klines()` 方法

### 5. 重连机制
- ✅ 自动重试（每 3 秒）
- ✅ 模拟数据兜底（连续失败 3 次后）

## 使用说明

### 1. 安装依赖

```bash
pip install aiosocksy
```

### 2. 配置代理（可选）

在 `.env` 文件中：
```bash
# 使用 SOCKS5 代理（推荐，v2rayN 默认）
PROXY_URL=socks5://127.0.0.1:10808

# 或使用 HTTP 代理
PROXY_URL=http://127.0.0.1:10809

# 或不使用代理（直接连接）
# 不设置 PROXY_URL 或设置为空
```

### 3. 启动服务

```bash
python main.py
```

### 4. 查看日志

启动时会看到代理选择日志：
```
[PROXY] 策略 1: 尝试 SOCKS5 代理 socks5://127.0.0.1:10808
[PROXY] ✅ SOCKS5 代理可用，将使用: socks5://127.0.0.1:10808
[WS] 订阅流: 20 个流（5 个交易对 × 4 个间隔）
[WS] 正在连接币安... (使用 SOCKS5 代理: socks5://127.0.0.1:10808)
✅ [OK] 币安 WebSocket 连接成功！接收数据中...
```

## 测试场景

### 场景 1：SOCKS5 代理可用
- 预期：使用 SOCKS5 代理连接
- 日志：`[PROXY] ✅ SOCKS5 代理可用，将使用: socks5://127.0.0.1:10808`

### 场景 2：SOCKS5 不可用，HTTP 可用
- 预期：Fallback 到 HTTP 代理
- 日志：
  ```
  [PROXY] ❌ SOCKS5 代理不可用: socks5://127.0.0.1:10808
  [PROXY] 策略 2: Fallback 到 HTTP 代理 http://127.0.0.1:10809
  [PROXY] ✅ HTTP 代理可用，将使用: http://127.0.0.1:10809
  ```

### 场景 3：所有代理都不可用
- 预期：Fallback 到直接连接
- 日志：
  ```
  [PROXY] ❌ SOCKS5 代理不可用
  [PROXY] ❌ HTTP 代理不可用
  [PROXY] 策略 3: Fallback 到直接连接（不使用代理）
  [WS] 正在连接币安... (直接连接，不使用代理)
  ```

## 注意事项

1. **aiosocksy 库是必需的**：
   - 如果未安装，SOCKS5 代理将无法使用
   - 系统会自动 fallback 到 HTTP 代理或直连

2. **代理端口**：
   - v2rayN SOCKS5 端口：`10808`
   - v2rayN HTTP 端口：`10809`

3. **环境变量优先级**：
   - 如果设置了 `PROXY_URL` 环境变量，使用环境变量的值
   - 否则使用默认值 `socks5://127.0.0.1:10808`

4. **Fallback 顺序**：
   - SOCKS5 → HTTP → 直连
   - 每个策略都会检查代理可用性，只有可用时才使用
