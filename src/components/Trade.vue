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
            @click="() => { orderSide = 'buy'; spotSliderValue = 0; amount.value = ''; }"
          >
            {{ t('trade.buy') }}
          </div>
          <div 
            class="toggle-btn sell-btn" 
            :class="{ active: orderSide === 'sell' }"
            @click="() => { orderSide = 'sell'; spotSliderValue = 0; amount.value = ''; }"
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

        <div class="slider-wrapper">
          <van-slider
            v-model="spotSliderValue"
            :min="0"
            :max="100"
            :step="1"
            bar-height="4px"
            button-size="16px"
            active-color="#FCD535"
            inactive-color="#2A2D35"
            @update:model-value="onSpotSliderChange"
          >
            <template #button>
              <div class="custom-slider-button">{{ spotSliderValue }}%</div>
            </template>
          </van-slider>
          <div class="slider-marks">
            <span 
              v-for="val in [0, 25, 50, 75, 100]" 
              :key="val" 
              class="mark-item"
              @click="spotSliderValue = val; onSpotSliderChange(val)"
            >
              {{ val }}%
            </span>
          </div>
        </div>

        <div class="fee-estimate-row">
          <span class="fee-estimate-label">{{ t('trade.estimated_fee') }}({{ orderSide === 'buy' ? currentCoinConfig.baseCoin : 'USDT' }})</span>
          <span class="fee-estimate-value">
            {{ formatEstimatedFee }}
            <span v-if="orderSide === 'buy' && formatEstimatedFeeUSDT" class="fee-usdt-note">(≈ {{ formatEstimatedFeeUSDT }} USDT)</span>
          </span>
        </div>

        <div class="total-row">
          <span class="total-label">{{ t('trade.total') }}(USDT)</span>
          <span class="total-value">{{ formatTotalAmount }}</span>
        </div>

        <div class="estimated-received-row">
          <span class="received-label">{{ t('trade.estimated_received') }}</span>
          <span class="received-value">{{ formatEstimatedReceived }}</span>
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
          :disabled="!isOrderValid || isLoading"
          :loading="isLoading"
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
              @input="handleFuturesAmountInput"
            />
          </div>

          <div class="slider-wrapper">
            <van-slider
              v-model="futuresSliderValue"
              :min="0"
              :max="100"
              :step="1"
              bar-height="4px"
              button-size="16px"
              active-color="#FCD535"
              inactive-color="#2A2D35"
              @update:model-value="onFuturesSliderChange"
            >
              <template #button>
                <div class="custom-slider-button">{{ futuresSliderValue }}%</div>
              </template>
            </van-slider>
            <div class="slider-marks">
              <span 
                v-for="val in [0, 25, 50, 75, 100]" 
                :key="val" 
                class="mark-item"
                @click="futuresSliderValue = val; onFuturesSliderChange(val)"
              >
                {{ val }}%
              </span>
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
              <span class="avail-value">{{ formatAssetBalance(availableBalance, 'USDT') }} USDT</span>
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
                <span class="asset-value">{{ formatAssetBalance(assetStore.getHolding(symbol), symbol) }} {{ symbol }}</span>
              </div>
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.frozen') }}</span>
                <span class="asset-value">{{ formatAssetBalance(assetStore.userAssets?.[`${symbol}_frozen`] || 0, symbol) }} {{ symbol }}</span>
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
import { showToast, Icon, Popup, Empty, ActionSheet, Tabs, Tab, showConfirmDialog, Slider } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { useMarketStore } from '@/stores/market';
import { createOrder, getOrders, cancelOrder as cancelOrderApi } from '@/api/trade';
import { createFuturesOrder, getPositions as getFuturesPositionsApi, closePosition as closeFuturesPositionApi } from '@/api/futures';
import { formatAssetAmount } from '@/utils/format';

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
  // 主流高价币：价格保留2位，数量保留4-6位
  'BTC/USDT': { priceFixed: 2, amountFixed: 6, step: 0.01, baseCoin: 'BTC' },
  'ETH/USDT': { priceFixed: 2, amountFixed: 4, step: 0.01, baseCoin: 'ETH' },
  'BNB/USDT': { priceFixed: 2, amountFixed: 3, step: 0.1, baseCoin: 'BNB' },
  'SOL/USDT': { priceFixed: 2, amountFixed: 2, step: 0.01, baseCoin: 'SOL' },
  // 低价币：价格保留4位(看清微小波动)，数量保留2位(不需要太碎)
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
const spotSliderValue = ref(0); // 现货滑块值 (0-100)
const ordersList = ref([]);
const showOrderTypeSheet = ref(false);
const currentLeverage = ref(20); // 默认杠杆20x
const isLoading = ref(false); // 下单加载状态 
const showLeveragePopup = ref(false);

