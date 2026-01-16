<template>
  <div class="chain-explorer-page">
    <!-- 顶部导航 -->
    <div class="explorer-header">
      <div class="header-left">
        <div class="back-button" @click="handleBack">
          <van-icon name="arrow-left" size="18" />
        </div>
        <span class="header-title">{{ $t('chain_explorer.title') }}</span>
      </div>
      <div class="header-right">
        <div class="status-indicator">
          <div class="status-dot"></div>
          <span class="status-text">{{ $t('chain_explorer.network_status') }}</span>
        </div>
      </div>
    </div>

    <!-- 仪表盘 -->
    <div class="dashboard">
      <div class="dashboard-card">
        <div class="card-label">{{ $t('chain_explorer.current_gas') }}</div>
        <div class="card-value">{{ currentGas }} Gwei</div>
      </div>
      <div class="dashboard-card">
        <div class="card-label">{{ $t('chain_explorer.block_height') }}</div>
        <div class="card-value">{{ blockHeight }}</div>
      </div>
      <div class="dashboard-card">
        <div class="card-label">{{ $t('chain_explorer.net_flow_24h') }}</div>
        <div class="card-value">{{ formatNetFlow(netFlow24h) }}</div>
      </div>
    </div>

    <!-- 列表容器 -->
    <div class="terminal-container">
      <!-- 表头 -->
      <div class="table-header">
        <div class="th-cell th-time">{{ $t('chain_explorer.table_time') }}</div>
        <div class="th-cell th-type">{{ $t('chain_explorer.table_type') }}</div>
        <div class="th-cell th-hash">{{ $t('chain_explorer.table_hash') }}</div>
        <div class="th-cell th-amount">{{ $t('chain_explorer.table_amount') }}</div>
        <div class="th-cell th-status">{{ $t('chain_explorer.table_status') }}</div>
      </div>

      <!-- 数据行 -->
      <div class="table-body">
        <transition-group name="slide-in" tag="div">
          <div
            v-for="tx in transactions"
            :key="tx.id"
            class="table-row"
            :class="{ 'is-whale': tx.isWhale, 'even-row': tx.index % 2 === 0 }"
          >
            <div class="td-cell td-time">{{ tx.time }}</div>
            <div class="td-cell td-type" :class="tx.isDeposit ? 'type-deposit' : 'type-withdraw'">
              <van-icon 
                :name="tx.isDeposit ? 'arrow-down' : 'arrow-up'" 
                class="type-icon"
              />
              <span>{{ tx.type }}</span>
            </div>
            <div class="td-cell td-hash">{{ tx.hash }}</div>
            <div class="td-cell td-amount" :class="{ 'whale-amount': tx.isWhale }">
              {{ formatAmount(tx.amount, tx.coin) }}
            </div>
            <div class="td-cell td-status" :class="tx.isSuccess ? 'status-success' : 'status-pending'">
              {{ tx.status }}
            </div>
          </div>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { Icon } from 'vant';

const VanIcon = Icon;

const router = useRouter();
const { t, locale } = useI18n();

// 监听语言变化，更新所有交易记录的类型和状态文本
watch(locale, () => {
  transactions.value.forEach(tx => {
    // 更新类型文本
    if (tx.isDeposit) {
      tx.type = t('chain_explorer.type_deposit');
    } else {
      tx.type = t('chain_explorer.type_withdraw');
    }
    // 更新状态文本
    if (tx.isSuccess) {
      tx.status = t('chain_explorer.status_success');
    } else {
      tx.status = t('chain_explorer.status_confirming');
    }
  });
});

// --- 核心变量定义 ---
const transactions = ref([]);
const coins = ['USDT', 'ETH', 'BTC', 'SOL'];

// 仪表盘数据
const currentGas = ref(24);
const blockHeight = ref(18293000);
const netFlow24h = ref(45200000); // $45.2M

// 定时器引用
let dataInterval = null;
let gasInterval = null;
let blockInterval = null;

// 交易索引计数器（用于斑马纹）
let transactionIndex = 0;

// --- 辅助函数 ---

/**
 * 生成伪随机哈希
 * 格式：0x + 4位随机字符 + ... + 4位随机字符
 */
const generateHash = () => {
  const chars = '0123456789abcdef';
  const firstPart = Array.from({ length: 4 }, () => 
    chars[Math.floor(Math.random() * chars.length)]
  ).join('');
  const lastPart = Array.from({ length: 4 }, () => 
    chars[Math.floor(Math.random() * chars.length)]
  ).join('');
  return `0x${firstPart}...${lastPart}`;
};

