# WebSocket 代理连接修复说明

## 问题诊断

1. **代理连接失败**：后端尝试连接 `127.0.0.1:10809`，但代理服务器未运行
2. **HTTP 代理不兼容 wss://**：HTTP 代理可能不完全支持 WebSocket 连接
3. **缺少 SOCKS5 支持**：SOCKS5 代理更适合 WebSocket 连接
4. **代理检测不足**：没有在连接前检查代理是否可用

## 修复内容

### 1. 安装必要的库

#### 选项 A：使用 aiosocksy（推荐）
```bash
pip install aiosocksy
```

#### 选项 B：使用 python-socks（备选）
```bash
pip install python-socks[asyncio]
```

**注意**：如果不需要 SOCKS5 代理支持，可以不安装这些库。系统会自动降级到仅支持 HTTP 代理。

### 2. 后端修复 (`app/services/market_service.py`)

#### 2.1 导入 SOCKS5 支持库

```python
# 优先使用 aiosocksy（更现代），如果没有则尝试 python-socks
try:
    import aiosocksy
    from aiosocksy.connector import SocksConnector
    HAS_SOCKS5 = True
    SOCKS5_LIB = "aiosocksy"
except ImportError:
    try:
        from python_socks.async_.asyncio import Proxy
        from python_socks._types import ProxyType
        HAS_SOCKS5 = True
        SOCKS5_LIB = "python-socks"
    except ImportError:
        HAS_SOCKS5 = False
        SOCKS5_LIB = None
```

**说明**：
- 优先尝试导入 `aiosocksy`（更现代，性能更好）
- 如果失败，尝试导入 `python-socks`
- 如果都不可用，系统会降级到仅支持 HTTP 代理

#### 2.2 新增 `_parse_proxy_url` 方法

```python
def _parse_proxy_url(self, proxy_url: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """解析代理 URL，返回代理类型、主机和端口"""
```

**功能**：
- 解析代理 URL，支持 `http://`、`https://`、`socks5://`、`socks5h://`
- 返回代理类型、主机和端口
- 标准化代理类型（`https` → `http`，`socks5h` → `socks5`）

#### 2.3 改进 `_check_proxy_available` 方法

**改进点**：
1. **使用 aiohttp 测试连通性**：不再使用简单的 socket 连接，而是通过 aiohttp 实际测试代理
2. **支持 SOCKS5 代理测试**：如果安装了 SOCKS5 支持库，可以测试 SOCKS5 代理
3. **更准确的检测**：通过实际 HTTP 请求测试代理是否可用

**测试流程**：
1. 解析代理 URL，确定代理类型
2. 如果是 SOCKS5，检查是否安装了支持库
3. 创建相应的 connector（SOCKS5 使用 SocksConnector，HTTP 使用 TCPConnector）
4. 通过代理发送 HTTP 请求到测试端点（`http://httpbin.org/ip`）
5. 如果请求成功，返回 `True`；否则返回 `False`

#### 2.4 重写 `start_stream_safe` 方法

**关键改进**：

1. **代理检测和选择**：
   ```python
   # 检查代理是否可用
   use_proxy = await self._check_proxy_available(PROXY_URL)
   
   # 根据代理类型创建 connector
   if proxy_type == 'socks5' and HAS_SOCKS5:
       if SOCKS5_LIB == "aiosocksy":
           connector = SocksConnector.from_url(PROXY_URL)
   ```

2. **多间隔订阅**：
   ```python
   # 订阅所有交易对的所有间隔
   for symbol in SYMBOLS:
       for interval in WS_INTERVALS:  # ["1m", "1h", "4h", "1d"]
           streams.append(f"{symbol.lower()}@kline_{interval}")
   ```

3. **智能代理使用**：
   - HTTP 代理：通过 `proxy` 参数传递
   - SOCKS5 代理：通过 `connector` 处理（更可靠）

4. **自动降级**：
   - 如果代理不可用，自动切换到直接连接模式
   - 如果 SOCKS5 库未安装，自动降级到 HTTP 代理或直接连接

### 3. 前端 Vite 配置 (`vite.config.js`)

**修复前**：
```javascript
'/ws': {
  target: 'http://localhost:8080',  // ❌ 错误的端口
  changeOrigin: true,
  ws: true
}
```

**修复后**：
```javascript
'/ws': {
  target: 'ws://127.0.0.1:8000',  // ✅ 正确的后端端口
  changeOrigin: true,
  ws: true,
  rewrite: (path) => path.replace(/^\/ws/, '/api/v1/market/ws/kline')  // ✅ 路径重写
}
```

**说明**：
- `target`: 使用 `ws://` 协议指向后端 FastAPI 服务器（端口 8000）
- `rewrite`: 将前端的 `/ws` 路径重写为后端的完整路径 `/api/v1/market/ws/kline`
- 前端通过 `ws://localhost:5173/ws` 连接，Vite 会自动代理到后端

