<template>
  <div class="trade-page">
    <!-- 顶部导航栏 -->
    <div class="trade-header">
      <div class="header-left" @click="$router.back()">
        <div class="header-action-left">
          <svg viewBox="0 0 1024 1024" class="custom-back-svg">
            <path d="M685.248 103.808L289.088 500l396.16 396.192 56.576-56.576L345.664 500l339.584-339.616z" fill="#FCD535"></path>
          </svg>
        </div>
      </div>
      <div class="header-center">
        <span class="page-title">交易</span>
      </div>
      <div class="nav-right-icon-wrap" @click="goToKlineChart">
        <svg viewBox="0 0 1024 1024" class="kline-svg-icon">
          <path d="M896 128H128a64 64 0 0 0-64 64v640a64 64 0 0 0 64 64h768a64 64 0 0 0 64-64V192a64 64 0 0 0-64-64zM320 768H192V448h128v320zm256 0H448V256h128v512zm256 0H704V512h128v256z" fill="#FCD535"></path>
        </svg>
      </div>
    </div>

    <!-- 标签栏：现货/杠杆 -->
    <div class="trade-tabs">
      <div 
        class="tab-item" 
        :class="{ active: activeTradeTab === 'spot' }"
        @click="activeTradeTab = 'spot'"
      >
        现货
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTradeTab === 'leverage' }"
        @click="activeTradeTab = 'leverage'"
      >
        杠杆
      </div>
    </div>

    <!-- 交易对信息 -->
    <div class="pair-info">
      <div class="pair-selector" @click="showCoinSelect = true">
        <span class="pair-name">{{ symbol }}/USDT</span>
        <van-icon name="arrow-down" size="12" color="#FFFFFF" style="margin-left: 4px" />
      </div>
      <div class="price-change" :class="{ positive: priceChange >= 0 }">
        {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
      </div>
    </div>

    <!-- 核心交易区 - 左右布局 -->
    <div class="trade-main">
      <!-- 左侧：盘口区 (42%) -->
      <div class="orderbook-side">
        <!-- 表头 -->
        <div class="orderbook-header">
          <span class="header-price">价格 (USDT)</span>
          <span class="header-quantity">数量 (BTC)</span>
        </div>

        <!-- 卖单列表 (Asks) - 倒序 -->
        <div class="asks-list">
          <div 
            v-for="(ask, index) in asks" 
            :key="`ask-${index}`"
            class="order-row ask-row"
            :style="{ '--depth-width': getDepthWidth(ask.quantity, asks, 'asks') + '%' }"
            @click="selectPrice(ask.price, 'sell')"
          >
            <div class="depth-bar ask-depth"></div>
            <span class="price ask-price">{{ formatPrice(ask.price) }}</span>
            <span class="quantity">{{ formatQuantity(ask.quantity) }}</span>
          </div>
        </div>

        <!-- 最新成交价 (Middle) -->
        <div class="last-price" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
          <div class="price-main">{{ formatPrice(lastPrice) }}</div>
          <div class="price-fiat">${{ formatPrice(lastPrice) }}</div>
        </div>

        <!-- 买单列表 (Bids) - 正序 -->
        <div class="bids-list">
          <div 
            v-for="(bid, index) in bids" 
            :key="`bid-${index}`"
            class="order-row bid-row"
            :style="{ '--depth-width': getDepthWidth(bid.quantity, bids, 'bids') + '%' }"
            @click="selectPrice(bid.price, 'buy')"
          >
            <div class="depth-bar bid-depth"></div>
            <span class="price bid-price">{{ formatPrice(bid.price) }}</span>
            <span class="quantity">{{ formatQuantity(bid.quantity) }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧：交易表单 (58%) -->
      <div class="form-side">
        <!-- 买/卖切换 -->
        <div class="buy-sell-toggle">
          <div 
            class="toggle-btn buy-btn" 
            :class="{ active: orderSide === 'buy' }"
            @click="orderSide = 'buy'"
          >
            买入
          </div>
          <div 
            class="toggle-btn sell-btn" 
            :class="{ active: orderSide === 'sell' }"
            @click="orderSide = 'sell'"
          >
            卖出
          </div>
        </div>

        <!-- 杠杆控制栏 -->
        <div v-if="activeTradeTab === 'leverage'" class="leverage-control-bar">
          <button class="leverage-btn" @click="showLeveragePopup = true">
            <span>全仓</span>
            <span class="leverage-value">{{ currentLeverage }}x</span>
            <van-icon name="arrow-down" size="12" color="#848E9C" />
          </button>
        </div>

        <!-- 订单类型选择器 -->
        <div class="order-type-selector" @click="showOrderTypeSheet = true">
          <span>{{ orderType === 'limit' ? '限价单' : '市价单' }}</span>
          <van-icon name="arrow-down" size="12" color="#848E9C" />
        </div>

        <!-- 价格输入 -->
        <div class="input-row">
          <input
            v-if="orderType === 'limit'"
            v-model="price"
            type="number"
            :placeholder="lastPrice.toFixed(currentCoinConfig.priceFixed)"
            class="input-field"
          />
          <input
            v-else
            type="text"
            value="以当前最优价格成交"
            disabled
            class="input-field market-price-input"
          />
        </div>

        <!-- 估值 -->
        <div class="estimated-row">
          <span class="est-label">估值</span>
          <span class="est-value">≈ ¥{{ formatFiatPrice(parseFloat(price) || lastPrice) }}</span>
        </div>

        <!-- 数量输入 -->
        <div class="input-row">
          <span class="input-label">数量({{ currentCoinConfig.baseCoin }})</span>
          <input
            v-model="amount"
            type="number"
            min="0"
            step="0.0001"
            placeholder="请输入数量"
            class="input-field"
            @input="handleAmountInput"
          />
        </div>

        <!-- 百分比快捷键 -->
        <div class="percent-row">
          <div 
            v-for="percent in [25, 50, 75, 100]"
            :key="percent"
            class="percent-btn"
            :class="{ active: selectedPercent === percent }"
            @click="setAmountPercent(percent)"
          >
            {{ percent }}%
          </div>
        </div>

        <!-- 成交金额 -->
        <div class="total-row">
          <span class="total-label">成交金额(USDT)</span>
          <span class="total-value">{{ formatTotalAmount }}</span>
        </div>

        <!-- 可用资产信息 -->
        <div class="available-row">
          <div class="avail-item">
            <span class="avail-label">可用：</span>
            <span class="avail-value">{{ formatAvailableBalance }}</span>
            <van-icon 
              name="plus" 
              size="12" 
              color="#FCD535" 
              style="margin-left: 4px; cursor: pointer;" 
              @click.stop="router.push('/deposit')" 
            />
          </div>
          <div class="avail-item">
            <span class="avail-label">可卖：</span>
            <span class="avail-value">{{ formatSellableBalance }}</span>
          </div>
        </div>

        <!-- 下单按钮 -->
        <button 
          class="submit-btn"
          :class="orderSide"
          :disabled="!isOrderValid"
          @click="handleSubmitOrder"
        >
          {{ orderSide === 'buy' ? '买入' : '卖出' }} {{ symbol }}
        </button>
      </div>
    </div>

    <!-- 底部：委托与资产 -->
    <div class="bottom-section">
      <div class="bottom-tabs">
        <div 
          class="tab-item"
          :class="{ active: activeOrderTab === 'orders' }"
          @click="activeOrderTab = 'orders'"
        >
          当前委托
        </div>
        <div 
          class="tab-item"
          :class="{ active: activeOrderTab === 'assets' }"
          @click="activeOrderTab = 'assets'"
        >
          资产
        </div>
      </div>

      <div class="bottom-content">
        <transition name="fade" mode="out-in">
          <div v-if="activeOrderTab === 'orders'" key="orders" class="orders-panel">
            <!-- 空状态 -->
            <div v-if="ordersList.length === 0" class="orders-empty">
              <div class="empty-icon">
                <van-icon name="orders-o" size="48" color="#848E9C" />
              </div>
              <div class="empty-text">暂无挂单</div>
              <button class="empty-action-btn" @click="scrollToTop">
                去交易
              </button>
            </div>
            <!-- 订单列表 -->
            <div v-else class="orders-list">
              <div 
                v-for="(order, index) in ordersList"
                :key="index"
                class="order-item"
              >
                <!-- 左侧：买入/卖出 + 币种 + 时间 -->
                <div class="order-left">
                  <div class="order-side-badge" :class="order.side">
                    {{ order.side === 'buy' ? '买入' : '卖出' }}
                  </div>
                  <div class="order-symbol-time">
                    <span class="order-symbol">{{ order.symbol }}</span>
                    <span class="order-time">{{ formatOrderTime(order.timestamp) }}</span>
                  </div>
                </div>
                
                <!-- 中间：价格和数量 -->
                <div class="order-center">
                  <div class="order-price">{{ formatPrice(order.price) }}</div>
                  <div class="order-quantity">{{ formatQuantity(order.quantity) }} / {{ formatQuantity(order.quantity) }}</div>
                </div>
                
                <!-- 右侧：撤单按钮 -->
                <div class="order-right">
                  <button class="cancel-btn" @click="cancelOrder(index)">撤单</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else key="assets" class="assets-panel">
            <div class="assets-list">
              <div class="asset-item">
                <span class="asset-label">可用</span>
                <span class="asset-value">{{ formatNumber(availableBalance) }} {{ symbol }}</span>
              </div>
              <div class="asset-item">
                <span class="asset-label">冻结</span>
                <span class="asset-value">{{ formatNumber(frozenBalance) }} {{ symbol }}</span>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- 币种选择弹窗 -->
    <van-popup
      v-model:show="showCoinSelect"
      position="bottom"
      :style="{ height: '60%' }"
      round
      class="coin-select-popup"
    >
      <div class="coin-select-container">
        <div class="coin-select-header">
          <h3 class="coin-select-title">切换币种</h3>
        </div>
        <div class="coin-list">
          <div
            v-for="coin in coinList"
            :key="coin.symbol"
            class="coin-item"
            :class="{ 'coin-item-active': coin.symbol === symbol }"
            @click="switchCoin(coin.symbol)"
          >
            <div class="coin-name">{{ coin.symbol }}</div>
            <div class="coin-pair">{{ coin.symbol }}/USDT</div>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 订单类型选择 ActionSheet -->
    <van-action-sheet
      v-model:show="showOrderTypeSheet"
      :actions="orderTypeOptions"
      @select="onOrderTypeSelect"
      cancel-text="取消"
      title="选择订单类型"
    />

    <!-- 杠杆倍数选择弹窗 -->
    <van-popup
      v-model:show="showLeveragePopup"
      position="bottom"
      :style="{ height: '40%' }"
      round
      class="leverage-popup"
    >
      <div class="leverage-popup-content">
        <div class="leverage-popup-header">
          <h3 class="leverage-popup-title">选择杠杆倍数</h3>
          <van-icon name="cross" @click="showLeveragePopup = false" class="close-icon" />
        </div>
        <div class="leverage-options">
          <div
            v-for="leverage in leverageOptions"
            :key="leverage"
            class="leverage-option"
            :class="{ active: currentLeverage === leverage }"
            @click="selectLeverage(leverage)"
          >
            <span>{{ leverage }}x</span>
            <van-icon v-if="currentLeverage === leverage" name="success" color="#FCD535" />
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast, Icon, Popup, Empty, ActionSheet } from 'vant';
import { useAssetStore } from '@/stores/assets';

const route = useRoute();
const router = useRouter();
const assetStore = useAssetStore();

// 获取 URL 里的 symbol，如果没有则默认显示 BTC
const symbol = ref(route.query.symbol || 'BTC');

// 币种配置表
const coinConfigs = {
  'ETH/USDT': { priceFixed: 2, amountFixed: 4, step: 0.1, baseCoin: 'ETH' },
  'BTC/USDT': { priceFixed: 2, amountFixed: 6, step: 0.01, baseCoin: 'BTC' },
  'BNB/USDT': { priceFixed: 2, amountFixed: 4, step: 0.1, baseCoin: 'BNB' },
  'SOL/USDT': { priceFixed: 2, amountFixed: 4, step: 0.1, baseCoin: 'SOL' },
  'DOGE/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'DOGE' },
  'TRX/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'TRX' },
  'BEAT/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'BEAT' },
  'AIC/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'AIC' }
};

// 当前选中的币种对
const selectedCoin = computed(() => {
  return `${symbol.value}/USDT`;
});

// 当前币种配置
const currentCoinConfig = computed(() => {
  return coinConfigs[selectedCoin.value] || coinConfigs['BTC/USDT'];
});

// 币种选择弹窗
const showCoinSelect = ref(false);

// 币种列表
const coinList = ref([
  { symbol: 'BTC' },
  { symbol: 'ETH' },
  { symbol: 'BNB' },
  { symbol: 'SOL' },
  { symbol: 'DOGE' },
  { symbol: 'TRX' },
  { symbol: 'BEAT' },
  { symbol: 'AIC' }
]);

// 状态管理
const activeTradeTab = ref('spot');
const orderSide = ref(route.query.side === 'buy' || route.query.side === 'sell' ? route.query.side : 'buy');
const orderType = ref('limit'); // 'limit' 或 'market'
const price = ref('');
const amount = ref('');
const priceChange = ref(1.83);
const lastPrice = ref(92255.50);
const activeOrderTab = ref('orders');
const selectedPercent = ref(null);
const ordersList = ref([]);
const showOrderTypeSheet = ref(false);
const currentLeverage = ref(20); // 默认 20 倍
const showLeveragePopup = ref(false); // 控制调整倍数的弹窗

// 模拟盘口数据
const asks = ref([
  { price: 92255.80, quantity: 0.00006 },
  { price: 92255.59, quantity: 0.00709 },
  { price: 92255.58, quantity: 0.00012 },
  { price: 92255.52, quantity: 0.00006 },
  { price: 92255.51, quantity: 0.00063 },
  { price: 92255.50, quantity: 3.04039 }
]);

const bids = ref([
  { price: 92255.49, quantity: 3.30750 },
  { price: 92255.48, quantity: 0.00025 },
  { price: 92255.47, quantity: 0.00012 },
  { price: 92255.46, quantity: 0.00079 },
  { price: 92255.45, quantity: 0.00121 },
  { price: 92255.44, quantity: 0.05419 }
]);

// 监听路由变化
watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
  }
});

