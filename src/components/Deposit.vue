<template>
    <van-nav-bar
      :title="t('deposit.title')"
      left-arrow
      @click-left="router.back()"
      fixed
      safe-area-inset-top
      class="app-sub-nav-bar"
    />
  
    <div class="deposit-page">
      <!-- 副标题 -->
      <p class="page-subtitle">{{ t('deposit.subtitle') }}</p>
  
      <!-- 选择网络卡片 -->
      <div class="section network-section">
        <div class="section-title">{{ t('deposit.net') }}</div>
        <div class="network-selector" @click="showNetworkSheet = true">
          <span class="network-text">{{ selectedNetwork.name }}</span>
          <van-icon name="arrow-down" class="arrow-icon" />
        </div>
      </div>
  
      <!-- 充值地址卡片 -->
      <div class="section address-section">
        <div class="section-title">{{ t('deposit.addr') }}</div>
        <div class="address-box">
          <span class="address-text">{{ currentAddress }}</span>
          <van-button size="small" class="copy-btn" @click="copyAddress">
            {{ t('deposit.copy') }}
          </van-button>
        </div>
  
        <div 
          class="qr-code" 
          @mousedown="handleTouchStart"
          @mouseup="handleTouchEnd"
          @mouseleave="handleTouchEnd"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
        >
          <div class="qr-placeholder">
            <van-icon name="qr" size="80" color="#8E8E93" />
            <span class="qr-tip">{{ t('deposit.qr_tip') }}</span>  <!-- 修改这里 -->
            <span class="qr-hint">{{ t('deposit.qr_hint') }}</span>  <!-- 修改这里 -->
          </div>
        </div>
      </div>
  
      <!-- 警告提示卡片 -->
      <div class="section warning-section">
        <div class="warning-tip">
          <van-icon name="warning-o" color="#D4AF37" size="22" />
          <span>{{ t('deposit.tips') }}</span>
        </div>
      </div>

      <!-- 测试专用按钮 -->
      <div class="test-section">
        <van-button 
          type="success" 
          size="small" 
          icon="plus"
          @click="handleTestDeposit"
        >
          [测试专用] 模拟到账 1000 USDT
        </van-button>
        <p class="test-hint">
          (真实环境中，这里不会有按钮，而是等待链上自动回调)
        </p>
      </div>

      <van-action-sheet
        v-model:show="showNetworkSheet"
        :actions="networkActions"
        cancel-text="Cancel"
        close-on-click-action
        @select="onNetworkSelect"
      />
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useI18n } from 'vue-i18n';
  import { showToast } from 'vant';
  import { useAssetStore } from '@/stores/assets';

  const router = useRouter();
  const { t } = useI18n();
  const assetStore = useAssetStore();
  
  const networks = {
    TRC20: { name: 'TRC20 (Tron)', address: 'TR7NHqjeKQxGTCuuP8qACu7f9i5dU9Y9aF' },
    ERC20: { name: 'ERC20 (Ethereum)', address: '0x8a9c9b8d1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6' },
    BEP20: { name: 'BEP20 (BSC)', address: '0x8a9c9b8d1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6' },
    Polygon: { name: 'Polygon', address: '0x8a9c9b8d1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6' }
  };
  
  const selectedNetwork = ref(networks.TRC20);
  const currentAddress = ref(networks.TRC20.address);
  const showNetworkSheet = ref(false);
  
  const networkActions = Object.values(networks).map(net => ({
    name: net.name,
    value: net
  }));
  
  const onNetworkSelect = (item) => {
    selectedNetwork.value = item.value;
    currentAddress.value = item.value.address;
    showNetworkSheet.value = false;
  };
  
  const copyAddress = async () => {
    try {
      await navigator.clipboard.writeText(currentAddress.value);
      showToast({ message: t('deposit.copy_success'), icon: 'success' });
    } catch (err) {
      showToast({ message: '复制失败', duration: 2000 });
    }
  };

  // 模拟充值功能（长按触发）
  let longPressTimer = null;
  const handleSimulateDeposit = () => {
    // 清除之前的定时器
    if (longPressTimer) {
      clearTimeout(longPressTimer);
    }
    
    // 设置长按定时器（500ms）
    longPressTimer = setTimeout(() => {
      assetStore.deposit(1000);
      showToast({ 
        message: 'Deposit Success: +1000 USDT', 
        icon: 'success',
        duration: 2000
      });
    }, 500);
  };

  // 处理触摸开始（移动端）
  const handleTouchStart = () => {
    handleSimulateDeposit();
  };

  // 处理触摸结束（取消长按）
  const handleTouchEnd = () => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
  };

  // 测试专用：模拟充值
  const handleTestDeposit = () => {
    assetStore.deposit(1000); // 调用 Pinia 的加钱方法
    showToast({
      message: '充值成功 +1000 USDT',
      icon: 'success',
    });
  };
  </script>
  
  <style scoped>
  .deposit-page {
    background: #000000;
    min-height: 100vh;
    padding: 16px;
    padding-top: 64px;
    padding-bottom: 80px;
    color: #fff;
    box-sizing: border-box;
  }
  
  /* 副标题 */
  .page-subtitle {
    font-size: 14px;
    color: #8E8E93;
    margin: 0 0 20px 0;
    padding: 0 4px;
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
  
  /* 卡片 */
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
  
  /* 网络选择器 */
  .network-selector {
    background: #1C1C1E;
    color: #FFFFFF;
    font-size: 16px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .network-selector:active {
    opacity: 0.7;
  }
  .network-text {
    font-weight: 400;
    color: #FFFFFF;
  }
  .arrow-icon {
    color: #D4AF37;
    font-size: 18px;
  }
  
  /* 地址盒子 */
  .address-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1C1C1E;
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 20px;
    word-break: break-all;
    border: 1px solid rgba(255,255,255,0.08);
    gap: 12px;
  }
  .address-text {
    font-family: monospace;
    font-size: 14px;
    color: #FFFFFF;
    flex: 1;
    font-variant-numeric: tabular-nums;
  }
  .copy-btn {
    background: #D4AF37;
    color: #000000;
    border: none;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.3s ease;
  }
  .copy-btn:active {
    opacity: 0.7;
  }
  
  /* 二维码 */
  .qr-code {
    text-align: center;
    margin: 20px 0 0 0;
  }
  .qr-placeholder {
    width: 200px;
    height: 200px;
    background: #1C1C1E;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    gap: 12px;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .qr-tip {
    font-size: 12px;
    color: #8E8E93;
  }
  .qr-hint {
    font-size: 11px;
    color: #5A5A5A;
    margin-top: 6px;
    opacity: 0.6;
  }
  
  /* 警告提示卡片 */
  .warning-section {
    background: #141414;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 0;
  }
  .warning-tip {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 13px;
    color: #FFFFFF;
    line-height: 1.5;
  }
  .warning-tip :deep(.van-icon) {
    flex-shrink: 0;
    margin-top: 2px;
  }

  /* 测试按钮区域 */
  .test-section {
    margin-top: 30px;
    text-align: center;
    opacity: 0.8;
  }
  .test-hint {
    font-size: 10px;
    color: #666;
    margin-top: 5px;
  }
  </style>

