<template>
  <div class="treasury-detail-page">
    <!-- 顶部导航栏 -->
    <div class="app-header">
      <div class="header-left">
        <div class="back-button" @click="router.go(-1)">
          <van-icon name="arrow-left" size="18" />
        </div>
      </div>
      <div class="header-title">
        <span>{{ $t('treasury.title') }}</span>
      </div>
      <div class="header-right"></div>
    </div>

    <div class="scroll-content">
      <!-- 头部卡片 -->
      <div class="header-card">
        <div class="treasury-amount">
          <div class="amount-label">{{ $t('treasury.real_time_assets') }}</div>
          <div class="amount-value">$ {{ formatTreasuryAmount(treasuryAmount) }}</div>
          <div class="amount-change" :class="{ positive: treasuryGrowth >= 0, negative: treasuryGrowth < 0 }">
            {{ treasuryGrowth >= 0 ? '+' : '' }}{{ treasuryGrowth.toFixed(2) }}% (24h)
          </div>
        </div>

        <div class="security-badges">
          <div class="badge-item">
            <van-icon name="passed" size="14" color="var(--color-success)" />
            <span>{{ $t('treasury.security_level') }}：AAA</span>
          </div>
          <div class="badge-item">
            <van-icon name="shield-o" size="14" color="var(--color-success)" />
            <span>{{ $t('treasury.auditor') }}：CertiK</span>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="chart-section">
        <div class="chart-title">{{ $t('treasury.net_inflow_30d') }}</div>
        <div class="chart-container">
          <svg class="trend-chart" viewBox="0 0 300 120" preserveAspectRatio="none">
            <defs>
              <linearGradient id="trendGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:var(--color-success);stop-opacity:0.28" />
                <stop offset="100%" style="stop-color:var(--color-success);stop-opacity:0" />
              </linearGradient>
            </defs>
            <!-- 面积图 -->
            <path 
              d="M 0 100 Q 50 80 100 70 T 200 50 T 300 40 L 300 120 L 0 120 Z" 
              fill="url(#trendGradient)"
            />
            <!-- 趋势线 -->
            <path 
              d="M 0 100 Q 50 80 100 70 T 200 50 T 300 40" 
              fill="none" 
              stroke="var(--color-success)" 
              stroke-width="2" 
              stroke-linecap="round"
            />
          </svg>
        </div>
      </div>

      <!-- 实时归集记录 -->
      <div class="records-section">
        <div class="section-title">
          <van-icon name="orders-o" size="16" color="var(--color-brand-legacy)" />
          <span>{{ $t('treasury.on_chain_records') }}</span>
        </div>

        <div class="records-list" ref="recordsListRef">
          <div 
            v-for="(record, index) in records" 
            :key="index"
            class="record-item"
            :class="{ 'new-record': index === 0 && isNewRecord }"
          >
            <div class="record-time">{{ record.time }}</div>
            <div class="record-source">{{ formatRecordSource(record.source, record.pair) }}</div>
            <div class="record-txid" @click="copyTxId(record.txId)">
              {{ record.txId }}
              <van-icon name="copy" size="12" class="copy-icon" />
            </div>
            <div class="record-amount positive">+ ${{ formatAmount(record.amount) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

// 国库资产金额（与首页同步）
const treasuryAmount = ref(142500000);
const treasuryGrowth = ref(0.88);

// 记录列表
const records = ref([
  {
    time: '10:24:58',
    source: 'spot',
    pair: 'BTC/USDT',
    txId: '0x8a...4b2d',
    amount: 124.50
  },
  {
    time: '10:23:15',
    source: 'futures',
    pair: 'ETH/USDT',
    txId: '0x7c...9f1a',
    amount: 89.30
  },
  {
    time: '10:21:42',
    source: 'spot',
    pair: 'BNB/USDT',
    txId: '0x5e...3c8b',
    amount: 156.80
  },
  {
    time: '10:20:08',
    source: 'staking',
    pair: '',
    txId: '0x4a...2d7e',
    amount: 234.20
  },
  {
    time: '10:18:33',
    source: 'spot',
    pair: 'SOL/USDT',
    txId: '0x3b...1a5c',
    amount: 67.90
  }
]);

const recordsListRef = ref(null);
const isNewRecord = ref(false);

// 生成随机交易来源
const generateRandomSource = () => {
  const sources = [
    { type: 'spot', pair: 'BTC/USDT' },
    { type: 'spot', pair: 'ETH/USDT' },
    { type: 'spot', pair: 'BNB/USDT' },
    { type: 'spot', pair: 'SOL/USDT' },
    { type: 'futures', pair: 'BTC/USDT' },
    { type: 'futures', pair: 'ETH/USDT' },
    { type: 'staking', pair: '' },
    { type: 'liquidity', pair: '' },
    { type: 'ido', pair: '' },
    { type: 'margin', pair: '' }
  ];
  return sources[Math.floor(Math.random() * sources.length)];
};

// 格式化记录来源显示文本
const formatRecordSource = (sourceType, pair) => {
  let sourceText = '';
  switch (sourceType) {
    case 'spot':
      sourceText = t('treasury.spot_fee');
      break;
    case 'futures':
      sourceText = t('treasury.futures_fee');
      break;
    case 'staking':
      sourceText = t('treasury.staking_reward');
      break;
    case 'liquidity':
      sourceText = t('treasury.liquidity_pool_fee');
      break;
    case 'ido':
      sourceText = t('treasury.ido_platform_fee');
      break;
    case 'margin':
      sourceText = t('treasury.margin_trading_fee');
      break;
    default:
      sourceText = sourceType;
  }
  
  // 如果有交易对，追加到文本后面
  if (pair) {
    return `${sourceText} - ${pair}`;
  }
  return sourceText;
};

// 生成随机 TxID
const generateRandomTxId = () => {
  const chars = '0123456789abcdef';
  const prefix = '0x';
  const suffix = chars[Math.floor(Math.random() * chars.length)] + 
                 chars[Math.floor(Math.random() * chars.length)] + 
                 chars[Math.floor(Math.random() * chars.length)] + 
                 chars[Math.floor(Math.random() * chars.length)];
  return prefix + suffix;
};

// 格式化金额
const formatAmount = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 格式化国库金额
const formatTreasuryAmount = (value) => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(2) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(2) + 'K';
  }
  return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
};

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// 复制 TxID
const copyTxId = async (txId) => {
  try {
    await navigator.clipboard.writeText(txId);
    showToast({
      message: t('treasury.txid_copied'),
      icon: 'success',
      duration: 1500
    });
  } catch (err) {
    showToast({
      message: t('treasury.copy_failed'),
      icon: 'fail',
      duration: 1500
    });
  }
};

