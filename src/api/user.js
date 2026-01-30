/**
 * 用户相关 API
 * 负责登录、用户信息等功能
 */

import request from '@/utils/request';

/**
 * Web3 钱包认证接口
 * 将钱包地址、签名和消息发送到后端进行验证
 * 
 * @param {Object} authData - 认证数据
 * @param {string} authData.address - 钱包地址
 * @param {string} authData.signature - 签名
 * @param {string} authData.message - 原始消息
 * @returns {Promise} 返回认证结果，包含 token
 * 
 * baseURL 使用说明：
 * 在 src/utils/request.js 中我们配置了 baseURL: 'http://127.0.0.1:8000'
 * 当调用 request.post('/api/v1/auth/connect', data) 时：
 * - axios 会自动将 baseURL 和路径拼接
 * - 实际请求的 URL 是：http://127.0.0.1:8000/api/v1/auth/connect
 * - 这样我们就不需要在每个 API 调用中都写完整的 URL
 * - 如果后端地址改变，只需要修改 request.js 中的 baseURL 即可
 */
export function walletConnect(authData) {
  return request.post('/api/v1/auth/connect', {
    address: authData.address,
    signature: authData.signature,
    message: authData.message
  });
}

/**
 * 获取当前用户信息（测试接口）
 * 这个接口会自动携带 token（通过 request.js 的请求拦截器）
 * 如果 token 无效或过期，会自动返回 401，并触发登出操作
 * 
 * @returns {Promise} 返回用户信息
 * 
 * 返回格式：
 * {
 *   code: 200,
 *   message: "获取用户信息成功",
 *   data: {
 *     id: 1,
 *     address: "0x...",
 *     role: "user"
 *   }
 * }
 */
export function getCurrentUser() {
  return request.get('/api/v1/users/me');
}

export default {
  walletConnect,
  getCurrentUser
};