"""
交易相关 API 端点
提供现货交易下单功能（Mock 实现）
支持限价单和市价单，包含手续费计算逻辑
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import time
from app.api.deps import get_current_user
from app.db.mock import (
    get_user_assets, 
    update_user_assets, 
    freeze_assets, 
    unfreeze_assets,
    create_order as create_order_in_db,
    get_order,
    update_order_status,
    get_user_orders
)

# 创建路由实例
router = APIRouter(prefix="/api/v1/trade", tags=["trade"])

# 交易手续费配置
BASE_FEE_RATE = 0.001  # 基础费率：0.1%

# 订单状态常量
ORDER_STATUS = {
    "NEW": "NEW",           # 新建（挂单中）
    "PARTIALLY_FILLED": "PARTIALLY_FILLED",  # 部分成交
    "FILLED": "FILLED",     # 完全成交
    "CANCELLED": "CANCELLED"  # 已取消
}

# 从 mock.py 导入价格相关函数（全局唯一事实来源）
from app.db.mock import get_market_price


class OrderRequest(BaseModel):
    """交易订单请求模型"""
    symbol: str = Field(..., description="交易对，例如 'BTC/USDT'")
    side: str = Field(..., description="交易方向：'BUY' 买入 或 'SELL' 卖出")
    type: str = Field(..., description="订单类型：'LIMIT' 限价单 或 'MARKET' 市价单")
    price: float = Field(..., gt=0, description="交易价格（单价）。对于 MARKET 单，此价格代表当前市场参考价")
    amount: float = Field(..., gt=0, description="交易数量")
    use_beat_discount: bool = Field(default=False, description="是否使用 BEAT 抵扣手续费（目前为占位符功能）")


@router.post("/order")
def create_order(
    request: OrderRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    创建现货交易订单（Mock 实现）
    
    功能：
    1. 验证用户身份（通过 JWT Token）
    2. 解析交易对（例如 "BTC/USDT"）
    3. 根据订单类型（LIMIT/MARKET）和交易方向（BUY/SELL）执行交易逻辑
    4. 计算手续费（0.1%），支持 BEAT 折扣占位符
    5. 更新内存账本 MOCK_USER_ASSETS
    6. 返回交易结果和最新余额
    
    手续费计算规则：
    - 买入（BUY）：从用户应得的 BTC 中扣除 0.1%
      - 用户支付：price * amount (USDT)
      - 用户应得：amount (BTC)
      - 实际得到：amount * (1 - fee_rate) (BTC)
      - 手续费：amount * fee_rate (BTC)
    
    - 卖出（SELL）：从用户应得的 USDT 中扣除 0.1%
      - 用户支付：amount (BTC)
      - 用户应得：price * amount (USDT)
      - 实际得到：price * amount * (1 - fee_rate) (USDT)
      - 手续费：price * amount * fee_rate (USDT)
    
    请求格式：
    {
        "symbol": "BTC/USDT",
        "side": "BUY",
        "type": "LIMIT",
        "price": 50000.0,
        "amount": 0.1,
        "use_beat_discount": false
    }
    
    返回格式：
    {
        "code": 200,
        "message": "订单提交成功",
        "data": {
            "order_id": "mock_order_123",
            "symbol": "BTC/USDT",
            "side": "BUY",
            "type": "LIMIT",
            "executed_price": 50000.0,
            "amount": 0.1,
            "fee": 0.0001,
            "fee_currency": "BTC",
            "total_cost": 5000.0,
            "assets": {
                "USDT": 45000.0,
                "BTC": 0.0999,
                "BEAT": 0.0
            }
        }
    }
    """
    try:
        # 1. 验证交易方向
        if request.side not in ["BUY", "SELL"]:
            raise HTTPException(
                status_code=400,
                detail="交易方向必须是 'BUY' 或 'SELL'"
            )
        
        # 2. 验证订单类型
        if request.type not in ["LIMIT", "MARKET"]:
            raise HTTPException(
                status_code=400,
                detail="订单类型必须是 'LIMIT' 或 'MARKET'"
            )
        
        # 3. 解析交易对（例如 "BTC/USDT" -> base="BTC", quote="USDT"）
        symbol_parts = request.symbol.split("/")
        if len(symbol_parts) != 2:
            raise HTTPException(
                status_code=400,
                detail=f"交易对格式错误，应为 'BASE/QUOTE'，例如 'BTC/USDT'"
            )
        
        base_currency = symbol_parts[0].upper()  # 基础货币（例如 BTC）
        quote_currency = symbol_parts[1].upper()  # 报价货币（例如 USDT）
        
        # 4. 验证币种是否支持
        supported_currencies = ["USDT", "BTC", "ETH", "BNB", "SOL", "DOGE", "TRX", "BEAT", "AIC"]
        if base_currency not in supported_currencies:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的基础货币: {base_currency}"
            )
        if quote_currency not in supported_currencies:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的报价货币: {quote_currency}"
            )
        
        # 5. 获取用户地址并转换为小写
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 6. 获取当前资产
        current_assets = get_user_assets(address_lower)
        
        # 7. 获取当前市场价格
        current_market_price = get_market_price(request.symbol)
        if current_market_price <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"无法获取交易对 {request.symbol} 的市场价格"
            )
        
        # 8. BEAT 折扣逻辑（占位符）
        if request.use_beat_discount:
            print(f"⚠️  TODO: Implement BEAT deduction for user {address_lower}")
            print(f"   当前仍按 0.1% 扣除原币种手续费（防止汇率换算导致 Mock 崩溃）")
            # 实际手续费计算仍使用基础费率
            actual_fee_rate = BASE_FEE_RATE
        else:
            actual_fee_rate = BASE_FEE_RATE
        
        # 9. 生成订单ID
        order_id = f"mock_order_{address_lower[:8]}_{int(time.time() * 1000)}"
        create_time = int(time.time())
        
        # 10. 判断订单类型并执行相应逻辑
        if request.type == "MARKET":
            # ========== 市价单：立即成交 ==========
            executed_price = current_market_price  # 使用当前市价成交
            order_status = ORDER_STATUS["FILLED"]
            order_type_note = "市价单（立即成交）"
            
            # 执行交易逻辑（与之前相同）
            if request.side == "BUY":
                # 买入逻辑
                total_cost = executed_price * request.amount
                usdt_balance = current_assets.get(quote_currency, 0.0)
                if usdt_balance < total_cost:
                    raise HTTPException(
                        status_code=400,
                        detail=f"余额不足。需要 {total_cost} {quote_currency}，当前余额: {usdt_balance} {quote_currency}"
                    )
                
                fee_amount = request.amount * actual_fee_rate
                fee_currency = base_currency
                actual_base_amount = request.amount * (1 - actual_fee_rate)
                
                current_assets[quote_currency] = usdt_balance - total_cost
                current_assets[base_currency] = current_assets.get(base_currency, 0.0) + actual_base_amount
                
                print(f"✅ 买入市价单（立即成交）：用户 {address_lower}")
                print(f"   成交价: {executed_price} {quote_currency}/{base_currency}")
                print(f"   花费: {total_cost} {quote_currency}")
                print(f"   实际得到: {actual_base_amount} {base_currency}")
                
            else:  # SELL
                # 卖出逻辑
                base_balance = current_assets.get(base_currency, 0.0)
                if base_balance < request.amount:
                    raise HTTPException(
                        status_code=400,
                        detail=f"余额不足。需要 {request.amount} {base_currency}，当前余额: {base_balance} {base_currency}"
                    )
                
                gross_revenue = executed_price * request.amount
                fee_amount = gross_revenue * actual_fee_rate
                fee_currency = quote_currency
                actual_quote_amount = gross_revenue * (1 - actual_fee_rate)
                
                current_assets[base_currency] = base_balance - request.amount
                current_assets[quote_currency] = current_assets.get(quote_currency, 0.0) + actual_quote_amount
                
                print(f"✅ 卖出市价单（立即成交）：用户 {address_lower}")
                print(f"   成交价: {executed_price} {quote_currency}/{base_currency}")
                print(f"   花费: {request.amount} {base_currency}")
                print(f"   实际得到: {actual_quote_amount} {quote_currency}")
            
            # 更新资产
            updated_assets = update_user_assets(address_lower, current_assets)
            
        else:  # request.type == "LIMIT"
            # ========== 限价单：判断是否立即成交或挂单 ==========
            order_price = request.price
            order_type_note = "限价单"
            
            # 判断是否满足立即成交条件
            should_execute_immediately = False
            
            if request.side == "BUY":
                # 买入限价单：只有当 order_price >= current_market_price 时才立即成交
                # （用户愿意以更高或相等的价格买入，可以立即成交）
                should_execute_immediately = order_price >= current_market_price
            else:  # SELL
                # 卖出限价单：只有当 order_price <= current_market_price 时才立即成交
                # （用户愿意以更低或相等的价格卖出，可以立即成交）
                should_execute_immediately = order_price <= current_market_price
            
            if should_execute_immediately:
                # ========== 限价单立即成交 ==========
                executed_price = order_price  # 使用限价成交
                order_status = ORDER_STATUS["FILLED"]
                
                if request.side == "BUY":
                    # 买入逻辑
                    total_cost = executed_price * request.amount
                    usdt_balance = current_assets.get(quote_currency, 0.0)
                    if usdt_balance < total_cost:
                        raise HTTPException(
                            status_code=400,
                            detail=f"余额不足。需要 {total_cost} {quote_currency}，当前余额: {usdt_balance} {quote_currency}"
                        )
                    
                    fee_amount = request.amount * actual_fee_rate
                    fee_currency = base_currency
                    actual_base_amount = request.amount * (1 - actual_fee_rate)
                    
                    current_assets[quote_currency] = usdt_balance - total_cost
                    current_assets[base_currency] = current_assets.get(base_currency, 0.0) + actual_base_amount
                    
                    print(f"✅ 买入限价单（立即成交）：用户 {address_lower}")
                    print(f"   限价: {order_price}, 市价: {current_market_price}")
                    print(f"   成交价: {executed_price} {quote_currency}/{base_currency}")
                    print(f"   实际得到: {actual_base_amount} {base_currency}")
                    
                else:  # SELL
                    # 卖出逻辑
                    base_balance = current_assets.get(base_currency, 0.0)
                    if base_balance < request.amount:
                        raise HTTPException(
                            status_code=400,
                            detail=f"余额不足。需要 {request.amount} {base_currency}，当前余额: {base_balance} {base_currency}"
                        )
                    
                    gross_revenue = executed_price * request.amount
                    fee_amount = gross_revenue * actual_fee_rate
                    fee_currency = quote_currency
                    actual_quote_amount = gross_revenue * (1 - actual_fee_rate)
                    
                    current_assets[base_currency] = base_balance - request.amount
                    current_assets[quote_currency] = current_assets.get(quote_currency, 0.0) + actual_quote_amount
                    
                    print(f"✅ 卖出限价单（立即成交）：用户 {address_lower}")
                    print(f"   限价: {order_price}, 市价: {current_market_price}")
                    print(f"   成交价: {executed_price} {quote_currency}/{base_currency}")
                    print(f"   实际得到: {actual_quote_amount} {quote_currency}")
                
                # 更新资产
                updated_assets = update_user_assets(address_lower, current_assets)
                
            else:
                # ========== 限价单挂单（Pending） ==========
                executed_price = None  # 尚未成交
                order_status = ORDER_STATUS["NEW"]
                
                if request.side == "BUY":
                    # 买入限价单挂单：冻结 USDT
                    total_cost = order_price * request.amount
                    usdt_balance = current_assets.get(quote_currency, 0.0)
                    if usdt_balance < total_cost:
                        raise HTTPException(
                            status_code=400,
                            detail=f"余额不足。需要 {total_cost} {quote_currency}，当前余额: {usdt_balance} {quote_currency}"
                        )
                    
                    # 冻结 USDT
                    updated_assets = freeze_assets(address_lower, quote_currency, total_cost)
                    
                    print(f"📋 买入限价单（挂单）：用户 {address_lower}")
                    print(f"   限价: {order_price}, 市价: {current_market_price}")
                    print(f"   冻结: {total_cost} {quote_currency}")
                    
                else:  # SELL
                    # 卖出限价单挂单：冻结 BTC
                    base_balance = current_assets.get(base_currency, 0.0)
                    if base_balance < request.amount:
                        raise HTTPException(
                            status_code=400,
                            detail=f"余额不足。需要 {request.amount} {base_currency}，当前余额: {base_balance} {base_currency}"
                        )
                    
                    # 冻结 BTC
                    updated_assets = freeze_assets(address_lower, base_currency, request.amount)
                    
                    print(f"📋 卖出限价单（挂单）：用户 {address_lower}")
                    print(f"   限价: {order_price}, 市价: {current_market_price}")
                    print(f"   冻结: {request.amount} {base_currency}")
        
        # 11. 创建订单记录
        order_data = {
            "order_id": order_id,
            "user_id": address_lower,  # 使用地址作为 user_id
            "address": address_lower,  # 保留 address 字段以兼容现有代码
            "symbol": request.symbol,
            "side": request.side,
            "type": request.type,
            "price": request.price,
            "quantity": request.amount,  # 使用 quantity 字段
            "amount": request.amount,  # 保留 amount 字段以兼容现有代码
            "status": order_status,
            "timestamp": create_time,  # 使用 timestamp 字段
            "create_time": create_time,  # 保留 create_time 字段以兼容现有代码
            "update_time": create_time
        }
        
        # 如果是立即成交，添加成交信息
        if order_status == ORDER_STATUS["FILLED"]:
            order_data["executed_price"] = executed_price
            order_data["executed_amount"] = request.amount
            order_data["fee"] = round(fee_amount, 8)
            order_data["fee_currency"] = fee_currency
            order_data["update_time"] = create_time
        
        # 保存订单
        created_order = create_order_in_db(order_data)
        
        # 13. 构建返回数据
        response_data = {
            "order_id": order_id,
            "symbol": request.symbol,
            "side": request.side,
            "type": request.type,
            "price": request.price,
            "amount": request.amount,
            "status": order_status,
            "create_time": create_time,
            "assets": updated_assets  # 更新后的资产余额
        }
        
        # 如果是立即成交，添加成交信息
        if order_status == ORDER_STATUS["FILLED"]:
            response_data["executed_price"] = executed_price
            response_data["executed_amount"] = request.amount
            response_data["fee"] = round(fee_amount, 8)
            response_data["fee_currency"] = fee_currency
            
            # 根据交易方向添加不同的字段名
            if request.side == "BUY":
                response_data["total_cost"] = executed_price * request.amount
            else:
                gross_revenue = executed_price * request.amount
                response_data["total_revenue"] = gross_revenue * (1 - actual_fee_rate)
                response_data["gross_revenue"] = gross_revenue
        
        # 14. 返回交易结果
        if order_status == ORDER_STATUS["NEW"]:
            message = "限价单已挂单，等待成交"
        else:
            message = "订单提交成功，已立即成交"
        
        return {
            "code": 200,
            "message": message,
            "data": response_data
        }
        
    except HTTPException:
        # 重新抛出 HTTP 异常（保持状态码和错误信息）
        raise
    except Exception as e:
        # 捕获其他未预期的错误
        raise HTTPException(
            status_code=500,
            detail=f"订单提交失败: {str(e)}"
        )