watch(() => route.query.side, (newSide) => {
  if (newSide === 'buy' || newSide === 'sell') {
    orderSide.value = newSide;
  }
}, { immediate: true });

// 动态价格步长
const priceStep = computed(() => {
  return currentCoinConfig.value.step;
});

// 可用余额
const availableBalance = computed(() => {
  try {
    let realBalance = 0;
    
    if (orderSide.value === 'buy') {
      realBalance = assetStore?.usdtBalance || 0;
    } else {
      realBalance = assetStore?.getHolding(symbol.value) || 0;
    }
    
    // 如果是杠杆模式，返回真实资产 * 杠杆倍数
    if (activeTradeTab.value === 'leverage') {
      return realBalance * currentLeverage.value;
    }
    
    // 现货模式，返回真实资产
    return realBalance;
  } catch (error) {
    console.error('Error getting available balance:', error);
    return 0;
  }
});

const frozenBalance = computed(() => {
  return 0;
});

// 格式化函数
const formatPrice = (value) => {
  if (!value) return '0.00';
  const config = currentCoinConfig.value;
  return value.toLocaleString('en-US', {
    minimumFractionDigits: config.priceFixed,
    maximumFractionDigits: config.priceFixed
  });
};

const formatQuantity = (value) => {
  if (!value) return '0.00000000';
  const config = currentCoinConfig.value;
  return value.toFixed(config.amountFixed);
};

