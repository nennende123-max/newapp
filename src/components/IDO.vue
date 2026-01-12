<template>
    <div class="ido-page">
      
      <div class="launchpad-header">
        <h2 class="page-title">TruthFi <span class="gold-text">Launchpad</span></h2>
        <p class="page-sub">Access top-tier crypto projects before listing.</p>
      </div>
  
      <div class="project-list">
        
        <div class="project-card live-card">
          <div class="status-badge live">
            <span class="pulse-dot"></span> LIVE
          </div>
  
          <div class="card-header">
            <div class="project-logo">AI</div>
            <div class="project-info">
              <h3 class="project-name">NeuroChain AI <span class="ticker">NCAI</span></h3>
              <div class="tags">
                <span class="tag">AI Infra</span>
                <span class="tag audit-tag">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                  Audited by CertiK
                </span>
              </div>
            </div>
          </div>
  
          <div class="progress-section">
            <div class="progress-info">
              <span>Progress</span>
              <span class="gold-text">84%</span>
            </div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" style="width: 84%"></div>
            </div>
            <div class="raise-detail">
              <span>420,000 / 500,000 USDT</span>
            </div>
          </div>
  
          <div class="data-grid">
            <div class="data-item">
              <span class="label">IDO Price</span>
              <span class="value">$0.045</span>
            </div>
            <div class="data-item">
              <span class="label">Total Raise</span>
              <span class="value">$500K</span>
            </div>
            <div class="data-item">
              <span class="label">Vesting</span>
              <span class="value highlight">20% TGE</span>
            </div>
          </div>
  
          <button class="action-btn primary-btn">Participate Now</button>
        </div>
  
        <div class="project-card upcoming-card">
          <div class="status-badge upcoming">
            <van-icon name="clock-o" /> UPCOMING
          </div>
  
          <div class="card-header">
            <div class="project-logo blue">GM</div>
            <div class="project-info">
              <h3 class="project-name">GameMaster <span class="ticker">GMT</span></h3>
              <div class="tags">
                <span class="tag">GameFi</span>
                <span class="tag audit-tag">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                  SlowMist
                </span>
              </div>
            </div>
          </div>
  
          <div class="countdown-box">
            <p>Subscription starts in:</p>
            <div class="timer">04d : 12h : 30m</div>
          </div>
  
          <div class="data-grid">
            <div class="data-item">
              <span class="label">IDO Price</span>
              <span class="value">$0.12</span>
            </div>
            <div class="data-item">
              <span class="label">Total Raise</span>
              <span class="value">$1.2M</span>
            </div>
            <div class="data-item">
              <span class="label">Min Alloc</span>
              <span class="value">100 USDT</span>
            </div>
          </div>
  
          <button class="action-btn secondary-btn">Set Reminder</button>
        </div>
  
         <div class="project-card ended-card">
          <div class="status-badge ended">ENDED</div>
          <div class="card-header">
            <div class="project-logo grey">DF</div>
            <div class="project-info">
              <h3 class="project-name">DeFi Prime <span class="ticker">DFP</span></h3>
              <div class="tags">
                <span class="tag">DeFi</span>
                <span class="tag text-green">ROI: 450%</span>
              </div>
            </div>
          </div>
          <div class="ended-info">
            Raise Completed: <span class="gold-text">$800,000</span> (100%)
          </div>
        </div>
  
      </div>
    </div>
  </template>
  
  <script setup>
  // 这里逻辑暂时很简单，后续接API
  </script>
  
  <style scoped>
  .ido-page {
    background-color: #0E0E0E;
    min-height: 100vh;
    padding: 16px;
    padding-bottom: 80px; /* 留出底部导航空间 */
    color: #fff;
  }
  
  /* 1. 头部 */
  .launchpad-header {
    margin-bottom: 24px;
  }
  .page-title {
    font-size: 28px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .gold-text { color: #FCD535; }
  .page-sub {
    color: #8E8E93;
    font-size: 13px;
    margin-top: 5px;
  }
  
  /* 2. 卡片通用样式 */
  .project-card {
    background: #1C1C1E;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
    border: 1px solid rgba(255,255,255,0.05);
  }
  
  /* 状态标签 */
  .status-badge {
    position: absolute;
    top: 16px;
    right: 16px;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .live { background: rgba(14, 203, 129, 0.2); color: #0ECB81; }
  .upcoming { background: rgba(252, 213, 53, 0.2); color: #FCD535; }
  .ended { background: #2B3139; color: #8E8E93; }
  
  /* 呼吸灯效果 */
  .pulse-dot {
    width: 6px; height: 6px;
    background-color: #0ECB81;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(14, 203, 129, 0.7); }
    70% { box-shadow: 0 0 0 6px rgba(14, 203, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(14, 203, 129, 0); }
  }
  
  /* 头部信息 */
  .card-header {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }
  .project-logo {
    width: 48px; height: 48px;
    background: #FCD535; color: #000;
    border-radius: 12px;
    display: flex; justify-content: center; align-items: center;
    font-weight: 900; font-size: 16px;
  }
  .project-logo.blue { background: #627EEA; color: #fff; }
  .project-logo.grey { background: #2B3139; color: #8E8E93; }
  
  .project-info {
    display: flex; flex-direction: column; justify-content: center;
  }
  .project-name {
    font-size: 16px; margin: 0 0 6px 0; font-weight: 700;
  }
  .ticker {
    font-size: 12px; color: #8E8E93; font-weight: 400; margin-left: 4px;
  }
  .tags { display: flex; gap: 6px; }
  .tag {
    font-size: 9px; padding: 2px 6px; background: #2B3139; color: #8E8E93;
    border-radius: 3px;
  }
  .audit-tag {
    background: rgba(14, 203, 129, 0.1); color: #0ECB81;
    display: flex; align-items: center; gap: 3px;
  }
  
  /* 进度条 */
  .progress-section { margin-bottom: 20px; }
  .progress-info {
    display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; color: #EAECEF;
  }
  .progress-bar-bg {
    width: 100%; height: 6px; background: #2B3139; border-radius: 3px; overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%; background: #FCD535; border-radius: 3px;
  }
  .raise-detail {
    font-size: 10px; color: #5E5E5E; text-align: right; margin-top: 4px; font-family: monospace;
  }
  
  /* 数据网格 */
  .data-grid {
    display: flex; justify-content: space-between;
    margin-bottom: 20px; background: #161A1E; padding: 12px; border-radius: 8px;
  }
  .data-item { display: flex; flex-direction: column; gap: 4px; }
  .label { font-size: 10px; color: #8E8E93; }
  .value { font-size: 13px; font-weight: 600; color: #EAECEF; }
  .highlight { color: #FCD535; }
  
  /* 倒计时 */
  .countdown-box {
    background: rgba(252, 213, 53, 0.05);
    padding: 12px; border-radius: 8px; text-align: center;
    margin-bottom: 20px; border: 1px dashed rgba(252, 213, 53, 0.3);
  }
  .countdown-box p { margin: 0 0 4px 0; font-size: 10px; color: #FCD535; }
  .timer { font-family: 'DIN Alternate', monospace; font-size: 16px; font-weight: 700; color: #fff; }
  
  /* 按钮 */
  .action-btn {
    width: 100%; padding: 12px; border: none; border-radius: 8px;
    font-weight: 600; font-size: 14px; cursor: pointer;
  }
  .primary-btn { background: #FCD535; color: #000; }
  .primary-btn:active { opacity: 0.8; }
  .secondary-btn { background: #2B3139; color: #fff; }
  .secondary-btn:active { background: #363c45; }
  
  .ended-card { opacity: 0.7; }
  .ended-info { font-size: 12px; color: #8E8E93; margin-top: 10px; }
  .text-green { color: #0ECB81; }
  </style>