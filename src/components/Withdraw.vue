<template>
  <van-nav-bar
    :title="t('withdraw.title')"
    left-arrow
    @click-left="router.back()"
    fixed
    safe-area-inset-top
    class="withdraw-nav-bar"
  >
    <template #right>
      <van-icon name="bill-o" class="history-icon" @click="showHistory" />
    </template>
  </van-nav-bar>

  <div class="withdraw-page">
    <!-- 币种选择栏 -->
    <div class="section coin-selector" @click="showCoinSheet = true">
      <div class="coin-selector-content">
        <div class="coin-info">
          <span class="coin-icon">{{ getCoinIcon(selectedCoin) }}</span>
          <span class="coin-name">{{ selectedCoin }}</span>
        </div>
        <van-icon name="arrow" size="14" color="#848E9C" />
      </div>
    </div>

    <!-- 网络选择标签 -->
    <div class="section network-tabs">
      <div
        class="network-tab"
        :class="{ active: selectedNetwork === 'TRC20' }"
        @click="handleNetworkSelect('TRC20')"
      >
        {{ t('withdraw.network_trc20') }}
      </div>
      <div
        class="network-tab"
        :class="{ active: selectedNetwork === 'ERC20' }"
        @click="handleNetworkSelect('ERC20')"
      >
        {{ t('withdraw.network_erc20') }}
      </div>
      <div
        class="network-tab"
        :class="{ active: selectedNetwork === 'BSC' }"
        @click="handleNetworkSelect('BSC')"
      >
        {{ t('withdraw.network_bsc') }}
      </div>
    </div>
    <!-- 网络提示信息 -->
    <div class="network-tip-section">
      <span class="network-tip">预计到账: {{ currentNetworkTime }}</span>
    </div>

    <!-- 地址输入卡片 -->
    <div class="section address-card">
      <div class="card-label">{{ t('withdraw.addr') }}</div>
      <div class="address-input-wrapper">
        <van-field
          v-model="withdrawAddress"
          :placeholder="t('withdraw.addr_placeholder')"
          class="address-field"
          autocomplete="off"
        />
        <div class="address-icons">
          <van-icon name="gold-coin-o" class="wallet-icon" @click.stop="handleWalletFill" />
          <van-icon name="description" class="paste-icon" @click="handlePaste" />
        </div>
      </div>
    </div>

    <!-- 金额输入卡片 -->
    <div class="section amount-card">
      <div class="balance-display">
        <span class="balance-label">{{ t('withdraw.available_balance') }}</span>
        <span class="balance-value">{{ formatBalance(availableBalance) }} {{ selectedCoin }}</span>
      </div>
      <div class="amount-input-wrapper">
        <van-field
          v-model="withdrawAmount"
          type="digit"
          :placeholder="amountPlaceholder"
          class="amount-field"
          inputmode="decimal"
          autocomplete="off"
        />
        <span class="max-button" @click="handleMax">{{ t('withdraw.max') }}</span>
      </div>
    </div>

    <!-- 摘要部分 -->
    <div class="section summary-card">
      <div class="summary-row">
        <span class="summary-label">{{ t('withdraw.network_fee') }}</span>
        <span 
          class="summary-value fee-value" 
          :class="{ 
            'fee-high': selectedNetwork === 'ERC20',
            'fee-highlight': feeHighlight 
          }"
        >
          {{ selectedCoin === 'USDT' ? networkFee : '0.001' }} {{ selectedCoin }}
        </span>
      </div>
      <div class="summary-row receive-row">
        <span class="summary-label">{{ t('withdraw.receive_amount') }}</span>
        <span class="summary-value receive-amount">{{ formatBalance(receiveAmount) }} {{ selectedCoin }}</span>
      </div>
    </div>

    <!-- 警告提示 -->
    <div class="warning-tips">
      <div class="tip-item">
        <span class="tip-dot"></span>
        <span>{{ t('withdraw.tip1') }}</span>
      </div>
      <div class="tip-item">
        <span class="tip-dot"></span>
        <span>{{ t('withdraw.tip2') }}</span>
      </div>
      <div class="tip-item">
        <span class="tip-dot"></span>
        <span>{{ t('withdraw.tip3') }}</span>
      </div>
    </div>

    <!-- 提现按钮 -->
    <van-button
      block
      class="withdraw-button"
      :disabled="isButtonDisabled"
      @click="handleWithdraw"
    >
      {{ t('withdraw.withdraw_btn') }}
    </van-button>

    <!-- 币种选择 ActionSheet -->
    <van-action-sheet
      v-model:show="showCoinSheet"
      :actions="coinOptions"
      @select="handleCoinSelect"
      cancel-text="取消"
      title="选择币种"
    />

    <!-- 密码验证弹窗 -->
    <van-dialog
      v-model:show="showPasswordDialog"
      title="资金密码验证"
      show-cancel-button
      @confirm="handlePasswordConfirm"
      @cancel="showPasswordDialog = false"
      class="password-dialog"
    >
      <div class="password-input-wrapper">
        <van-field
          v-model="passwordInput"
          type="password"
          placeholder="请输入6位资金密码"
          maxlength="6"
          class="password-field"
          autocomplete="off"
        />
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, ActionSheet, Dialog } from 'vant';
import { useAssetStore } from '@/stores/assets';

