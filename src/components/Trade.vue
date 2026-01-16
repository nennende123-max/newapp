<template>
  <div class="trade-page">
    <div class="trade-header">
      <div class="header-center">
        <span class="page-title">{{ pageTitle }}</span>
      </div>
      
      <div class="nav-right-icon-wrap" @click="goToKlineChart">
        <svg viewBox="0 0 1024 1024" class="kline-svg-icon">
          <path d="M896 128H128a64 64 0 0 0-64 64v640a64 64 0 0 0 64 64h768a64 64 0 0 0 64-64V192a64 64 0 0 0-64-64zM320 768H192V448h128v320zm256 0H448V256h128v512zm256 0H704V512h128v256z" fill="#FCD535"></path>
        </svg>
      </div>
    </div>

    <div class="trade-tabs">
      <div 
        class="tab-item" 
        :class="{ active: activeTradeTab === 'spot' }"
        @click="activeTradeTab = 'spot'"
      >
        {{ t('assets.spot') }}
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTradeTab === 'leverage' }"
        @click="activeTradeTab = 'leverage'"
      >
        {{ t('assets.leverage') }}
      </div>
    </div>

    <div class="pair-info">
      <div class="pair-selector" @click="showCoinSelect = true">
        <span class="pair-name">{{ symbol }}/USDT</span>
        <van-icon name="arrow-down" size="12" color="#FFFFFF" style="margin-left: 4px" />
      </div>
      <div class="price-change" :class="{ positive: priceChange >= 0 }">
        {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
      </div>
    </div>

    <div class="trade-main">
      <div class="orderbook-side">
        <div class="orderbook-header">
          <span class="header-price">{{ t('trade.price') }} (USDT)</span>
          <span class="header-quantity">{{ t('trade.amount') }} ({{ currentCoinConfig.baseCoin }})</span>
        </div>

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

        <div class="last-price" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
          <div class="price-main">{{ formatPrice(lastPrice) }}</div>
          <div class="price-fiat">${{ formatPrice(lastPrice) }}</div>
        </div>

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

      <div class="form-side">
        <div class="buy-sell-toggle">
          <div 
            class="toggle-btn buy-btn" 
            :class="{ active: orderSide === 'buy' }"
            @click="orderSide = 'buy'"
          >
            {{ t('trade.buy') }}
          </div>
          <div 
            class="toggle-btn sell-btn" 
            :class="{ active: orderSide === 'sell' }"
            @click="orderSide = 'sell'"
          >
            {{ t('trade.sell') }}
          </div>
        </div>

        <div v-if="activeTradeTab === 'leverage'" class="leverage-control-bar">
          <button class="leverage-btn" @click="showLeveragePopup = true">
            <span>{{ t('trade.full_position') }}</span>
            <span class="leverage-value">{{ currentLeverage }}x</span>
            <van-icon name="arrow-down" size="12" color="#848E9C" />
          </button>
        </div>

        <div class="order-type-selector" @click="showOrderTypeSheet = true">
          <span>{{ orderType === 'limit' ? t('trade.limit_order') : t('trade.market_order') }}</span>
          <van-icon name="arrow-down" size="12" color="#848E9C" />
        </div>

        <div class="input-row">
          <input
            v-if="orderType === 'limit'"
            v-model="price"
            type="number"
            :placeholder="formatPrice(lastPrice)"
            class="input-field no-spinner"
          />
          <input
            v-else
            type="text"
            :value="t('trade.market_price_hint')"
            disabled
            class="input-field market-price-input"
          />
        </div>

        <div class="estimated-row">
          <span class="est-label">{{ t('trade.estimated_value') }}</span>
          <span class="est-value">≈ ¥{{ formatFiatPrice(parseFloat(price) || lastPrice) }}</span>
        </div>

        <div class="input-row">
          <span class="input-label">{{ t('trade.amount') }}({{ currentCoinConfig.baseCoin }})</span>
          <input
            v-model="amount"
            type="number"
            min="0"
            step="0.0001"
            :placeholder="t('trade.amount_placeholder')"
            class="input-field no-spinner"
            @input="handleAmountInput"
          />
        </div>

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

        <div class="fee-estimate-row">
          <span class="fee-estimate-label">{{ t('trade.estimated_fee') }}(USDT)</span>
          <span class="fee-estimate-value">
            {{ formatEstimatedFee }}
            <span v-if="assetStore.useBNBForFees" class="discount-badge">{{ t('trade.discount_applied') }}</span>
          </span>
        </div>

        <div class="total-row">
          <span class="total-label">{{ t('trade.total') }}(USDT)</span>
          <span class="total-value">{{ formatTotalAmount }}</span>
        </div>

        <div class="available-row">
          <div class="avail-item">
            <span class="avail-label">{{ t('trade.avail') }}：</span>
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
            <span class="avail-label">{{ t('trade.sellable') }}：</span>
            <span class="avail-value">{{ formatSellableBalance }}</span>
          </div>
        </div>

        <button 
          class="submit-btn"
          :class="orderSide"
          :disabled="!isOrderValid"
          @click="handleSubmitOrder"
        >
          {{ orderSide === 'buy' ? t('trade.buy_btc').replace('BTC', symbol) : t('trade.sell_btc').replace('BTC', symbol) }}
        </button>
      </div>
    </div>

    <div class="bottom-section">
      <div class="bottom-tabs">
        <div 
          class="tab-item"
          :class="{ active: activeOrderTab === 'orders' }"
          @click="activeOrderTab = 'orders'"
        >
          {{ t('trade.open_orders') }}
        </div>
        <div 
          class="tab-item"
          :class="{ active: activeOrderTab === 'assets' }"
          @click="activeOrderTab = 'assets'"
        >
          {{ t('trade.assets') }}
        </div>
      </div>

      <div class="bottom-content">
        <transition name="fade" mode="out-in">
          <div v-if="activeOrderTab === 'orders'" key="orders" class="orders-panel panel-full">
            <div v-if="ordersList.length === 0" class="orders-empty">
              <div class="empty-icon">
                <van-icon name="orders-o" size="48" color="#848E9C" />
              </div>
              <div class="empty-text">{{ t('trade.no_orders') }}</div>
              <button class="empty-action-btn" @click="scrollToTop">
                {{ t('trade.go_trade') }}
              </button>
            </div>
            <div v-else class="orders-list">
              <div 
                v-for="(order, index) in ordersList"
                :key="index"
                class="order-item"
              >
                <div class="order-left">
                  <div class="order-side-badge" :class="order.side">
                    {{ order.side === 'buy' ? t('trade.buy') : t('trade.sell') }}
                  </div>
                  <div class="order-symbol-time">
                    <span class="order-symbol">{{ order.symbol }}</span>
                    <span class="order-time">{{ formatOrderTime(order.timestamp) }}</span>
                  </div>
                </div>
                
                <div class="order-center">
                  <div class="order-price">{{ formatPrice(order.price) }}</div>
                  <div class="order-quantity">{{ formatQuantity(order.quantity) }} / {{ formatQuantity(order.quantity) }}</div>
                </div>
                
                <div class="order-right">
                  <button class="cancel-btn" @click="cancelOrder(index)">{{ t('trade.cancel') }}</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else key="assets" class="assets-panel panel-full">
            <div class="assets-list">
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.avail') }}</span>
                <span class="asset-value">{{ formatNumber(availableBalance) }} {{ symbol }}</span>
              </div>
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.frozen') }}</span>
                <span class="asset-value">{{ formatNumber(frozenBalance) }} {{ symbol }}</span>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <van-popup
      v-model:show="showCoinSelect"
      position="bottom"
      :style="{ height: '60%' }"
      round
      class="coin-select-popup"
    >
      <div class="coin-select-container">
        <div class="coin-select-header">
          <h3 class="coin-select-title">{{ t('trade.switch_coin') }}</h3>
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

    <van-action-sheet
      v-model:show="showOrderTypeSheet"
      :actions="orderTypeOptions"
      @select="onOrderTypeSelect"
      :cancel-text="t('common.cancel')"
      :title="t('trade.select_order_type')"
      class="custom-action-sheet" 
    />

    <van-popup
      v-model:show="showLeveragePopup"
      position="bottom"
      :style="{ height: '40%' }"
      round
      class="leverage-popup"
    >
      <div class="leverage-popup-content">
        <div class="leverage-popup-header">
          <h3 class="leverage-popup-title">{{ t('trade.select_leverage') }}</h3>
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
import { useI18n } from 'vue-i18n';
import { showToast, Icon, Popup, Empty, ActionSheet } from 'vant';
import { useAssetStore } from '@/stores/assets';

defineOptions({
  name: 'Trade'
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n(); 
const assetStore = useAssetStore();

// 修复1：计算属性绑定 pageTitle，解决语言切换问题
const pageTitle = computed(() => t('trade.title'));

const symbol = ref(route.query.symbol || 'BTC');

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

const selectedCoin = computed(() => `${symbol.value}/USDT`);
const currentCoinConfig = computed(() => coinConfigs[selectedCoin.value] || coinConfigs['BTC/USDT']);

const showCoinSelect = ref(false);
const coinList = ref([
  { symbol: 'BTC' }, { symbol: 'ETH' }, { symbol: 'BNB' }, { symbol: 'SOL' },
  { symbol: 'DOGE' }, { symbol: 'TRX' }, { symbol: 'BEAT' }, { symbol: 'AIC' }
]);

const activeTradeTab = ref('spot');
const orderSide = ref(route.query.side === 'buy' || route.query.side === 'sell' ? route.query.side : 'buy');
const orderType = ref('limit'); 
const price = ref('');
const amount = ref('');
const priceChange = ref(1.83);
const lastPrice = ref(92255.50);
const activeOrderTab = ref('orders');
const selectedPercent = ref(null);
const ordersList = ref([]);
const showOrderTypeSheet = ref(false);
const currentLeverage = ref(20); 
const showLeveragePopup = ref(false); 

// 模拟币种价格数据
const coinPrices = {
  'BTC': 92255.50,
  'ETH': 2500.00,
  'BNB': 500.00,
  'SOL': 150.00,
  'DOGE': 0.10,
  'TRX': 0.15,
  'BEAT': 1.00,
  'AIC': 2.00
};

const asks = ref([]);
const bids = ref([]);

// 生成盘口数据
const generateOrderBook = () => {
  const basePrice = lastPrice.value;
  asks.value = [
    { price: basePrice + 0.30, quantity: 0.00006 },
    { price: basePrice + 0.09, quantity: 0.00709 },
    { price: basePrice + 0.08, quantity: 0.00012 },
    { price: basePrice + 0.02, quantity: 0.00006 },
    { price: basePrice + 0.01, quantity: 0.00063 },
    { price: basePrice, quantity: 3.04039 }
  ];
  bids.value = [
    { price: basePrice - 0.01, quantity: 3.30750 },
    { price: basePrice - 0.02, quantity: 0.00025 },
    { price: basePrice - 0.03, quantity: 0.00012 },
    { price: basePrice - 0.04, quantity: 0.00079 },
    { price: basePrice - 0.05, quantity: 0.00121 },
    { price: basePrice - 0.06, quantity: 0.05419 }
  ];
};

watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
    // 切换页面时也更新价格
    updatePriceForSymbol(newSymbol);
  }
});

