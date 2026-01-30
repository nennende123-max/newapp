# K 线数据服务使用说明

## 概述

基于 ccxt 库开发的币安 K 线数据后端服务，提供历史数据同步和实时行情推送功能。

## 功能特性

1. **历史数据同步**：应用启动时自动抓取主流币种最近 1000 根 1分钟 K 线数据
2. **实时行情流**：通过 WebSocket 连接币安，实时接收并广播 K 线数据
3. **数据持久化**：使用 SQLite 数据库存储 K 线数据
4. **容错处理**：自动重连机制，网络断开时每 3 秒尝试重连

## API 接口

### 1. GET /api/v1/market/kline

获取 K 线历史数据

**请求参数：**
- `symbol` (必需): 交易对，如 `BTC/USDT`
- `interval` (可选): 时间间隔，如 `1m`, `5m`, `1h`，默认 `1m`
- `limit` (可选): 返回数量限制，默认 1000，最大 5000
- `start_time` (可选): 开始时间戳（毫秒）
- `end_time` (可选): 结束时间戳（毫秒）

**示例请求：**
```bash
GET /api/v1/market/kline?symbol=BTC/USDT&interval=1m&limit=100
```

**响应格式：**
```json
{
  "code": 200,
  "message": "获取 K 线数据成功",
  "data": [
    {
      "symbol": "BTC/USDT",
      "interval": "1m",
      "timestamp": 1234567890000,
      "open": 50000.0,
      "high": 51000.0,
      "low": 49000.0,
      "close": 50500.0,
      "volume": 1000.0
    }
  ]
}
```

### 2. WebSocket /api/v1/market/ws/kline

实时 K 线数据推送

**连接示例（JavaScript）：**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/market/ws/kline');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'kline') {
    const kline = message.data;
    console.log('收到 K 线数据:', kline);
    // kline 包含: symbol, interval, timestamp, open, high, low, close, volume, is_closed
  }
};

// 发送心跳（可选）
ws.send(JSON.stringify({ type: 'ping' }));
```

**消息格式：**
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
    "is_closed": false
  }
}
```

## 数据库结构

SQLite 数据库文件位置：`data/kline.db`

**klines 表结构：**
```sql
CREATE TABLE klines (
    symbol TEXT NOT NULL,
    interval TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    PRIMARY KEY (symbol, interval, timestamp)
);
```

## 启动流程

1. **数据库初始化**：应用启动时自动创建 SQLite 数据库和表结构
2. **历史数据同步**：自动抓取以下币种最近 1000 根 1分钟 K 线：
   - BTC/USDT
   - ETH/USDT
   - BNB/USDT
   - SOL/USDT
   - DOGE/USDT
3. **实时行情流**：启动 WebSocket 连接，订阅上述币种的实时 K 线数据
4. **数据入库**：当 K 线收盘（`x=True`）时，自动保存到数据库

## 容错机制

- **网络断开重连**：WebSocket 连接断开时，每 3 秒自动尝试重连
- **数据库容错**：使用 `INSERT OR REPLACE` 防止重复数据
- **API 容错**：如果数据库为空，临时调用 ccxt 抓取数据

## 日志输出

服务运行时会输出以下日志：

- `[OK] K 线数据库初始化成功`
- `[SYNC] 开始同步 BTC/USDT 1m 历史数据（最近 1000 根）...`
- `[OK] BTC/USDT 1m 历史数据同步完成，共 1000 根 K 线`
- `[STREAM] 启动实时行情流: BTC/USDT, ETH/USDT, ...`
- `[OK] 币安 WebSocket 连接成功`
- `[WARN] WebSocket 连接已关闭，3 秒后重连...`（网络波动时）
- `[WS] 新客户端连接，当前连接数: 1`

## 注意事项

1. **网络要求**：需要能够访问币安 API（外网连接）
2. **数据延迟**：历史数据同步可能需要几秒钟时间
3. **实时数据**：只有 K 线收盘（`is_closed=true`）时才会保存到数据库
4. **WebSocket 连接**：前端需要处理连接断开和重连逻辑

## 依赖库

- `ccxt`: 加密货币交易所 API 库
- `websockets`: WebSocket 客户端/服务器库
- `aiosqlite`: 异步 SQLite 数据库驱动

## 文件结构

```
app/
├── models/
│   └── kline.py          # K 线数据模型
├── services/
│   └── market_service.py # 市场数据服务
└── api/
    └── endpoints/
        └── market.py     # K 线 API 端点
```
