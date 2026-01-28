"""
合约交易相关 API 端点
提供 U 本位合约交易下单、持仓管理、撤单等功能（Mock 实现）
支持开仓（Long/Short）、平仓、杠杆设置等逻辑
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import time
import uuid
from app.api.deps import get_current_user
from app.db.mock import (
    get_user_assets, 
    update_user_assets, 
    freeze_assets, 
    unfreeze_assets,
    create_order as create_order_in_db,
    get_order,
    update_order_status,
    get_user_orders,
    get_user_positions,
    update_position,
    # 价格相关函数和数据（全局唯一事实来源）
    MOCK_MARKET_PRICES,
    get_market_price,
    save_prices
)

# 创建路由实例
router = APIRouter(prefix="/api/v1/futures", tags=["futures"])

# 交易手续费配置 (合约通常比现货低)
FUTURES_FEE_RATE = 0.0004  # 基础费率：0.04%

# 订单状态常量
ORDER_STATUS = {
    "NEW": "NEW",           # 新建（挂单中）
    "FILLED": "FILLED",     # 完全成交
    "CANCELLED": "CANCELLED"  # 已取消
}

class FuturesOrderRequest(BaseModel):
    """合约交易下单请求模型"""
    symbol: str = Field(..., description="交易对，例如 'BTC/USDT'")
    side: str = Field(..., description="交易方向：'BUY' (做多/开多或平空) 或 'SELL' (做空/开空或平多)")
    type: str = Field(..., description="订单类型：'LIMIT' 或 'MARKET'")
    price: float = Field(..., description="交易价格")
    amount: float = Field(..., gt=0, description="交易数量 (张/币)")
    leverage: int = Field(default=20, ge=1, le=125, description="杠杆倍数")
    margin_type: str = Field(default="ISOLATED", description="保证金模式：ISOLATED (逐仓) 或 CROSS (全仓)")

@router.post("/order")
def create_futures_order(
    request: FuturesOrderRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    创建合约交易订单（智能路由：自动判断开仓/加仓/平仓）
    
    逻辑流程：
    1. 获取用户在当前币种的持仓
    2. 判断订单方向：
       - 无持仓 -> 开仓逻辑
       - 有持仓且同方向 -> 加仓逻辑（更新均价）
       - 有持仓且反方向 -> 平仓逻辑
         - 如果下单数量 <= 持仓数量：平仓
         - 如果下单数量 > 持仓数量：报错"不支持直接反手，请先平仓"
    """
    try:
        address = current_user.get("address").lower()
        symbol = request.symbol.upper()
        current_price = get_market_price(symbol)
        
        if current_price <= 0:
            raise HTTPException(status_code=400, detail=f"不支持的交易对: {symbol}")

        # 1. 获取用户在当前币种的持仓
        existing_positions = get_user_positions(address, symbol)
        order_side = "LONG" if request.side == "BUY" else "SHORT"
        
        # 2. 确定执行价格
        exec_price = request.price if request.type == "LIMIT" else current_price
        
        # 3. 智能路由判断
        if not existing_positions:
            # ========== 场景1: 无持仓 -> 开仓逻辑 ==========
            return _execute_open_position(
                address, symbol, request, exec_price, current_price, order_side
            )
        else:
            # 有持仓，检查方向
            existing_pos = existing_positions[0]
            existing_side = existing_pos.get("side", "").upper()
            
            if existing_side == order_side:
                # ========== 场景2: 同方向 -> 加仓逻辑 ==========
                return _execute_add_position(
                    address, symbol, request, exec_price, current_price, existing_pos, order_side
                )
            else:
                # ========== 场景3: 反方向 -> 平仓逻辑 ==========
                if request.amount > existing_pos["size"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"不支持直接反手。当前持仓: {existing_pos['size']} {symbol.split('/')[0]}，请先平仓后再开反向仓位"
                    )
                
                return _execute_close_position(
                    address, symbol, request, exec_price, current_price, existing_pos
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"合约下单失败: {str(e)}")


def _execute_open_position(
    address: str, symbol: str, request: FuturesOrderRequest,
    exec_price: float, current_price: float, order_side: str
) -> dict:
    """执行开仓逻辑"""
    # 计算名义价值和保证金
    notional_value = exec_price * request.amount
    initial_margin = notional_value / request.leverage
    
    # 检查余额
    assets = get_user_assets(address)
    usdt_balance = assets.get("USDT", 0.0)
    
    if usdt_balance < initial_margin:
        raise HTTPException(
            status_code=400,
            detail=f"保证金不足。所需: {initial_margin:.2f} USDT, 当前可用: {usdt_balance:.2f} USDT"
        )
    
    # 扣除保证金和手续费
    fee = notional_value * FUTURES_FEE_RATE
    assets["USDT"] = usdt_balance - initial_margin - fee
    update_user_assets(address, assets)
    
    # 创建持仓
    timestamp = int(time.time())
    position_data = {
        "symbol": symbol,
        "side": order_side,
        "size": request.amount,
        "entry_price": exec_price,
        "mark_price": current_price,
        "leverage": request.leverage,
        "margin": initial_margin,
        "unrealized_pnl": 0.0,
        "update_time": timestamp
    }
    
    updated_pos = update_position(address, symbol, position_data)
    
    # 创建订单记录
    order_id = f"fut_{uuid.uuid4().hex[:12]}"
    order_record = {
        "order_id": order_id,
        "user_id": address,
        "symbol": symbol,
        "side": request.side,
        "type": request.type,
        "price": exec_price,
        "amount": request.amount,
        "status": "FILLED",
        "timestamp": timestamp,
        "fee": fee,
        "fee_currency": "USDT"
    }
    create_order_in_db(order_record)
    
    return {
        "code": 200,
        "message": "开仓成功",
        "data": {
            "order_id": order_id,
            "action": "OPEN",
            "position": updated_pos,
            "assets": get_user_assets(address)
        }
    }