const formatFiatPrice = (value) => {
  const cnyPrice = value * 7.2;
  if (cnyPrice >= 1000000) {
    return (cnyPrice / 1000000).toFixed(2) + 'M';
  } else if (cnyPrice >= 1000) {
    return (cnyPrice / 1000).toFixed(0) + 'K';
  }
  return cnyPrice.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });
};

const formatNumber = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  });
};

// 深度宽度计算
const getDepthWidth = (quantity, list, type) => {
  if (!list || list.length === 0) return 0;
  const maxQuantity = Math.max(...list.map(item => item.quantity));
  if (maxQuantity === 0) return 0;
  return (quantity / maxQuantity) * 100;
};

// 选择价格
const selectPrice = (selectedPrice, side) => {
  const config = currentCoinConfig.value;
  price.value = selectedPrice.toFixed(config.priceFixed);
  if (side !== orderSide.value) {
    orderSide.value = side;
  }
};

// 调整价格
const adjustPrice = (direction) => {
  const currentPrice = parseFloat(price.value) || lastPrice.value;
  const step = priceStep.value;
  const config = currentCoinConfig.value;
  const newPrice = currentPrice + (direction * step);
  price.value = newPrice.toFixed(config.priceFixed);
};

// 处理数量输入（拦截负数）
const handleAmountInput = (e) => {
  let value = e.target.value;
  
  // 1. 禁止负号 '-'
  if (value.includes('-')) {
    value = value.replace(/-/g, '');
  }
  
  // 2. 确保不小于 0
  const numValue = parseFloat(value);
  if (!isNaN(numValue) && numValue < 0) {
    value = Math.abs(numValue).toString();
  }
  
  // 如果输入为空或只包含非数字字符（除了小数点），保持原值或清空
  if (value === '' || value === '-') {
    amount.value = '';
    return;
  }
  
  // 更新 v-model
  amount.value = value;
};

