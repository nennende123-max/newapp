/**
 * 钱包相关 API
 * 负责资产、充值、提现等功能
 * 
 * 注意：现在使用真实的后端 API，不再使用 Mock 数据
 */

import request from '@/utils/request';

/**
 * 从 localStorage 读取数据
 */
const loadFromStorage = (key, defaultValue) => {
  try {
    const item = localStorage.getItem(key);
    if (item !== null) {
      return JSON.parse(item);
    }
  } catch (error) {
    console.error(`Error loading ${key} from localStorage:`, error);
  }
  return defaultValue;
};

/**
 * 保存数据到 localStorage
 */
const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error saving ${key} to localStorage:`, error);
  }
};

/**
 * 获取资产余额
 * 从后端 API 获取当前用户的资产余额
 * 
 * @returns {Promise} 返回资产余额
 * 
 * 返回格式：
 * {
 *   code: 200,
 *   message: "获取余额成功",
 *   data: {
 *     USDT: 50000.0,
 *     BTC: 0.0,
 *     BEAT: 0.0
 *   }
 * }
 */
export function getBalance() {
  return request.get('/api/v1/assets/balance');
}

/**
 * 获取资产列表（兼容旧代码）
 * 返回格式：{ code: 200, data: { balance: USDT余额, holdings: 持仓对象 } }
 */
export function getAssets() {
  return getBalance().then(response => {
    // 适配后端返回格式：{ code: 200, data: { USDT: 50000, BTC: 0, BEAT: 0 } }
    const assets = response.data.data || {};
    return {
      code: 200,
      data: {
        balance: assets.USDT || 0,
        holdings: {
          BTC: assets.BTC || 0,
          BEAT: assets.BEAT || 0
        }
      }
    };
  });
}

/**
 * 充值
 * 调用后端 API 进行充值操作
 * 
 * @param {Object} data - 充值数据对象
 * @param {number} data.amount - 充值金额（必填）
 * @param {string} data.currency - 币种，默认为 'USDT'
 * @returns {Promise} 返回最新余额
 * 
 * 使用示例：
 * deposit({ amount: 1000, currency: 'USDT' })
 * 
 * 返回格式：
 * {
 *   code: 200,
 *   message: "充值成功",
 *   data: {
 *     USDT: 51000.0,
 *     BTC: 0.0,
 *     BEAT: 0.0
 *   }
 * }
 */
export function deposit(data) {
  // 参数验证
  if (!data || typeof data !== 'object') {
    return Promise.reject(new Error('参数必须是一个对象'));
  }
  
  const { amount, currency = 'USDT' } = data;
  
  if (!amount || amount <= 0) {
    return Promise.reject(new Error('充值金额必须大于 0'));
  }

  // POST 请求到 /api/v1/assets/deposit
  // request 中已配置 baseURL: 'http://127.0.0.1:8000'
  // 实际请求的 URL 是：http://127.0.0.1:8000/api/v1/assets/deposit
  return request.post('/api/v1/assets/deposit', {
    amount: amount,
    currency: currency
  });
}

/**
 * 提现
 * 调用后端 API 进行提现操作
 * 
 * @param {Object} data - 提现数据对象
 * @param {number} data.amount - 提现金额（必填）
 * @param {string} data.currency - 币种，默认为 'USDT'
 * @returns {Promise} 返回最新余额
 * 
 * 使用示例：
 * withdraw({ amount: 1000, currency: 'USDT' })
 * 
 * 返回格式：
 * {
 *   code: 200,
 *   message: "提现成功",
 *   data: {
 *     USDT: 49000.0,
 *     BTC: 0.0,
 *     BEAT: 0.0
 *   }
 * }
 */
export function withdraw(data) {
  // 参数验证
  if (!data || typeof data !== 'object') {
    return Promise.reject(new Error('参数必须是一个对象'));
  }
  
  const { amount, currency = 'USDT' } = data;
  
  if (!amount || amount <= 0) {
    return Promise.reject(new Error('提现金额必须大于 0'));
  }

  // POST 请求到 /api/v1/assets/withdraw
  // request 中已配置 baseURL: 'http://127.0.0.1:8000'
  // 实际请求的 URL 是：http://127.0.0.1:8000/api/v1/assets/withdraw
  return request.post('/api/v1/assets/withdraw', {
    amount: amount,
    currency: currency
  });
}

/**
 * 获取资产详情
 * @param {string} symbol - 币种符号
 */
export function getAssetDetail(symbol) {
  // 使用 Promise.resolve 保持与 mockRequest 相同的返回格式
  // TODO: 如果后端有资产详情 API，替换为真实 API 调用
  return Promise.resolve({
    code: 200,
    msg: 'success',
    data: (() => {
      const holdings = loadFromStorage('userHoldings', {});
      return {
        symbol,
        balance: holdings[symbol] || 0
      };
    })()
  });
}

/**
 * 获取充值历史
 */
export function getDepositHistory() {
  // 使用 Promise.resolve 保持与 mockRequest 相同的返回格式
  // TODO: 如果后端有充值历史 API，替换为真实 API 调用
  return Promise.resolve({
    code: 200,
    msg: 'success',
    data: (() => {
      const txHistory = loadFromStorage('txHistory', []);
      return txHistory.filter(tx => tx.type === '充值');
    })()
  });
}

/**
 * 获取提现历史
 */
export function getWithdrawHistory() {
  // 使用 Promise.resolve 保持与 mockRequest 相同的返回格式
  // TODO: 如果后端有提现历史 API，替换为真实 API 调用
  return Promise.resolve({
    code: 200,
    msg: 'success',
    data: (() => {
      const txHistory = loadFromStorage('txHistory', []);
      return txHistory.filter(tx => tx.type === '提现');
    })()
  });
}

export default {
  getBalance,
  getAssets,
  deposit,
  withdraw,
  getAssetDetail,
  getDepositHistory,
  getWithdrawHistory
};