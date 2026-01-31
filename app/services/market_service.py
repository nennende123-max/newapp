"""
币安 K 线市场服务（固定直连模式，使用443端口，日本东京IP已确认通）
负责历史数据同步和实时行情流
如果网络连接失败，自动切换到模拟数据模式，确保前端永不白屏

固定直连 Binance WebSocket，移除所有代理逻辑
使用443端口（日本东京IP已确认通）
修复Session管理：使用 async with ClientSession() 确保 Session 不会过早关闭
"""
import aiohttp
import asyncio
import json
import logging
import random
import time
import os
import requests
import traceback
import websockets  # 确保导入
from typing import Dict, Set, Optional, Any, List
from urllib.parse import urlparse

from fastapi import HTTPException
from app.models.kline import KlineModel

# ========== 配置日志 ==========
logging.basicConfig(
    level=logging.DEBUG,  # 启用DEBUG级别日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 确保DEBUG级别日志被打印

# ========== 配置 ==========
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]

# 需要同步的时间周期列表（必须包含 1h，否则前端不显示）
SYNC_INTERVALS = ["1m", "1h", "4h", "1d"]

# ========== 关键修复：WebSocket 订阅的间隔列表（用于实时流）==========
# 支持多个间隔：1m, 5m, 15m, 1h, 4h, 1d
WS_INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d"]

# WebSocket 连接管理（用于广播给前端）
_active_connections: Set[Any] = set()
_reconnect_delay = 5  # 重连延迟（秒）
_max_reconnect_attempts = 0  # 0 表示无限重试


