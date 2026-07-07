<template>
  <van-nav-bar
    :title="$t('profile.title')"
    left-arrow
    fixed
    :border="false"
    @click-left="router.back()"
    style="
      background-color: var(--color-bg);
      --van-nav-bar-background: var(--color-bg);
      --van-nav-bar-title-text-color: var(--color-brand-legacy);
      --van-nav-bar-icon-color: var(--color-brand-legacy);
    "
  />

  <div class="profile-page">
    <!-- 顶部 Header 区域 -->
    <div class="header-section">
      <div class="wallet-info">
        <div class="wallet-name-row">
          <van-icon name="phone-o" size="18" color="var(--color-text-primary)" />
          <span class="wallet-name">{{ walletName }}</span>
        </div>
        <div class="wallet-id-row">
          <span class="wallet-id-label">{{ $t('profile.uid') }}: </span>
          <span class="wallet-id-value tabular-nums">{{ displayWalletId }}</span>
          <van-icon 
            name="doc-on-doc-o" 
            size="16" 
            color="var(--color-brand-legacy)" 
            class="copy-icon"
            @click.stop="handleCopyWalletId"
          />
        </div>
      </div>
    </div>

    <!-- 核心功能开关区 -->
    <div class="settings-card">
      <div class="setting-item">
        <div class="setting-content">
          <div class="setting-title">{{ $t('profile.bnb_fee_discount') }}</div>
          <div class="setting-desc">{{ $t('profile.bnb_fee_discount_desc') }}</div>
        </div>
        <van-switch 
          :model-value="assetStore.useBNBForFees"
          @update:model-value="handleBNBFeesToggle"
          size="22" 
          active-color="var(--color-brand-legacy)" 
          inactive-color="var(--color-surface-muted)"
          class="switch-item"
        />
      </div>

      <div class="setting-item">
        <div class="setting-content">
          <div class="setting-title">{{ $t('profile.bnb_interest_discount') }}</div>
          <div class="setting-desc">{{ $t('profile.bnb_interest_discount_desc') }}</div>
        </div>
        <van-switch 
          :model-value="assetStore.useBNBForInterest"
          @update:model-value="handleBNBInterestToggle"
          size="22" 
          active-color="var(--color-brand-legacy)" 
          inactive-color="var(--color-surface-muted)"
          class="switch-item"
        />
      </div>

      <div class="setting-item">
        <div class="setting-content">
          <div class="setting-title">{{ $t('profile.google_auth') }}</div>
        </div>
        <van-switch 
          :model-value="googleAuthEnabled" 
          @update:model-value="handleGoogleAuthToggle"
          size="22" 
          active-color="var(--color-brand-legacy)" 
          inactive-color="var(--color-surface-muted)"
          class="switch-item"
        />
      </div>
    </div>

    <!-- 费率展示区 -->
    <div class="fee-card">
      <div class="fee-item">
        <div class="fee-label">{{ $t('profile.spot_fee_rate') }}</div>
        <div class="fee-value">
          <span class="fee-text tabular-nums">{{ $t('profile.spot_fee_maker') }} {{ formatFeeRate(assetStore.currentSpotFeeRate) }}%</span>
          <span class="fee-divider"> / </span>
          <span class="fee-text tabular-nums">{{ $t('profile.spot_fee_taker') }} {{ formatFeeRate(assetStore.currentSpotFeeRate) }}%</span>
        </div>
      </div>

      <div class="fee-item">
        <div class="fee-label">{{ $t('profile.futures_fee_rate') }}</div>
        <div class="fee-value">
          <span class="fee-text tabular-nums">{{ $t('profile.futures_fee_maker') }} {{ formatFeeRate(assetStore.currentFuturesFeeRate.maker) }}%</span>
          <span class="fee-divider"> / </span>
          <span class="fee-text tabular-nums">{{ $t('profile.futures_fee_taker') }} {{ formatFeeRate(assetStore.currentFuturesFeeRate.taker) }}%</span>
        </div>
      </div>
    </div>

    <!-- 退出登录按钮 -->
    <div class="logout-wrapper">
      <div class="logout-gradient"></div>
      <div class="logout-section">
        <van-button 
          block 
          class="logout-btn" 
          @click="handleLogout"
        >
          {{ $t('profile.logout') }}
        </van-button>
      </div>
    </div>
  </div>

  <!-- 确认退出对话框 -->
  <van-dialog
    v-model:show="showLogoutDialog"
    :title="$t('settings.logout_confirm_title')"
    :message="$t('settings.logout_confirm_message')"
    show-cancel-button
    :confirm-button-text="$t('settings.logout_confirm_btn')"
    :cancel-button-text="$t('settings.logout_cancel_btn')"
    class-name="dark-dialog"
    @confirm="confirmLogout"
  />
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import { useAssetStore } from '@/stores/assets';

