<template>
  <div class="stock-home">
    <header class="top-header">
      <div class="brand-row">
        <div class="brand-left">
          <span class="brand-logo">
            <i></i>
            <i></i>
            <i></i>
          </span>
          <strong>TRUTHSTOCK</strong>
        </div>
        <span class="market-time">{{ currentDate }}</span>
        <button class="globe-btn" type="button" aria-label="language">
          <van-icon name="globe-o" />
        </button>
      </div>

      <div class="session-row">
        <span class="session-dot gold"></span>
        <span class="session-dot red"></span>
        <strong>盘后</strong>
      </div>
    </header>

    <main class="page-body">
      <section class="news-bar">
        <span class="speaker">
          <van-icon name="volume-o" />
        </span>
        <p>霍尔木兹海峡油轮通行状况改善，美原油跌破 70 美元 / 桶</p>
        <button type="button" aria-label="news list">
          <van-icon name="apps-o" />
        </button>
      </section>

      <section class="asset-card">
        <h2>资产概览</h2>
        <div class="asset-amount">
          <strong>0.00</strong>
          <span>USD</span>
        </div>
        <div class="asset-actions">
          <button class="deposit" type="button" @click="showActionToast('存款')">
            <span class="arrow down"></span>
            存款
          </button>
          <button class="withdraw" type="button" @click="showActionToast('提现')">
            <span class="arrow up"></span>
            提现
          </button>
        </div>
      </section>

      <section class="shortcut-card">
        <button type="button" @click="showActionToast('OTC')">
          <span class="shortcut-icon">
            <van-icon name="exchange" />
          </span>
          <strong>OTC</strong>
        </button>
        <button type="button" @click="showActionToast('借贷')">
          <span class="shortcut-icon">
            <van-icon name="gold-coin-o" />
          </span>
          <strong>借贷</strong>
        </button>
      </section>

      <section class="index-grid">
        <button
          v-for="item in indices"
          :key="item.symbol"
          type="button"
          class="index-card"
          @click="selectIndex(item)"
        >
          <strong class="index-name">{{ item.name }}</strong>
          <span class="index-symbol">{{ item.symbol }}</span>
          <span class="index-value">
            {{ item.value }}
            <em :class="item.change >= 0 ? 'up' : 'down'">
              / {{ item.change >= 0 ? '+' : '' }}{{ item.delta }}({{ item.change >= 0 ? '+' : '' }}{{ item.change.toFixed(2) }}%)
            </em>
          </span>
          <svg class="sparkline" viewBox="0 0 180 76" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient :id="`stock-fill-${item.symbol}`" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" :stop-color="item.change >= 0 ? '#00a862' : '#f23645'" stop-opacity="0.26" />
                <stop offset="100%" :stop-color="item.change >= 0 ? '#00a862' : '#f23645'" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path :d="areaPath(item.points)" :fill="`url(#stock-fill-${item.symbol})`" />
            <polyline
              :points="linePoints(item.points)"
              :class="item.change >= 0 ? 'line-up' : 'line-down'"
            />
          </svg>
        </button>
      </section>

      <section class="movers">
        <div class="movers-title">
          <h2>涨幅居前</h2>
          <button type="button" aria-label="refresh" @click="refreshQuotes">
            <van-icon name="replay" />
          </button>
        </div>

        <div class="mover-grid">
          <button
            v-for="stock in topMovers"
            :key="stock.symbol"
            type="button"
            class="mover-card"
            @click="selectStock(stock)"
          >
            <span class="stock-letter" :style="{ '--stock-color': stock.color }">{{ stock.symbol[0] }}</span>
            <strong>{{ stock.symbol }}</strong>
            <em>{{ stock.name }}</em>
            <span class="stock-price">
              ${{ stock.price.toFixed(2) }}
              <i :class="stock.change >= 0 ? 'up' : 'down'">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
              </i>
            </span>
          </button>
        </div>
      </section>
    </main>

    <nav class="bottom-nav" aria-label="stock market navigation">
      <button class="active" type="button">
        <van-icon name="wap-home-o" />
        <span>首页</span>
      </button>
      <button type="button" @click="scrollToIndices">
        <van-icon name="bar-chart-o" />
        <span>市场</span>
      </button>
      <button type="button" @click="showActionToast('交易')">
        <van-icon name="exchange" />
        <span>交易</span>
      </button>
      <button type="button" @click="showActionToast('IPO')">
        <van-icon name="records-o" />
        <span>IPO</span>
      </button>
      <button type="button" @click="router.push('/me')">
        <van-icon name="manager-o" />
        <span>我的</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Icon, showToast } from 'vant';

