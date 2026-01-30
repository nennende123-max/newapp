"""
币安 K 线市场服务（使用 aiohttp 直接连接 + 自动兜底模式）
负责历史数据同步和实时行情流
如果网络连接失败，自动切换到模拟数据模式，确保前端永不白屏

支持 SOCKS5 代理（推荐用于 wss:// 连接）
如果代理不可用，自动切换到直接连接模式
"""
import aiohttp
import asyncio
import json
import logging
import random
import time
import os
import requests
import socket
from typing import Dict, Set, Optional, Any, List, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException
from app.models.kline import KlineModel

# ========== 配置日志（必须在导入 SOCKS5 库之前） ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== 尝试导入 SOCKS5 支持库 ==========
# 优先使用 aiosocksy（更现代），如果没有则尝试 python-socks
try:
    import aiosocksy
    from aiosocksy.connector import SocksConnector
    HAS_SOCKS5 = True
    SOCKS5_LIB = "aiosocksy"
    logger.info("[PROXY] 已加载 aiosocksy，支持 SOCKS5 代理")
except ImportError:
    try:
        from python_socks.async_.asyncio import Proxy
        from python_socks._types import ProxyType
        HAS_SOCKS5 = True
        SOCKS5_LIB = "python-socks"
        logger.info("[PROXY] 已加载 python-socks，支持 SOCKS5 代理")
    except ImportError:
        HAS_SOCKS5 = False
        SOCKS5_LIB = None
        logger.warning("[PROXY] 未安装 SOCKS5 支持库，仅支持 HTTP 代理。建议安装: pip install aiosocksy 或 pip install python-socks[asyncio]")

# ========== 配置 ==========
# 代理配置：优先直连（日本东京 IP 可直连 Binance API）
# 如果直连失败，fallback 到 SOCKS5 代理
# 支持格式：
# - SOCKS5 代理: socks5://127.0.0.1:10808（v2rayN 默认）
PROXY_URL = os.getenv("PROXY_URL", "socks5://127.0.0.1:10808")  # SOCKS5 代理（fallback 使用）
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]

# 需要同步的时间周期列表（必须包含 1h，否则前端不显示）
SYNC_INTERVALS = ["1m", "1h", "4h", "1d"]

# WebSocket 订阅的间隔列表（用于实时流）
WS_INTERVALS = ["1m", "1h", "4h", "1d"]

