<template>
  <div class="futures-trade-page">
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
        <span class="page-title">{{ $t('assets.futures') }}</span>
      </div>
      <div class="nav-right-icon-wrap" @click="goToKlineChart">
        <svg viewBox="0 0 1024 1024" class="kline-svg-icon">
          <path d="M896 128H128a64 64 0 0 0-64 64v640a64 64 0 0 0 64 64h768a64 64 0 0 0 64-64V192a64 64 0 0 0-64-64zM320 768H192V448h128v320zm256 0H448V256h128v512zm256 0H704V512h128v256z" fill="#FCD535"></path>
        </svg>
      </div>
    </div>

    <!-- 合约控制栏：全仓/逐仓 + 杠杆倍数 -->
    <div class="futures-control-bar">
      <div class="margin-mode-toggle">
        <div 
          class="mode-btn" 
          :class="{ active: marginMode === 'cross' }"
          @click="marginMode = 'cross'"
        >
          {{ $t('trade.full_position') }}
        </div>
        <div 
          class="mode-btn" 
          :class="{ active: marginMode === 'isolated' }"
          @click="marginMode = 'isolated'"
        >
          {{ $t('trade.isolated_position') }}
        </div>
      </div>
      <button class="leverage-btn" @click="showLeveragePopup = true">
        <span>{{ currentLeverage }}x</span>
        <van-icon name="arrow-down" size="12" color="#848E9C" />
      </button>
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
          <span class="header-price">{{ $t('trade.price') }} (USDT)</span>
          <span class="header-quantity">{{ $t('trade.amount') }} (BTC)</span>
        </div>

        <!-- 卖单列表 (Asks) - 倒序 -->
        <div class="asks-list">
          <div 
            v-for="(ask, index) in asks" 
            :key="`ask-${index}`"
            class="order-row ask-row"
            :style="{ '--depth-width': getDepthWidth(ask.quantity, asks, 'asks') + '%' }"
            @click="selectPrice(ask.price)"
          >
            <div class="depth-bar ask-depth"></div>
            <span class="price ask-price">{{ formatPrice(ask.price) }}</span>
            <span class="quantity">{{ formatQuantity(ask.quantity) }}</span>
          </div>
        </div>

        <!-- 最新成交价 (Middle) -->
        <div class="last-price" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
          <div class="price-main">{{ formatPrice(markPrice) }}</div>
          <div class="price-fiat">${{ formatPrice(markPrice) }}</div>
        </div>

        <!-- 买单列表 (Bids) - 正序 -->
        <div class="bids-list">
          <div 
            v-for="(bid, index) in bids" 
            :key="`bid-${index}`"
            class="order-row bid-row"
            :style="{ '--depth-width': getDepthWidth(bid.quantity, bids, 'bids') + '%' }"
            @click="selectPrice(bid.price)"
          >
            <div class="depth-bar bid-depth"></div>
            <span class="price bid-price">{{ formatPrice(bid.price) }}</span>
            <span class="quantity">{{ formatQuantity(bid.quantity) }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧：交易表单 (58%) -->
      <div class="form-side">
        <!-- 订单类型选择器 -->
        <div class="order-type-selector" @click="showOrderTypeSheet = true">
          <span>{{ orderType === 'limit' ? $t('trade.limit_order') : $t('trade.market_order') }}</span>
          <van-icon name="arrow-down" size="12" color="#848E9C" />
        </div>

        <!-- 价格输入 -->
        <div class="input-row">
          <input
            v-if="orderType === 'limit'"
            v-model="price"
            type="number"
            :placeholder="markPrice.toFixed(currentCoinConfig.priceFixed)"
            class="input-field"
          />
          <input
            v-else
            type="text"
            :value="$t('trade.market_price_hint')"
            disabled
            class="input-field market-price-input"
          />
        </div>

        <!-- 数量输入 -->
        <div class="input-row">
          <input
            v-model="amount"
            type="number"
            :placeholder="$t('trade.amount_placeholder')"
            class="input-field"
          />
        </div>

        <!-- 百分比快捷键 -->
        <div class="percent-buttons">
          <button 
            v-for="pct in [25, 50, 75, 100]" 
            :key="pct"
            class="percent-btn"
            :class="{ active: selectedPercent === pct }"
            @click="selectPercent(pct)"
          >
            {{ pct }}%
          </button>
        </div>

        <!-- 预估手续费 -->
        <div class="info-row">
          <span>{{ $t('trade.estimated_fee') }} (USDT)</span>
          <span class="info-value">{{ estimatedFee.toFixed(2) }}</span>
        </div>

        <!-- 成交金额 -->
        <div class="info-row">
          <span>{{ $t('trade.total') }} (USDT)</span>
          <span class="info-value">{{ totalValue.toFixed(2) }}</span>
        </div>

        <!-- 合约账户余额 -->
        <div class="info-row">
          <span>{{ $t('trade.avail') }}:</span>
          <span class="info-value">{{ availableBalance.toFixed(2) }} USDT</span>
        </div>

        <!-- 开多/开空按钮 -->
        <div class="futures-action-buttons">
          <button 
            class="long-btn"
            :disabled="!isFormValid"
            @click="handleLong"
          >
            {{ $t('trade.open_long') }}
          </button>
          <button 
            class="short-btn"
            :disabled="!isFormValid"
            @click="handleShort"
          >
            {{ $t('trade.open_short') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 底部：专业持仓看板 -->
    <div class="positions-section">
      <van-tabs 
        v-model:active="activePositionTab" 
        background="transparent" 
        title-active-color="#FCD535" 
        title-inactive-color="#8E8E93" 
        line-width="30px" 
        line-height="3px" 
        color="#FCD535" 
        :border="false"
        class="position-tabs"
      >
        <van-tab :title="$t('trade.positions_tab', { count: positions.length })">
          <div class="positions-list">
            <div v-if="positions.length === 0" class="empty-state">
              {{ $t('trade.no_positions') }}
            </div>
            <div 
              v-for="(position, index) in positions" 
              :key="index"
              class="position-card"
            >
              <div class="position-card-main">
                <!-- 左侧：币种名 + 杠杆倍数 -->
                <div class="position-left">
                  <div class="position-symbol-row">
                    <span class="position-symbol">{{ position.symbol }}USDT</span>
                    <span class="position-perpetual">{{ $t('trade.perpetual') }}</span>
                  </div>
                  <div class="position-leverage">
                    {{ position.leverage || currentLeverage }}x
                  </div>
                </div>

                <!-- 中间：未实现盈亏 -->
                <div class="position-center">
                  <div class="unrealized-pnl-label">{{ $t('trade.unrealized_pnl') }}</div>
                  <div 
                    class="unrealized-pnl-value" 
                    :class="{ positive: position.unrealizedPnl >= 0, negative: position.unrealizedPnl < 0 }"
                  >
                    {{ position.unrealizedPnl >= 0 ? '+' : '-' }}{{ formatUnrealizedPnl(position.unrealizedPnl) }}
                  </div>
                  <div 
                    class="unrealized-pnl-percent" 
                    :class="{ positive: position.unrealizedPnlPercent >= 0, negative: position.unrealizedPnlPercent < 0 }"
                  >
                    {{ position.unrealizedPnlPercent >= 0 ? '+' : '' }}{{ position.unrealizedPnlPercent.toFixed(2) }}%
                  </div>
                </div>

                <!-- 右侧：强平价格、保证金、仓位数量 -->
                <div class="position-right">
                  <div class="position-info-row">
                    <span class="info-label">{{ $t('trade.liquidation_price') }}:</span>
                    <span class="info-value liquidation-price">{{ formatPrice(position.liquidationPrice) }}</span>
                  </div>
                  <div class="position-info-row">
                    <span class="info-label">{{ $t('trade.margin_amount') }}:</span>
                    <span class="info-value">{{ formatPrice(position.margin) }} USDT</span>
                  </div>
                  <div class="position-info-row">
                    <span class="info-label">{{ $t('trade.position_size') }}:</span>
                    <span class="info-value">{{ formatQuantity(position.quantity) }} {{ position.symbol }}</span>
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="position-actions">
                <button class="action-btn tp-sl-btn" @click="handleTakeProfitStopLoss(position, index)">
                  {{ $t('trade.take_profit_stop_loss') }}
                </button>
                <button class="action-btn close-btn" @click="handleClosePosition(position, index)">
                  {{ $t('trade.close_position') }}
                </button>
              </div>
            </div>
          </div>
        </van-tab>
        <van-tab :title="$t('trade.open_orders_tab')">
          <div class="orders-list">
            <div class="empty-state">
              {{ $t('trade.no_orders') }}
            </div>
          </div>
        </van-tab>
        <van-tab :title="$t('trade.trade_history_tab')">
          <div class="history-list">
            <div class="empty-state">
              {{ $t('trade.no_orders') }}
            </div>
          </div>
        </van-tab>
      </van-tabs>
    </div>

    <!-- 止盈止损弹窗 -->
    <van-popup
      v-model:show="showTPSLPopup"
      position="bottom"
      :style="{ height: '50%' }"
      round
      class="tp-sl-popup"
    >
      <div class="tp-sl-popup-content">
        <div class="tp-sl-popup-header">
          <h3>{{ $t('trade.take_profit_stop_loss') }}</h3>
          <van-icon name="cross" @click="showTPSLPopup = false" class="close-icon" />
        </div>
        <div class="tp-sl-form">
          <div class="form-item">
            <label>{{ $t('trade.take_profit_price') }}</label>
            <input v-model="tpSlForm.takeProfitPrice" type="number" :placeholder="markPrice.toFixed(2)" />
          </div>
          <div class="form-item">
            <label>{{ $t('trade.stop_loss_price') }}</label>
            <input v-model="tpSlForm.stopLossPrice" type="number" :placeholder="markPrice.toFixed(2)" />
          </div>
          <button class="submit-btn" @click="confirmTPSL">
            {{ $t('common.confirm') }}
          </button>
        </div>
      </div>
    </van-popup>

    <!-- 订单类型选择弹窗 -->
    <van-action-sheet
      v-model:show="showOrderTypeSheet"
      :actions="orderTypeActions"
      @select="onOrderTypeSelect"
      :title="$t('trade.select_order_type')"
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
          <h3 class="leverage-popup-title">{{ $t('trade.select_leverage') }}</h3>
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

    <!-- 币种选择弹窗 -->
    <van-popup
      v-model:show="showCoinSelect"
      position="bottom"
      :style="{ height: '50%' }"
      round
      class="coin-select-popup"
    >
      <div class="coin-select-content">
        <div class="coin-select-header">
          <h3>{{ $t('trade.switch_coin') }}</h3>
          <van-icon name="cross" @click="showCoinSelect = false" class="close-icon" />
        </div>
        <div class="coin-list">
          <div
            v-for="coin in coinList"
            :key="coin.symbol"
            class="coin-item"
            :class="{ active: symbol === coin.symbol }"
            @click="selectCoin(coin.symbol)"
          >
            <span>{{ coin.symbol }}/USDT</span>
            <van-icon v-if="symbol === coin.symbol" name="success" color="#FCD535" />
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, showConfirmDialog, Tabs, Tab, Popup, ActionSheet } from 'vant';
import { useMarketStore } from '@/stores/market';
import { useAssetStore } from '@/stores/assets';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const marketStore = useMarketStore();
const assetStore = useAssetStore();

// 币种配置
const coinConfigs = {
  'BTC/USDT': { priceFixed: 2, amountFixed: 5, step: 0.01, baseCoin: 'BTC' },
  'ETH/USDT': { priceFixed: 2, amountFixed: 4, step: 0.01, baseCoin: 'ETH' },
  'BNB/USDT': { priceFixed: 2, amountFixed: 3, step: 0.01, baseCoin: 'BNB' },
  'SOL/USDT': { priceFixed: 3, amountFixed: 3, step: 0.001, baseCoin: 'SOL' },
  'DOGE/USDT': { priceFixed: 5, amountFixed: 2, step: 0.00001, baseCoin: 'DOGE' },
  'TRX/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'TRX' },
  'BEAT/USDT': { priceFixed: 3, amountFixed: 2, step: 0.001, baseCoin: 'BEAT' },
  'AIC/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'AIC' }
};

// 状态管理
const symbol = ref('BTC');
const marginMode = ref('cross'); // 'cross' 全仓, 'isolated' 逐仓
const currentLeverage = ref(20);
const orderType = ref('limit');
const price = ref('');
const amount = ref('');
const priceChange = ref(1.83);
const markPrice = ref(92255.50);
const selectedPercent = ref(null);
const showOrderTypeSheet = ref(false);
const showLeveragePopup = ref(false);
const showCoinSelect = ref(false);
const activePositionTab = ref(0);
const showTPSLPopup = ref(false);
const currentTPSLPosition = ref(null);
const tpSlForm = ref({
  takeProfitPrice: '',
  stopLossPrice: ''
});
const positions = ref([]);

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

// 当前币种配置
const currentCoinConfig = computed(() => {
  return coinConfigs[`${symbol.value}/USDT`] || coinConfigs['BTC/USDT'];
});

// 订单类型选项
const orderTypeActions = computed(() => [
  { name: t('trade.limit_order'), value: 'limit' },
  { name: t('trade.market_order'), value: 'market' }
]);

// 杠杆倍数选项
const leverageOptions = [1, 2, 3, 5, 10, 20, 50, 100];

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

// 从 marketStore 获取标记价格
watch(() => marketStore.getTicker(symbol.value), (ticker) => {
  if (ticker) {
    markPrice.value = ticker.price || markPrice.value;
    priceChange.value = ticker.change || priceChange.value;
  }
}, { immediate: true });

// 监听路由变化
watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
  }
});