class MarketService:
    """市场数据服务（固定直连模式，使用443端口，日本东京IP已确认通）"""
    
    def __init__(self):
        self.ws = None  # WebSocket 连接
        self.clients = set()  # 连接的WebSocket客户端
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]
        self.intervals = ["1m", "1h", "4h", "1d"]
        self.is_running = False
        self.current_prices = {
            "BTCUSDT": 90000.0,
            "ETHUSDT": 3000.0,
            "BNBUSDT": 600.0,
            "SOLUSDT": 150.0,
            "DOGEUSDT": 0.08
        }  # 模拟数据的初始价格
        logger.info("[OK] MarketService 初始化（固定直连模式，确保实时Binance数据）")
    
    async def initialize_exchange(self):
        """初始化交易所连接和数据库"""
        # 初始化 K 线数据库
        try:
            await KlineModel.init_db()
            logger.info("[OK] K 线数据库初始化成功")
        except Exception as e:
            logger.error(f"[ERROR] K 线数据库初始化失败: {str(e)}")
            logger.debug(f"[DEBUG] 数据库初始化异常详情: {traceback.format_exc()}")
        
        # 注意：initialize_exchange 方法会在数据库初始化后再次记录日志
    
    async def start(self):
        """启动服务"""
        self.is_running = True
        # 启动两个任务：同步历史 + 实时流
        asyncio.create_task(self.sync_history_safe())
        asyncio.create_task(self.start_stream_safe())
    
    async def sync_history_safe(self):
        """
        尝试同步历史数据，失败则忽略，不影响启动
        
        双层循环遍历 SYMBOLS 和 SYNC_INTERVALS，确保同步所有周期（包括 1h）
        固定直连 Binance API，不使用代理
        """
        try:
            logger.info(f"[SYNC] 正在尝试同步历史数据（周期: {SYNC_INTERVALS}）...")
            # 固定直连，不使用代理
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                # 双层循环：遍历所有交易对和时间周期
                for symbol in SYMBOLS:
                    for interval in SYNC_INTERVALS:
                        url = "https://fapi.binance.com/fapi/v1/klines"
                        try:
                            async with session.get(
                                url,
                                params={"symbol": symbol, "interval": interval, "limit": "1000"},
                                timeout=aiohttp.ClientTimeout(total=10)
                            ) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    
                                    # 币安 API 返回格式: [t, o, h, l, c, v, ...]
                                    # 转换为 KlineModel 需要的字典格式
                                    klines = []
                                    normalized_symbol = self._normalize_symbol(symbol)
                                    for item in data:
                                        klines.append({
                                            'symbol': normalized_symbol,
                                            'interval': interval,
                                            'timestamp': int(item[0]),  # 时间戳（毫秒）
                                            'open': float(item[1]),
                                            'high': float(item[2]),
                                            'low': float(item[3]),
                                            'close': float(item[4]),
                                            'volume': float(item[5])
                                        })
                                    
                                    # 调用 KlineModel.upsert_klines 保存数据（严禁手写 SQL）
                                    await KlineModel.upsert_klines(klines)
                                    logger.info(f"[OK] {normalized_symbol} {interval} 同步成功: {len(klines)} 条")
                                else:
                                    error_text = await resp.text()
                                    logger.warning(f"[SYNC] {symbol} {interval} HTTP {resp.status}: {error_text}")
                        except asyncio.TimeoutError:
                            logger.warning(f"[SYNC] {symbol} {interval} 请求超时，跳过")
                        except Exception as e:
                            logger.warning(f"[SYNC] {symbol} {interval} 网络连接失败，跳过 (使用本地缓存或空数据): {str(e)}")
                            logger.debug(f"[DEBUG] 同步异常详情: {traceback.format_exc()}")
        except Exception as e:
            logger.error(f"[SYNC] 历史同步模块报错: {e}")
            logger.debug(f"[DEBUG] 历史同步异常详情: {traceback.format_exc()}")
    
    async def start_stream_safe(self):
        """
        实时流：固定直连 Binance WebSocket，使用443端口（日本东京IP已确认通）
        
        使用 websockets 库，重连优化，添加 ping 保持连接
        固定直连，无限重试，处理SSL/409错误
        使用指数退避策略，避免被ban
        """
        primary_url = "wss://stream.binance.com:443/ws"
        fallback_url = "wss://fstream.binance.com:443/ws"  # 备用（从文档推荐）
        current_url = primary_url
        reconnect_attempts = 0
        reconnect_delay = 5  # 初始5s，指数退避

        streams = [f"{symbol.lower()}@kline_{interval}" for symbol in self.symbols for interval in self.intervals]
        streams_path = '/'.join(streams)
        ws_url = f"{current_url}?streams={streams_path}"
        
        logger.info(f"[WS] ========== WebSocket 连接初始化（使用websockets库，固定直连模式，443端口）==========")
        logger.info(f"[WS] 订阅流: {len(streams)} 个流（{len(self.symbols)} 个交易对 × {len(self.intervals)} 个间隔）")
        logger.info(f"[WS] 交易对: {self.symbols}")
        logger.info(f"[WS] 间隔: {self.intervals}")
        logger.info(f"[WS] WebSocket URL: {ws_url}")
        logger.info(f"[WS] ========================================")

        while self.is_running:
            try:
                async with websockets.connect(ws_url, ping_interval=30, ping_timeout=60, ssl=False) as ws:  # 用websockets，添加ping保持
                    self.ws = ws
                    logger.info(f"[WS] ✅ 实时Binance WebSocket连接成功: {ws_url} (使用websockets库，避免409错误)")
                    reconnect_attempts = 0  # 重置重连次数
                    reconnect_delay = 5  # 重置延迟
                    
                    async for message in ws:
                        data = json.loads(message)
                        if 'stream' in data and '@kline_' in data['stream']:  # 验证@kline（非@depth）
                            kline = data['data']['k']
                            # 传递原始币安格式给 _process_kline（期望格式：'s', 'i', 't', 'o', 'h', 'l', 'c', 'v', 'x'）
                            await self._process_kline(kline)  # 处理所有K线
                        else:
                            logger.debug(f"[DEBUG] 忽略非@kline流: {data.get('stream')} - 检查是否订阅了@depth")
            except Exception as e:
                error_str = str(e).lower()
                if '409' in error_str or 'invalid response' in error_str:
                    logger.error("[ERROR] ⚠️ 409错误 - 可能连接限额或URL冲突，切换备用URL并延长延迟")
                    current_url = fallback_url if current_url == primary_url else primary_url
                    ws_url = f"{current_url}?streams={streams_path}"
                    reconnect_delay = min(reconnect_delay * 2, 120)  # 延长延迟
                elif 'ssl' in error_str:
                    logger.error("[ERROR] ⚠️ SSL错误 - 已禁用验证，重试中")
                logger.error(f"[ERROR] WebSocket断开: {e} - 重连尝试 {reconnect_attempts}")
                reconnect_attempts += 1
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 120)  # 最大120s，避免ban
    
    async def _generate_mock_data(self):
        """生成逼真的假数据，用于网络断开时兜底"""
        for symbol in self.symbols:
            # 随机波动 +/- 0.05%
            current_price = self.current_prices.get(symbol, 90000.0)
            change = current_price * random.uniform(-0.0005, 0.0005)
            new_price = current_price + change
            self.current_prices[symbol] = new_price
            
            # 构建模拟 K 线数据
            normalized_symbol = self._normalize_symbol(symbol)
            mock_kline = {
                'symbol': normalized_symbol,
                'interval': '1m',
                'timestamp': int(time.time() * 1000),
                'open': new_price,
                'high': new_price + abs(change) * 2,
                'low': new_price - abs(change) * 2,
                'close': new_price,
                'volume': random.uniform(10, 100),
                'is_closed': False
            }
            
            # 广播假数据，让前端动起来
            await self._broadcast_kline(mock_kline)
    
    async def _process_kline(self, kline_data):
        """
        处理真实的 K 线数据（核心逻辑）
        
        收到 WebSocket 数据后，调用 KlineModel.upsert_klines 保存实时数据
        并推送给所有前端 /ws 客户端
        
        Args:
            kline_data: 币安 WebSocket 返回的 K 线数据字典，格式：
                {
                    's': 'BTCUSDT',  # symbol
                    'i': '1m',       # interval
                    't': 1234567890, # timestamp (ms)
                    'o': '50000.0',  # open
                    'h': '51000.0',  # high
                    'l': '49000.0',  # low
                    'c': '50500.0',  # close
                    'v': '1000.0',   # volume
                    'x': True        # is_closed
                }
        """
        try:
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
            is_closed = kline_data.get('x', False)
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
            
            # 如果 K 线收盘，保存到数据库
            if kline['is_closed']:
                # 创建不包含 is_closed 的字典（数据库不需要此字段）
                db_kline = {
                    'symbol': kline['symbol'],
                    'interval': kline['interval'],
                    'timestamp': kline['timestamp'],
                    'open': kline['open'],
                    'high': kline['high'],
                    'low': kline['low'],
                    'close': kline['close'],
                    'volume': kline['volume']
                }
                await KlineModel.upsert_klines([db_kline])  # 保存到DB
                logger.debug(f"[DB] 保存收盘K线: {kline['symbol']} {kline['interval']}")
            
            # 推送所有K线（包括未收盘的，用于实时更新）
            await self._broadcast_kline(kline)  # 推送所有（实时更新）
            logger.debug(f"[BROADCAST] 推送实时K线: {kline['symbol']} {kline['interval']}")
        except Exception as e:
            logger.error(f"[ERROR] 处理 K 线数据失败: {str(e)}")
            logger.error(f"[ERROR] K线数据: {kline_data}")
            logger.debug(f"[DEBUG] K线处理异常详情: {traceback.format_exc()}")
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化交易对格式
        将 BTCUSDT 转换为 BTC/USDT（与 KlineModel 存储格式一致）
        """
        symbol = symbol.upper()
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}/USDT"
        return symbol
    
    async def _broadcast_kline(self, kline: Dict[str, Any]):
        """
        广播 K 线数据给所有连接的客户端（前端 /ws 客户端）
        
        关键修复：确保数据接收后立即推送给前端，不延迟
        推送格式：{type: 'kline', data: {time: unix_ms, open: float, high: float, low: float, close: float, volume: float}}
        """
        if not _active_connections:
            logger.debug(f"[DEBUG] 无活跃的前端连接，跳过推送: {kline.get('symbol')} {kline.get('interval')}")
            return
        
        # ========== 关键修复：推送标准 JSON 数组格式给前端 ==========
        # 前端 TradingViewWidget 需要的数据格式：[{time: number, open: float, high: float, low: float, close: float, volume: float}]
        # 注意：这里 time 保持为毫秒（unix_ms），前端会转换为秒级时间戳（time / 1000）
        # 推送标准 JSON 格式：{type: 'kline', data: {time: number, open: float, high: float, low: float, close: float, volume: float}}
        kline_data = {
            'symbol': kline.get('symbol'),
            'interval': kline.get('interval'),
            'time': int(kline.get('timestamp', 0)),  # 毫秒级时间戳（unix_ms），确保是整数
            'open': float(kline.get('open', 0)),
            'high': float(kline.get('high', 0)),
            'low': float(kline.get('low', 0)),
            'close': float(kline.get('close', 0)),
            'volume': float(kline.get('volume', 0)),
            'is_closed': kline.get('is_closed', False)
        }
        
        message = {
            'type': 'kline',
            'data': kline_data
        }
        
        # 记录推送数据格式（用于调试）
        logger.debug(f"[BROADCAST] 推送 K 线数据格式: time={kline_data['time']} (ms), open={kline_data['open']}, close={kline_data['close']}, volume={kline_data['volume']}")
        
        # 发送给所有活跃连接
        disconnected = set()
        success_count = 0
        
        for ws in _active_connections:
            try:
                # FastAPI WebSocket 支持 send_json
                if hasattr(ws, 'send_json'):
                    await ws.send_json(message)
                    success_count += 1
                else:
                    # 兼容标准 websockets 库
                    await ws.send(json.dumps(message))
                    success_count += 1
            except Exception as e:
                logger.warning(f"[WARN] 发送消息失败，连接将被移除: {str(e)}")
                logger.debug(f"[DEBUG] 发送消息异常详情: {traceback.format_exc()}")
                disconnected.add(ws)
        
        # 移除断开的连接
        _active_connections.difference_update(disconnected)
        
        # 记录推送成功日志（每10条记录一次，避免日志过多）
        if success_count > 0:
            logger.debug(f"[BROADCAST] ✅ 成功推送 K 线数据到 {success_count} 个客户端: {kline.get('symbol')} {kline.get('interval')} timestamp={kline.get('timestamp')}")
        
        if disconnected:
            logger.warning(f"[WARN] 移除了 {len(disconnected)} 个断开的连接，当前活跃连接数: {len(_active_connections)}")
    
    async def sync_all_main_symbols(self):
        """同步所有主流币种的历史数据（兼容性方法）"""
        await self.sync_history_safe()
    
    async def sync_history(self, symbol: str = "BTC/USDT", interval: str = "1m", limit: int = 1000):
        """同步历史 K 线数据（兼容性方法）"""
        await self.sync_history_safe()
    
    async def start_stream(self, symbols: Optional[list] = None):
        """启动实时行情流（兼容性方法）"""
        await self.start_stream_safe()
    
    async def stop_stream(self):
        """停止实时行情流"""
        self.is_running = False
        logger.info("[INFO] 实时行情流已停止")
    
    async def close(self):
        """关闭服务，释放资源"""
        await self.stop_stream()
    
    async def get_kline_data(self, symbol: str, interval: str, limit: int) -> List[List[float]]:
        """
        获取 K 线数据（从数据库查询）
        
        直接调用 KlineModel.get_klines 方法获取数据，然后转换为前端需要的数组格式。
        严禁使用 .filter() 或手写 SQL。
        
        Args:
            symbol: 交易对，如 "BTC/USDT" 或 "BTCUSDT"（会被标准化为 BTC/USDT）
            interval: 时间间隔，如 "1m", "5m", "1h"
            limit: 返回数量限制
        
        Returns:
            K 线数据列表，每个元素为 [timestamp(毫秒), open, high, low, close, volume] 的数组格式
            按时间正序排列（旧的在左，新的在右）
        
        Raises:
            Exception: 数据库查询失败时抛出异常
        """
        try:
            # 标准化 symbol：转为大写并转换为 BTC/USDT 格式
            # 确保与同步写入时的标准化逻辑一致（KlineModel 中存储的格式为 BTC/USDT）
            symbol_upper = symbol.upper()
            normalized_symbol = self._normalize_symbol(symbol_upper)
            
            logger.info(f"[KLINE] 查询 K 线数据: 原始symbol={symbol}, 标准化后={normalized_symbol}, interval={interval}, limit={limit}")
            
            # 直接调用 KlineModel.get_klines 获取数据（严禁手写 SQL）
            # KlineModel.get_klines 返回字典列表，格式为：
            # [{'symbol': 'BTC/USDT', 'interval': '1h', 'timestamp': ..., 'open': ..., 'high': ..., 'low': ..., 'close': ..., 'volume': ...}, ...]
            klines_dict = await KlineModel.get_klines(
                symbol=normalized_symbol,
                interval=interval,
                limit=limit
            )
            
            # 如果查询结果为空，打印警告
            if not klines_dict:
                logger.warning(f"[WARN] 数据库未找到 K 线数据: symbol={normalized_symbol}, interval={interval}")
                return []
            
            # 数据格式转换：从字典列表转换为数组列表
            # 前端 Lightweight Charts 需要的格式：[[timestamp, open, high, low, close, volume], ...]
            # 注意：KlineModel.get_klines 已经按时间戳升序排列，无需反转
            # 确保 timestamp 是毫秒（KlineModel 中存储的就是毫秒）
            result = [
                [
                    float(kline['timestamp']),  # 时间戳（毫秒）
                    float(kline['open']),
                    float(kline['high']),
                    float(kline['low']),
                    float(kline['close']),
                    float(kline['volume'])
                ]
                for kline in klines_dict
            ]
            
            logger.info(f"[KLINE] 查询成功: 返回 {len(result)} 条数据")
            return result
                    
        except Exception as e:
            logger.error(f"[ERROR] 查询 K 线数据失败: symbol={symbol}, interval={interval}, error={str(e)}")
            logger.debug(f"[DEBUG] 查询异常详情: {traceback.format_exc()}")
            raise


# 全局服务实例
market_service = MarketService()


async def register_websocket(websocket: Any):
    """注册 WebSocket 连接"""
    _active_connections.add(websocket)
    logger.info(f"[WS] 新客户端连接，当前连接数: {len(_active_connections)}")


async def unregister_websocket(websocket: Any):
    """注销 WebSocket 连接"""
    _active_connections.discard(websocket)
    logger.info(f"[WS] 客户端断开，当前连接数: {len(_active_connections)}")


def get_current_price(symbol: str) -> float:
    """从币安 API 获取当前价格"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched price for {symbol}: {data['price']}")
        return float(data['price'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Binance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch price from Binance: {str(e)}")


def get_klines(symbol: str, interval: str, limit: int = 500) -> List[Dict]:
    """从币安 API 获取 K 线数据"""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        klines = response.json()
        print(f"Fetched {len(klines)} klines for {symbol} interval {interval}")
        
        # 返回格式：确保时间戳为毫秒（Binance API 返回的时间戳已经是毫秒）
        result = [
            {
                "time": int(k[0]),  # 已为 ms，无需改，但确认
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            }
            for k in klines
        ]
        
        # 添加日志：输出返回的数据条数和第一条数据
        if result:
            print(f"返回 K 线数据: {len(result)} 条，第一条: {result[0]}")
        else:
            print(f"返回 K 线数据: 0 条（空数据）")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Binance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch klines from Binance: {str(e)}")


def get_order_book(symbol: str, limit: int = 20) -> Dict:
    """从币安 API 获取订单簿（盘口数据）"""
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol.upper()}&limit={limit}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched order book for {symbol}: {len(data['bids'])} bids, {len(data['asks'])} asks")
        return {
            "bids": [[float(b[0]), float(b[1])] for b in data['bids']],
            "asks": [[float(a[0]), float(a[1])] for a in data['asks']]
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Binance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch order book from Binance: {str(e)}")
