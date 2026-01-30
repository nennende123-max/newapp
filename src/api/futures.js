/**
 * 合约交易相关 API
 * 负责下单、平仓、持仓查询、撤单等功能
 */

import request from '@/utils/request';

/**
 * 创建合约交易订单（开仓：买入做多或卖出做空）
 * @param {Object} params - 订单参数
 * @param {string} params.symbol - 交易对，例如 "BTC/USDT"
 * @param {string} params.side - 交易方向："BUY" (买入/做多) 或 "SELL" (卖出/做空)
 * @param {string} params.type - 订单类型："LIMIT" 或 "MARKET"
 * @param {number} params.price - 交易价格
 * @param {number} params.amount - 交易数量 (张/币)
 * @param {number} params.leverage - 杠杆倍数 (1-125)
 * @returns {Promise} 返回订单结果
 */
export function createFuturesOrder(params) {
  return request.post('/api/v1/futures/order', {
    symbol: params.symbol,
    side: params.side.toUpperCase(),
    type: params.type.toUpperCase(),
    price: parseFloat(params.price) || 0,
    amount: parseFloat(params.amount),
    leverage: parseInt(params.leverage) || 20,
    margin_type: "ISOLATED"
  });
}

/**
 * 获取当前持仓列表
 * @returns {Promise} 返回持仓数据
 */
export function getPositions() {
  console.log('[API] getPositions 调用');
  return request.get('/api/v1/futures/positions').then(response => {
    console.log('[API] getPositions 响应:', response);
    return response;
  }).catch(error => {
    console.error('[API] getPositions 错误:', error);
    throw error;
  });
}

/**
 * 平仓（市价全平或部分平仓）
 * @param {Object} params - 参数
 * @param {string} params.symbol - 交易对
 * @param {number} params.amount - 平仓数量
 * @returns {Promise} 返回操作结果
 */
export function closePosition(params) {
  return request.post('/api/v1/futures/close', {
    symbol: params.symbol,
    amount: parseFloat(params.amount),
    type: "MARKET"
  });
}

/**
 * 获取当前委托订单（挂单）
 * @param {Object} params - 查询参数（可选）
 * @param {string} params.status - 订单状态筛选：'NEW' 或 'OPEN' 获取当前委托，'FILLED' 获取已成交，'CANCELLED' 获取已撤销
 * @returns {Promise} 返回订单列表
 */
export function getFuturesOrders(params = {}) {
  return request.get('/api/v1/futures/orders', { params });
}

/**
 * 取消合约挂单
 * @param {string} orderId - 订单 ID
 * @returns {Promise} 返回操作结果
 */
export function cancelFuturesOrder(orderId) {
  return request.post('/api/v1/futures/order/cancel', {
    order_id: orderId
  });
}

/**
 * 设置持仓的止盈止损价格
 * @param {Object} params - 参数
 * @param {string} params.symbol - 交易对，例如 "BTC/USDT"
 * @param {number|null} params.takeProfitPrice - 止盈价格（可选，传0或null表示清除）
 * @param {number|null} params.stopLossPrice - 止损价格（可选，传0或null表示清除）
 * @returns {Promise} 返回操作结果
 */
export function setPositionTPSL(params) {
  console.log('[API] setPositionTPSL 调用:', {
    symbol: params.symbol,
    take_profit: params.take_profit,
    stop_loss: params.stop_loss
  });
  
  return request.post('/api/v1/futures/position/set-tpsl', {
    symbol: params.symbol,
    take_profit_price: params.take_profit || null,
    stop_loss_price: params.stop_loss || null
  }).then(response => {
    console.log('[API] setPositionTPSL 响应:', response);
    return response;
  }).catch(error => {
    console.error('[API] setPositionTPSL 错误:', error);
    throw error;
  });
}

export default {
  createFuturesOrder,
  getPositions,
  closePosition,
  getFuturesOrders,
  cancelFuturesOrder,
  setPositionTPSL
};
