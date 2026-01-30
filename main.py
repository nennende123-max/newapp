from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from eth_account import Account
from eth_account.messages import encode_defunct
import jwt
import os
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict

# 导入依赖函数
from app.api.deps import get_current_user
# 导入资产路由
from app.api.endpoints import assets
# 导入交易路由
from app.api.endpoints import trade
# 导入合约路由
from app.api.endpoints import futures
# 导入市场数据路由
from app.api.endpoints import market
# 导入 Mock 数据层
from app.db.mock import MOCK_POSITIONS, MOCK_ORDERS, MOCK_USER_ASSETS, update_position, get_market_price, save_assets, _save_json_file, ORDERS_FILE, POSITIONS_FILE, MOCK_MARKET_PRICES, save_prices, create_order as create_order_in_db
# 导入交易服务层
from app.services.trade import check_tpsl_triggers
# 导入市场服务
from app.services.market_service import market_service
from app.models.kline import KlineModel

# 创建 FastAPI 应用实例
app = FastAPI(title="TruthFi API")

# 注册资产路由
app.include_router(assets.router)
# 注册交易路由
app.include_router(trade.router)
# 注册合约路由
app.include_router(futures.router)
# 注册市场数据路由
app.include_router(market.router)

# JWT Token 安全配置
# SECRET_KEY 的作用和重要性：
# 1. SECRET_KEY 是用于签名和验证 JWT Token 的密钥
# 2. 只有拥有这个密钥的服务器才能创建和验证 Token
# 3. 如果 SECRET_KEY 泄露，攻击者可以伪造任意用户的 Token
# 4. 因此 SECRET_KEY 必须保密，绝不能提交到代码仓库

# 从环境变量读取 SECRET_KEY（推荐方式）
# 如果环境变量不存在，使用默认值（仅用于开发环境）
# 生产环境必须设置环境变量，不要使用默认值
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

# JWT Token 配置
JWT_ALGORITHM = "HS256"  # 使用 HMAC SHA-256 算法
TOKEN_EXPIRE_HOURS = 24  # Token 24 小时后过期

# 定义请求数据模型
class WalletConnectRequest(BaseModel):
    address: str  # 钱包地址
    signature: str  # 签名
    message: str  # 原始消息

# 配置 CORS 中间件
# 这是解决跨域问题的关键配置
# 注意：如果 allow_credentials=True，FastAPI 不允许使用 "*"，必须明确指定域名
# 如果运行时出现 CORS 错误，请移除 "*" 或设置 allow_credentials=False
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173", "http://127.0.0.1:5173"],  # Wildcard + specific for Vite dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

@app.get("/")  # 这是一个接口
def read_root():
    return {"message": "TruthFi API 运行中"}

@app.get("/ping") # 这是另一个接口
def ping():
    return "pong"

# TODO: DELETE THIS DEBUG ENDPOINT BEFORE PRODUCTION（待办：上线前必须删除此接口）
def _check_debug_environment():
    """
    检查是否在开发环境中运行
    
    返回:
        bool: 如果在开发环境返回 True，否则返回 False
    """
    import os
    # 检查环境变量 DEBUG 是否为 True
    if os.getenv("DEBUG", "").upper() == "TRUE":
        return True
    # 检查是否在本地环境（127.0.0.1 或 localhost）
    # 注意：这里无法直接获取请求的 IP，所以只检查环境变量
    # 在生产环境部署时，应该设置 DEBUG=False 或删除此环境变量
    return False

