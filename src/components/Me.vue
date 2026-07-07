<template>
  <div class="me-page">
    <!-- 顶部固定区域：头像 + 用户名 + 功能图标 -->
    <div class="top-nav">
      <div class="user-profile" @click="router.push('/profile')">
        <div class="avatar-circle">
          <van-icon name="manager" color="#000" />
        </div>
        <span class="username">User_8829</span>
      </div>
      <div class="top-icons">
        <van-icon name="service-o" size="20" class="icon-right" @click="goToSupport" />
        <van-icon
          :name="isAmountHidden ? 'closed-eye' : 'eye-o'"
          size="20"
          class="icon-right"
          @click="toggleAmountHidden"
        />
        <van-icon name="setting-o" size="20" class="icon-right" @click="goToSettings" />
      </div>
    </div>

    <!-- 钱包连接横幅 -->
    <div class="wallet-banner">
      <div class="wallet-line">
        <van-icon name="checked" class="wallet-check" />
        <span class="wallet-text">钱包已连接</span>
        <span class="wallet-switch" @click="handleSwitchWallet">切换钱包</span>
      </div>
      <div class="wallet-addr-row" @click="copyAddress">
        <span class="wallet-addr-label">钱包地址</span>
        <span class="wallet-addr">{{ shortAddress }}</span>
        <van-icon name="records" class="copy-icon" />
      </div>
    </div>

    <!-- 资产 Tab -->
    <van-tabs
      v-model:active="activeTab"
      :ellipsis="false"
      background="transparent"
      title-active-color="#0F172A"
      title-inactive-color="#64748B"
      line-width="20px"
      line-height="3px"
      color="#F0B90B"
      :border="false"
      class="asset-tabs"
    >
      <van-tab title="总览" />
      <van-tab title="现货" />
      <van-tab title="理财" />
      <van-tab title="合约" />
      <van-tab title="IEO" />
      <van-tab title="股票" />
    </van-tabs>

    <!-- Tab 0: 总览 -->
    <div v-if="activeTab === 0" class="overview-content">
      <!-- 预估总资产 -->
      <section class="summary-card">
        <div class="summary-head">
          <span class="summary-label">预估总资产</span>
          <div class="unit-switch">
            <button
              v-for="u in units"
              :key="u"
              type="button"
              class="unit-chip"
              :class="{ active: activeUnit === u }"
              @click="activeUnit = u"
            >{{ u }}</button>
          </div>
        </div>
        <div class="summary-total">{{ displayTotal }}</div>
        <div class="summary-sub">
          <span v-if="!isAmountHidden">≈ {{ approxLine }}</span>
          <span v-else>≈ ****</span>
        </div>
        <div class="summary-pnl">
          <span class="pnl-cap">今日收益</span>
          <span :class="overview.todayPnl >= 0 ? 'up' : 'down'">
            {{ signedMoney(overview.todayPnl) }}
            <em v-if="!isAmountHidden">{{ signedPercent(overview.todayPnlPercent) }}</em>
          </span>
        </div>
      </section>

      <!-- 操作按钮：充值 / 提现 / 划转 -->
      <section class="action-grid">
        <button class="action-btn primary" type="button" @click="handleDeposit">充值</button>
        <button class="action-btn dark" type="button" @click="handleWithdraw">提现</button>
        <button class="action-btn light" type="button" @click="openTransfer('spot')">划转</button>
      </section>

      <!-- 邀请好友赚奖励 -->
      <div class="referral-card" @click="toReferral">
        <div class="referral-visual">
          <van-icon name="friends-o" size="22" />
        </div>
        <div class="referral-info">
          <div class="ref-kicker">好友交易</div>
          <div class="ref-title">邀请好友赚奖励</div>
          <div class="ref-desc">好友交易，你最高可获得 <span class="highlight">40%</span> 返佣</div>
        </div>
        <div class="referral-action">
          <span class="earned-label">已赚取</span>
          <span class="earned-text">${{ formatNumber(overview.inviteEarned, 2) }}</span>
          <van-icon name="arrow" size="16" />
        </div>
      </div>

      <!-- 资产分布：5 个账户卡片 -->
      <section class="allocation-section">
        <div class="allocation-title">资产分布</div>
        <div class="allocation-list">
          <div
            v-for="acc in accounts"
            :key="acc.key"
            class="account-card"
            @click="goToAccount(acc)"
          >
            <div class="account-top">
              <div class="account-icon" :class="'ic-' + acc.color">
                <van-icon :name="acc.icon" size="22" />
              </div>
              <div class="account-name-box">
                <span class="account-name">{{ acc.name }}</span>
                <span class="account-desc">{{ acc.desc }}</span>
              </div>
              <div class="account-total">
                <span class="account-value">{{ money(acc.value) }}</span>
                <van-icon name="arrow" size="14" color="#94A3B8" />
              </div>
            </div>
            <div class="account-metrics">
              <div class="metric" v-for="(m, i) in acc.metrics" :key="i">
                <span class="metric-label">{{ m.label }}</span>
                <span class="metric-value" :class="m.tone">{{ metricText(m) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Tab 1: 现货（保留原有资产列表） -->
    <div v-else-if="activeTab === 1" class="spot-content">
      <div class="tools-bar">
        <div class="convert-bnb">
          <span>{{ $t('assets.convert_small') }}</span>
          <van-icon name="arrow" />
        </div>
        <div class="history-btn" @click="goToHistory">
          <van-icon name="bill-o" />
          <span>{{ $t('history.title') }}</span>
        </div>
      </div>

      <div class="search-bar">
        <div class="hide-small" @click="toggleHideSmall">
          <div class="radio-circle" :class="{ checked: hideSmallBalances }"></div>
          <span>{{ $t('assets.hide_zero') }}</span>
        </div>
        <van-field
          v-model="searchQuery"
          :placeholder="$t('assets.search_placeholder')"
          class="search-field"
          left-icon="search"
        />
      </div>

      <div class="coin-list">
        <div v-if="!assetStore.isWalletConnected && filteredAndSortedAssets.length === 0" class="empty-state">
          <van-icon name="wallet-o" size="48" color="#94A3B8" />
          <p class="empty-text">连接钱包后查看资产</p>
        </div>
        <div
          v-else
          class="coin-item"
          v-for="asset in filteredAndSortedAssets"
          :key="asset.symbol"
        >
          <div class="coin-left">
            <div class="coin-icon" :class="asset.symbol.toLowerCase()">
              <img v-if="asset.iconUrl" :src="asset.iconUrl" :alt="asset.symbol" />
              <span v-else>{{ asset.symbol[0] }}</span>
            </div>
            <div class="coin-info">
              <span class="coin-name">{{ asset.symbol }}</span>
              <span class="coin-fullname">{{ getFullName(asset.symbol) }}</span>
            </div>
          </div>
          <div class="coin-right">
            <span class="coin-balance">{{ displayBalance(asset.balance, asset.symbol) }}</span>
            <span class="coin-price">{{ displayValue(asset.value) }} USDT</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 2: 理财 -->
    <div v-else-if="activeTab === 2" class="earn-content">
      <EarnList />
    </div>

    <!-- Tab 3: 合约 -->
    <div v-else-if="activeTab === 3" class="module-content">
      <section class="summary-card">
        <div class="summary-label">合约账户权益 (USDT)</div>
        <div class="summary-total">{{ money(futures.total) }}</div>
        <div class="mini-stats">
          <div class="mini">
            <span class="mini-label">可用保证金</span>
            <span class="mini-value">{{ money(futures.availableMargin) }}</span>
          </div>
          <div class="mini">
            <span class="mini-label">持仓盈亏</span>
            <span class="mini-value" :class="futures.positionPnl >= 0 ? 'up' : 'down'">{{ signedMoney(futures.positionPnl) }}</span>
          </div>
        </div>
      </section>

      <section class="list-card">
        <div class="list-title">当前持仓</div>
        <div class="pos-row" v-for="p in futures.positions" :key="p.symbol">
          <div class="pos-left">
            <span class="pos-symbol">{{ p.symbol }}</span>
            <span class="pos-tags">
              <em class="tag" :class="p.side === '做多' ? 'long' : 'short'">{{ p.side }}</em>
              <em class="tag lev">{{ p.leverage }}</em>
            </span>
          </div>
          <div class="pos-right">
            <span class="pos-pnl" :class="p.pnl >= 0 ? 'up' : 'down'">{{ signedMoney(p.pnl) }}</span>
            <span class="pos-sub" :class="p.pnl >= 0 ? 'up' : 'down'">{{ signedPercent(p.pnlPercent) }}</span>
          </div>
        </div>
      </section>

      <button class="wide-btn" type="button" @click="router.push('/trade')">前往合约交易</button>
    </div>

    <!-- Tab 4: IEO -->
    <div v-else-if="activeTab === 4" class="module-content">
      <section class="summary-card">
        <div class="ieo-hero">
          <div class="ieo-stat">
            <span class="mini-label">待解锁资产</span>
            <span class="summary-total sm">{{ money(ieo.pendingUnlock) }}</span>
          </div>
          <div class="ieo-stat">
            <span class="mini-label">已中签资产</span>
            <span class="summary-total sm">{{ money(ieo.wonAssets) }}</span>
          </div>
        </div>
      </section>

      <section class="list-card">
        <div class="list-title">IEO 项目仓位</div>
        <div class="ieo-row" v-for="p in ieo.projects" :key="p.id">
          <div class="ieo-left">
            <span class="ieo-name">{{ p.name }}</span>
            <span class="ieo-sub">
              <template v-if="p.status === 'won'">中签 {{ money(p.amount, 0) }}</template>
              <template v-else-if="p.status === 'pending'">认购 {{ money(p.amount, 0) }}</template>
              <template v-else>已退款 {{ money(p.refund) }}</template>
            </span>
          </div>
          <span class="status-badge" :class="p.status">{{ ieoStatusLabel(p.status) }}</span>
        </div>
      </section>

      <button class="wide-btn" type="button" @click="router.push('/asset/ieo')">查看 IEO 详情</button>
    </div>

    <!-- Tab 5: 股票 -->
    <div v-else-if="activeTab === 5" class="module-content">
      <section class="summary-card">
        <div class="summary-label">股票总资产 (USDT)</div>
        <div class="summary-total">{{ money(stock.total) }}</div>
        <div class="summary-pnl">
          <span class="pnl-cap">今日收益</span>
          <span :class="stock.todayPnl >= 0 ? 'up' : 'down'">
            {{ signedMoney(stock.todayPnl) }}
            <em v-if="!isAmountHidden">{{ signedPercent(stock.todayPnlPercent) }}</em>
          </span>
        </div>
      </section>

      <section class="list-card">
        <div class="list-title">股票持仓</div>
        <div class="pos-row" v-for="s in stock.holdings" :key="s.symbol">
          <div class="pos-left">
            <span class="pos-symbol">{{ s.symbol }}</span>
            <span class="ieo-sub">{{ money(s.amount, 0) }} 股</span>
          </div>
          <div class="pos-right">
            <span class="pos-pnl">{{ money(s.value) }}</span>
            <span class="pos-sub" :class="s.changePercent >= 0 ? 'up' : 'down'">{{ signedPercent(s.changePercent) }}</span>
          </div>
        </div>
      </section>

      <button class="wide-btn" type="button" @click="router.push('/asset/stock')">查看股票账户</button>
    </div>

    <!-- 划转弹窗 -->
    <TransferModal v-model:show="showTransfer" :default-from="transferFrom" />
  </div>
</template>

<script setup>
import { ref, computed, onActivated } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { formatAssetAmount, formatNumber } from '@/utils/format';
import { useAmountPrivacy } from '@/composables/useAmountPrivacy';
import { useAssetActions } from '@/composables/useAssetActions';
import {
  walletMock,
  overviewMock,
  accountsMock,
  futuresSummaryMock,
  ieoDetailMock,
  stockDetailMock
} from '@/data/assetMock';
import EarnList from './EarnList.vue';
import TransferModal from './TransferModal.vue';

defineOptions({ name: 'Me' });

const router = useRouter();
const route = useRoute();
const assetStore = useAssetStore();
const { t } = useI18n();
const { isAmountHidden, toggleAmountHidden } = useAmountPrivacy();
const { openDeposit, openWithdraw } = useAssetActions();

const activeTab = ref(0);
const hideSmallBalances = ref(false);
const searchQuery = ref('');

// 划转弹窗
const showTransfer = ref(false);
const transferFrom = ref('spot');

// Mock 数据（结构清晰，后续可接真实接口）
const overview = overviewMock;
const accounts = accountsMock;
const futures = futuresSummaryMock;
const ieo = ieoDetailMock;
const stock = stockDetailMock;

// 单位切换
const units = ['USDT', 'BTC', 'CNY'];
const activeUnit = ref('USDT');

// ---------- 金额格式化 / 脱敏 ----------
const money = (value, digits = 2) => (isAmountHidden.value ? '****' : formatNumber(value, digits));

const signedMoney = (value, digits = 2) => {
  if (isAmountHidden.value) return '****';
  const sign = value >= 0 ? '+' : '-';
  return `${sign}$${formatNumber(Math.abs(value), digits)}`;
};

const signedPercent = (value) => `${value >= 0 ? '+' : ''}${formatNumber(value, 2)}%`;

const metricText = (m) => {
  if (isAmountHidden.value) return '****';
  if (m.signed) {
    const sign = m.value >= 0 ? '+' : '-';
    return `${sign}${formatNumber(Math.abs(m.value), 2)}`;
  }
  return formatNumber(m.value, 2);
};

const displayTotal = computed(() => {
  if (isAmountHidden.value) return '****';
  if (activeUnit.value === 'BTC') return `${formatNumber(overview.totalBtc, 4)} BTC`;
  if (activeUnit.value === 'CNY') return `¥${formatNumber(overview.totalUsdt * overview.cnyRate, 2)}`;
  return `$${formatNumber(overview.totalUsdt, 2)}`;
});

const approxLine = computed(() => {
  if (activeUnit.value === 'BTC') return `$${formatNumber(overview.totalUsdt, 2)}`;
  return `${formatNumber(overview.totalBtc, 4)} BTC`;
});

// ---------- 钱包 ----------
const walletAddress = computed(() => assetStore.walletAddress || walletMock.address);

const shortAddress = computed(() => {
  const addr = walletAddress.value || '';
  if (addr.length <= 12) return addr;
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
});

const copyAddress = async () => {
  const addr = walletAddress.value;
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(addr);
    } else {
      const el = document.createElement('textarea');
      el.value = addr;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    }
    showToast('钱包地址已复制');
  } catch (error) {
    showToast('复制失败');
  }
};