// 合约账户余额（从 assetStore 获取）
const availableBalance = computed(() => {
  return assetStore?.usdtBalance || 0;
});

// 表单验证
const isFormValid = computed(() => {
  if (orderType.value === 'limit') {
    return price.value && amount.value && parseFloat(price.value) > 0 && parseFloat(amount.value) > 0;
  }
  return amount.value && parseFloat(amount.value) > 0;
});

// 预估手续费
const estimatedFee = computed(() => {
  if (!price.value || !amount.value) return 0;
  const total = parseFloat(price.value) * parseFloat(amount.value);
  const feeRate = assetStore.currentFuturesFeeRate || 0.0004;
  return total * feeRate;
});

// 成交金额
const totalValue = computed(() => {
  if (!amount.value) return 0;
  if (orderType.value === 'market') {
    return markPrice.value * parseFloat(amount.value);
  }
  if (!price.value) return 0;
  return parseFloat(price.value) * parseFloat(amount.value);
});

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0.00';
  return parseFloat(price).toFixed(currentCoinConfig.value.priceFixed);
};

// 格式化数量
const formatQuantity = (quantity) => {
  if (!quantity) return '0.00';
  return parseFloat(quantity).toFixed(currentCoinConfig.value.amountFixed);
};

// 计算深度宽度
const getDepthWidth = (quantity, list, type) => {
  if (!list || list.length === 0) return 0;
  const maxQuantity = Math.max(...list.map(item => item.quantity));
  if (maxQuantity === 0) return 0;
  return (quantity / maxQuantity) * 100;
};

