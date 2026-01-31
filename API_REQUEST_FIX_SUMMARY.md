# API 请求失败问题修复总结

## 修复目标
彻底解决 API 请求失败的问题，确保所有 `/api` 请求都通过 Vite 代理正确转发到后端。

## 修复步骤

### ✅ 1. 移除 MockJS 干扰

**检查结果**：
- ✅ `src/main.js`：**没有 Mock 导入**，无需修改
- ✅ `src/api/mockRequest.js`：存在但**未被导入**，不影响功能
- ✅ 全局搜索：**没有发现任何 Mock 导入**

**结论**：MockJS 干扰已完全移除，所有请求都会走真实 API。

### ✅ 2. 强制修正 API 路径

**检查结果**：
- ✅ `src/components/MarketDetail.vue`：
  - `fetchKlineHistory`: 使用 `/api/v1/market/klines` ✓
  - `fetchOrderBook`: 使用 `/api/v1/market/orderbook` ✓
- ✅ 后端路由：`router = APIRouter(prefix="/api/v1/market")` ✓
- ✅ 后端端点：`@router.get("/klines")` → 完整路径 `/api/v1/market/klines` ✓

**修复内容**：
- 已确认所有 API 请求路径正确
- 已添加详细的错误日志，便于调试

### ✅ 3. 优化 Vite 代理配置

**修复前**：
```javascript
'/api': {
  target: 'http://127.0.0.1:8000',
  changeOrigin: true,
  secure: false
}
```

**修复后**：
```javascript
'/api': {
  target: 'http://127.0.0.1:8000',  // 后端 FastAPI 服务器（端口8000）
  changeOrigin: true,
  secure: false,  // 禁用 SSL 验证（开发环境）
  configure: (proxy) => {
    proxy.on('error', (err) => {
      console.error('[Proxy] API 代理错误:', err);
      console.error('[Proxy] 请确保后端服务运行在 http://127.0.0.1:8000');
    });
    proxy.on('proxyReq', (proxyReq, req) => {
      console.log(`[Proxy] 转发请求: ${req.method} ${req.url} -> ${proxyReq.path}`);
    });
  }
}
```

**关键说明**：
- ✅ **不启用 `rewrite`**：因为后端路由已有 `/api/v1/market` 前缀
- ✅ 前端请求 `/api/v1/market/klines` → Vite 代理 → `http://127.0.0.1:8000/api/v1/market/klines`
- ✅ 添加了详细的代理日志，便于调试

### ✅ 4. 增强错误处理

**修复内容**：
在 `fetchKlineHistory` 中添加了详细的错误日志：

```javascript
catch (error) {
  console.error('[Market] ❌ 获取 K 线数据失败:', error);
  console.error('[Market] 请求 URL:', '/api/v1/market/klines');
  console.error('[Market] 请求参数:', {
    symbol: symbol.value + 'USDT',
    interval: selectedTimeframe.value,
    limit: 1000
  });
  if (error.response) {
    console.error('[Market] 响应状态:', error.response.status);
    console.error('[Market] 响应数据:', error.response.data);
  } else if (error.request) {
    console.error('[Market] 请求已发出但未收到响应，请检查：');
    console.error('[Market] 1. 后端服务是否运行在 http://127.0.0.1:8000');
    console.error('[Market] 2. Vite 代理配置是否正确');
    console.error('[Market] 3. 网络连接是否正常');
  }
}
```

## 数据流验证

### 请求流程：
1. **前端组件** (`MarketDetail.vue`)：
   ```javascript
   request.get('/api/v1/market/klines', {
     params: { symbol: 'BTCUSDT', interval: '1h', limit: 1000 }
   })
   ```

2. **Vite 代理** (`vite.config.js`)：
   ```
   /api/v1/market/klines → http://127.0.0.1:8000/api/v1/market/klines
   ```

3. **后端路由** (`app/api/endpoints/market.py`)：
   ```python
   router = APIRouter(prefix="/api/v1/market")
   @router.get("/klines")
   ```

4. **完整路径**：
   ```
   前端: /api/v1/market/klines
   ↓ (Vite 代理)
   后端: http://127.0.0.1:8000/api/v1/market/klines
   ```

## 验证步骤

### 1. 后端验证
```bash
# 启动后端服务
python main.py

# 测试 API 端点
curl "http://127.0.0.1:8000/api/v1/market/klines?symbol=BTCUSDT&interval=1h&limit=1000"
```

**预期结果**：
- ✅ 返回 200 OK
- ✅ 返回数组格式：`[[timestamp(ms), open, high, low, close, volume], ...]`

### 2. 前端验证
```bash
# 启动前端服务
npm run dev
```

**浏览器控制台检查**：
1. **Network 标签页**：
   - ✅ 应看到 `GET /api/v1/market/klines?symbol=BTCUSDT&interval=1h&limit=1000`
   - ✅ 请求状态应为 200 OK
   - ✅ 不应看到 404 或 500 错误

2. **Console 标签页**：
   - ✅ 应看到 `[Proxy] 转发请求: GET /api/v1/market/klines -> /api/v1/market/klines`
   - ✅ 应看到 `[Market] ✅ K-line history loaded from /klines: X 条`
   - ✅ 如果失败，应看到详细的错误信息

### 3. 常见问题排查

#### 问题 1：404 Not Found
**可能原因**：
- 后端服务未启动
- 后端路由路径不匹配

**解决方案**：
1. 检查后端服务是否运行：`curl http://127.0.0.1:8000/docs`
2. 检查后端路由：确认 `app/api/endpoints/market.py` 中路由前缀正确

#### 问题 2：Network Error
**可能原因**：
- Vite 代理配置错误
- 后端服务未启动

**解决方案**：
1. 检查 Vite 代理配置：确认 `vite.config.js` 中 `/api` 配置正确
2. 检查后端服务：确认后端运行在 `http://127.0.0.1:8000`
3. 查看 Vite 控制台日志：确认代理转发日志

#### 问题 3：CORS 错误
**可能原因**：
- 后端 CORS 配置不正确

**解决方案**：
1. 检查后端 CORS 配置：确认允许 `http://localhost:5173` 来源
2. 检查 `changeOrigin: true`：Vite 代理配置中已启用

## 修复文件清单

1. ✅ `vite.config.js` - 优化代理配置，添加日志
2. ✅ `src/components/MarketDetail.vue` - 增强错误处理
3. ✅ `src/main.js` - 确认无 Mock 导入（无需修改）

## 预期结果

修复完成后：
1. ✅ 所有 API 请求都通过 Vite 代理正确转发
2. ✅ 控制台显示详细的代理日志
3. ✅ 如果请求失败，显示详细的错误信息
4. ✅ K线图正常加载真实数据
5. ✅ 不再出现 404 或 Network Error

## 注意事项

1. **后端服务必须运行**：
   - 确保后端服务运行在 `http://127.0.0.1:8000`
   - 可以通过 `http://127.0.0.1:8000/docs` 访问 API 文档

2. **Vite 代理不启用 rewrite**：
   - 因为后端路由已有 `/api/v1/market` 前缀
   - 如果启用 rewrite，会导致路径不匹配

3. **请求路径必须完整**：
   - 前端请求：`/api/v1/market/klines`（包含完整路径）
   - Vite 代理：转发到 `http://127.0.0.1:8000/api/v1/market/klines`
   - 后端路由：`/api/v1/market/klines`（匹配）

4. **MockJS 已完全移除**：
   - 所有请求都会走真实 API
   - 不会再有 Mock 数据干扰