const handleSwitchWallet = () => {
  showToast('切换钱包');
  // TODO: 接入真实钱包切换逻辑
};

// ---------- 现货资产列表（保留原有逻辑，隐私改为全局） ----------
const formatCurrency = (value, decimals = 2) => {
  const number = Number(value) || 0;
  return number.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

const filteredAndSortedAssets = computed(() => {
  const assets = [];
  const priceMap = assetStore.priceMap || {};
  const userAssets = assetStore.userAssets || {};
  const holdings = assetStore.holdings || {};
  const symbols = new Set([...Object.keys(holdings), ...Object.keys(userAssets)]);

  if ((assetStore.usdtBalance || 0) > 0 || userAssets.USDT !== undefined) {
    symbols.add('USDT');
  }

  symbols.forEach((rawSymbol) => {
    const symbol = String(rawSymbol).replace(/_frozen$/i, '').toUpperCase();
    if (!symbol || symbol.endsWith('_FROZEN')) return;

    const balance = symbol === 'USDT'
      ? (assetStore.usdtBalance || userAssets.USDT || 0)
      : (assetStore.getHolding?.(symbol) || holdings[symbol] || userAssets[symbol] || 0);
    const value = balance * (priceMap[symbol] || (symbol === 'USDT' ? 1 : 0));

    if (hideSmallBalances.value && balance <= 0) return;
    if (searchQuery.value && !symbol.includes(searchQuery.value.trim().toUpperCase())) return;

    assets.push({ symbol, balance, value });
  });

  return assets.sort((a, b) => b.value - a.value || a.symbol.localeCompare(b.symbol));
});

const toggleHideSmall = () => {
  hideSmallBalances.value = !hideSmallBalances.value;
};

const displayBalance = (balance, symbol) => {
  if (isAmountHidden.value) return '****';
  return formatAssetAmount ? formatAssetAmount(balance, symbol) : formatCurrency(balance, 6);
};

const displayValue = (value) => {
  if (isAmountHidden.value) return '****';
  return formatCurrency(value);
};

const getFullName = (symbol) => {
  const names = {
    USDT: 'Tether USD',
    USDC: 'USD Coin',
    FDUSD: 'First Digital USD',
    BTC: 'Bitcoin',
    ETH: 'Ethereum',
    BNB: 'BNB',
    BEAT: 'BEAT',
    ZEC: 'Zcash',
    AIC: 'AIC',
    MEME: 'Meme'
  };
  return names[symbol] || symbol;
};

// ---------- 导航 ----------
const goToAccount = (acc) => {
  if (acc.route) {
    router.push(acc.route);
  } else if (typeof acc.tab === 'number') {
    activeTab.value = acc.tab;
  }
};

const openTransfer = (from) => {
  transferFrom.value = from || 'spot';
  showTransfer.value = true;
};

const handleDeposit = () => openDeposit('USDT');
const handleWithdraw = () => openWithdraw('USDT');
const goToHistory = () => router.push('/history');
const goToSupport = () => router.push('/support');
const goToSettings = () => router.push('/settings');
const toReferral = () => router.push('/referral');

const ieoStatusLabel = (status) => {
  if (status === 'won') return '已中签';
  if (status === 'pending') return '待中签';
  return '未中签';
};

const applyTabFromQuery = () => {
  const map = { overview: 0, spot: 1, earn: 2, futures: 3, ieo: 4, stock: 5 };
  const tab = route.query.tab;
  if (tab && map[tab] !== undefined) {
    activeTab.value = map[tab];
  }
};

const initializeData = async () => {
  if (typeof assetStore.initData === 'function') {
    await assetStore.initData();
  }
};

onActivated(async () => {
  applyTabFromQuery();
  await initializeData();
});
</script>

<style scoped>
.me-page {
  min-height: 100vh;
  background: #f4f7fb;
  color: #1e293b;
  padding-bottom: 88px;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, 'Segoe UI', Arial, Roboto, 'PingFang SC', 'Microsoft Yahei', sans-serif;
}

/* 顶部导航 */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px 10px;
  background: #ffffff;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  background: #fcd535;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.username {
  font-weight: 700;
  font-size: 16px;
  color: #0f172a;
}

