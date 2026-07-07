<template>
  <!-- 顶部导航栏 - 居中标题（参考充值页面） -->
  <van-nav-bar
    :title="t('withdraw.title')"
    left-arrow
    @click-left="router.back()"
    fixed
    safe-area-inset-top
    class="app-sub-nav-bar"
  />

  <div class="withdraw-page">
    <!-- 地址输入区域 -->
    <div class="section address-section">
      <div class="section-title">{{ t('withdraw.addr') }}</div>
      <div class="address-input-wrapper">
        <van-field
          v-model="address"
          :placeholder="t('withdraw.addr_placeholder')"
          class="address-input"
          autocomplete="off"
        />
        <div class="address-actions">
          <van-icon name="qr" class="action-icon" @click="handleScan" />
          <van-icon name="description" class="action-icon" @click="handlePaste" />
        </div>
      </div>
    </div>

    <!-- 转账网络卡片 -->
    <div class="section network-section">
      <div class="section-title">{{ t('withdraw.net') }}</div>
      <div class="network-card selected">
        <div class="network-info">
          <span class="network-name">TRC20</span>
        </div>
        <van-icon name="success" class="check-icon" />
      </div>
    </div>

    <!-- 金额输入区域 - 视觉中心 -->
    <div class="section amount-section">
      <div class="amount-header">
        <div class="section-title">{{ t('withdraw.amount') }}</div>
        <div class="available-balance">
          {{ t('withdraw.available_balance') }} <span class="balance-number">{{ formatBalance(balance) }} USDT</span>
        </div>
      </div>
      <div class="amount-input-wrapper">
        <van-field
          v-model.number="amount"
          type="number"
          :placeholder="t('withdraw.amount_placeholder')"
          class="amount-input"
          inputmode="decimal"
          min="0"
          autocomplete="off"
        />
        <button class="max-link" @click="handleMax">{{ t('withdraw.max') }}</button>
      </div>
    </div>

    <!-- 费用明细 -->
    <div class="section summary-section">
      <div class="summary-row">
        <span class="summary-label">{{ t('withdraw.network_fee') }}</span>
        <span class="summary-value">{{ fee }} USDT</span>
      </div>
      <div class="summary-row highlight-row">
        <span class="summary-label">{{ t('withdraw.receive_amount') }}</span>
        <span class="summary-value highlight">{{ formatBalance(receiveAmount) }} USDT</span>
      </div>
    </div>

    <!-- 提现按钮 - 底部固定 -->
    <div class="button-container">
      <van-button
        block
        class="withdraw-btn"
        :class="{ ready: canSubmit, inactive: !canSubmit }"
        :loading="isLoading"
        :disabled="isLoading"
        :aria-disabled="!canSubmit"
        @click="handleWithdraw"
      >
        {{ t('withdraw.withdraw_btn') }}
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { withdraw } from '@/api/wallet';

const router = useRouter();
const { t } = useI18n();
const assetStore = useAssetStore();

// 变量绑定
const address = ref('');
const amount = ref(0);
const isLoading = ref(false);

// 常量：网络手续费（USDT）
const fee = 1;

// 可用余额（从 Store 获取）
const balance = computed(() => {
  return assetStore.usdtBalance || 0;
});

// 计算属性：实际到账金额 = 提现金额 - 手续费
const receiveAmount = computed(() => {
  const numAmount = Number(amount.value) || 0;
  const result = numAmount - fee;
  // 如果小于0则显示0.00
  return Math.max(0, result);
});

const canSubmit = computed(() => {
  const numAmount = Number(amount.value) || 0;
  return Boolean(address.value.trim()) && numAmount > fee && numAmount <= balance.value;
});

const getWithdrawValidationMessage = () => {
  const numAmount = Number(amount.value) || 0;
  if (!address.value.trim()) return t('withdraw.addr_required');
  if (!numAmount || numAmount <= 0) return t('withdraw.amount_invalid');
  if (numAmount <= fee) return t('withdraw.amount_below_fee');
  if (numAmount > balance.value) {
    return `${t('withdraw.insufficient_balance')}，${t('withdraw.available_balance')} ${formatBalance(balance.value)} USDT`;
  }
  return '';
};

// 格式化余额显示
const formatBalance = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// 最大按钮：填入全部可用余额
const handleMax = () => {
  amount.value = balance.value;
};

// 模拟扫码功能
const handleScan = async () => {
  // 第一步：显示"正在启动摄像头..."提示（使用 i18n）
  showToast({
    message: t('withdraw.scanning'),
    duration: 1500
  });

  // 第二步：延迟 1.5 秒（模拟扫描耗时）
  await new Promise(resolve => setTimeout(resolve, 1500));

  // 第三步：预设的 TRC20 钱包地址
  const mockAddress = 'TF1rp5qLqJ3vT1xYX5iQwVqJz8vK9mN2pQ';

  // 第四步：自动填入地址到输入框
  address.value = mockAddress;

  // 第五步：弹出成功提示（使用 i18n）
  showToast({
    message: t('withdraw.scan_success'),
    icon: 'success',
    duration: 2000
  });
};