// 调整数量
const adjustAmount = (direction) => {
  const currentAmount = parseFloat(amount.value) || 0;
  const config = currentCoinConfig.value;
  const step = Math.pow(10, -config.amountFixed);
  const newAmount = Math.max(0, currentAmount + (direction * step));
  amount.value = newAmount.toFixed(config.amountFixed);
};

// 设置数量百分比
const setAmountPercent = (percent) => {
  selectedPercent.value = percent;
  try {
    const balance = availableBalance.value;
    if (balance <= 0) {
      showToast({ message: '余额不足', duration: 2000 });
      return;
    }
    
    const config = currentCoinConfig.value;
    if (orderSide.value === 'buy') {
      const totalCost = balance * (percent / 100);
      const calculatedAmount = totalCost / (parseFloat(price.value) || lastPrice.value);
      amount.value = calculatedAmount.toFixed(config.amountFixed);
    } else {
      const calculatedAmount = balance * (percent / 100);
      amount.value = calculatedAmount.toFixed(config.amountFixed);
    }
  } catch (error) {
    console.error('Error setting amount percent:', error);
    showToast({ message: '计算数量失败', duration: 2000 });
  }
};

// 成交金额
const formatTotalAmount = computed(() => {
  const p = parseFloat(price.value) || 0;
  const a = parseFloat(amount.value) || 0;
  const total = p * a;
  return total > 0 ? total.toFixed(2) : '0.00';
});