// 合约交易相关变量
const marginMode = ref('cross'); // 'cross' 全仓, 'isolated' 逐仓
const markPrice = ref(92255.50);
const futuresPrice = ref('');
const futuresAmount = ref('');
const selectedFuturesPercent = ref(null);
const futuresSliderValue = ref(0); // 合约滑块值 (0-100)
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

// 模拟币种价格数据（与后端 MOCK_MARKET_PRICES 保持一致）
const coinPrices = {
  'BTC': 92255.0,
  'ETH': 3100.0,
  'BNB': 590.0,
  'SOL': 145.0,
  'DOGE': 0.12,
  'TRX': 0.15,
  'BEAT': 1.2,
  'AIC': 2.0
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

const frozenBalance = computed(() => {
  // 1. 简单判空保护
  if (!assetStore.userAssets) return 0;
  
  // 2. 根据当前是"买"还是"卖"来决定显示哪个币种的冻结额
  // 买入时 (Buy BTC) -> 显示冻结的 USDT
  if (orderSide.value === 'buy') {
    return assetStore.userAssets['USDT_frozen'] || 0;
  }
  // 卖出时 (Sell BTC) -> 显示冻结的 BTC (即 symbol)
  else {
    const frozenKey = `${symbol.value}_frozen`;
    return assetStore.userAssets[frozenKey] || 0;
  }
});

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

// 格式化资产数量（使用统一的格式化函数）
const formatAssetBalance = (value, symbol = '') => {
  return formatAssetAmount(value, symbol);
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
  if (value === '' || value === '-') { 
    amount.value = '';
    spotSliderValue.value = 0;
    return; 
  }
  amount.value = value;
  
  // 反向计算百分比：根据输入的数量更新滑块值
  updateSpotSliderFromAmount();
};

// 根据输入的数量反向计算滑块百分比
const updateSpotSliderFromAmount = () => {
  try {
    const inputAmount = parseFloat(amount.value);
    if (isNaN(inputAmount) || inputAmount <= 0) {
      spotSliderValue.value = 0;
      return;
    }
    
    const balance = availableBalance.value;
    if (balance <= 0) {
      spotSliderValue.value = 0;
      return;
    }
    
    const orderPrice = parseFloat(price.value) || lastPrice.value;
    if (!orderPrice || orderPrice <= 0) {
      spotSliderValue.value = 0;
      return;
    }
    
    let percent = 0;
    
    if (orderSide.value === 'buy') {
      // 买入：根据数量计算总花费，再计算百分比
      // percent = (amount * price / balance) * 100
      const totalCost = inputAmount * orderPrice;
      percent = Math.min(100, Math.max(0, (totalCost / balance) * 100));
    } else {
      // 卖出：直接计算百分比
      // percent = (amount / balance) * 100
      percent = Math.min(100, Math.max(0, (inputAmount / balance) * 100));
    }
    
    // 直接使用计算出的百分比（允许任意精度）
    spotSliderValue.value = Math.round(percent);
  } catch (error) {
    console.error('Error updating slider from amount:', error);
  }
};

// 滑块变化事件处理
const onSpotSliderChange = (value) => {
  // 确保值在有效范围内
  const clampedValue = Math.max(0, Math.min(100, value));
  spotSliderValue.value = clampedValue;
  setAmountPercent(clampedValue);
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
    if (balance <= 0) { 
      spotSliderValue.value = 0;
      amount.value = '';
      return; 
    }
    
    const config = currentCoinConfig.value;
    const orderPrice = parseFloat(price.value) || lastPrice.value;
    
    if (!orderPrice || orderPrice <= 0) {
      spotSliderValue.value = 0;
      amount.value = '';
      return;
    }
    
    if (orderSide.value === 'buy') {
      // 买入操作：amount = (余额 * percent / 100) / price
      let scalingFactor = percent / 100;
      
      // 如果是 100%，预留缓冲空间防止计算精度溢出或滑点
      if (percent === 100) {
        // 限价单：预留 0.1% 缓冲空间
        // 市价单：预留 0.5% 缓冲空间（防止价格波动和滑点）
        scalingFactor = orderType.value === 'market' ? 0.995 : 0.999;
      }
      
      const totalCost = balance * scalingFactor;
      const calculatedAmount = totalCost / orderPrice;
      amount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(config.amountFixed) : '';
    } else {
      // 卖出操作：amount = 余额 * percent / 100
      let scalingFactor = percent / 100;
      
      // 如果是 100%，预留极小缓冲空间
      if (percent === 100) {
        scalingFactor = 0.999;
      }
      
      const calculatedAmount = balance * scalingFactor;
      amount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(config.amountFixed) : '';
    }
  } catch (error) { 
    console.error('Error setting amount percent:', error); 
    spotSliderValue.value = 0;
    amount.value = '';
  }
};

