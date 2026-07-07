<template>
  <div class="history-page">
    <!-- 顶部导航栏 -->
    <div class="history-header">
      <van-icon name="arrow-left" class="header-icon" @click="router.back()" />
      <div class="header-center">
        <span class="header-title">{{ t('history.title') }}</span>
      </div>
    </div>

    <!-- Tab 切换栏 -->
    <van-tabs 
      v-model:active="activeTab" 
      background="transparent" 
      title-active-color="var(--color-brand-legacy)" 
      title-inactive-color="var(--color-text-secondary)" 
      line-width="40px" 
      line-height="2px" 
      color="var(--color-brand-legacy)" 
      :border="false"
      class="history-tabs"
      @change="handleTabChange"
    >
      <van-tab :title="t('history.tab.deposit')"></van-tab>
      <van-tab :title="t('history.tab.withdraw')"></van-tab>
      <van-tab :title="t('history.tab.subscription')"></van-tab>
    </van-tabs>

    <!-- 内容区域 -->
    <div class="history-content">
      <!-- 空状态 -->
      <div v-if="filteredList.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-secondary)" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
            <rect x="6" y="6" width="12" height="12" rx="1" fill="none" stroke="var(--color-text-secondary)" stroke-width="1.5"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke="var(--color-text-secondary)" stroke-width="1.5"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke="var(--color-text-secondary)" stroke-width="1.5"/>
          </svg>
        </div>
        <p class="empty-text">{{ t('history.empty') }}</p>
      </div>

      <!-- 记录列表 -->
      <div v-else class="history-list">
        <div 
          v-for="item in filteredList" 
          :key="item.id"
          class="history-item"
          @click="handleItemClick(item)"
        >
          <div class="item-left">
            <div class="item-icon" :class="getItemIconClass(item.type)">
              <van-icon :name="getItemIcon(item.type)" />
            </div>
            <div class="item-info">
              <div class="item-title">{{ getItemTitle(item) }}</div>
              <div class="item-meta">
                <span class="item-time">{{ formatTime(item.time) }}</span>
                <span v-if="item.tx_id" class="item-hash">{{ formatHash(item.tx_id) }}</span>
                <span v-if="item.chain_name" class="item-chain">{{ item.chain_name }}</span>
              </div>
            </div>
          </div>
          <div class="item-right">
            <div class="item-amount" :class="getAmountClass(item)">
              {{ formatAmount(item) }}
            </div>
            <div class="item-status" :class="getStatusClass(item.status)">
              {{ getStatusText(item.status) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAssetStore } from '@/stores/assets';

const router = useRouter();
const { t } = useI18n();
const assetStore = useAssetStore();

// Tab 状态
const activeTab = ref(0);

// Tab 类型映射
const tabTypes = ['充值', '提现', '认购'];

// 当前 Tab 类型
const currentType = computed(() => tabTypes[activeTab.value]);

// 过滤后的列表
const filteredList = computed(() => {
  const allHistory = assetStore.transactionHistory || [];
  return allHistory.filter(item => {
    // 根据当前 Tab 过滤
    if (activeTab.value === 0) {
      return item.type === '充值';
    } else if (activeTab.value === 1) {
      return item.type === '提现';
    } else if (activeTab.value === 2) {
      return item.type === '认购';
    }
    return false;
  });
});

// Tab 切换处理
const handleTabChange = (index) => {
  activeTab.value = index;
};

// 获取项目标题
const getItemTitle = (item) => {
  if (item.type === '认购' && item.project_name) {
    return item.project_name;
  }
  // 根据类型返回对应的翻译
  const typeMap = {
    '充值': t('history.tab.deposit'),
    '提现': t('history.tab.withdraw'),
    '认购': t('history.tab.subscription')
  };
  return typeMap[item.type] || item.type || t('history.transaction');
};

// 获取图标
const getItemIcon = (type) => {
  const iconMap = {
    '充值': 'balance-list',
    '提现': 'balance-o',
    '认购': 'gem-o'
  };
  return iconMap[type] || 'bill-o';
};

// 获取图标样式类
const getItemIconClass = (type) => {
  const classMap = {
    '充值': 'icon-deposit',
    '提现': 'icon-withdraw',
    '认购': 'icon-subscription'
  };
  return classMap[type] || '';
};

// 格式化金额
const formatAmount = (item) => {
  if (item.type === '认购') {
    // 认购显示：消耗金额 + 获得代币数量
    const cost = item.total_cost || Math.abs(item.amount) || 0;
    const tokens = item.token_amount || 0;
    if (tokens > 0) {
      return `-${cost.toFixed(2)} USDT\n+${tokens.toFixed(2)} TOKEN`;
    }
    return `-${cost.toFixed(2)} USDT`;
  } else {
    // 充值/提现显示金额
    const amount = item.amount || 0;
    const sign = amount >= 0 ? '+' : '';
    return `${sign}${Math.abs(amount).toFixed(2)} USDT`;
  }
};

// 获取金额样式类
const getAmountClass = (item) => {
  if (item.type === '认购') {
    return 'amount-subscription';
  }
  const amount = item.amount || 0;
  return amount >= 0 ? 'amount-positive' : 'amount-negative';
};

// 获取状态样式类
const getStatusClass = (status) => {
  const statusMap = {
    '成功': 'status-success',
    '完成': 'status-success',
    '失败': 'status-failed',
    '進行中': 'status-pending',
    '审核中': 'status-pending',
    '进行中': 'status-pending'
  };
  return statusMap[status] || 'status-default';
};

// 获取状态显示文本
const getStatusText = (status) => {
  const statusMap = {
    '成功': t('history.status.success'),
    '完成': t('history.status.success'),
    '失败': t('history.status.failed'),
    '進行中': t('history.status.pending'),
    '审核中': t('history.status.pending'),
    '进行中': t('history.status.pending')
  };
  return statusMap[status] || status;
};

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  // 如果已经是格式化好的时间字符串，直接返回
  if (timeStr.includes(' ')) {
    return timeStr;
  }
  // 否则尝试格式化
  try {
    const date = new Date(timeStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  } catch {
    return timeStr;
  }
};

// 格式化哈希值
const formatHash = (hash) => {
  if (!hash) return '';
  if (hash.length <= 10) return hash;
  return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
};

// 点击项目
const handleItemClick = (item) => {
  // 可以在这里添加详情页跳转逻辑
  console.log('Item clicked:', item);
};
</script>

<style scoped>
.history-page {
  background-color: var(--color-bg);
  min-height: 100vh;
  color: var(--color-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
}

/* 顶部导航栏 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--color-bg-card);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-icon {
  font-size: 20px;
  color: var(--color-brand-legacy);
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.header-icon:active {
  opacity: 0.7;
}

.header-center {
  flex: 1;
  text-align: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* Tab 栏 */
.history-tabs {
  background-color: var(--color-bg);
  padding: 0 16px;
}

:deep(.van-tabs__wrap) {
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
}

:deep(.van-tab) {
  font-size: 15px;
  font-weight: 500;
  padding: 12px 0;
}

:deep(.van-tabs__line) {
  background-color: var(--color-brand-legacy);
  height: 2px;
}

/* 内容区域 */
.history-content {
  padding: 16px;
  min-height: calc(100vh - 120px);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 24px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 记录列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: var(--color-bg-card);
  border-radius: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.history-item:active {
  background-color: var(--color-surface-muted);
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.icon-deposit {
  background-color: rgb(var(--color-earn-rgb) / 0.15);
  color: var(--color-earn);
}

.icon-withdraw {
  background-color: rgb(var(--color-loss-rgb) / 0.15);
  color: var(--color-loss);
}

.icon-subscription {
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.15);
  color: var(--color-brand-legacy);
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.item-time {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

.item-hash {
  font-size: 11px;
  color: var(--color-text-muted);
  font-family: monospace;
  background-color: rgb(var(--color-border-rgb) / 0.05);
  padding: 2px 6px;
  border-radius: 4px;
}

.item-chain {
  font-size: 11px;
  color: var(--color-text-secondary);
  background-color: rgb(var(--color-border-rgb) / 0.05);
  padding: 2px 6px;
  border-radius: 4px;
}

.item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
  margin-left: 12px;
}

.item-amount {
  font-size: 15px;
  font-weight: 600;
  font-family: 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
  text-align: right;
  white-space: pre-line;
  line-height: 1.3;
}

.amount-positive {
  color: var(--color-earn);
}

.amount-negative {
  color: var(--color-loss);
}

.amount-subscription {
  color: var(--color-brand-legacy);
  font-size: 13px;
}

.item-status {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
}

.status-success {
  color: var(--color-earn);
  background-color: rgb(var(--color-earn-rgb) / 0.15);
}

.status-failed {
  color: var(--color-loss);
  background-color: rgb(var(--color-loss-rgb) / 0.15);
}

.status-pending {
  color: var(--color-brand-legacy);
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.15);
}

.status-default {
  color: var(--color-text-secondary);
  background-color: rgb(var(--color-border-rgb) / 0.05);
}
</style>