// 选择价格
const selectPrice = (priceValue) => {
  if (orderType.value === 'limit') {
    price.value = priceValue.toString();
  }
};

// 选择百分比
const selectPercent = (pct) => {
  selectedPercent.value = pct;
  const balance = availableBalance.value;
  const maxAmount = balance / (orderType.value === 'market' ? markPrice.value : parseFloat(price.value || markPrice.value));
  amount.value = (maxAmount * (pct / 100)).toFixed(currentCoinConfig.value.amountFixed);
};

// 选择订单类型
const onOrderTypeSelect = (action) => {
  orderType.value = action.value;
  showOrderTypeSheet.value = false;
  if (orderType.value === 'market') {
    price.value = '';
  }
};

// 选择杠杆倍数
const selectLeverage = (leverage) => {
  currentLeverage.value = leverage;
  showLeveragePopup.value = false;
};

// 选择币种
const selectCoin = (coinSymbol) => {
  symbol.value = coinSymbol;
  showCoinSelect.value = false;
  // 重置表单
  price.value = '';
  amount.value = '';
  selectedPercent.value = null;
};

// 开多
const handleLong = () => {
  if (!isFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }

  const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(price.value);
  
  showToast({
    message: orderType.value === 'market' 
      ? t('trade.market_order_submitted') 
      : t('trade.limit_order_submitted'),
    duration: 2000
  });

  // 模拟添加持仓
  const positionValue = orderPrice * parseFloat(amount.value);
  const margin = positionValue / currentLeverage.value;
  const liquidationPrice = calculateLiquidationPrice(orderPrice, currentLeverage.value, 'long');
  
  positions.value.push({
    symbol: symbol.value,
    side: 'long',
    quantity: parseFloat(amount.value),
    entryPrice: orderPrice,
    leverage: currentLeverage.value,
    margin: margin,
    liquidationPrice: liquidationPrice,
    unrealizedPnl: 0,
    unrealizedPnlPercent: 0
  });

  // 重置表单
  amount.value = '';
  price.value = '';
  selectedPercent.value = null;
};