// ========== 费率常量 ==========
const SPOT_FEE_RATE = 0.001;   // 现货 0.1%
const FUTURES_FEE_RATE = 0.0004; // 合约 0.04% (与后端保持一致)

// ========== 现货交易计算属性 ==========

// 获取当前有效的价格（市价单使用当前价格，限价单使用用户输入价格）
const spotCurrentPrice = computed(() => {
  if (orderType.value === 'market') {
    return lastPrice.value; // 市价单使用最新价格
  }
  return parseFloat(price.value) || lastPrice.value; // 限价单使用用户输入，否则使用最新价格
});

// 现货预估手续费
const spotEstimatedFee = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  
  if (p <= 0 || a <= 0) return 0;
  
  if (orderSide.value === 'buy') {
    // 买入：手续费从获得的币种中扣除，显示币种单位
    return a * SPOT_FEE_RATE;
  } else {
    // 卖出：手续费从获得的 USDT 中扣除，显示 USDT 单位
    return (p * a) * SPOT_FEE_RATE;
  }
});

// 格式化现货预估手续费显示
const formatEstimatedFee = computed(() => {
  const fee = spotEstimatedFee.value;
  if (fee <= 0) return '0.00';
  
  if (orderSide.value === 'buy') {
    // 买入：显示币种单位
    const config = currentCoinConfig.value;
    return fee.toFixed(config.amountFixed);
  } else {
    // 卖出：显示 USDT 单位
    return formatAssetBalance(fee, 'USDT');
  }
});

// 买入时的手续费 USDT 等值（用于小字备注）
const formatEstimatedFeeUSDT = computed(() => {
  if (orderSide.value !== 'buy') return '';
  const fee = spotEstimatedFee.value;
  if (fee <= 0) return '';
  
  const p = spotCurrentPrice.value;
  const feeUSDT = fee * p; // BTC手续费 * BTC价格 = USDT等值
  return feeUSDT > 0 ? formatAssetBalance(feeUSDT, 'USDT') : '';
});

// 现货总额（名义价值）
const spotTotal = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  
  if (p <= 0 || a <= 0) return 0;
  
  // 总额 = 价格 * 数量（名义价值）
  return p * a;
});

