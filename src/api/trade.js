/**
 * 交易相关 API
 * 负责下单、撤单、历史记录等功能
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
 * 提交订单
 * @param {Object} orderData - 订单数据
 * @param {string} orderData.symbol - 币种符号，如 'BTC'
 * @param {string} orderData.side - 'buy' 或 'sell'
 * @param {number} orderData.price - 订单价格
 * @param {number} orderData.amount - 订单数量
 * @returns {Promise} 返回订单 ID
 */
export function submitOrder(orderData) {
  return mockRequest(() => {
    const { symbol, side, price, amount } = orderData;

    // 参数验证
    if (!symbol || !side || !price || !amount) {
      throw new Error('订单参数不完整');
    }

    if (price <= 0 || amount <= 0) {
      throw new Error('价格和数量必须大于 0');
    }

    const sideUpper = side.toUpperCase();
    const totalCost = amount * price;

    // 读取当前余额和持仓
    const balance = loadFromStorage('userBalance', 10000.00);
    const holdings = loadFromStorage('userHoldings', {
      BTC: 0.15,
      ZEC: 8.50,
      AIC: 3200.00
    });

    // 预扣除资产（模拟冻结）
    if (sideUpper === 'BUY' || side === 'buy') {
      // 买入：检查 USDT 余额是否足够
      if (balance < totalCost) {
        throw new Error('USDT 余额不足');
      }
      
      // 冻结 USDT（扣除余额）
      const newBalance = balance - totalCost;
      saveToStorage('userBalance', newBalance);
    } else if (sideUpper === 'SELL' || side === 'sell') {
      // 卖出：检查持仓数量是否足够
      const currentHolding = holdings[symbol] || 0;
      if (currentHolding < amount) {
        throw new Error(`${symbol} 持仓不足`);
      }
      
      // 冻结持仓（扣除持仓）
      holdings[symbol] = (holdings[symbol] || 0) - amount;
      if (holdings[symbol] <= 0) {
        delete holdings[symbol];
      }
      saveToStorage('userHoldings', holdings);
    } else {
      throw new Error('订单方向无效，必须是 buy 或 sell');
    }

    // 读取订单列表
    const orders = loadFromStorage('userOrders', []);

    // 生成订单对象
    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    
    const orderId = Date.now() + Math.random();
    const newOrder = {
      id: orderId,
      time: timeStr,
      symbol,
      type: sideUpper === 'BUY' || side === 'buy' ? 'BUY' : 'SELL',
      side: side.toLowerCase(),
      price,
      amount,
      status: 'open',
      total: totalCost,
      createdAt: now.toISOString()
    };

    // 添加到订单列表开头
    orders.unshift(newOrder);
    saveToStorage('userOrders', orders);

    return {
      orderId,
      order: newOrder
    };
  });
}

/**
 * 获取当前委托订单
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.symbol - 币种筛选（可选）
 * @param {string} params.side - 方向筛选（可选）
 * @returns {Promise} 返回订单列表
 */
export function getOrders(params = {}) {
  return mockRequest(() => {
    const orders = loadFromStorage('userOrders', []);
    
    // 只返回状态为 'open' 的订单
    let filteredOrders = orders.filter(order => order.status === 'open');

    // 按 symbol 筛选
    if (params.symbol) {
      filteredOrders = filteredOrders.filter(order => 
        order.symbol === params.symbol.toUpperCase()
      );
    }

    // 按 side 筛选
    if (params.side) {
      const sideLower = params.side.toLowerCase();
      filteredOrders = filteredOrders.filter(order => 
        order.side === sideLower || order.type.toLowerCase() === sideLower
      );
    }

    return filteredOrders;
  });
}

/**
 * 取消订单
 * @param {number|string} orderId - 订单 ID
 * @returns {Promise} 返回操作结果
 */
export function cancelOrder(orderId) {
  return mockRequest(() => {
    // 读取订单列表
    const orders = loadFromStorage('userOrders', []);
    
    // 查找订单
    const orderIndex = orders.findIndex(o => o.id === orderId && o.status === 'open');
    
    if (orderIndex === -1) {
      throw new Error('订单不存在或已关闭');
    }

    const order = orders[orderIndex];
    
    // 将订单状态改为已取消
    order.status = 'canceled';
    order.canceledAt = new Date().toISOString();

    // 退还冻结的资金
    const totalCost = order.amount * order.price;

    if (order.type === 'BUY') {
      // 买入订单：退还 USDT
      const balance = loadFromStorage('userBalance', 10000.00);
      const newBalance = balance + totalCost;
      saveToStorage('userBalance', newBalance);
    } else if (order.type === 'SELL') {
      // 卖出订单：退还持仓
      const holdings = loadFromStorage('userHoldings', {});
      if (!holdings[order.symbol]) {
        holdings[order.symbol] = 0;
      }
      holdings[order.symbol] += order.amount;
      saveToStorage('userHoldings', holdings);
    }

    // 更新订单列表
    orders[orderIndex] = order;
    saveToStorage('userOrders', orders);

    return {
      success: true,
      orderId,
      order
    };
  });
}

/**
 * 获取订单历史
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.symbol - 币种筛选（可选）
 * @param {string} params.status - 状态筛选（可选）
 * @returns {Promise} 返回订单历史列表
 */
export function getOrderHistory(params = {}) {
  return mockRequest(() => {
    const orders = loadFromStorage('userOrders', []);
    
    // 返回所有非 open 状态的订单（已成交、已取消等）
    let filteredOrders = orders.filter(order => order.status !== 'open');

    // 按 symbol 筛选
    if (params.symbol) {
      filteredOrders = filteredOrders.filter(order => 
        order.symbol === params.symbol.toUpperCase()
      );
    }

    // 按 status 筛选
    if (params.status) {
      filteredOrders = filteredOrders.filter(order => 
        order.status === params.status.toLowerCase()
      );
    }

    return filteredOrders;
  });
}

/**
 * 获取成交历史
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.symbol - 币种筛选（可选）
 * @returns {Promise} 返回成交记录列表
 */
export function getTradeHistory(params = {}) {
  return mockRequest(() => {
    // 这里可以从 txHistory 中筛选交易类型的记录
    // 或者从订单历史中筛选已成交的订单
    const txHistory = loadFromStorage('txHistory', []);
    
    // 筛选交易类型的记录（如果有的话）
    let trades = txHistory.filter(tx => 
      tx.type === '交易' || tx.type === 'Trade'
    );

    // 按 symbol 筛选
    if (params.symbol) {
      trades = trades.filter(trade => 
        trade.symbol === params.symbol.toUpperCase()
      );
    }

    return trades;
  });
}

/**
 * 获取市场数据（模拟）
 * @param {string} symbol - 币种符号
 * @returns {Promise} 返回市场数据
 */
export function getMarketData(symbol) {
  return mockRequest(() => {
    // 模拟市场数据
    const priceMap = {
      BTC: 92000.00,
      ETH: 3109.04,
      BNB: 585.30,
      SOL: 142.08,
      USDT: 1.00
    };

    const basePrice = priceMap[symbol.toUpperCase()] || 1000.00;
    const change = (Math.random() - 0.5) * 10; // -5% 到 +5% 的随机变化

    return {
      symbol: symbol.toUpperCase(),
      price: basePrice + (basePrice * change / 100),
      change: change,
      high: basePrice * 1.05,
      low: basePrice * 0.95,
      volume: Math.random() * 1000000,
      timestamp: Date.now()
    };
  });
}

export default {
  submitOrder,
  getOrders,
  cancelOrder,
  getOrderHistory,
  getTradeHistory,
  getMarketData
};