.top-icons {
  display: flex;
  gap: 18px;
  color: #334155;
}

.icon-right {
  cursor: pointer;
}

/* 钱包横幅 */
.wallet-banner {
  margin: 0 16px 12px;
  padding: 12px 14px;
  background: #eafaf2;
  border: 1px solid #bdecd4;
  border-radius: 12px;
}

.wallet-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wallet-check {
  color: #10b981;
  font-size: 16px;
}

.wallet-text {
  font-size: 13px;
  font-weight: 700;
  color: #0f7a52;
  flex: 1;
}

.wallet-switch {
  font-size: 12px;
  color: #0f7a52;
  font-weight: 600;
  cursor: pointer;
  opacity: 0.8;
}

.wallet-addr-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  cursor: pointer;
}

.wallet-addr-label {
  font-size: 12px;
  color: #6b8e7d;
}

.wallet-addr {
  font-size: 12px;
  color: #0f172a;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.copy-icon {
  font-size: 14px;
  color: #0f7a52;
}

/* Tabs */
.asset-tabs {
  background: #ffffff;
  margin-bottom: 12px;
}

:deep(.asset-tabs .van-tabs__wrap) {
  height: 46px;
}

:deep(.asset-tabs .van-tab) {
  font-size: 15px;
  font-weight: 600;
  padding: 0 14px;
}

