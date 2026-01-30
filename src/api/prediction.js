/**
 * 预测市场相关 API
 * 负责预测事件、下注等功能
 * 所有数据操作直接读写 localStorage，不依赖 Pinia Store
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
 * 生成模拟预测市场数据
 */
const generateMockMarkets = () => {
  const categories = ['Crypto', 'Politics', 'Sports', 'Macro'];
  const cryptoIcons = [
    'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
    'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
    'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png',
    'https://assets.coingecko.com/coins/images/4128/large/solana.png'
  ];

  const markets = [
    {
      id: 1,
      category: 'Crypto',
      titleKey: 'prediction.btc_100k',
      volume: '$2.4m',
      endDate: 'Jan 31, 2026',
      image: cryptoIcons[0],
      outcomes: [
        { side: 'YES', price: 0.62, color: '#0ECB81' },
        { side: 'NO', price: 0.38, color: '#F6465D' }
      ],
      comments: 124
    },
    {
      id: 2,
      category: 'Politics',
      titleKey: 'prediction.trump_crypto',
      volume: '$1.8m',
      endDate: 'Feb 15, 2026',
      image: 'https://via.placeholder.com/48x48/1C1C1E/FFFFFF?text=P',
      outcomes: [
        { side: 'YES', price: 0.12, color: '#0ECB81' },
        { side: 'NO', price: 0.88, color: '#F6465D' }
      ],
      comments: 89
    },
    {
      id: 3,
      category: 'Crypto',
      titleKey: 'prediction.eth_5k',
      volume: '$1.2m',
      endDate: 'Mar 31, 2026',
      image: cryptoIcons[1],
      outcomes: [
        { side: 'YES', price: 0.58, color: '#0ECB81' },
        { side: 'NO', price: 0.42, color: '#F6465D' }
      ],
      comments: 92
    },
    {
      id: 4,
      category: 'Macro',
      titleKey: 'prediction.fed_rates',
      volume: '$950k',
      endDate: 'Mar 1, 2026',
      image: 'https://via.placeholder.com/48x48/1C1C1E/FFFFFF?text=M',
      outcomes: [
        { side: 'YES', price: 0.45, color: '#0ECB81' },
        { side: 'NO', price: 0.55, color: '#F6465D' }
      ],
      comments: 67
    },
    {
      id: 5,
      category: 'Sports',
      titleKey: 'prediction.lakers_championship',
      volume: '$680k',
      endDate: 'Jun 30, 2026',
      image: 'https://via.placeholder.com/48x48/1C1C1E/FFFFFF?text=L',
      outcomes: [
        { side: 'YES', price: 0.28, color: '#0ECB81' },
        { side: 'NO', price: 0.72, color: '#F6465D' }
      ],
      comments: 156
    },
    {
      id: 6,
      category: 'Crypto',
      titleKey: 'prediction.eth_flip_btc',
      volume: '$1.5m',
      endDate: 'Dec 31, 2026',
      image: cryptoIcons[1],
      outcomes: [
        { side: 'YES', price: 0.35, color: '#0ECB81' },
        { side: 'NO', price: 0.65, color: '#F6465D' }
      ],
      comments: 203
    },
    {
      id: 7,
      category: 'Macro',
      titleKey: 'prediction.inflation_2pct',
      volume: '$820k',
      endDate: 'Dec 31, 2026',
      image: 'https://via.placeholder.com/48x48/1C1C1E/FFFFFF?text=I',
      outcomes: [
        { side: 'YES', price: 0.52, color: '#0ECB81' },
        { side: 'NO', price: 0.48, color: '#F6465D' }
      ],
      comments: 78
    },
    {
      id: 8,
      category: 'Crypto',
      titleKey: 'prediction.solana_200',
      volume: '$1.1m',
      endDate: 'Jun 30, 2026',
      image: cryptoIcons[3],
      outcomes: [
        { side: 'YES', price: 0.41, color: '#0ECB81' },
        { side: 'NO', price: 0.59, color: '#F6465D' }
      ],
      comments: 145
    }
  ];

  return markets;
};

