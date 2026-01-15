/**
 * 钱包相关 API
 * 负责资产、充值、提现等功能
 * 所有数据操作直接读写 localStorage，不依赖 Pinia Store
 */

import { mockRequest } from './mockRequest';

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
 * 获取资产列表
 * 返回 { balance: USDT余额, holdings: 持仓对象 }
 */
export function getAssets() {
  return mockRequest(() => {
    const balance = loadFromStorage('userBalance', 10000.00);
    const holdings = loadFromStorage('userHoldings', {
      BTC: 0.15,
      ZEC: 8.50,
      AIC: 3200.00
    });

    return {
      balance,
      holdings
    };
  });
}

/**
 * 充值
 * @param {number} amount - 充值金额
 * @returns {Promise} 返回最新余额
 */
export function deposit(amount) {
  return mockRequest(() => {
    if (!amount || amount <= 0) {
      throw new Error('充值金额必须大于 0');
    }

    // 读取当前余额
    const currentBalance = loadFromStorage('userBalance', 10000.00);
    
    // 更新余额
    const newBalance = currentBalance + amount;
    saveToStorage('userBalance', newBalance);

    // 读取交易历史
    const txHistory = loadFromStorage('txHistory', []);
    
    // 生成交易记录
    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    
    const transaction = {
      id: Date.now() + Math.random(),
      time: `${dateStr} ${timeStr}`,
      type: '充值',
      amount: amount,
      status: '成功',
      tx_id: '0x' + Array.from({ length: 64 }, () => 
        Math.floor(Math.random() * 16).toString(16)
      ).join(''),
      chain_name: 'TRC20'
    };

    // 添加到历史记录开头
    txHistory.unshift(transaction);
    saveToStorage('txHistory', txHistory);

    return {
      balance: newBalance,
      transaction
    };
  });
}

/**
 * 提现
 * @param {number} amount - 提现金额
 * @returns {Promise} 返回最新余额
 */
export function withdraw(amount) {
  return mockRequest(() => {
    if (!amount || amount <= 0) {
      throw new Error('提现金额必须大于 0');
    }

    // 读取当前余额
    const currentBalance = loadFromStorage('userBalance', 10000.00);
    
    // 检查余额是否足够
    if (currentBalance < amount) {
      throw new Error('余额不足');
    }

    // 扣除余额
    const newBalance = currentBalance - amount;
    saveToStorage('userBalance', newBalance);

    // 读取交易历史
    const txHistory = loadFromStorage('txHistory', []);
    
    // 生成交易记录
    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    
    const transaction = {
      id: Date.now() + Math.random(),
      time: `${dateStr} ${timeStr}`,
      type: '提现',
      amount: -amount, // 负数表示支出
      status: '成功',
      tx_id: '0x' + Array.from({ length: 64 }, () => 
        Math.floor(Math.random() * 16).toString(16)
      ).join(''),
      chain_name: 'TRC20'
    };

    // 添加到历史记录开头
    txHistory.unshift(transaction);
    saveToStorage('txHistory', txHistory);

    return {
      balance: newBalance,
      transaction
    };
  });
}

/**
 * 获取资产详情
 * @param {string} symbol - 币种符号
 */
export function getAssetDetail(symbol) {
  return mockRequest(() => {
    const holdings = loadFromStorage('userHoldings', {});
    return {
      symbol,
      balance: holdings[symbol] || 0
    };
  });
}

/**
 * 获取充值历史
 */
export function getDepositHistory() {
  return mockRequest(() => {
    const txHistory = loadFromStorage('txHistory', []);
    return txHistory.filter(tx => tx.type === '充值');
  });
}

/**
 * 获取提现历史
 */
export function getWithdrawHistory() {
  return mockRequest(() => {
    const txHistory = loadFromStorage('txHistory', []);
    return txHistory.filter(tx => tx.type === '提现');
  });
}

export default {
  getAssets,
  deposit,
  withdraw,
  getAssetDetail,
  getDepositHistory,
  getWithdrawHistory
};

