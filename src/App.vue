<template>
  <div id="app">
    <!-- 全局加载条 -->
    <div v-if="assetStore.isLoading" class="global-loading-bar">
      <van-loading color="#FCD535" vertical size="20px">加载中...</van-loading>
    </div>

    <div class="app-header" v-if="showAppHeader">
      <div class="header-left">
        <img 
          src="https://cryptologos.cc/logos/binance-coin-bnb-logo.svg?v=026" 
          alt="App Logo" 
          class="app-logo"
        />
      </div>

      <div class="header-right">
        <div 
          class="connect-wallet-btn" 
          :class="{ 'connected': assetStore.isWalletConnected, 'loading': isConnecting }"
          @click="handleWalletClick"
        >
          <van-icon v-if="isConnecting" name="loading" class="loading-icon" />
          <span v-if="!assetStore.isWalletConnected && !isConnecting">{{ $t('connect') }}</span>
          <span v-else-if="assetStore.isWalletConnected && !isConnecting">
            {{ formatAddress(assetStore.walletAddress) }}
          </span>
        </div>
        
        <div class="lang-icon-box" @click="langRef?.open()">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EAECEF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
        </div>
      </div>
    </div>

    <div class="main-content" :class="{ 'fullscreen-mode': isFullScreen, 'no-app-header': !showAppHeader }">
      <router-view v-slot="{ Component }">
        <keep-alive :include="['MarketDetail']">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>

    <van-tabbar 
      v-if="!isFullScreen"
      v-model="active" 
      active-color="#FCD535" 
      inactive-color="#8E8E93" 
      :border="false" 
      fixed 
      placeholder 
      safe-area-inset-bottom 
      @change="onTabChange"
      style="
        --van-tabbar-background: #1C1C1E;
        --van-tabbar-item-active-background: transparent;
        --van-tabbar-height: 60px;
        background-color: #1C1C1E;
      "
    >
      <van-tabbar-item icon="wap-home-o" name="/">{{ $t('tab.home') }}</van-tabbar-item>
      <van-tabbar-item icon="cluster-o" name="/miner">{{ $t('tab.miner') }}</van-tabbar-item>
      <van-tabbar-item icon="balance-list-o" name="/trade">交易</van-tabbar-item>
      <van-tabbar-item icon="gem-o" name="/ido">{{ $t('tab.ido') }}</van-tabbar-item>
      <van-tabbar-item icon="manager-o" name="/me">{{ $t('tab.me') }}</van-tabbar-item>
    </van-tabbar>

    <LanguageSelect ref="langRef" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Tabbar, TabbarItem, Icon, showConfirmDialog, showToast } from 'vant';
import LanguageSelect from './components/LanguageSelect.vue';
import { useAssetStore } from '@/stores/assets';

// 注册组件
const VanTabbar = Tabbar;
const VanTabbarItem = TabbarItem;
const VanIcon = Icon;

const router = useRouter();
const route = useRoute();
const langRef = ref(null);
const active = ref('/');
const routerReady = ref(false);
const assetStore = useAssetStore();
const isConnecting = ref(false);

// 判断是否全屏
const isFullScreen = computed(() => {
  if (!route || !route.path) return false;
  // /earn (理财列表页) 不在全屏列表中，会显示底部 TabBar，让用户感觉仍在 App 内
  const fullScreenPaths = ['/deposit', '/withdraw', '/market', '/history', '/earn/subscribe', '/all-markets']; 
  return fullScreenPaths.includes(route.path);
});

const showAppHeader = computed(() => {
  if (!route || !route.path) return false;
  const headerHiddenPaths = ['/profile', '/support', '/settings'];
  return !isFullScreen.value && route.path !== '/earn' && !headerHiddenPaths.includes(route.path);
});

// 监听路由
watch(
  () => route?.path, 
  (newPath) => {
    if (newPath) {
      active.value = newPath;
      routerReady.value = true;
    }
  },
  { immediate: true }
);

const onTabChange = (path) => {
  router.push(path);
};

// 格式化地址显示（截断）
const formatAddress = (address) => {
  if (!address) return '';
  if (address.length <= 10) return address;
  return `${address.slice(0, 4)}...${address.slice(-4)}`;
};

// 处理钱包按钮点击
const handleWalletClick = async () => {
  if (assetStore.isWalletConnected) {
    // 已连接，显示断开确认对话框
    try {
      await showConfirmDialog({
        title: '断开连接',
        message: '确定要断开钱包连接吗？',
        confirmButtonText: '断开',
        cancelButtonText: '取消',
        confirmButtonColor: '#F6465D'
      });
      assetStore.disconnectWallet();
      showToast({
        message: '钱包已断开',
        icon: 'success'
      });
    } catch {
      // 用户取消
    }
  } else {
    // 未连接，开始连接
    isConnecting.value = true;
    try {
      const address = await assetStore.connectWallet();
      showToast({
        message: '钱包连接成功',
        icon: 'success'
      });
    } catch (error) {
      showToast({
        message: '连接失败，请重试',
        icon: 'fail'
      });
    } finally {
      isConnecting.value = false;
    }
  }
};