// 格式化现货总额显示
const formatTotalAmount = computed(() => {
  const total = spotTotal.value;
  return total > 0 ? total.toFixed(2) : '0.00';
});

// 预估到账金额（用户实际能拿到的数量）
const formatEstimatedReceived = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  if (p <= 0 || a <= 0) return '0.00';
  
  if (orderSide.value === 'buy') {
    // 买入：实际得到的币种 = amount - fee
    const fee = spotEstimatedFee.value;
    const received = a - fee;
    const config = currentCoinConfig.value;
    return received > 0 ? received.toFixed(config.amountFixed) + ' ' + currentCoinConfig.value.baseCoin : '0.00 ' + currentCoinConfig.value.baseCoin;
  } else {
    // 卖出：实际得到的 USDT = total - fee（统一使用 formatAssetBalance 确保 2 位小数）
    const total = spotTotal.value;
    const fee = spotEstimatedFee.value;
    const received = total - fee;
    return received > 0 ? formatAssetBalance(received, 'USDT') + ' USDT' : '0.00 USDT';
  }
});

const formatAvailableBalance = computed(() => {
  if (orderSide.value === 'buy') {
    return formatAssetBalance(availableBalance.value, 'USDT') + ' USDT';
  } else {
    return formatAssetBalance(availableBalance.value, symbol.value) + ' ' + symbol.value;
  }
});

const formatSellableBalance = computed(() => {
  if (orderSide.value === 'buy') {
    return formatAssetBalance(availableBalance.value, symbol.value) + ' ' + symbol.value;
  } else {
    return formatAssetBalance(availableBalance.value, 'USDT') + ' USDT';
  }
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

// 合约滑块变化事件处理
const onFuturesSliderChange = (value) => {
  // 确保值在有效范围内
  const clampedValue = Math.max(0, Math.min(100, value));
  futuresSliderValue.value = clampedValue;
  setFuturesAmountPercent(clampedValue);
};

// 根据合约输入的数量反向计算滑块百分比
const updateFuturesSliderFromAmount = () => {
  try {
    const inputAmount = parseFloat(futuresAmount.value);
    if (isNaN(inputAmount) || inputAmount <= 0) {
      futuresSliderValue.value = 0;
      return;
    }
    
    const balance = assetStore?.usdtBalance || 0;
    if (balance <= 0) {
      futuresSliderValue.value = 0;
      return;
    }
    
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value || markPrice.value);
    if (!orderPrice || orderPrice <= 0) {
      futuresSliderValue.value = 0;
      return;
    }
    
    // 基于可用保证金和杠杆计算最大可开仓位
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    
    if (maxAmount <= 0) {
      futuresSliderValue.value = 0;
      return;
    }
    
    // percent = (inputAmount / maxAmount) * 100
    const percent = Math.min(100, Math.max(0, (inputAmount / maxAmount) * 100));
    
    // 直接使用计算出的百分比（允许任意精度）
    futuresSliderValue.value = Math.round(percent);
  } catch (error) {
    console.error('Error updating futures slider from amount:', error);
  }
};

// 合约数量输入处理
const handleFuturesAmountInput = (e) => {
  let value = e.target.value;
  if (value.includes('-')) value = value.replace(/-/g, '');
  const numValue = parseFloat(value);
  if (!isNaN(numValue) && numValue < 0) value = Math.abs(numValue).toString();
  if (value === '' || value === '-') { 
    futuresAmount.value = '';
    futuresSliderValue.value = 0;
    return; 
  }
  futuresAmount.value = value;
  
  // 反向计算百分比：根据输入的数量更新滑块值
  updateFuturesSliderFromAmount();
};

const setFuturesAmountPercent = (percent) => {
  selectedFuturesPercent.value = percent;
  try {
    const balance = assetStore?.usdtBalance || 0;
    if (balance <= 0) {
      futuresSliderValue.value = 0;
      futuresAmount.value = '';
      return;
    }
    
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value || markPrice.value);
    if (!orderPrice || orderPrice <= 0) {
      futuresSliderValue.value = 0;
      futuresAmount.value = '';
      return;
    }
    
    // 基于可用保证金和杠杆计算最大可开仓位
    // 最大可开数量 = (可用保证金 * 杠杆倍数) / 价格
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    
    // 如果是 100%，预留极小缓冲空间（防止计算精度问题）
    let scalingFactor = percent / 100;
    if (percent === 100) {
      scalingFactor = 0.999; // 预留 0.1% 缓冲
    }
    
    const calculatedAmount = maxAmount * scalingFactor;
    futuresAmount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(currentCoinConfig.value.amountFixed) : '';
  } catch (error) {
    console.error('Error setting futures amount percent:', error);
    futuresSliderValue.value = 0;
    futuresAmount.value = '';
  }
};