const router = useRouter();
const { t } = useI18n();
const assetStore = useAssetStore();

// 网络配置数据
const networkConfig = {
  TRC20: { fee: 1, min: 10, time: '约 3 分钟', color: '#FCD535' },
  ERC20: { fee: 5, min: 20, time: '约 10 分钟', color: '#EAECEF' }, // 以太坊贵且慢
  BSC:   { fee: 0.5, min: 10, time: '约 2 分钟', color: '#F0B90B' }
};

// 数据
const withdrawAddress = ref('');
const withdrawAmount = ref('');
const selectedNetwork = ref('TRC20');
const selectedCoin = ref('USDT');
const showCoinSheet = ref(false);
const showPasswordDialog = ref(false);
const passwordInput = ref('');
const feeHighlight = ref(false); // 用于手续费高亮动画

// 网络手续费（响应式）
const networkFee = computed(() => {
  return networkConfig[selectedNetwork.value].fee;
});

// 当前网络预计到账时间
const currentNetworkTime = computed(() => {
  return networkConfig[selectedNetwork.value].time;
});

// 最小提现金额
const minWithdrawAmount = computed(() => {
  return networkConfig[selectedNetwork.value].min;
});

// 金额输入框 placeholder
const amountPlaceholder = computed(() => {
  return `最小提现 ${minWithdrawAmount.value} ${selectedCoin.value}`;
});

// Computed properties
const availableBalance = computed(() => {
  if (selectedCoin.value === 'USDT') {
    return assetStore.usdtBalance;
  } else {
    return assetStore.getHolding(selectedCoin.value) || 0;
  }
});

// 获取有余额的币种列表
const coinOptions = computed(() => {
  const coins = [];
  
  // 添加 USDT（如果有余额）
  if (assetStore.usdtBalance > 0) {
    coins.push({ name: 'USDT', value: 'USDT' });
  }
  
  // 添加其他有余额的币种
  Object.keys(assetStore.holdings).forEach(symbol => {
    const balance = assetStore.getHolding(symbol);
    if (balance > 0) {
      coins.push({ name: symbol, value: symbol });
    }
  });
  
  return coins;
});

// 获取币种图标（简单实现，可根据需要扩展）
const getCoinIcon = (coin) => {
  const icons = {
    'USDT': '💵',
    'BTC': '₿',
    'ETH': 'Ξ',
    'BNB': '🔶',
    'SOL': '◎',
    'DOGE': '🐕',
    'TRX': 'T',
    'BEAT': 'B',
    'AIC': 'A'
  };
  return icons[coin] || '💰';
};

const receiveAmount = computed(() => {
  const amount = parseFloat(withdrawAmount.value) || 0;
  // 根据币种调整手续费（USDT 固定 1，其他币种可能不同）
  const fee = selectedCoin.value === 'USDT' ? networkFee.value : 0.001;
  return Math.max(0, amount - fee);
});

