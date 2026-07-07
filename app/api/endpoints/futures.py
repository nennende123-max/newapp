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
    save_prices,
    MOCK_ORDERS
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
    1. 获取当前市场价格
    2. 对于限价单，判断价格是否满足立即成交条件：
       - 限价买入（Long）：只有当 委托价格 >= 当前市场价格 时，才立即成交
       - 限价卖出（Short）：只有当 委托价格 <= 当前市场价格 时，才立即成交
    3. 如果不满足立即成交条件，创建 PENDING 订单（挂单），冻结保证金
    4. 如果满足立即成交条件，执行智能路由判断：
       - 无持仓 -> 开仓逻辑
       - 有持仓且同方向 -> 加仓逻辑（更新均价）
       - 有持仓且反方向 -> 平仓逻辑
    """
    try:
        address = current_user.get("address").lower()
        symbol = request.symbol.upper()
        current_price = get_market_price(symbol)
        
        if current_price <= 0:
            raise HTTPException(status_code=400, detail=f"不支持的交易对: {symbol}")

        # 1. 对于限价单，判断是否满足立即成交条件
        if request.type == "LIMIT":
            should_execute_immediately = False
            
            if request.side == "BUY":
                # 限价买入（Long）：只有当 委托价格 >= 当前市场价格 时，才立即成交
                should_execute_immediately = request.price >= current_price
            else:  # SELL
                # 限价卖出（Short）：只有当 委托价格 <= 当前市场价格 时，才立即成交
                should_execute_immediately = request.price <= current_price
            
            if not should_execute_immediately:
                # ========== 限价单不满足立即成交条件，创建挂单 ==========
                return _create_pending_order(
                    address, symbol, request, current_price
                )
        
        # 2. 满足立即成交条件（市价单或满足条件的限价单），执行智能路由
        # 获取用户在当前币种的持仓
        existing_positions = get_user_positions(address, symbol)
        order_side = "LONG" if request.side == "BUY" else "SHORT"
        
        # 确定执行价格
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
        # 不吞掉错误：把完整堆栈打印到服务端控制台，方便定位 500 真实原因
        import traceback
        print("\n" + "=" * 80)
        print("[ERROR] 合约下单发生未捕获异常，完整堆栈如下：")
        print(f"[ERROR] 请求参数: symbol={getattr(request, 'symbol', None)}, "
              f"side={getattr(request, 'side', None)}, type={getattr(request, 'type', None)}, "
              f"price={getattr(request, 'price', None)}, amount={getattr(request, 'amount', None)}, "
              f"leverage={getattr(request, 'leverage', None)}")
        traceback.print_exc()
        print("=" * 80 + "\n")
        # detail 中带上真实异常信息，前端可直接展示
        raise HTTPException(status_code=500, detail=f"合约下单失败: {str(e)}")


def _create_pending_order(
    address: str, symbol: str, request: FuturesOrderRequest,
    current_price: float
) -> dict:
    """
    创建限价单挂单（PENDING状态）
    
    当限价单价格不满足立即成交条件时调用：
    - 限价买入（Long）：委托价格 < 当前市场价格
    - 限价卖出（Short）：委托价格 > 当前市场价格
    
    逻辑：
    1. 冻结保证金（USDT）
    2. 创建 NEW 状态的订单记录
    3. 不创建持仓
    """
    # 计算名义价值和保证金
    notional_value = request.price * request.amount
    initial_margin = notional_value / request.leverage
    
    # 检查余额
    assets = get_user_assets(address)
    usdt_balance = assets.get("USDT", 0.0)
    
    if usdt_balance < initial_margin:
        raise HTTPException(
            status_code=400,
            detail=f"保证金不足。所需: {initial_margin:.2f} USDT, 当前可用: {usdt_balance:.2f} USDT"
        )
    
    # 冻结保证金（不扣除，只是冻结）
    try:
        updated_assets = freeze_assets(address, "USDT", initial_margin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 创建订单记录（PENDING状态）
    # 必须在函数内部动态获取时间戳，不能使用默认参数或模块级变量
    timestamp = int(time.time())
    order_id = f"fut_{uuid.uuid4().hex[:12]}"
    order_record = {
        "order_id": order_id,
        "user_id": address,
        "symbol": symbol,
        "side": request.side,
        "type": request.type,
        "price": request.price,
        "amount": request.amount,
        "leverage": request.leverage,
        "status": ORDER_STATUS["NEW"],  # PENDING状态，实际值为 "NEW"
        "timestamp": timestamp,  # 动态生成的时间戳
        "create_time": timestamp,  # 同时设置 create_time 字段
        "margin": initial_margin,  # 记录冻结的保证金
        "margin_type": request.margin_type,
        "market_type": "futures"  # 强制标记为合约订单
    }
    created_order = create_order_in_db(order_record)
    print(f"[DEBUG] 创建限价单挂单成功: order_id={order_id}, timestamp={timestamp}, status={created_order.get('status')}, user_id={address}, symbol={symbol}")
    print(f"[DEBUG] 订单已保存到 MOCK_ORDERS，当前订单总数: {len(MOCK_ORDERS)}")
    
    order_side = "LONG" if request.side == "BUY" else "SHORT"
    
    return {
        "code": 200,
        "message": "限价单已挂单，等待成交",
        "data": {
            "order_id": order_id,
            "symbol": symbol,
            "side": request.side,
            "type": request.type,
            "price": request.price,
            "amount": request.amount,
            "status": ORDER_STATUS["NEW"],
            "current_market_price": current_price,
            "assets": updated_assets
        }
    }


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
    # 必须在函数内部动态获取时间戳，不能使用默认参数或模块级变量
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
        "timestamp": timestamp,  # 动态生成的时间戳
        "create_time": timestamp,  # 同时设置 create_time 字段
        "fee": fee,
        "fee_currency": "USDT",
        "market_type": "futures"  # 强制标记为合约订单
    }
    create_order_in_db(order_record)
    print(f"[DEBUG] 创建开仓订单成功: order_id={order_id}, timestamp={timestamp}")
    
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
    # 必须在函数内部动态获取时间戳，不能使用默认参数或模块级变量
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
        "timestamp": timestamp,  # 动态生成的时间戳
        "create_time": timestamp,  # 同时设置 create_time 字段
        "fee": fee,
        "fee_currency": "USDT",
        "market_type": "futures"  # 强制标记为合约订单
    }
    create_order_in_db(order_record)
    print(f"[DEBUG] 创建开仓订单成功: order_id={order_id}, timestamp={timestamp}")
    
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
        "realized_pnl": realized_pnl,
        "market_type": "futures"  # 强制标记为合约订单
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

@router.get("/orders")
def get_futures_orders(
    status: Optional[str] = Query(None, description="订单状态筛选：'NEW' 或 'OPEN' 获取当前委托，'FILLED' 获取已成交，'CANCELLED' 获取已撤销，'HISTORY' 获取历史订单"),
    skip: int = Query(0, ge=0, description="分页偏移量（从0开始）"),
    limit: int = Query(20, ge=1, le=100, description="每页条数（默认20，最大100）"),
    current_user: Dict = Depends(get_current_user)
):
    """
    获取用户的合约订单列表
    
    功能：
    1. 验证用户身份（通过 JWT Token）
    2. 根据 status 参数筛选订单
    3. 返回订单列表（按创建时间倒序排列）
    
    参数：
    - status (可选):
      - 'NEW' 或 'OPEN': 获取当前委托（挂单中）
      - 'FILLED': 获取已成交订单
      - 'CANCELLED': 获取已撤销订单
      - 不传: 获取所有订单
    
    返回格式：
    {
        "code": 200,
        "message": "获取订单列表成功",
        "data": [
            {
                "order_id": "fut_xxx",
                "user_id": "0x...",
                "symbol": "BTC/USDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": 90000.0,
                "amount": 0.1,
                "leverage": 20,
                "status": "NEW",
                "timestamp": 1234567890,
                "margin": 450.0,
                ...
            }
        ]
    }
    """
    try:
        # ========== 终极调试日志 ==========
        print(f"\n{'='*80}")
        print(f"[DEBUG] ========== 查询合约订单 ==========")
        print(f"[DEBUG] 当前内存中的所有订单数量: {len(MOCK_ORDERS)}")
        print(f"DEBUG [ALL_ORDERS]: {MOCK_ORDERS}")
        print(f"{'='*80}\n")
        
        # 1. 获取用户地址
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        print(f"[DEBUG] 查询用户地址: {address_lower}")
        
        # 2. 处理状态筛选
        # 兼容 'OPEN' 状态（映射到 'NEW'）
        filter_status = None
        if status:
            print(f"[DEBUG] 传入的状态参数: {status}")
            if status.upper() == "OPEN":
                filter_status = ORDER_STATUS["NEW"]
                print(f"[DEBUG] OPEN 映射为: {filter_status}")
            elif status.upper() == "HISTORY":
                # 如果传入 'HISTORY'，返回已成交和已撤销的订单（带分页和时间过滤）
                import time
                
                all_orders = get_user_orders(address_lower)
                print(f"[DEBUG] HISTORY 模式：开始过滤历史订单")
                print(f"[DEBUG] 分页参数: skip={skip}, limit={limit}")
                
                # 第一步：时间过滤 - 只保留最近90天的订单
                current_timestamp = int(time.time())
                days_90_ago_timestamp = current_timestamp - (90 * 24 * 60 * 60)  # 90天前的时间戳
                print(f"[DEBUG] 时间过滤：当前时间戳={current_timestamp}, 90天前时间戳={days_90_ago_timestamp}")
                
                history_orders = []
                for order in all_orders:
                    order_id = order.get("order_id", "N/A")
                    order_status = order.get("status", "N/A")
                    market_type = order.get("market_type", "N/A")
                    order_timestamp = order.get("timestamp") or order.get("create_time", 0)
                    
                    # 检查状态
                    status_match = order_status in [ORDER_STATUS["FILLED"], ORDER_STATUS["CANCELLED"]]
                    # 检查市场类型
                    type_match = market_type == "futures" or order.get("order_id", "").startswith("fut_")
                    # 检查时间范围（最近90天）
                    time_match = order_timestamp >= days_90_ago_timestamp
                    
                    if status_match and type_match and time_match:
                        history_orders.append(order)
                    else:
                        skip_reason = []
                        if not status_match:
                            skip_reason.append(f"status={order_status}")
                        if not type_match:
                            skip_reason.append(f"type={market_type}")
                        if not time_match:
                            skip_reason.append(f"time={order_timestamp} < {days_90_ago_timestamp}")
                        print(f"[DEBUG] Order {order_id} SKIPPED: {', '.join(skip_reason)}")
                
                # 第二步：按时间倒序排列（最新的在最前）
                history_orders.sort(key=lambda x: x.get("timestamp") or x.get("create_time", 0), reverse=True)
                print(f"[DEBUG] 时间过滤后订单数量: {len(history_orders)}")
                
                # 第三步：分页切片
                start_idx = skip
                end_idx = skip + limit
                paginated_orders = history_orders[start_idx:end_idx]
                print(f"[DEBUG] 分页切片: [{start_idx}:{end_idx}], 返回数量: {len(paginated_orders)}")
                
                # 格式化历史订单数据
                formatted_history = []
                for order in paginated_orders:
                    formatted_order = {
                        "order_id": order.get("order_id"),
                        "user_id": order.get("user_id") or order.get("address"),
                        "symbol": order.get("symbol"),
                        "side": order.get("side"),
                        "type": order.get("type"),
                        "price": order.get("price"),
                        "quantity": order.get("quantity") or order.get("amount"),
                        "amount": order.get("amount") or order.get("quantity"),
                        "leverage": order.get("leverage", 20),
                        "margin": order.get("margin"),
                        "margin_type": order.get("margin_type", "ISOLATED"),
                        "status": order.get("status"),
                        "timestamp": order.get("timestamp") or order.get("create_time"),
                        "create_time": order.get("create_time") or order.get("timestamp"),
                        "update_time": order.get("update_time")
                    }
                    # 如果已成交，添加成交信息
                    if order.get("status") == ORDER_STATUS["FILLED"]:
                        formatted_order["executed_price"] = order.get("executed_price") or order.get("price")
                        formatted_order["executed_amount"] = order.get("executed_amount") or order.get("amount") or order.get("quantity")
                        formatted_order["fee"] = order.get("fee", 0)
                        formatted_order["fee_currency"] = order.get("fee_currency", "USDT")
                        if "realized_pnl" in order:
                            formatted_order["realized_pnl"] = order.get("realized_pnl", 0)
                    formatted_history.append(formatted_order)
                
                return {
                    "code": 200,
                    "message": "获取历史订单成功",
                    "data": formatted_history
                }
            else:
                filter_status = status.upper()
                print(f"[DEBUG] 状态筛选: {filter_status}")
        else:
            print(f"[DEBUG] 无状态筛选，返回所有订单")
        
        # 3. 获取订单列表
        orders = get_user_orders(address_lower, filter_status)
        print(f"[DEBUG] get_user_orders 返回的订单数量: {len(orders)}")
        print(f"[DEBUG] get_user_orders 返回的订单详情:")
        for order in orders:
            print(f"         Order ID: {order.get('order_id')}, Status: {order.get('status')}, Market Type: {order.get('market_type')}")
        
        # 4. 只返回合约订单（严格隔离：market_type == 'futures' 或 order_id 以 "fut_" 开头）
        print(f"\n[DEBUG] ========== 开始过滤合约订单 ==========")
        futures_orders = []
        for order in orders:
            order_id = order.get("order_id", "N/A")
            order_status = order.get("status", "N/A")
            market_type = order.get("market_type", "N/A")
            order_id_str = order.get("order_id", "")
            order_id_prefix = order_id_str[:4] if order_id_str else "N/A"
            
            print(f"[DEBUG] Checking Order {order_id}:")
            print(f"         status={order_status}, market_type={market_type}, order_id_prefix={order_id_prefix}")
            
            # 检查市场类型
            type_match = market_type == "futures" or order_id_str.startswith("fut_")
            
            if type_match:
                print(f"         -> KEPT (market_type={market_type} or order_id starts with 'fut_')")
                futures_orders.append(order)
            else:
                skip_reason = []
                if market_type != "futures":
                    skip_reason.append(f"market_type={market_type} != 'futures'")
                if not order_id_str.startswith("fut_"):
                    skip_reason.append(f"order_id={order_id_str} not startswith 'fut_'")
                print(f"         -> SKIPPED ({', '.join(skip_reason)})")
        
        print(f"[DEBUG] 过滤后的合约订单数量: {len(futures_orders)}")
        print(f"[DEBUG] 过滤后的合约订单详情:")
        for order in futures_orders:
            print(f"         Order ID: {order.get('order_id')}, Status: {order.get('status')}, Market Type: {order.get('market_type')}")
        print(f"{'='*80}\n")
        
        # 5. 格式化订单数据（确保包含所有必要字段）
        formatted_orders = []
        for order in futures_orders:
            formatted_order = {
                "order_id": order.get("order_id"),
                "user_id": order.get("user_id") or order.get("address"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "type": order.get("type"),
                "price": order.get("price"),
                "quantity": order.get("quantity") or order.get("amount"),  # 兼容 amount 字段
                "amount": order.get("amount") or order.get("quantity"),  # 保留 amount 字段
                "leverage": order.get("leverage", 20),
                "margin": order.get("margin"),
                "margin_type": order.get("margin_type", "ISOLATED"),
                "status": order.get("status"),
                "timestamp": order.get("timestamp") or order.get("create_time"),
                "create_time": order.get("create_time") or order.get("timestamp"),
                "update_time": order.get("update_time")
            }
            
            # 如果已成交，添加成交信息
            if order.get("status") == ORDER_STATUS["FILLED"]:
                formatted_order["executed_price"] = order.get("executed_price") or order.get("price")
                formatted_order["executed_amount"] = order.get("executed_amount") or order.get("amount") or order.get("quantity")
                formatted_order["fee"] = order.get("fee")
                formatted_order["fee_currency"] = order.get("fee_currency", "USDT")
                if "realized_pnl" in order:
                    formatted_order["realized_pnl"] = order.get("realized_pnl")
            
            formatted_orders.append(formatted_order)
        
        return {
            "code": 200,
            "message": "获取订单列表成功",
            "data": formatted_orders
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取订单列表失败: {str(e)}"
        )

@router.get("/positions")
def get_futures_positions(current_user: Dict = Depends(get_current_user)):
    """
    获取用户当前所有持仓（动态计算未实现盈亏）
    
    返回格式：
    {
        "code": 200,
        "data": [
            {
                "symbol": "BTC/USDT",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 90000.0,
                "mark_price": 95000.0,  # 当前标记价格
                "leverage": 10,
                "margin": 900.0,
                "unrealized_pnl": 500.0,  # 动态计算的未实现盈亏
                "liquidation_price": 8100.0,
                ...
            }
        ]
    }
    """
    address = current_user.get("address").lower()
    positions = get_user_positions(address)
    
    # 动态更新未实现盈亏（确保每次请求都获取最新价格）
    for pos in positions:
        symbol = pos.get("symbol", "")
        if not symbol:
            continue
            
        # 获取最新市场价格
        current_price = get_market_price(symbol)
        pos["mark_price"] = current_price
        
        # 盈亏计算: (当前价 - 开仓价) * 数量 * 方向系数
        entry_price = float(pos.get("entry_price", 0))
        size = float(pos.get("size", 0))
        side = pos.get("side", "LONG").upper()
        
        if entry_price > 0 and size > 0:
            price_diff = current_price - entry_price
            
            # 做多：价格上涨盈利；做空：价格下跌盈利
            if side == "SHORT":
                price_diff = -price_diff
            
            calculated_pnl = price_diff * size
            pos["unrealized_pnl"] = calculated_pnl
        else:
            pos["unrealized_pnl"] = 0.0
    
    print(f"[API] Returning: {positions}")
    return {
        "code": 200,
        "message": "获取持仓成功",
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
    
    # 确定平仓订单的方向（反向交易）
    # LONG 持仓 -> SELL 平仓，SHORT 持仓 -> BUY 平仓
    close_side = "SELL" if pos["side"] == "LONG" else "BUY"
    
    # 创建平仓订单记录
    # 必须在函数内部动态获取时间戳，不能使用默认参数或模块级变量
    timestamp = int(time.time())
    order_id = f"fut_{uuid.uuid4().hex[:12]}"
    order_record = {
        "order_id": order_id,
        "user_id": address,
        "symbol": symbol,
        "side": close_side,  # 反向交易方向
        "type": (request.type or "MARKET").upper(),  # 平仓类型（默认市价单）
        "price": current_price,  # 平仓执行价格
        "amount": request.amount,
        "status": "FILLED",  # 平仓立即成交
        "timestamp": timestamp,  # 动态生成的时间戳
        "create_time": timestamp,  # 同时设置 create_time 字段
        "fee": fee,
        "fee_currency": "USDT",
        "realized_pnl": realized_pnl,  # 已实现盈亏
        "market_type": "futures"  # 强制标记为合约订单
    }
    create_order_in_db(order_record)
    print(f"[DEBUG] 创建平仓订单成功: order_id={order_id}, timestamp={timestamp}")
    
    # 更新持仓信息
    new_size = pos["size"] - request.amount
    if new_size <= 0:
        update_position(address, symbol, {"size": 0})
    else:
        # 按比例减少保证金
        pos["size"] = new_size
        pos["margin"] -= margin_to_return
        update_position(address, symbol, pos)
    
    # 返回响应（订单记录已在上面创建）
    return {
        "code": 200,
        "message": "平仓成功" if new_size <= 0 else "部分平仓成功",
        "data": {
            "order_id": order_id,
            "action": "CLOSE",
            "realized_pnl": realized_pnl,
            "fee": fee,
            "remaining_position": None if new_size <= 0 else pos,
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
        
        # 自动保存到 JSON 文件（确保持久化）
        save_prices()
        
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

@router.post("/test/update-price")
def update_price_alias(request: UpdatePriceRequest):
    """
    测试接口别名：强制修改行情价格（与 /test/price 功能相同）
    
    此接口是 /test/price 的别名，方便前端调用
    """
    return update_market_price(request)

class CancelFuturesOrderRequest(BaseModel):
    """撤单请求模型"""
    order_id: str = Field(..., description="订单ID")

@router.post("/order/cancel")
def cancel_futures_order(
    request: CancelFuturesOrderRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    撤销合约订单
    
    功能：
    1. 验证用户身份（通过 JWT Token）
    2. 查找订单并确认订单属于当前用户
    3. 检查订单状态是否为 NEW（挂单中）
    4. 将订单状态改为 CANCELLED
    5. 解冻保证金（USDT）
    
    请求格式：
    {
        "order_id": "fut_xxx"
    }
    
    返回格式：
    {
        "code": 200,
        "message": "订单撤销成功",
        "data": {
            "order_id": "fut_xxx",
            "status": "CANCELLED",
            "assets": {
                "USDT": 5000000.0,
                ...
            }
        }
    }
    """
    try:
        # 1. 获取用户地址
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 2. 查找订单
        order = get_order(request.order_id)
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"订单不存在: {request.order_id}"
            )
        
        # 3. 验证订单是否属于当前用户
        order_user_id = order.get("user_id") or order.get("address", "").lower()
        if order_user_id != address_lower:
            raise HTTPException(
                status_code=403,
                detail="无权撤销此订单"
            )
        
        # 4. 检查订单状态
        current_status = order.get("status")
        if current_status != ORDER_STATUS["NEW"]:
            raise HTTPException(
                status_code=400,
                detail=f"只能撤销挂单中的订单。当前订单状态: {current_status}"
            )
        
        # 5. 解冻保证金（合约订单统一使用 USDT 作为保证金）
        margin = order.get("margin")
        if margin is None:
            # 如果没有保存保证金信息，根据订单信息计算
            quantity = order.get("quantity") or order.get("amount")
            price = order.get("price")
            leverage = order.get("leverage", 20)
            margin = (price * quantity) / leverage
        
        # 解冻保证金（使用安全模式，避免坏账卡死系统）
        updated_assets = unfreeze_assets(address_lower, "USDT", margin, safe_mode=True)
        
        # 6. 更新订单状态
        update_time = int(time.time())
        updated_order = update_order_status(
            request.order_id,
            ORDER_STATUS["CANCELLED"],
            update_time=update_time
        )
        
        # 7. 构建返回数据
        return {
            "code": 200,
            "message": "订单撤销成功",
            "data": {
                "order_id": request.order_id,
                "status": ORDER_STATUS["CANCELLED"],
                "assets": updated_assets
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"撤销订单失败: {str(e)}"
        )

class SetTPSLRequest(BaseModel):
    """设置止盈止损请求模型"""
    symbol: str = Field(..., description="交易对，例如 'BTC/USDT'")
    take_profit_price: Optional[float] = Field(None, ge=0, description="止盈价格（可选，传0或null表示清除）")
    stop_loss_price: Optional[float] = Field(None, ge=0, description="止损价格（可选，传0或null表示清除）")

@router.post("/position/set-tpsl")
def set_position_tpsl(
    request: SetTPSLRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    设置持仓的止盈止损价格
    
    功能：
    1. 验证用户身份（通过 JWT Token）
    2. 查找用户对应的持仓
    3. 更新持仓的止盈止损价格
    4. 支持单独设置止盈或止损，也支持清除（传0或null）
    
    请求格式：
    {
        "symbol": "BTC/USDT",
        "take_profit_price": 95000.0,  // 可选，传0或null表示清除
        "stop_loss_price": 85000.0     // 可选，传0或null表示清除
    }
    
    返回格式：
    {
        "code": 200,
        "message": "止盈止损设置成功",
        "data": {
            "symbol": "BTC/USDT",
            "take_profit_price": 95000.0,
            "stop_loss_price": 85000.0,
            "position": {...}
        }
    }
    """
    try:
        # 1. 获取用户地址
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 2. 规范化交易对格式
        symbol = request.symbol.upper()
        if '/' not in symbol:
            symbol = f"{symbol}/USDT"
        
        # 3. 查找用户对应的持仓
        positions = get_user_positions(address_lower, symbol)
        if not positions:
            raise HTTPException(
                status_code=404,
                detail=f"未找到对应持仓: {symbol}"
            )
        
        position = positions[0]
        
        # 4. 验证持仓是否有效
        if position.get("size", 0) <= 0:
            raise HTTPException(
                status_code=400,
                detail="持仓数量为0，无法设置止盈止损"
            )
        
        # 5. 构建更新数据
        update_data = {}
        
        print(f"[API] 设置止盈止损 - 用户: {address_lower[:8]}..., 交易对: {symbol}")
        print(f"[API] 请求数据 - take_profit_price: {request.take_profit_price}, stop_loss_price: {request.stop_loss_price}")
        
        # 处理止盈价格
        if request.take_profit_price is not None:
            if request.take_profit_price > 0:
                update_data["take_profit_price"] = request.take_profit_price
                print(f"[API] 设置止盈价格: {request.take_profit_price}")
            else:
                # 传0或负数表示清除
                update_data["take_profit_price"] = None
                print(f"[API] 清除止盈价格")
        
        # 处理止损价格
        if request.stop_loss_price is not None:
            if request.stop_loss_price > 0:
                update_data["stop_loss_price"] = request.stop_loss_price
                print(f"[API] 设置止损价格: {request.stop_loss_price}")
            else:
                # 传0或负数表示清除
                update_data["stop_loss_price"] = None
                print(f"[API] 清除止损价格")
        
        # 6. 更新持仓
        updated_position = update_position(address_lower, symbol, update_data)
        print(f"[API] 持仓已更新 - take_profit_price: {updated_position.get('take_profit_price')}, stop_loss_price: {updated_position.get('stop_loss_price')}")
        print(f"[API] Updated: {updated_position}")
        
        # 7. 返回响应（返回所有持仓）
        all_positions = get_user_positions(address_lower)
        return {
            "code": 200,
            "message": "止盈止损设置成功",
            "data": {
                "symbol": symbol,
                "take_profit_price": updated_position.get("take_profit_price"),
                "stop_loss_price": updated_position.get("stop_loss_price"),
                "position": updated_position,
                "positions": all_positions
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"设置止盈止损失败: {str(e)}"
        )