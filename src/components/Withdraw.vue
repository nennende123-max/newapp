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
          type="digit"
          :placeholder="t('withdraw.amount_placeholder')"
          class="amount-input"
          inputmode="decimal"
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
        :loading="isLoading"
        :disabled="isLoading || !address || !amount || amount <= 0"
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
  background: #000000;
  min-height: 100vh;
  padding: 16px;
  padding-top: 64px;
  padding-bottom: 100px;
  color: #fff;
  box-sizing: border-box;
}

/* NavBar 统一 */
.app-sub-nav-bar {
  background: #000000 !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
  height: 52px !important;
}
:deep(.van-nav-bar__arrow),
:deep(.van-nav-bar .van-icon-arrow-left) {
  color: #D4AF37 !important;
  font-size: 28px !important;
  font-weight: bold !important;
}
:deep(.van-nav-bar__title) {
  color: #D4AF37 !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}
:deep(.van-nav-bar__left) {
  padding: 0 12px;
  min-width: 60px;
}

/* 卡片样式（参考充值页面） */
.section {
  background: #141414;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 12px;
  border: 1px solid rgba(255,255,255,0.08);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #D4AF37;
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

/* 地址输入框（参考充值页面样式） */
.address-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #1C1C1E;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  min-height: 56px;
}

.address-input {
  flex: 1;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

:deep(.address-input .van-field__control) {
  color: #FFFFFF;
  font-size: 15px;
  padding: 0 20px;
  padding-right: 100px;
  background: transparent;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  letter-spacing: 0.3px;
}

:deep(.address-input .van-field__control::placeholder) {
  color: #8E8E93;
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
  color: #848E9C; /* 默认灰色 */
  font-size: 20px;
  cursor: pointer; /* 鼠标变为手型 */
  transition: all 0.2s ease;
  padding: 4px;
}

.action-icon:hover {
  color: #FCD535; /* 悬停时变成金色 */
}

.action-icon:active {
  opacity: 0.6;
  transform: scale(0.95);
}

/* 网络卡片（参考充值页面） */
.network-card {
  background: #1C1C1E;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.2s ease;
}

.network-card.selected {
  border-color: #D4AF37;
  background: rgba(212, 175, 55, 0.05);
}

.network-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.network-name {
  font-size: 16px;
  color: #FFFFFF;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.check-icon {
  color: #D4AF37;
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
  color: #8E8E93;
  font-weight: 400;
}

.balance-number {
  color: #FFFFFF;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

.amount-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #1C1C1E;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  min-height: 72px;
}

.amount-input {
  flex: 1;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

:deep(.amount-input .van-field__control) {
  color: #FFFFFF;
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
  color: #8E8E93;
  opacity: 0.4;
  font-size: 32px;
}

.max-link {
  position: absolute;
  right: 20px;
  color: #D4AF37;
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
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.summary-label {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 400;
}

.summary-value {
  font-size: 14px;
  color: #FFFFFF;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

.summary-value.highlight {
  font-size: 20px;
  font-weight: 700;
  color: #D4AF37;
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
  background: #000000;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
}

.withdraw-btn {
  background: #FCD535 !important;
  color: #000000 !important;
  height: 50px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  border: none !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.5px !important;
}

.withdraw-btn:active:not(:disabled) {
  opacity: 0.85;
  transform: scale(0.98);
}

.withdraw-btn:disabled {
  background: rgba(252, 213, 53, 0.3) !important;
  color: rgba(0, 0, 0, 0.4) !important;
  cursor: not-allowed !important;
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
  -webkit-box-shadow: 0 0 0 1000px #1C1C1E inset !important;
  -webkit-text-fill-color: #FFFFFF !important;
  transition: background-color 5000s ease-in-out 0s;
}
</style>