watch(() => route.query.side, (newSide) => {
  if (newSide === 'buy' || newSide === 'sell') orderSide.value = newSide;
}, { immediate: true });

// 修复2：监听 symbol 变化，自动更新输入框价格为对应币种的最新价
watch(symbol, (newSymbol) => {
  updatePriceForSymbol(newSymbol);
});

// 辅助函数：根据币种更新价格
const updatePriceForSymbol = (newSymbol) => {
  lastPrice.value = coinPrices[newSymbol] || 92255.50;
  generateOrderBook();
  // 只有是限价单时，才自动填充价格
  if (orderType.value === 'limit') {
    price.value = lastPrice.value.toFixed(currentCoinConfig.value.priceFixed);
  }
};

const priceStep = computed(() => currentCoinConfig.value.step);

const availableBalance = computed(() => {
  try {
    let realBalance = 0;
    if (orderSide.value === 'buy') realBalance = assetStore?.usdtBalance || 0;
    else realBalance = assetStore?.getHolding(symbol.value) || 0;
    
    if (activeTradeTab.value === 'leverage') return realBalance * currentLeverage.value;
    return realBalance;
  } catch (error) {
    console.error('Error getting available balance:', error);
    return 0;
  }
});

const frozenBalance = computed(() => 0);

const formatPrice = (value) => {
  if (!value) return '0.00';
  const config = currentCoinConfig.value;
  return value.toLocaleString('en-US', { minimumFractionDigits: config.priceFixed, maximumFractionDigits: config.priceFixed });
};