const isButtonDisabled = computed(() => {
  return !withdrawAddress.value || !withdrawAmount.value || parseFloat(withdrawAmount.value) <= 0;
});

// 监听网络切换，触发手续费高亮动画
watch(selectedNetwork, (newNetwork, oldNetwork) => {
  // 如果切换到 ERC20（手续费最高），触发高亮动画
  if (newNetwork === 'ERC20' && oldNetwork !== 'ERC20') {
    feeHighlight.value = true;
    setTimeout(() => {
      feeHighlight.value = false;
    }, 1000); // 1秒后取消高亮
  }
  
  // 更新最小提现金额提示（通过 computed 自动更新）
});

// Functions
const handleNetworkSelect = (network) => {
  selectedNetwork.value = network;
  // 可以添加触觉反馈或音效（如果需要）
};

const handleMax = () => {
  withdrawAmount.value = availableBalance.value.toString();
};

const handlePaste = async () => {
  try {
    const text = await navigator.clipboard.readText();
    withdrawAddress.value = text;
    showToast({ message: t('withdraw.address_pasted'), duration: 1000 });
  } catch (err) {
    showToast({ message: t('withdraw.paste_failed'), duration: 1000 });
  }
};

// 选择币种
const handleCoinSelect = (action) => {
  selectedCoin.value = action.value;
  showCoinSheet.value = false;
  // 重置网络选择和输入金额
  selectedNetwork.value = 'TRC20';
  withdrawAmount.value = '';
};

// 钱包地址快捷填入
const handleWalletFill = () => {
  if (assetStore.isWalletConnected && assetStore.walletAddress) {
    withdrawAddress.value = assetStore.walletAddress;
    showToast({ message: '已自动填入钱包地址', duration: 1500 });
  } else {
    showToast({ message: '请先连接钱包', duration: 2000 });
  }
};

// 密码验证确认
const handlePasswordConfirm = async () => {
  // 验证密码长度（模拟，任意6位即可）
  if (passwordInput.value.length !== 6) {
    showToast({ message: '请输入6位资金密码', duration: 2000 });
    return;
  }
  
  showPasswordDialog.value = false;
  
  // 执行提现逻辑
  try {
    const amount = parseFloat(withdrawAmount.value);
    
    // 根据币种调用不同的提现逻辑
    if (selectedCoin.value === 'USDT') {
      const success = await assetStore.withdraw(amount);
      if (success) {
        showToast({ 
          message: '提现成功', 
          icon: 'success' 
        });
        setTimeout(() => {
          router.push('/me');
        }, 1000);
      } else {
        showToast({ message: '余额不足', duration: 2000 });
      }
    } else {
      // 其他币种的提现逻辑（从持仓中扣除）
      const currentHolding = assetStore.getHolding(selectedCoin.value);
      if (currentHolding < amount) {
        showToast({ message: '余额不足', duration: 2000 });
        return;
      }
      
      // 模拟提现成功（实际应该调用 API）
      assetStore.holdings[selectedCoin.value] = (assetStore.holdings[selectedCoin.value] || 0) - amount;
      if (assetStore.holdings[selectedCoin.value] <= 0) {
        delete assetStore.holdings[selectedCoin.value];
      }
      
      showToast({ 
        message: '提现成功', 
        icon: 'success' 
      });
      setTimeout(() => {
        router.push('/me');
      }, 1000);
    }
    
    // 清空密码输入
    passwordInput.value = '';
  } catch (error) {
    console.error('Withdraw error:', error);
    showToast({ message: '提现失败，请重试', duration: 2000 });
  }
};

const handleWithdraw = () => {
  if (isButtonDisabled.value) {
    return;
  }
  
  // 弹出密码验证弹窗
  showPasswordDialog.value = true;
  passwordInput.value = '';
};

const showHistory = () => {
  showToast({ message: t('withdraw.history_coming_soon'), duration: 2000 });
};

const formatBalance = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};
</script>