// 开空
const handleShort = () => {
  if (!isFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }

  const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(price.value);
  
  showToast({
    message: orderType.value === 'market' 
      ? t('trade.market_order_submitted') 
      : t('trade.limit_order_submitted'),
    duration: 2000
  });

  // 模拟添加持仓
  const positionValue = orderPrice * parseFloat(amount.value);
  const margin = positionValue / currentLeverage.value;
  const liquidationPrice = calculateLiquidationPrice(orderPrice, currentLeverage.value, 'short');
  
  positions.value.push({
    symbol: symbol.value,
    side: 'short',
    quantity: parseFloat(amount.value),
    entryPrice: orderPrice,
    leverage: currentLeverage.value,
    margin: margin,
    liquidationPrice: liquidationPrice,
    unrealizedPnl: 0,
    unrealizedPnlPercent: 0
  });

  // 重置表单
  amount.value = '';
  price.value = '';
  selectedPercent.value = null;
};

// 计算强平价格
const calculateLiquidationPrice = (entryPrice, leverage, side) => {
  // 简化的强平价格计算（全仓模式）
  // 实际应该考虑维持保证金率等因素
  if (side === 'long') {
    return entryPrice * (1 - 1 / leverage * 0.9); // 假设维持保证金率为10%
  } else {
    return entryPrice * (1 + 1 / leverage * 0.9);
  }
};

