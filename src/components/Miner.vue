<template>
    <div class="earn-page">
      <transition name="nav-slide">
        <div v-if="betSuccess" class="top-notification">
          <div class="notif-glow"></div>
          <van-icon name="checked" color="#FCD535" size="18" />
          <span>{{ lastSide }} Trade Placed Successfully</span>
        </div>
      </transition>
  
      <div class="nav-header">
        <div class="top-nav-tabs">
          <div class="nav-item" :class="{ active: currentTab === 'mining' }" @click="changeTab('mining')">
            <van-icon name="cluster" /> Cloud Mining
          </div>
          <div class="nav-item" :class="{ active: currentTab === 'battle' }" @click="changeTab('battle')">
            <van-icon name="fire" /> Price Battle
          </div>
        </div>
      </div>
  
      <div v-if="currentTab === 'battle'" class="tab-view battle-main">
        
        <div class="battle-info-bar">
          <div class="round-id">Round #{{ currentRound }}</div>
          <div class="timer-box">
            <span class="t-val">{{ countdown }}s</span>
            <span class="t-lab">&nbsp;LEFT</span>
          </div>
        </div>
  
        <div class="price-hero">
          <div class="market-selector" @click.stop="isMenuOpen = true">
            <span class="m-name">{{ selectedCoin.name }}/USDT</span>
            <van-icon name="arrow-down" class="m-arrow" />
            <div class="m-index-tag">INDEX</div>
          </div>
  
          <div class="price-val-wrap" :class="priceChange >= 0 ? 'text-green' : 'text-red'">
            <span class="p-symbol">$</span>
            <span class="p-integer">{{ currentPrice.split('.')[0] }}</span>
            <span class="p-decimal">.{{ currentPrice.split('.')[1] }}</span>
            <span class="p-trend">{{ priceChange >= 0 ? '▲' : '▼' }}</span>
          </div>
          <div class="feed-note">Real-time Feed: Binance & Coinbase Weighted</div>
        </div>
  
        <div class="sentiment-section">
          <div class="s-bar">
            <div class="s-fill bull" :style="{ width: selectedCoin.sentiment + '%' }">
              {{ selectedCoin.sentiment }}% Bull
            </div>
            <div class="s-fill bear" :style="{ width: (100 - selectedCoin.sentiment) + '%' }">
              {{ 100 - selectedCoin.sentiment }}% Bear
            </div>
          </div>
        </div>
  
        <div class="action-grid">
          <button class="btn-battle bullish" @click.stop="handleBet('UP')">BULLISH</button>
          <button class="btn-battle bearish" @click.stop="handleBet('DOWN')">BEARISH</button>
        </div>
  
        <div class="results-container">
          <div class="res-head">
            <span class="res-title">Recent Battle Results</span>
            <span class="res-market">{{ selectedCoin.name }} Market</span>
          </div>
  
          <div class="res-table-header">
            <div class="cell-l">PAIR / ROUND</div>
            <div class="cell-c">CLOSE PRICE</div>
            <div class="cell-r">STATUS / PNL</div>
          </div>
  
          <div class="res-list">
            <div v-if="filteredHistory.length > 0">
              <div class="res-row" v-for="h in filteredHistory" :key="h.id">
                <div class="cell-l">
                  <span class="pair">{{ h.coin }}</span>
                  <span class="id">#{{ h.id }}</span>
                </div>
                <div class="cell-c price">${{ h.close }}</div>
                <div class="cell-r">
                  <span class="badge" :class="h.type">{{ h.type }}</span>
                  <span class="pnl" :class="h.type === 'WIN' ? 'text-green' : 'text-red'">{{ h.profit }}</span>
                </div>
              </div>
            </div>
            <div v-else class="res-empty">
              <p>No Records for {{ selectedCoin.name }}</p>
              <span>Waiting for next settlement...</span>
            </div>
          </div>
        </div>
      </div>
  
      <div v-else class="tab-view mining-view">
        <div class="mining-header-text">Institutional Mining Power</div>
        <div v-if="loading" class="loading-box">
          <van-loading color="#FCD535" vertical>Updating Database...</van-loading>
        </div>
        <div v-else class="miner-list">
          <div class="miner-card" v-for="m in minersFromDB" :key="m.id">
            <div class="m-top">
              <div class="m-icon-box">{{ m.name[0] }}</div>
              <div class="m-title"><h3>{{ m.name }}</h3><span class="m-badge">Safe & SLA Guaranteed</span></div>
            </div>
            <div class="m-stats">
              <div class="s-item"><span class="l">Daily Rate</span><span class="v text-gold">{{ m.rate }}%</span></div>
              <div class="s-item"><span class="l">Cycle</span><span class="v">{{ m.days }}D</span></div>
              <div class="s-item"><span class="l">Min Price</span><span class="v">${{ m.price }}</span></div>
            </div>
            <button class="m-buy-btn">Rent Machine Now</button>
          </div>
        </div>
      </div>
  
      <div v-if="isMenuOpen" class="menu-overlay" @click="isMenuOpen = false">
        <div class="menu-sheet" @click.stop>
          <div class="menu-indicator"></div>
          <div class="menu-title-row">
            <span>Select Market Pair</span>
            <van-icon name="cross" @click="isMenuOpen = false" />
          </div>
          <div class="coin-list">
            <div v-for="coin in coinList" :key="coin.name" 
                 class="coin-item" :class="{ active: selectedCoin.name === coin.name }"
                 @click="selectCoin(coin.name)">
              <div class="ci-left">
                <div class="ci-icon" :style="{ background: coin.color }">{{ coin.name[0] }}</div>
                <div class="ci-info">
                  <span class="name">{{ coin.name }}/USDT</span>
                  <span class="full">{{ coin.fullName }}</span>
                </div>
              </div>
              <van-icon v-if="selectedCoin.name === coin.name" name="success" color="#FCD535" size="20" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted, computed } from 'vue';
  import axios from 'axios';
  
  const currentTab = ref('battle');
  const isMenuOpen = ref(false);
  const betSuccess = ref(false);
  const lastSide = ref('');
  const loading = ref(false);
  
  const currentRound = ref(8297);
  const countdown = ref(54);
  
  // 资产配置：包含独立情绪数值
  const coinAssets = {
    BTC: { name: 'BTC', fullName: 'Bitcoin Index', price: 92436.40, sentiment: 69 },
    ETH: { name: 'ETH', fullName: 'Ethereum Index', price: 3109.04, sentiment: 52 },
    SOL: { name: 'SOL', fullName: 'Solana Index', price: 142.08, sentiment: 41 },
    BNB: { name: 'BNB', fullName: 'Binance Coin', price: 709.20, sentiment: 65 }
  };
  
  const selectedCoin = ref(coinAssets.BNB); 
  const currentPrice = ref(selectedCoin.value.price.toFixed(2));
  const priceChange = ref(-1);
  
  const coinList = [
    { name: 'BTC', fullName: 'Bitcoin', color: '#F7931A' },
    { name: 'ETH', fullName: 'Ethereum', color: '#627EEA' },
    { name: 'SOL', fullName: 'Solana', color: '#14F195' },
    { name: 'BNB', fullName: 'Binance Coin', color: '#F3BA2F' }
  ];
  
  let pTimer, cTimer;
  const stopAllTimers = () => {
    if (pTimer) clearInterval(pTimer);
    if (cTimer) clearInterval(cTimer);
  };
  
  const startTimers = () => {
    stopAllTimers();
    pTimer = setInterval(() => {
      const delta = (Math.random() - 0.5) * 4;
      currentPrice.value = (parseFloat(currentPrice.value) + delta).toFixed(2);
      priceChange.value = delta >= 0 ? 1 : -1;
    }, 1000);
    cTimer = setInterval(() => {
      if (countdown.value > 0) countdown.value--;
      else { countdown.value = 60; currentRound.value++; }
    }, 1000);
  };
  
  const changeTab = (tab) => { 
    currentTab.value = tab; 
    if (tab === 'mining') {
      stopAllTimers();
      fetchMiners();
    } else {
      startTimers();
    }
  };
  
  const selectCoin = (name) => {
    selectedCoin.value = coinAssets[name];
    currentPrice.value = selectedCoin.value.price.toFixed(2);
    isMenuOpen.value = false;
  };
  
  const handleBet = (side) => {
    lastSide.value = side;
    betSuccess.value = true;
    setTimeout(() => { betSuccess.value = false; }, 3000);
  };
  
  const minersFromDB = ref([]);
  const fetchMiners = async () => {
    loading.value = true;
    try {
      const res = await axios.get('http://localhost:3000/api/miners');
      minersFromDB.value = res.data;
    } catch (err) {
      minersFromDB.value = [{ id: 1, name: 'Antminer S21 Pro', rate: 2.5, days: 30, price: 1000 }];
    } finally { loading.value = false; }
  };
  
  const allHistory = ref([
    { id: 8293, coin: 'BTC', close: '92434.32', type: 'WIN', profit: '+$185.00' },
    { id: 991, coin: 'BNB', close: '685.12', type: 'LOSS', profit: '-$50.00' }
  ]);
  const filteredHistory = computed(() => allHistory.value.filter(h => h.coin === selectedCoin.value.name));
  
  onMounted(startTimers);
  onUnmounted(stopAllTimers);
  </script>
  
  <style scoped>
  .earn-page { background: #0E0E0E; min-height: 100vh; padding: 16px; color: #fff; font-family: sans-serif; overflow-x: hidden; }
  
  /* 顶部通知条 */
  .top-notification {
    position: fixed; top: 15px; left: 15px; right: 15px; z-index: 12000;
    background: rgba(28, 28, 30, 0.95); border: 1px solid rgba(252, 213, 53, 0.4);
    backdrop-filter: blur(10px); padding: 12px 18px; border-radius: 12px;
    display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 13px;
  }
  .notif-glow { position: absolute; left: 0; width: 4px; height: 60%; background: #FCD535; border-radius: 2px; }
  
  /* 导航 */
  .nav-header { margin-bottom: 24px; }
  .top-nav-tabs { display: flex; background: #1C1C1E; padding: 4px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
  .nav-item { flex: 1; text-align: center; padding: 12px 0; font-size: 14px; color: #8E8E93; border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }
  .nav-item.active { background: #2B3139; color: #FCD535; }
  
  /* 头部状态行 */
  .battle-info-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
  .round-id { background: #2B3139; padding: 4px 10px; border-radius: 6px; font-size: 11px; color: #8E8E93; font-weight: 800; }
  .timer-box { font-weight: 900; color: #FCD535; font-size: 18px; }
  .t-lab { font-size: 10px; opacity: 0.5; font-weight: 400; } /* 修正间距由 &nbsp; 实现 */
  
  /* 价格区药丸 */
  .price-hero { text-align: center; padding: 10px 0; margin-bottom: 15px; }
  .market-selector { display: inline-flex; align-items: center; gap: 8px; background: #1C1C1E; padding: 8px 18px; border-radius: 20px; border: 1px solid #2B3139; cursor: pointer; }
  .m-name { font-weight: 800; font-size: 16px; }
  .m-index-tag { background: #FCD535; color: #000; font-size: 9px; font-weight: 900; padding: 1px 4px; border-radius: 3px; }
  .price-val-wrap { display: flex; align-items: baseline; justify-content: center; margin: 10px 0; }
  .p-integer { font-size: 56px; font-weight: 900; letter-spacing: -2px; }
  .p-decimal { font-size: 24px; font-weight: 700; opacity: 0.8; }
  .feed-note { font-size: 10px; color: #5E5E5E; }
  
  /* 情绪条 */
  .sentiment-section { margin-bottom: 24px; padding: 0 5px; }
  .s-bar { display: flex; height: 16px; border-radius: 8px; overflow: hidden; font-size: 9px; font-weight: 900; border: 1px solid rgba(255,255,255,0.03); }
  .s-fill { transition: width 0.6s ease-in-out; }
  .bull { background: #0ECB81; padding-left: 10px; display: flex; align-items: center; }
  .bear { background: #F6465D; padding-right: 10px; display: flex; align-items: center; justify-content: flex-end; }
  
  /* 按钮组 */
  .action-grid { display: flex; gap: 12px; margin-bottom: 30px; }
  .btn-battle { flex: 1; border: none; padding: 18px; border-radius: 12px; font-size: 20px; font-weight: 900; color: #fff; cursor: pointer; }
  .bullish { background: #0ECB81; }
  .bearish { background: #F6465D; }
  
  /* 战绩列表 */
  .results-container { background: #1C1C1E; border-radius: 20px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); }
  .res-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 20px; }
  .res-title { font-size: 14px; font-weight: 800; color: #FCD535; }
  .res-market { font-size: 11px; color: #5E5E5E; font-weight: 600; }
  .res-table-header { display: flex; font-size: 10px; color: #5E5E5E; font-weight: 900; padding-bottom: 10px; border-bottom: 1px solid #2B3139; }
  .res-row { display: flex; align-items: center; padding: 15px 0; border-bottom: 1px solid #2B3139; }
  .cell-l { flex: 1.5; display: flex; flex-direction: column; gap: 2px; }
  .cell-c { flex: 2; text-align: center; font-family: monospace; font-size: 14px; font-weight: 700; }
  .cell-r { flex: 1.5; text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 3px; }
  .badge { font-size: 9px; font-weight: 900; padding: 2px 6px; border-radius: 4px; }
  .WIN { background: rgba(14,203,129,0.15); color: #0ECB81; }
  .LOSS { background: rgba(246,70,93,0.15); color: #F6465D; }
  .res-empty { text-align: center; padding: 40px 0; color: #444; }
  
  /* 矿机卡片 */
  .miner-card { background: #1C1C1E; border-radius: 20px; padding: 20px; border: 1px solid #2B3139; margin-bottom: 16px; }
  .m-top { display: flex; align-items: center; gap: 15px; margin-bottom: 18px; }
  .m-icon-box { width: 46px; height: 46px; background: #FCD535; color: #000; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 20px; }
  .m-title h3 { margin: 0; font-size: 18px; }
  .m-stats { display: flex; justify-content: space-between; background: #0E0E0E; padding: 14px; border-radius: 10px; margin-bottom: 18px; }
  .v { font-size: 15px; font-weight: 800; }
  .m-buy-btn { width: 100%; background: #FCD535; border: none; padding: 14px; border-radius: 12px; font-weight: 900; font-size: 15px; color: #000; cursor: pointer; }
  
  /* 币种选单 */
  .menu-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 20000; display: flex; align-items: flex-end; }
  .menu-sheet { width: 100%; background: #1C1C1E; border-radius: 24px 24px 0 0; padding: 12px 20px 40px 20px; animation: slideUp 0.3s ease-out; }
  .menu-indicator { width: 40px; height: 4px; background: #2B3139; border-radius: 2px; margin: 0 auto 20px; }
  .menu-title-row { display: flex; justify-content: space-between; font-weight: 800; font-size: 18px; color: #FCD535; margin-bottom: 20px; align-items: center; }
  .coin-item { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #2B3139; border-radius: 16px; margin-bottom: 10px; border: 1px solid transparent; }
  .coin-item.active { border-color: rgba(252,213,53,0.3); background: rgba(252,213,53,0.05); }
  .ci-left { display: flex; align-items: center; gap: 12px; }
  .ci-icon { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
  
  /* 动画 */
  .nav-slide-enter-active, .nav-slide-leave-active { transition: all 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28); }
  .nav-slide-enter-from { transform: translateY(-100px); opacity: 0; }
  .nav-slide-leave-to { transform: translateY(-50px); opacity: 0; }
  @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
  
  .text-green { color: #0ECB81; } .text-red { color: #F6465D; } .text-gold { color: #FCD535; }
  .center { text-align: center; } .right { text-align: right; }
  </style>