:deep(.asset-tabs .van-tab--active) {
  font-weight: 800;
}

/* 通用 up / down */
.up { color: #00b976; }
.down { color: #ef4444; }

/* 总览内容 */
.overview-content {
  padding: 0 16px 24px;
}

.module-content {
  padding: 0 16px 24px;
}

/* 预估总资产卡片 */
.summary-card {
  padding: 18px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  margin-bottom: 14px;
}

.summary-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.summary-label {
  font-size: 13px;
  color: #64748b;
}

.unit-switch {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 999px;
  padding: 2px;
}

.unit-chip {
  border: none;
  background: transparent;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
}

.unit-chip.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.12);
}

.summary-total {
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.summary-total.sm {
  font-size: 22px;
}

.summary-sub {
  margin-top: 4px;
  font-size: 13px;
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.summary-pnl {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pnl-cap {
  color: #94a3b8;
  font-weight: 500;
}

.summary-pnl em {
  font-style: normal;
  margin-left: 6px;
}

.mini-stats {
  display: flex;
  gap: 16px;
  margin-top: 14px;
}

.mini {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mini-label {
  font-size: 12px;
  color: #64748b;
}

.mini-value {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.ieo-hero {
  display: flex;
  gap: 16px;
}

.ieo-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 操作按钮 */
.action-grid {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}

.action-btn {
  flex: 1;
  height: 48px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.action-btn.primary { background: #fcd535; color: #111827; }
.action-btn.dark { background: #29313d; color: #ffffff; }
.action-btn.light { background: #ffffff; color: #334155; border: 1px solid #e2e8f0; }
.action-btn:active { opacity: 0.85; }

/* 邀请卡片 */
.referral-card {
  position: relative;
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 18px;
  border-radius: 14px;
  overflow: hidden;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 55%, #f8fafc 100%);
  border: 1px solid #f3d48a;
  box-shadow: 0 12px 26px rgba(180, 126, 13, 0.12);
  cursor: pointer;
}

.referral-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  color: #111827;
  background: linear-gradient(135deg, #fcd535 0%, #f0b90b 100%);
}

.referral-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.ref-kicker { color: #b7791f; font-size: 11px; font-weight: 800; }
.ref-title { color: #111827; font-size: 15px; font-weight: 800; }
.ref-desc { color: #64748b; font-size: 12px; }
.ref-desc .highlight { color: #d97706; font-weight: 800; }

.referral-action {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  min-width: 78px;
}

.earned-label { color: #94a3b8; font-size: 11px; font-weight: 600; }

.earned-text {
  padding: 4px 8px;
  color: #b7791f;
  font-size: 12px;
  font-weight: 800;
  background: #fff4d6;
  border: 1px solid #f3d48a;
  border-radius: 999px;
}

.referral-action .van-icon { color: #b7791f; }

/* 资产分布 */
.allocation-section { margin-top: 4px; }

.allocation-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
  padding: 0 2px;
}

.allocation-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.account-card {
  background: #ffffff;
  border: 1px solid #e6ebf2;
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.account-card:active { transform: scale(0.99); background: #f8fafc; }

.account-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.account-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.ic-spot { background: linear-gradient(135deg, #fcd535 0%, #f0b90b 100%); color: #7a5b00; }
.ic-earn { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); }
.ic-futures { background: linear-gradient(135deg, #3b82f6 0%, #f97316 100%); }
.ic-ieo { background: linear-gradient(135deg, #ff6b6b 0%, #ef4444 100%); }
.ic-stock { background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%); }

.account-name-box {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.account-name { font-size: 15px; font-weight: 700; color: #0f172a; }
.account-desc { font-size: 12px; color: #94a3b8; }

.account-total {
  display: flex;
  align-items: center;
  gap: 4px;
}

.account-value {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
  font-variant-numeric: tabular-nums;
}

.account-metrics {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.metric {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label { font-size: 11px; color: #94a3b8; }

.metric-value {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  font-variant-numeric: tabular-nums;
}

.metric-value.up { color: #00b976; }
.metric-value.down { color: #ef4444; }

/* 列表卡片（合约/IEO/股票） */
.list-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
  margin-bottom: 14px;
}

.list-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 8px;
}

.pos-row, .ieo-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.pos-row:last-child, .ieo-row:last-child { border-bottom: none; }

.pos-left { display: flex; flex-direction: column; gap: 6px; }
.pos-symbol { font-size: 15px; font-weight: 700; }
.pos-tags { display: flex; gap: 6px; }

.tag {
  font-style: normal;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
}
.tag.long { background: #e6f9f1; color: #00b976; }
.tag.short { background: #fdecec; color: #ef4444; }
.tag.lev { background: #fff7e0; color: #b7791f; }

.pos-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.pos-pnl { font-size: 15px; font-weight: 800; font-variant-numeric: tabular-nums; }
.pos-sub { font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; }

.ieo-left { display: flex; flex-direction: column; gap: 4px; }
.ieo-name { font-size: 14px; font-weight: 700; }
.ieo-sub { font-size: 12px; color: #94a3b8; }

.status-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.status-badge.won { background: #e6f9f1; color: #00b976; }
.status-badge.pending { background: #fff3e0; color: #f59e0b; }
.status-badge.failed { background: #f1f5f9; color: #94a3b8; }

.wide-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 12px;
  background: #fcd535;
  color: #111827;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

/* 现货 Tab */
.spot-content { padding-bottom: 8px; }

.tools-bar {
  padding: 0 16px;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.convert-bnb {
  background: #ffffff;
  border: 1px solid #e6ebf2;
  padding: 10px 12px;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #334155;
  font-size: 13px;
  flex: 1;
}

.history-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #b7791f;
  cursor: pointer;
  padding: 10px 14px;
  background: #fff7e0;
  border-radius: 10px;
  white-space: nowrap;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  margin-bottom: 14px;
  gap: 12px;
}

.hide-small {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.radio-circle {
  width: 16px;
  height: 16px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  position: relative;
}

.radio-circle.checked {
  border-color: #f0b90b;
  background: #f0b90b;
}

.radio-circle.checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  background: #ffffff;
  border-radius: 50%;
}

.search-field {
  flex: 1;
  background: #ffffff;
  border: 1px solid #e6ebf2;
  border-radius: 10px;
  height: 40px;
}

:deep(.search-field .van-field__control) {
  color: #1e293b;
  font-size: 14px;
  background: transparent;
}

:deep(.search-field .van-field__control::placeholder) { color: #94a3b8; }
:deep(.search-field .van-field__left-icon) { color: #94a3b8; }

.coin-list {
  display: flex;
  flex-direction: column;
  margin: 0 16px;
  background: #ffffff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state .van-icon { margin-bottom: 16px; opacity: 0.6; }
.empty-text { color: #94a3b8; font-size: 14px; margin: 0; }

.coin-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
}
.coin-item:last-child { border-bottom: none; }

.coin-left { display: flex; align-items: center; gap: 12px; }

.coin-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
  color: #ffffff;
  overflow: hidden;
}

.coin-icon img { width: 100%; height: 100%; object-fit: cover; }
.coin-icon.usdt { background: #26a17b; }
.coin-icon.btc { background: #f7931a; }
.coin-icon.eth { background: #627eea; }
.coin-icon.beat { background: #ff6b6b; }
.coin-icon.zec { background: #ecb244; }
.coin-icon.aic { background: #4ecdc4; }
.coin-icon.meme { background: #95e1d3; }

.coin-info { display: flex; flex-direction: column; gap: 4px; }
.coin-name { font-size: 16px; font-weight: 600; color: #0f172a; }
.coin-fullname { font-size: 12px; color: #94a3b8; }

.coin-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.coin-balance { font-size: 16px; color: #0f172a; font-weight: 600; font-variant-numeric: tabular-nums; }
.coin-price { font-size: 12px; color: #94a3b8; font-variant-numeric: tabular-nums; }

/* 理财 Tab */
.earn-content { padding: 0; width: 100%; }
:deep(.van-empty), :deep(.van-empty__description) { color: #94a3b8; }

/* =====================================================================
   深色模式适配 —— 「我的/资产」页此前为硬编码浅色，深色下重映射为主题变量
   （绿/红/金等语义色保持不变）
   ===================================================================== */
:global(html[data-theme='dark']) .me-page {
  background: var(--color-surface-1) !important;
  color: var(--color-text-primary) !important;
}

/* 白色卡片 / 面板 → 深色表面 */
:global(html[data-theme='dark']) .me-page .top-nav,
:global(html[data-theme='dark']) .me-page .asset-tabs,
:global(html[data-theme='dark']) .me-page .summary-card,
:global(html[data-theme='dark']) .me-page .account-card,
:global(html[data-theme='dark']) .me-page .list-card,
:global(html[data-theme='dark']) .me-page .convert-bnb,
:global(html[data-theme='dark']) .me-page .search-field,
:global(html[data-theme='dark']) .me-page .coin-list {
  background: var(--color-surface-2) !important;
  border-color: var(--color-border) !important;
  box-shadow: none !important;
}

/* 主文字 */
:global(html[data-theme='dark']) .me-page .username,
:global(html[data-theme='dark']) .me-page .summary-total,
:global(html[data-theme='dark']) .me-page .account-value,
:global(html[data-theme='dark']) .me-page .account-name,
:global(html[data-theme='dark']) .me-page .allocation-title,
:global(html[data-theme='dark']) .me-page .list-title,
:global(html[data-theme='dark']) .me-page .pos-symbol,
:global(html[data-theme='dark']) .me-page .ieo-name,
:global(html[data-theme='dark']) .me-page .coin-name,
:global(html[data-theme='dark']) .me-page .coin-balance,
:global(html[data-theme='dark']) .me-page .mini-value {
  color: var(--color-text-primary) !important;
}

/* 次级文字 */
:global(html[data-theme='dark']) .me-page .top-icons,
:global(html[data-theme='dark']) .me-page .summary-label,
:global(html[data-theme='dark']) .me-page .summary-sub,
:global(html[data-theme='dark']) .me-page .mini-label,
:global(html[data-theme='dark']) .me-page .metric-value:not(.up):not(.down),
:global(html[data-theme='dark']) .me-page .convert-bnb,
:global(html[data-theme='dark']) .me-page .hide-small,
:global(html[data-theme='dark']) .me-page .unit-chip:not(.active) {
  color: var(--color-text-secondary) !important;
}

/* 弱化文字 */
:global(html[data-theme='dark']) .me-page .pnl-cap,
:global(html[data-theme='dark']) .me-page .earned-label,
:global(html[data-theme='dark']) .me-page .account-desc,
:global(html[data-theme='dark']) .me-page .metric-label,
:global(html[data-theme='dark']) .me-page .ieo-sub,
:global(html[data-theme='dark']) .me-page .coin-fullname,
:global(html[data-theme='dark']) .me-page .coin-price,
:global(html[data-theme='dark']) .me-page .empty-text {
  color: var(--color-text-muted) !important;
}

/* 分隔线 / 边框 */
:global(html[data-theme='dark']) .me-page .account-metrics,
:global(html[data-theme='dark']) .me-page .pos-row,
:global(html[data-theme='dark']) .me-page .ieo-row,
:global(html[data-theme='dark']) .me-page .coin-item {
  border-color: var(--color-border) !important;
}

/* 单位切换分段 */
:global(html[data-theme='dark']) .me-page .unit-switch {
  background: var(--color-surface-1) !important;
}
:global(html[data-theme='dark']) .me-page .unit-chip.active {
  background: var(--color-surface-2) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

/* 卡片按下态 */
:global(html[data-theme='dark']) .me-page .account-card:active {
  background: var(--color-surface-1) !important;
}

/* 浅色操作按钮 */
:global(html[data-theme='dark']) .me-page .action-btn.light {
  background: var(--color-surface-2) !important;
  color: var(--color-text-primary) !important;
  border-color: var(--color-border) !important;
}

/* 钱包横幅（保留绿色语义，降低明度） */
:global(html[data-theme='dark']) .me-page .wallet-banner {
  background: rgb(16 185 129 / 0.12) !important;
  border-color: rgb(16 185 129 / 0.28) !important;
}
:global(html[data-theme='dark']) .me-page .wallet-text,
:global(html[data-theme='dark']) .me-page .wallet-switch,
:global(html[data-theme='dark']) .me-page .copy-icon {
  color: #34d399 !important;
}
:global(html[data-theme='dark']) .me-page .wallet-addr-label {
  color: var(--color-text-muted) !important;
}
:global(html[data-theme='dark']) .me-page .wallet-addr {
  color: var(--color-text-primary) !important;
}

/* 邀请卡片（深色金调） */
:global(html[data-theme='dark']) .me-page .referral-card {
  background: linear-gradient(135deg, rgb(252 213 53 / 0.10) 0%, var(--color-surface-2) 60%) !important;
  border-color: rgb(240 185 11 / 0.28) !important;
  box-shadow: none !important;
}
:global(html[data-theme='dark']) .me-page .ref-title {
  color: var(--color-text-primary) !important;
}
:global(html[data-theme='dark']) .me-page .ref-desc {
  color: var(--color-text-secondary) !important;
}
:global(html[data-theme='dark']) .me-page .earned-text {
  background: rgb(240 185 11 / 0.14) !important;
  border-color: rgb(240 185 11 / 0.28) !important;
}

/* 失败/未中签标签 */
:global(html[data-theme='dark']) .me-page .status-badge.failed {
  background: var(--color-surface-muted) !important;
  color: var(--color-text-muted) !important;
}

/* 历史记录 / 金调按钮 */
:global(html[data-theme='dark']) .me-page .history-btn {
  background: rgb(240 185 11 / 0.14) !important;
  color: #f0b24a !important;
}

/* 搜索框内文字 */
:global(html[data-theme='dark']) .me-page :deep(.search-field .van-field__control) {
  color: var(--color-text-primary) !important;
}
</style>