/**
 * 获取预测市场列表
 * @param {string} category - 分类筛选（可选），'All' 返回全部
 * @returns {Promise} 返回市场列表
 */
export function getMarkets(category = 'All') {
  // 使用 Promise.resolve 保持与 mockRequest 相同的返回格式
  // TODO: 如果后端有预测市场 API，替换为真实 API 调用
  return Promise.resolve({
    code: 200,
    msg: 'success',
    data: (() => {
      const allMarkets = generateMockMarkets();
      
      if (category === 'All' || !category) {
        return allMarkets;
      }
      
      return allMarkets.filter(market => market.category === category);
    })()
  });
}

/**
 * 下注预测
 * @param {number} eventId - 事件 ID
 * @param {string} side - 'YES' 或 'NO'
 * @param {number} amount - USDT 金额
 * @returns {Promise} 返回订单结果
 */
export function placePredictionBet(eventId, side, amount) {
  // 使用 Promise.resolve 保持与 mockRequest 相同的返回格式
  // TODO: 如果后端有预测市场 API，替换为真实 API 调用
  try {
    if (!eventId || !side || !amount || amount <= 0) {
      return Promise.reject({
        code: 500,
        msg: '参数无效'
      });
    }

    if (side !== 'YES' && side !== 'NO') {
      return Promise.reject({
        code: 500,
        msg: '下注方向必须是 YES 或 NO'
      });
    }

    // 读取当前余额
    const balance = loadFromStorage('userBalance', 10000.00);
    
    if (balance < amount) {
      return Promise.reject({
        code: 500,
        msg: 'USDT 余额不足'
      });
    }

    // 扣除余额
    const newBalance = balance - amount;
    saveToStorage('userBalance', newBalance);

    // 获取市场信息（用于计算）
    const markets = generateMockMarkets();
    const market = markets.find(m => m.id === eventId);
    
    if (!market) {
      return Promise.reject({
        code: 500,
        msg: '事件不存在'
      });
    }

    const outcome = market.outcomes.find(o => o.side === side);
    if (!outcome) {
      return Promise.reject({
        code: 500,
        msg: '下注方向无效'
      });
    }

    // 计算预期收益
    // 如果事件结果为 YES，每份 YES 代币价值 $1，否则为 $0
    // 用户花费 amount USDT，以 price 的价格买入，可以获得 amount / price 份代币
    const shares = amount / outcome.price;
    const maxReturn = shares * 1.0; // 如果预测正确，每份代币价值 $1
    const estReturn = maxReturn - amount; // 预期收益 = 最大收益 - 投入
    const estReturnPercent = (estReturn / amount) * 100; // 预期收益率

    // 生成订单记录
    const order = {
      id: Date.now() + Math.random(),
      eventId,
      eventTitleKey: market.titleKey, // 保存翻译键而不是硬编码文本
      side,
      amount,
      price: outcome.price,
      shares,
      estReturn,
      estReturnPercent,
      createdAt: new Date().toISOString(),
      status: 'open'
    };

    // 保存订单到 localStorage（可以扩展为独立的预测订单存储）
    const predictionOrders = loadFromStorage('predictionOrders', []);
    predictionOrders.unshift(order);
    saveToStorage('predictionOrders', predictionOrders);

    return Promise.resolve({
      code: 200,
      msg: 'success',
      data: {
        orderId: order.id,
        order,
        newBalance
      }
    });
  } catch (error) {
    return Promise.reject({
      code: 500,
      msg: error.message || '下注失败'
    });
  }
}

/**
 * 获取用户的预测订单
 * @returns {Promise} 返回订单列表
 */
export function getPredictionOrders() {
  // 使用 Promise.resolve 保持与 mockRequest 相同的返回格式
  // TODO: 如果后端有预测市场 API，替换为真实 API 调用
  return Promise.resolve({
    code: 200,
    msg: 'success',
    data: loadFromStorage('predictionOrders', [])
  });
}

export default {
  getMarkets,
  placePredictionBet,
  getPredictionOrders
};