// ========== 合约交易计算属性 ==========

// 获取当前有效的价格（市价单使用标记价格，限价单使用用户输入价格）
const futuresCurrentPrice = computed(() => {
  if (orderType.value === 'market') {
    return markPrice.value; // 市价单使用标记价格
  }
  return parseFloat(futuresPrice.value) || markPrice.value; // 限价单使用用户输入，否则使用标记价格
});

// 合约名义价值
const futuresNotionalValue = computed(() => {
  const p = futuresCurrentPrice.value;
  const a = parseFloat(futuresAmount.value) || 0;
  
  if (p <= 0 || a <= 0) return 0;
  
  // 名义价值 = 价格 * 数量
  return p * a;
});

// 合约预估手续费
const futuresEstimatedFee = computed(() => {
  const notional = futuresNotionalValue.value;
  if (notional <= 0) return 0;
  
  // 手续费 = 名义价值 * 费率
  return notional * FUTURES_FEE_RATE;
});

// 格式化合约预估手续费显示
const formatFuturesEstimatedFee = computed(() => {
  const fee = futuresEstimatedFee.value;
  return fee > 0 ? fee.toFixed(4) : '0.00';
});

// 合约保证金（所需保证金）
const futuresMargin = computed(() => {
  const notional = futuresNotionalValue.value;
  const leverage = currentLeverage.value || 20;
  
  if (notional <= 0 || leverage <= 0) return 0;
  
  // 保证金 = 名义价值 / 杠杆倍数
  return notional / leverage;
});

// 合约总额（显示名义价值，也可以显示保证金）
const futuresTotal = computed(() => {
  // 这里显示名义价值，如果需要显示保证金，可以改为 futuresMargin.value
  return futuresNotionalValue.value;
});

