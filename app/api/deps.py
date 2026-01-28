"""
FastAPI 依赖函数模块
用于提供可复用的依赖函数，如用户认证、权限验证等
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from typing import Dict

# 从环境变量读取 SECRET_KEY（与 main.py 保持一致）
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# HTTP Bearer Token 认证
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    获取当前用户信息的依赖函数
    
    功能：
    1. 从请求头的 Authorization 字段提取 Token
    2. 使用 SECRET_KEY 验证 Token 的签名和过期时间
    3. 如果验证成功，返回模拟的用户对象
    4. 如果验证失败，抛出 401 异常
    
    返回值：
        Dict: 包含用户信息的字典
        {
            "id": 1,  # 模拟的用户 ID
            "address": "0x...",  # 从 Token 中解析出的钱包地址
            "role": "user"  # 用户角色
        }
    
    异常：
        HTTPException(401): Token 无效或过期时抛出
    
    使用示例：
        @app.get("/api/v1/users/me")
        def get_user_info(current_user: Dict = Depends(get_current_user)):
            return current_user
    """
    try:
        # 1. 从 HTTP Bearer Token 中提取 Token 字符串
        # credentials.credentials 就是前端发送的 Token（格式：Bearer <token>）
        token = credentials.credentials
        
        # 2. 使用 SECRET_KEY 解密和验证 Token
        # jwt.decode 会：
        # - 验证 Token 的签名是否有效（使用 SECRET_KEY）
        # - 检查 Token 是否过期（exp 字段）
        # - 如果验证通过，返回 Payload 中的数据
        # - 如果验证失败，抛出异常
        decoded_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        
        # 3. 从 Token 中提取用户信息
        # decoded_token 包含我们在生成 Token 时设置的 payload 数据
        # 例如：{"sub": "0x...", "address": "0x...", "type": "web3_auth", "iat": ..., "exp": ...}
        address = decoded_token.get("address") or decoded_token.get("sub")
        
        # 4. 确保地址统一转换为小写（防止大小写不匹配导致找不到数据）
        if address:
            address = address.lower()
        
        # 5. 返回模拟的用户对象
        # 注意：这里暂时使用 Mock 数据，不连接真实数据库
        # 实际项目中，应该根据 address 从数据库查询用户信息
        user = {
            "id": 1,  # 模拟的用户 ID（实际应该从数据库查询）
            "address": address,  # 钱包地址（从 Token 中解析，已转换为小写）
            "role": "user"  # 用户角色（实际应该从数据库查询）
        }
        
        return user
        
    except jwt.ExpiredSignatureError:
        # Token 已过期
        raise HTTPException(
            status_code=401,
            detail="Token 已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        # Token 无效（签名错误、格式错误等）
        raise HTTPException(
            status_code=401,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        # 其他错误
        raise HTTPException(
            status_code=401,
            detail=f"Token 验证失败: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