const router = useRouter();
const { t } = useI18n();
const assetStore = useAssetStore();

// 数据
const walletName = ref('Wallet01-BW0');
const walletId = ref('0x1234567890abcdef1234567890abcdef123De');
const googleAuthEnabled = ref(localStorage.getItem('googleAuthEnabled') === 'true');
const showLogoutDialog = ref(false);

// 加载谷歌验证状态
const loadGoogleAuthStatus = () => {
  const enabled = localStorage.getItem('googleAuthEnabled') === 'true';
  googleAuthEnabled.value = enabled;
};

// 页面加载时读取状态
onMounted(() => {
  loadGoogleAuthStatus();
});

// 页面激活时重新加载状态（从其他页面返回时）
onActivated(() => {
  loadGoogleAuthStatus();
});

// 监听谷歌验证状态变化，同步到 localStorage
watch(googleAuthEnabled, (newVal) => {
  if (newVal) {
    localStorage.setItem('googleAuthEnabled', 'true');
    localStorage.setItem('googleAuthStatus', '已开启');
  } else {
    localStorage.setItem('googleAuthEnabled', 'false');
    localStorage.setItem('googleAuthStatus', '未开启');
  }
});

// 计算属性：ID 过长时中间省略号处理
const displayWalletId = computed(() => {
  const id = walletId.value;
  if (id.length > 20) {
    return `${id.slice(0, 4)}...${id.slice(-4)}`;
  }
  return id;
});

// 格式化费率（将小数转换为百分比显示）
const formatFeeRate = (rate) => {
  return (rate * 100).toFixed(3);
};

// 方法：处理 BNB 手续费开关切换
const handleBNBFeesToggle = (value) => {
  assetStore.toggleBNBForFees(value);
  showToast({
    message: value ? t('profile.bnb_fee_enabled') : t('profile.bnb_fee_disabled'),
    duration: 1500,
    position: 'middle'
  });
};

// 方法：处理 BNB 利息开关切换
const handleBNBInterestToggle = (value) => {
  assetStore.toggleBNBForInterest(value);
  showToast({
    message: value ? t('profile.bnb_interest_enabled') : t('profile.bnb_interest_disabled'),
    duration: 1500,
    position: 'middle'
  });
};

// 方法：处理谷歌验证开关切换
const handleGoogleAuthToggle = (value) => {
  // 如果用户尝试开启但当前未开启，跳转到设置页面
  if (value && !googleAuthEnabled.value) {
    router.push('/google-auth');
    return;
  }
  // 如果用户尝试关闭，直接更新状态
  if (!value) {
    googleAuthEnabled.value = false;
    showToast({
      message: t('profile.google_auth_disabled'),
      duration: 1500,
      position: 'middle'
    });
  }
};

// 方法
const handleCopyWalletId = async () => {
  try {
    await navigator.clipboard.writeText(walletId.value);
    showToast({ 
      message: t('profile.id_copied'), 
      icon: 'success', 
      duration: 1500,
      position: 'middle'
    });
  } catch (err) {
    showToast({ 
      message: t('common.copy_failed'), 
      duration: 1500,
      position: 'middle'
    });
  }
};

const handleLogout = () => {
  showLogoutDialog.value = true;
};

const confirmLogout = () => {
  showLogoutDialog.value = false;
  
  // 先断开钱包连接，重置 Pinia 状态
  assetStore.disconnectWallet();
  
  // 然后清空 localStorage
  localStorage.clear();
  
  showToast({ 
    message: t('settings.logout_success'), 
    icon: 'success',
    duration: 1500,
    position: 'middle'
  });
  setTimeout(() => {
    router.push('/');
  }, 1500);
};
</script>

<style scoped>
.profile-page {
  background: var(--color-bg);
  min-height: 100vh;
  padding-top: 46px;
  padding-bottom: 120px;
  color: var(--color-text-primary);
  font-family: sans-serif;
}

/* 顶部 Header 区域 */
.header-section {
  padding: 15px 20px 20px;
  background: var(--color-bg);
}

.wallet-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.wallet-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wallet-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.wallet-id-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.wallet-id-label {
  font-size: 14px;
  color: var(--color-brand-legacy);
  font-weight: 500;
}