// 格式化合约总额显示
const formatFuturesTotalAmount = computed(() => {
  const total = futuresTotal.value;
  return total > 0 ? total.toFixed(2) : '0.00';
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

const handleLong = async () => {
  if (!isFuturesFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }
  
  isLoading.value = true;
  
  try {
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value);
    
    const params = {
      symbol: `${symbol.value}/USDT`,
      side: 'BUY',
      type: orderType.value.toUpperCase(),
      price: orderPrice,
      amount: parseFloat(futuresAmount.value),
      leverage: currentLeverage.value
    };
    
    console.log('📤 发送合约开多请求:', params);
    
    const response = await createFuturesOrder(params);
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({
        message: responseData.message || t('trade.order_submitted'),
        icon: 'success',
        duration: 2000
      });
      
      // 刷新持仓列表和资产余额
      await fetchFuturesPositions();
      await assetStore.initData();
      
      // 清空输入框
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
      
      console.log('✅ 合约开多成功，持仓列表和资产余额已刷新');
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    console.error('❌ 合约开多失败:', error);
    
    let errorMessage = t('trade.order_failed') || '开仓失败，请重试';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showToast({
      message: errorMessage,
      icon: 'fail',
      duration: 3000
    });
  } finally {
    isLoading.value = false;
  }
};

const handleShort = async () => {
  if (!isFuturesFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }
  
  isLoading.value = true;
  
  try {
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value);
    
    const params = {
      symbol: `${symbol.value}/USDT`,
      side: 'SELL',
      type: orderType.value.toUpperCase(),
      price: orderPrice,
      amount: parseFloat(futuresAmount.value),
      leverage: currentLeverage.value
    };
    
    console.log('📤 发送合约开空请求:', params);
    
    const response = await createFuturesOrder(params);
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({
        message: responseData.message || t('trade.order_submitted'),
        icon: 'success',
        duration: 2000
      });
      
      // 刷新持仓列表和资产余额
      await fetchFuturesPositions();
      await assetStore.initData();
      
      // 清空输入框
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
      
      console.log('✅ 合约开空成功，持仓列表和资产余额已刷新');
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    console.error('❌ 合约开空失败:', error);
    
    let errorMessage = t('trade.order_failed') || '开仓失败，请重试';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showToast({
      message: errorMessage,
      icon: 'fail',
      duration: 3000
    });
  } finally {
    isLoading.value = false;
  }
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
    
    isLoading.value = true;
    
    try {
      const symbolPair = position.symbol.includes('/') ? position.symbol : `${position.symbol}/USDT`;
      
      const response = await closeFuturesPositionApi({
        symbol: symbolPair,
        amount: position.quantity
      });
      
      const responseData = response.data || response;
      
      if (responseData && responseData.code === 200) {
        showToast({
          message: responseData.message || t('trade.position_closed'),
          icon: 'success',
          duration: 2000
        });
        
        // 刷新持仓列表和资产余额
        await fetchFuturesPositions();
        await assetStore.initData();
        
        console.log('✅ 平仓成功，持仓列表和资产余额已刷新');
      } else {
        throw new Error(responseData?.message || t('trade.close_failed'));
      }
    } catch (error) {
      console.error('❌ 平仓失败:', error);
      
      let errorMessage = t('trade.close_failed') || '平仓失败，请重试';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showToast({
        message: errorMessage,
        icon: 'fail',
        duration: 3000
      });
    } finally {
      isLoading.value = false;
    }
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

// 获取当前委托订单列表
const fetchOpenOrders = async () => {
  try {
    const response = await getOrders({ status: 'NEW' });
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 映射后端数据格式到前端显示格式
      ordersList.value = responseData.data.map(order => ({
        order_id: order.order_id,
        side: order.side.toLowerCase(), // BUY -> buy, SELL -> sell
        type: order.type.toLowerCase(), // LIMIT -> limit, MARKET -> market
        price: order.price,
        quantity: order.quantity || order.amount, // 兼容 quantity 和 amount 字段
        symbol: order.symbol.split('/')[0], // "BTC/USDT" -> "BTC"
        timestamp: order.timestamp || order.create_time || Date.now(),
        status: order.status
      }));
      
      console.log('✅ 获取当前委托订单成功:', ordersList.value);
    } else {
      ordersList.value = [];
      console.warn('⚠️ 获取订单列表失败:', responseData);
    }
  } catch (error) {
    console.error('❌ 获取订单列表失败:', error);
    ordersList.value = [];
  }
};

// 获取合约持仓列表
const fetchFuturesPositions = async () => {
  try {
    // 检查钱包是否连接
    if (!assetStore.isWalletConnected) {
      positions.value = [];
      return;
    }
    
    const response = await getFuturesPositionsApi();
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 映射后端数据格式到前端显示格式
      positions.value = responseData.data.map(pos => ({
        symbol: pos.symbol?.split('/')[0] || pos.symbol, // "BTC/USDT" -> "BTC"
        side: pos.side?.toLowerCase() || 'long', // LONG -> long, SHORT -> short
        quantity: pos.size || pos.quantity || 0,
        entryPrice: pos.entry_price || 0,
        leverage: pos.leverage || 20,
        margin: pos.margin || 0,
        liquidationPrice: pos.liquidation_price || 0,
        unrealizedPnl: pos.unrealized_pnl || 0,
        unrealizedPnlPercent: 0, // 将在 updatePositionsPnl 中计算
        markPrice: pos.mark_price || markPrice.value
      }));
      
      // 更新盈亏
      updatePositionsPnl();
      
      console.log('✅ 获取合约持仓成功:', positions.value);
    } else {
      positions.value = [];
      console.warn('⚠️ 获取合约持仓失败:', responseData);
    }
  } catch (error) {
    console.error('❌ 获取合约持仓失败:', error);
    positions.value = [];
  }
};

