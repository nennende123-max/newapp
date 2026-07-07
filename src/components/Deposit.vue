<template>
  <van-nav-bar
    :title="`充值 ${token}`"
    left-arrow
    @click-left="router.back()"
    fixed
    safe-area-inset-top
    class="app-sub-nav-bar"
  />

  <div class="dapp-page">
    <!-- 已连接钱包卡片 -->
    <div class="card wallet-card">
      <div class="wallet-head">
        <span class="wallet-label">充值来源钱包</span>
        <span class="wallet-status">
          <i class="dot"></i>已连接
        </span>
      </div>
      <div class="wallet-addr-row" @click="copyAddress">
        <span class="wallet-addr">{{ shortAddress }}</span>
        <van-icon name="records" class="copy-ic" />
      </div>
    </div>

    <!-- 选择网络 -->
    <div class="card">
      <div class="card-title">选择网络</div>
      <div class="network-grid">
        <button
          v-for="net in networks"
          :key="net.key"
          type="button"
          class="network-chip"
          :class="{ active: net.key === selectedNetworkKey }"
          @click="selectedNetworkKey = net.key"
        >
          {{ net.name }}
        </button>
      </div>
    </div>

    <!-- 金额输入 -->
    <div class="card">
      <div class="amount-head">
        <span class="card-title mb0">充值数量</span>
        <span class="balance-text">
          钱包余额 <b>{{ formatNum(walletBalance) }} {{ token }}</b>
        </span>
      </div>
      <div class="amount-input-row">
        <input
          v-model="amountInput"
          type="text"
          inputmode="decimal"
          class="amount-input"
          placeholder="0.00"
          @input="onAmountInput"
        />
        <span class="input-suffix">{{ token }}</span>
        <button type="button" class="max-btn" @click="fillMax">最大</button>
      </div>
      <p v-if="amountError" class="err-text">{{ amountError }}</p>
    </div>

    <!-- 费用 / 到账 -->
    <div class="card summary-card">
      <div class="summary-row">
        <span>网络费用 (Gas 预估)</span>
        <span class="val">{{ selectedNetwork.gasLabel }}</span>
      </div>
      <div class="summary-row highlight">
        <span>预计到账</span>
        <span class="val strong">{{ formatNum(receiveAmount) }} {{ token }}</span>
      </div>
    </div>

    <!-- 开发环境快捷入账（正式环境不显示） -->
    <div v-if="isDev" class="dev-hint">
      <span>开发模式：确认后将本地模拟入账，便于预览。</span>
    </div>

    <div class="bottom-bar">
      <van-button
        block
        class="primary-btn"
        :class="{ disabled: !canSubmit }"
        :loading="isLoading"
        :disabled="isLoading || !canSubmit"
        @click="handleDeposit"
      >
        确认充值
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { showToast } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { assetNetworks, walletOnChainBalanceMock } from '@/data/assetMock';

defineOptions({ name: 'Deposit' });

const router = useRouter();
const route = useRoute();
const assetStore = useAssetStore();
const isDev = import.meta.env.DEV;

const token = computed(() => String(route.query.token || 'USDT').toUpperCase());

const networks = assetNetworks;
const selectedNetworkKey = ref(networks[0].key);
const selectedNetwork = computed(
  () => networks.find((n) => n.key === selectedNetworkKey.value) || networks[0]
);

const amountInput = ref('');
const isLoading = ref(false);

// 当前连接钱包地址（充值来源）
const walletAddress = computed(() => assetStore.walletAddress || '');
const shortAddress = computed(() => shorten(walletAddress.value));

// 链上钱包余额（Mock）
// TODO: 接入真实链上余额查询（按当前连接钱包地址 + 网络 + 币种读取）
const walletBalance = computed(() => walletOnChainBalanceMock[token.value] ?? 0);

const numericAmount = computed(() => Number(amountInput.value) || 0);
const receiveAmount = computed(() => numericAmount.value);

const amountError = computed(() => {
  if (!amountInput.value) return '';
  if (numericAmount.value <= 0) return '请输入有效金额';
  if (numericAmount.value > walletBalance.value) return '钱包余额不足';
  return '';
});

const canSubmit = computed(
  () => numericAmount.value > 0 && numericAmount.value <= walletBalance.value
);

function shorten(addr) {
  if (!addr) return '';
  if (addr.length <= 12) return addr;
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}