// 粘贴地址
const handlePaste = async () => {
  try {
    const text = await navigator.clipboard.readText();
    address.value = text;
    showToast({
      message: t('withdraw.address_pasted'),
      icon: 'success',
      duration: 1500
    });
  } catch (err) {
    showToast({
      message: t('withdraw.paste_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 提现处理函数
const handleWithdraw = async () => {
  const validationMessage = getWithdrawValidationMessage();
  if (validationMessage) {
    showToast({
      message: validationMessage,
      icon: 'warning',
      duration: 2200
    });
    return;
  }

  // 第一步：前端严查
  if (!address.value || address.value.trim() === '') {
    showToast({
      message: t('withdraw.addr_required') || '请输入提现地址',
      icon: 'warning',
      duration: 2000
    });
    return;
  }

  const numAmount = Number(amount.value);
  
  // 校验：金额必须大于 0
  if (!numAmount || numAmount <= 0) {
    showToast({
      message: t('withdraw.amount_invalid'),
      icon: 'warning',
      duration: 2000
    });
    return;
  }

  // 校验：金额必须大于手续费
  if (numAmount <= fee) {
    showToast({
      message: t('withdraw.amount_below_fee') || '提现金额无法覆盖手续费',
      icon: 'warning',
      duration: 2000
    });
    return;
  }

  // 校验：余额是否充足
  if (numAmount > balance.value) {
    showToast({
      message: `${t('withdraw.insufficient_balance')}，${t('withdraw.available_balance')}：${formatBalance(balance.value)} USDT`,
      icon: 'warning',
      duration: 3000
    });
    return;
  }

  // 第二步：调用 API
  isLoading.value = true;

  try {
    // 调用 withdraw API
    // 注释：虽然后端 Mock 接口暂不记录目标地址，但前端必须校验用户已填写，以保证仿真体验
    const response = await withdraw({
      amount: numAmount,
      currency: 'USDT'
    });

    // 第三步：成功反馈
    // 注意：axios 返回的是 response 对象，后端数据在 response.data 中
    // 后端返回格式：{ code: 200, message: "...", data: {...} }
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({
        message: t('withdraw.submitted'),
        icon: 'success',
        duration: 3000
      });

      // 关键：调用 assetStore.initData() 刷新余额，确保界面显示的余额减少
      await assetStore.initData();

      // 清空输入框
      address.value = '';
      amount.value = 0;

      console.log('✅ 提现成功，余额已刷新');
    } else {
      throw new Error(responseData?.message || t('withdraw.failed'));
    }
  } catch (error) {
    // 失败反馈：显示后端错误信息
    console.error('❌ 提现失败:', error);

    let errorMessage = t('withdraw.failed') || '提现失败，请重试';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }

    showToast({
      message: errorMessage,
      icon: 'fail',
      duration: 3000
    });
  } finally {
    // 结束：重置加载状态
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 参考充值页面风格 - 黑金风格 */

.withdraw-page {
  background:
    linear-gradient(180deg, rgb(var(--color-primary-rgb) / 0.07) 0, rgb(var(--color-primary-rgb) / 0) 190px),
    var(--color-surface-1);
  min-height: 100vh;
  padding: 20px 16px;
  padding-top: 64px;
  padding-bottom: 100px;
  color: var(--color-text-primary);
  box-sizing: border-box;
}

/* NavBar 统一 */
.app-sub-nav-bar {
  background: var(--color-surface-2) !important;
  border-bottom: 1px solid var(--color-border) !important;
  height: 52px !important;
}
:deep(.van-nav-bar__arrow),
:deep(.van-nav-bar .van-icon-arrow-left) {
  color: var(--color-accent) !important;
  font-size: 28px !important;
  font-weight: bold !important;
}
:deep(.van-nav-bar__title) {
  color: var(--color-text-primary) !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}
:deep(.van-nav-bar__left) {
  padding: 0 12px;
  min-width: 60px;
}

/* 卡片样式（参考充值页面） */
.section {
  background: var(--color-surface-2);
  border-radius: 16px;
  padding: 22px 24px;
  margin-bottom: 16px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary-hover);
  margin-bottom: 16px;
  letter-spacing: 0;
  font-weight: 800;
}

/* 地址输入框（参考充值页面样式） */
.address-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--color-bg-input);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  min-height: 56px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.address-input-wrapper:focus-within,
.amount-input-wrapper:focus-within {
  border-color: var(--color-primary-border);
  box-shadow: 0 0 0 3px var(--color-focus-ring);
}

.address-input {
  flex: 1;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

.address-input:focus-within,
.amount-input:focus-within {
  border-color: transparent !important;
  box-shadow: none !important;
}

:deep(.address-input.van-field),
:deep(.amount-input.van-field),
:deep(.address-input .van-cell),
:deep(.amount-input .van-cell) {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

:deep(.address-input .van-field__body),
:deep(.amount-input .van-field__body) {
  background: transparent !important;
  box-shadow: none !important;
}

:deep(.address-input .van-field__control) {
  color: var(--color-text-primary);
  font-size: 15px;
  padding: 0 20px;
  padding-right: 100px;
  background: transparent;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  letter-spacing: 0.3px;
}

:deep(.address-input .van-field__control::placeholder) {
  color: var(--color-text-secondary);
  opacity: 0.6;
}

.address-actions {
  position: absolute;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-icon {
  color: var(--color-text-muted); /* 默认灰色 */
  font-size: 20px;
  cursor: pointer; /* 鼠标变为手型 */
  transition: all 0.2s ease;
  padding: 4px;
}

.action-icon:hover {
  color: var(--color-brand-legacy); /* 悬停时变成金色 */
}

.action-icon:active {
  opacity: 0.6;
  transform: scale(0.95);
}

/* 网络卡片（参考充值页面） */
.network-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.network-card.selected {
  border-color: var(--color-primary-border);
  background: rgb(var(--color-brand-rgb) / 0.05);
  box-shadow: 0 0 0 3px rgb(var(--color-primary-rgb) / 0.08);
}

.network-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.network-name {
  font-size: 16px;
  color: var(--color-text-primary);
  font-weight: 600;
  letter-spacing: 0.3px;
}

.check-icon {
  color: var(--color-accent);
  font-size: 20px;
}

/* 金额输入区域 */
.amount-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.available-balance {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 400;
}

.balance-number {
  color: var(--color-text-primary);
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

.amount-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--color-bg-input);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  min-height: 72px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.amount-input {
  flex: 1;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

:deep(.amount-input .van-field__control) {
  color: var(--color-text-primary);
  font-size: 32px;
  padding: 20px;
  padding-right: 90px;
  background: transparent;
  font-family: 'DIN Alternate', 'Roboto', 'SF Pro Display', sans-serif;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  letter-spacing: -0.5px;
}

:deep(.amount-input .van-field__control::placeholder) {
  color: var(--color-text-secondary);
  opacity: 0.4;
  font-size: 32px;
}

.max-link {
  position: absolute;
  right: 20px;
  color: var(--color-accent);
  font-size: 14px;
  font-weight: 600;
  background: transparent;
  border: none;
  padding: 8px 0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, sans-serif;
}

.max-link:hover {
  opacity: 0.8;
}

.max-link:active {
  opacity: 0.6;
}

/* 费用明细 */
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.highlight-row {
  padding-top: 16px;
  margin-top: 8px;
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.08);
}

.summary-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 400;
}

.summary-value {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

.summary-value.highlight {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: -0.3px;
}

/* 提现按钮 */
.button-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
  background: rgb(var(--color-surface-2-rgb) / 0.96);
  border-top: 1px solid var(--color-border);
  box-shadow: 0 -8px 24px rgb(var(--color-shadow-rgb) / 0.08);
  z-index: 100;
}

.withdraw-btn {
  background: var(--color-surface-2) !important;
  color: var(--color-text-primary) !important;
  height: 50px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  border: 1px solid var(--color-border-strong) !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.5px !important;
  box-shadow: var(--shadow-md) !important;
}

.withdraw-btn:active:not(:disabled) {
  background: var(--color-surface-muted) !important;
  opacity: 1;
  transform: scale(0.98);
}

.withdraw-btn:disabled {
  background: var(--color-surface-muted) !important;
  color: var(--color-text-muted) !important;
  border-color: var(--color-border) !important;
  box-shadow: none !important;
  cursor: not-allowed !important;
}

.withdraw-btn.inactive:not(:disabled) {
  background: var(--color-surface-2) !important;
  color: var(--color-text-muted) !important;
  border-color: var(--color-border) !important;
  box-shadow: none !important;
}

.withdraw-btn.ready {
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-hover) 100%) !important;
  color: var(--color-text-on-accent) !important;
  border-color: rgb(var(--color-primary-rgb) / 0.48) !important;
  box-shadow: 0 10px 22px rgb(var(--color-primary-rgb) / 0.22) !important;
}

/* 自动填充样式处理 */
:deep(.address-input .van-field__control:-webkit-autofill),
:deep(.address-input .van-field__control:-webkit-autofill:hover),
:deep(.address-input .van-field__control:-webkit-autofill:focus),
:deep(.address-input .van-field__control:-webkit-autofill:active),
:deep(.amount-input .van-field__control:-webkit-autofill),
:deep(.amount-input .van-field__control:-webkit-autofill:hover),
:deep(.amount-input .van-field__control:-webkit-autofill:focus),
:deep(.amount-input .van-field__control:-webkit-autofill:active) {
  -webkit-box-shadow: 0 0 0 1000px var(--color-bg-card) inset !important;
  -webkit-text-fill-color: var(--color-text-primary) !important;
  transition: background-color 5000s ease-in-out 0s;
}
</style>