class CancelOrderRequest(BaseModel):
    """撤单请求模型"""
    order_id: str = Field(..., description="订单ID")


@router.get("/orders")
def get_orders(
    status: Optional[str] = Query(None, description="订单状态筛选：'NEW' 获取当前委托，'FILLED' 或 'CANCELLED' 获取历史订单"),
    current_user: Dict = Depends(get_current_user)
):
    """
    获取用户的订单列表
    
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
                "order_id": "mock_order_xxx",
                "user_id": "0x...",
                "symbol": "BTC/USDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": 92000.0,
                "quantity": 1.0,
                "status": "NEW",
                "timestamp": 1234567890,
                ...
            }
        ]
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
        
        # 2. 处理状态筛选
        # 兼容 'OPEN' 状态（映射到 'NEW'）
        filter_status = None
        if status:
            if status.upper() == "OPEN":
                filter_status = ORDER_STATUS["NEW"]
            elif status.upper() == "HISTORY":
                # 如果传入 'HISTORY'，返回已成交和已撤销的订单
                all_orders = get_user_orders(address_lower)
                history_orders = [
                    order for order in all_orders
                    if order.get("status") in [ORDER_STATUS["FILLED"], ORDER_STATUS["CANCELLED"]]
                ]
                return {
                    "code": 200,
                    "message": "获取历史订单成功",
                    "data": history_orders
                }
            else:
                filter_status = status.upper()
        
        # 3. 获取订单列表
        orders = get_user_orders(address_lower, filter_status)
        
        # 4. 格式化订单数据（确保包含所有必要字段）
        formatted_orders = []
        for order in orders:
            formatted_order = {
                "order_id": order.get("order_id"),
                "user_id": order.get("user_id") or order.get("address"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "type": order.get("type"),
                "price": order.get("price"),
                "quantity": order.get("quantity") or order.get("amount"),  # 兼容 amount 字段
                "status": order.get("status"),
                "timestamp": order.get("timestamp") or order.get("create_time"),
                "create_time": order.get("create_time") or order.get("timestamp"),
                "update_time": order.get("update_time")
            }
            
            # 如果已成交，添加成交信息
            if order.get("status") == ORDER_STATUS["FILLED"]:
                formatted_order["executed_price"] = order.get("executed_price")
                formatted_order["executed_amount"] = order.get("executed_amount")
                formatted_order["fee"] = order.get("fee")
                formatted_order["fee_currency"] = order.get("fee_currency")
            
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


@router.post("/order/cancel")
def cancel_order(
    request: CancelOrderRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    撤销订单
    
    功能：
    1. 验证用户身份（通过 JWT Token）
    2. 查找订单并确认订单属于当前用户
    3. 检查订单状态是否为 NEW（挂单中）
    4. 将订单状态改为 CANCELLED
    5. 执行解冻逻辑（将冻结的资金退回给可用余额）
    
    请求格式：
    {
        "order_id": "mock_order_xxx"
    }
    
    返回格式：
    {
        "code": 200,
        "message": "订单撤销成功",
        "data": {
            "order_id": "mock_order_xxx",
            "status": "CANCELLED",
            "assets": {
                "USDT": 5000000.0,
                "BTC": 0.0,
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
        
        # 5. 解析交易对和币种
        symbol = order.get("symbol")
        symbol_parts = symbol.split("/")
        if len(symbol_parts) != 2:
            raise HTTPException(
                status_code=400,
                detail=f"订单交易对格式错误: {symbol}"
            )
        
        base_currency = symbol_parts[0].upper()
        quote_currency = symbol_parts[1].upper()
        
        # 6. 执行解冻逻辑
        side = order.get("side")
        quantity = order.get("quantity") or order.get("amount")
        price = order.get("price")
        
        if side == "BUY":
            # 买入订单：解冻 USDT
            total_cost = price * quantity
            try:
                updated_assets = unfreeze_assets(address_lower, quote_currency, total_cost)
                print(f"✅ 撤销买入订单：用户 {address_lower}")
                print(f"   解冻: {total_cost} {quote_currency}")
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"解冻资产失败: {str(e)}"
                )
        else:  # SELL
            # 卖出订单：解冻 BTC
            try:
                updated_assets = unfreeze_assets(address_lower, base_currency, quantity)
                print(f"✅ 撤销卖出订单：用户 {address_lower}")
                print(f"   解冻: {quantity} {base_currency}")
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"解冻资产失败: {str(e)}"
                )
        
        # 7. 更新订单状态
        update_time = int(time.time())
        updated_order = update_order_status(
            request.order_id,
            ORDER_STATUS["CANCELLED"],
            update_time=update_time
        )
        
        # 8. 构建返回数据
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