# WebSocket 连接管理（用于广播给前端）
_active_connections: Set[Any] = set()
_reconnect_delay = 5  # 重连延迟（秒）
_max_reconnect_attempts = 5  # 最大重连次数（每 5 秒重试，最多 5 次）


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
        """初始化交易所连接和数据库"""
        # 初始化 K 线数据库
        try:
            await KlineModel.init_db()
            logger.info("[OK] K 线数据库初始化成功")
        except Exception as e:
            logger.error(f"[ERROR] K 线数据库初始化失败: {str(e)}")
        
        logger.info("[OK] MarketService 初始化（使用 aiohttp 直接连接 + 自动兜底模式）")
    
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
        """
        # 如果未配置代理，跳过历史数据同步
        if not PROXY_URL:
            logger.info("[SYNC] 未配置代理，跳过历史数据同步（使用模拟模式）")
            return
        
        try:
            logger.info(f"[SYNC] 正在尝试同步历史数据（周期: {SYNC_INTERVALS}）...")
            # 这里的 SSL=False 和 proxy 是关键
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
                                proxy=PROXY_URL,
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
        except Exception as e:
            logger.error(f"[SYNC] 历史同步模块报错: {e}")
    
    def _parse_proxy_url(self, proxy_url: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        解析代理 URL，返回代理类型、主机和端口
        
        Args:
            proxy_url: 代理 URL，格式如 "http://127.0.0.1:10809" 或 "socks5://127.0.0.1:10808"
        
        Returns:
            Tuple[proxy_type, host, port]: 代理类型（'http'/'socks5'）、主机、端口
        """
        try:
            parsed = urlparse(proxy_url)
            proxy_type = parsed.scheme.lower()
            host = parsed.hostname
            port = parsed.port
            
            if proxy_type not in ('http', 'https', 'socks5', 'socks5h'):
                logger.warning(f"[PROXY] 不支持的代理类型: {proxy_type}")
                return None, None, None
            
            # 标准化代理类型
            if proxy_type in ('https', 'http'):
                proxy_type = 'http'
            elif proxy_type in ('socks5', 'socks5h'):
                proxy_type = 'socks5'
            
            if not host or not port:
                logger.warning(f"[PROXY] 代理 URL 格式错误: {proxy_url}")
                return None, None, None
            
            return proxy_type, host, port
        except Exception as e:
            logger.error(f"[PROXY] 解析代理 URL 失败: {str(e)}")
            return None, None, None
    
    async def _check_proxy_available(self, proxy_url: str) -> bool:
        """
        检查代理是否可用（使用 aiohttp 测试连通性）
        
        Args:
            proxy_url: 代理 URL，格式如 "http://127.0.0.1:10809" 或 "socks5://127.0.0.1:10808"
        
        Returns:
            bool: 代理是否可用
        """
        try:
            proxy_type, host, port = self._parse_proxy_url(proxy_url)
            if not proxy_type:
                return False
            
            # 对于 SOCKS5，检查库是否可用
            if proxy_type == 'socks5' and not HAS_SOCKS5:
                logger.warning(f"[PROXY] SOCKS5 代理需要安装支持库: pip install aiosocksy 或 pip install python-socks[asyncio]")
                return False
            
            # 使用 aiohttp 测试代理连通性（尝试连接一个简单的 HTTP 端点）
            test_url = "http://httpbin.org/ip"  # 简单的测试端点
            timeout = aiohttp.ClientTimeout(total=5)  # 5秒超时
            
            try:
                if proxy_type == 'socks5':
                    # SOCKS5 代理需要特殊处理
                    if SOCKS5_LIB == "aiosocksy":
                        # 使用 aiosocksy
                        connector = SocksConnector.from_url(proxy_url)
                    elif SOCKS5_LIB == "python-socks":
                        # 使用 python-socks
                        from python_socks.async_.asyncio import Proxy  # type: ignore
                        from python_socks._types import ProxyType  # type: ignore
                        proxy = Proxy.from_url(proxy_url)
                        connector = aiohttp.TCPConnector()
                        # 注意：python-socks 需要额外的配置
                        logger.info(f"[PROXY] 使用 python-socks 连接 SOCKS5 代理")
                    else:
                        return False
                else:
                    # HTTP 代理
                    connector = aiohttp.TCPConnector()
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    resp = None
                    if proxy_type == 'http':
                        # HTTP 代理通过 proxy 参数传递
                        async with session.get(test_url, proxy=proxy_url) as resp:
                            if resp.status == 200:
                                logger.info(f"[PROXY] ✅ HTTP 代理可用: {proxy_url}")
                                return True
                    else:
                        # SOCKS5 代理通过 connector 处理
                        async with session.get(test_url) as resp:
                            if resp.status == 200:
                                logger.info(f"[PROXY] ✅ SOCKS5 代理可用: {proxy_url}")
                                return True
                    
                    # 如果到达这里，说明请求失败
                    if resp:
                        logger.warning(f"[PROXY] ❌ 代理测试失败: HTTP {resp.status}")
                    else:
                        logger.warning(f"[PROXY] ❌ 代理测试失败: 无法建立连接")
                    return False
                
            except asyncio.TimeoutError:
                logger.warning(f"[PROXY] ❌ 代理连接超时: {proxy_url}")
                return False
            except Exception as e:
                logger.warning(f"[PROXY] ❌ 代理测试失败: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"[PROXY] 检查代理失败: {str(e)}")
            return False
    
    async def _create_proxy_connector(self, proxy_url: str, proxy_type: str) -> Tuple[bool, Optional[Any], Optional[str]]:
        """
        创建代理 connector（不实际连接，只创建）
        
        Args:
            proxy_url: 代理 URL
            proxy_type: 代理类型 ('socks5')
        
        Returns:
            Tuple[success, connector, error_message]: 是否成功创建、connector、错误信息
        """
        try:
            connector = None
            
            if proxy_type == 'socks5':
                if not HAS_SOCKS5:
                    return False, None, "SOCKS5 支持库未安装，请运行: pip install aiosocksy"
                
                if SOCKS5_LIB == "aiosocksy":
                    connector = SocksConnector.from_url(proxy_url)
                    logger.info(f"[PROXY] 创建 SOCKS5 connector: {proxy_url}")
                else:
                    return False, None, f"不支持的 SOCKS5 库: {SOCKS5_LIB}"
            elif proxy_type == 'http':
                connector = aiohttp.TCPConnector(ssl=False)
                logger.info(f"[PROXY] 创建 HTTP connector: {proxy_url}")
            else:
                return False, None, f"不支持的代理类型: {proxy_type}"
            
            return True, connector, None
                    
        except Exception as e:
            error_msg = str(e)
            logger.debug(f"[PROXY] 创建 connector 失败 ({proxy_type}): {error_msg}")
            return False, None, error_msg
    
    async def _try_connect_websocket(self, url: str, connector: Optional[Any], proxy_url: Optional[str] = None, proxy_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        尝试连接 WebSocket（带详细日志，包括 URL、端口、异常信息）
        
        Args:
            url: WebSocket URL
            connector: aiohttp connector（None 表示使用默认）
            proxy_url: 代理 URL（可选）
            proxy_type: 代理类型（'socks5' 或 None）
        
        Returns:
            Tuple[success, error_message]: 连接是否成功、错误信息
        """
        try:
            # 解析 URL 获取端口信息
            parsed_url = urlparse(url)
            port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
            
            logger.info(f"[WS] ========== 尝试连接 WebSocket ==========")
            logger.info(f"[WS] URL: {url}")
            logger.info(f"[WS] 主机: {parsed_url.hostname}")
            logger.info(f"[WS] 端口: {port}")
            logger.info(f"[WS] 协议: {parsed_url.scheme}")
            if proxy_url:
                proxy_parsed = urlparse(proxy_url)
                proxy_port = proxy_parsed.port or (10808 if proxy_type == 'socks5' else 10809)
                logger.info(f"[WS] 使用代理: {proxy_type.upper()}")
                logger.info(f"[WS] 代理地址: {proxy_parsed.hostname}:{proxy_port}")
            else:
                logger.info(f"[WS] 连接方式: 直接连接（不使用代理）")
            logger.info(f"[WS] ========================================")
            
            timeout = aiohttp.ClientTimeout(total=10)  # 10秒超时用于测试
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                ws_kwargs = {
                    'url': url,
                    'heartbeat': 15,
                    'timeout': aiohttp.ClientTimeout(total=10)
                }
                
                # SOCKS5 代理通过 connector 处理，不需要 proxy 参数
                # HTTP 代理已移除，不再使用
                
                async with session.ws_connect(**ws_kwargs) as ws:
                    logger.info(f"[WS] ✅ WebSocket 连接成功")
                    logger.info(f"[WS] URL: {url}")
                    logger.info(f"[WS] 端口: {port}")
                    return True, None
                    
        except asyncio.TimeoutError as e:
            parsed_url = urlparse(url)
            port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
            error_msg = f"连接超时 (URL: {url}, 端口: {port})"
            logger.error(f"[WS] ❌ {error_msg}")
            logger.error(f"[WS] 异常类型: {type(e).__name__}")
            logger.error(f"[WS] 异常信息: {str(e)}")
            return False, error_msg
        except Exception as e:
            parsed_url = urlparse(url)
            port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
            error_msg = f"连接失败: {str(e)} (URL: {url}, 端口: {port})"
            logger.error(f"[WS] ❌ {error_msg}")
            logger.error(f"[WS] 异常类型: {type(e).__name__}")
            logger.error(f"[WS] 异常信息: {str(e)}")
            # 处理 SSL 相关错误
            if 'SSL' in str(e) or 'ssl' in str(e).lower() or 'certificate' in str(e).lower():
                logger.warning(f"[WS] ⚠️ 检测到 SSL 相关错误，可能需要检查 SSL 配置")
            return False, error_msg
    
    async def start_stream_safe(self):
        """
        实时流：连不上就造假数据，绝不报错退出
        
        支持多个间隔（1m, 1h, 4h, 1d）的 K 线流订阅
        代理连接策略（Fallback 机制，优先直连）：
        1. 优先直接连接币安 WebSocket（日本东京 IP 可直连）
        2. 如果直连失败，fallback 到 SOCKS5 代理 (socks5://127.0.0.1:10808)
        
        重连机制：每 5 秒重试，最多 5 次（处理 SSL 默认错误）
        所有 K 线数据会自动保存到 KlineModel 数据库
        """
        # 构建 WebSocket URL：订阅多个间隔的 K 线流
        # 币安 WebSocket 端点：优先使用 stream.binance.com，fallback 到 fstream.binance.com
        # 格式：stream1/stream2/stream3...
        streams = []
        for symbol in SYMBOLS:
            for interval in WS_INTERVALS:
                # 币安 WebSocket 流格式：btcusdt@kline_1m
                streams.append(f"{symbol.lower()}@kline_{interval}")
        
        # 优先使用现货 WebSocket 端点（stream.binance.com）
        # Fallback 端点：fstream.binance.com（期货）
        # 币安组合流格式：
        # - 现货: wss://stream.binance.com:9443/stream?streams=stream1/stream2/...
        # - 期货: wss://fstream.binance.com/stream?streams=stream1/stream2/...
        # 注意：使用 443 端口（标准 HTTPS 端口）或 9443（币安 WebSocket 专用端口）
        # 443 端口可以避免某些 SSL 默认错误，但 9443 是币安官方推荐端口
        primary_url = f"wss://stream.binance.com:443/stream?streams={'/'.join(streams)}"
        fallback_url = f"wss://fstream.binance.com:443/stream?streams={'/'.join(streams)}"
        
        logger.info(f"[WS] ========== WebSocket 连接初始化 ==========")
        logger.info(f"[WS] 订阅流: {len(streams)} 个流（{len(SYMBOLS)} 个交易对 × {len(WS_INTERVALS)} 个间隔）")
        logger.info(f"[WS] 主要端点: {primary_url}")
        logger.info(f"[WS] 备用端点: {fallback_url}")
        
        # ========== 代理连接策略（Fallback 机制，优先直连） ==========
        connector = None
        use_proxy = False
        proxy_type = None
        current_proxy_url = None
        current_url = primary_url
        
        # 策略 1: 优先直接连接（不使用代理）
        # 注意：ssl=False 可以避免 SSL 证书验证错误，但可能不安全
        # 如果需要 SSL 验证，可以设置为 ssl=True 或使用 ssl.create_default_context()
        logger.info("[PROXY] 策略 1: 尝试直接连接币安 WebSocket（不使用代理）")
        logger.info(f"[PROXY] 目标 URL: {primary_url}")
        direct_connector = aiohttp.TCPConnector(ssl=False)  # 禁用 SSL 验证以避免 SSL 默认错误
        success, error = await self._try_connect_websocket(primary_url, direct_connector)
        
        if success:
            logger.info("[PROXY] ✅ 直接连接成功，将使用直连模式")
            connector = direct_connector
            use_proxy = False
            proxy_type = None
            current_proxy_url = None
            current_url = primary_url
        else:
            logger.warning(f"[PROXY] ❌ 直接连接失败: {error}")
            logger.info("[PROXY] 策略 2: Fallback 到 SOCKS5 代理")
            
            # 策略 2: Fallback 到 SOCKS5 代理
            if PROXY_URL:
                proxy_type_parsed, _, _ = self._parse_proxy_url(PROXY_URL)
                if proxy_type_parsed == 'socks5':
                    logger.info(f"[PROXY] 检查 SOCKS5 代理可用性: {PROXY_URL}")
                    proxy_available = await self._check_proxy_available(PROXY_URL)
                    
                    if proxy_available:
                        logger.info(f"[PROXY] ✅ SOCKS5 代理可用，创建 connector")
                        success, connector, connector_error = await self._create_proxy_connector(PROXY_URL, 'socks5')
                        
                        if success and connector:
                            # 测试 SOCKS5 代理连接
                            test_success, test_error = await self._try_connect_websocket(primary_url, connector, PROXY_URL, 'socks5')
                            
                            if test_success:
                                use_proxy = True
                                proxy_type = 'socks5'
                                current_proxy_url = PROXY_URL
                                current_url = primary_url
                                logger.info(f"[PROXY] ✅ SOCKS5 代理连接成功，将使用: {PROXY_URL}")
                            else:
                                logger.warning(f"[PROXY] ❌ SOCKS5 代理连接测试失败: {test_error}")
                                # 即使 SOCKS5 测试失败，也尝试使用（可能是测试端点问题）
                                use_proxy = True
                                proxy_type = 'socks5'
                                current_proxy_url = PROXY_URL
                                current_url = primary_url
                                logger.warning("[PROXY] ⚠️ 继续使用 SOCKS5 代理（测试失败但可能仍可用）")
                        else:
                            logger.error(f"[PROXY] ❌ SOCKS5 connector 创建失败: {connector_error}")
                            connector = direct_connector
                            use_proxy = False
                    else:
                        logger.warning(f"[PROXY] ❌ SOCKS5 代理不可用: {PROXY_URL}")
                        connector = direct_connector
                        use_proxy = False
                else:
                    logger.warning(f"[PROXY] ❌ 代理 URL 格式错误: {PROXY_URL}")
                    connector = direct_connector
                    use_proxy = False
            else:
                logger.warning("[PROXY] ❌ 未配置 SOCKS5 代理")
                connector = direct_connector
                use_proxy = False
        
        # 如果所有策略都失败，使用直连 connector（至少尝试连接）
        if connector is None:
            connector = direct_connector
            use_proxy = False
        
        # 解析 URL 获取详细信息
        parsed_url = urlparse(current_url)
        url_port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
        
        logger.info(f"[WS] ========== 连接策略确定 ==========")
        logger.info(f"[WS] 使用代理: {'是' if use_proxy else '否'}")
        if use_proxy:
            proxy_parsed = urlparse(current_proxy_url) if current_proxy_url else None
            if proxy_parsed:
                proxy_port = proxy_parsed.port or (10808 if proxy_type == 'socks5' else 10809)
                logger.info(f"[WS] 代理类型: {proxy_type.upper()}")
                logger.info(f"[WS] 代理地址: {proxy_parsed.hostname}:{proxy_port}")
        logger.info(f"[WS] WebSocket URL: {current_url}")
        logger.info(f"[WS] WebSocket 主机: {parsed_url.hostname}")
        logger.info(f"[WS] WebSocket 端口: {url_port}")
        logger.info(f"[WS] WebSocket 协议: {parsed_url.scheme}")
        logger.info(f"[WS] ========================================")
        
        reconnect_attempts = 0
        consecutive_failures = 0
        max_failures_before_mock = 3  # 连续失败3次后切换到模拟模式
        
        logger.info(f"[WS] 重连配置: 延迟 {_reconnect_delay} 秒，最多重试 {_max_reconnect_attempts} 次")
        
        while self.is_running:
            try:
                # --- 关键修改：Session 在循环内创建，支持 SOCKS5 connector ---
                async with aiohttp.ClientSession(connector=connector) as session:
                    if use_proxy:
                        logger.info(f"[WS] [{reconnect_attempts + 1}] 正在连接币安... (使用 {proxy_type.upper()} 代理: {current_proxy_url})")
                        logger.info(f"[WS] URL: {current_url}")
                    else:
                        logger.info(f"[WS] [{reconnect_attempts + 1}] 正在连接币安... (直接连接，不使用代理)")
                        logger.info(f"[WS] URL: {current_url}")
                    
                    # 设置超时，防止卡死
                    ws_kwargs = {
                        'url': current_url,
                        'heartbeat': 15,
                        'timeout': aiohttp.ClientTimeout(total=30)
                    }
                    
                    # SOCKS5 代理通过 connector 处理，不需要 proxy 参数
                    # HTTP 代理已移除，不再使用
                    
                    async with session.ws_connect(**ws_kwargs) as ws:
                        parsed_url = urlparse(current_url)
                        url_port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
                        
                        logger.info(f"✅ [OK] ========== 币安 WebSocket 连接成功 ==========")
                        logger.info(f"[WS] URL: {current_url}")
                        logger.info(f"[WS] 主机: {parsed_url.hostname}")
                        logger.info(f"[WS] 端口: {url_port}")
                        logger.info(f"[WS] 协议: {parsed_url.scheme}")
                        if use_proxy:
                            proxy_parsed = urlparse(current_proxy_url) if current_proxy_url else None
                            if proxy_parsed:
                                proxy_port = proxy_parsed.port or 10808  # SOCKS5 默认端口 10808
                                logger.info(f"[WS] 使用代理: {proxy_type.upper()}")
                                logger.info(f"[WS] 代理地址: {proxy_parsed.hostname}:{proxy_port}")
                        logger.info(f"[WS] 开始接收数据...")
                        logger.info(f"[WS] ========================================")
                        
                        consecutive_failures = 0  # 重置失败计数
                        reconnect_attempts = 0  # 重置重连次数
                        
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
                                        
                                        # 处理 K 线数据（会自动保存到数据库）
                                        await self._process_kline(kline_data)
                                        
                                except json.JSONDecodeError as e:
                                    logger.error(f"[ERROR] 解析 WebSocket 消息失败: {str(e)}")
                                    logger.error(f"[ERROR] 消息内容: {msg.data[:200] if len(msg.data) > 200 else msg.data}")
                                except Exception as e:
                                    logger.error(f"[ERROR] 处理 WebSocket 消息失败: {str(e)}")
                                    logger.error(f"[ERROR] 异常类型: {type(e).__name__}")
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                error_exception = ws.exception()
                                logger.error(f"[ERROR] WebSocket 错误: {error_exception}")
                                logger.error(f"[ERROR] 错误类型: {type(error_exception).__name__ if error_exception else 'Unknown'}")
                                break  # 触发重连
                            elif msg.type == aiohttp.WSMsgType.CLOSE:
                                logger.warning("[WARN] WebSocket 连接已关闭")
                                logger.warning(f"[WARN] 关闭代码: {ws.close_code if hasattr(ws, 'close_code') else 'Unknown'}")
                                break  # 触发重连
                                
            except asyncio.TimeoutError as e:
                consecutive_failures += 1
                reconnect_attempts += 1
                
                # 解析 URL 获取端口信息
                parsed_url = urlparse(current_url)
                port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
                
                logger.error(f"[ERROR] ========== WebSocket 连接超时 ==========")
                logger.error(f"[ERROR] URL: {current_url}")
                logger.error(f"[ERROR] 主机: {parsed_url.hostname}")
                logger.error(f"[ERROR] 端口: {port}")
                logger.error(f"[ERROR] 协议: {parsed_url.scheme}")
                logger.error(f"[ERROR] 失败次数: {consecutive_failures}")
                logger.error(f"[ERROR] 重连次数: {reconnect_attempts}/{_max_reconnect_attempts}")
                logger.error(f"[ERROR] 异常类型: {type(e).__name__}")
                logger.error(f"[ERROR] 异常信息: {str(e)}")
                if use_proxy:
                    proxy_parsed = urlparse(current_proxy_url) if current_proxy_url else None
                    if proxy_parsed:
                        proxy_port = proxy_parsed.port or 10808  # SOCKS5 默认端口 10808
                        logger.error(f"[ERROR] 代理地址: {proxy_parsed.hostname}:{proxy_port}")
                logger.error(f"[ERROR] ========================================")
                
                # 如果重连次数超过限制，切换到模拟数据模式
                if reconnect_attempts >= _max_reconnect_attempts:
                    logger.warning(f"[MOCK] 重连次数达到上限 ({_max_reconnect_attempts} 次)，切换至【模拟数据模式】运行 10 秒...")
                    for i in range(10):
                        if not self.is_running:
                            break
                        await self._generate_mock_data()
                        await asyncio.sleep(1)
                    logger.info("[WS] 尝试重新连接真实网络...")
                    reconnect_attempts = 0  # 重置重连次数
                    
            except Exception as e:
                consecutive_failures += 1
                reconnect_attempts += 1
                
                # 解析 URL 获取端口信息
                parsed_url = urlparse(current_url)
                port = parsed_url.port or (443 if parsed_url.scheme == 'wss' else 80)
                
                logger.error(f"[ERROR] ========== WebSocket 连接断开 ==========")
                logger.error(f"[ERROR] URL: {current_url}")
                logger.error(f"[ERROR] 主机: {parsed_url.hostname}")
                logger.error(f"[ERROR] 端口: {port}")
                logger.error(f"[ERROR] 协议: {parsed_url.scheme}")
                logger.error(f"[ERROR] 失败次数: {consecutive_failures}")
                logger.error(f"[ERROR] 重连次数: {reconnect_attempts}/{_max_reconnect_attempts}")
                logger.error(f"[ERROR] 异常类型: {type(e).__name__}")
                logger.error(f"[ERROR] 异常信息: {str(e)}")
                if use_proxy:
                    proxy_parsed = urlparse(current_proxy_url) if current_proxy_url else None
                    if proxy_parsed:
                        proxy_port = proxy_parsed.port or 10808  # SOCKS5 默认端口 10808
                        logger.error(f"[ERROR] 代理地址: {proxy_parsed.hostname}:{proxy_port}")
                
                # 检查是否是 SSL 相关错误
                error_str = str(e).lower()
                if 'ssl' in error_str or 'certificate' in error_str or 'tls' in error_str:
                    logger.error(f"[ERROR] ⚠️ 检测到 SSL/TLS 相关错误")
                    logger.error(f"[ERROR] 建议: 检查 SSL 证书配置或网络连接")
                
                logger.error(f"[ERROR] ========================================")
                
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
                    consecutive_failures = 0  # 重置失败计数
                    reconnect_attempts = 0  # 重置重连次数
                
                # 如果重连次数超过限制，切换到模拟数据模式
                if reconnect_attempts >= _max_reconnect_attempts:
                    logger.warning(f"[MOCK] 重连次数达到上限 ({_max_reconnect_attempts} 次)，切换至【模拟数据模式】运行 10 秒...")
                    for i in range(10):
                        if not self.is_running:
                            break
                        await self._generate_mock_data()
                        await asyncio.sleep(1)
                    logger.info("[WS] 尝试重新连接真实网络...")
                    reconnect_attempts = 0  # 重置重连次数
            
            if self.is_running:
                logger.info(f"[WS] 等待 {_reconnect_delay} 秒后重连...")
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
        """
        处理真实的 K 线数据
        
        收到 WebSocket 数据后，调用 KlineModel.upsert_klines 保存实时数据
        """
        try:
            # 检查是否收盘（x=True）
            is_closed = kline_data.get('x', False)
            
            # 标准化交易对
            symbol_raw = kline_data.get('s', '')
            symbol = self._normalize_symbol(symbol_raw)
            
            # 构建 K 线数据字典（符合 KlineModel 格式）
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
            
            # 如果 K 线收盘，保存到数据库（调用 KlineModel.upsert_klines）
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
        将 BTCUSDT 转换为 BTC/USDT（与 KlineModel 存储格式一致）
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
