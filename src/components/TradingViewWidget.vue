<template>
  <div class="chart-container" ref="chartContainer"></div>
</template>

<script>
import { createChart } from 'lightweight-charts';

export default {
  name: 'TradingViewWidget',
  props: {
    // 初始历史数据 (数组: [{time, open, high, low, close}, ...])
    initialData: {
      type: Array,
      default: () => []
    },
    // 当前显示的交易对名称
    symbol: {
      type: String,
      default: 'BTC/USDT'
    }
  },
  data() {
    return {
      chart: null,       // 图表实例
      candleSeries: null // K线系列实例
    };
  },
  mounted() {
    // 1. 初始化图表
    this.initChart();
    
    // 2. 如果有初始数据，立即填充
    if (this.initialData.length > 0) {
      this.candleSeries.setData(this.initialData);
    }

    // 3. 监听窗口大小变化，实现响应式
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    // 销毁图表，释放内存
    if (this.chart) {
      this.chart.remove();
      this.chart = null;
    }
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    initChart() {
      // 获取容器 DOM
      const container = this.$refs.chartContainer;

      // 创建图表实例
      this.chart = createChart(container, {
        layout: {
          background: { type: 'solid', color: '#000000' }, // 背景色
          textColor: '#D9D9D9', // 文字颜色
        },
        grid: {
          vertLines: { color: '#2B2B43' },
          horzLines: { color: '#2B2B43' },
        },
        // 自动适应容器大小
        width: container.clientWidth,
        height: container.clientHeight,
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      // 创建 K 线系列
      this.candleSeries = this.chart.addCandlestickSeries({
        upColor: '#26a69a',        // 涨：绿色
        downColor: '#ef5350',      // 跌：红色
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      });
    },

    // --- 核心方法：供父组件调用 ---
    
    // 1. 更新整个历史数据（切换币种或初始化时用）
    updateHistory(data) {
      if (this.candleSeries) {
        this.candleSeries.setData(data);
      }
    },

    // 2. 更新单根 K 线（WebSocket 实时推送时用）
    updateLiveCandle(candle) {
      if (this.candleSeries) {
        this.candleSeries.update(candle);
      }
    },

    handleResize() {
      if (this.chart && this.$refs.chartContainer) {
        this.chart.applyOptions({ 
          width: this.$refs.chartContainer.clientWidth,
          height: this.$refs.chartContainer.clientHeight
        });
      }
    }
  },
  watch: {
    // 监听数据变化，如果有新的历史数据传入，自动更新
    initialData: {
      handler(newData) {
        if (this.candleSeries && newData.length > 0) {
          this.candleSeries.setData(newData);
        }
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>