const formatQuantity = (value) => {
  if (!value) return '0.00000000';
  const config = currentCoinConfig.value;
  return value.toFixed(config.amountFixed);
};

const formatFiatPrice = (value) => {
  const cnyPrice = value * 7.2;
  if (cnyPrice >= 1000000) return (cnyPrice / 1000000).toFixed(2) + 'M';
  else if (cnyPrice >= 1000) return (cnyPrice / 1000).toFixed(0) + 'K';
  return cnyPrice.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
};

const formatNumber = (value) => {
  return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
};

const getDepthWidth = (quantity, list, type) => {
  if (!list || list.length === 0) return 0;
  const maxQuantity = Math.max(...list.map(item => item.quantity));
  if (maxQuantity === 0) return 0;
  return (quantity / maxQuantity) * 100;
};

const selectPrice = (selectedPrice, side) => {
  const config = currentCoinConfig.value;
  price.value = selectedPrice.toFixed(config.priceFixed);
  if (side !== orderSide.value) orderSide.value = side;
};

const adjustPrice = (direction) => {
  const currentPrice = parseFloat(price.value) || lastPrice.value;
  const step = priceStep.value;
  const config = currentCoinConfig.value;
  const newPrice = currentPrice + (direction * step);
  price.value = newPrice.toFixed(config.priceFixed);
};

