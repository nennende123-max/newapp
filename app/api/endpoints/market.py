"""
K 线市场数据 API 端点
提供历史 K 线查询和实时 WebSocket 推送
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
import logging

from app.models.kline import KlineModel
from app.services.market_service import (
    market_service,
    register_websocket,
    unregister_websocket,
    get_current_price,
    get_klines,
    get_order_book
)

logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/price")
def get_price(symbol: str = Query(..., description="交易对，如 BTCUSDT")):
    """获取当前价格"""
    return {"price": get_current_price(symbol)}


@router.get("/kline")
async def get_kline(
    symbol: str = Query(..., description="交易对，如 BTCUSDT 或 BTC/USDT"),
    interval: str = Query("1h", description="K线间隔，如 1m, 5m, 1h"),
    limit: int = Query(1000, description="数据条数，最大1000")
):
    """
    获取 K 线数据（从数据库查询）
    
    返回格式：数组列表，每个元素为 [timestamp(毫秒), open, high, low, close, volume]
    """
    # 清理 symbol 字符串：移除 "BINANCE:", "/", "USDT" 等杂质
    # 例如：BINANCE:BTCUSDT -> BTCUSDT, BTC/USDT -> BTCUSDT
    cleaned_symbol = symbol.upper()
    cleaned_symbol = cleaned_symbol.replace("BINANCE:", "")
    cleaned_symbol = cleaned_symbol.replace("/", "")
    
    # 调用 market_service.get_kline_data 获取数据
    kline_data = await market_service.get_kline_data(cleaned_symbol, interval, limit)
    return kline_data


@router.get("/klines")
async def get_klines_endpoint(
    symbol: str = Query(..., description="交易对，如 BTCUSDT"),
    interval: str = Query("1m", description="K线间隔，如 1m, 5m, 1h"),
    limit: int = Query(1000, description="数据条数，最大1000")
):
    """
    获取 K 线数据（从币安 REST API 获取）
    
    返回格式：数组列表，每个元素为 [timestamp(毫秒), open, high, low, close, volume]
    与 /kline 接口格式一致，便于前端统一处理
    """
    # 清理 symbol 字符串：移除 "BINANCE:", "/", "USDT" 等杂质
    cleaned_symbol = symbol.upper()
    cleaned_symbol = cleaned_symbol.replace("BINANCE:", "")
    cleaned_symbol = cleaned_symbol.replace("/", "")
    
    # 调用 get_klines 获取数据（从币安 REST API）
    klines_dict = get_klines(cleaned_symbol, interval, min(limit, 1000))
    
    # 转换为数组格式：[[timestamp(ms), open, high, low, close, volume], ...]
    result = [
        [
            kline["time"],      # timestamp (毫秒)
            kline["open"],      # open
            kline["high"],      # high
            kline["low"],       # low
            kline["close"],     # close
            kline["volume"]      # volume
        ]
        for kline in klines_dict
    ]
    
    logger.info(f"[API] /klines: symbol={cleaned_symbol}, interval={interval}, limit={limit}, 返回 {len(result)} 条数据")
    return result


@router.get("/orderbook")
def get_orderbook_endpoint(
    symbol: str = Query(..., description="交易对，如 BTCUSDT"),
    limit: int = Query(20, description="盘口深度，最大500")
):
    """获取订单簿（盘口数据）"""
    return get_order_book(symbol, limit)


@router.websocket("/ws/kline")
async def websocket_kline(websocket: WebSocket):
    """
    K 线实时推送 WebSocket 接口
    
    前端连接此接口后，后端将从币安收到的实时数据转发给前端
    
    消息格式：
    发送给客户端：
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
    """
    await websocket.accept()
    await register_websocket(websocket)
    
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "K 线实时推送已连接"
        })
        
        # 保持连接，等待消息
        while True:
            # 可以接收客户端的心跳或订阅请求
            try:
                data = await websocket.receive_text()
                # 解析客户端消息（可选）
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    pass
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        logger.info("[WS] 客户端主动断开连接")
    except Exception as e:
        logger.error(f"[ERROR] WebSocket 错误: {str(e)}")
    finally:
        await unregister_websocket(websocket)