// 计算未实现盈亏
const calculateUnrealizedPnl = (position) => {
  const currentPrice = markPrice.value;
  const priceDiff = currentPrice - position.entryPrice;
  
  if (position.side === 'long') {
    return priceDiff * position.quantity;
  } else {
    return -priceDiff * position.quantity;
  }
};

// 计算未实现盈亏百分比
const calculateUnrealizedPnlPercent = (position) => {
  const pnl = calculateUnrealizedPnl(position);
  const margin = position.margin || (position.entryPrice * position.quantity / position.leverage);
  return margin > 0 ? (pnl / margin) * 100 : 0;
};

// 格式化未实现盈亏（显示绝对值，符号由模板控制）
const formatUnrealizedPnl = (pnl) => {
  if (!pnl && pnl !== 0) return '0.00';
  return Math.abs(pnl).toFixed(2);
};

// 更新持仓的未实现盈亏
const updatePositionsPnl = () => {
  positions.value.forEach(position => {
    position.unrealizedPnl = calculateUnrealizedPnl(position);
    position.unrealizedPnlPercent = calculateUnrealizedPnlPercent(position);
  });
};

// 监听标记价格变化，更新未实现盈亏
watch(markPrice, () => {
  updatePositionsPnl();
}, { immediate: true });

// 止盈止损
const handleTakeProfitStopLoss = (position, index) => {
  currentTPSLPosition.value = { position, index };
  tpSlForm.value.takeProfitPrice = '';
  tpSlForm.value.stopLossPrice = '';
  showTPSLPopup.value = true;
};

// 确认止盈止损
const confirmTPSL = () => {
  if (!tpSlForm.value.takeProfitPrice && !tpSlForm.value.stopLossPrice) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }
  
  showToast({
    message: t('trade.take_profit_stop_loss') + ' ' + t('trade.order_submitted'),
    duration: 2000
  });
  
  showTPSLPopup.value = false;
  currentTPSLPosition.value = null;
};

// 平仓
const handleClosePosition = async (position, index) => {
  try {
    await showConfirmDialog({
      title: t('trade.close_position_confirm'),
      message: t('trade.close_position_message'),
      confirmButtonText: t('trade.close_position_confirm_btn'),
      cancelButtonText: t('trade.close_position_cancel_btn'),
      confirmButtonColor: '#F6465D'
    });
    
    // 执行平仓
    positions.value.splice(index, 1);
    
    showToast({
      message: t('trade.position_closed'),
      icon: 'success',
      duration: 2000
    });
  } catch {
    // 用户取消
  }
};

// 跳转到K线图
const goToKlineChart = () => {
  showToast({ message: t('trade.chart_coming_soon'), duration: 2000 });
};