// 可用余额显示
const formatAvailableBalance = computed(() => {
  if (orderSide.value === 'buy') {
    return formatNumber(availableBalance.value) + ' USDT';
  } else {
    return formatNumber(availableBalance.value) + ' ' + symbol.value;
  }
});

// 可卖余额显示
const formatSellableBalance = computed(() => {
  if (orderSide.value === 'buy') {
    return formatNumber(availableBalance.value) + ' ' + symbol.value;
  } else {
    return formatNumber(availableBalance.value) + ' USDT';
  }
});

// 订单类型选项
const orderTypeOptions = [
  { name: '限价单', type: 'limit' },
  { name: '市价单', type: 'market' }
];

// 订单类型选择处理
const onOrderTypeSelect = (action) => {
  orderType.value = action.type;
  showOrderTypeSheet.value = false;
  
  // 切换为限价单时，如果价格为空，设置为最新价格
  if (action.type === 'limit' && !price.value) {
    price.value = lastPrice.value.toFixed(currentCoinConfig.value.priceFixed);
  }
};

// 杠杆倍数选项
const leverageOptions = [1, 2, 3, 5, 10, 20, 50, 100];

// 选择杠杆倍数
const selectLeverage = (leverage) => {
  currentLeverage.value = leverage;
  showLeveragePopup.value = false;
};

// 订单验证
const isOrderValid = computed(() => {
  const a = parseFloat(amount.value);
  if (orderType.value === 'market') {
    // 市价单只需要数量
    return a > 0;
  } else {
    // 限价单需要价格和数量
    const p = parseFloat(price.value);
    return p > 0 && a > 0;
  }
});

// 格式化订单时间
const formatOrderTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// 滚动到顶部（去交易）
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// 提交订单
const handleSubmitOrder = () => {
  // 双重保险：严厉校验数量必须大于 0
  const amountValue = parseFloat(amount.value);
  if (isNaN(amountValue) || amountValue <= 0) {
    showToast({ message: '数量必须大于 0', icon: 'fail' });
    return;
  }
  
  if (!isOrderValid.value) {
    showToast({ message: '请填写完整信息', duration: 2000 });
    return;
  }
  
  // 市价单使用最新成交价，限价单使用用户输入的价格
  const orderPrice = orderType.value === 'market' 
    ? lastPrice.value 
    : parseFloat(price.value);
  
  const order = {
    side: orderSide.value,
    type: orderType.value, // 添加订单类型
    price: orderPrice,
    quantity: parseFloat(amount.value),
    symbol: symbol.value,
    timestamp: Date.now() // 添加时间戳
  };
  
  ordersList.value.push(order);
  showToast({ 
    message: orderType.value === 'market' ? '市价单提交成功' : '限价单提交成功', 
    duration: 2000 
  });
  
  // 清空表单
  if (orderType.value === 'limit') {
    price.value = '';
  }
  amount.value = '';
  selectedPercent.value = null;
};

// 撤销订单
const cancelOrder = (index) => {
  ordersList.value.splice(index, 1);
  showToast({ message: '订单已撤销', duration: 2000 });
};

// 跳转到K线图页面
const goToKlineChart = () => {
  router.push({
    path: '/market',
    query: {
      symbol: symbol.value
    }
  });
};

// 切换币种
const switchCoin = (newSymbol) => {
  symbol.value = newSymbol;
  showCoinSelect.value = false;
  
  router.push({
    path: '/trade',
    query: {
      symbol: newSymbol,
      side: orderSide.value
    }
  });
  
  showToast({ message: `已切换到 ${newSymbol}/USDT`, duration: 1500 });
};

