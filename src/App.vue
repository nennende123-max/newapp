<template>
  <div id="app">
    <div class="app-header">
      <div class="header-left">
        <img 
          src="https://cryptologos.cc/logos/binance-coin-bnb-logo.svg?v=026" 
          alt="App Logo" 
          class="app-logo"
        />
      </div>

      <div class="header-right">
        <div class="connect-wallet-btn">
          连接钱包
        </div>
        
        <div class="lang-icon-box">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="#EAECEF" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
        </div>
      </div>
    </div>

    <div class="main-content">
      <component :is="currentView" />
    </div>

    <van-tabbar v-model="active" active-color="#FCD535" inactive-color="#8E8E93" :border="false" fixed placeholder safe-area-inset-bottom>
      <van-tabbar-item icon="wap-home-o" name="home">Home</van-tabbar-item>
      <van-tabbar-item icon="cluster-o" name="miner">Miner</van-tabbar-item>
      <van-tabbar-item icon="gem-o" name="ido">IDO</van-tabbar-item>
      <van-tabbar-item icon="manager-o" name="me">Me</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Tabbar, TabbarItem } from 'vant';

import Home from './components/Home.vue';
import Miner from './components/Miner.vue';
import IDO from './components/IDO.vue';
import Me from './components/Me.vue';

const VanTabbar = Tabbar;
const VanTabbarItem = TabbarItem;

const active = ref('home');

const currentView = computed(() => {
  switch (active.value) {
    case 'home': return Home;
    case 'miner': return Miner;
    case 'ido': return IDO;
    case 'me': return Me;
    default: return Home;
  }
});
</script>

<style>
/* 全局样式重置 */
body, html, #app {
  background-color: #000000;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', sans-serif;
}

/* --- 顶部导航栏核心样式 --- */
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

.header-left {
  display: flex;
  align-items: center;
}
.app-logo {
  height: 28px;
  width: auto;
  display: block;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px; 
}

.connect-wallet-btn {
  background-color: #383E46;
  color: #EAECEF;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
}

.lang-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0.9;
  /* 确保 SVG 不会太大 */
  width: 24px; 
  height: 24px;
}

.main-content {
  padding-top: 52px;
  padding-bottom: 50px;
  min-height: 100vh;
  box-sizing: border-box;
}

.van-tabbar {
  background-color: #141414 !important;
  border-top: 1px solid #2C2C2E !important;
}
</style>