const VanIcon = Icon;
const router = useRouter();
const quotePulse = ref(0);

const currentDate = computed(() => {
  const now = new Date();
  const weekday = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()];
  const date = `${now.getFullYear()}/${String(now.getMonth() + 1).padStart(2, '0')}/${String(now.getDate()).padStart(2, '0')}`;
  const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
  return `${weekday}，${date} ${time}`;
});

const indices = computed(() => [
  {
    name: 'Nikkei 225 Index',
    symbol: 'JPN225',
    value: '68,516.97',
    delta: '-1,084.21',
    change: -1.58 + quotePulse.value,
    points: [36, 30, 18, 33, 31, 42, 30, 38, 36, 41, 30, 27, 35, 25, 47, 39, 52, 49]
  },
  {
    name: 'Tokyo Stock Price Index',
    symbol: 'TOPIX',
    value: '4,062.26',
    delta: '8.35',
    change: 0.21 + quotePulse.value,
    points: [56, 45, 50, 24, 42, 38, 48, 40, 35, 30, 28, 18, 24, 34, 38, 44, 46, 51]
  },
  {
    name: 'JPX Nikkei 400',
    symbol: 'JPXNIKKEI400',
    value: '36,768.20',
    delta: '15.97',
    change: 0.04 + quotePulse.value,
    points: [58, 46, 51, 21, 36, 44, 40, 38, 34, 29, 18, 25, 34, 43, 47, 42, 50, 54]
  }
]);

const topMovers = computed(() => (
  [
    { symbol: 'AAPL', name: 'Apple Inc.', price: 214.62, change: 0.84, color: '#657ef8' },
    { symbol: 'MSFT', name: 'Microsoft', price: 497.44, change: 1.12, color: '#11b972' },
    { symbol: 'NVDA', name: 'NVIDIA', price: 152.94, change: 2.36, color: '#8bc728' },
    { symbol: 'TSLA', name: 'Tesla', price: 318.86, change: -0.64, color: '#f04b5f' },
    { symbol: 'JPM', name: 'JPMorgan Chase', price: 286.30, change: 0.31, color: '#d69a2a' }
  ].map((stock, index) => ({
    ...stock,
    price: stock.price * (1 + quotePulse.value / 160) + index * 0.02,
    change: stock.change + quotePulse.value
  }))
));

const normalizeY = (point, points) => {
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 1;
  return 10 + ((point - min) / range) * 48;
};

const linePoints = (points) => points.map((point, index) => {
  const x = (index / (points.length - 1)) * 180;
  const y = normalizeY(point, points);
  return `${x.toFixed(1)},${y.toFixed(1)}`;
}).join(' ');

const areaPath = (points) => {
  const line = linePoints(points).split(' ');
  return `M ${line[0]} L ${line.slice(1).join(' L ')} L 180 76 L 0 76 Z`;
};

const refreshQuotes = () => {
  quotePulse.value = Number(((Math.random() - 0.45) * 0.18).toFixed(2));
  showToast('行情已刷新');
};

const showActionToast = (name) => {
  showToast(`${name}功能即将开放`);
};

const selectIndex = (item) => {
  showToast(`${item.name} 详情即将开放`);
};

const selectStock = (stock) => {
  showToast(`${stock.symbol} 详情即将开放`);
};

