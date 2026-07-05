<template>
  <div id="app">
    <!-- 全局加载条 -->
    <div v-if="assetStore.isLoading" class="global-loading-bar">
      <van-loading color="#FCD535" vertical size="20px">加载中...</van-loading>
    </div>

    <div class="app-header" v-if="showAppHeader">
      <div class="header-left">
        <BinanceLogo :size="18" />
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
        
        <!-- 测试按钮：验证 API 连通性和 Token 自动携带 -->
        <div 
          class="test-btn" 
          @click="handleTestUserInfo"
          title="测试获取用户信息"
        >
          🛠️
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
        <keep-alive :include="['Home', 'MarketDetail', 'Miner', 'Trade', 'IDO', 'Me']">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>

    <van-tabbar 
      v-if="!isFullScreen"
      v-model="active" 
      active-color="#EAECEF" 
      inactive-color="#8E8E93" 
      :border="false" 
      fixed 
      placeholder 
      safe-area-inset-bottom 
      @change="onTabChange"
      style="
        --van-tabbar-background: #1E2329;
        --van-tabbar-item-active-background: transparent;
        --van-tabbar-height: 60px;
        background-color: #1E2329;
      "
    >
      <van-tabbar-item icon="wap-home-o" name="/">{{ $t('tab.home') }}</van-tabbar-item>
      <van-tabbar-item icon="cluster-o" name="/miner">{{ $t('tab.miner') }}</van-tabbar-item>
      <van-tabbar-item icon="balance-list-o" name="/trade">{{ $t('tab.trade') }}</van-tabbar-item>
      <van-tabbar-item icon="gem-o" name="/ido">{{ $t('tab.ido') }}</van-tabbar-item>
      <van-tabbar-item icon="manager-o" name="/me">{{ $t('tab.me') }}</van-tabbar-item>
    </van-tabbar>

    <LanguageSelect ref="langRef" />
    
    <!-- 断开连接确认弹窗 -->
    <DisconnectDialog 
      :show="showDisconnectDialog"
      @confirm="handleDisconnectConfirm"
      @cancel="handleDisconnectCancel"
    />
    
    <!-- 全局通知组件 (高端黑金风格) -->
    <transition name="notif-slide">
      <div v-if="notification.show" class="global-notification" @click="handleNotifClick">
        <div class="notif-glow"></div>
        <van-icon :name="notification.icon" class="notif-icon" />
        <div class="notif-body">
          <div class="notif-title">{{ notification.title }}</div>
          <div class="notif-message">{{ notification.message }}</div>
        </div>
        <van-icon name="arrow" class="notif-arrow" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { Tabbar, TabbarItem, Icon, showToast } from 'vant';
import LanguageSelect from './components/LanguageSelect.vue';
import DisconnectDialog from './components/DisconnectDialog.vue';
import { useAssetStore } from '@/stores/assets';
import { useMarketStore } from '@/stores/market';
import { getCurrentUser } from '@/api/user';
import BinanceLogo from '@/components/BinanceLogo.vue';

const { t } = useI18n();

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
const marketStore = useMarketStore();
const isConnecting = ref(false);
const showDisconnectDialog = ref(false);

// --- 全局通知状态 ---
const notification = ref({
  show: false,
  title: '',
  message: '',
  icon: 'bell-o',
  path: '',
  timer: null
});

// 存储上一次的价格，用于检测波动
const previousPrices = ref({});

// 显示通知函数
const triggerNotification = (title, message, icon = 'bullhorn-o', path = '') => {
  // 检查设置中的推送开关
  const pushEnabled = localStorage.getItem('user_push_enabled') !== 'false';
  if (!pushEnabled) return;

  // 清除之前的定时器
  if (notification.value.timer) {
    clearTimeout(notification.value.timer);
  }

  notification.value = {
    show: true,
    title,
    message,
    icon,
    path,
    timer: setTimeout(() => {
      notification.value.show = false;
    }, 5000) // 5秒后自动消失
  };
};

const handleNotifClick = () => {
  if (notification.value.path) {
    router.push(notification.value.path);
  }
  notification.value.show = false;
};