// 初始化
onMounted(() => {
  // 确保 WebSocket 连接
  marketStore.ensureConnection();
  
  // 从路由参数获取币种
  if (route.query.symbol) {
    symbol.value = route.query.symbol;
  }
});

onUnmounted(() => {
  // 组件卸载时不需要关闭 WebSocket，因为其他页面可能也在使用
});
</script>

<style scoped>
.futures-trade-page {
  min-height: 100vh;
  background-color: #000000;
  color: #FFFFFF;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  padding-bottom: 45vh;
}

/* 顶部导航栏 */
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #000000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  flex: 0 0 auto;
  cursor: pointer;
}

.header-action-left {
  display: flex;
  align-items: center;
}

.custom-back-svg {
  width: 24px;
  height: 24px;
}

.header-center {
  flex: 1;
  text-align: center;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #FCD535;
}

.nav-right-icon-wrap {
  flex: 0 0 auto;
  cursor: pointer;
}

.kline-svg-icon {
  width: 24px;
  height: 24px;
}

/* 合约控制栏 */
.futures-control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #0E0E0E;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.margin-mode-toggle {
  display: flex;
  gap: 8px;
  flex: 1;
}

.mode-btn {
  flex: 1;
  padding: 8px 16px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  text-align: center;
  font-size: 13px;
  color: #8E8E93;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn.active {
  background-color: #FCD535;
  color: #000000;
  border-color: #FCD535;
  font-weight: 600;
}

.leverage-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FCD535;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.leverage-btn:active {
  background-color: #252A32;
}

/* 交易对信息 */
.pair-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #0E0E0E;
}