const scrollToIndices = () => {
  document.querySelector('.index-grid')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
};
</script>

<style scoped>
.stock-home {
  --stock-yellow: #f3ba2f;
  --stock-yellow-soft: #fff4cc;
  --stock-bg: #f5f6f8;
  --stock-text: #07142e;
  --stock-muted: #8f96a3;
  --stock-border: #e9edf2;
  min-height: 100vh;
  color: var(--stock-text);
  background: var(--stock-bg);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.stock-home button {
  appearance: none !important;
  -webkit-appearance: none !important;
  border: 0 !important;
  font-family: inherit !important;
  box-shadow: none;
}

.top-header {
  padding: 16px 16px 12px;
  background: #fff;
  box-shadow: 0 1px 0 var(--stock-border), 0 10px 20px rgba(15, 23, 42, 0.04);
}

.brand-row {
  min-height: 38px;
  display: grid;
  grid-template-columns: auto 1fr 42px;
  align-items: center;
  gap: 12px;
}

.brand-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-logo {
  width: 28px;
  height: 28px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3px;
  transform: rotate(-14deg);
}

.brand-logo i {
  display: block;
  border-radius: 4px;
  background: var(--stock-yellow);
}

.brand-logo i:nth-child(2) {
  background: #f6465d;
}

.brand-logo i:nth-child(3) {
  grid-column: span 2;
  background: #0ecb81;
}

.brand-left strong {
  color: #111827;
  font-size: 24px;
  font-weight: 900;
  letter-spacing: 0;
}

.market-time {
  color: #9ca3af;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.globe-btn {
  width: 42px;
  height: 42px;
  border: 0 !important;
  border-radius: 50%;
  background: #fff;
  color: #222;
  font-size: 25px;
}

.session-row {
  height: 26px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--stock-yellow);
}

.session-row strong {
  color: var(--stock-yellow);
  font-size: 13px;
}

.session-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 3px solid #f1f1f1;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);
}

.session-dot.gold {
  background: var(--stock-yellow);
}

.session-dot.red {
  background: #e0063c;
}

.page-body {
  padding: 14px 14px 102px;
}

.news-bar {
  height: 56px;
  padding: 0 12px;
  border-radius: 8px;
  background: #fff7e5;
  color: #161b29;
  display: grid;
  grid-template-columns: 32px 1fr 32px;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
}

.speaker {
  width: 28px;
  height: 28px;
  color: #d5b15d;
  font-size: 24px;
  display: grid;
  place-items: center;
}

.news-bar p {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.news-bar button,
.movers-title button {
  border: 0 !important;
  background: transparent;
  color: #303640;
  font-size: 22px;
}

.asset-card,
.shortcut-card,
.index-card,
.mover-card {
  background: #fff;
  border: 1px solid var(--stock-border);
  box-shadow: 0 4px 14px rgba(16, 24, 40, 0.08);
}

.asset-card {
  padding: 24px 28px 26px;
  border-radius: 20px;
  margin-bottom: 18px;
}

.asset-card h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
}