// 监听行情变化，触发波动通知
watch(() => marketStore.tickers, (newTickers) => {
  const coinSymbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX'];
  
  coinSymbols.forEach(symbol => {
    const ticker = newTickers[symbol];
    if (ticker && ticker.price > 0) {
      const currentPrice = Number(ticker.price);
      const oldPrice = previousPrices.value[symbol];
      
      if (oldPrice) {
        const priceChange = Math.abs((currentPrice - oldPrice) / oldPrice);
        
        // 如果价格波动超过 2%，触发通知
        if (priceChange >= 0.02) {
          const changePercent = ((currentPrice - oldPrice) / oldPrice * 100).toFixed(2);
          const isUp = currentPrice > oldPrice;
          
          triggerNotification(
            t(isUp ? 'settings.notif_market_up' : 'settings.notif_market_down', { symbol }),
            t('settings.notif_market_current', { 
              price: currentPrice.toFixed(2), 
              change: (isUp ? '+' : '') + changePercent 
            }),
            isUp ? 'trending-up' : 'trending-down',
            `/market?symbol=${symbol}`
          );
        }
      }
      
      // 更新历史价格
      previousPrices.value[symbol] = currentPrice;
    }
  });
}, { deep: true });

// 判断是否全屏
const isFullScreen = computed(() => {
  if (!route || !route.path) return false;
  
  // 优先检查路由meta中是否有hideTabbar标记
  if (route.meta?.hideTabbar === true) {
    return true;
  }
  
  // 定义需要全屏展示（隐藏底部导航和AppHeader）的路径关键词
  const fullScreenKeywords = [
    'deposit',
    'withdraw',
    'market',
    'history',
    'subscribe',
    'all-markets',
    'profile',
    'settings',
    'support',
    'security-center',
    'fund-password',
    'google-auth',
    'futures',
    'treasury',        // 新增：国库资产页面
    'chain-explorer', // 新增：链上交易页面
    'earn',           // 新增：理财页面
    'referral'        // 新增：邀请返佣页面
  ];
  
  // 只要当前路径包含以上任何一个关键词，就返回 true
  return fullScreenKeywords.some(key => route.path.includes(key));
});

const showAppHeader = computed(() => {
  if (!route || !route.path) return false;
  const headerHiddenPaths = ['/profile', '/settings', '/support'];
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
    showDisconnectDialog.value = true;
  } else {
    // 未连接，开始连接
    isConnecting.value = true;
    try {
      const result = await assetStore.connectWallet();
      // 检查返回结果，如果成功获取 token，显示欢迎登录提示
      if (result && result.success && result.token) {
        showToast({
          message: t('auth.loginSuccess'),
          icon: 'success'
        });
      } else {
      showToast({
          message: t('auth.loginSuccess'),
        icon: 'success'
      });
      }
    } catch (error) {
      // 根据错误类型显示不同的提示
      let errorMessage = '连接失败，请重试'
      
      if (error.code === 'WALLET_NOT_INSTALLED' || error.message?.includes('安装')) {
        errorMessage = '请先安装 MetaMask 钱包以使用此功能'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      showToast({
        message: errorMessage,
        icon: 'fail',
        duration: 3000
      });
    } finally {
      isConnecting.value = false;
    }
  }
};

// 处理断开连接确认
const handleDisconnectConfirm = () => {
  assetStore.disconnectWallet();
  showDisconnectDialog.value = false;
  showToast({
    message: t('auth.disconnected'),
    icon: 'success'
  });
};

// 处理断开连接取消
const handleDisconnectCancel = () => {
  showDisconnectDialog.value = false;
};

// 测试获取用户信息（验证 API 连通性和 Token 自动携带）
const handleTestUserInfo = async () => {
  try {
    console.log('🧪 开始测试获取用户信息...');
    
    // 调用 getCurrentUser API
    // request.js 的请求拦截器会自动从 localStorage 读取 token 并添加到请求头
    const response = await getCurrentUser();
    
    // 成功时：显示后端返回的用户数据
    const userData = response.data;
    console.log('✅ 测试成功');
    console.log('返回数据:', userData);
    
    // 使用 alert 显示数据（格式化 JSON）
    alert(`✅ 测试成功！\n\n返回数据：\n${JSON.stringify(userData, null, 2)}`);
    
  } catch (error) {
    // 失败时：显示错误信息
    console.error('❌ 测试失败:', error);
    
    // 获取错误详情
    let errorMessage = '请求失败';
    if (error.response) {
      // 服务器返回了错误响应
      errorMessage = `请求失败：${error.response.status} - ${error.response.data?.detail || error.response.data?.message || '未知错误'}`;
      console.error('错误响应:', error.response.data);
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '请求失败：网络错误或服务器无响应';
      console.error('请求已发出但无响应:', error.request);
    } else {
      // 请求配置错误
      errorMessage = `请求失败：${error.message}`;
      console.error('请求配置错误:', error.message);
    }
    
    // 使用 alert 显示错误
    alert(`❌ ${errorMessage}`);
  }
};

// App 启动时初始化数据
onMounted(async () => {
  try {
    // 检查 localStorage 中是否有 Token
    const token = localStorage.getItem('token');
    
    if (token) {
      // 如果有 Token，立即调用 initData() 拉取用户数据
      console.log('🔄 页面加载，正在初始化用户数据...');
      console.log('检测到 Token，开始拉取余额和订单数据');
      
    await assetStore.initData();
      
      console.log('✅ 用户数据初始化完成');
      console.log('当前余额:', assetStore.usdtBalance);
    } else {
      // 如果没有 Token，说明用户未登录，不需要拉取数据
      console.log('ℹ️ 未检测到 Token，跳过数据初始化（用户未登录）');
    }
  } catch (error) {
    console.error('❌ 初始化用户数据失败:', error);
    // 如果是 401 错误，说明 Token 无效，响应拦截器会自动处理
    // 这里只记录错误，不进行额外处理
  }
});
</script>

<style>
body, html, #app {
  background-color: var(--color-bg);
  margin: 0;
  padding: 0;
  min-height: 100vh;
  color: var(--color-text-primary);
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
  border-bottom: 1px solid var(--color-border-subtle);
}
.header-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.header-right { display: flex; align-items: center; gap: 16px; }