/**
 * 生成金额（包含巨鲸逻辑）
 * @param {string} coin - 币种
 * @returns {number} 金额
 */
const generateAmount = (coin) => {
  const isWhale = Math.random() < 0.05; // 5% 概率触发巨鲸
  
  // 币种对应的金额范围配置
  const coinConfig = {
    USDT: {
      whale: { min: 50000, max: 500000 },
      normal: { min: 10, max: 5000 }
    },
    ETH: {
      whale: { min: 50, max: 500 },
      normal: { min: 0.1, max: 50 }
    },
    BTC: {
      whale: { min: 0.5, max: 5 },
      normal: { min: 0.001, max: 0.5 }
    },
    SOL: {
      whale: { min: 500, max: 5000 },
      normal: { min: 1, max: 500 }
    }
  };

  const config = coinConfig[coin] || coinConfig.USDT;
  
  if (isWhale) {
    return parseFloat((Math.random() * (config.whale.max - config.whale.min) + config.whale.min).toFixed(coin === 'USDT' ? 2 : 6));
  } else {
    return parseFloat((Math.random() * (config.normal.max - config.normal.min) + config.normal.min).toFixed(coin === 'USDT' ? 2 : 6));
  }
};

/**
 * 生成新交易数据
 */
const generateTransaction = () => {
  const coin = coins[Math.floor(Math.random() * coins.length)];
  const amount = generateAmount(coin);
  const isWhale = amount > (coin === 'USDT' ? 50000 : coin === 'ETH' ? 50 : coin === 'BTC' ? 0.5 : 500);
  
  // 根据当前语言设置时间格式
  const timeLocale = locale.value === 'zh' ? 'zh-CN' : 'en-US';
  
  // 判断是充值还是提现
  const isDeposit = Math.random() > 0.4; // 充值稍多一点
  
  const transaction = {
    id: Date.now() + Math.random(),
    time: new Date().toLocaleTimeString(timeLocale, { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
    type: isDeposit ? t('chain_explorer.type_deposit') : t('chain_explorer.type_withdraw'),
    coin: coin,
    amount: amount,
    hash: generateHash(),
    status: t('chain_explorer.status_confirming'),
    isDeposit: isDeposit,
    isSuccess: false,
    isWhale: isWhale,
    index: transactionIndex++
  };

  // 使用 unshift 添加到数组开头
  transactions.value.unshift(transaction);

  // 保持数组长度不超过 50 条
  if (transactions.value.length > 50) {
    transactions.value.pop();
  }

  // 3秒后自动将状态改为"成功"
  setTimeout(() => {
    const tx = transactions.value.find(txItem => txItem.id === transaction.id);
    if (tx) {
      tx.status = t('chain_explorer.status_success');
      tx.isSuccess = true;
    }
  }, 3000);

  // 更新24H净流入（简化计算：充值增加，提现减少）
  if (transaction.isDeposit) {
    netFlow24h.value += transaction.amount * (coin === 'USDT' ? 1 : getCoinPrice(coin));
  } else {
    netFlow24h.value -= transaction.amount * (coin === 'USDT' ? 1 : getCoinPrice(coin));
  }
};

/**
 * 获取币种价格（用于计算净流入）
 */
const getCoinPrice = (coin) => {
  const prices = {
    ETH: 3100,
    BTC: 92000,
    SOL: 140
  };
  return prices[coin] || 1;
};

/**
 * 格式化金额显示
 */
const formatAmount = (amount, coin) => {
  if (coin === 'USDT') {
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  } else {
    return `${amount.toFixed(6)} ${coin}`;
  }
};

/**
 * 格式化净流入
 */
const formatNetFlow = (value) => {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(1)}K`;
  }
  return `$${value.toFixed(0)}`;
};

// --- 主循环 ---

/**
 * 启动数据生成循环
 */
const startDataGeneration = () => {
  const generateNext = () => {
    generateTransaction();
    // 随机间隔 800ms ~ 2000ms
    const nextDelay = Math.floor(Math.random() * (2000 - 800 + 1)) + 800;
    dataInterval = setTimeout(generateNext, nextDelay);
  };
  generateNext();
};

/**
 * 启动 Gas 价格微调
 */
const startGasUpdate = () => {
  gasInterval = setInterval(() => {
    // Gas 价格在 20-30 Gwei 之间随机微调
    currentGas.value = Math.floor(Math.random() * (30 - 20 + 1)) + 20;
  }, 2000);
};

/**
 * 启动区块高度跳动
 */
const startBlockUpdate = () => {
  blockInterval = setInterval(() => {
    // 区块高度最后三位动态跳动（每次增加 1-3）
    const increment = Math.floor(Math.random() * 3) + 1;
    blockHeight.value += increment;
  }, 1500);
};

// --- 生命周期 ---

onMounted(() => {
  // 初始化生成几条数据
  for (let i = 0; i < 5; i++) {
    setTimeout(() => {
      generateTransaction();
    }, i * 500);
  }

  // 启动各种定时器
  startDataGeneration();
  startGasUpdate();
  startBlockUpdate();
});

onUnmounted(() => {
  // 清理定时器
  if (dataInterval) clearTimeout(dataInterval);
  if (gasInterval) clearInterval(gasInterval);
  if (blockInterval) clearInterval(blockInterval);
});

// --- 导航处理 ---

const handleBack = () => {
  router.back();
};
</script>

<style scoped>
.chain-explorer-page {
  background-color: #0E0E0E;
  min-height: 100vh;
  color: #FFFFFF;
  font-family: 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  padding-bottom: 20px;
}

/* 顶部导航 */
.explorer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #0E0E0E;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #141414;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.back-button :deep(.van-icon) {
  color: #D4AF37;
  transition: color 0.3s ease;
}

.back-button:active {
  background-color: rgba(212, 175, 55, 0.1);
  border-color: rgba(212, 175, 55, 0.3);
  transform: scale(0.95);
}

.back-button:active :deep(.van-icon) {
  color: #FCD535;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.3px;
}

.header-right {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background-color: #0ECB81;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(14, 203, 129, 0.6);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 8px rgba(14, 203, 129, 0.6);
  }
  50% {
    opacity: 0.7;
    box-shadow: 0 0 16px rgba(14, 203, 129, 0.8);
  }
}

.status-text {
  font-size: 12px;
  color: #0ECB81;
  font-weight: 500;
}

/* 仪表盘 */
.dashboard {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.dashboard-card {
  flex: 1;
  background-color: #141414;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.card-label {
  font-size: 11px;
  color: #848E9C;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

/* 列表容器 */
.terminal-container {
  padding: 0 16px;
}

.table-header {
  display: flex;
  background-color: #141414;
  padding: 12px 16px;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  font-weight: 700;
  color: #848E9C;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.th-cell {
  font-family: 'Roboto Mono', 'Courier New', monospace;
}

.th-time {
  flex: 0 0 80px;
}

.th-type {
  flex: 0 0 80px;
}

.th-hash {
  flex: 1;
  min-width: 0;
}

.th-amount {
  flex: 0 0 140px;
  text-align: right;
}

.th-status {
  flex: 0 0 80px;
  text-align: right;
}

/* 表体 */
.table-body {
  background-color: #0E0E0E;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.table-row {
  display: flex;
  align-items: center;
  height: 40px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  transition: background-color 0.3s ease;
}

.table-row.even-row {
  background-color: #141414;
}

.table-row.is-whale {
  background-color: rgba(252, 213, 53, 0.05);
}

.td-cell {
  font-size: 12px;
  font-weight: 500;
  color: #EAECEF;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.td-time {
  flex: 0 0 80px;
  color: #848E9C;
}

.td-type {
  flex: 0 0 80px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}

.type-icon {
  font-size: 14px;
}

.type-deposit {
  color: #0ECB81;
}

.type-withdraw {
  color: #F6465D;
}

.td-hash {
  flex: 1;
  min-width: 0;
  color: #848E9C;
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-amount {
  flex: 0 0 140px;
  text-align: right;
  font-weight: 600;
}

.td-amount.whale-amount {
  color: #FCD535;
  font-weight: 700;
  font-size: 13px;
}

.td-status {
  flex: 0 0 80px;
  text-align: right;
  font-size: 11px;
  font-weight: 600;
}

.status-success {
  color: #0ECB81;
}

.status-pending {
  color: #FCD535;
}

/* 滑入动画 */
.slide-in-enter-active {
  animation: slideIn 0.5s ease-out;
}

.slide-in-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translateY(-20px);
    background-color: rgba(252, 213, 53, 0.2);
  }
  50% {
    background-color: rgba(252, 213, 53, 0.1);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
    background-color: transparent;
  }
}

/* 大单行特殊样式 */
.table-row.is-whale .td-amount {
  position: relative;
}

.table-row.is-whale .td-amount::before {
  content: '🐋';
  margin-right: 4px;
  font-size: 14px;
}
</style>