// App 启动时初始化数据
onMounted(async () => {
  try {
    await assetStore.initData();
  } catch (error) {
    console.error('Failed to initialize app data:', error);
  }
});
</script>

<style>
body, html, #app {
  background-color: #000000;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  color: #ffffff;
}

:root {
  --van-cell-vertical-padding: 18px;
  --van-cell-font-size: 16px;
  --van-cell-line-height: 24px;
}

.van-cell {
  background: transparent !important;
  align-items: center;
}

.van-cell__title {
  color: #FFFFFF;
  font-weight: 500;
  flex: auto;
}

.van-cell__value {
  color: #8E8E93 !important;
  font-size: 14px;
}

.van-cell .van-icon {
  font-size: 20px !important;
  margin-right: 12px;
}

.van-cell::after {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
  left: 16px;
  right: 16px;
}

.section-group {
  background: #1C1C1E !important;
  border-radius: 16px !important;
  overflow: hidden;
  margin-bottom: 16px;
}
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 52px;
  background-color: #1E2329;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  box-sizing: border-box;
  z-index: 2000;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.app-logo { height: 28px; width: auto; }
.header-right { display: flex; align-items: center; gap: 16px; }
.connect-wallet-btn { 
  background-color: #383E46; 
  color: #EAECEF; 
  font-size: 12px; 
  padding: 6px 12px; 
  border-radius: 4px; 
  font-weight: 500; 
  cursor: pointer; 
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  user-select: none;
}
.connect-wallet-btn:hover {
  background-color: #424850;
}
.connect-wallet-btn.connected {
  background-color: #0ECB81;
  color: #FFFFFF;
}
.connect-wallet-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}
.loading-icon {
  animation: rotate 1s linear infinite;
}
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 主内容区域默认样式 */
.main-content { 
  padding-top: 52px; 
  padding-bottom: 50px; 
  min-height: 100vh; 
  box-sizing: border-box; 
}

.main-content.no-app-header {
  padding-top: 0;
}

/* 全屏模式样式 */
.main-content.fullscreen-mode {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* ========== 底部导航栏 Tabbar 美化 ========== */

/* 导航栏背景优化 */
.van-tabbar { 
  background-color: #0E0E0E !important; 
  border-top: 1px solid #1C1C1E !important; 
}

/* 1. 底部导航选中时，图标背景变黄，图标变黑 */
:deep(.van-tabbar-item--active .van-tabbar-item__icon) {
  background-color: #FCD535 !important;
  color: #000000 !important;
  border-radius: 10px;
  padding: 6px 10px;
  transition: all 0.2s ease;
}

/* 2. 确保选中时文字也变为品牌黄 */
:deep(.van-tabbar-item--active) {
  color: #FCD535 !important;
  
}

:deep(.van-tabbar-item--active .van-tabbar-item__text) {
  color: #FCD535 !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  transition: color 0.2s ease !important;
}

/* 未选中状态样式 */
:deep(.van-tabbar-item) {
  color: #8E8E93 !important;
  transition: all 0.3s ease !important;
  position: relative;
}

:deep(.van-tabbar-item:not(.van-tabbar-item--active) .van-tabbar-item__text) {
  color: #8E8E93 !important;
  font-weight: 400 !important;
  font-size: 12px !important;
  transition: color 0.3s ease !important;
}

:deep(.van-tabbar-item:not(.van-tabbar-item--active) .van-tabbar-item__icon) {
  color: #8E8E93 !important;
  transition: all 0.3s ease !important;
}

/* 确保图标和文字对齐 */
:deep(.van-tabbar-item__icon) {
  font-size: 22px !important;
  margin-bottom: 4px !important;
  transition: all 0.3s ease !important;
  display: block !important;
}

:deep(.van-tabbar-item__text) {
  font-size: 12px !important;
  line-height: 1.2 !important;
  margin-top: 2px !important;
  display: block !important;
}

/* Tabbar 项目容器样式 - 确保垂直对齐 */
:deep(.van-tabbar-item) {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 8px 0 !important;
  min-height: 50px !important;
  position: relative !important;
}


/* 确保 Vant 图标字体不被全局字体覆盖 */
.van-icon,
[class*="van-icon"] {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
  font-style: normal !important;
  font-weight: normal !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
}

/* Toast Notification Fixes */
.van-toast {
  min-width: 160px !important;
  white-space: nowrap !important;
  padding: 14px 24px !important;
  box-sizing: border-box !important;
}

.van-toast__text {
  white-space: nowrap !important;
  padding: 0 10px !important;
  font-size: 14px !important;
}

.van-toast--success .van-toast__icon,
.van-toast--fail .van-toast__icon,
.van-toast--loading .van-toast__icon {
  margin-right: 10px !important;
  flex-shrink: 0 !important;
}

.van-toast__message {
  white-space: nowrap !important;
  word-break: keep-all !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.van-toast__content {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: nowrap !important;
}

/* 全局加载条 */
.global-loading-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(252, 213, 53, 0.2);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  backdrop-filter: blur(4px);
}

.global-loading-bar :deep(.van-loading__text) {
  color: #FCD535;
  font-size: 12px;
  margin-top: 4px;
}
</style>