.pair-selector {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.pair-name {
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
}

.price-change {
  font-size: 14px;
  font-weight: 600;
  color: #F6465D;
}

.price-change.positive {
  color: #0ECB81;
}

/* 核心交易区 */
.trade-main {
  display: flex;
  height: calc(100vh - 280px);
  min-height: 400px;
}

/* 左侧盘口区 */
.orderbook-side {
  flex: 0 0 42%;
  background-color: #0E0E0E;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 11px;
  color: #8E8E93;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-price, .header-quantity {
  flex: 1;
}

.asks-list, .bids-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.asks-list {
  flex-direction: column-reverse;
}

.order-row {
  position: relative;
  display: flex;
  justify-content: space-between;
  padding: 4px 12px;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.order-row:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.depth-bar {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  width: var(--depth-width);
  opacity: 0.15;
  z-index: 0;
}

.ask-depth {
  background-color: #F6465D;
}

.bid-depth {
  background-color: #0ECB81;
}

.price, .quantity {
  position: relative;
  z-index: 1;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

.ask-price {
  color: #F6465D;
}

.bid-price {
  color: #0ECB81;
}

.quantity {
  color: #8E8E93;
}

.last-price {
  padding: 16px 12px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.last-price.up {
  background-color: rgba(14, 203, 129, 0.05);
}

.last-price.down {
  background-color: rgba(246, 70, 93, 0.05);
}

.price-main {
  font-size: 20px;
  font-weight: 700;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

.price-fiat {
  font-size: 12px;
  color: #8E8E93;
  margin-top: 4px;
}

/* 右侧表单区 */
.form-side {
  flex: 0 0 58%;
  background-color: #0E0E0E;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.order-type-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #1C1C1E;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #FFFFFF;
}

.input-row {
  width: 100%;
}

.input-field {
  width: 100%;
  padding: 14px 16px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

.input-field:focus {
  outline: none;
  border-color: #FCD535;
}

.input-field.market-price-input {
  color: #8E8E93;
  cursor: not-allowed;
}

.percent-buttons {
  display: flex;
  gap: 8px;
}

.percent-btn {
  flex: 1;
  padding: 10px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #8E8E93;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.percent-btn.active {
  background-color: #FCD535;
  color: #000000;
  border-color: #FCD535;
  font-weight: 600;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #8E8E93;
}

.info-value {
  color: #FFFFFF;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* 开多/开空按钮 */
.futures-action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
  padding-top: 16px;
}

.long-btn, .short-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-variant-numeric: tabular-nums;
}

.long-btn {
  background-color: #0ECB81;
  color: #000000;
}

.long-btn:hover:not(:disabled) {
  background-color: #0db870;
}

.short-btn {
  background-color: #F6465D;
  color: #FFFFFF;
}

.short-btn:hover:not(:disabled) {
  background-color: #e63950;
}

.long-btn:disabled, .short-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 持仓区域 */
.positions-section {
  background-color: #0E0E0E;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 45vh;
  display: flex;
  flex-direction: column;
  z-index: 50;
}

.position-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.position-tabs .van-tabs__wrap) {
  background-color: #0E0E0E;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.position-tabs .van-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

:deep(.position-tabs .van-tab__panel) {
  height: 100%;
  overflow-y: auto;
}

.positions-list, .orders-list, .history-list {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 100%;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #8E8E93;
  font-size: 14px;
}

/* 专业持仓卡片 */
.position-card {
  background-color: #1C1C1E;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.position-card-main {
  display: grid;
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 16px;
  align-items: start;
}

@media (max-width: 768px) {
  .position-card-main {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.position-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.position-left {
  flex: 0 0 auto;
  min-width: 120px;
}

.position-symbol-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.position-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

.position-perpetual {
  font-size: 11px;
  color: #8E8E93;
  padding: 2px 6px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.position-leverage {
  font-size: 13px;
  color: #FCD535;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.position-center {
  flex: 1;
  text-align: center;
  padding: 0 16px;
}

.unrealized-pnl-label {
  font-size: 12px;
  color: #8E8E93;
  margin-bottom: 8px;
}

.unrealized-pnl-value {
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  margin-bottom: 4px;
  line-height: 1.2;
}

.unrealized-pnl-value.positive {
  color: #0ECB81;
}

.unrealized-pnl-value.negative {
  color: #F6465D;
}

.unrealized-pnl-percent {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.unrealized-pnl-percent.positive {
  color: #0ECB81;
}

.unrealized-pnl-percent.negative {
  color: #F6465D;
}

.position-right {
  flex: 0 0 auto;
  min-width: 140px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.position-info-row {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: 12px;
}

.info-label {
  color: #8E8E93;
  font-size: 11px;
}

.info-value {
  color: #FFFFFF;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  text-align: right;
  font-size: 13px;
}

.liquidation-price {
  color: #F6465D;
  font-weight: 700;
}

.position-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.action-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tp-sl-btn {
  background-color: rgba(252, 213, 53, 0.1);
  color: #FCD535;
  border: 1px solid rgba(252, 213, 53, 0.3);
}

.tp-sl-btn:active {
  background-color: rgba(252, 213, 53, 0.2);
}

.close-btn {
  background-color: rgba(246, 70, 93, 0.1);
  color: #F6465D;
  border: 1px solid rgba(246, 70, 93, 0.3);
}

.close-btn:active {
  background-color: rgba(246, 70, 93, 0.2);
}

/* 止盈止损弹窗 */
.tp-sl-popup-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tp-sl-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.tp-sl-popup-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
}

.tp-sl-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item label {
  font-size: 14px;
  color: #8E8E93;
}

.form-item input {
  padding: 14px 16px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

.form-item input:focus {
  outline: none;
  border-color: #FCD535;
}

.submit-btn {
  margin-top: 8px;
  padding: 16px;
  background-color: #FCD535;
  color: #000000;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:active {
  background-color: #e6c42f;
}

:deep(.tp-sl-popup .van-popup) {
  background: #1C1C1E !important;
}

/* 弹窗样式 */
.leverage-popup-content, .coin-select-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.leverage-popup-header, .coin-select-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.leverage-popup-title, .coin-select-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
}

.close-icon {
  cursor: pointer;
  color: #8E8E93;
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
  padding: 16px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
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

.coin-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.coin-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #1C1C1E;
  border-radius: 8px;
  color: #FFFFFF;
  cursor: pointer;
  transition: all 0.2s ease;
}

.coin-item:active {
  background-color: #252A32;
}

.coin-item.active {
  background-color: rgba(252, 213, 53, 0.1);
  border-color: #FCD535;
  color: #FCD535;
}

/* 深度覆盖弹窗背景 */
:deep(.leverage-popup .van-popup),
:deep(.coin-select-popup .van-popup) {
  background: #1C1C1E !important;
}

:deep(.van-action-sheet) {
  background: #1C1C1E !important;
}

:deep(.van-action-sheet__item) {
  background: #1C1C1E !important;
  color: #FFFFFF !important;
}

:deep(.van-action-sheet__item:active) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}
</style>