// 模拟定时器
let treasuryTimer = null;
let recordsTimer = null;

// 启动国库增长模拟
const startTreasuryGrowth = () => {
  treasuryTimer = setInterval(() => {
    const increase = Math.floor(Math.random() * 451) + 50; // 50-500
    treasuryAmount.value += increase;
    
    // 24h涨幅微调
    treasuryGrowth.value = 0.88 + (Math.random() - 0.5) * 0.5;
  }, 3000 + Math.random() * 2000); // 每 3-5 秒更新一次
};

// 启动记录模拟
const startRecordsSimulation = () => {
  recordsTimer = setInterval(() => {
    // 生成新记录
    const sourceData = generateRandomSource();
    const newRecord = {
      time: getCurrentTime(),
      source: sourceData.type,
      pair: sourceData.pair,
      txId: generateRandomTxId(),
      amount: Math.random() * 300 + 50 // 50-350
    };
    
    // 添加到列表顶部
    records.value.unshift(newRecord);
    
    // 标记为新记录，触发动画
    isNewRecord.value = true;
    setTimeout(() => {
      isNewRecord.value = false;
    }, 500);
    
    // 限制列表长度，最多保留 50 条
    if (records.value.length > 50) {
      records.value = records.value.slice(0, 50);
    }
    
    // 自动滚动到顶部（可选）
    if (recordsListRef.value) {
      recordsListRef.value.scrollTop = 0;
    }
  }, 4000 + Math.random() * 3000); // 每 4-7 秒添加一条新记录
};

onMounted(() => {
  startTreasuryGrowth();
  startRecordsSimulation();
});

onUnmounted(() => {
  if (treasuryTimer) {
    clearInterval(treasuryTimer);
  }
  if (recordsTimer) {
    clearInterval(recordsTimer);
  }
});
</script>

<style scoped>
.treasury-detail-page {
  background-color: var(--color-surface-1);
  min-height: 100vh;
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
  font-variant-numeric: tabular-nums;
}

/* 顶部导航栏 */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 52px;
  padding: 0 16px;
  background-color: var(--color-surface-2);
  position: sticky;
  top: 0;
  z-index: 100;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border-subtle);
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  min-width: 40px;
}

.back-button {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button :deep(.van-icon) {
  color: var(--color-text-primary);
  transition: color 0.2s ease;
}

.back-button:active {
  background-color: var(--color-surface-muted);
  transform: scale(0.95);
}

.header-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: center;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 80px;
}

/* 头部卡片 */
.header-card {
  background: var(--color-surface-2);
  border-radius: 16px;
  padding: 22px;
  margin-bottom: 14px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.treasury-amount {
  margin-bottom: 18px;
}

.amount-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.amount-value {
  font-size: 34px;
  font-weight: 800;
  color: var(--color-text-primary);
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
  font-variant-numeric: tabular-nums;
  margin-bottom: 6px;
  line-height: 1.15;
  letter-spacing: -0.5px;
}

.amount-change {
  font-size: 13px;
  font-weight: 600;
}

.amount-change.positive {
  color: var(--color-success);
}

.amount-change.negative {
  color: var(--color-danger);
}

.security-badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

/* 图表区域 */
.chart-section {
  background: var(--color-surface-2);
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 14px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.chart-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 14px;
}

.chart-container {
  width: 100%;
  height: 120px;
  overflow: hidden;
}

.trend-chart {
  width: 100%;
  height: 100%;
}

/* 记录列表 */
.records-section {
  background: var(--color-surface-2);
  border-radius: 16px;
  padding: 18px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.records-list {
  max-height: 500px;
  overflow-y: auto;
}

.record-item {
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border-subtle);
  display: grid;
  grid-template-columns: 66px 1fr auto;
  grid-template-rows: auto auto;
  gap: 6px 12px;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.record-item:last-child {
  border-bottom: none;
}

.record-item.new-record {
  background-color: rgb(var(--color-success-rgb) / 0.06);
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.record-time {
  grid-column: 1;
  grid-row: 1 / 3;
  font-size: 11px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
  display: flex;
  align-items: center;
}

.record-source {
  grid-column: 2;
  grid-row: 1;
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.record-txid {
  grid-column: 2;
  grid-row: 2;
  font-size: 11px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.record-txid:active {
  color: var(--color-primary);
}

.copy-icon {
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.record-txid:active .copy-icon {
  opacity: 1;
}

.record-amount {
  grid-column: 3;
  grid-row: 1 / 3;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-success);
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif;
  font-variant-numeric: tabular-nums;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.record-amount.positive {
  color: var(--color-success);
}

/* 滚动条样式 */
.records-list::-webkit-scrollbar {
  width: 4px;
}

.records-list::-webkit-scrollbar-track {
  background: transparent;
}

.records-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}
</style>