"""
资产相关 API 端点
提供充值、提现、查询余额等功能
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from app.api.deps import get_current_user
from app.db.mock import (
    get_user_assets, 
    update_user_assets,
    get_user_available_assets,
    get_user_frozen_assets,
    get_user_positions
)

# 创建路由实例
router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


class DepositRequest(BaseModel):
    """充值请求模型"""
    amount: float  # 充值金额
    currency: str = "USDT"  # 币种，默认为 USDT


class WithdrawRequest(BaseModel):
    """提现请求模型"""
    amount: float  # 提现金额
    currency: str = "USDT"  # 币种，默认为 USDT


@router.get("/balance")
def get_balance(current_user: Dict = Depends(get_current_user)):
    """
    获取当前用户的资产余额（包含可用和冻结）
    
    功能：
    1. 从 Token 中解析出用户地址
    2. 从 MOCK_USER_ASSETS 中查询该用户的余额
    3. 如果用户不存在，返回默认值（全为0）
    
    返回格式：
    {
        "code": 200,
        "message": "获取余额成功",
        "data": {
            "USDT": 50000.0,
            "BTC": 0.0,
            "BEAT": 0.0,
            "USDT_frozen": 0.0,
            "BTC_frozen": 0.0,
            "BEAT_frozen": 0.0
        }
    }
    """
    try:
        # 1. 从 current_user 中获取钱包地址
        address = current_user.get("address")
        
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        
        # 2. 将地址转换为小写（确保忽略大小写差异）
        address_lower = address.lower()
        
        # 3. 从 Mock 数据库中获取用户资产（包含可用和冻结）
        assets = get_user_assets(address_lower)
        
        # 4. 添加调试日志：打印查询的地址和余额
        print(f"查询地址: {address_lower}, 余额: {assets}")
        
        return {
            "code": 200,
            "message": "获取余额成功",
            "data": assets
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取余额失败: {str(e)}"
        )


@router.get("/")
def read_assets(current_user: Dict = Depends(get_current_user)):
    """
    获取当前用户的资产详情（包含账户权益计算）
    
    功能：
    1. 从 Token 中解析出用户地址
    2. 分别获取可用余额和冻结余额
    3. 计算账户权益 (Equity) = 可用余额 + 冻结保证金 + 合约未实现盈亏
    4. 返回结构化的资产数据
    
    账户权益计算公式：
    Equity = USDT可用余额 + USDT冻结余额 + 所有合约持仓的未实现盈亏(Unrealized PnL)
    
    返回格式：
    {
        "code": 200,
        "message": "获取资产成功",
        "data": {
            "balance": 50000.0,      # USDT 可用余额（兼容旧代码）
            "equity": 51234.56,      # 账户权益（包含合约盈亏）
            "holdings": {             # 可用余额（所有币种）
                "USDT": 50000.0,
                "BTC": 0.0,
                "BEAT": 0.0
            },
            "frozen": {               # 冻结余额（所有币种）
                "USDT": 0.0,
                "BTC": 0.0,
                "BEAT": 0.0
            },
            "futures_unrealized_pnl": 1234.56  # 合约未实现盈亏总计
        }
    }
    """
    try:
        # 1. 从 current_user 中获取钱包地址
        address = current_user.get("address")
        
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        
        # 2. 将地址转换为小写（确保忽略大小写差异）
        address_lower = address.lower()
        
        # 3. 分别获取可用余额和冻结余额
        available = get_user_available_assets(address_lower)
        frozen = get_user_frozen_assets(address_lower)
        
        # 4. 计算 USDT 可用余额和冻结余额
        usdt_available = available.get("USDT", 0.0)
        usdt_frozen = frozen.get("USDT", 0.0)
        
        # 5. 获取所有合约持仓并计算未实现盈亏总和
        positions = get_user_positions(address_lower)
        futures_unrealized_pnl = 0.0
        
        for pos in positions:
            # 获取持仓的未实现盈亏（后台任务已实时更新）
            unrealized_pnl = float(pos.get("unrealized_pnl", 0.0))
            futures_unrealized_pnl += unrealized_pnl
        
        # 6. 计算账户权益 (Equity)
        # Equity = 可用余额 + 冻结保证金 + 合约未实现盈亏
        equity = usdt_available + usdt_frozen + futures_unrealized_pnl
        
        # 7. 添加调试日志
        print(f"查询地址: {address_lower}")
        print(f"  可用余额: {usdt_available:.2f} USDT")
        print(f"  冻结余额: {usdt_frozen:.2f} USDT")
        print(f"  合约未实现盈亏: {futures_unrealized_pnl:.2f} USDT")
        print(f"  账户权益: {equity:.2f} USDT")
        
        return {
            "code": 200,
            "message": "获取资产成功",
            "data": {
                "balance": usdt_available,              # USDT 可用余额（兼容旧代码）
                "equity": equity,                        # 账户权益（包含合约盈亏）
                "holdings": available,                   # 可用余额（所有币种）
                "frozen": frozen,                        # 冻结余额（所有币种）
                "futures_unrealized_pnl": futures_unrealized_pnl  # 合约未实现盈亏总计
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取资产失败: {str(e)}"
        )


@router.post("/deposit")
def deposit(
    request: DepositRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    充值接口（模拟）
    
    功能：
    1. 接收充值金额和币种
    2. 直接修改内存账本，将用户余额加上该金额
    3. 返回最新余额
    
    请求格式：
    {
        "amount": 1000.0,
        "currency": "USDT"
    }
    
    返回格式：
    {
        "code": 200,
        "message": "充值成功",
        "data": {
            "USDT": 51000.0,
            "BTC": 0.0,
            "BEAT": 0.0
        }
    }
    """
    try:
        # 1. 验证请求参数
        if request.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="充值金额必须大于0"
            )
        
        if request.currency not in ["USDT", "BTC", "ETH", "BNB", "SOL", "DOGE", "TRX", "BEAT", "AIC"]:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的币种: {request.currency}"
            )
        
        # 2. 获取用户地址并转换为小写
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 3. 获取当前资产
        current_assets = get_user_assets(address_lower)
        
        # 4. 更新资产（加上充值金额）
        new_balance = current_assets[request.currency] + request.amount
        current_assets[request.currency] = new_balance
        
        # 5. 保存到 Mock 数据库（使用小写地址）
        updated_assets = update_user_assets(address_lower, current_assets)
        
        return {
            "code": 200,
            "message": "充值成功",
            "data": updated_assets
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"充值失败: {str(e)}"
        )