// 初始化模拟数据
onMounted(() => {
  // 如果列表为空，生成2条模拟订单数据
  if (ordersList.value.length === 0) {
    const now = Date.now();
    
    // 买入订单：价格略低于当前价
    const buyPrice = lastPrice.value * 0.998; // 低于当前价 0.2%
    ordersList.value.push({
      side: 'buy',
      type: 'limit',
      price: buyPrice,
      quantity: 0.0015,
      symbol: symbol.value,
      timestamp: now - 300000 // 5分钟前
    });
    
    // 卖出订单：价格略高于当前价
    const sellPrice = lastPrice.value * 1.002; // 高于当前价 0.2%
    ordersList.value.push({
      side: 'sell',
      type: 'limit',
      price: sellPrice,
      quantity: 0.002,
      symbol: symbol.value,
      timestamp: now - 180000 // 3分钟前
    });
  }
});
</script>

<style scoped>
/* ========== 全局容器 ========== */
.trade-page {
  background-color: #000000;
  min-height: 100vh;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
}

/* ========== 顶部导航栏 ========== */
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 16px;
  background-color: #000000;
  position: sticky;
  top: 0;
  z-index: 999;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-left {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

/* 确保右侧图标容器拥有最高层级，防止被中间标题遮挡 */
.nav-right-icon-wrap {
  width: 44px;
  height: 44px;
  display: flex !important;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  z-index: 99; /* 提高层级 */
  transition: opacity 0.2s ease;
}

.nav-right-icon-wrap:hover {
  opacity: 0.8;
}

.nav-right-icon-wrap:active {
  opacity: 0.6;
}

/* 强制定义 SVG 尺寸和颜色 */
.kline-svg-icon {
  width: 22px !important;
  height: 22px !important;
  fill: #FCD535 !important;
  display: block !important;
}

.header-action-left {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.custom-back-svg {
  width: 24px;
  height: 24px;
  fill: #FCD535 !important;
  filter: drop-shadow(0 0 1px rgba(252, 213, 53, 0.3));
}

/* 修正中间标题，确保它不会横向撑开挡住右侧点击区域 */
.header-center {
  position: absolute; /* 改为绝对定位居中，彻底解决遮挡问题 */
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  pointer-events: none; /* 让中间区域不响应点击，防止干扰两侧 */
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  pointer-events: auto; /* 仅文字响应点击（如果有切换需求） */
}

/* ========== 标签栏：现货/杠杆 ========== */
.trade-tabs {
  display: flex;
  padding: 0 16px;
  gap: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.trade-tabs .tab-item {
  padding: 12px 0;
  font-size: 14px;
  color: #848E9C;
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;
}

.trade-tabs .tab-item.active {
  color: #FFFFFF;
  font-weight: 600;
}

.trade-tabs .tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #FCD535;
}

/* ========== 交易对信息 ========== */
.pair-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.pair-selector {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.pair-name {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

.price-change {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.price-change.positive {
  color: #0ECB81;
  background-color: rgba(14, 203, 129, 0.1);
}

.price-change.negative {
  color: #F6465D;
  background-color: rgba(246, 70, 93, 0.1);
}

/* ========== 核心交易区 - Flex 布局 ========== */
.trade-main {
  display: flex;
  gap: 8px;
  flex: 1;
  min-height: 0;
  padding: 8px 8px 8px 0;
}

/* ========== 左侧：盘口区 (42%) ========== */
.orderbook-side {
  width: 42%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 确保所有元素从顶部开始紧密堆叠 */
  background-color: #0E0E0E;
  border-radius: 4px;
  overflow: hidden;
  padding: 0;
}

/* 表头 */
.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 4px 8px !important; /* 进一步压缩表头高度 */
  font-size: 11px;
  color: #848E9C;
  border-bottom: none !important; /* 移除表头下边框，消除视觉间隙 */
}

.header-price {
  flex: 1;
  text-align: left;
}

.header-quantity {
  flex: 1;
  text-align: right;
}

/* 1. 移除强制填充，让列表高度由内容(20px * 行数)决定 */
.asks-list, .bids-list {
  display: flex;
  flex-direction: column; /* 统一为标准向下排列 */
  flex: none !important; /* 彻底禁止拉伸 */
  min-height: 0;
  overflow-y: auto;
}

/* 盘口行 - 强制 20px 高度 */
.order-row {
  position: relative;
  height: 20px !important;
  line-height: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
  margin: 0 !important; /* 彻底消除 margin 导致的留白 */
  cursor: pointer;
  overflow: hidden;
}

/* 深度条 */
.depth-bar {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: var(--depth-width, 0%);
  height: 100%;
  z-index: 0;
  transition: width 0.3s ease;
}

.ask-depth {
  background: linear-gradient(to left, rgba(246, 70, 93, 0.1) 0%, rgba(246, 70, 93, 0.05) 100%);
}

.bid-depth {
  background: linear-gradient(to left, rgba(14, 203, 129, 0.1) 0%, rgba(14, 203, 129, 0.05) 100%);
}

/* 价格和数量 */
.order-row .price {
  position: relative;
  z-index: 1;
  font-size: 11px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.ask-price {
  color: #F6465D;
  text-align: left;
  flex: 1;
}

.bid-price {
  color: #0ECB81;
  text-align: left;
  flex: 1;
}

.order-row .quantity {
  position: relative;
  z-index: 1;
  font-size: 11px;
  color: #848E9C;
  text-align: right;
  flex: 1;
  font-variant-numeric: tabular-nums;
}

/* 最新成交价 - 32px 高度 */
.last-price {
  flex-shrink: 0;
  height: 32px;
  background-color: #1C1C1E;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 4px 0;
  margin: 0 !important; /* 消除 margin 导致的留白 */
}

.price-main {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.price-fiat {
  font-size: 11px;
  color: #848E9C;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  margin-top: 2px;
}

.last-price.up .price-main {
  color: #0ECB81 !important;
}

.last-price.down .price-main {
  color: #F6465D !important;
}

/* ========== 右侧：交易表单 (58%) ========== */
.form-side {
  width: 58%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 买/卖切换 */
.buy-sell-toggle {
  display: flex;
  gap: 0;
  background-color: #1C1C1E;
  border-radius: 4px;
  padding: 2px;
}

.toggle-btn {
  flex: 1;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #848E9C;
}

.buy-btn.active {
  background-color: #0ECB81;
  color: #000000;
}

.sell-btn.active {
  background-color: #F6465D;
  color: #FFFFFF;
}

/* 订单类型选择器 */
.order-type-selector {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background-color: #1C1C1E;
  border-radius: 4px;
  font-size: 13px;
  color: #EAECEF;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.order-type-selector:active {
  background-color: #252A32;
}

/* 杠杆控制栏 */
.leverage-control-bar {
  margin-bottom: 8px;
}

.leverage-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  font-size: 12px;
  color: #EAECEF;
  cursor: pointer;
  transition: all 0.2s ease;
}

.leverage-btn:active {
  background-color: #252A32;
  border-color: rgba(252, 213, 53, 0.3);
}

.leverage-value {
  color: #FCD535;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* 杠杆弹窗 */
.leverage-popup {
  background: #1C1C1E;
}

:deep(.leverage-popup .van-popup) {
  background: #1C1C1E;
}

.leverage-popup-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.leverage-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.leverage-popup-title {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
}

.close-icon {
  font-size: 20px;
  color: #848E9C;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-icon:active {
  color: #FFFFFF;
}

.leverage-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.leverage-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #141414;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #EAECEF;
  cursor: pointer;
  transition: all 0.2s ease;
  font-variant-numeric: tabular-nums;
}

.leverage-option:active {
  background-color: #252A32;
}

.leverage-option.active {
  background-color: rgba(252, 213, 53, 0.1);
  border-color: #FCD535;
  color: #FCD535;
}

/* 输入行 */
.input-row {
  display: flex;
  align-items: center;
  background-color: #1C1C1E;
  border-radius: 4px;
  padding: 0 12px;
  height: 36px;
  gap: 8px;
}

.input-label {
  font-size: 12px;
  color: #EAECEF;
  white-space: nowrap;
  min-width: 80px;
}

.input-field {
  flex: 1;
  background: transparent;
  border: none;
  color: #FFFFFF;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  outline: none;
}

.input-field::placeholder {
  color: #848E9C;
}

/* 市价单禁用输入框 */
.market-price-input {
  color: #848E9C !important;
  cursor: not-allowed;
  opacity: 0.6;
}


/* 估值行 */
.estimated-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
  font-size: 11px;
}

.est-label {
  color: #848E9C;
}

.est-value {
  color: #EAECEF;
}

/* 百分比快捷键 */
.percent-row {
  display: flex;
  gap: 8px;
}

.percent-btn {
  flex: 1;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1C1C1E;
  border-radius: 4px;
  font-size: 12px;
  color: #EAECEF;
  cursor: pointer;
  transition: all 0.2s ease;
}

.percent-btn.active {
  background-color: #FCD535;
  color: #000000;
  font-weight: 600;
}

.percent-btn:active {
  opacity: 0.8;
}

/* 成交金额行 */
.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #1C1C1E;
  border-radius: 4px;
  height: 36px;
  margin-bottom: 16px; /* 增加与可用资产行之间的间距，保持视觉呼吸感 */
}

.total-label {
  font-size: 12px;
  color: #848E9C;
}

.total-value {
  font-size: 13px;
  color: #EAECEF;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* 可用资产信息 */
.available-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 4px;
}

.avail-item {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 11px;
}

.avail-label {
  color: #848E9C;
  margin-right: 4px;
}

.avail-value {
  color: #EAECEF;
  font-variant-numeric: tabular-nums;
}

/* 下单按钮 */
.submit-btn {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  font-variant-numeric: tabular-nums;
}

.submit-btn.buy {
  background-color: #0ECB81;
  color: #000000;
}

.submit-btn.sell {
  background-color: #F6465D;
  color: #FFFFFF;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn:active:not(:disabled) {
  opacity: 0.8;
  transform: scale(0.98);
}

/* ========== 底部：委托与资产 ========== */
.bottom-section {
  background-color: #1E2329;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.bottom-tabs {
  display: flex;
  padding: 8px 16px;
  gap: 24px;
}

.bottom-tabs .tab-item {
  font-size: 14px;
  color: #848E9C;
  cursor: pointer;
  padding-bottom: 4px;
  position: relative;
  transition: color 0.2s ease;
}

.bottom-tabs .tab-item.active {
  color: #FCD535;
  font-weight: 600;
}

.bottom-tabs .tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #FCD535;
}

.bottom-content {
  padding: 16px;
  min-height: 320px;
  max-height: 320px;
  overflow-y: auto;
  background-color: #1E2329;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 订单面板 */
.orders-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 资产面板 */
.assets-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 订单列表 */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 空状态 */
.orders-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  padding: 20px;
}

.empty-icon {
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: #848E9C;
  margin-bottom: 16px;
}

.empty-action-btn {
  padding: 8px 20px;
  background-color: #2B3139;
  color: #FCD535;
  border: 1px solid rgba(252, 213, 53, 0.3);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.empty-action-btn:active {
  background-color: rgba(252, 213, 53, 0.1);
  border-color: #FCD535;
}

/* 订单项 - 币安风格 */
.order-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #1C1C1E;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: background-color 0.2s ease;
}

.order-item:hover {
  background-color: #252A32;
}

/* 左侧：买入/卖出 + 币种 + 时间 */
.order-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  min-width: 120px;
}

.order-side-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

.order-side-badge.buy {
  background-color: rgba(14, 203, 129, 0.15);
  color: #0ECB81;
}

.order-side-badge.sell {
  background-color: rgba(246, 70, 93, 0.15);
  color: #F6465D;
}

.order-symbol-time {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.order-symbol {
  font-size: 13px;
  font-weight: 600;
  color: #FFFFFF;
}

.order-time {
  font-size: 11px;
  color: #848E9C;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

/* 中间：价格和数量 */
.order-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 12px;
  min-width: 0;
}

.order-price {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.order-quantity {
  font-size: 12px;
  color: #848E9C;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

/* 右侧：撤单按钮 */
.order-right {
  flex: 0 0 auto;
}

.cancel-btn {
  padding: 6px 14px;
  background-color: #2B3139;
  color: #848E9C;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.cancel-btn:active {
  background-color: #363c45;
  color: #EAECEF;
  border-color: rgba(255, 255, 255, 0.1);
}

/* 资产列表 */
.assets-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.asset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #1C1C1E;
  border-radius: 6px;
}

/* Tab 切换过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.asset-label {
  font-size: 12px;
  color: #848E9C;
}

.asset-value {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

/* ========== 币种选择弹窗 ========== */
.coin-select-popup {
  background-color: #1C1C1E !important;
}

.coin-select-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #1C1C1E;
}

.coin-select-header {
  padding: 20px 16px 16px;
  border-bottom: 1px solid #2A2D35;
  flex-shrink: 0;
}

.coin-select-title {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
  text-align: left;
}

.coin-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.coin-item {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #2A2D35;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.coin-item:active {
  background-color: rgba(255, 255, 255, 0.05);
}

.coin-item-active {
  background-color: #2A2D35;
}

.coin-name {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
}

.coin-pair {
  font-size: 12px;
  color: #848E9C;
  margin-top: 4px;
}

/* 空状态 */
:deep(.van-empty__description) {
  color: #848E9C;
  font-size: 12px;
}
</style>