/* 测试按钮样式 */
.test-btn {
  background-color: #383E46;
  color: #EAECEF;
  font-size: 18px;
  padding: 6px 10px;
  border-radius: var(--radius-button);
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  user-select: none;
  min-width: 36px;
  height: 32px;
}

.test-btn:hover {
  background-color: #424850;
  transform: scale(1.05);
}

.test-btn:active {
  transform: scale(0.95);
  opacity: 0.8;
}

.connect-wallet-btn { 
  background-color: #383E46; 
  color: #EAECEF; 
  font-size: 12px; 
  padding: 6px 12px; 
  border-radius: var(--radius-button); 
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
  background-color: #383E46;
  color: var(--color-text-primary);
  border: 1px solid var(--color-earn);
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

/* 平滑过渡效果 */
:deep(.van-tabbar-item) {
  transition: all 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28) !important;
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

/* ========== 全局通知组件样式 (Pro Max 黑金风格) ========== */
.global-notification {
  position: fixed;
  top: 16px;
  left: 16px;
  right: 16px;
  background: rgba(28, 28, 30, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(252, 213, 53, 0.3);
  border-radius: 16px;
  padding: 12px 16px;
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(252, 213, 53, 0.1);
  animation: notif-bounce 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  overflow: hidden;
}

.notif-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 50%, rgba(252, 213, 53, 0.1), transparent 70%);
  pointer-events: none;
}

.notif-icon {
  font-size: 24px;
  color: #FCD535;
  background: rgba(252, 213, 53, 0.1);
  padding: 8px;
  border-radius: 12px;
}

.notif-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notif-title {
  font-size: 14px;
  font-weight: 700;
  color: #FCD535;
  letter-spacing: 0.5px;
}

.notif-message {
  font-size: 12px;
  color: #EAECEF;
  opacity: 0.9;
}

.notif-arrow {
  font-size: 14px;
  color: #8E8E93;
}

/* 通知进场离场动画 */
.notif-slide-enter-active {
  transition: all 0.4s cubic-bezier(0.2, 0.9, 0.3, 1.2);
}
.notif-slide-leave-active {
  transition: all 0.3s ease;
}
.notif-slide-enter-from {
  opacity: 0;
  transform: translateY(-100%) scale(0.9);
}
.notif-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

@keyframes notif-bounce {
  from { transform: translateY(-100%); }
  to { transform: translateY(0); }
}
</style>