def _execute_add_position(
    address: str, symbol: str, request: FuturesOrderRequest,
    exec_price: float, current_price: float, existing_pos: dict, order_side: str
) -> dict:
    """执行加仓逻辑（同方向持仓，更新均价）"""
    # 计算新仓位的名义价值和保证金
    new_notional = exec_price * request.amount
    new_margin = new_notional / request.leverage
    
    # 检查余额
    assets = get_user_assets(address)
    usdt_balance = assets.get("USDT", 0.0)
    
    if usdt_balance < new_margin:
        raise HTTPException(
            status_code=400,
            detail=f"保证金不足。所需: {new_margin:.2f} USDT, 当前可用: {usdt_balance:.2f} USDT"
        )
    
    # 计算加权平均开仓价
    old_size = existing_pos["size"]
    old_price = existing_pos["entry_price"]
    new_size = request.amount
    
    # 均价公式：(旧价*旧量 + 新价*新量) / 总数量
    avg_entry_price = (old_price * old_size + exec_price * new_size) / (old_size + new_size)
    total_size = old_size + new_size
    total_margin = existing_pos["margin"] + new_margin
    
    # 扣除保证金和手续费
    fee = new_notional * FUTURES_FEE_RATE
    assets["USDT"] = usdt_balance - new_margin - fee
    update_user_assets(address, assets)
    
    # 更新持仓（使用加权平均价）
    timestamp = int(time.time())
    position_data = {
        "symbol": symbol,
        "side": order_side,
        "size": total_size,
        "entry_price": avg_entry_price,
        "mark_price": current_price,
        "leverage": request.leverage,  # 使用新杠杆（简化处理）
        "margin": total_margin,
        "unrealized_pnl": 0.0,
        "update_time": timestamp
    }
    
    updated_pos = update_position(address, symbol, position_data)
    
    # 创建订单记录
    order_id = f"fut_{uuid.uuid4().hex[:12]}"
    order_record = {
        "order_id": order_id,
        "user_id": address,
        "symbol": symbol,
        "side": request.side,
        "type": request.type,
        "price": exec_price,
        "amount": request.amount,
        "status": "FILLED",
        "timestamp": timestamp,
        "fee": fee,
        "fee_currency": "USDT"
    }
    create_order_in_db(order_record)
    
    return {
        "code": 200,
        "message": "加仓成功",
        "data": {
            "order_id": order_id,
            "action": "ADD",
            "position": updated_pos,
            "assets": get_user_assets(address)
        }
    }


def _execute_close_position(
    address: str, symbol: str, request: FuturesOrderRequest,
    exec_price: float, current_price: float, existing_pos: dict
) -> dict:
    """执行平仓逻辑（反方向订单，自动平仓）"""
    close_amount = request.amount
    
    if close_amount > existing_pos["size"]:
        raise HTTPException(
            status_code=400,
            detail=f"平仓数量超过持仓数量。持仓: {existing_pos['size']}, 平仓: {close_amount}"
        )
    
    # 计算已实现盈亏
    entry_price = existing_pos["entry_price"]
    diff = current_price - entry_price
    if existing_pos["side"] == "SHORT":
        diff = -diff
    
    realized_pnl = diff * close_amount
    
    # 按比例返还保证金
    margin_ratio = close_amount / existing_pos["size"]
    margin_to_return = existing_pos["margin"] * margin_ratio
    
    # 计算平仓手续费
    close_notional = exec_price * close_amount
    fee = close_notional * FUTURES_FEE_RATE
    
    # 更新资产：返还保证金 + 盈亏 - 手续费
    assets = get_user_assets(address)
    assets["USDT"] += (margin_to_return + realized_pnl - fee)
    update_user_assets(address, assets)
    
    # 更新持仓
    new_size = existing_pos["size"] - close_amount
    timestamp = int(time.time())
    
    if new_size <= 0:
        # 全部平仓，删除持仓
        update_position(address, symbol, {"size": 0})
        remaining_pos = None
    else:
        # 部分平仓，更新持仓
        remaining_margin = existing_pos["margin"] - margin_to_return
        position_data = {
            "symbol": symbol,
            "side": existing_pos["side"],
            "size": new_size,
            "entry_price": entry_price,  # 开仓价不变
            "mark_price": current_price,
            "leverage": existing_pos["leverage"],
            "margin": remaining_margin,
            "unrealized_pnl": 0.0,
            "update_time": timestamp
        }
        remaining_pos = update_position(address, symbol, position_data)
    
    # 创建订单记录
    order_id = f"fut_{uuid.uuid4().hex[:12]}"
    order_record = {
        "order_id": order_id,
        "user_id": address,
        "symbol": symbol,
        "side": request.side,
        "type": request.type,
        "price": exec_price,
        "amount": close_amount,
        "status": "FILLED",
        "timestamp": timestamp,
        "fee": fee,
        "fee_currency": "USDT",
        "realized_pnl": realized_pnl
    }
    create_order_in_db(order_record)
    
    return {
        "code": 200,
        "message": "平仓成功" if new_size <= 0 else "部分平仓成功",
        "data": {
            "order_id": order_id,
            "action": "CLOSE",
            "realized_pnl": realized_pnl,
            "fee": fee,
            "remaining_position": remaining_pos,
            "assets": get_user_assets(address)
        }
    }

