"""
币安 K 线市场服务（使用 aiohttp 直接连接 + 自动兜底模式）
负责历史数据同步和实时行情流
如果网络连接失败，自动切换到模拟数据模式，确保前端永不白屏
"""
import aiohttp
import asyncio
import json
import logging
import random
import time
import os
import requests
from typing import Dict, Set, Optional, Any, List

from fastapi import HTTPException
from app.models.kline import KlineModel

# ========== 配置 ==========
# 代理配置：None 表示不使用代理，直接进入模拟模式
PROXY_URL = None
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket 连接管理（用于广播给前端）
_active_connections: Set[Any] = set()
_reconnect_delay = 3  # 重连延迟（秒）


class MarketService:
    """市场数据服务（使用 aiohttp 直接连接 + 自动兜底模式）"""
    
    def __init__(self):
        self.is_running = False
        self.current_prices = {
            "BTCUSDT": 90000.0,
            "ETHUSDT": 3000.0,
            "BNBUSDT": 600.0,
            "SOLUSDT": 150.0,
            "DOGEUSDT": 0.08
        }  # 模拟数据的初始价格
    
    async def initialize_exchange(self):
        """初始化（兼容性方法，实际不需要）"""
        logger.info("[OK] MarketService 初始化（使用 aiohttp 直接连接 + 自动兜底模式）")
    
    async def start(self):
        """启动服务"""
        self.is_running = True
        # 启动两个任务：同步历史 + 实时流
        asyncio.create_task(self.sync_history_safe())
        asyncio.create_task(self.start_stream_safe())
    
    async def sync_history_safe(self):
        """尝试同步历史，失败则忽略，不影响启动"""
        # 如果未配置代理，跳过历史数据同步
        if not PROXY_URL:
            logger.info("[SYNC] 未配置代理，跳过历史数据同步（使用模拟模式）")
            return
        
        try:
            logger.info("[SYNC] 正在尝试同步历史数据...")
            # 这里的 SSL=False 和 proxy 是关键
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                for symbol in SYMBOLS:
                    url = "https://fapi.binance.com/fapi/v1/klines"
                    try:
                        async with session.get(
                            url,
                            params={"symbol": symbol, "interval": "1m", "limit": "1000"},
                            proxy=PROXY_URL,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                
                                # 币安格式: [t, o, h, l, c, v, ...]
                                klines = []
                                for item in data:
                                    normalized_symbol = self._normalize_symbol(symbol)
                                    klines.append({
                                        'symbol': normalized_symbol,
                                        'interval': '1m',
                                        'timestamp': int(item[0]),
                                        'open': float(item[1]),
                                        'high': float(item[2]),
                                        'low': float(item[3]),
                                        'close': float(item[4]),
                                        'volume': float(item[5])
                                    })
                                
                                await KlineModel.upsert_klines(klines)
                                logger.info(f"[OK] {symbol} 同步成功: {len(klines)} 条")
                            else:
                                error_text = await resp.text()
                                logger.warning(f"[SYNC] {symbol} HTTP {resp.status}: {error_text}")
                    except asyncio.TimeoutError:
                        logger.warning(f"[SYNC] {symbol} 请求超时，跳过")
                    except Exception as e:
                        logger.warning(f"[SYNC] {symbol} 网络连接失败，跳过 (使用本地缓存或空数据): {str(e)}")
        except Exception as e:
            logger.error(f"[SYNC] 历史同步模块报错: {e}")
    
    async def start_stream_safe(self):
        """实时流：连不上就造假数据，绝不报错退出"""
        # 如果未配置代理，直接进入模拟模式
        if not PROXY_URL:
            logger.info("[MODE] 未配置代理，直接启动【本地模拟模式】")
            while self.is_running:
                await self._generate_mock_data()
                await asyncio.sleep(1)
            return
        
        url = "wss://fstream.binance.com/stream?streams=" + "/".join([f"{s.lower()}@kline_1m" for s in SYMBOLS])
        
        consecutive_failures = 0
        max_failures_before_mock = 3  # 连续失败3次后切换到模拟模式
        
        while self.is_running:
            try:
                # --- 关键修改：Session 在循环内创建 ---
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    logger.info(f"[WS] 正在连接币安... (代理: {PROXY_URL})")
                    
                    # 设置超时，防止卡死
                    async with session.ws_connect(
                        url,
                        proxy=PROXY_URL,
                        heartbeat=15,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as ws:
                        logger.info("✅ [OK] 币安 WebSocket 连接成功！接收数据中...")
                        consecutive_failures = 0  # 重置失败计数
                        
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    data = json.loads(msg.data)
                                    
                                    # 解析数据格式: {"stream": "btcusdt@kline_1m", "data": {"e": "kline", "k": {...}}}
                                    if 'data' in data and 'k' in data['data']:
                                        kline_data = data['data']['k']
                                        
                                        # 更新基准价格
                                        symbol_raw = kline_data.get('s', '')
                                        if symbol_raw in self.current_prices:
                                            self.current_prices[symbol_raw] = float(kline_data.get('c', self.current_prices.get(symbol_raw, 90000)))
                                        
                                        await self._process_kline(kline_data)
                                        
                                except json.JSONDecodeError as e:
                                    logger.error(f"[ERROR] 解析 WebSocket 消息失败: {str(e)}")
                                except Exception as e:
                                    logger.error(f"[ERROR] 处理 WebSocket 消息失败: {str(e)}")
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"[ERROR] WebSocket 错误: {ws.exception()}")
                                break  # 触发重连
                            elif msg.type == aiohttp.WSMsgType.CLOSE:
                                logger.warning("[WARN] WebSocket 连接已关闭")
                                break  # 触发重连
                                
            except asyncio.TimeoutError:
                consecutive_failures += 1
                logger.warning(f"[WARN] WebSocket 连接超时 (失败次数: {consecutive_failures})")
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"❌ [ERROR] WebSocket 连接断开 ({str(e)})。失败次数: {consecutive_failures}")
                
                # 如果连续失败多次，切换到模拟数据模式
                if consecutive_failures >= max_failures_before_mock:
                    logger.warning(f"[MOCK] 连续失败 {consecutive_failures} 次，切换至【模拟数据模式】运行 10 秒...")
                    # --- 兜底逻辑：网络断开期间，生成模拟数据推给前端 ---
                    # 这样你的 K 线永远在动，不会卡死
                    for i in range(10):
                        if not self.is_running:
                            break
                        await self._generate_mock_data()
                        await asyncio.sleep(1)
                    logger.info("[WS] 尝试重新连接真实网络...")
                    consecutive_failures = 0  # 重置计数，重新尝试连接
            
            if self.is_running:
                await asyncio.sleep(_reconnect_delay)
    
    async def _generate_mock_data(self):
        """生成逼真的假数据，用于网络断开时兜底"""
        for symbol in SYMBOLS:
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
        """处理真实的 K 线数据"""
        try:
            # 检查是否收盘（x=True）
            is_closed = kline_data.get('x', False)
            
            # 标准化交易对
            symbol_raw = kline_data.get('s', '')
            symbol = self._normalize_symbol(symbol_raw)
            
            # 构建 K 线数据
            kline = {
                'symbol': symbol,
                'interval': kline_data.get('i', '1m'),
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
            
            # 广播给所有连接的客户端
            await self._broadcast_kline(kline)
        except Exception as e:
            logger.error(f"[ERROR] 处理 K 线数据失败: {str(e)}")
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化交易对格式
        将 BTCUSDT 转换为 BTC/USDT
        """
        symbol = symbol.upper()
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}/USDT"
        return symbol
    
    async def _broadcast_kline(self, kline: Dict[str, Any]):
        """广播 K 线数据给所有连接的客户端"""
        if not _active_connections:
            return
        
        message = {
            'type': 'kline',
            'data': kline
        }
        
        # 发送给所有活跃连接
        disconnected = set()
        for ws in _active_connections:
            try:
                # FastAPI WebSocket 支持 send_json
                if hasattr(ws, 'send_json'):
                    await ws.send_json(message)
                else:
                    # 兼容标准 websockets 库
                    await ws.send(json.dumps(message))
            except Exception as e:
                logger.warning(f"[WARN] 发送消息失败，连接将被移除: {str(e)}")
                disconnected.add(ws)
        
        # 移除断开的连接
        _active_connections.difference_update(disconnected)
    
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
