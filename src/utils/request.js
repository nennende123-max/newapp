/**
 * Axios 请求配置文件
 * 统一管理所有 HTTP 请求的基础配置
 * 
 * 功能：
 * 1. 请求拦截器：自动添加 Token 到请求头
 * 2. 响应拦截器：统一处理错误，特别是 401 未授权错误
 */

import axios from 'axios';
import router from '@/router';

// 创建 axios 实例
const request = axios.create({
  // baseURL: API 的基础地址
  // 使用空字符串，因为各 API 路径已包含 /api/v1/...，Vite 会把 /api 代理到 127.0.0.1:8000
  // 若写 baseURL: '/api' 会与路径里的 /api 重复，变成 /api/api/v1/... 导致 404
  baseURL: '',
  
  // timeout: 请求超时时间（毫秒）
  // 如果服务器在 10 秒内没有响应，请求会被自动取消
  // 防止因为网络问题或服务器无响应导致前端一直等待
  timeout: 10000,  // 10 秒
  
  // 默认请求头
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求头以支持 CORS
request.defaults.headers.common['Content-Type'] = 'application/json';

/**
 * 请求拦截器：在发送请求之前做一些处理
 * 
 * 作用：
 * 1. 检查 localStorage 中是否存在 token
 * 2. 如果存在，自动添加到请求头的 Authorization 字段
 * 3. 格式：Bearer <token>（这是 JWT Token 的标准传递方式）
 * 
 * 好处：
 * - 不需要在每个 API 调用中手动添加 token
 * - 统一管理认证逻辑，减少重复代码
 * - 如果 token 不存在，请求会正常发送（不会报错），后端可以根据需要处理
 */
request.interceptors.request.use(
  (config) => {
    // 记录请求日志
    console.log('发送请求:', config.url);
    
    // 1. 从 localStorage 获取 token
    // localStorage.getItem('token') 会返回存储的 token 字符串，如果不存在则返回 null
    const token = localStorage.getItem('token');
    
    // 2. 如果 token 存在，自动添加到请求头
    if (token) {
      // 将 token 添加到请求头的 Authorization 字段
      // 格式：Bearer <token>
      // 这是 HTTP 标准中传递认证令牌的方式
      // 后端可以通过 request.headers.get('Authorization') 获取并验证
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 3. 返回配置对象，axios 会使用这个配置发送请求
    return config;
  },
  (error) => {
    // 请求错误时的处理（例如：请求配置错误）
    // 这种情况很少发生，通常是代码错误导致的
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器：在收到响应之后做一些处理
 * 
 * 作用：
 * 1. 统一处理成功响应（可选：格式化数据）
 * 2. 统一处理错误响应，特别是 401 未授权错误
 * 3. 当收到 401 时，执行登出操作：清除 token 和用户信息，跳转到首页
 */
request.interceptors.response.use(
  (response) => {
    // 成功响应处理
    // 如果后端返回的数据格式是 { code: 200, data: {...}, msg: 'success' }
    // 可以在这里统一处理，直接返回 data 部分
    // return response.data;
    
    // 当前直接返回整个响应对象，让调用方自己处理
    return response;
  },
  (error) => {
    // 处理 Network Error
    if (error.message && error.message.includes('Network Error')) {
      console.error('网络错误: 请确保后端运行在 http://127.0.0.1:8000');
      return Promise.reject(error);
    }
    
    // 记录响应错误日志
    console.error('Response error:', error.message);
    
    // 错误响应处理
    if (error.response) {
      // 服务器返回了错误响应（有状态码）
      const status = error.response.status;
      
      switch (status) {
        case 401:
          // 401 Unauthorized：Token 过期或无效
          // 这是认证失败的情况，需要执行登出操作
          console.warn('⚠️ Token 已过期或无效，执行登出操作');
          
          // 1. 清除 localStorage 中的 token
          // 这是最重要的步骤，确保下次请求不会携带无效的 token
          localStorage.removeItem('token');
          
          // 2. 清除其他用户相关信息（可选，根据实际需求）
          // 清除钱包地址
          localStorage.removeItem('walletAddress');
          // 清除其他可能的用户信息
          localStorage.removeItem('username');
          
          // 3. 清除 Store 中的用户状态（如果使用了 Pinia）
          // 使用动态导入避免循环依赖问题
          // 这样即使 store 导入了 request，也不会造成循环依赖
          try {
            import('@/stores/assets').then(({ useAssetStore }) => {
              // 动态获取 store 实例并清除状态
              const assetStore = useAssetStore();
              if (assetStore && typeof assetStore.disconnectWallet === 'function') {
                assetStore.disconnectWallet();
              }
            }).catch(() => {
              // 如果导入失败，忽略（可能是循环依赖或其他原因）
              // 不影响其他清理操作
            });
          } catch (e) {
            // 如果动态导入失败，忽略
            console.warn('无法清除 Store 状态，将在页面刷新时自动清除');
          }
          
          // 4. 强制跳转到首页（或刷新页面）
          // 方式一：跳转到首页（推荐，用户体验更好）
          router.push('/').catch(() => {
            // 如果路由跳转失败（例如已经在首页），则刷新页面
            window.location.reload();
          });
          
          // 方式二：直接刷新页面（备选方案）
          // window.location.reload();
          
          // 5. 显示友好的错误提示（可选）
          // 注意：这里不能使用 showToast，因为可能造成循环依赖
          // 如果需要提示，可以在组件中处理
          
          break;
          
        case 403:
          // 403 Forbidden：拒绝访问（权限不足）
          console.error('❌ 拒绝访问：权限不足');
          break;
          
        case 404:
          // 404 Not Found：请求的资源不存在
          console.error('❌ 请求的资源不存在');
          break;
          
        case 500:
          // 500 Internal Server Error：服务器内部错误
          console.error('❌ 服务器错误');
          break;
          
        default:
          // 其他错误状态码
          console.error(`❌ 请求失败 (${status}):`, error.message);
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      // 可能的原因：
      // 1. 网络连接问题
      // 2. 服务器未启动
      // 3. CORS 跨域问题
      // 4. 请求超时
      console.error('❌ 网络错误：请求已发出但未收到响应');
      console.error('请检查：1. 网络连接 2. 后端服务是否运行 3. CORS 配置');
    } else {
      // 在设置请求时发生了错误
      // 这通常是代码错误导致的，例如：请求配置格式错误
      console.error('❌ 请求配置错误:', error.message);
    }
    
    // 返回被拒绝的 Promise，让调用方可以继续处理错误
    return Promise.reject(error);
  }
);

// 导出配置好的 axios 实例
export default request;