@router.get("/positions")
def get_futures_positions(current_user: Dict = Depends(get_current_user)):
    """获取用户当前所有持仓"""
    address = current_user.get("address").lower()
    positions = get_user_positions(address)
    
    # 动态更新未实现盈亏
    for pos in positions:
        current_price = get_market_price(pos["symbol"])
        pos["mark_price"] = current_price
        
        # 盈亏计算: (当前价 - 开仓价) * 数量 * 方向
        diff = current_price - pos["entry_price"]
        if pos["side"] == "SHORT":
            diff = -diff
        
        pos["unrealized_pnl"] = diff * pos["size"]
    
    return {
        "code": 200,
        "data": positions
    }

class ClosePositionRequest(BaseModel):
    symbol: str
    amount: float = Field(..., gt=0)
    type: str = Field(default="MARKET") # MARKET 或 LIMIT

@router.post("/close")
def close_futures_position(
    request: ClosePositionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """全平或平掉部分持仓"""
    address = current_user.get("address").lower()
    symbol = request.symbol.upper()
    positions = get_user_positions(address, symbol)
    
    if not positions:
        raise HTTPException(status_code=404, detail="未找到对应持仓")
    
    pos = positions[0]
    if request.amount > pos["size"]:
        raise HTTPException(status_code=400, detail="平仓数量超过持仓数量")

    current_price = get_market_price(symbol)
    
    # 计算实现的盈亏
    diff = current_price - pos["entry_price"]
    if pos["side"] == "SHORT":
        diff = -diff
    
    realized_pnl = diff * request.amount
    
    # 返还保证金 (按比例)
    margin_to_return = (request.amount / pos["size"]) * pos["margin"]
    
    # 更新资产
    assets = get_user_assets(address)
    assets["USDT"] += (margin_to_return + realized_pnl)
    
    # 扣除平仓手续费
    fee = (current_price * request.amount) * FUTURES_FEE_RATE
    assets["USDT"] -= fee
    
    update_user_assets(address, assets)
    
    # 更新持仓信息
    new_size = pos["size"] - request.amount
    if new_size <= 0:
        update_position(address, symbol, {"size": 0})
    else:
        # 按比例减少保证金
        pos["size"] = new_size
        pos["margin"] -= margin_to_return
        update_position(address, symbol, pos)
        
    return {
        "code": 200,
        "message": "平仓成功",
        "data": {
            "realized_pnl": realized_pnl,
            "fee": fee,
            "assets": get_user_assets(address)
        }
    }
# ========== 测试专用接口 (不要上线) ==========

class UpdatePriceRequest(BaseModel):
    """更新价格请求模型"""
    symbol: str = Field(..., description="交易对，例如 'BTC/USDT' 或 'BTC'")
    price: float = Field(..., gt=0, description="新价格")

@router.post("/test/price")
def update_market_price(request: UpdatePriceRequest):
    """
    测试接口：强制修改行情价格，用于测试盈亏和爆仓
    
    注意：此接口仅用于开发测试，生产环境应禁用
    
    请求格式：
    {
        "symbol": "BTC/USDT",
        "price": 85000.0
    }
    
    返回格式：
    {
        "code": 200,
        "message": "价格更新成功",
        "data": {
            "symbol": "BTC/USDT",
            "old_price": 92255.0,
            "new_price": 85000.0
        }
    }
    """
    try:
        # 规范化交易对格式
        symbol = request.symbol.upper()
        if '/' not in symbol:
            symbol = f"{symbol}/USDT"
        
        # 获取旧价格
        old_price = MOCK_MARKET_PRICES.get(symbol, 0.0)
        
        # 修改内存中的价格（全局唯一事实来源）
        MOCK_MARKET_PRICES[symbol] = request.price
        
        # 自动保存到 JSON 文件
        save_prices()
        
        print(f"🔧 [测试接口] 价格更新: {symbol} {old_price} -> {request.price}")
        
        return {
            "code": 200,
            "message": f"价格更新成功: {symbol}",
            "data": {
                "symbol": symbol,
                "old_price": old_price,
                "new_price": request.price
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新价格失败: {str(e)}"
        )