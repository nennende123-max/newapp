"""
合约交易服务层
提供止盈止损检查、强平检查等业务逻辑
"""
import time
import uuid
from typing import Optional
from app.db.mock import (
    MOCK_POSITIONS,
    get_market_price,
    get_user_assets,
    update_user_assets,
    create_order as create_order_in_db,
    update_position,
    save_prices
)


def check_tpsl_triggers(new_price: float, symbol: str) -> list:
    """
    检查并执行止盈止损触发逻辑
    
    功能：
    1. 遍历所有持仓
    2. 检查止盈止损条件
    3. 如果触发，立即市价平仓
    4. 同时检查强平条件
    
    逻辑：
    - 多单（LONG）：
      * 止损：如果 new_price <= stop_loss_price -> 立即平仓
      * 止盈：如果 new_price >= take_profit_price -> 立即平仓
    - 空单（SHORT）：
      * 止损：如果 new_price >= stop_loss_price -> 立即平仓
      * 止盈：如果 new_price <= take_profit_price -> 立即平仓
    
    Args:
        new_price: 新的市场价格
        symbol: 交易对，例如 "BTC/USDT"
        
    Returns:
        list: 被触发的持仓信息列表（用于日志记录）
    """
    triggered_positions = []
    
    # 规范化交易对格式
    symbol_upper = symbol.upper()
    if '/' not in symbol_upper:
        symbol_upper = f"{symbol_upper}/USDT"
    
    # 遍历所有持仓（使用列表副本，避免迭代时修改原列表）
    positions_to_check = list(MOCK_POSITIONS)
    
    for pos in positions_to_check:
        pos_symbol = pos.get("symbol", "")
        user_address = pos.get("user_id") or pos.get("address", "")
        
        # 只检查匹配的交易对
        if pos_symbol != symbol_upper or not user_address:
            continue
        
        # 获取持仓关键信息
        side = pos.get("side", "LONG").upper()
        size = float(pos.get("size", 0))
        entry_price = float(pos.get("entry_price", 0))
        margin = float(pos.get("margin", 0))
        leverage = pos.get("leverage", 20)
        
        # 跳过无效持仓
        if size <= 0 or entry_price <= 0:
            continue
        
        # 获取止盈止损价格
        stop_loss_price = pos.get("stop_loss_price")
        take_profit_price = pos.get("take_profit_price")
        
        # 检查强平条件（优先于止盈止损）
        liquidation_price = float(pos.get("liquidation_price", 0))
        should_liquidate = False
        
        if liquidation_price > 0:
            if side == "LONG":
                # 多单：当前价 <= 强平价 -> 强平
                if new_price <= liquidation_price:
                    should_liquidate = True
            else:  # SHORT
                # 空单：当前价 >= 强平价 -> 强平
                if new_price >= liquidation_price:
                    should_liquidate = True
        
        # 检查止盈止损条件
        should_close_tpsl = False
        tpsl_reason = ""
        
        if stop_loss_price is not None and stop_loss_price > 0:
            if side == "LONG":
                # 多单止损：价格 <= 止损价
                if new_price <= stop_loss_price:
                    should_close_tpsl = True
                    tpsl_reason = "STOP_LOSS"
            else:  # SHORT
                # 空单止损：价格 >= 止损价
                if new_price >= stop_loss_price:
                    should_close_tpsl = True
                    tpsl_reason = "STOP_LOSS"
        
        if take_profit_price is not None and take_profit_price > 0:
            if side == "LONG":
                # 多单止盈：价格 >= 止盈价
                if new_price >= take_profit_price:
                    should_close_tpsl = True
                    tpsl_reason = "TAKE_PROFIT"
            else:  # SHORT
                # 空单止盈：价格 <= 止盈价
                if new_price <= take_profit_price:
                    should_close_tpsl = True
                    tpsl_reason = "TAKE_PROFIT"
        
        # 执行平仓逻辑
        if should_liquidate:
            # 强平：保证金归零，创建强平订单
            timestamp = int(time.time())
            order_id = f"fut_liq_{uuid.uuid4().hex[:12]}"
            liquidation_side = "SELL" if side == "LONG" else "BUY"
            realized_pnl = -margin  # 强平时亏损全部保证金
            
            liquidation_order = {
                "order_id": order_id,
                "user_id": user_address,
                "symbol": symbol_upper,
                "side": liquidation_side,
                "type": "LIQUIDATION",
                "price": new_price,
                "amount": size,
                "leverage": leverage,
                "status": "FILLED",
                "timestamp": timestamp,
                "create_time": timestamp,
                "fee": 0.0,
                "fee_currency": "USDT",
                "realized_pnl": realized_pnl,
                "margin": margin,
                "margin_type": pos.get("margin_type", "ISOLATED"),
                "market_type": "futures",
                "liquidation_price": liquidation_price,
                "entry_price": entry_price
            }
            
            create_order_in_db(liquidation_order)
            update_position(user_address, symbol_upper, {"size": 0})
            
            triggered_positions.append({
                "user_address": user_address,
                "symbol": symbol_upper,
                "side": side,
                "reason": "LIQUIDATION",
                "order_id": order_id,
                "price": new_price,
                "realized_pnl": realized_pnl
            })
            
            print(f"\n{'='*60}")
            print(f"[LIQUIDATION] User {user_address[:8]}... Position {symbol_upper} CLOSED")
            print(f"  Side: {side}")
            print(f"  Entry Price: {entry_price:.2f}")
            print(f"  Liquidation Price: {liquidation_price:.2f}")
            print(f"  Current Price: {new_price:.2f}")
            print(f"  Size: {size}")
            print(f"  Margin Lost: {margin:.2f} USDT")
            print(f"  Realized PnL: {realized_pnl:.2f} USDT")
            print(f"  Liquidation Order ID: {order_id}")
            print(f"{'='*60}\n")
            
        elif should_close_tpsl:
            # 止盈止损平仓：正常平仓，返还保证金和盈亏
            # 计算已实现盈亏
            price_diff = new_price - entry_price
            if side == "SHORT":
                price_diff = -price_diff
            
            realized_pnl = price_diff * size
            
            # 返还保证金
            assets = get_user_assets(user_address)
            assets["USDT"] += (margin + realized_pnl)
            
            # 扣除平仓手续费
            FUTURES_FEE_RATE = 0.0004
            fee = (new_price * size) * FUTURES_FEE_RATE
            assets["USDT"] -= fee
            
            update_user_assets(user_address, assets)
            
            # 创建平仓订单记录
            timestamp = int(time.time())
            order_id = f"fut_tpsl_{uuid.uuid4().hex[:12]}"
            close_side = "SELL" if side == "LONG" else "BUY"
            
            tpsl_order = {
                "order_id": order_id,
                "user_id": user_address,
                "symbol": symbol_upper,
                "side": close_side,
                "type": "MARKET",  # 市价单
                "price": new_price,
                "amount": size,
                "status": "FILLED",
                "timestamp": timestamp,
                "create_time": timestamp,
                "fee": fee,
                "fee_currency": "USDT",
                "realized_pnl": realized_pnl,
                "market_type": "futures",
                "tpsl_reason": tpsl_reason,  # 记录触发原因
                "stop_loss_price": stop_loss_price if tpsl_reason == "STOP_LOSS" else None,
                "take_profit_price": take_profit_price if tpsl_reason == "TAKE_PROFIT" else None
            }
            
            create_order_in_db(tpsl_order)
            update_position(user_address, symbol_upper, {"size": 0})
            
            triggered_positions.append({
                "user_address": user_address,
                "symbol": symbol_upper,
                "side": side,
                "reason": tpsl_reason,
                "order_id": order_id,
                "price": new_price,
                "realized_pnl": realized_pnl,
                "stop_loss_price": stop_loss_price,
                "take_profit_price": take_profit_price
            })
            
            print(f"\n{'='*60}")
            print(f"[TPSL TRIGGER] User {user_address[:8]}... Position {symbol_upper} CLOSED")
            print(f"  Side: {side}")
            print(f"  Entry Price: {entry_price:.2f}")
            print(f"  Current Price: {new_price:.2f}")
            print(f"  Trigger Reason: {tpsl_reason}")
            if tpsl_reason == "STOP_LOSS":
                print(f"  Stop Loss Price: {stop_loss_price:.2f}")
            elif tpsl_reason == "TAKE_PROFIT":
                print(f"  Take Profit Price: {take_profit_price:.2f}")
            print(f"  Size: {size}")
            print(f"  Margin Returned: {margin:.2f} USDT")
            print(f"  Realized PnL: {realized_pnl:.2f} USDT")
            print(f"  Fee: {fee:.2f} USDT")
            print(f"  Order ID: {order_id}")
            print(f"{'='*60}\n")
    
    return triggered_positions
