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
def get_kline(
    symbol: str = Query(..., description="交易对，如 BTCUSDT"),
    interval: str = Query("1m", description="K线间隔，如 1m, 5m, 1h"),
    limit: int = Query(500, description="数据条数，最大1000")
):
    """获取 K 线数据"""
    return get_klines(symbol, interval, limit)


@router.get("/klines")
def get_klines_endpoint(
    symbol: str = Query(..., description="交易对，如 BTCUSDT"),
    interval: str = Query("1m", description="K线间隔，如 1m, 5m, 1h"),
    limit: int = Query(500, description="数据条数，最大1000")
):
    """获取 K 线数据（别名端点）"""
    return get_klines(symbol, interval, limit)


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