const handleAmountInput = (e) => {
  let value = e.target.value;
  if (value.includes('-')) value = value.replace(/-/g, '');
  const numValue = parseFloat(value);
  if (!isNaN(numValue) && numValue < 0) value = Math.abs(numValue).toString();
  if (value === '' || value === '-') { amount.value = ''; return; }
  amount.value = value;
};

const adjustAmount = (direction) => {
  const currentAmount = parseFloat(amount.value) || 0;
  const config = currentCoinConfig.value;
  const step = Math.pow(10, -config.amountFixed);
  const newAmount = Math.max(0, currentAmount + (direction * step));
  amount.value = newAmount.toFixed(config.amountFixed);
};

const setAmountPercent = (percent) => {
  selectedPercent.value = percent;
  try {
    const balance = availableBalance.value;
    if (balance <= 0) { showToast({ message: t('earn.insufficient_balance'), duration: 2000 }); return; }
    const config = currentCoinConfig.value;
    if (orderSide.value === 'buy') {
      const totalCost = balance * (percent / 100);
      const calculatedAmount = totalCost / (parseFloat(price.value) || lastPrice.value);
      amount.value = calculatedAmount.toFixed(config.amountFixed);
    } else {
      const calculatedAmount = balance * (percent / 100);
      amount.value = calculatedAmount.toFixed(config.amountFixed);
    }
  } catch (error) { console.error(error); showToast({ message: t('common.error'), duration: 2000 }); }
};

