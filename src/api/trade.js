/**
 * 交易相关 API
 * 负责下单、撤单、历史记录等功能
 * 
 * 注意：现在使用真实的后端 API，不再使用 Mock 数据
 */

import request from '@/utils/request';
import { isProdMode } from '@/config/appMode';

const LOCAL_ORDERS_KEY = 'userOrders';

const shouldUseLocalTradeApi = () => {
  return import.meta.env.DEV || !isProdMode() || localStorage.getItem('TRUTHFI_FRONTEND_ONLY') === 'true';
};

const createApiResponse = (data, message = 'success') => ({
  data: {
    code: 200,
    message,
    data
  }
});

const normalizeOrderStatus = (status) => String(status || 'NEW').toUpperCase();

const normalizeSymbol = (symbol = 'BTC/USDT') => {
  const value = String(symbol || 'BTC/USDT').toUpperCase();
  return value.includes('/') ? value : `${value}/USDT`;
};

const getLocalOrders = () => {
  const orders = loadFromStorage(LOCAL_ORDERS_KEY, []);
  return Array.isArray(orders) ? orders : [];
};

const saveLocalOrders = (orders) => {
  saveToStorage(LOCAL_ORDERS_KEY, Array.isArray(orders) ? orders : []);
};

const filterLocalOrders = (orders, params = {}) => {
  const status = params.status ? normalizeOrderStatus(params.status) : '';

  if (!status) return orders;

  if (status === 'OPEN' || status === 'NEW') {
    return orders.filter(order => ['NEW', 'OPEN', 'PENDING'].includes(normalizeOrderStatus(order.status)));
  }

  return orders.filter(order => normalizeOrderStatus(order.status) === status);
};

const buildLocalOrder = (params) => {
  const now = Date.now();
  const amount = Number(params.amount || params.quantity || 0);
  const price = Number(params.price || 0);
  const symbol = normalizeSymbol(params.symbol);
  const type = String(params.type || 'LIMIT').toUpperCase();
  const side = String(params.side || 'BUY').toUpperCase();

  return {
    order_id: `local-${now}-${Math.random().toString(36).slice(2, 8)}`,
    symbol,
    side,
    type,
    price,
    amount,
    quantity: amount,
    status: 'NEW',
    timestamp: now,
    create_time: now,
    use_beat_discount: Boolean(params.use_beat_discount)
  };
};

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
 * 创建交易订单（真实后端 API）
 * @param {Object} params - 订单参数
 * @param {string} params.symbol - 交易对，例如 "BTC/USDT"
 * @param {string} params.side - 交易方向："BUY" 或 "SELL"
 * @param {string} params.type - 订单类型："LIMIT" 或 "MARKET"
 * @param {number} params.price - 交易价格（限价单必填，市价单可传当前市场参考价）
 * @param {number} params.amount - 交易数量
 * @param {boolean} params.use_beat_discount - 是否使用 BEAT 抵扣手续费（可选，默认 false）
 * @returns {Promise} 返回订单结果
 */
export function createOrder(params) {
  // 参数验证
  if (!params.symbol || !params.side || !params.type || !params.amount) {
    return Promise.reject(new Error('订单参数不完整'));
  }

  if (params.amount <= 0) {
    return Promise.reject(new Error('交易数量必须大于 0'));
  }

  if (params.type === 'LIMIT' && (!params.price || params.price <= 0)) {
    return Promise.reject(new Error('限价单必须提供有效的价格'));
  }

  // POST 请求到 /api/v1/trade/order
  // request 中已配置 baseURL: 'http://127.0.0.1:8000'
  // 实际请求的 URL 是：http://127.0.0.1:8000/api/v1/trade/order
  if (shouldUseLocalTradeApi()) {
    const order = buildLocalOrder(params);
    const orders = getLocalOrders();
    saveLocalOrders([order, ...orders]);
    return Promise.resolve(createApiResponse(order, 'Order created locally'));
  }

  return request.post('/api/v1/trade/order', {
    symbol: params.symbol,
    side: params.side.toUpperCase(),
    type: params.type.toUpperCase(),
    price: params.price || 0,
    amount: params.amount,
    use_beat_discount: params.use_beat_discount || false
  });
}

/**
 * 提交订单（兼容旧接口，内部调用 createOrder）
 * @deprecated 请使用 createOrder
 */
