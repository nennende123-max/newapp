/**
 * TradingView 自定义 Datafeed
 * 对接后端 K 线 API 和 WebSocket
 */

import request from './request';

// API 基础地址
const API_BASE = 'http://127.0.0.1:8000';
const WS_BASE = 'ws://127.0.0.1:8000';

/**
 * 将 TradingView 分辨率转换为后端 API 格式
 */
function resolutionToInterval(resolution) {
  const map = {
    '1': '1m',
    '3': '3m',
    '5': '5m',
    '15': '15m',
    '30': '30m',
    '60': '1h',
    '120': '2h',
    '240': '4h',
    '360': '6h',
    '480': '8h',
    '720': '12h',
    'D': '1d',
    '1D': '1d',
    'W': '1w',
    '1W': '1w',
    'M': '1M',
    '1M': '1M'
  };
  return map[resolution] || '1m';
}

/**
 * 将后端时间间隔转换为 TradingView 分辨率
 */
function intervalToResolution(interval) {
  const map = {
    '1m': '1',
    '3m': '3',
    '5m': '5',
    '15m': '15',
    '30m': '30',
    '1h': '60',
    '2h': '120',
    '4h': '240',
    '6h': '360',
    '8h': '480',
    '12h': '720',
    '1d': 'D',
    '1w': 'W',
    '1M': 'M'
  };
  return map[interval] || '1';
}

/**
 * 创建自定义 Datafeed
 */