const formatTotalAmount = computed(() => {
  const p = parseFloat(price.value) || 0;
  const a = parseFloat(amount.value) || 0;
  const total = p * a;
  return total > 0 ? total.toFixed(2) : '0.00';
});

const formatEstimatedFee = computed(() => {
  const p = parseFloat(price.value) || lastPrice.value;
  const a = parseFloat(amount.value) || 0;
  if (p <= 0 || a <= 0) return '0.00';
  const fee = p * a * assetStore.currentSpotFeeRate;
  return fee > 0 ? fee.toFixed(4) : '0.00';
});

const formatAvailableBalance = computed(() => {
  if (orderSide.value === 'buy') return formatNumber(availableBalance.value) + ' USDT';
  else return formatNumber(availableBalance.value) + ' ' + symbol.value;
});

const formatSellableBalance = computed(() => {
  if (orderSide.value === 'buy') return formatNumber(availableBalance.value) + ' ' + symbol.value;
  else return formatNumber(availableBalance.value) + ' USDT';
});

// 使用 computed 来实现响应式翻译
const orderTypeOptions = computed(() => [
  { name: t('trade.limit_order'), type: 'limit' },
  { name: t('trade.market_order'), type: 'market' }
]);

const onOrderTypeSelect = (action) => {
  orderType.value = action.type;
  showOrderTypeSheet.value = false;
  if (action.type === 'limit' && !price.value) price.value = lastPrice.value.toFixed(currentCoinConfig.value.priceFixed);
};

const leverageOptions = [1, 2, 3, 5, 10, 20, 50, 100];
const selectLeverage = (leverage) => { currentLeverage.value = leverage; showLeveragePopup.value = false; };

const isOrderValid = computed(() => {
  const a = parseFloat(amount.value);
  if (orderType.value === 'market') return a > 0;
  else { const p = parseFloat(price.value); return p > 0 && a > 0; }
});

const formatOrderTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

const scrollToTop = () => { window.scrollTo({ top: 0, behavior: 'smooth' }); };

const handleSubmitOrder = () => {
  const amountValue = parseFloat(amount.value);
  if (isNaN(amountValue) || amountValue <= 0) { showToast({ message: t('trade.amount_invalid'), icon: 'fail' }); return; }
  if (!isOrderValid.value) { showToast({ message: t('trade.fill_all_fields'), duration: 2000 }); return; }
  
  const orderPrice = orderType.value === 'market' ? lastPrice.value : parseFloat(price.value);
  const order = { side: orderSide.value, type: orderType.value, price: orderPrice, quantity: parseFloat(amount.value), symbol: symbol.value, timestamp: Date.now() };
  
  ordersList.value.push(order);
  showToast({ message: orderType.value === 'market' ? t('trade.market_order_submitted') : t('trade.limit_order_submitted'), duration: 2000 });
  
  if (orderType.value === 'limit') price.value = '';
  amount.value = ''; selectedPercent.value = null;
};

const cancelOrder = (index) => { ordersList.value.splice(index, 1); showToast({ message: t('trade.order_cancelled'), duration: 2000 }); };

const goToKlineChart = () => { router.push({ path: '/market', query: { symbol: symbol.value } }); };

const switchCoin = (newSymbol) => {
  symbol.value = newSymbol; showCoinSelect.value = false;
  router.push({ path: '/trade', query: { symbol: newSymbol, side: orderSide.value } });
  showToast({ message: t('trade.switched_to', { symbol: `${newSymbol}/USDT` }), duration: 1500 });
};