const handleSubmitOrder = async () => {
  // 第一步：表单校验
  const amountValue = parseFloat(amount.value);
  if (isNaN(amountValue) || amountValue <= 0) {
    showToast({ message: t('trade.amount_invalid'), icon: 'fail' });
    return;
  }
  
  if (!isOrderValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }

  // 第二步：设置加载状态
  isLoading.value = true;

  try {
    // 第三步：构造发送给后端的参数对象
    const orderPrice = orderType.value === 'market' ? lastPrice.value : parseFloat(price.value);
    
    const params = {
      symbol: `${symbol.value}/USDT`, // 确保格式为 "BTC/USDT"
      side: orderSide.value.toUpperCase(), // 转换为大写：'BUY' 或 'SELL'
      type: orderType.value.toUpperCase(), // 转换为大写：'LIMIT' 或 'MARKET'
      price: orderType.value === 'market' ? orderPrice : parseFloat(price.value), // 市价单传当前市场价，限价单传用户输入的价格
      amount: parseFloat(amount.value),
      use_beat_discount: false // 暂时不使用 BEAT 折扣
    };

    console.log('📤 发送下单请求:', params);

    // 第四步：调用后端 API
    const response = await createOrder(params);
    
    console.log('✅ 下单成功:', response);

    // 第五步：成功处理
    // 注意：axios 返回的是 response 对象，后端数据在 response.data 中
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      // 显示成功提示
      showToast({
        message: orderType.value === 'market' 
          ? t('trade.market_order_submitted') 
          : t('trade.limit_order_submitted'),
        icon: 'success',
        duration: 2000
      });

      // 关键：刷新用户资产余额
      await assetStore.initData();
      
      // 关键：刷新当前委托订单列表
      await fetchOpenOrders();

      // 清空输入框
      if (orderType.value === 'limit') {
        price.value = '';
      }
      amount.value = '';
      selectedPercent.value = null;
      spotSliderValue.value = 0; // 重置滑块

      console.log('✅ 订单提交成功，资产余额和订单列表已刷新');
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    // 第六步：失败处理
    console.error('❌ 下单失败:', error);
    
    let errorMessage = t('trade.order_failed') || '订单提交失败，请重试';
    
    // 尝试从错误响应中提取错误信息
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }

    showToast({
      message: errorMessage,
      icon: 'fail',
      duration: 3000
    });
  } finally {
    // 第七步：重置加载状态
    isLoading.value = false;
  }
};

const cancelOrder = async (index) => {
  const order = ordersList.value[index];
  if (!order || !order.order_id) {
    showToast({ message: t('trade.order_not_found'), icon: 'fail' });
    return;
  }

  try {
    // 调用后端撤单接口
    const response = await cancelOrderApi(order.order_id);
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({ 
        message: t('trade.order_cancelled'), 
        icon: 'success',
        duration: 2000 
      });
      
      // 刷新订单列表和资产余额
      await fetchOpenOrders();
      await assetStore.initData();
      
      console.log('✅ 订单撤销成功，订单列表和资产余额已刷新');
    } else {
      throw new Error(responseData?.message || t('trade.cancel_failed'));
    }
  } catch (error) {
    console.error('❌ 撤销订单失败:', error);
    
    let errorMessage = t('trade.cancel_failed') || '撤销订单失败，请重试';
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showToast({
      message: errorMessage,
      icon: 'fail',
      duration: 3000
    });
  }
};