export function createDatafeed() {
  // WebSocket 连接管理
  let wsConnection = null;
  let currentSymbol = null;
  let currentResolution = null;
  let onRealtimeCallback = null;
  let reconnectTimer = null;
  let isReconnecting = false;
  
  // 保存回调函数的引用（用于在 WebSocket 消息处理中调用）
  const callbacks = new Map();
  
  // 保存轮询定时器的引用（用于在取消订阅时清理）
  const pricePollIntervals = new Map();
  
  // 保存 bar 轮询定时器
  let barTimer = null;

  /**
   * 连接 WebSocket
   */
  function connectWebSocket(symbol, resolution) {
    // 如果已有连接且参数相同，不重复连接
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN && 
        currentSymbol === symbol && currentResolution === resolution) {
      return;
    }

    // 关闭旧连接
    if (wsConnection) {
      wsConnection.close();
      wsConnection = null;
    }

    currentSymbol = symbol;
    currentResolution = resolution;

    const wsUrl = `${WS_BASE}/api/v1/market/ws/kline`;
    console.log('[Datafeed] 连接 WebSocket:', wsUrl);

    try {
      wsConnection = new WebSocket(wsUrl);

      wsConnection.onopen = () => {
        console.log('[Datafeed] WebSocket 连接成功');
        isReconnecting = false;
        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }
      };

      wsConnection.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'kline') {
            const kline = message.data;
            
            // 检查是否是当前订阅的交易对和时间周期
            const klineResolution = intervalToResolution(kline.interval);
            const callbackKey = `${kline.symbol}_${klineResolution}`;
            
            // 查找匹配的回调函数
            const callback = callbacks.get(callbackKey);
            if (callback) {
              // 转换为 TradingView 格式
              const bar = {
                time: kline.timestamp,
                open: kline.open,
                high: kline.high,
                low: kline.low,
                close: kline.close,
                volume: kline.volume
              };

              // 调用回调更新图表
              callback(bar);
            }
          } else if (message.type === 'connected') {
            console.log('[Datafeed] WebSocket 已连接:', message.message);
          } else if (message.type === 'pong') {
            // 心跳响应
          }
        } catch (error) {
          console.error('[Datafeed] 解析 WebSocket 消息失败:', error);
        }
      };

      wsConnection.onerror = (error) => {
        console.error('[Datafeed] WebSocket 错误:', error);
      };

      wsConnection.onclose = () => {
        console.warn('[Datafeed] WebSocket 连接已关闭');
        wsConnection = null;
        
        // 自动重连（如果还在订阅状态）
        if (currentSymbol && currentResolution && !isReconnecting) {
          isReconnecting = true;
          reconnectTimer = setTimeout(() => {
            console.log('[Datafeed] 尝试重连 WebSocket...');
            connectWebSocket(currentSymbol, currentResolution);
          }, 3000);
        }
      };
    } catch (error) {
      console.error('[Datafeed] 创建 WebSocket 连接失败:', error);
    }
  }

  /**
   * 关闭 WebSocket
   */
  function disconnectWebSocket(subscribeUID) {
    // 移除回调
    if (subscribeUID) {
      callbacks.delete(subscribeUID);
    }
    
    // 如果没有其他订阅，关闭连接
    if (callbacks.size === 0) {
      if (wsConnection) {
        wsConnection.close();
        wsConnection = null;
      }
      currentSymbol = null;
      currentResolution = null;
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      isReconnecting = false;
    }
  }

  // 保存配置数据，供 resolveSymbol 使用
  let configurationData = {
    supported_resolutions: ['1', '5', '15', '60', '240', 'D']
  };

  return {
    /**
     * onReady: 初始化 Datafeed
     */
    onReady(callback) {
      console.log('[Datafeed] onReady 被调用');
      
      setTimeout(() => {
        configurationData = {
          supported_resolutions: ['1', '5', '15', '60', '240', 'D'],
          supports_group_request: false,
          supports_marks: false,
          supports_search: false,
          supports_timescale_marks: false
        };
        callback(configurationData);
      }, 0);
    },

    /**
     * resolveSymbol: 解析交易对信息
     */
    resolveSymbol(symbolName, onSymbolResolvedCallback, onResolveErrorCallback) {
      console.log('[Datafeed] resolveSymbol:', symbolName);

      // 强制 symbol 为 BTCUSDT
      const symbolInfo = {
        name: symbolName || 'BTCUSDT',
        description: 'Bitcoin / USDT',
        type: 'crypto',
        session: '24x7',
        timezone: 'Etc/UTC',
        ticker: (symbolName || 'BTCUSDT').toUpperCase().replace('/', ''),
        minmov: 1,
        pricescale: 100,
        has_intraday: true,
        intraday_multipliers: ['1', '5', '15', '30', '60'],
        supported_resolutions: configurationData.supported_resolutions || ['1', '5', '15', '60', '240', 'D'],
        volume_precision: 8,
        data_status: 'streaming'
      };

      onSymbolResolvedCallback(symbolInfo);
    },

    /**
     * getBars: 获取历史 K 线数据
     */
    getBars(symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) {
      // 时间间隔映射
      const intervalMap = {
        '1': '1m',
        '3': '3m',
        '5': '5m',
        '15': '15m',
        '30': '30m',
        '60': '1h',
        '120': '2h',
        '240': '4h',
        '360': '6h',
        '480': '8h',
        '720': '12h',
        'D': '1d',
        '1D': '1d',
        'W': '1w',
        '1W': '1w',
        'M': '1M',
        '1M': '1M'
      };

      const interval = intervalMap[resolution] || '1m';
      const symbol = 'BTCUSDT';  // 强制 symbol 为 BTCUSDT
      console.log(`获取 K 线: symbol=${symbol}, interval=${interval}, from=${periodParams.from}, to=${periodParams.to}`);

      request.get('/api/v1/market/klines', {
        params: { symbol, interval, limit: 1000 }
      }).then(response => {
        const bars = response.data.map(k => ({
          time: k.time * 1000,  // Binance 时间戳为 ms，确保乘 1000（如果后端返回秒级时间戳）
          open: parseFloat(k.open),
          high: parseFloat(k.high),
          low: parseFloat(k.low),
          close: parseFloat(k.close),
          volume: parseFloat(k.volume)
        }));
        console.log('K 线数据返回:', bars.slice(0, 5));  // 日志前 5 条数据以验证
        onHistoryCallback(bars, { noData: false });
      }).catch(error => {
        console.error('K 线获取失败:', error);
        onErrorCallback('无法加载 Binance K 线数据');
      });
    },

    /**
     * subscribeBars: 订阅实时 K 线数据
     */
    subscribeBars(symbolInfo, resolution, onRealtimeCallback, subscriberUID, onResetCacheNeededCallback) {
      console.log('[Datafeed] subscribeBars:', {
        symbol: symbolInfo.name,
        resolution,
        subscriberUID
      });

      // 保存回调函数（使用 subscriberUID 作为 key）
      callbacks.set(`${symbolInfo.name}_${resolution}`, onRealtimeCallback);

      // 连接 WebSocket（如果可用）
      connectWebSocket(symbolInfo.name, resolution);

      // 时间间隔映射
      const intervalMap = {
        '1': '1m',
        '3': '3m',
        '5': '5m',
        '15': '15m',
        '30': '30m',
        '60': '1h',
        '120': '2h',
        '240': '4h',
        '360': '6h',
        '480': '8h',
        '720': '12h',
        'D': '1d',
        '1D': '1d',
        'W': '1w',
        '1W': '1w',
        'M': '1M',
        '1M': '1M'
      };

      // 添加轮询以实时更新（每10秒）
      barTimer = setInterval(() => {
        request.get('/api/v1/market/klines', {
          params: {
            symbol: 'BTCUSDT',
            interval: intervalMap[resolution] || '1m',
            limit: 1
          }
        })
        .then(res => {
          if (res.data && Array.isArray(res.data) && res.data.length > 0) {
            const latestBar = {
              time: res.data[0].time * 1000,  // Binance 时间戳为 ms，确保乘 1000
              open: parseFloat(res.data[0].open),
              high: parseFloat(res.data[0].high),
              low: parseFloat(res.data[0].low),
              close: parseFloat(res.data[0].close),
              volume: parseFloat(res.data[0].volume)
            };
            onRealtimeCallback(latestBar);
          }
        })
        .catch(err => console.error('实时 K 线更新失败:', err));
      }, 10000);  // 每 10 秒更新一次

      // 保存轮询定时器，以便在取消订阅时清理
      pricePollIntervals.set(subscriberUID, barTimer);
    },

    /**
     * unsubscribeBars: 取消订阅实时 K 线数据
     */
    unsubscribeBars(subscriberUID) {
      console.log('[Datafeed] unsubscribeBars:', subscriberUID);
      
      // 清理 bar 轮询定时器
      if (barTimer) {
        clearInterval(barTimer);
        barTimer = null;
      }
      
      // 清理价格轮询定时器
      if (pricePollIntervals.has(subscriberUID)) {
        clearInterval(pricePollIntervals.get(subscriberUID));
        pricePollIntervals.delete(subscriberUID);
      }
      
      // 关闭 WebSocket 连接（传入 subscriberUID）
      disconnectWebSocket(subscriberUID);
    }
  };
}
