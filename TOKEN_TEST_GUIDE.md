# Token 自动携带与后端验证测试指南

## 📋 测试准备

### 1. 确保后端服务运行
```bash
# 在项目根目录下运行
uvicorn main:app --reload
```

后端服务应该运行在：`http://127.0.0.1:8000`

### 2. 确保前端服务运行
```bash
# 在项目根目录下运行
npm run dev
```

前端服务应该运行在：`http://localhost:5173`

---

## 🧪 测试方法一：Swagger UI 测试

### 步骤 1：打开 Swagger UI
访问：`http://127.0.0.1:8000/docs`

### 步骤 2：获取 Token
1. 找到 `/api/v1/auth/connect` 接口
2. 点击 "Try it out"
3. 填写请求体（需要先通过前端钱包登录获取真实的 address、signature、message）
4. 点击 "Execute"
5. 复制返回的 `token` 值

### 步骤 3：测试 `/api/v1/users/me` 接口

#### 方法 A：使用 Swagger UI 的 Authorize 功能
1. 点击页面右上角的 **"Authorize"** 按钮（🔒 图标）
2. 在弹出的对话框中，在 `Value` 输入框中输入：`Bearer <你的token>`
   - 例如：`Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **注意**：不要忘记 `Bearer ` 前缀和后面的空格
3. 点击 "Authorize"
4. 点击 "Close"
5. 找到 `/api/v1/users/me` 接口
6. 点击 "Try it out"
7. 点击 "Execute"
8. 应该能看到返回的用户信息：
   ```json
   {
     "code": 200,
     "message": "获取用户信息成功",
     "data": {
       "id": 1,
       "address": "0x...",
       "role": "user"
     }
   }
   ```

#### 方法 B：直接在请求头中添加 Authorization
1. 找到 `/api/v1/users/me` 接口
2. 点击 "Try it out"
3. 在请求参数中，找到 "Headers" 部分
4. 添加一个新的 Header：
   - Key: `Authorization`
   - Value: `Bearer <你的token>`
5. 点击 "Execute"

### 步骤 4：测试 Token 过期/无效的情况
1. 使用一个无效的 Token（例如：`Bearer invalid_token`）
2. 执行请求
3. 应该返回 401 错误：
   ```json
   {
     "detail": "无效的 Token"
   }
   ```

---

## 🧪 测试方法二：前端调用测试

### 步骤 1：在前端登录获取 Token
1. 打开前端应用：`http://localhost:5173`
2. 点击 "连接钱包" 按钮
3. 在 MetaMask 中确认连接和签名
4. 登录成功后，Token 会自动保存到 `localStorage`

### 步骤 2：在浏览器控制台测试
打开浏览器开发者工具（F12），在 Console 中输入：

```javascript
// 导入 API 函数
import { getCurrentUser } from '@/api/user';

// 调用接口
getCurrentUser().then(response => {
  console.log('✅ 获取用户信息成功:', response.data);
}).catch(error => {
  console.error('❌ 请求失败:', error);
});
```

### 步骤 3：在 Vue 组件中测试
在任意 Vue 组件中（例如 `Me.vue`），添加测试代码：

```vue
<script setup>
import { onMounted } from 'vue';
import { getCurrentUser } from '@/api/user';

onMounted(async () => {
  try {
    // 调用获取用户信息接口
    // request.js 会自动从 localStorage 读取 token 并添加到请求头
    const response = await getCurrentUser();
    console.log('✅ 用户信息:', response.data.data);
    // 输出：{ id: 1, address: "0x...", role: "user" }
  } catch (error) {
    console.error('❌ 获取用户信息失败:', error);
    // 如果是 401 错误，request.js 会自动清除 token 并跳转到首页
  }
});
</script>
```

### 步骤 4：测试 401 自动登出
1. 手动修改 `localStorage` 中的 token 为无效值：
   ```javascript
   localStorage.setItem('token', 'invalid_token');
   ```
2. 调用 `getCurrentUser()` 接口
3. 应该看到：
   - 控制台输出：`⚠️ Token 已过期或无效，执行登出操作`
   - `localStorage` 中的 `token` 被清除
   - 页面自动跳转到首页

---

## ✅ 验证清单

- [ ] **请求拦截器测试**：确认每次请求都自动携带 `Authorization: Bearer <token>` 头
- [ ] **Token 验证测试**：使用有效 Token 能成功获取用户信息
- [ ] **401 错误测试**：使用无效 Token 返回 401 错误
- [ ] **自动登出测试**：401 错误时自动清除 token 并跳转首页
- [ ] **Swagger UI 测试**：能在 Swagger UI 中成功测试接口
- [ ] **前端调用测试**：前端能成功调用接口并获取用户信息

---

## 🔍 调试技巧

### 1. 检查 Token 是否正确携带
在浏览器开发者工具的 Network 标签中：
1. 找到 `/api/v1/users/me` 请求
2. 查看 Request Headers
3. 确认有 `Authorization: Bearer <token>` 字段

### 2. 检查 Token 内容
在浏览器控制台中：
```javascript
// 查看 localStorage 中的 token
console.log('Token:', localStorage.getItem('token'));

// 解析 Token（仅用于调试，不要在生产环境使用）
const token = localStorage.getItem('token');
if (token) {
  const parts = token.split('.');
  const payload = JSON.parse(atob(parts[1]));
  console.log('Token Payload:', payload);
}
```

### 3. 检查后端日志
在后端终端中查看请求日志，确认：
- Token 是否正确接收
- Token 验证是否通过
- 返回的状态码是什么

---

## 📝 常见问题

### Q1: Swagger UI 中显示 401 错误
**原因**：Token 格式不正确或已过期
**解决**：
- 确认 Token 格式：`Bearer <token>`（注意 `Bearer` 后面有空格）
- 重新登录获取新的 Token

### Q2: 前端调用接口时没有自动携带 Token
**原因**：`localStorage` 中没有 `token`
**解决**：
- 确认已成功登录
- 检查 `localStorage.getItem('token')` 是否有值

### Q3: 401 错误时没有自动跳转
**原因**：响应拦截器可能没有正确配置
**解决**：
- 检查 `src/utils/request.js` 中的响应拦截器代码
- 确认 `router.push('/')` 是否正确执行

---

## 🎯 下一步

完成测试后，你可以：
1. 在更多接口中使用 `Depends(get_current_user)` 来保护 API
2. 根据实际需求修改 `get_current_user` 函数，从数据库查询真实用户信息
3. 添加更多用户角色和权限验证逻辑