function formatNum(value) {
  return Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

// 仅允许数字与单个小数点，禁止负数
function onAmountInput() {
  let v = String(amountInput.value).replace(/[^\d.]/g, '');
  const firstDot = v.indexOf('.');
  if (firstDot !== -1) {
    v = v.slice(0, firstDot + 1) + v.slice(firstDot + 1).replace(/\./g, '');
  }
  amountInput.value = v;
}

function fillMax() {
  amountInput.value = String(walletBalance.value);
}

async function copyAddress() {
  if (!walletAddress.value) return;
  try {
    await navigator.clipboard.writeText(walletAddress.value);
    showToast({ message: '钱包地址已复制', icon: 'success', duration: 1500 });
  } catch (err) {
    showToast({ message: '复制失败', duration: 1500 });
  }
}

const handleDeposit = async () => {
  if (!canSubmit.value || isLoading.value) return;

  isLoading.value = true;
  try {
    // TODO: 接入真实链上合约充值流程：
    //   1) 若为 ERC20/USDT，先 approve 授权额度
    //   2) approve 完成后再调用合约 deposit 方法
    //   3) 校验当前钱包网络与所选网络一致，否则提示切换网络
    // 当前为 mock：本地模拟入账（开发/前端 only 模式下真实更新余额）
    await assetStore.deposit(numericAmount.value, token.value);
    showToast({ message: '充值请求已提交', icon: 'success', duration: 2500 });
    amountInput.value = '';
    setTimeout(() => router.back(), 800);
  } catch (error) {
    showToast({
      message: error?.message || '充值失败，请重试',
      icon: 'fail',
      duration: 2500
    });
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  // 直接访问 URL 且未连接钱包时，回到首页并提示
  if (!assetStore.isWalletConnected) {
    showToast({ message: '请先连接钱包', icon: 'warning' });
    router.replace('/');
  }
});
</script>

<style scoped>
.dapp-page {
  min-height: 100vh;
  padding: 64px 16px 96px;
  box-sizing: border-box;
  background: var(--color-surface-1);
  color: var(--color-text-primary);
}

/* NavBar 统一 */
.app-sub-nav-bar {
  background: var(--color-surface-2) !important;
  border-bottom: 1px solid var(--color-border) !important;
  height: 52px !important;
}
:deep(.van-nav-bar__arrow),
:deep(.van-nav-bar .van-icon-arrow-left) {
  color: var(--color-text-primary) !important;
  font-size: 22px !important;
}
:deep(.van-nav-bar__title) {
  color: var(--color-text-primary) !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}

.card {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}
.card-title.mb0 { margin-bottom: 0; }

/* 已连接钱包卡片 */
.wallet-card { padding: 16px; }
.wallet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.wallet-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}
.wallet-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-success);
}
.wallet-status .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-success);
}
.wallet-addr-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border);
  cursor: pointer;
}
.wallet-addr {
  font-size: 15px;
  font-weight: 700;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-primary);
}
.copy-ic { color: var(--color-text-secondary); font-size: 18px; }

/* 网络选择 */
.network-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.network-chip {
  height: 44px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-1);
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.network-chip.active {
  background: rgb(var(--color-primary-rgb) / 0.12);
  border-color: var(--color-primary);
  color: var(--color-primary-hover);
  font-weight: 800;
}

/* 金额输入 */
.amount-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.balance-text { font-size: 12px; color: var(--color-text-secondary); }
.balance-text b { color: var(--color-text-primary); font-variant-numeric: tabular-nums; }

.amount-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--color-surface-1);
  border: 1px solid var(--color-border);
}
.amount-input-row:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}
.amount-input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}
.amount-input::placeholder { color: var(--color-text-muted); }
.input-suffix { font-size: 14px; font-weight: 700; color: var(--color-text-secondary); }
.max-btn {
  border: none;
  background: transparent;
  color: var(--color-primary-hover);
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}
.err-text { margin: 8px 2px 0; font-size: 12px; color: var(--color-danger); }

/* 费用 / 到账 */
.summary-card { padding: 6px 16px; }
.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}
.summary-row .val { color: var(--color-text-primary); font-weight: 600; font-variant-numeric: tabular-nums; }
.summary-row.highlight {
  border-top: 1px solid var(--color-border);
}
.summary-row.highlight .val.strong {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-primary-hover);
}

.dev-hint {
  font-size: 11px;
  color: var(--color-text-muted);
  padding: 0 4px 4px;
}

/* 底部按钮 */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom));
  background: var(--color-surface-2);
  border-top: 1px solid var(--color-border);
  z-index: 20;
}
.primary-btn {
  height: 50px !important;
  border: none !important;
  border-radius: 12px !important;
  font-size: 16px !important;
  font-weight: 800 !important;
  color: var(--color-text-on-accent) !important;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-hover) 100%) !important;
  box-shadow: 0 8px 20px rgb(var(--color-primary-rgb) / 0.24) !important;
}
.primary-btn.disabled {
  background: var(--color-surface-muted) !important;
  color: var(--color-text-muted) !important;
  box-shadow: none !important;
}
</style>