@router.post("/withdraw")
def withdraw(
    request: WithdrawRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    提现接口（模拟）
    
    功能：
    1. 接收提现金额和币种
    2. 检查余额是否充足
    3. 如果充足，将余额减去该金额
    4. 如果不足，返回错误
    5. 返回最新余额
    
    请求格式：
    {
        "amount": 1000.0,
        "currency": "USDT"
    }
    
    返回格式：
    {
        "code": 200,
        "message": "提现成功",
        "data": {
            "USDT": 49000.0,
            "BTC": 0.0,
            "BEAT": 0.0
        }
    }
    """
    try:
        # 1. 验证请求参数
        if request.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="提现金额必须大于0"
            )
        
        if request.currency not in ["USDT", "BTC", "ETH", "BNB", "SOL", "DOGE", "TRX", "BEAT", "AIC"]:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的币种: {request.currency}"
            )
        
        # 2. 获取用户地址并转换为小写
        address = current_user.get("address")
        if not address:
            raise HTTPException(
                status_code=400,
                detail="无法获取用户地址"
            )
        address_lower = address.lower()
        
        # 3. 获取当前资产
        current_assets = get_user_assets(address_lower)
        
        # 4. 检查余额是否充足
        current_balance = current_assets[request.currency]
        if current_balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail=f"余额不足。当前余额: {current_balance} {request.currency}，提现金额: {request.amount} {request.currency}"
            )
        
        # 5. 更新资产（减去提现金额）
        new_balance = current_balance - request.amount
        current_assets[request.currency] = new_balance
        
        # 6. 保存到 Mock 数据库（使用小写地址）
        updated_assets = update_user_assets(address_lower, current_assets)
        
        return {
            "code": 200,
            "message": "提现成功",
            "data": updated_assets
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提现失败: {str(e)}"
        )