const goToKlineChart = () => { router.push({ path: '/market', query: { symbol: symbol.value } }); };

const switchCoin = (newSymbol) => {
  // 1. 更新 symbol
  symbol.value = newSymbol;
  
  // 2. 关闭币种选择弹窗
  showCoinSelect.value = false;
  
  // 3. 清空 amount 输入框
  amount.value = '';
  
  // 4. 重置百分比按钮状态和滑块值
  selectedPercent.value = null;
  spotSliderValue.value = 0;
  
  // 5. 更新价格为新币种的当前市价
  updatePriceForSymbol(newSymbol);
  
  // 6. 更新 URL 参数（使用 replace 避免产生历史记录）
  router.replace({ 
    path: '/trade', 
    query: { 
      symbol: newSymbol, 
      side: orderSide.value 
    } 
  });
  
  // 7. 显示切换成功提示
  showToast({ 
    message: t('trade.switched_to', { symbol: `${newSymbol}/USDT` }), 
    duration: 1500 
  });
};

// 初始化函数
const initializeTrade = async () => {
  generateOrderBook();
  // 首次进入也初始化价格
  updatePriceForSymbol(symbol.value);
  
  // 确保 WebSocket 连接（用于合约交易的标记价格）
  marketStore.ensureConnection();
  
  // 检查钱包连接状态
  if (assetStore.isWalletConnected) {
    // 获取当前委托订单列表（现货）
    await fetchOpenOrders();
    
    // 如果当前在合约 Tab，获取合约持仓
    if (activeTradeTab.value === 'futures') {
      await fetchFuturesPositions();
    }
  }
};

// 监听 Tab 切换，加载对应的数据
watch(activeTradeTab, async (newTab) => {
  if (assetStore.isWalletConnected) {
    if (newTab === 'futures') {
      // 切换到合约 Tab，获取持仓列表
      await fetchFuturesPositions();
    } else if (newTab === 'spot') {
      // 切换到现货 Tab，获取订单列表
      await fetchOpenOrders();
    }
  }
});

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

/* 滑块容器样式 */
.slider-wrapper {
  padding: 10px 10px; /* 上下左右留出空间，防止滑块被切断 */
  margin-bottom: 12px;
}

.slider-container {
  padding: 10px 10px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

/* 刻度标签栏 */
.slider-marks {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 4px 0;
  margin-top: 4px;
}

.mark-item {
  font-size: 10px;
  color: #848E9C;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.2s ease;
  user-select: none;
  min-width: 32px;
  text-align: center;
}

.mark-item:hover {
  color: #FCD535;
  background-color: rgba(252, 213, 53, 0.1);
}

.mark-item:active {
  transform: scale(0.95);
}

/* 自定义滑块按钮样式 */
.custom-slider-button {
  width: 24px;
  color: #000;
  font-size: 10px;
  line-height: 16px;
  text-align: center;
  background-color: #FCD535;
  border-radius: 100px;
  font-weight: bold;
}

/* 保留旧样式以兼容（如果其他地方还在使用） */
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
.fee-usdt-note { font-size: 11px; color: #8E8E93; font-weight: 400; margin-left: 4px; }
.discount-badge { font-size: 11px; color: #FCD535; font-weight: 500; }

.total-row {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
  background-color: #1C1C1E; border-radius: 4px; height: 36px; margin-bottom: 8px;
}
.total-label { font-size: 12px; color: #848E9C; }
.total-value { font-size: 13px; color: #EAECEF; font-weight: 600; font-variant-numeric: tabular-nums; }

.estimated-received-row {
  display: flex; justify-content: space-between; align-items: center; padding: 10px 12px;
  background-color: rgba(252, 213, 53, 0.08); border-radius: 4px; height: 40px; margin-bottom: 16px;
  border: 1px solid rgba(252, 213, 53, 0.2);
}
.received-label { font-size: 13px; color: #D4AF37; font-weight: 600; }
.received-value { font-size: 15px; color: #FCD535; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -0.3px; }

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