### 4. 环境变量配置

在 `.env` 文件中配置代理：

```bash
# HTTP 代理（如果代理服务器支持 HTTP）
PROXY_URL=http://127.0.0.1:10809

# SOCKS5 代理（推荐，更适合 WebSocket）
PROXY_URL=socks5://127.0.0.1:10808
```

## 工作流程

### 启动流程

1. **后端启动**：
   - 尝试导入 SOCKS5 支持库
   - 读取 `PROXY_URL` 环境变量
   - 如果配置了代理，检查代理是否可用
   - 根据代理类型和可用性创建 connector

2. **WebSocket 连接**：
   - 构建包含所有交易对和间隔的 WebSocket URL
   - 根据代理可用性决定连接方式：
     - SOCKS5 代理可用 → 使用 SocksConnector
     - HTTP 代理可用 → 使用 HTTP 代理
     - 代理不可用 → 直接连接（不使用代理）

3. **数据接收和保存**：
   - 接收币安 WebSocket 实时数据
   - 解析 K 线数据
   - 调用 `KlineModel.upsert_klines()` 保存到数据库
   - 广播给前端连接的客户端

### 前端连接流程

1. **前端页面加载**：
   - 从 `http://localhost:5173` 页面内通过 JavaScript 创建 WebSocket 连接
   - 连接地址：`ws://localhost:5173/ws`

2. **Vite 代理**：
   - Vite 开发服务器接收 WebSocket 连接
   - 将请求代理到 `ws://127.0.0.1:8000/api/v1/market/ws/kline`

3. **后端处理**：
   - FastAPI 接收 WebSocket 连接
   - 注册连接，开始转发币安的实时数据

## 错误处理和重连机制

1. **代理检测失败**：
   - 自动切换到直接连接模式
   - 记录警告日志，但不影响服务启动

2. **WebSocket 连接失败**：
   - 记录错误日志
   - 增加失败计数
   - 如果连续失败 3 次，切换到模拟数据模式 10 秒
   - 然后重新尝试连接

3. **网络断开**：
   - 自动重连机制（每 3 秒尝试一次）
   - 断开期间生成模拟数据，确保前端不白屏

## 测试建议

### 1. 测试 SOCKS5 代理

```bash
# 设置 SOCKS5 代理
export PROXY_URL=socks5://127.0.0.1:10808

# 启动后端
python main.py

# 检查日志，应该看到：
# [PROXY] 已加载 aiosocksy，支持 SOCKS5 代理
# [PROXY] ✅ SOCKS5 代理可用，将使用代理连接
```

### 2. 测试 HTTP 代理

```bash
# 设置 HTTP 代理
export PROXY_URL=http://127.0.0.1:10809

# 启动后端
python main.py

# 检查日志，应该看到：
# [PROXY] ✅ HTTP 代理可用，将使用代理连接
```

### 3. 测试代理不可用场景

```bash
# 设置代理但代理服务器未运行
export PROXY_URL=http://127.0.0.1:10809

# 启动后端
python main.py

# 检查日志，应该看到：
# [PROXY] ❌ 代理不可用，将直接连接币安（不使用代理）
# [WS] 正在连接币安... (直接连接，不使用代理)
```

### 4. 测试前端连接

1. 启动前端：`npm run dev`
2. 打开浏览器：`http://localhost:5173`
3. 打开浏览器控制台（F12）
4. 检查 WebSocket 连接日志：
   - 应该看到 `[Datafeed] WebSocket 连接成功`
   - 不应该看到连接错误

## 关键改进点总结

1. ✅ **SOCKS5 代理支持**：推荐用于 WebSocket 连接，更可靠
2. ✅ **智能代理检测**：使用 aiohttp 实际测试代理连通性
3. ✅ **自动降级机制**：代理不可用时自动切换到直接连接
4. ✅ **多间隔订阅**：订阅 1m、1h、4h、1d 四个间隔
5. ✅ **正确的 Vite 配置**：WebSocket 代理到正确的后端端点
6. ✅ **完善的错误处理**：重连机制和模拟数据兜底

## 注意事项

1. **不能直接在浏览器地址栏访问 `ws://` 协议**：
   - ❌ 错误：在浏览器地址栏输入 `ws://localhost:5173/ws`
   - ✅ 正确：从 `http://localhost:5173` 页面内通过 JavaScript 连接

2. **SOCKS5 库是可选的**：
   - 如果不安装 SOCKS5 库，系统会自动降级到 HTTP 代理或直接连接
   - 但推荐安装 `aiosocksy` 以获得更好的 WebSocket 支持

3. **代理 URL 格式**：
   - HTTP: `http://127.0.0.1:10809`
   - SOCKS5: `socks5://127.0.0.1:10808`

4. **多个间隔订阅**：
   - 确保 `WS_INTERVALS` 包含前端需要的所有间隔
   - 当前配置：`["1m", "1h", "4h", "1d"]`
