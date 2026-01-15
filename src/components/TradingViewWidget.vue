<template>
  <div class="tradingview-widget-container">
    <div id="tradingview_widget"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch, toRaw } from 'vue';

// Props definition
const props = defineProps({
  symbol: {
    type: String,
    default: 'BTC'
  },
  interval: {
    type: String,
    default: 'D'
  }
});

// 映射用户友好的时间周期到 TradingView 格式
const mapIntervalToTradingView = (interval) => {
  const intervalMap = {
    '1m': '1',
    '5m': '5',
    '15m': '15',
    '30m': '30',
    '1h': '60',
    '4h': '240',
    '1d': 'D',
    '1w': 'W'
  };
  return intervalMap[interval] || interval;
};

let widget = null;

onMounted(() => {
  if (window.TradingView) {
    initWidget();
  } else {
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      initWidget();
    };
    script.onerror = () => {
      console.error('Failed to load TradingView script');
    };
    
    const existingScript = document.querySelector('script[src="https://s3.tradingview.com/tv.js"]');
    if (!existingScript) {
      document.head.appendChild(script);
    } else {
      if (window.TradingView) {
        initWidget();
      } else {
        existingScript.onload = () => {
          initWidget();
        };
      }
    }
  }
});

// 内部函数：使用指定的 symbol 初始化 widget
const initWidgetWithSymbol = (finalTradingPair, mappedInterval) => {
  if (!window.TradingView) {
    console.error('TradingView is not available');
    return;
  }

  if (widget) {
    try {
      widget.remove();
    } catch (e) {
      console.error('Error removing existing widget:', e);
    }
    widget = null;
  }

  console.log('Initializing TradingView with symbol:', finalTradingPair, 'interval:', mappedInterval);

  // **深度修复：强制使用加密货币数据源，彻底禁用盘前/盘后**
  widget = new window.TradingView.widget({
    container_id: 'tradingview_widget',
    // **核心修复**：symbol 必须是 "BINANCE:XXXUSDT" 格式
    symbol: finalTradingPair,
    interval: mappedInterval,
    theme: 'dark',
    locale: 'zh_CN',
    autosize: true,
    toolbar_bg: '#1e1e1e',
    hide_side_toolbar: false,
    allow_symbol_change: false,
    // **关键配置：禁用市场状态显示（这会显示盘前/盘后信息）**
    disabled_features: [
      'use_localstorage_for_settings',
      'volume_force_overlay',
      'create_volume_indicator_by_default',
      'header_symbol_search',
      'header_compare',
      'header_screenshot',
      'header_widget',
      'display_market_status', // **关键**：禁用市场状态显示
      'header_symbol_info',
      'symbol_info'
    ],
    enabled_features: [
      'study_templates'
    ],
    studies: [
      'Volume@tv-basicstudies'
    ],
    // **强制使用加密货币市场设置**
    overrides: {
      'paneProperties.background': '#000000',
      'paneProperties.backgroundType': 'solid',
      'mainSeriesProperties.candleStyle.upColor': '#0ECB81',
      'mainSeriesProperties.candleStyle.downColor': '#F6465D',
      'mainSeriesProperties.candleStyle.borderUpColor': '#0ECB81',
      'mainSeriesProperties.candleStyle.borderDownColor': '#F6465D',
      'mainSeriesProperties.candleStyle.wickUpColor': '#0ECB81',
      'mainSeriesProperties.candleStyle.wickDownColor': '#F6465D',
      'paneProperties.backgroundGradientStartColor': '#000000',
      'paneProperties.backgroundGradientEndColor': '#000000',
      'scalesProperties.showLeftScale': true,
      'scalesProperties.showRightScale': true,
      'mainSeriesProperties.showCountdown': false,
      'paneProperties.legendProperties.showSeriesPrevClosePrice': false,
      'paneProperties.legendProperties.showSeriesChange': false,
      'paneProperties.legendProperties.showSeriesChangePercent': false
    },
    // **关键配置：时区和交易时段**
    timezone: 'UTC',
    session: '24x7', // **关键**：24x7 明确告诉 TradingView 这是 24 小时交易市场，无盘前/盘后
    extended_hours: false, // **双重保险**：明确禁用延长交易时段
    charts_storage_url: 'https://saveload.tradingview.com',
    charts_storage_api_version: '1.1',
    client_id: 'tradingview.com',
    user_id: 'public_user_id',
    fullscreen: false,
    width: '100%',
    height: 500
  });
  
  if (widget) {
    console.log('TradingView widget initialized successfully with:', finalTradingPair);
  } else {
    console.error('Failed to initialize TradingView widget');
  }
};

const initWidget = () => {
  if (!window.TradingView) {
    console.error('TradingView is not available');
    return;
  }

  let symbolUpper = (props.symbol || 'BTC').toUpperCase().trim();
  symbolUpper = symbolUpper.replace(/[^A-Z0-9]/g, '');
  
  const baseSymbol = (symbolUpper === 'USDT' || symbolUpper === '' || symbolUpper.length === 0) ? 'BTC' : symbolUpper;
  
  let finalTradingPair;
  if (baseSymbol.includes('BINANCE:')) {
    const extracted = baseSymbol.replace(/^BINANCE:/i, '').replace(/USDT$/i, '');
    finalTradingPair = `BINANCE:${extracted || 'BTC'}USDT`;
  } else {
    finalTradingPair = `BINANCE:${baseSymbol}USDT`;
  }
  
  const mappedInterval = mapIntervalToTradingView(props.interval);
  
  if (!finalTradingPair.startsWith('BINANCE:') || !finalTradingPair.endsWith('USDT')) {
    console.error('Invalid symbol format detected:', finalTradingPair, '- Using BTCUSDT as fallback');
    finalTradingPair = 'BINANCE:BTCUSDT';
  }
  
  if (finalTradingPair.includes('OTC:') || 
      finalTradingPair.includes('NASDAQ:') || 
      finalTradingPair.includes('NYSE:') ||
      finalTradingPair.includes('CBOE:') ||
      finalTradingPair.match(/^[A-Z]{1,5}$/)) {
    console.error('Stock/ETF symbol detected:', finalTradingPair, '- Forcing crypto format');
    finalTradingPair = 'BINANCE:BTCUSDT';
  }
  
  console.log('Final TradingView symbol (CRYPTO FORCED):', finalTradingPair);
  
  initWidgetWithSymbol(finalTradingPair, mappedInterval);
};

let lastSymbol = toRaw(props.symbol);
let lastInterval = toRaw(props.interval);

watch(
  () => [props.symbol, props.interval],
  ([newSymbol, newInterval]) => {
    const symbolChanged = toRaw(newSymbol) !== lastSymbol;
    const intervalChanged = toRaw(newInterval) !== lastInterval;
    
    if ((symbolChanged || intervalChanged) && window.TradingView) {
      lastSymbol = toRaw(newSymbol);
      lastInterval = toRaw(newInterval);
      initWidget();
    }
  },
  { deep: false }
);

onUnmounted(() => {
  if (widget) {
    try {
      widget.remove();
    } catch (e) {
      console.error('Error removing TradingView widget:', e);
    }
    widget = null;
  }
});
</script>

<style scoped>
.tradingview-widget-container {
  width: 100%;
  margin-bottom: 20px;
  background: #1C1C1E;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

#tradingview_widget {
  width: 100%;
  height: 500px;
  min-height: 500px;
  pointer-events: auto;
}

:deep(#tradingview_widget) {
  width: 100% !important;
  height: 500px !important;
  pointer-events: auto !important;
}
</style>