.wallet-id-value {
  font-size: 14px;
  color: var(--color-brand-legacy);
  font-weight: 500;
  font-family: 'DIN Alternate', sans-serif;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.copy-icon {
  cursor: pointer;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.copy-icon:active {
  opacity: 0.7;
}

.tabular-nums {
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', sans-serif;
}

/* 核心功能开关区 */
.settings-card {
  margin: 16px;
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  overflow: hidden;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-title {
  font-size: 15px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.setting-desc {
  font-size: 12px;
  color: var(--color-brand-legacy);
  font-weight: 400;
}

/* Switch 深度覆盖与动画 */
:deep(.switch-item.van-switch) {
  background-color: var(--color-surface-muted) !important;
  transition: transform 0.15s ease;
}

:deep(.switch-item.van-switch:active) {
  transform: scale(0.95);
}

:deep(.switch-item.van-switch--on) {
  background-color: var(--color-brand-legacy) !important;
}

:deep(.switch-item.van-switch__node) {
  background-color: var(--color-surface-elevated) !important;
}

/* 费率展示区 */
.fee-card {
  margin: 16px;
  padding: 16px 20px;
  background: rgb(var(--color-border-rgb) / 0.02);
  border-radius: 12px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.fee-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fee-label {
  font-size: 15px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.fee-value {
  display: flex;
  align-items: center;
  gap: 4px;
}

.fee-text {
  font-size: 15px;
  color: var(--color-brand-legacy);
  font-weight: 500;
  font-family: 'DIN Alternate', sans-serif;
}

.fee-divider {
  font-size: 15px;
  color: var(--color-text-secondary);
  font-weight: 400;
}

/* 退出登录按钮区域 */
.logout-wrapper {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

.logout-gradient {
  height: 60px;
  background: linear-gradient(to top, rgb(var(--color-bg-rgb) / 0.95) 0%, rgb(var(--color-bg-rgb) / 0.5) 50%, transparent 100%);
  backdrop-filter: blur(8px);
  pointer-events: none;
}

.logout-section {
  padding: 12px 16px 24px;
  background: var(--color-bg);
}

.logout-btn {
  background: transparent !important;
  border: 1px solid var(--color-brand-legacy) !important;
  color: var(--color-brand-legacy) !important;
  border-radius: 12px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.logout-btn:active {
  background: rgb(var(--color-brand-legacy-rgb) / 0.1) !important;
  opacity: 0.8;
}

/* Dialog 深度覆盖 */
:deep(.dark-dialog.van-dialog),
:deep(.dark-dialog .van-dialog__content),
:deep(.dark-dialog .van-dialog__footer) {
  background-color: var(--color-bg-card) !important;
}

:deep(.dark-dialog .van-dialog__header) {
  color: var(--color-text-primary) !important;
}

:deep(.dark-dialog .van-dialog__message) {
  color: var(--color-text-primary) !important;
}

:deep(.dark-dialog .van-dialog__confirm),
:deep(.dark-dialog .van-dialog__confirm .van-button__text) {
  color: var(--color-brand-legacy) !important;
  font-weight: 600;
}

:deep(.dark-dialog .van-button--default) {
  background: transparent !important;
  border: none !important;
  color: var(--color-text-secondary) !important;
}
</style>

<!-- 全局样式：Dialog 暗黑主题（因为 Dialog 挂载在 body 下，scoped 无法触达） -->
<style>
/* 强制覆盖 Dialog 整体背景 */
.dark-dialog.van-dialog,
.dark-dialog.van-dialog .van-dialog__content {
  background-color: var(--color-bg-card) !important;
  border-radius: 12px;
}

/* 标题和内容文字 */
.dark-dialog .van-dialog__header {
  color: var(--color-text-primary) !important;
  padding-top: 24px;
  padding-bottom: 16px;
}

.dark-dialog .van-dialog__message {
  color: var(--color-text-primary) !important;
  padding: 0 24px 20px;
}

/* 底部按钮栏 */
.dark-dialog .van-dialog__footer {
  background-color: var(--color-bg-card) !important;
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.05) !important;
  display: flex;
}

/* 取消按钮 */
.dark-dialog .van-dialog__cancel,
.dark-dialog .van-dialog__cancel .van-button__text {
  background: transparent !important;
  border: none !important;
  color: var(--color-text-secondary) !important;
  font-weight: 500;
}

.dark-dialog .van-dialog__cancel::after {
  border-right: 1px solid rgb(var(--color-border-rgb) / 0.05) !important;
}

/* 确认按钮 */
.dark-dialog .van-dialog__confirm,
.dark-dialog .van-dialog__confirm .van-button__text {
  background: transparent !important;
  border: none !important;
  color: var(--color-brand-legacy) !important;
  font-weight: 600 !important;
}

/* 按钮通用样式 */
.dark-dialog .van-dialog__footer .van-button {
  background: transparent !important;
  border: none !important;
  flex: 1;
  height: 50px;
  font-size: 16px;
}

.dark-dialog .van-dialog__footer .van-button:active {
  background-color: rgb(var(--color-border-rgb) / 0.05) !important;
}
</style>