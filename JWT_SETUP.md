# JWT 认证设置指南

## 1. 安装依赖

### Python 依赖

```bash
# 激活虚拟环境（如果使用）
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install PyJWT eth-account
```

## 2. SECRET_KEY 安全管理

### ⚠️ 重要：SECRET_KEY 绝不能提交到代码仓库！

### 方式一：使用环境变量（推荐）

#### Windows (PowerShell):
```powershell
# 设置环境变量（当前会话）
$env:JWT_SECRET_KEY = "your-super-secret-key-here-change-this"

# 永久设置（需要管理员权限）
[System.Environment]::SetEnvironmentVariable("JWT_SECRET_KEY", "your-super-secret-key-here", "User")
```

#### Windows (CMD):
```cmd
set JWT_SECRET_KEY=your-super-secret-key-here-change-this
```

#### Mac/Linux:
```bash
# 临时设置（当前终端会话）
export JWT_SECRET_KEY="your-super-secret-key-here-change-this"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export JWT_SECRET_KEY="your-super-secret-key-here-change-this"' >> ~/.bashrc
source ~/.bashrc
```

### 方式二：使用 .env 文件（开发环境推荐）

1. 创建 `.env` 文件（在项目根目录）：
```env
JWT_SECRET_KEY=your-super-secret-key-here-change-this-to-a-random-string
```

2. 安装 python-dotenv：
```bash
pip install python-dotenv
```

3. 在 `main.py` 开头添加：
```python
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

4. **重要**：将 `.env` 添加到 `.gitignore`，不要提交到代码仓库！

### 方式三：使用配置文件（生产环境）

创建 `config.py`：
```python
import os

# 从环境变量读取，如果不存在则抛出错误（强制设置）
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY 环境变量未设置！")
```

### 生成安全的 SECRET_KEY

```python
import secrets
# 生成一个 32 字节的随机密钥（Base64 编码）
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

## 3. 测试 JWT 认证

### 1. 启动后端
```bash
python main.py
# 或
uvicorn main:app --reload
```

### 2. 连接钱包获取 Token
- 打开前端页面
- 点击"连接钱包"
- 完成签名后，Token 会保存到 localStorage

### 3. 测试受保护的接口

使用 curl 测试：
```bash
# 替换 <your-token> 为实际的 token
curl -X GET "http://127.0.0.1:8000/api/v1/user/me" \
  -H "Authorization: Bearer <your-token>"
```

使用 Postman：
1. 方法：GET
2. URL：`http://127.0.0.1:8000/api/v1/user/me`
3. Headers：
   - Key: `Authorization`
   - Value: `Bearer <your-token>`

## 4. Token 结构说明

JWT Token 由三部分组成，用 `.` 分隔：
```
Header.Payload.Signature
```

### Header（头部）
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload（载荷）
```json
{
  "sub": "0x1234...",
  "address": "0x1234...",
  "type": "web3_auth",
  "iat": 1234567890,
  "exp": 1234654290
}
```

### Signature（签名）
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

## 5. 安全最佳实践

1. ✅ **使用强密码作为 SECRET_KEY**（至少 32 字符）
2. ✅ **定期轮换 SECRET_KEY**（但会导致所有 Token 失效）
3. ✅ **使用 HTTPS**（生产环境必须）
4. ✅ **设置合理的过期时间**（当前为 24 小时）
5. ✅ **不要在前端代码中暴露 SECRET_KEY**
6. ✅ **使用环境变量或密钥管理服务**（如 AWS Secrets Manager）
