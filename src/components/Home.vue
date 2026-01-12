<template>
    <div class="home-page">
      
      <div class="ticker-container">
        <div class="ticker-wrapper">
          <div class="ticker-content">
            🚀 链上实况: 用户 0x8a...9c 刚刚提取 1,200 USDT (Tx: 0x88...1a) &nbsp;&nbsp;|&nbsp;&nbsp; 用户 0xbb...21 赢得了预测对决 (+500 USDT) &nbsp;&nbsp;|&nbsp;&nbsp; 国库今日新增资产 $240,000 &nbsp;&nbsp;|&nbsp;&nbsp; 审计雷达: IDO #829 已通过 CertiK 验证
          </div>
        </div>
      </div>
  
      <div class="scroll-content">
        <div class="hero-section">
          <h1 class="hero-title">TruthFi <span class="gold-dot">.</span></h1>
          <p class="hero-subtitle">The World's First Transparent Asset Platform</p>
        </div>
  
        <div class="trust-dashboard">
          <div class="dashboard-header">
            <span class="dash-title">Platform Transparency</span>
            <div class="audit-badge" @click="showAuditToast">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              <span>Audited by CertiK</span>
            </div>
          </div>
          
          <div class="data-grid">
            <div class="data-item">
              <div class="data-label">Treasury TVL</div>
              <div class="data-value">$ 142.5M</div>
              <div class="data-sub text-green">+1.2% (24h)</div>
            </div>
            <div class="data-item">
              <div class="data-label">Total Payout</div>
              <div class="data-value">$ 8.2M</div>
              <div class="data-sub">Since 2025</div>
            </div>
            <div class="data-item">
              <div class="data-label">24h Txns</div>
              <div class="data-value">45,201</div>
              <div class="data-sub">On-Chain</div>
            </div>
          </div>
        </div>
  
        <div class="quick-actions">
          
          <div class="action-btn" @click="$router.push('/deposit')">
            <div class="icon-circle gold-bg">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1E2329" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"></path>
                <path d="M4 6v12a2 2 0 0 0 2 2h14v-4"></path>
                <path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"></path>
                <path d="M12 8v4"></path> <path d="M9 10l3 3 3-3"></path>
              </svg>
            </div>
            <span>Deposit</span>
          </div>
  
          <div class="action-btn">
            <div class="icon-circle grey-bg">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EAECEF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"></path>
                <path d="M4 6v12a2 2 0 0 0 2 2h14v-4"></path>
                <path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"></path>
                <path d="M12 16v-4"></path> <path d="M9 14l3-3 3 3"></path>
              </svg>
            </div>
            <span>Withdraw</span>
          </div>
  
          <div class="action-btn" @click="$router.push('/miner')">
            <div class="icon-circle grey-bg">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EAECEF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                <polyline points="17 6 23 6 23 12"></polyline>
              </svg>
            </div>
            <span>Earn</span>
          </div>
  
          <div class="action-btn" @click="$router.push('/ido')">
            <div class="icon-circle grey-bg">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EAECEF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 3h12l4 6-10 13L2 9z"></path>
                <path d="M11 3 8 9l4 13 4-13-3-6"></path>
                <path d="M2 9h20"></path>
              </svg>
            </div>
            <span>IDO</span>
          </div>
  
        </div>
  
        <div class="market-section">
          <div class="section-header">
            <h3>Market Overview</h3>
            <span class="more-btn">All Markets ></span>
          </div>
          <div class="market-list">
            <div v-for="coin in marketList" :key="coin.name" class="market-row">
              <div class="row-left">
                <div class="coin-icon-box" :class="coin.name.toLowerCase()">{{ coin.name[0] }}</div>
                <div class="coin-meta">
                  <span class="coin-name">{{ coin.name }} <span class="perp-tag">PERP</span></span>
                  <span class="coin-vol">Vol ${{ coin.vol }}</span>
                </div>
              </div>
              <div class="row-right">
                <span class="price">{{ coin.price }}</span>
                <div class="change-box" :class="coin.change >= 0 ? 'bg-green' : 'bg-red'">
                  {{ coin.change >= 0 ? '+' : '' }}{{ coin.change }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { showToast } from 'vant';
  
  const showAuditToast = () => {
    showToast({ message: 'Redirecting to CertiK Scan...' });
  };
  
  const marketList = ref([
    { name: 'BTC', price: '92,458.20', change: 1.53, vol: '2.4B' },
    { name: 'ETH', price: '3,107.01', change: -1.81, vol: '1.1B' },
    { name: 'BNB', price: '685.16', change: 1.62, vol: '450M' },
    { name: 'SOL', price: '145.20', change: 5.40, vol: '890M' },
    { name: 'DOGE', price: '0.1400', change: -4.14, vol: '200M' },
    { name: 'TRX', price: '0.1250', change: -0.06, vol: '50M' },
  ]);
  </script>
  
  <style scoped>
  .home-page {
    background-color: #0E0E0E;
    color: #fff;
    min-height: 100vh;
  }
  
  /* --- 1. 纯 CSS 跑马灯样式 (核心修改) --- */
  .ticker-container {
    width: 100%;
    height: 40px;
    background: #161A1E;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    overflow: hidden; /* 隐藏超出部分 */
    display: flex;
    align-items: center;
  }
  
  .ticker-wrapper {
    width: 100%;
    overflow: hidden;
  }
  
  .ticker-content {
    display: inline-block;
    white-space: nowrap; /* 强制不换行 */
    padding-left: 100%; /* 从最右侧开始 */
    color: #FCD535;
    font-size: 12px;
    /* 应用动画：25秒滚完一圈，匀速，无限循环 */
    animation: marquee 25s linear infinite;
  }
  
  /* 定义滚动动画 */
  @keyframes marquee {
    0% {
      transform: translate(0, 0);
    }
    100% {
      transform: translate(-100%, 0); /* 向左平移自身宽度的 100% */
    }
  }
  
  .scroll-content {
    padding: 20px 16px; 
  }
  
  /* 2. Hero Section */
  .hero-section {
    margin-bottom: 24px;
  }
  .hero-title {
    font-size: 32px; 
    font-weight: 800;
    margin: 0;
    letter-spacing: -1px;
    line-height: 1.2;
  }
  .gold-dot { color: #FCD535; }
  .hero-subtitle {
    color: #8E8E93;
    font-size: 13px;
    margin: 8px 0 0 0;
    font-weight: 400;
  }
  
  /* 3. 信任仪表盘 */
  .trust-dashboard {
    background: #1C1C1E;
    border-radius: 16px; 
    padding: 20px;
    margin-bottom: 30px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2); 
  }
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  .dash-title {
    font-size: 14px;
    font-weight: 600;
    color: #EAECEF;
    letter-spacing: 0.5px;
  }
  .audit-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: #0ECB81;
    background: rgba(14, 203, 129, 0.15);
    padding: 6px 10px;
    border-radius: 20px; 
    cursor: pointer;
  }
  
  .data-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px; 
  }
  .data-item {
    display: flex;
    flex-direction: column;
  }
  .data-label {
    font-size: 10px;
    color: #8E8E93;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
    text-transform: uppercase; 
  }
  .data-value {
    font-size: 18px; 
    font-weight: 700;
    color: #fff;
    font-family: 'DIN Alternate', sans-serif;
  }
  .data-sub {
    font-size: 10px;
    color: #5E5E5E;
    margin-top: 4px;
  }
  .text-green { color: #0ECB81; }
  
  /* 4. 快捷操作 */
  .quick-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
    padding: 0 8px; 
  }
  .action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: #EAECEF;
    font-weight: 500;
    cursor: pointer;
  }
  .icon-circle {
    width: 52px; 
    height: 52px;
    border-radius: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: opacity 0.2s;
  }
  .icon-circle:active { opacity: 0.8; }
  .gold-bg { background: #FCD535; color: #1E2329; }
  .grey-bg { background: #2B3139; color: #EAECEF; }
  
  /* 5. 行情列表 */
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .section-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: #fff;
  }
  .more-btn {
    font-size: 12px;
    color: #8E8E93;
  }
  
  .market-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05); 
  }
  .row-left { display: flex; align-items: center; gap: 12px; }
  
  .coin-icon-box {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: #2B3139;
    display: flex; justify-content: center; align-items: center;
    font-weight: bold; color: #fff; font-size: 14px;
  }
  .coin-icon-box.btc { background: #F7931A; }
  .coin-icon-box.eth { background: #627EEA; }
  .coin-icon-box.bnb { background: #F3BA2F; }
  
  .coin-meta { display: flex; flex-direction: column; gap: 2px; }
  .coin-name { 
    font-size: 16px; font-weight: 600; color: #fff; 
    display: flex; align-items: center; gap: 6px;
  }
  .perp-tag {
    font-size: 9px; background: rgba(255,255,255,0.1); color: #8E8E93; 
    padding: 2px 4px; border-radius: 3px; font-weight: normal;
  }
  .coin-vol { font-size: 12px; color: #5E5E5E; }
  
  .row-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
  .price { 
    font-size: 16px; font-weight: 600; color: #fff; 
    font-family: 'DIN Alternate', sans-serif;
  }
  .change-box {
    font-size: 12px; font-weight: 600;
    padding: 4px 8px; border-radius: 4px;
    min-width: 60px; text-align: center;
  }
  .bg-green { background: #0ECB81; color: #fff; }
  .bg-red { background: #F6465D; color: #fff; }
  </style>