@app.get("/api/v1/debug/reset")
def reset_data(current_user: Dict = Depends(get_current_user)):
    """
    重置数据（开发环境专用）
    
    功能：
    1. 清空订单表（MOCK_ORDERS）
    2. 清空持仓表（MOCK_POSITIONS）
    3. 重置用户 USDT 余额为 1,000,000
    4. 重置用户 USDT 冻结金额为 0
    
    注意：此接口仅用于开发环境，生产环境应禁用
    """
    # TODO: DELETE THIS DEBUG ENDPOINT BEFORE PRODUCTION（待办：上线前必须删除此接口）
    
    # 环境隔离：只在开发环境允许运行
    if not _check_debug_environment():
        raise HTTPException(
            status_code=403,
            detail="此接口仅在开发环境中可用"
        )
    
    # 日志警告：每次调用时打印醒目的警告
    print("\n" + "="*80)
    print("⚠️  WARNING: DEBUG INTERFACE CALLED! DATA HAS BEEN RESET.")
    print("="*80 + "\n")
    
    try:
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 1. 清空订单列表
        global MOCK_ORDERS
        MOCK_ORDERS.clear()
        _save_json_file(ORDERS_FILE, MOCK_ORDERS)
        print(f"[RESET] 已清空订单列表，当前订单数: {len(MOCK_ORDERS)}")
        
        # 2. 清空持仓列表
        global MOCK_POSITIONS
        MOCK_POSITIONS.clear()
        _save_json_file(POSITIONS_FILE, MOCK_POSITIONS)
        print(f"[RESET] 已清空持仓列表，当前持仓数: {len(MOCK_POSITIONS)}")
        
        # 3. 重置用户资产（仅 USDT）
        if address_lower not in MOCK_USER_ASSETS:
            MOCK_USER_ASSETS[address_lower] = {}
        
        # 强制重置 USDT 余额为 1,000,000，冻结金额为 0
        MOCK_USER_ASSETS[address_lower]["USDT"] = 1000000.0
        MOCK_USER_ASSETS[address_lower]["USDT_frozen"] = 0.0
        
        # 保存资产数据
        save_assets()
        print(f"[RESET] 已重置用户资产：USDT={MOCK_USER_ASSETS[address_lower].get('USDT', 0)}, USDT_frozen={MOCK_USER_ASSETS[address_lower].get('USDT_frozen', 0)}")
        
        return {
            "code": 200,
            "message": "数据重置成功",
            "data": {
                "orders_count": 0,
                "positions_count": 0,
                "usdt_balance": MOCK_USER_ASSETS[address_lower].get("USDT", 0),
                "usdt_frozen": MOCK_USER_ASSETS[address_lower].get("USDT_frozen", 0)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置数据失败: {str(e)}"
        )

@app.get("/api/v1/debug/reset_all")
def reset_all_data(current_user: Dict = Depends(get_current_user)):
    """
    一键重置所有数据（开发环境专用）
    
    功能：
    1. 清空 MOCK_ORDERS 列表
    2. 清空 MOCK_POSITIONS 列表
    3. 重置用户资产：USDT 余额设为 1,000,000，冻结余额归零
    
    注意：此接口仅用于开发环境，生产环境应禁用
    """
    # TODO: DELETE THIS DEBUG ENDPOINT BEFORE PRODUCTION（待办：上线前必须删除此接口）
    
    # 环境隔离：只在开发环境允许运行
    if not _check_debug_environment():
        raise HTTPException(
            status_code=403,
            detail="此接口仅在开发环境中可用"
        )
    
    # 日志警告：每次调用时打印醒目的警告
    print("\n" + "="*80)
    print("⚠️  WARNING: DEBUG INTERFACE CALLED! DATA HAS BEEN RESET.")
    print("="*80 + "\n")
    
    try:
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 1. 清空订单列表
        global MOCK_ORDERS
        MOCK_ORDERS.clear()
        _save_json_file(ORDERS_FILE, MOCK_ORDERS)
        print(f"[RESET] 已清空订单列表，当前订单数: {len(MOCK_ORDERS)}")
        
        # 2. 清空持仓列表
        global MOCK_POSITIONS
        MOCK_POSITIONS.clear()
        _save_json_file(POSITIONS_FILE, MOCK_POSITIONS)
        print(f"[RESET] 已清空持仓列表，当前持仓数: {len(MOCK_POSITIONS)}")
        
        # 3. 重置用户资产
        if address_lower not in MOCK_USER_ASSETS:
            MOCK_USER_ASSETS[address_lower] = {}
        
        # 重置 USDT 余额为 1,000,000，冻结余额归零
        MOCK_USER_ASSETS[address_lower]["USDT"] = 1000000.0
        MOCK_USER_ASSETS[address_lower]["USDT_frozen"] = 0.0
        
        # 其他币种保持不变，但冻结余额归零
        for currency in ["BTC", "ETH", "BNB", "SOL", "DOGE", "TRX", "BEAT", "AIC"]:
            frozen_key = f"{currency}_frozen"
            if frozen_key in MOCK_USER_ASSETS[address_lower]:
                MOCK_USER_ASSETS[address_lower][frozen_key] = 0.0
        
        # 保存资产数据
        save_assets()
        print(f"[RESET] 已重置用户资产：USDT={MOCK_USER_ASSETS[address_lower].get('USDT', 0)}")
        
        return {
            "code": 200,
            "message": "数据重置成功",
            "data": {
                "orders_count": 0,
                "positions_count": 0,
                "assets": MOCK_USER_ASSETS[address_lower].copy()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置数据失败: {str(e)}"
        )

# TODO: DELETE THIS DEBUG ENDPOINT BEFORE PRODUCTION（待办：上线前必须删除此接口）
class SetPriceRequest(BaseModel):
    """设置价格请求模型"""
    symbol: str  # 交易对，例如 "BTC/USDT"
    price: float  # 新价格

@app.post("/api/v1/debug/set_price")
def set_price(request: SetPriceRequest):
    """
    强制修改市场价格（开发环境专用）
    
    功能：
    1. 修改内存中的全局价格变量 MOCK_MARKET_PRICES
    2. 保存价格到 JSON 文件（确保持久化）
    3. 修改后，持仓列表中的"未实现盈亏"会立即根据新价格计算
    
    请求格式：
    {
        "symbol": "BTC/USDT",
        "price": 95000.0
    }
    
    返回格式：
    {
        "code": 200,
        "message": "价格更新成功",
        "data": {
            "symbol": "BTC/USDT",
            "old_price": 92255.0,
            "new_price": 95000.0,
            "variable_name": "MOCK_MARKET_PRICES"
        }
    }
    
    注意：
    - 此接口修改的变量名：MOCK_MARKET_PRICES（在 app.db.mock 模块中定义）
    - 此接口仅用于开发环境，生产环境应禁用
    """
    # TODO: DELETE THIS DEBUG ENDPOINT BEFORE PRODUCTION（待办：上线前必须删除此接口）
    
    # 环境限制已移除：允许本地测试直接调用
    # 注意：生产环境部署前必须删除此接口或重新启用环境检查
    
    # 日志警告：每次调用时打印醒目的警告
    print("\n" + "="*80)
    print("⚠️  WARNING: DEBUG INTERFACE CALLED! PRICE HAS BEEN MODIFIED.")
    print("="*80 + "\n")
    
    try:
        # 规范化交易对格式
        symbol = request.symbol.upper()
        if '/' not in symbol:
            symbol = f"{symbol}/USDT"
        
        # 验证价格
        if request.price <= 0:
            raise HTTPException(
                status_code=400,
                detail="价格必须大于 0"
            )
        
        # 获取旧价格
        old_price = MOCK_MARKET_PRICES.get(symbol, 0.0)
        
        # 修改内存中的价格（全局唯一事实来源）
        # 变量名：MOCK_MARKET_PRICES（在 app.db.mock 模块中定义）
        MOCK_MARKET_PRICES[symbol] = request.price
        
        # 自动保存到 JSON 文件（确保持久化）
        save_prices()
        
        print(f"[DEBUG] 价格已更新: {symbol} = {old_price} -> {request.price}")
        
        # 被动触发止盈止损检查（集成强平检查）
        print(f"[DEBUG] 开始检查止盈止损和强平条件...")
        triggered_positions = check_tpsl_triggers(request.price, symbol)
        
        if triggered_positions:
            print(f"[DEBUG] 共触发 {len(triggered_positions)} 个持仓的止盈止损/强平")
            for tp in triggered_positions:
                print(f"  - {tp['symbol']} {tp['side']}: {tp['reason']} (Order: {tp['order_id']})")
        else:
            print(f"[DEBUG] 未触发任何止盈止损或强平条件")
        
        return {
            "code": 200,
            "message": f"价格更新成功: {symbol}",
            "data": {
                "symbol": symbol,
                "old_price": old_price,
                "new_price": request.price,
                "variable_name": "MOCK_MARKET_PRICES",  # 告诉用户修改的变量名
                "triggered_positions": len(triggered_positions),  # 触发的持仓数量
                "triggered_details": triggered_positions if triggered_positions else None  # 触发详情
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新价格失败: {str(e)}"
        )

# ========== 合约交易后台任务：定时更新持仓盈亏和自动强平 ==========
# 注意：get_market_price 已从 app.db.mock 导入，确保使用全局唯一的价格数据源


async def futures_position_monitor():
    """
    合约持仓监控后台任务
    每3秒执行一次，更新持仓盈亏并检查强平条件
    
    功能：
    1. 遍历所有持仓
    2. 获取最新市场价格
    3. 计算并更新未实现盈亏 (Unrealized PnL)
    4. 检查强平条件并执行强平
    
    注意：此任务在后台持续运行，不会阻塞主线程
    """
    while True:
        try:
            # 遍历所有持仓（使用列表副本，避免迭代时修改原列表）
            # 注意：这里使用深拷贝可能更安全，但为了性能考虑，使用浅拷贝即可
            # 因为我们在遍历时不会删除元素，只是更新字段
            positions_to_check = list(MOCK_POSITIONS)  # 创建列表副本
            
            for pos in positions_to_check:
                symbol = pos.get("symbol", "")
                user_address = pos.get("user_id") or pos.get("address", "")
                
                if not symbol or not user_address:
                    continue
                
                # 获取最新市场价格
                current_price = get_market_price(symbol)
                if current_price <= 0:
                    continue  # 跳过无效的交易对
                
                # 计算未实现盈亏
                entry_price = float(pos.get("entry_price", 0))
                size = float(pos.get("size", 0))
                side = pos.get("side", "LONG").upper()
                
                if entry_price <= 0 or size <= 0:
                    continue
                
                # 盈亏计算：(当前价 - 开仓价) * 数量 * 方向系数
                price_diff = current_price - entry_price
                if side == "SHORT":
                    price_diff = -price_diff  # 空单方向相反
                
                unrealized_pnl = price_diff * size
                
                # 检查强平条件（在更新持仓之前检查）
                liquidation_price = float(pos.get("liquidation_price", 0))
                should_liquidate = False
                
                if liquidation_price > 0:
                    if side == "LONG":
                        # 多单：当前价 <= 强平价 -> 强平
                        if current_price <= liquidation_price:
                            should_liquidate = True
                    else:  # SHORT
                        # 空单：当前价 >= 强平价 -> 强平
                        if current_price >= liquidation_price:
                            should_liquidate = True
                
                if should_liquidate:
                    # 执行强平：删除持仓，保证金归零（模拟被没收）
                    # 注意：保证金不会返还给用户，这是强平的惩罚机制
                    
                    # 获取持仓信息用于创建强平订单
                    margin = float(pos.get("margin", 0))
                    leverage = pos.get("leverage", 20)
                    
                    # 确定强平订单的方向（与持仓方向相反）
                    # LONG 持仓 -> SELL 强平，SHORT 持仓 -> BUY 强平
                    liquidation_side = "SELL" if side == "LONG" else "BUY"
                    
                    # 创建强平订单记录
                    timestamp = int(time.time())
                    order_id = f"fut_liq_{uuid.uuid4().hex[:12]}"
                    
                    # 计算已实现盈亏（强平时亏光保证金）
                    realized_pnl = -margin  # 强平时亏损全部保证金
                    
                    # 创建强平订单记录
                    liquidation_order = {
                        "order_id": order_id,
                        "user_id": user_address,
                        "symbol": symbol,
                        "side": liquidation_side,  # 与持仓方向相反
                        "type": "LIQUIDATION",  # 强平类型
                        "price": current_price,  # 强平执行价格
                        "amount": size,
                        "leverage": leverage,
                        "status": "FILLED",  # 强平立即成交
                        "timestamp": timestamp,
                        "create_time": timestamp,
                        "fee": 0.0,  # 强平时不收取手续费（已经亏光了）
                        "fee_currency": "USDT",
                        "realized_pnl": realized_pnl,  # 亏损全部保证金
                        "margin": margin,  # 记录被没收的保证金
                        "margin_type": pos.get("margin_type", "ISOLATED"),
                        "market_type": "futures",  # 必须标记为合约订单
                        "liquidation_price": liquidation_price,  # 记录强平价
                        "entry_price": entry_price  # 记录开仓价
                    }
                    
                    # 保存强平订单到数据库
                    create_order_in_db(liquidation_order)
                    
                    # 执行强平：删除持仓
                    update_position(user_address, symbol, {"size": 0})
                    
                    # 打印强平日志
                    print(f"\n{'='*60}")
                    print(f"[LIQUIDATION] User {user_address[:8]}... Position {symbol} CLOSED")
                    print(f"  Side: {side}")
                    print(f"  Entry Price: {entry_price:.2f}")
                    print(f"  Liquidation Price: {liquidation_price:.2f}")
                    print(f"  Current Price: {current_price:.2f}")
                    print(f"  Size: {size}")
                    print(f"  Margin Lost: {margin:.2f} USDT")
                    print(f"  Realized PnL: {realized_pnl:.2f} USDT")
                    print(f"  Liquidation Order ID: {order_id}")
                    print(f"{'='*60}\n")
                else:
                    # 更新持仓的未实现盈亏和标记价格（使用 update_position 确保数据一致性）
                    position_update = {
                        "symbol": symbol,
                        "side": side,
                        "size": size,
                        "entry_price": entry_price,
                        "mark_price": current_price,
                        "leverage": pos.get("leverage", 20),
                        "margin": pos.get("margin", 0),
                        "unrealized_pnl": unrealized_pnl,
                        "liquidation_price": liquidation_price,
                        "update_time": int(time.time())
                    }
                    update_position(user_address, symbol, position_update)
            
            # 等待3秒后继续下一次循环
            await asyncio.sleep(3)
            
        except Exception as e:
            # 捕获异常，避免任务崩溃
            import traceback
            print(f"[ERROR] Futures position monitor error: {str(e)}")
            print(traceback.format_exc())
            await asyncio.sleep(3)


@app.on_event("startup")
async def startup_event():
    """
    FastAPI 启动事件
    在服务器启动时启动后台任务
    """
    # 初始化 K 线数据库
    try:
        await KlineModel.init_db()
        print("[INFO] K 线数据库初始化完成")
    except Exception as e:
        print(f"[ERROR] K 线数据库初始化失败: {str(e)}")
    
    # 启动市场服务（包含历史数据同步和实时行情流）
    try:
        print("[INFO] 启动市场服务...")
        await market_service.initialize_exchange()
        await market_service.start()
        print("[INFO] 市场服务已启动（历史数据同步和实时行情流）")
    except Exception as e:
        print(f"[ERROR] 启动市场服务失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # 启动合约持仓监控任务
    asyncio.create_task(futures_position_monitor())
    print("[INFO] Futures position monitor started (runs every 3 seconds)")


@app.on_event("shutdown")
async def shutdown_event():
    """
    FastAPI 关闭事件
    在服务器关闭时清理资源
    """
    try:
        await market_service.close()
        print("[INFO] 市场服务已关闭")
    except Exception as e:
        print(f"[ERROR] 关闭市场服务失败: {str(e)}")


@app.get("/api/v1/users/me")
def get_user_info(current_user: Dict = Depends(get_current_user)):
    """
    获取当前用户信息（测试接口）
    演示如何使用 get_current_user 依赖函数保护 API
    
    功能：
    1. 自动从请求头中提取 Token
    2. 验证 Token 的有效性（签名、过期时间）
    3. 如果验证通过，返回用户信息
    4. 如果验证失败，返回 401 错误
    
    访问方式：
    GET /api/v1/users/me
    Headers: Authorization: Bearer <your-token>
    
    返回格式：
    {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "id": 1,
            "address": "0x...",
            "role": "user"
        }
    }
    """
    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": current_user
    }

@app.post("/api/v1/auth/connect")
def wallet_connect(request: WalletConnectRequest):
    """
    Web3 钱包认证接口
    参考币安 Web3 钱包的认证流程
    
    流程说明：
    1. 前端获取用户钱包地址
    2. 前端让用户签名一条消息（如 "Welcome to TruthFi. Sign to login."）
    3. 前端将地址、签名和消息发送到后端
    4. 后端使用 eth_account 验证签名是否由该地址对应的私钥签署
    5. 验证通过后返回 JWT Token
    """
    try:
        # 1. 验证地址格式（以太坊地址应该是 42 字符，以 0x 开头）
        if not request.address.startswith('0x') or len(request.address) != 42:
            raise HTTPException(
                status_code=400,
                detail="无效的钱包地址格式"
            )
        
        # 2. 将地址转换为小写（以太坊地址不区分大小写，但校验和地址除外）
        # 这里统一转换为小写进行验证
        address_lower = request.address.lower()
        
        # 3. 使用 eth_account 验证签名
        # 
        # ========== 为什么后端"信任"前端传来的 message 依然是安全的？==========
        # 
        # 这是一个基于数学三方匹配的安全机制：
        # 
        # 1. 前端发送三个数据：address（地址）、signature（签名）、message（消息）
        # 2. 后端使用这三个数据进行验证：
        #    - 使用 Account.recover_message(message, signature) 从签名中恢复地址
        #    - 比较恢复出的地址与前端传来的 address 是否一致
        # 
        # 安全原理（数学上的三方匹配）：
        # - 签名（signature）是用私钥对特定消息（message）进行加密的结果
        # - 只有拥有对应私钥的地址才能生成有效的签名
        # - 如果攻击者修改了 message，但 signature 是用原始 message 签名的
        #   那么 recover_message(修改后的message, signature) 恢复出的地址
        #   就不会与用户提供的 address 匹配，验证会失败
        # 
        # 具体流程：
        # 1. 用户在前端看到消息："欢迎登录 TruthFi。请签名以验证身份..."
        # 2. 用户用私钥签名这个消息，得到 signature
        # 3. 前端将 address、message、signature 发送到后端
        # 4. 后端验证：recover_message(message, signature) == address？
        #    - 如果匹配：说明 signature 确实是用 address 对应的私钥对 message 签名的
        #    - 如果不匹配：说明签名无效或消息被篡改
        # 
        # 为什么即使前端传来不同的 message 也是安全的？
        # - 如果攻击者修改了 message（比如改成"我是管理员"），但 signature 是用原始 message 签名的
        # - 后端执行 recover_message(修改后的message, signature) 会恢复出一个错误的地址
        # - 这个错误的地址不会与用户提供的 address 匹配，验证会失败
        # - 因此，攻击者无法通过修改 message 来绕过验证
        # 
        # ========== 如果前端传来的 message 多了一个空格会发生什么？==========
        # 
        # 假设原始消息是："Welcome to TruthFi. Sign to login."
        # 如果前端传来："Welcome to TruthFi. Sign to login. "（末尾多了一个空格）
        # 
        # 会发生什么：
        # 1. 用户在前端签名时，看到的是原始消息（没有空格）
        # 2. 用户用私钥签名原始消息，得到 signature_A
        # 3. 前端（被攻击者修改）发送了带空格的 message + signature_A
        # 4. 后端执行 recover_message("Welcome... ", signature_A)
        # 5. 由于消息内容不同，恢复出的地址不会与用户提供的 address 匹配
        # 6. 验证失败，返回 401 错误："签名验证失败：签名与地址不匹配"
        # 
        # 结论：
        # - 即使 message 只多了一个空格、一个标点、一个字符，验证都会失败
        # - 这是因为签名是消息内容的哈希值，任何微小的改动都会导致完全不同的哈希
        # - 这确保了消息的完整性：只有完全匹配的消息和签名才能通过验证
        
        # 将前端传来的消息编码为以太坊消息格式
        # encode_defunct 会将普通字符串转换为以太坊标准消息格式
        # 注意：这里直接使用前端传来的 request.message，不需要后端硬编码
        # 因为即使 message 被修改，签名验证也会失败（见上面的安全原理说明）
        message_encoded = encode_defunct(text=request.message)
        
        # 从签名中恢复地址
        # recover_message 会返回签署该消息的地址
        # 如果 message 或 signature 有任何不匹配，恢复出的地址就不会与用户提供的 address 一致
        recovered_address = Account.recover_message(message_encoded, signature=request.signature)
        
        # 4. 比较恢复出的地址和用户提供的地址（都转换为小写）
        # 这是三方匹配的关键步骤：
        # - 用户提供的 address（前端）
        # - 从签名恢复的地址（后端验证）
        # - 签名本身（前端）
        # 只有当这三个数据完全匹配时，验证才会通过
        if recovered_address.lower() != address_lower:
            raise HTTPException(
                status_code=401,
                detail="签名验证失败：签名与地址不匹配。请确保消息内容完全一致，包括空格和标点符号。"
            )
        
        # 5. 验证通过，使用 PyJWT 生成真正的 JWT Token
        # JWT Token 的结构：Header.Payload.Signature
        # - Header: 包含算法类型（如 HS256）
        # - Payload: 包含用户信息（如地址）和过期时间（exp）
        # - Signature: 使用 SECRET_KEY 对 Header 和 Payload 进行签名
        
        # 计算 Token 过期时间（当前时间 + 24 小时）
        expire_time = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
        
        # 构建 JWT Payload（Token 的有效载荷）
        # 标准字段说明：
        # - exp: 过期时间（Expiration Time），Unix 时间戳
        # - iat: 签发时间（Issued At），Unix 时间戳
        # - sub: 主题（Subject），通常是用户 ID 或地址
        token_payload = {
            "sub": address_lower,  # 主题：钱包地址
            "address": address_lower,  # 钱包地址（自定义字段）
            "type": "web3_auth",  # Token 类型
            "iat": datetime.utcnow(),  # 签发时间
            "exp": expire_time  # 过期时间（24 小时后）
        }
        
        # 使用 PyJWT 生成 Token
        # jwt.encode 会：
        # 1. 将 payload 转换为 JSON
        # 2. 添加 Header（包含算法信息）
        # 3. 使用 SECRET_KEY 对 Header 和 Payload 进行签名
        # 4. 返回完整的 JWT Token 字符串（格式：Header.Payload.Signature）
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return {
            "code": 200,
            "message": "认证成功",
            "data": {
                "token": token,
                "address": address_lower,
                "expires_in": TOKEN_EXPIRE_HOURS * 3600  # Token 有效期（秒）
            }
        }
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"认证过程出错: {str(e)}"
        )

# 在文件加载时打印成功消息
print("FastAPI app 已加载成功")

# 如果直接运行此文件，启动 uvicorn 服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    print("后端启动成功，访问 http://localhost:8000/docs 测试")