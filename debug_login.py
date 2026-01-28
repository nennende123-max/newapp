#!/usr/bin/env python3
"""
TruthFi Web3 钱包认证接口测试脚本
用于在没有浏览器钱包的情况下测试 /api/v1/auth/connect 接口

使用方法：
1. 确保后端服务运行在 http://127.0.0.1:8000
2. 安装依赖：pip install eth-account httpx
3. 运行脚本：python debug_login.py
"""

from eth_account import Account
from eth_account.messages import encode_defunct
import httpx
import json

# 配置
API_URL = "http://127.0.0.1:8000/api/v1/auth/connect"

# 签名消息（需要和前端 i18n 配置保持一致）
# 英文版本（默认）
MESSAGE_EN = "Welcome to TruthFi. Sign to verify your identity and access institutional services."
# 中文版本（可选）
MESSAGE_ZH = "欢迎登录 TruthFi。请签名以验证身份并访问机构级服务。"

# 使用英文消息进行测试（可以改为 MESSAGE_ZH 测试中文）
MESSAGE = MESSAGE_EN


def generate_wallet():
    """
    生成一个全新的以太坊钱包（私钥和地址）
    
    返回：
        account: Account 对象，包含私钥和地址
    """
    # 使用 Account.create() 随机生成一个新的账户
    # 这会生成一个全新的私钥和对应的地址
    account = Account.create()
    return account


def sign_message(account, message):
    """
    使用私钥对消息进行签名
    
    参数：
        account: Account 对象，包含私钥
        message: 要签名的消息字符串
    
    返回：
        signature: 十六进制格式的签名字符串（0x 开头）
    """
    # 将消息编码为以太坊消息格式
    # encode_defunct 会添加以太坊标准前缀 "\x19Ethereum Signed Message:\n" + 消息长度
    message_encoded = encode_defunct(text=message)
    
    # 使用私钥对消息进行签名
    # sign_message 返回一个 SignedMessage 对象
    signed_message = account.sign_message(message_encoded)
    
    # 获取签名的十六进制字符串（0x 开头）
    signature = signed_message.signature.hex()
    
    return signature


def test_auth_connect(address, message, signature):
    """
    测试 /api/v1/auth/connect 接口
    
    参数：
        address: 钱包地址
        message: 原始消息
        signature: 签名
    
    返回：
        response: HTTP 响应对象
    """
    # 构建请求数据
    data = {
        "address": address,
        "message": message,
        "signature": signature
    }
    
    # 发送 POST 请求
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            API_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
    
    return response


def main():
    """
    主函数：执行完整的测试流程
    """
    print("=" * 80)
    print("TruthFi Web3 钱包认证接口测试")
    print("=" * 80)
    print()
    
    # 1. 生成随机钱包
    print("步骤 1: 生成随机钱包...")
    account = generate_wallet()
    address = account.address
    private_key = account.key.hex()
    
    print(f"✅ 钱包生成成功！")
    print(f"   地址 (Address): {address}")
    print(f"   私钥 (Private Key): {private_key}")
    print(f"   地址长度: {len(address)} 字符")
    print(f"   私钥长度: {len(private_key)} 字符")
    print()
    
    # 2. 准备签名消息
    print("步骤 2: 准备签名消息...")
    print(f"   消息内容: {MESSAGE}")
    print(f"   消息长度: {len(MESSAGE)} 字符")
    print()
    
    # 3. 对消息进行签名
    print("步骤 3: 使用私钥对消息进行签名...")
    signature = sign_message(account, MESSAGE)
    
    print(f"✅ 签名生成成功！")
    print(f"   签名 (Signature): {signature}")
    print(f"   签名长度: {len(signature)} 字符")
    print(f"   签名格式: 0x 开头的十六进制字符串")
    print()
    
    # 4. 验证签名（可选，用于调试）
    print("步骤 4: 验证签名（本地验证）...")
    message_encoded = encode_defunct(text=MESSAGE)
    recovered_address = Account.recover_message(message_encoded, signature=signature)
    
    if recovered_address.lower() == address.lower():
        print(f"✅ 签名验证通过！")
        print(f"   恢复出的地址: {recovered_address}")
        print(f"   与原始地址匹配: ✓")
    else:
        print(f"❌ 签名验证失败！")
        print(f"   恢复出的地址: {recovered_address}")
        print(f"   原始地址: {address}")
        return
    print()
    
    # 5. 发送请求到后端
    print("步骤 5: 发送认证请求到后端...")
    print(f"   API 地址: {API_URL}")
    print(f"   请求数据:")
    print(f"     - address: {address}")
    print(f"     - message: {MESSAGE}")
    print(f"     - signature: {signature[:20]}...{signature[-20:]}")
    print()
    
    try:
        response = test_auth_connect(address, MESSAGE, signature)
        
        print(f"✅ 请求发送成功！")
        print(f"   状态码: {response.status_code}")
        print()
        
        # 6. 解析并打印响应
        print("步骤 6: 解析后端响应...")
        try:
            response_data = response.json()
            print(f"✅ 响应解析成功！")
            print()
            print("=" * 80)
            print("后端响应内容:")
            print("=" * 80)
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            print("=" * 80)
            print()
            
            # 检查是否成功获取 Token
            if response.status_code == 200:
                if response_data.get("code") == 200:
                    token_data = response_data.get("data", {})
                    token = token_data.get("token")
                    
                    if token:
                        print("🎉 测试成功！成功获取 JWT Token！")
                        print()
                        print(f"Token: {token}")
                        print(f"Token 长度: {len(token)} 字符")
                        print(f"钱包地址: {token_data.get('address')}")
                        print(f"过期时间: {token_data.get('expires_in')} 秒")
                        print()
                        print("=" * 80)
                        print("✅ 后端逻辑完美！认证流程正常工作！")
                        print("=" * 80)
                    else:
                        print("⚠️  响应成功，但未找到 Token")
                else:
                    print(f"❌ 后端返回错误代码: {response_data.get('code')}")
                    print(f"   错误信息: {response_data.get('message')}")
            else:
                print(f"❌ HTTP 请求失败，状态码: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except json.JSONDecodeError:
            print(f"❌ 响应不是有效的 JSON 格式")
            print(f"   响应内容: {response.text}")
            
    except httpx.ConnectError:
        print("❌ 无法连接到后端服务器！")
        print(f"   请确保后端服务运行在 {API_URL}")
        print("   启动命令: python main.py 或 uvicorn main:app --reload")
    except httpx.TimeoutException:
        print("❌ 请求超时！")
    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")


if __name__ == "__main__":
    main()
