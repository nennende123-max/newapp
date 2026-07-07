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
          <van-button size="small" class="copy-btn deposit-primary btn-cta" @click="copyAddress">
            {{ t('deposit.copy') }}
          </van-button>
        </div>
  
        <div class="qr-code">
          <div class="qr-placeholder">
            <img v-if="qrDataUrl" :src="qrDataUrl" class="qr-image" :alt="`${selectedNetwork.name} deposit QR`" />
            <van-icon v-else name="qr" size="80" color="var(--color-text-secondary)" />
            <span class="qr-tip">{{ t('deposit.qr_tip') }}</span>  <!-- 修改这里 -->
            <span class="qr-hint">{{ t('deposit.qr_hint') }}</span>  <!-- 修改这里 -->
          </div>
        </div>
      </div>
  
      <!-- 警告提示卡片 -->
      <div class="section warning-section">
        <div class="warning-tip">
          <van-icon name="warning-o" color="var(--color-accent)" size="22" />
          <span>{{ t('deposit.tips') }}</span>
        </div>
      </div>

      <!-- 测试专用按钮 -->
      <div v-if="isDev" class="test-section">
        <van-button 
          type="success" 
          size="small" 
          icon="plus"
          :loading="isLoading"
          :disabled="isLoading"
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
        :cancel-text="t('common.cancel')"
        close-on-click-action
        @select="onNetworkSelect"
      />
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useI18n } from 'vue-i18n';
  import { showToast } from 'vant';
  import QRCode from 'qrcode';
  import { useAssetStore } from '@/stores/assets';
  import { deposit } from '@/api/wallet';
  import { getThemeColor } from '@/styles/theme';

  const router = useRouter();
  const { t } = useI18n();
  const assetStore = useAssetStore();
  const isDev = import.meta.env.DEV;
  
  // 加载状态
  const isLoading = ref(false);
  
  const networks = {
    TRC20: { labelKey: 'deposit.network_trc20', address: 'TR7NHqjeKQxGTCuuP8qACu7f9i5dU9Y9aF' },
    ERC20: { labelKey: 'deposit.network_erc20', address: '0x8a9c9b8d1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6' },
    BEP20: { labelKey: 'deposit.network_bep20', address: '0x8a9c9b8d1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6' },
    Polygon: { labelKey: 'deposit.network_polygon', address: '0x8a9c9b8d1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6' }
  };
  
  const selectedNetworkKey = ref('TRC20');
  const showNetworkSheet = ref(false);
  const qrDataUrl = ref('');
  const selectedNetwork = computed(() => {
    const network = networks[selectedNetworkKey.value] || networks.TRC20;
    return {
      ...network,
      key: selectedNetworkKey.value,
      name: t(network.labelKey)
    };
  });
  const currentAddress = computed(() => selectedNetwork.value.address);
  const qrPayload = computed(() => `${selectedNetwork.value.name}:${currentAddress.value}`);
  
  const networkActions = computed(() => Object.entries(networks).map(([key, net]) => ({
    name: t(net.labelKey),
    value: key
  })));
  
  const onNetworkSelect = (item) => {
    selectedNetworkKey.value = item.value;
    showNetworkSheet.value = false;
  };

  const updateQrCode = async () => {
    try {
      qrDataUrl.value = await QRCode.toDataURL(qrPayload.value, {
        width: 180,
        margin: 1,
        color: {
          dark: getThemeColor('--color-qr-dark'),
          light: getThemeColor('--color-qr-light')
        }
      });
    } catch (err) {
      qrDataUrl.value = '';
    }
  };

  watch(qrPayload, updateQrCode);
  onMounted(updateQrCode);
  
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
          message: '测试充值成功！资金已到账',
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
  const handleTestDeposit = async () => {
    // 设置加载状态，防止重复点击
    isLoading.value = true;
    
    try {
      // 核心调用：调用真实的 deposit API，硬编码充值 1000 USDT
      const response = await deposit({ 
        amount: 1000, 
        currency: 'USDT' 
      });
      
      // 成功反馈
      if (response.data && response.data.code === 200) {
        showToast({
          message: '测试充值成功！资金已到账',
          icon: 'success',
          duration: 3000
        });
        
        // 调用 assetStore.initData() 刷新右上角的总余额
        await assetStore.initData();
        
        console.log('✅ 充值成功，余额已刷新');
      } else {
        throw new Error(response.data?.message || '充值失败');
      }
    } catch (error) {
      // 失败反馈
      console.error('❌ 充值失败:', error);
      
      let errorMessage = error.message || '充值失败，请重试';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
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
  .deposit-page {
    background: var(--color-surface-1);
    min-height: 100vh;
    padding: 20px 16px;
    padding-top: 64px;
    padding-bottom: 80px;
    color: var(--color-text-primary);
    box-sizing: border-box;
  }
  
  /* 副标题 */
  .page-subtitle {
    font-size: 14px;
    color: var(--color-text-secondary);
    margin: 0 0 20px 0;
    padding: 0 4px;
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
  
  /* 卡片 */
  .section {
    background: var(--color-surface-2);
    border-radius: var(--radius-card);
    padding: var(--space-card-md);
    margin-bottom: 16px;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-md);
  }
  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin-bottom: 16px;
    letter-spacing: 0.5px;
  }
  
  /* 网络选择器 */
  .network-selector {
    background: var(--color-bg-input);
    color: var(--color-text-primary);
    font-size: 16px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }
  .network-selector:active {
    opacity: 0.7;
  }
  .network-text {
    font-weight: 400;
    color: var(--color-text-primary);
  }
  .arrow-icon {
    color: var(--color-accent);
    font-size: 18px;
  }
  
  /* 地址盒子 */
  .address-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--color-bg-input);
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 20px;
    word-break: break-all;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    gap: 12px;
  }
  .address-text {
    font-family: monospace;
    font-size: 14px;
    color: var(--color-text-primary);
    flex: 1;
    font-variant-numeric: tabular-nums;
  }
  .copy-btn {
    background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
    color: var(--color-text-on-accent);
    border: 1px solid rgb(var(--color-primary-rgb) / 0.48);
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgb(var(--color-primary-rgb) / 0.2);
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
    background: var(--color-surface-2);
    border-radius: 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    gap: 10px;
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    padding: 14px;
  }
  .qr-image {
    width: 132px;
    height: 132px;
    padding: 8px;
    background: var(--color-qr-light);
    border-radius: 12px;
    border: 1px solid var(--color-border-subtle);
  }
  .qr-tip {
    font-size: 12px;
    color: var(--color-text-secondary);
  }
  .qr-hint {
    font-size: 11px;
    color: var(--color-text-muted);
    margin-top: 6px;
    opacity: 0.6;
  }
  
  /* 警告提示卡片 */
  .warning-section {
    background: rgb(var(--color-warning-rgb) / 0.08);
    border-color: rgb(var(--color-warning-rgb) / 0.22);
    border-radius: var(--radius-card);
    padding: 16px;
    margin-bottom: 0;
  }
  .warning-tip {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 13px;
    color: var(--color-text-primary);
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
    color: var(--color-text-muted);
    margin-top: 5px;
  }

  .deposit-page {
    background:
      linear-gradient(180deg, rgb(var(--color-primary-rgb) / 0.07) 0, rgb(var(--color-primary-rgb) / 0) 190px),
      var(--color-surface-1);
  }

  .page-subtitle {
    font-size: 15px;
    color: var(--color-text-secondary);
    margin-bottom: 22px;
  }

  .section {
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: var(--shadow-md);
  }

  .section-title {
    color: var(--color-primary-hover);
    font-weight: 800;
    letter-spacing: 0;
  }

  .network-selector,
  .address-box {
    min-height: 58px;
    border-radius: 14px;
  }

  .network-selector:active,
  .address-box:focus-within {
    border-color: var(--color-primary-border);
    box-shadow: 0 0 0 3px var(--color-focus-ring);
  }

  .address-section {
    padding-bottom: 26px;
  }

  .warning-section {
    box-shadow: none;
  }
  </style>