.asset-amount {
  margin: 34px 0 28px;
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.asset-amount strong {
  font-size: 48px;
  line-height: 1;
  font-weight: 900;
}

.asset-amount span {
  font-size: 22px;
  font-weight: 700;
}

.asset-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.asset-actions button {
  height: 58px;
  border: 0 !important;
  border-radius: 10px;
  color: #111827;
  font-size: 18px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.asset-actions .deposit {
  background: var(--stock-yellow) !important;
  color: #111827 !important;
}

.asset-actions .withdraw {
  background: #f6465d !important;
  color: #fff !important;
}

.arrow {
  width: 24px;
  height: 24px;
  position: relative;
}

.arrow::before,
.arrow::after {
  content: '';
  position: absolute;
  background: currentColor;
  opacity: 0.65;
}

.arrow::before {
  left: 11px;
  top: 1px;
  width: 2px;
  height: 22px;
  transform: rotate(45deg);
}

.arrow::after {
  right: 1px;
  top: 3px;
  width: 10px;
  height: 2px;
  transform: rotate(45deg);
}

.arrow.down {
  transform: rotate(180deg);
}

.shortcut-card {
  min-height: 132px;
  border-radius: 20px;
  margin-bottom: 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
}

.shortcut-card button {
  border: 0 !important;
  background: #fff !important;
  color: #111827 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.shortcut-icon {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #363942;
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 30px;
}

.shortcut-card strong {
  font-size: 20px;
  font-weight: 900;
}

.index-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 28px;
}

.index-card {
  min-height: 190px;
  border-radius: 18px;
  padding: 18px 16px 12px;
  color: var(--stock-text);
  text-align: left;
  overflow: hidden;
  background: #fff !important;
  border: 1px solid var(--stock-border) !important;
}

.index-name,
.index-symbol,
.index-value {
  display: block;
}

.index-name {
  min-height: 42px;
  font-size: 18px;
  line-height: 1.18;
  font-weight: 900;
}

.index-symbol {
  margin-top: 4px;
  color: #a0a4ad;
  font-size: 16px;
  font-weight: 800;
}

.index-value {
  margin-top: 6px;
  font-size: 16px;
  line-height: 1.35;
  font-weight: 800;
}

.index-value em {
  font-style: normal;
}

.sparkline {
  width: 100%;
  height: 78px;
  margin-top: 8px;
}

.sparkline polyline {
  fill: none;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.line-up {
  stroke: #00a862;
}

.line-down {
  stroke: #f23645;
}

.movers-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.movers-title h2 {
  margin: 0;
  font-size: 27px;
  font-weight: 950;
}

.movers-title button {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: #fff !important;
  border: 1px solid var(--stock-border) !important;
  color: var(--stock-yellow) !important;
}

.mover-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.mover-card {
  min-height: 126px;
  padding: 10px 8px 8px;
  border-radius: 0;
  color: var(--stock-text);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff !important;
  border: 1px solid #b8bec8 !important;
}

.stock-letter {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  color: var(--stock-color);
  background: color-mix(in srgb, var(--stock-color) 20%, white);
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 18px;
  margin-bottom: 4px;
}

.mover-card strong {
  font-size: 18px;
  line-height: 1.1;
}

.mover-card em {
  color: #777f8f;
  font-size: 14px;
  font-style: normal;
  margin-top: 4px;
}

.stock-price {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 900;
  white-space: nowrap;
}

.stock-price i {
  font-style: italic;
  font-weight: 500;
}

.up {
  color: #00a862 !important;
}

.down {
  color: #f23645 !important;
}

.bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 76px;
  padding: 7px 18px max(7px, env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.96);
  border-top: 1px solid var(--stock-border);
  box-shadow: 0 -8px 24px rgba(16, 24, 40, 0.08);
  backdrop-filter: blur(18px);
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  z-index: 50;
}

.bottom-nav button {
  border: 0 !important;
  background: transparent !important;
  color: #111827 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  font-size: 14px;
  font-weight: 800;
}

.bottom-nav .van-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #eef1f5;
  color: #343a44;
  display: grid;
  place-items: center;
  font-size: 18px;
}

.bottom-nav .active {
  color: #a47b00 !important;
}

.bottom-nav .active .van-icon {
  color: #a47b00;
  background: var(--stock-yellow-soft);
}

@media (max-width: 390px) {
  .top-header {
    padding-left: 12px;
    padding-right: 12px;
  }

  .page-body {
    padding-left: 12px;
    padding-right: 12px;
  }

  .brand-left strong {
    font-size: 21px;
  }

  .market-time {
    font-size: 12px;
  }

  .asset-card {
    padding: 20px 20px 22px;
  }

  .index-grid {
    gap: 10px;
  }

  .index-card {
    padding: 14px 12px 10px;
  }
}
</style>