<style scoped>
.withdraw-page {
  background: #0E0E0E;
  min-height: 100vh;
  padding: 16px;
  padding-top: 64px;
  padding-bottom: 100px;
  color: #FFFFFF;
  box-sizing: border-box;
}

/* NavBar */
.withdraw-nav-bar {
  background: #0E0E0E !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
  height: 52px !important;
}
:deep(.van-nav-bar__arrow),
:deep(.van-nav-bar .van-icon-arrow-left) {
  color: #FCD535 !important;
  font-size: 28px !important;
  font-weight: bold !important;
}
:deep(.van-nav-bar__title) {
  color: #FCD535 !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}
:deep(.van-nav-bar__left) {
  padding: 0 12px;
  min-width: 60px;
}
.history-icon {
  color: #FCD535;
  font-size: 20px;
  padding: 0 16px;
  cursor: pointer;
  transition: opacity 0.3s ease;
}
.history-icon:active {
  opacity: 0.7;
}

/* 卡片通用样式 */
.section {
  background: #1C1C1E;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,0.08);
}

/* 币种选择栏 */
.coin-selector {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.coin-selector:active {
  background-color: #252A32;
}

.coin-selector-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.coin-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.coin-icon {
  font-size: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(252, 213, 53, 0.1);
  border-radius: 8px;
}

.coin-name {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
  font-family: sans-serif;
}

/* 网络标签选择器 */
.network-tabs {
  display: flex;
  gap: 12px;
  padding: 20px;
}
.network-tab {
  flex: 1;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #8E8E93;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: sans-serif;
}
.network-tab.active {
  background: #FCD535;
  color: #0E0E0E;
  border-color: #FCD535;
}
.network-tab.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.network-tab:not(.disabled):active {
  opacity: 0.8;
  transform: scale(0.98);
}

/* 网络提示信息 */
.network-tip-section {
  padding: 0 20px 8px 20px;
  margin-top: -8px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.network-tip {
  font-size: 12px;
  color: #8E8E93;
  font-family: sans-serif;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.network-tip::before {
  content: '⏱️';
  font-size: 12px;
}

/* 卡片标签 */
.card-label {
  font-size: 13px;
  color: #8E8E93;
  margin-bottom: 12px;
  font-weight: 500;
  font-family: sans-serif;
}

/* 地址输入 */
.address-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.address-field {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  height: 56px;
  border: 1px solid rgba(255,255,255,0.08);
  flex: 1;
}
:deep(.address-field .van-field__control) {
  color: #FFFFFF;
  font-size: 15px;
  padding: 0 16px;
  background: transparent;
  font-family: sans-serif;
}
:deep(.address-field .van-field__control::placeholder) {
  color: #8E8E93;
}
.address-icons {
  position: absolute;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.wallet-icon {
  color: #FCD535;
  font-size: 20px;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.wallet-icon:active {
  opacity: 0.7;
}

.paste-icon {
  color: #FCD535;
  font-size: 20px;
  cursor: pointer;
  transition: opacity 0.3s ease;
}
.paste-icon:active {
  opacity: 0.7;
}

/* 金额输入 */
.balance-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.balance-label {
  font-size: 13px;
  color: #8E8E93;
  font-family: sans-serif;
}
.balance-value {
  font-size: 15px;
  color: #FFFFFF;
  font-weight: 600;
  font-family: 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
}
.amount-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.amount-field {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  height: 56px;
  border: 1px solid rgba(255,255,255,0.08);
  flex: 1;
}
:deep(.amount-field .van-field__control) {
  color: #FFFFFF;
  font-size: 16px;
  padding: 0 16px;
  background: transparent;
  font-family: 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
}
:deep(.amount-field .van-field__control::placeholder) {
  color: #8E8E93;
}
.max-button {
  position: absolute;
  right: 16px;
  color: #FCD535;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  transition: opacity 0.3s ease;
  font-family: sans-serif;
}
.max-button:active {
  opacity: 0.7;
}

/* 摘要部分 */
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.summary-row:last-child {
  margin-bottom: 0;
}
.receive-row {
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.08);
  margin-top: 12px;
}
.summary-label {
  font-size: 14px;
  color: #8E8E93;
  font-family: sans-serif;
}
.summary-value {
  font-size: 15px;
  color: #FFFFFF;
  font-weight: 500;
  font-family: 'DIN Alternate', sans-serif;
  font-variant-numeric: tabular-nums;
  transition: all 0.3s ease;
}

/* ERC20 手续费高亮样式 */
.fee-value.fee-high {
  color: #F6465D;
  font-weight: 700;
  font-size: 16px;
}

/* 手续费高亮动画 */
.fee-value.fee-highlight {
  animation: feePulse 0.6s ease-in-out;
}

@keyframes feePulse {
  0% {
    transform: scale(1);
    color: #FFFFFF;
  }
  50% {
    transform: scale(1.15);
    color: #F6465D;
    text-shadow: 0 0 8px rgba(246, 70, 93, 0.5);
  }
  100% {
    transform: scale(1);
    color: #F6465D;
  }
}
.receive-amount {
  font-size: 18px;
  font-weight: 600;
  color: #FCD535;
}

/* 警告提示 */
.warning-tips {
  margin-bottom: 24px;
  padding: 0 4px;
}
.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #8E8E93;
  line-height: 1.5;
  font-family: sans-serif;
}
.tip-item:last-child {
  margin-bottom: 0;
}
.tip-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #F6465D;
  margin-top: 6px;
  flex-shrink: 0;
}

/* 针对自动填充状态的特殊处理 */
:deep(.address-field .van-field__control:-webkit-autofill),
:deep(.address-field .van-field__control:-webkit-autofill:hover),
:deep(.address-field .van-field__control:-webkit-autofill:focus),
:deep(.address-field .van-field__control:-webkit-autofill:active),
:deep(.amount-field .van-field__control:-webkit-autofill),
:deep(.amount-field .van-field__control:-webkit-autofill:hover),
:deep(.amount-field .van-field__control:-webkit-autofill:focus),
:deep(.amount-field .van-field__control:-webkit-autofill:active) {
  /* 使用内阴影覆盖原本的白色背景，颜色设置为 #1C1C1E (卡片背景色) */
  -webkit-box-shadow: 0 0 0 1000px #1C1C1E inset !important;
  /* 强制文字颜色为白色 */
  -webkit-text-fill-color: #FFFFFF !important;
  /* 保持透明度过渡，防止闪烁 */
  transition: background-color 5000s ease-in-out 0s;
}

/* 提现按钮 */
.withdraw-button {
  background: #FCD535;
  color: #0E0E0E;
  height: 56px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  transition: all 0.3s ease;
  font-family: sans-serif;
}
.withdraw-button:active:not(:disabled) {
  opacity: 0.8;
}
.withdraw-button:disabled {
  background: rgba(252, 213, 53, 0.3);
  color: rgba(14, 14, 14, 0.5);
  cursor: not-allowed;
}

/* 密码验证弹窗 */
:deep(.password-dialog .van-dialog) {
  background: #1C1C1E;
  border-radius: 16px;
}

:deep(.password-dialog .van-dialog__header) {
  color: #FFFFFF;
  font-weight: 600;
  padding: 20px 20px 16px;
}

:deep(.password-dialog .van-dialog__content) {
  padding: 0 20px 20px;
}

.password-input-wrapper {
  margin-top: 8px;
}

.password-field {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
}

:deep(.password-field .van-field__control) {
  color: #FFFFFF;
  font-size: 16px;
  padding: 12px 16px;
  background: transparent;
  font-family: 'Roboto Mono', monospace;
  letter-spacing: 4px;
  text-align: center;
}

:deep(.password-field .van-field__control::placeholder) {
  color: #8E8E93;
  letter-spacing: 0;
}

:deep(.password-dialog .van-dialog__footer) {
  padding: 16px 20px 20px;
}

:deep(.password-dialog .van-button) {
  background: #FCD535;
  color: #0E0E0E;
  border: none;
  font-weight: 600;
}

:deep(.password-dialog .van-button--default) {
  background: rgba(255,255,255,0.05);
  color: #FFFFFF;
}
</style>