onMounted(() => {
  generateOrderBook();
  // 首次进入也初始化价格
  updatePriceForSymbol(symbol.value);
  
  if (ordersList.value.length === 0) {
    const now = Date.now();
    const buyPrice = lastPrice.value * 0.998;
    ordersList.value.push({ side: 'buy', type: 'limit', price: buyPrice, quantity: 0.0015, symbol: symbol.value, timestamp: now - 300000 });
    const sellPrice = lastPrice.value * 1.002;
    ordersList.value.push({ side: 'sell', type: 'limit', price: sellPrice, quantity: 0.002, symbol: symbol.value, timestamp: now - 180000 });
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

.header-center {
  flex: 1; /* 占据左侧空间 */
  display: flex;
  align-items: center;
  justify-content: flex-start; /* 标题靠左对齐 */
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
}

.nav-right-icon-wrap {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: flex-end; /* 图标靠右 */
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.nav-right-icon-wrap:hover { opacity: 0.8; }
.nav-right-icon-wrap:active { opacity: 0.6; }

.kline-svg-icon {
  width: 22px;
  height: 22px;
  fill: #FCD535;
  display: block;
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

.pair-selector { display: flex; align-items: center; cursor: pointer; }
.pair-name { font-size: 16px; font-weight: 700; color: #FFFFFF; }
.price-change { font-size: 14px; font-weight: 600; padding: 4px 8px; border-radius: 4px; }
.price-change.positive { color: #0ECB81; background-color: rgba(14, 203, 129, 0.1); }
.price-change.negative { color: #F6465D; background-color: rgba(246, 70, 93, 0.1); }

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
  justify-content: flex-start;
  background-color: #0E0E0E;
  border-radius: 4px;
  overflow: hidden;
  padding: 0;
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 4px 8px;
  font-size: 11px;
  color: #848E9C;
  border-bottom: none;
}

.header-price { flex: 1; text-align: left; }
.header-quantity { flex: 1; text-align: right; }

.asks-list, .bids-list {
  display: flex;
  flex-direction: column;
  flex: none;
  min-height: 0;
  overflow-y: auto;
}

.order-row {
  position: relative;
  height: 20px;
  line-height: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
  cursor: pointer;
  overflow: hidden;
}

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

.ask-depth { background: linear-gradient(to left, rgba(246, 70, 93, 0.1) 0%, rgba(246, 70, 93, 0.05) 100%); }
.bid-depth { background: linear-gradient(to left, rgba(14, 203, 129, 0.1) 0%, rgba(14, 203, 129, 0.05) 100%); }

.order-row .price { position: relative; z-index: 1; font-size: 11px; font-weight: 500; font-variant-numeric: tabular-nums; }
.ask-price { color: #F6465D; text-align: left; flex: 1; }
.bid-price { color: #0ECB81; text-align: left; flex: 1; }
.order-row .quantity { position: relative; z-index: 1; font-size: 11px; color: #848E9C; text-align: right; flex: 1; font-variant-numeric: tabular-nums; }

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
}

.price-main { font-size: 16px; font-weight: 700; color: #FFFFFF; font-variant-numeric: tabular-nums; line-height: 1.2; }
.price-fiat { font-size: 11px; color: #848E9C; font-variant-numeric: tabular-nums; line-height: 1; margin-top: 2px; }
.last-price.up .price-main { color: #0ECB81; }
.last-price.down .price-main { color: #F6465D; }

.form-side {
  width: 58%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

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

.buy-btn.active { background-color: #0ECB81; color: #000000; }
.sell-btn.active { background-color: #F6465D; color: #FFFFFF; }

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
}

.order-type-selector:active { background-color: #252A32; }

.leverage-control-bar { margin-bottom: 8px; }
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
}

.leverage-value { color: #FCD535; font-weight: 600; font-variant-numeric: tabular-nums; }
.leverage-popup, :deep(.leverage-popup .van-popup) { background: #1C1C1E; }
.leverage-popup-content { padding: 20px; height: 100%; display: flex; flex-direction: column; }
.leverage-popup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.leverage-popup-title { font-size: 18px; font-weight: 700; color: #FFFFFF; margin: 0; }
.close-icon { font-size: 20px; color: #848E9C; cursor: pointer; }
.leverage-options { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.leverage-option {
  display: flex; align-items: center; justify-content: space-between; padding: 12px 16px;
  background-color: #141414; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px;
  font-size: 14px; font-weight: 600; color: #EAECEF; cursor: pointer;
}
.leverage-option.active { background-color: rgba(252, 213, 53, 0.1); border-color: #FCD535; color: #FCD535; }

.input-row {
  display: flex;
  align-items: center;
  background-color: #1C1C1E;
  border-radius: 4px;
  padding: 0 12px;
  height: 36px;
  gap: 8px;
}
.input-label { font-size: 12px; color: #EAECEF; white-space: nowrap; min-width: 80px; }
.input-field { flex: 1; background: transparent; border: none; color: #FFFFFF; font-size: 13px; font-variant-numeric: tabular-nums; outline: none; }
.input-field::placeholder { color: #848E9C; }

/* 修复3：隐藏数字输入框默认的上下箭头 */
.no-spinner::-webkit-inner-spin-button,
.no-spinner::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.no-spinner {
  -moz-appearance: textfield;
}

.market-price-input { color: #848E9C !important; cursor: not-allowed; opacity: 0.6; }

.estimated-row { display: flex; justify-content: space-between; align-items: center; padding: 0 4px; font-size: 11px; }
.est-label { color: #848E9C; }
.est-value { color: #EAECEF; }

.percent-row { display: flex; gap: 8px; }
.percent-btn {
  flex: 1; height: 32px; display: flex; align-items: center; justify-content: center;
  background-color: #1C1C1E; border-radius: 4px; font-size: 12px; color: #EAECEF; cursor: pointer;
}
.percent-btn.active { background-color: #FCD535; color: #000000; font-weight: 600; }

.fee-estimate-row {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
  background-color: #1C1C1E; border-radius: 4px; height: 36px; margin-bottom: 8px;
}
.fee-estimate-label { font-size: 12px; color: #848E9C; }
.fee-estimate-value { font-size: 13px; color: #EAECEF; font-weight: 600; font-variant-numeric: tabular-nums; display: flex; align-items: center; gap: 4px; }
.discount-badge { font-size: 11px; color: #FCD535; font-weight: 500; }

.total-row {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
  background-color: #1C1C1E; border-radius: 4px; height: 36px; margin-bottom: 16px;
}
.total-label { font-size: 12px; color: #848E9C; }
.total-value { font-size: 13px; color: #EAECEF; font-weight: 600; font-variant-numeric: tabular-nums; }

.available-row { display: flex; flex-direction: column; gap: 4px; padding: 0 4px; }
.avail-item { display: flex; align-items: center; justify-content: flex-end; font-size: 11px; }
.avail-label { color: #848E9C; margin-right: 4px; }
.avail-value { color: #EAECEF; font-variant-numeric: tabular-nums; }

.submit-btn {
  width: 100%; height: 44px; border: none; border-radius: 4px; font-size: 16px; font-weight: 700;
  cursor: pointer; transition: all 0.2s ease; font-variant-numeric: tabular-nums;
}
.submit-btn.buy { background-color: #0ECB81; color: #000000; }
.submit-btn.sell { background-color: #F6465D; color: #FFFFFF; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.submit-btn:active:not(:disabled) { opacity: 0.8; transform: scale(0.98); }

/* ========== 底部：委托与资产 ========== */
.bottom-section { background-color: #1E2329; border-top: 1px solid rgba(255, 255, 255, 0.05); }
.bottom-tabs { display: flex; padding: 8px 16px; gap: 24px; }
.bottom-tabs .tab-item {
  font-size: 14px; color: #848E9C; cursor: pointer; padding-bottom: 4px; position: relative; transition: color 0.2s ease;
}
.bottom-tabs .tab-item.active { color: #FCD535; font-weight: 600; }
.bottom-tabs .tab-item.active::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background-color: #FCD535;
}

.bottom-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1E2329;
  min-height: 320px; 
}

.panel-full {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.orders-panel, .assets-panel { flex: 1; display: flex; flex-direction: column; min-height: 0; }

.orders-list { display: flex; flex-direction: column; gap: 8px; flex: 1; }
.orders-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 200px; padding: 20px; flex: 1;
}
.empty-icon { margin-bottom: 12px; opacity: 0.6; }
.empty-text { font-size: 14px; color: #848E9C; margin-bottom: 16px; }
.empty-action-btn {
  padding: 8px 20px; background-color: #2B3139; color: #FCD535; border: 1px solid rgba(252, 213, 53, 0.3);
  border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer;
}

.order-item {
  display: flex; align-items: center; padding: 12px; background-color: #1C1C1E;
  border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); transition: background-color 0.2s ease;
}
.order-left { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; min-width: 120px; }
.order-side-badge { padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.order-side-badge.buy { background-color: rgba(14, 203, 129, 0.15); color: #0ECB81; }
.order-side-badge.sell { background-color: rgba(246, 70, 93, 0.15); color: #F6465D; }
.order-symbol-time { display: flex; flex-direction: column; gap: 2px; }
.order-symbol { font-size: 13px; font-weight: 600; color: #FFFFFF; }
.order-time { font-size: 11px; color: #848E9C; font-family: 'Roboto Mono', monospace; }
.order-center { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 0 12px; min-width: 0; }
.order-price { font-size: 14px; font-weight: 600; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
.order-quantity { font-size: 12px; color: #848E9C; font-family: 'Roboto Mono', monospace; }
.order-right { flex: 0 0 auto; }
.cancel-btn { padding: 6px 14px; background-color: #2B3139; color: #848E9C; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; font-size: 12px; font-weight: 500; }

.assets-list { display: flex; flex-direction: column; gap: 8px; flex: 1; }

.asset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 12px; 
  background-color: #1C1C1E;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  min-height: 48px;
}

.asset-label { font-size: 13px; color: #848E9C; }
.asset-value { font-size: 14px; font-weight: 600; color: #FFFFFF; font-variant-numeric: tabular-nums; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.coin-select-popup { background-color: #1C1C1E !important; }
.coin-select-container { display: flex; flex-direction: column; height: 100%; background-color: #1C1C1E; }
.coin-select-header { padding: 20px 16px 16px; border-bottom: 1px solid #2A2D35; flex-shrink: 0; }
.coin-select-title { font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 0; text-align: left; }
.coin-list { flex: 1; overflow-y: auto; padding: 0; }
.coin-item { padding: 12px 16px; display: flex; flex-direction: column; border-bottom: 1px solid #2A2D35; cursor: pointer; transition: background-color 0.2s ease; }
.coin-item:active { background-color: rgba(255, 255, 255, 0.05); }
.coin-item-active { background-color: #2A2D35; }
.coin-name { font-size: 16px; font-weight: 700; color: #FFFFFF; margin: 0; }
.coin-pair { font-size: 12px; color: #848E9C; margin-top: 4px; }
:deep(.van-empty__description) { color: #848E9C; font-size: 12px; }

/* 修复3：ActionSheet 黑金风格 */
.custom-action-sheet {
  --van-action-sheet-background: #1C1C1E;
  --van-action-sheet-item-background: #1C1C1E;
  --van-action-sheet-item-text-color: #EAECEF;
  --van-action-sheet-cancel-padding-top: 8px;
  --van-action-sheet-cancel-padding-color: #000000;
  --van-popup-background: #1C1C1E;
}

:deep(.van-action-sheet__item), :deep(.van-action-sheet__cancel) {
  background-color: #1C1C1E;
  color: #EAECEF;
}

:deep(.van-action-sheet__item:active), :deep(.van-action-sheet__cancel:active) {
  background-color: #252A32;
}

:deep(.van-action-sheet__gap) {
  background-color: #000000;
  height: 8px;
}

:deep(.van-action-sheet__header) {
  background-color: #1C1C1E;
  color: #FFFFFF;
  font-weight: 700;
}
</style>