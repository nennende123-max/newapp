<template>
  <div class="tradingview-widget-container" style="height: 500px; width: 100%">
    <div id="tv-chart-container" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script>
import { onMounted, onUnmounted } from 'vue';
import { createDatafeed } from '../utils/tradingview-datafeed.js';

export default {
  name: 'TradingViewWidget',
  props: {
    symbol: {
      type: String,
      default: 'BTCUSDT'  // 接收 symbol 属性，默认为 BTCUSDT
    }
  },
  setup(props) {
    let widget = null;
    
    function initWidget() {
      // 添加加载检查
      if (window.TradingView) {
        // 确保容器存在
        const containerElement = document.getElementById('tv-chart-container');
        if (!containerElement) {
          console.error('Container #tv-chart-container not found!');
          return;
        }

        // 清空容器
        containerElement.innerHTML = '';

        // 如果已有 widget，先移除
        if (widget) {
          try {
            widget.remove();
          } catch (e) {
            console.error('移除旧 widget 失败:', e);
          }
          widget = null;
        }

        // 创建自定义 datafeed
        const Datafeed = createDatafeed();

        widget = new window.TradingView.widget({
          autosize: true,
          symbol: 'BINANCE:BTCUSDT',  // 强制 Binance BTCUSDT
          interval: '1',
          timezone: 'Etc/UTC',
          theme: 'dark',
          style: '1',
          locale: 'zh_CN',
          enable_publishing: false,
          withdateranges: true,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          container_id: 'tv-chart-container',
          datafeed: Datafeed,
        });
        
        console.log('K 线 widget 加载成功，symbol: BINANCE:BTCUSDT');
      } else {
        console.error('TradingView 库未加载');
      }
    }

    onMounted(() => {
      try {
        if (!window.TradingView) {
          const script = document.createElement('script');
          script.src = 'https://s3.tradingview.com/tv.js';
          script.async = true;
          script.onload = () => {
            console.log('TradingView 库加载成功');
            initWidget();
          };
          script.onerror = () => {
            console.error('TradingView 脚本加载失败');
          };
          document.head.appendChild(script);
        } else {
          initWidget();
        }
      } catch (error) {
        console.error('Widget 初始化错误:', error);
      }
    });

    onUnmounted(() => {
      if (widget) {
        widget.remove();
        widget = null;
      }
    });
  }
};
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

#tv-chart-container {
  width: 100%;
  height: 500px;
  min-height: 500px;
  pointer-events: auto;
}

:deep(#tv-chart-container) {
  width: 100% !important;
  height: 500px !important;
  pointer-events: auto !important;
}
</style>
