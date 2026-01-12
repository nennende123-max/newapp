<template>
    <div class="me-page">
      <div class="top-nav">
        <div class="user-profile">
          <div class="avatar-circle"><van-icon name="manager" color="#000" /></div>
          <span class="username">User_8829</span>
        </div>
        <div class="top-icons">
          <van-icon name="eye-o" size="20" class="icon-right" />
          <van-icon name="service-o" size="20" class="icon-right" />
          <van-icon name="setting-o" size="20" class="icon-right" />
        </div>
      </div>
  
      <van-tabs v-model:active="activeTab" background="transparent" title-active-color="#fff" title-inactive-color="#8E8E93" line-width="20px" line-height="3px" color="#D4AF37" :border="false" class="asset-tabs">
        <van-tab title="Overview"></van-tab>
        <van-tab title="Spot"></van-tab>
        <van-tab title="Futures"></van-tab>
        <van-tab title="Earn"></van-tab>
      </van-tabs>
  
      <div class="asset-card">
        <div class="asset-label">
          <span>Est. Total Value</span>
          <van-icon name="eye-o" style="margin-left: 5px" />
        </div>
        <div class="asset-value">
          <span class="currency">USD</span>
          <span class="amount">{{ totalAssetUSD }}</span>
        </div>
        <div class="asset-fiat">≈ ¥ {{ (parseFloat(totalAssetUSD.replace(/,/g, '')) * 7.2).toFixed(2) }}</div>
  
        <div class="action-grid">
          <div class="action-btn primary"><span class="btn-text">Deposit</span></div>
          <div class="action-btn secondary"><span class="btn-text">Withdraw</span></div>
          <div class="action-btn secondary"><span class="btn-text">Transfer</span></div>
        </div>
      </div>
  
      <div class="tools-bar">
        <div class="convert-bnb"><span>Convert small assets to BNB</span><van-icon name="arrow" /></div>
      </div>
      <div class="search-bar">
        <div class="hide-small"><div class="radio-circle"></div><span>Hide 0 balances</span></div>
        <van-icon name="search" size="18" color="#8E8E93" />
      </div>
  
      <div class="coin-list">
        <div class="coin-item" v-for="coin in coinList" :key="coin.name">
          <div class="coin-left">
            <div class="coin-icon" :class="coin.name.toLowerCase()">{{ coin.name[0] }}</div>
            <div class="coin-info">
              <span class="coin-name">{{ coin.name }}</span>
              <span class="coin-fullname">{{ coin.fullname }}</span>
            </div>
          </div>
          
          <div class="coin-right">
            <span class="coin-balance">{{ coin.balance }}</span>
            <span class="coin-price">$ {{ (coin.balance * coin.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
    import { ref, computed } from 'vue';
    
    const activeTab = ref(1); // 默认选中 'Spot'
    
    // 1. 模拟数据：为了演示排序，我给每个币都预设了不同的数量和价格
    // 注意：balance = 持有数量, price = 单价
    const rawCoinList = ref([
      { name: 'USDT', fullname: 'TetherUS', balance: 5402.00, price: 1.00 },     // 总价 $5402 (排第2)
      { name: 'BTC',  fullname: 'Bitcoin',  balance: 0.15,    price: 92000.00 }, // 总价 $13800 (排第1)
      { name: 'ETH',  fullname: 'Ethereum', balance: 0.00,    price: 3200.00 },  // 总价 $0 (排后面)
      { name: 'BNB',  fullname: 'BNB',      balance: 10.50,   price: 620.00 },   // 总价 $6510 (排第? 自己算)
      { name: 'DOGE', fullname: 'Dogecoin', balance: 9999.00, price: 0.14 },     // 总价 $1399
      { name: 'TRX',  fullname: 'Tron',     balance: 0.00,    price: 0.12 },
      { name: 'USDC', fullname: 'USD Coin', balance: 0.00,    price: 1.00 },
    ]);
    
    // 2. 自动排序逻辑 (核心代码)
    // 它会实时计算 (数量 * 价格)，然后从大到小排列
    const coinList = computed(() => {
      // 复制一份数据以免影响原数据
      const sorted = [...rawCoinList.value];
      
      // sort 函数：如果 b 的价值大于 a，就把 b 排在前面
      sorted.sort((a, b) => {
        const valueA = a.balance * a.price;
        const valueB = b.balance * b.price;
        return valueB - valueA; // 降序排列 (大 -> 小)
      });
    
      return sorted;
    });
    
    // 3. 辅助工具：算出所有币的总资产显示在卡片上
    const totalAssetUSD = computed(() => {
      let total = 0;
      rawCoinList.value.forEach(coin => {
        total += coin.balance * coin.price;
      });
      return total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    });
    </script>
  
  <style scoped>
  /* 页面容器 */
  .me-page {
    background-color: #000;
    min-height: 100vh;
    padding-bottom: 80px; /* 给底部导航留位置 */
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
  }
  
  /* 1. 顶部导航 */
  .top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 16px 10px;
  }
  .user-profile {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .avatar-circle {
    width: 28px;
    height: 28px;
    background-color: #333;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .username {
    font-weight: 600;
    font-size: 16px;
  }
  .top-icons {
    display: flex;
    gap: 16px;
    color: #fff;
  }
  
  /* 2. Tabs */
  .asset-tabs {
    margin-bottom: 10px;
  }
  :deep(.van-tab) {
    font-size: 15px;
    font-weight: 500;
    padding: 0 10px;
  }
  
  /* 3. 资产卡片 */
  .asset-card {
    padding: 0 16px;
    margin-bottom: 20px;
  }
  .asset-label {
    color: #8E8E93;
    font-size: 12px;
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }
  .asset-value {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .asset-value .amount {
    font-size: 32px;
    font-weight: bold;
    font-family: 'DIN Alternate', sans-serif; /* 数字字体 */
  }
  .asset-value .currency {
    font-size: 14px;
    font-weight: 600;
  }
  .asset-fiat {
    color: #8E8E93;
    font-size: 14px;
    margin-top: 4px;
    margin-bottom: 20px;
  }
  
  /* 按钮组 */
  .action-grid {
    display: flex;
    gap: 12px;
  }
  .action-btn {
    flex: 1;
    height: 44px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 4px; /* 稍微方一点的圆角 */
    font-weight: 600;
    font-size: 15px;
  }
  .primary {
    background-color: #FCD535; /* 币安黄 */
    color: #1E2329;
  }
  .secondary {
    background-color: #2B3139; /* 深灰底 */
    color: #EAECEF;
  }
  
  /* 4. 工具栏 */
  .tools-bar {
    padding: 0 16px;
    margin-bottom: 20px;
  }
  .convert-bnb {
    background-color: #1C1C1E;
    padding: 10px 12px;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #EAECEF;
    font-size: 13px;
  }
  
  /* 5. 搜索栏 */
  .search-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    margin-bottom: 16px;
  }
  .hide-small {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #8E8E93;
    font-size: 13px;
  }
  .radio-circle {
    width: 14px;
    height: 14px;
    border: 1px solid #5E5E5E;
    border-radius: 50%;
  }
  
  /* 6. 列表样式 */
  .coin-list {
    display: flex;
    flex-direction: column;
  }
  .coin-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #141414; /* 极淡的分割线 */
  }
  .coin-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .coin-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #333;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    font-size: 14px;
    color: #fff;
  }
  /* 给不同币种一些简单的颜色区分 */
  .coin-icon.usdt { background: #26A17B; }
  .coin-icon.btc { background: #F7931A; }
  .coin-icon.eth { background: #627EEA; }
  .coin-icon.bnb { background: #F3BA2F; }
  
  .coin-info {
    display: flex;
    flex-direction: column;
  }
  .coin-name {
    font-size: 16px;
    font-weight: 500;
    color: #EAECEF;
  }
  .coin-fullname {
    font-size: 12px;
    color: #848E9C;
  }
  .coin-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }
  .coin-balance {
    font-size: 16px;
    color: #EAECEF;
    font-weight: 500;
  }
  .coin-price {
    font-size: 12px;
    color: #848E9C;
  }
  </style>