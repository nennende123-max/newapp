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
        :class="{ active: activeTradeTab === 'futures' }"
        @click="activeTradeTab = 'futures'"
      >
        {{ t('assets.futures') }}
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

    <!-- 现货交易界面 -->
    <div v-if="activeTradeTab === 'spot'" class="trade-main">
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

    <!-- 合约交易界面 -->
    <div v-else-if="activeTradeTab === 'futures'" class="futures-trade-container">
      <!-- 合约控制栏：全仓文本 + 杠杆倍数（左边），资金费率（右边） -->
      <div class="futures-control-bar">
        <div class="control-left">
          <div class="margin-mode-text">
            {{ t('trade.full_position') }}
          </div>
          <button class="leverage-btn" @click="showLeveragePopup = true">
            <span>{{ currentLeverage }}x</span>
            <van-icon name="arrow-down" size="12" color="#848E9C" />
          </button>
        </div>
        <div class="control-right">
          <div class="funding-rate-info">
            <span class="funding-rate-label">{{ t('trade.funding_rate') }}</span>
            <span class="funding-rate-value" :class="{ positive: fundingRate >= 0, negative: fundingRate < 0 }">
              {{ fundingRate >= 0 ? '+' : '' }}{{ (fundingRate * 100).toFixed(4) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- 核心交易区 - 左右布局 -->
      <div class="futures-trade-main">
        <!-- 左侧：盘口区 (42%) -->
        <div class="futures-orderbook-side">
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
              @click="selectFuturesPrice(ask.price)"
            >
              <div class="depth-bar ask-depth"></div>
              <span class="price ask-price">{{ formatPrice(ask.price) }}</span>
              <span class="quantity">{{ formatQuantity(ask.quantity) }}</span>
            </div>
          </div>

          <div class="last-price" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
            <div class="price-main">{{ formatPrice(markPrice) }}</div>
            <div class="price-fiat">${{ formatPrice(markPrice) }}</div>
          </div>

          <div class="bids-list">
            <div 
              v-for="(bid, index) in bids" 
              :key="`bid-${index}`"
              class="order-row bid-row"
              :style="{ '--depth-width': getDepthWidth(bid.quantity, bids, 'bids') + '%' }"
              @click="selectFuturesPrice(bid.price)"
            >
              <div class="depth-bar bid-depth"></div>
              <span class="price bid-price">{{ formatPrice(bid.price) }}</span>
              <span class="quantity">{{ formatQuantity(bid.quantity) }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧：交易表单 (58%) -->
        <div class="futures-form-side">
          <div class="order-type-selector" @click="showOrderTypeSheet = true">
            <span>{{ orderType === 'limit' ? t('trade.limit_order') : t('trade.market_order') }}</span>
            <van-icon name="arrow-down" size="12" color="#848E9C" />
          </div>

          <div class="input-row">
            <input
              v-if="orderType === 'limit'"
              v-model="futuresPrice"
              type="number"
              :placeholder="markPrice.toFixed(currentCoinConfig.priceFixed)"
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

          <div class="input-row">
            <input
              v-model="futuresAmount"
              type="number"
              :placeholder="t('trade.amount_placeholder')"
              class="input-field no-spinner"
            />
          </div>

          <div class="percent-row">
            <div 
              v-for="percent in [25, 50, 75, 100]"
              :key="percent"
              class="percent-btn"
              :class="{ active: selectedFuturesPercent === percent }"
              @click="setFuturesAmountPercent(percent)"
            >
              {{ percent }}%
            </div>
          </div>

          <div class="fee-estimate-row">
            <span class="fee-estimate-label">{{ t('trade.estimated_fee') }}(USDT)</span>
            <span class="fee-estimate-value">{{ formatFuturesEstimatedFee }}</span>
          </div>

          <div class="total-row">
            <span class="total-label">{{ t('trade.total') }}(USDT)</span>
            <span class="total-value">{{ formatFuturesTotalAmount }}</span>
          </div>

          <div class="available-row">
            <div class="avail-item">
              <span class="avail-label">{{ t('trade.avail') }}：</span>
              <span class="avail-value">{{ formatNumber(availableBalance) }} USDT</span>
            </div>
          </div>

          <div class="futures-action-buttons">
            <button 
              class="long-btn"
              :disabled="!isFuturesFormValid"
              @click="handleLong"
            >
              {{ t('trade.open_long') }}
            </button>
            <button 
              class="short-btn"
              :disabled="!isFuturesFormValid"
              @click="handleShort"
            >
              {{ t('trade.open_short') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 底部：持仓看板 -->
      <div class="futures-bottom-section">
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
          <van-tab :title="t('trade.positions_tab', { count: positions.length })">
            <div class="positions-list">
              <div v-if="positions.length === 0" class="empty-state">
                {{ t('trade.no_positions') }}
              </div>
              <div 
                v-for="(position, index) in positions" 
                :key="index"
                class="position-card"
              >
                <div class="position-card-main">
                  <div class="position-left">
                    <div class="position-symbol-row">
                      <span class="position-symbol">{{ position.symbol }}USDT</span>
                      <span class="position-perpetual">{{ t('trade.perpetual') }}</span>
                    </div>
                    <div class="position-leverage">
                      {{ position.leverage || currentLeverage }}x
                    </div>
                  </div>

                  <div class="position-center">
                    <div class="unrealized-pnl-label">{{ t('trade.unrealized_pnl') }}</div>
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

                  <div class="position-right">
                    <div class="position-info-row">
                      <span class="info-label">{{ t('trade.liquidation_price') }}:</span>
                      <span class="info-value liquidation-price">{{ formatPrice(position.liquidationPrice) }}</span>
                    </div>
                    <div class="position-info-row">
                      <span class="info-label">{{ t('trade.margin_amount') }}:</span>
                      <span class="info-value">{{ formatPrice(position.margin) }} USDT</span>
                    </div>
                    <div class="position-info-row">
                      <span class="info-label">{{ t('trade.position_size') }}:</span>
                      <span class="info-value">{{ formatQuantity(position.quantity) }} {{ position.symbol }}</span>
                    </div>
                  </div>
                </div>

                <div class="position-actions">
                  <button class="action-btn tp-sl-btn" @click="handleTakeProfitStopLoss(position, index)">
                    {{ t('trade.take_profit_stop_loss') }}
                  </button>
                  <button class="action-btn close-btn" @click="handleClosePosition(position, index)">
                    {{ t('trade.close_position') }}
                  </button>
                </div>
              </div>
            </div>
          </van-tab>
          <van-tab :title="t('trade.open_orders_tab')">
            <div class="orders-list">
              <div class="empty-state">
                {{ t('trade.no_orders') }}
              </div>
            </div>
          </van-tab>
          <van-tab :title="t('trade.trade_history_tab')">
            <div class="history-list">
              <div class="empty-state">
                {{ t('trade.no_orders') }}
              </div>
            </div>
          </van-tab>
        </van-tabs>
      </div>
    </div>

    <div v-if="activeTradeTab === 'spot'" class="bottom-section">
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
          <h3>{{ t('trade.take_profit_stop_loss') }}</h3>
          <van-icon name="cross" @click="showTPSLPopup = false" class="close-icon" />
        </div>
        <div class="tp-sl-form">
          <div class="form-item">
            <label>{{ t('trade.take_profit_price') }}</label>
            <input v-model="tpSlForm.takeProfitPrice" type="number" :placeholder="markPrice.toFixed(2)" />
          </div>
          <div class="form-item">
            <label>{{ t('trade.stop_loss_price') }}</label>
            <input v-model="tpSlForm.stopLossPrice" type="number" :placeholder="markPrice.toFixed(2)" />
          </div>
          <button class="submit-btn" @click="confirmTPSL">
            {{ t('common.confirm') }}
          </button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated, onDeactivated } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, Icon, Popup, Empty, ActionSheet, Tabs, Tab, showConfirmDialog } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { useMarketStore } from '@/stores/market';

defineOptions({
  name: 'Trade'
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n(); 
const assetStore = useAssetStore();
const marketStore = useMarketStore();

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
const currentLeverage = ref(20); // 默认杠杆20x 
const showLeveragePopup = ref(false);

// 合约交易相关变量
const marginMode = ref('cross'); // 'cross' 全仓, 'isolated' 逐仓
const markPrice = ref(92255.50);
const futuresPrice = ref('');
const futuresAmount = ref('');
const selectedFuturesPercent = ref(null);
const activePositionTab = ref(0);
const positions = ref([]);
const showTPSLPopup = ref(false);
const currentTPSLPosition = ref(null);
const tpSlForm = ref({
  takeProfitPrice: '',
  stopLossPrice: ''
});
// 资金费率（每8小时更新一次，通常范围在 -0.01% 到 0.01% 之间）
const fundingRate = ref(0.0001); // 0.01% = 0.0001 

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
    
    // 合约交易使用合约账户余额
    if (activeTradeTab.value === 'futures') {
      return assetStore?.usdtBalance || 0;
    }
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

const leverageOptions = [20, 50, 100, 125];
const selectLeverage = (leverage) => { currentLeverage.value = leverage; showLeveragePopup.value = false; };

const isOrderValid = computed(() => {
  const a = parseFloat(amount.value);
  if (orderType.value === 'market') return a > 0;
  else { const p = parseFloat(price.value); return p > 0 && a > 0; }
});

// 合约交易相关方法
const selectFuturesPrice = (priceValue) => {
  if (orderType.value === 'limit') {
    futuresPrice.value = priceValue.toString();
  }
};

const setFuturesAmountPercent = (percent) => {
  selectedFuturesPercent.value = percent;
  const balance = assetStore?.usdtBalance || 0;
  const maxAmount = balance / (orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value || markPrice.value));
  futuresAmount.value = (maxAmount * (percent / 100)).toFixed(currentCoinConfig.value.amountFixed);
};

const formatFuturesEstimatedFee = computed(() => {
  if (!futuresPrice.value || !futuresAmount.value) return '0.00';
  const total = parseFloat(futuresPrice.value) * parseFloat(futuresAmount.value);
  const feeRate = assetStore.currentFuturesFeeRate || 0.0004;
  const fee = total * feeRate;
  return fee > 0 ? fee.toFixed(4) : '0.00';
});

const formatFuturesTotalAmount = computed(() => {
  if (!futuresAmount.value) return '0.00';
  if (orderType.value === 'market') {
    return (markPrice.value * parseFloat(futuresAmount.value)).toFixed(2);
  }
  if (!futuresPrice.value) return '0.00';
  return (parseFloat(futuresPrice.value) * parseFloat(futuresAmount.value)).toFixed(2);
});

const isFuturesFormValid = computed(() => {
  if (orderType.value === 'limit') {
    return futuresPrice.value && futuresAmount.value && parseFloat(futuresPrice.value) > 0 && parseFloat(futuresAmount.value) > 0;
  }
  return futuresAmount.value && parseFloat(futuresAmount.value) > 0;
});

const calculateLiquidationPrice = (entryPrice, leverage, side) => {
  if (side === 'long') {
    return entryPrice * (1 - 1 / leverage * 0.9);
  } else {
    return entryPrice * (1 + 1 / leverage * 0.9);
  }
};

const calculateUnrealizedPnl = (position) => {
  const currentPrice = markPrice.value;
  const priceDiff = currentPrice - position.entryPrice;
  if (position.side === 'long') {
    return priceDiff * position.quantity;
  } else {
    return -priceDiff * position.quantity;
  }
};

const calculateUnrealizedPnlPercent = (position) => {
  const pnl = calculateUnrealizedPnl(position);
  const margin = position.margin || (position.entryPrice * position.quantity / position.leverage);
  return margin > 0 ? (pnl / margin) * 100 : 0;
};

const formatUnrealizedPnl = (pnl) => {
  if (!pnl && pnl !== 0) return '0.00';
  return Math.abs(pnl).toFixed(2);
};

const updatePositionsPnl = () => {
  positions.value.forEach(position => {
    position.unrealizedPnl = calculateUnrealizedPnl(position);
    position.unrealizedPnlPercent = calculateUnrealizedPnlPercent(position);
  });
};

const handleLong = () => {
  if (!isFuturesFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }
  const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value);
  showToast({
    message: orderType.value === 'market' 
      ? t('trade.market_order_submitted') 
      : t('trade.limit_order_submitted'),
    duration: 2000
  });
  const positionValue = orderPrice * parseFloat(futuresAmount.value);
  const margin = positionValue / currentLeverage.value;
  const liquidationPrice = calculateLiquidationPrice(orderPrice, currentLeverage.value, 'long');
  positions.value.push({
    symbol: symbol.value,
    side: 'long',
    quantity: parseFloat(futuresAmount.value),
    entryPrice: orderPrice,
    leverage: currentLeverage.value,
    margin: margin,
    liquidationPrice: liquidationPrice,
    unrealizedPnl: 0,
    unrealizedPnlPercent: 0
  });
  futuresAmount.value = '';
  futuresPrice.value = '';
  selectedFuturesPercent.value = null;
};

const handleShort = () => {
  if (!isFuturesFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }
  const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value);
  showToast({
    message: orderType.value === 'market' 
      ? t('trade.market_order_submitted') 
      : t('trade.limit_order_submitted'),
    duration: 2000
  });
  const positionValue = orderPrice * parseFloat(futuresAmount.value);
  const margin = positionValue / currentLeverage.value;
  const liquidationPrice = calculateLiquidationPrice(orderPrice, currentLeverage.value, 'short');
  positions.value.push({
    symbol: symbol.value,
    side: 'short',
    quantity: parseFloat(futuresAmount.value),
    entryPrice: orderPrice,
    leverage: currentLeverage.value,
    margin: margin,
    liquidationPrice: liquidationPrice,
    unrealizedPnl: 0,
    unrealizedPnlPercent: 0
  });
  futuresAmount.value = '';
  futuresPrice.value = '';
  selectedFuturesPercent.value = null;
};

const handleTakeProfitStopLoss = (position, index) => {
  currentTPSLPosition.value = { position, index };
  tpSlForm.value.takeProfitPrice = '';
  tpSlForm.value.stopLossPrice = '';
  showTPSLPopup.value = true;
};

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

const handleClosePosition = async (position, index) => {
  try {
    await showConfirmDialog({
      title: t('trade.close_position_confirm'),
      message: t('trade.close_position_message'),
      confirmButtonText: t('trade.close_position_confirm_btn'),
      cancelButtonText: t('trade.close_position_cancel_btn'),
      confirmButtonColor: '#F6465D'
    });
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

// 监听标记价格变化
watch(markPrice, () => {
  updatePositionsPnl();
}, { immediate: true });

// 从 marketStore 获取标记价格
watch(() => marketStore.getTicker(symbol.value), (ticker) => {
  if (ticker) {
    markPrice.value = ticker.price || markPrice.value;
    priceChange.value = ticker.change || priceChange.value;
  }
}, { immediate: true });

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

// 初始化函数
const initializeTrade = () => {
  generateOrderBook();
  // 首次进入也初始化价格
  updatePriceForSymbol(symbol.value);
  
  // 确保 WebSocket 连接（用于合约交易的标记价格）
  marketStore.ensureConnection();
  
  if (ordersList.value.length === 0) {
    const now = Date.now();
    const buyPrice = lastPrice.value * 0.998;
    ordersList.value.push({ side: 'buy', type: 'limit', price: buyPrice, quantity: 0.0015, symbol: symbol.value, timestamp: now - 300000 });
    const sellPrice = lastPrice.value * 1.002;
    ordersList.value.push({ side: 'sell', type: 'limit', price: sellPrice, quantity: 0.002, symbol: symbol.value, timestamp: now - 180000 });
  }
};

onMounted(() => {
  initializeTrade();
});

// Keep-alive 激活时
onActivated(() => {
  initializeTrade();
});

// Keep-alive 停用时
onDeactivated(() => {
  // 可以在这里清理资源
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
  padding: 12px 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #0E0E0E; /* 改为纯黑背景，更符合黑金风格 */
  height: 320px; /* 设置固定高度，确保列表高度一致 */
  overflow: hidden;
}

.panel-full {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto; /* 内部滚动 */
  scrollbar-width: none; /* 隐藏滚动条 (Firefox) */
  -ms-overflow-style: none; /* 隐藏滚动条 (IE/Edge) */
}

.panel-full::-webkit-scrollbar {
  display: none; /* 隐藏滚动条 (Chrome/Safari) */
}

.orders-panel, .assets-panel { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  min-height: 0; 
}

.orders-list { 
  display: flex; 
  flex-direction: column; 
  gap: 10px; 
  padding-bottom: 20px;
}

.orders-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; padding: 20px; flex: 1;
}

.empty-icon { margin-bottom: 12px; opacity: 0.6; }
.empty-text { font-size: 14px; color: #8E8E93; margin-bottom: 16px; }
.empty-action-btn {
  padding: 8px 24px; background-color: #1C1C1E; color: #FCD535; border: 1px solid rgba(252, 213, 53, 0.3);
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease;
}
.empty-action-btn:active { background-color: #252A32; transform: scale(0.98); }

.order-item {
  display: flex; align-items: center; padding: 14px 12px; background-color: #141414;
  border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.03); transition: all 0.2s ease;
}
.order-item:active { background-color: #1C1C1E; }

.order-left { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; min-width: 110px; }
.order-side-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; white-space: nowrap; }
.order-side-badge.buy { background-color: rgba(14, 203, 129, 0.12); color: #0ECB81; }
.order-side-badge.sell { background-color: rgba(246, 70, 93, 0.12); color: #F6465D; }
.order-symbol-time { display: flex; flex-direction: column; gap: 4px; }
.order-symbol { font-size: 14px; font-weight: 700; color: #FFFFFF; }
.order-time { font-size: 11px; color: #8E8E93; font-family: 'DIN Alternate', monospace; }
.order-center { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 0 12px; min-width: 0; }
.order-price { font-size: 15px; font-weight: 700; color: #FFFFFF; font-family: 'DIN Alternate', monospace; }
.order-quantity { font-size: 12px; color: #8E8E93; font-family: 'DIN Alternate', monospace; }
.order-right { flex: 0 0 auto; }
.cancel-btn { 
  padding: 6px 16px; background-color: #1C1C1E; color: #8E8E93; 
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; 
  font-size: 12px; font-weight: 600; transition: all 0.2s ease;
}
.cancel-btn:active { background-color: #252A32; color: #FFFFFF; border-color: rgba(255, 255, 255, 0.15); }

.assets-list { display: flex; flex-direction: column; gap: 10px; padding-bottom: 20px; }

.asset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 16px; 
  background-color: #141414;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.03);
  transition: all 0.2s ease;
}
.asset-item:active { background-color: #1C1C1E; }

.asset-label { font-size: 14px; color: #8E8E93; font-weight: 500; }
.asset-value { font-size: 15px; font-weight: 700; color: #FFFFFF; font-family: 'DIN Alternate', sans-serif; }

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

/* ========== 合约交易样式 ========== */
.futures-trade-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.futures-control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #0E0E0E;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  gap: 12px;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.margin-mode-text {
  font-size: 13px;
  color: #8E8E93;
  font-weight: 500;
}

.control-right {
  display: flex;
  align-items: center;
}

.funding-rate-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.funding-rate-label {
  font-size: 11px;
  color: #8E8E93;
  font-weight: 400;
}

.funding-rate-value {
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.funding-rate-value.positive {
  color: #0ECB81;
}

.funding-rate-value.negative {
  color: #F6465D;
}

.futures-trade-main {
  display: flex;
  gap: 8px;
  flex: 1;
  min-height: 0;
  padding: 8px 8px 8px 0;
}

.futures-orderbook-side {
  width: 42%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background-color: #0E0E0E;
  border-radius: 4px;
  overflow: hidden;
  padding: 0;
}

.futures-form-side {
  width: 58%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.futures-action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
  padding-top: 16px;
}

.long-btn, .short-btn {
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

.long-btn {
  background-color: #0ECB81;
  color: #000000;
}

.short-btn {
  background-color: #F6465D;
  color: #FFFFFF;
}

.long-btn:disabled, .short-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.futures-bottom-section {
  background-color: #1E2329;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  min-height: 320px;
  max-height: 45vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.position-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.position-tabs .van-tabs__wrap) {
  background-color: #1E2329;
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

.tp-sl-form .form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tp-sl-form .form-item label {
  font-size: 14px;
  color: #8E8E93;
}

.tp-sl-form .form-item input {
  padding: 14px 16px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

.tp-sl-form .form-item input:focus {
  outline: none;
  border-color: #FCD535;
}

.tp-sl-form .submit-btn {
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

.tp-sl-form .submit-btn:active {
  background-color: #e6c42f;
}

:deep(.tp-sl-popup .van-popup) {
  background: #1C1C1E !important;
}
</style>