export function submitOrder(orderData) {
  // 兼容旧接口格式，转换为新格式
  const symbol = orderData.symbol.includes('/') 
    ? orderData.symbol 
    : `${orderData.symbol}/USDT`;
  
  return createOrder({
    symbol: symbol,
    side: orderData.side,
    type: orderData.type || 'LIMIT',
    price: orderData.price,
    amount: orderData.amount
  });
}

/**
 * 获取当前委托订单
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.status - 订单状态筛选：'NEW' 或 'OPEN' 获取当前委托，'FILLED' 获取已成交，'CANCELLED' 获取已撤销
 * @returns {Promise} 返回订单列表
 */
export function getOrders(params = {}) {
  if (shouldUseLocalTradeApi()) {
    const orders = filterLocalOrders(getLocalOrders(), params);
    return Promise.resolve(createApiResponse(orders, 'Orders loaded locally'));
  }

  return request.get('/api/v1/trade/orders', { params });
}

/**
 * 取消订单
 * @param {string} orderId - 订单 ID
 * @returns {Promise} 返回操作结果
 */
export function cancelOrder(orderId) {
  if (shouldUseLocalTradeApi()) {
    const orders = getLocalOrders();
    let cancelledOrder = null;
    const nextOrders = orders.map(order => {
      if (String(order.order_id) !== String(orderId)) return order;
      cancelledOrder = {
        ...order,
        status: 'CANCELLED',
        cancelled_at: Date.now()
      };
      return cancelledOrder;
    });

    saveLocalOrders(nextOrders);
    return Promise.resolve(createApiResponse(cancelledOrder || { order_id: orderId }, 'Order cancelled locally'));
  }

  return request.post('/api/v1/trade/order/cancel', {
    order_id: orderId
  });
}

/**
 * 获取订单历史
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.symbol - 币种筛选（可选）
 * @param {string} params.status - 状态筛选（可选）
 * @returns {Promise} 返回订单历史列表
 * 
 * 注意：后端暂时还没有订单历史接口，暂时返回空数组防止报错
 * TODO: 当后端实现 /api/v1/trade/orders/history 接口后，改为真实 API 调用
 */
export function getOrderHistory(params = {}) {
  // 临时方案：防止接口 404 导致报错
  return Promise.resolve({
    data: {
      code: 200,
      message: '获取订单历史成功',
      data: []
    }
  });
  
  // TODO: 当后端实现订单历史接口后，使用以下代码：
  // return request.get('/api/v1/trade/orders/history', { params });
}

/**
 * 获取成交历史
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.symbol - 币种筛选（可选）
 * @returns {Promise} 返回成交记录列表
 * 
 * 注意：后端暂时还没有成交历史接口，暂时返回空数组防止报错
 * TODO: 当后端实现 /api/v1/trade/trades/history 接口后，改为真实 API 调用
 */
export function getTradeHistory(params = {}) {
  // 临时方案：防止接口 404 导致报错
  return Promise.resolve({
    data: {
      code: 200,
      message: '获取成交历史成功',
      data: []
    }
  });
  
  // TODO: 当后端实现成交历史接口后，使用以下代码：
  // return request.get('/api/v1/trade/trades/history', { params });
}

/**
 * 获取市场数据（模拟）
 * @param {string} symbol - 币种符号
 * @returns {Promise} 返回市场数据
 * 
 * 注意：此函数暂时返回模拟数据，不依赖后端接口
 * TODO: 当后端实现市场数据接口后，改为真实 API 调用
 */
export function getMarketData(symbol) {
  // 临时方案：返回模拟市场数据（不依赖后端）
  const priceMap = {
    BTC: 92000.00,
    ETH: 3109.04,
    BNB: 585.30,
    SOL: 142.08,
    USDT: 1.00
  };

  const basePrice = priceMap[symbol.toUpperCase()] || 1000.00;
  const change = (Math.random() - 0.5) * 10; // -5% 到 +5% 的随机变化

  return Promise.resolve({
    data: {
      code: 200,
      message: '获取市场数据成功',
      data: {
        symbol: symbol.toUpperCase(),
        price: basePrice + (basePrice * change / 100),
        change: change,
        high: basePrice * 1.05,
        low: basePrice * 0.95,
        volume: Math.random() * 1000000,
        timestamp: Date.now()
      }
    }
  });
  
  // TODO: 当后端实现市场数据接口后，使用以下代码：
  // return request.get(`/api/v1/market/ticker/${symbol}`);
}

export default {
  submitOrder,
  getOrders,
  cancelOrder,
  getOrderHistory,
  getTradeHistory,
  getMarketData
};
