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
      <div ref="orderBookContainerRef" class="orderbook-side">
        <!-- 表头 -->
        <div class="orderbook-header">
          <span class="header-price">{{ $t('trade.price') }} (USDT)</span>
          <span class="header-quantity">{{ $t('trade.amount') }} (BTC)</span>
        </div>

        <!-- 卖单列表 (Asks) - 倒序 -->
        <div class="asks-list" v-if="displayedAsks && displayedAsks.length > 0">
          <div 
            v-for="(ask, index) in displayedAsks" 
            :key="`ask-${index}`"
            class="order-row ask-row"
            :style="{ '--depth-width': getDepthWidth(ask?.quantity || 0, displayedAsks, 'asks') + '%' }"
            @click="selectPrice(ask?.price || 0)"
          >
            <div class="depth-bar ask-depth"></div>
            <span class="price ask-price">{{ formatPrice(ask?.price) }}</span>
            <span class="quantity">{{ formatQuantity(ask?.quantity) }}</span>
          </div>
        </div>
        <div v-else class="empty-orderbook">暂无卖单</div>

        <!-- 最新成交价 (Middle) -->
        <div class="last-price" :class="{ up: priceChange >= 0, down: priceChange < 0 }">
          <div class="price-main">{{ formatPrice(markPrice) }}</div>
          <div class="price-fiat">${{ formatPrice(markPrice) }}</div>
        </div>

        <!-- 买单列表 (Bids) - 正序 -->
        <div class="bids-list" v-if="displayedBids && displayedBids.length > 0">
          <div 
            v-for="(bid, index) in displayedBids" 
            :key="`bid-${index}`"
            class="order-row bid-row"
            :style="{ '--depth-width': getDepthWidth(bid?.quantity || 0, displayedBids, 'bids') + '%' }"
            @click="selectPrice(bid?.price || 0)"
          >
            <div class="depth-bar bid-depth"></div>
            <span class="price bid-price">{{ formatPrice(bid?.price) }}</span>
            <span class="quantity">{{ formatQuantity(bid?.quantity) }}</span>
          </div>
        </div>
        <div v-else class="empty-orderbook">暂无买单</div>
      </div>

      <!-- 右侧：交易表单 (58%) -->
      <div ref="orderFormRef" class="form-side">
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

                <!-- 右侧：开仓均价、强平价格、保证金、仓位数量 -->
                <div class="position-right">
                  <div class="position-info-row">
                    <span class="info-label">{{ $t('trade.entry_price') }}:</span>
                    <span class="info-value">{{ formatPrice(position.entryPrice) }}</span>
                  </div>
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
            <div v-if="!ordersList || ordersList.length === 0" class="empty-state">
              {{ $t('trade.no_orders') }}
            </div>
            <div v-else>
              <div 
                v-for="(order, index) in (ordersList || [])"
                :key="order?.order_id || index"
                class="order-item"
              >
                <div class="order-left">
                  <div class="order-side-badge" :class="order?.side?.toLowerCase() || ''">
                    {{ order?.side === 'BUY' ? t('trade.buy') : t('trade.sell') }}
                  </div>
                  <div class="order-symbol-time">
                    <span class="order-symbol">{{ order?.symbol || '' }}</span>
                    <span class="order-time">{{ formatOrderTime(order?.timestamp) }}</span>
                  </div>
                </div>
                
                <div class="order-center">
                  <div class="order-price">{{ formatPrice(order?.price) }}</div>
                  <div class="order-quantity">{{ formatQuantity(order?.quantity || order?.amount || 0) }} / {{ formatQuantity(order?.quantity || order?.amount || 0) }}</div>
                </div>
                
                <div class="order-right">
                  <button class="cancel-btn" @click="cancelFuturesOrder(order?.order_id)">{{ t('trade.cancel') }}</button>
                </div>
              </div>
            </div>
          </div>
        </van-tab>
       <!-- 历史记录标签：添加渲染逻辑 -->
      <van-tab :title="$t('trade.trade_history_tab')">
        <div class="history-list">
          <div v-if="!historyList || historyList.length === 0" class="empty-state">
            {{ $t('trade.no_orders') }}
          </div>
          <div v-else>
            <div 
              v-for="(order, index) in (historyList || [])"
              :key="order?.order_id || index"
              class="order-item"
              :class="{ 'filled': order?.status === 'FILLED', 'cancelled': order?.status === 'CANCELLED' }"
            >
              <div class="order-left">
                <div class="order-side-badge" :class="order?.side?.toLowerCase() || ''">
                  {{ order?.side === 'BUY' ? t('trade.buy') : t('trade.sell') }}
                </div>
                <div class="order-symbol-time">
                  <span class="order-symbol">{{ order?.symbol || '' }}</span>
                  <span class="order-time">{{ formatOrderTime(order?.timestamp) }}</span>
                </div>
                <!-- 新增：显示状态 -->
                <span class="order-status">{{ order?.status === 'FILLED' ? '已成交' : '已取消' }}</span>
              </div>
              
              <div class="order-center">
                <div class="order-price">{{ formatPrice(order?.price) }}</div>
                <div class="order-quantity">{{ formatQuantity(order?.quantity || order?.amount || 0) }} / {{ formatQuantity(order?.quantity || order?.amount || 0) }}</div>
                <!-- 新增：如果有 realized_pnl，显示 -->
                <div v-if="order?.realized_pnl" class="order-pnl" :class="{ positive: order?.realized_pnl >= 0, negative: order?.realized_pnl < 0 }">
                  PNL: {{ order?.realized_pnl >= 0 ? '+' : '-' }}{{ Math.abs(order?.realized_pnl || 0).toFixed(2) }} USDT
                </div>
              </div>
              
              <!-- 历史记录无撤单按钮 -->
              <div class="order-right">
                <!-- 可选：添加查看详情按钮 -->
                <!-- <button class="detail-btn" @click="viewOrderDetail(order.order_id)">{{ t('trade.detail') }}</button> -->
              </div>
            </div>
          </div>
        </div>
      </van-tab>
    </van-tabs>
  </div>

    <!-- 止盈止损弹窗 -->
    <van-popup
      v-model:show="showTPSLPopup"
      position="bottom"
      round
      class="premium-tpsl-popup"
      :overlay-style="{ backgroundColor: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(10px)' }"
      :style="{ height: 'auto', background: '#0a0a0a' }"
    >
      <div class="premium-modal-container">
        <!-- 头部装饰线 -->
        <div class="modal-drag-indicator"></div>
        
        <div class="premium-modal-header">
          <div class="header-title-wrap">
            <span class="gold-dot"></span>
            <h3>{{ $t('trade.take_profit_stop_loss') }}</h3>
          </div>
          <van-icon name="cross" @click="showTPSLPopup = false" class="premium-close-btn" />
        </div>

        <div class="premium-tpsl-form">
          <!-- 止盈价格输入 -->
          <div class="premium-form-group">
            <div class="group-label-row">
              <label>{{ $t('trade.take_profit_price') }}</label>
              <span class="mark-price-ref">Mark: {{ markPrice.toFixed(2) }}</span>
            </div>
            
            <div class="premium-input-box">
              <button class="step-btn" @click="adjustTPSLPrice('takeProfitPrice', -10)">-</button>
              <div class="input-inner-wrap">
                <input 
                  v-model="tpSlForm.takeProfitPrice" 
                  type="number" 
                  placeholder="0.00"
                  class="mono-font"
                />
                <span class="input-suffix">USDT</span>
              </div>
              <button class="step-btn" @click="adjustTPSLPrice('takeProfitPrice', 10)">+</button>
            </div>

            <div class="quick-select-row">
              <div v-for="p in [0.05, 0.1, 0.25]" :key="p" 
                   class="percent-tag" @click="setTPSLPercentage('takeProfitPrice', p)">
                +{{ p * 100 }}%
              </div>
            </div>
          </div>

          <!-- 止损价格输入 -->
          <div class="premium-form-group">
            <div class="group-label-row">
              <label>{{ $t('trade.stop_loss_price') }}</label>
            </div>
            
            <div class="premium-input-box">
              <button class="step-btn" @click="adjustTPSLPrice('stopLossPrice', -10)">-</button>
              <div class="input-inner-wrap">
                <input 
                  v-model="tpSlForm.stopLossPrice" 
                  type="number" 
                  placeholder="0.00"
                  class="mono-font"
                />
                <span class="input-suffix">USDT</span>
              </div>
              <button class="step-btn" @click="adjustTPSLPrice('stopLossPrice', 10)">+</button>
            </div>

            <div class="quick-select-row">
              <div v-for="p in [0.02, 0.05, 0.1]" :key="p" 
                   class="percent-tag sl" @click="setTPSLPercentage('stopLossPrice', p)">
                -{{ p * 100 }}%
              </div>
            </div>
          </div>

          <!-- 核心执行按钮 -->
          <button class="premium-gold-button" @click="confirmTPSL">
            {{ $t('trade.confirm') }}
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
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, showConfirmDialog, Tabs, Tab, Popup, ActionSheet } from 'vant';
import { useMarketStore } from '@/stores/market';
import { useAssetStore } from '@/stores/assets';
import { createFuturesOrder, getFuturesOrders, cancelFuturesOrder as cancelFuturesOrderAPI, getPositions, closePosition } from '@/api/futures';

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
// 彻底初始化所有列表数据，防止 undefined 错误
const positions = ref([]);
const ordersList = ref([]);
const historyList = ref([]);

const orderBookContainerRef = ref(null);
const orderFormRef = ref(null);
const maxVisibleRows = ref(20);

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

// 盘口数据管理（彻底初始化，确保不为 undefined）
const orderBook = ref({
  list: [],
  bids: [],
  asks: []
});
const asks = ref([]);
const bids = ref([]);
const currentPrice = ref(null);

// 从 Binance API 加载真实盘口数据
const loadOrderBook = async () => {
  try {
    // 标准化交易对名称（BTC -> BTCUSDT）
    const binanceSymbol = symbol.value.toUpperCase() + 'USDT';
    
    let url = `https://api.binance.com/api/v3/depth?symbol=${binanceSymbol}&limit=50`;
    let response;
    
    try {
      response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      // 如果跨域失败，使用无 CORS 限制的 API
      console.warn('[OrderBook] 主 API 失败，尝试备用 API:', error);
      url = `https://data-api.binance.vision/api/v3/depth?symbol=${binanceSymbol}&limit=50`;
      response = await fetch(url);
    }
    
    const data = await response.json();
    
    if (data && data.bids && data.asks) {
      // Binance API 返回格式: { bids: [["price", "quantity"], ...], asks: [["price", "quantity"], ...] }
      // 转换为我们的格式: [{ price: number, quantity: number }, ...]
      const formattedBids = (data.bids || []).map(item => ({
        price: parseFloat(item[0]),
        quantity: parseFloat(item[1])
      })).sort((a, b) => b.price - a.price);
      
      const formattedAsks = (data.asks || []).map(item => ({
        price: parseFloat(item[0]),
        quantity: parseFloat(item[1])
      })).sort((a, b) => a.price - b.price);
      
      // 更新 orderBook（填充 list 防 undefined）
      orderBook.value.bids = formattedBids;
      orderBook.value.asks = formattedAsks;
      orderBook.value.list = [...formattedBids, ...formattedAsks]; // 填充 list
      
      // 更新 asks 和 bids
      asks.value = formattedAsks;
      bids.value = formattedBids;
      
      // 更新当前价格（使用最佳买价和卖价的中间价）
      if (formattedBids.length > 0 && formattedAsks.length > 0) {
        const bestBid = formattedBids[0].price;
        const bestAsk = formattedAsks[0].price;
        currentPrice.value = (bestBid + bestAsk) / 2;
        if (!markPrice.value || markPrice.value === 92255.50) {
          markPrice.value = currentPrice.value;
        }
      }
      
      console.log('Order book loaded with real data', {
        bids: formattedBids.length,
        asks: formattedAsks.length,
        currentPrice: currentPrice.value,
        listLength: orderBook.value.list.length
      });
    }
  } catch (e) {
    console.error('Binance depth API 错误:', e);
    // 如果 API 失败，使用模拟数据作为后备
    generateOrderBook();
  }
};

// 生成更多模拟盘口数据（作为后备）
const generateOrderBook = () => {
  const basePrice = markPrice.value || 92255.50;
  const totalRows = 100;
  
  const newAsks = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (totalRows - i) * 0.01 + Math.random() * 0.1;
    newAsks.push({
      price: basePrice + priceOffset,
      quantity: Math.random() * 5 + 0.00001
    });
  }
  asks.value = newAsks.sort((a, b) => a.price - b.price);
  
  const newBids = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (i + 1) * 0.01 + Math.random() * 0.1;
    newBids.push({
      price: basePrice - priceOffset,
      quantity: Math.random() * 5 + 0.00001
    });
  }
  bids.value = newBids.sort((a, b) => b.price - a.price);
  
  // 更新 orderBook
  orderBook.value.bids = bids.value;
  orderBook.value.asks = asks.value;
  orderBook.value.list = [...bids.value, ...asks.value];
};

// 计算可显示的最大行数
const calculateMaxRows = () => {
  if (!orderFormRef.value) return 20;
  
  const rightSideHeight = orderFormRef.value.clientHeight;
  const headerHeight = 24;
  const lastPriceHeight = 32;
  const rowHeight = 20;
  
  const availableHeight = rightSideHeight - headerHeight - lastPriceHeight;
  const rowsPerSide = Math.floor(availableHeight / 2 / rowHeight);
  
  return Math.max(10, Math.min(100, rowsPerSide));
};

// 动态计算显示的买卖单数量（添加空值保护）
const displayedAsks = computed(() => {
  if (!asks.value || !Array.isArray(asks.value) || asks.value.length === 0) {
    return [];
  }
  return asks.value.slice(0, maxVisibleRows.value).reverse();
});

const displayedBids = computed(() => {
  if (!bids.value || !Array.isArray(bids.value) || bids.value.length === 0) {
    return [];
  }
  return bids.value.slice(0, maxVisibleRows.value);
});

// 使用 ResizeObserver 监听右侧高度
let resizeObserver = null;
const initOrderBookResizeObserver = () => {
  nextTick(() => {
    if (orderFormRef.value) {
      maxVisibleRows.value = calculateMaxRows();
      if (resizeObserver) resizeObserver.disconnect();
      resizeObserver = new ResizeObserver(() => {
        maxVisibleRows.value = calculateMaxRows();
      });
      resizeObserver.observe(orderFormRef.value);
    }
  });
};

// 从 marketStore 获取标记价格
watch(() => marketStore.getTicker(symbol.value), (ticker) => {
  if (ticker) {
    markPrice.value = ticker.price || markPrice.value;
    priceChange.value = ticker.change || priceChange.value;
  }
}, { immediate: true });

// 监听币种对应的真实深度数据变化
watch(() => marketStore.depths[symbol.value], (newDepth) => {
  if (newDepth && newDepth.asks && newDepth.bids) {
    asks.value = [...newDepth.asks];
    bids.value = [...newDepth.bids];
  }
}, { immediate: true, deep: true });

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
  if (!list || list.length === 0 || !quantity || quantity <= 0) return 0;
  const maxQuantity = Math.max(...list.map(item => item?.quantity || 0));
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
const selectCoin = async (coinSymbol) => {
  symbol.value = coinSymbol;
  showCoinSelect.value = false;
  
  // 加载新币种的真实盘口数据
  await loadOrderBook();
  
  // 如果加载失败，尝试从 marketStore 获取
  const realDepth = marketStore.depths[coinSymbol];
  if ((!orderBook.value.bids || orderBook.value.bids.length === 0) && realDepth && realDepth.asks && realDepth.bids) {
    asks.value = [...realDepth.asks];
    bids.value = [...realDepth.bids];
    orderBook.value.bids = bids.value;
    orderBook.value.asks = asks.value;
    orderBook.value.list = [...bids.value, ...asks.value];
  } else if (!orderBook.value.bids || orderBook.value.bids.length === 0) {
    // 如果都没有，使用模拟数据
    generateOrderBook();
  }

  // 重置表单
  price.value = '';
  amount.value = '';
  selectedPercent.value = null;
};

// 获取当前委托：添加 try-catch 错误处理
const fetchFuturesOrders = async () => {
  try {
    console.log('📤 [DEBUG] 开始获取当前委托订单...');
    const response = await getFuturesOrders({ status: 'NEW' });
    const responseData = response.data || response;
    
    console.log('📥 [DEBUG] API返回的订单数据:', responseData);
    
    if (responseData && responseData.code === 200) {
      if (responseData.data && Array.isArray(responseData.data) && responseData.data.length > 0) {
        // 过滤：只显示状态为 NEW 或 PENDING 的订单
        const pendingOrders = responseData.data.filter(order => 
          order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
        );
        
        ordersList.value = pendingOrders.map(order => ({
          order_id: order.order_id,
          side: order.side, // BUY 或 SELL
          type: order.type ? order.type.toLowerCase() : 'limit', // LIMIT -> limit, MARKET -> market
          price: order.price,
          quantity: order.quantity || order.amount, // 兼容 quantity 和 amount 字段
          amount: order.amount || order.quantity,
          symbol: order.symbol ? order.symbol.split('/')[0] : '', // "BTC/USDT" -> "BTC"
          leverage: order.leverage || 20,
          margin: order.margin || 0,
          status: order.status,
          timestamp: order.timestamp || order.create_time || Date.now()
        }));
        console.log('✅ [DEBUG] 当前委托订单（已过滤）:', ordersList.value);
        console.log(`✅ [DEBUG] 当前委托数量: ${ordersList.value.length}`);
      } else {
        ordersList.value = [];
        console.log('⚠️ [DEBUG] 当前委托列表为空');
      }
    } else {
      ordersList.value = [];
      console.error('❌ [DEBUG] 获取当前委托失败，响应码:', responseData?.code);
      showToast({ message: '获取当前委托失败' });
    }
  } catch (error) {
    console.error('❌ [DEBUG] 获取当前委托失败:', error);
    ordersList.value = [];
    showToast({ message: '网络错误，请重试' });
  }
};

// 新增：获取历史订单
const fetchHistoryOrders = async () => {
  try {
    console.log('📤 [DEBUG] 开始获取历史订单...');
    const response = await getFuturesOrders({ status: 'HISTORY' });
    const responseData = response.data || response;
    
    console.log('📥 [DEBUG] API返回的历史订单数据:', responseData);
    
    if (responseData && responseData.code === 200) {
      if (responseData.data && Array.isArray(responseData.data) && responseData.data.length > 0) {
        // 过滤：只显示状态为 FILLED 或 CANCELLED 的订单
        const historyOrders = responseData.data.filter(order => 
          order.status === 'FILLED' || order.status === 'CANCELLED'
        );
        
        historyList.value = historyOrders.map(order => ({
          order_id: order.order_id,
          side: order.side,
          type: order.type ? order.type.toLowerCase() : 'limit',
          price: order.price,
          quantity: order.quantity || order.amount,
          amount: order.amount || order.quantity,
          symbol: order.symbol ? order.symbol.split('/')[0] : '', // "BTC/USDT" -> "BTC"
          leverage: order.leverage || 20,
          margin: order.margin || 0,
          status: order.status,
          timestamp: order.timestamp || order.create_time || Date.now(),
          realized_pnl: order.realized_pnl || 0,  // 新增：从后端获取 PNL
          fee: order.fee || 0
        }));
        console.log('✅ [DEBUG] 历史订单（已过滤）:', historyList.value);
        console.log(`✅ [DEBUG] 历史订单数量: ${historyList.value.length}`);
      } else {
        historyList.value = [];
        console.log('⚠️ [DEBUG] 历史订单列表为空');
      }
    } else {
      historyList.value = [];
      console.error('❌ [DEBUG] 获取历史订单失败，响应码:', responseData?.code);
      showToast({ message: '获取历史记录失败' });
    }
  } catch (error) {
    console.error('❌ [DEBUG] 获取历史记录失败:', error);
    historyList.value = [];
    showToast({ message: '网络错误，请重试' });
  }
};

// 新增：监听标签切换，加载历史
watch(activePositionTab, (newTab) => {
  if (newTab === 0) {  // 持仓标签
    fetchPositions();  // 刷新持仓
  } else if (newTab === 1) {  // 当前委托标签
    fetchFuturesOrders();  // 刷新当前委托
  } else if (newTab === 2) {  // 历史记录标签
    fetchHistoryOrders();
  }
});

// 格式化订单时间
const formatOrderTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000 || timestamp);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  
  if (minutes < 1) return t('trade.just_now');
  if (minutes < 60) return `${minutes}${t('trade.minutes_ago')}`;
  if (hours < 24) return `${hours}${t('trade.hours_ago')}`;
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};

// 取消合约订单
const cancelFuturesOrder = async (orderId) => {
  try {
    await showConfirmDialog({
      title: t('trade.cancel_order_confirm'),
      message: t('trade.cancel_order_message'),
      confirmButtonText: t('trade.confirm'),
      cancelButtonText: t('trade.cancel'),
      confirmButtonColor: '#F6465D'
    });
    
    const response = await cancelFuturesOrderAPI(orderId);
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({
        message: t('trade.order_cancelled'),
        icon: 'success',
        duration: 2000
      });
      
      // 刷新订单列表
      await fetchFuturesOrders();
      await fetchHistoryOrders();

      // 刷新资产余额
      if (assetStore) {
        await assetStore.fetchAssets();
      }
    } else {
      showToast({
        message: responseData?.message || t('trade.cancel_order_failed'),
        duration: 2000
      });
    }
  } catch (error) {
    if (error !== 'cancel') { // 用户取消操作不算错误
      console.error('❌ 取消订单失败:', error);
      showToast({
        message: error.response?.data?.detail || t('trade.cancel_order_failed'),
        duration: 2000
      });
    }
  }
};

// 获取持仓列表
const fetchPositions = async () => {
  try {
    const response = await getPositions();
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200 && responseData.data) {
      positions.value = responseData.data.map(pos => ({
        symbol: pos.symbol.split('/')[0], // "BTC/USDT" -> "BTC"
        side: pos.side.toLowerCase(), // LONG -> long, SHORT -> short
        quantity: pos.size,
        entryPrice: pos.entry_price,
        leverage: pos.leverage,
        margin: pos.margin,
        liquidationPrice: pos.liquidation_price,
        unrealizedPnl: pos.unrealized_pnl || 0,
        unrealizedPnlPercent: 0 // 将在 updatePositionsPnl 中计算
      }));
      
      updatePositionsPnl();
      console.log('✅ 获取持仓列表成功:', positions.value);
    } else {
      positions.value = [];
    }
  } catch (error) {
    console.error('❌ 获取持仓列表失败:', error);
    positions.value = [];
  }
};

// 开多
const handleLong = async () => {
  if (!isFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }

  const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(price.value);
  
  try {
    const response = await createFuturesOrder({
      symbol: `${symbol.value}/USDT`,
      side: 'BUY',
      type: orderType.value.toUpperCase(),
      price: orderPrice,
      amount: parseFloat(amount.value),
      leverage: currentLeverage.value
    });
    
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      const message = responseData.message || (orderType.value === 'market' 
        ? t('trade.market_order_submitted') 
        : t('trade.limit_order_submitted'));
      
      showToast({
        message: message,
        icon: 'success',
        duration: 2000
      });
      
      // 如果立即成交，刷新持仓列表
      if (responseData.data && responseData.data.position) {
        await fetchPositions();
      }
      
      // 刷新订单列表（包括挂单）
      await fetchFuturesOrders();
      await fetchHistoryOrders();
      // 刷新资产余额
      if (assetStore) {
        await assetStore.fetchAssets();
      }
      
      // 重置表单
      amount.value = '';
      price.value = '';
      selectedPercent.value = null;
    } else {
      showToast({
        message: responseData?.message || t('trade.order_submit_failed'),
        duration: 2000
      });
    }
  } catch (error) {
    console.error('❌ 下单失败:', error);
    showToast({
      message: error.response?.data?.detail || t('trade.order_submit_failed'),
      duration: 2000
    });
  }
};

// 开空
const handleShort = async () => {
  if (!isFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }

  const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(price.value);
  
  try {
    const response = await createFuturesOrder({
      symbol: `${symbol.value}/USDT`,
      side: 'SELL',
      type: orderType.value.toUpperCase(),
      price: orderPrice,
      amount: parseFloat(amount.value),
      leverage: currentLeverage.value
    });
    
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      const message = responseData.message || (orderType.value === 'market' 
        ? t('trade.market_order_submitted') 
        : t('trade.limit_order_submitted'));
      
      showToast({
        message: message,
        icon: 'success',
        duration: 2000
      });
      
      // 如果立即成交，刷新持仓列表
      if (responseData.data && responseData.data.position) {
        await fetchPositions();
      }
      
      // 刷新订单列表（包括挂单和历史）
      await fetchFuturesOrders();
      await fetchHistoryOrders();
      
      // 刷新资产余额
      if (assetStore) {
        await assetStore.fetchAssets();
      }
      
      // 重置表单
      amount.value = '';
      price.value = '';
      selectedPercent.value = null;
    } else {
      showToast({
        message: responseData?.message || t('trade.order_submit_failed'),
        duration: 2000
      });
    }
  } catch (error) {
    console.error('❌ 下单失败:', error);
    showToast({
      message: error.response?.data?.detail || t('trade.order_submit_failed'),
      duration: 2000
    });
  }
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

// 监听标记价格变化，更新未实现盈亏和盘口
watch(markPrice, () => {
  updatePositionsPnl();
  
  // 仅在没有真实深度数据且当前还没有数据时，才生成模拟数据作为填充
  if (!asks.value.length || !bids.value.length) {
    generateOrderBook();
  }
}, { immediate: true });

// 监听币种变化，重新生成盘口
watch(symbol, () => {
  generateOrderBook();
});

// 止盈止损
const handleTakeProfitStopLoss = (position, index) => {
  currentTPSLPosition.value = { position, index };
  tpSlForm.value.takeProfitPrice = '';
  tpSlForm.value.stopLossPrice = '';
  showTPSLPopup.value = true;
};

const adjustTPSLPrice = (field, step) => {
  const currentVal = parseFloat(tpSlForm.value[field]) || markPrice.value;
  // 根据步长增减，保留2位小数
  tpSlForm.value[field] = (currentVal + step).toFixed(2);
};

const setTPSLPercentage = (field, percent) => {
  // 基于标记价格快速设置百分比偏移
  const basePrice = markPrice.value;
  if (field === 'takeProfitPrice') {
    tpSlForm.value[field] = (basePrice * (1 + percent)).toFixed(2);
  } else {
    tpSlForm.value[field] = (basePrice * (1 - percent)).toFixed(2);
  }
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
    
    console.log('📤 [DEBUG] 开始平仓，持仓信息:', position);
    
    // 调用后端平仓API
    const symbolPair = position.symbol.includes('/') ? position.symbol : `${position.symbol}/USDT`;
    const response = await closePosition({
      symbol: symbolPair,
      amount: position.quantity
    });
    
    const responseData = response.data || response;
    console.log('📥 [DEBUG] 平仓API返回数据:', responseData);
    
    if (responseData && responseData.code === 200) {
      showToast({
        message: responseData.message || t('trade.position_closed'),
        icon: 'success',
        duration: 2000
      });
      
      // 刷新持仓列表
      await fetchPositions();
      
      // 刷新订单列表（平仓会创建FILLED订单）
      await fetchFuturesOrders();
      await fetchHistoryOrders();
      
      // 刷新资产余额
      if (assetStore) {
        await assetStore.fetchAssets();
      }
      
      console.log('✅ [DEBUG] 平仓成功，已刷新持仓和订单列表');
    } else {
      throw new Error(responseData?.message || '平仓失败');
    }
  } catch (error) {
    if (error !== 'cancel') { // 用户取消操作不算错误
      console.error('❌ [DEBUG] 平仓失败:', error);
      showToast({
        message: error.response?.data?.detail || error.message || t('trade.close_failed'),
        duration: 2000
      });
    }
  }
};

// 跳转到K线图
const goToKlineChart = () => {
  showToast({ message: t('trade.chart_coming_soon'), duration: 2000 });
};

// 初始化
onMounted(async () => {
  // 确保 WebSocket 连接
  marketStore.ensureConnection();
  
  // 从路由参数获取币种
  if (route.query.symbol) {
    symbol.value = route.query.symbol;
  }
  
  // 使用 nextTick 确保 DOM 就绪后再加载盘口数据
  await nextTick();
  await loadOrderBook();
  
  // 如果加载失败，使用模拟数据
  if (!orderBook.value.bids || orderBook.value.bids.length === 0) {
    generateOrderBook();
  }
  
  initOrderBookResizeObserver();
  window.addEventListener('resize', () => {
    maxVisibleRows.value = calculateMaxRows();
  });
  
  // 加载持仓列表和订单列表
  await fetchPositions();
  await fetchFuturesOrders();
  await fetchHistoryOrders();
});

const viewOrderDetail = (orderId) => {
  showToast({ message: `查看订单 ${orderId} 详情 (开发中)` });
};

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect();
});
</script>

<style scoped>
.order-item.filled {
  border-color: rgba(14, 203, 129, 0.3);  /* 成交绿色边框 */
}
.order-item.cancelled {
  border-color: rgba(246, 70, 93, 0.3);  /* 取消红色边框 */
}
.order-status {
  font-size: 11px;
  color: #8E8E93;
  margin-top: 4px;
}
.order-pnl {
  font-size: 12px;
  margin-top: 4px;
}
.order-pnl.positive {
  color: #0ECB81;
}
.order-pnl.negative {
  color: #F6465D;
}


.futures-trade-page {
  min-height: 100vh;
  background-color: #000000;
  color: #FFFFFF;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  padding-bottom: 300px; /* 关键：防止内容被底部全局导航栏（60px）遮挡 - 增加足够的缓冲空间 */
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
  gap: 8px;
  min-height: 0;
  padding: 8px 8px 8px 0;
  align-items: flex-start;
}

/* 左侧盘口区 */
.orderbook-side {
  width: 42%;
  display: flex;
  flex-direction: column;
  background-color: #0E0E0E;
  border-radius: 4px;
  overflow: hidden;
  padding: 0;
  align-self: stretch; /* 强制对齐右侧高度 */
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 4px 8px;
  font-size: 11px;
  color: #848E9C;
  flex-shrink: 0;
}

.header-price, .header-quantity {
  flex: 1;
}

.asks-list, .bids-list {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
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
  opacity: 0.2;
}

.bid-depth {
  background-color: #0ECB81;
  opacity: 0.2;
}

.price, .quantity {
  position: relative;
  z-index: 1;
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.ask-price {
  color: #F6465D;
  font-weight: 600;
  text-shadow: 0 0 6px rgba(246, 70, 93, 0.4);
}

.bid-price {
  color: #0ECB81;
  font-weight: 600;
  text-shadow: 0 0 6px rgba(14, 203, 129, 0.4);
}

.quantity {
  color: #8E8E93;
  font-weight: 500;
}

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
  padding: 0;
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
  position: relative; /* 改为相对定位，不再固定 */
  margin-top: 8px; /* 与交易表单的间距 */
  margin-bottom: 100px; /* 与底部全局导航栏的间距，防止重叠 */
  display: flex;
  flex-direction: column;
  /* 移除固定高度，使用自然流式布局 */
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

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.order-item:hover {
  background-color: #252525;
  border-color: rgba(255, 255, 255, 0.12);
}

.order-item:active {
  opacity: 0.8;
}

.order-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.order-side-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  width: fit-content;
}

.order-side-badge.buy {
  background-color: rgba(14, 203, 129, 0.2);
  color: #0ECB81;
}

.order-side-badge.sell {
  background-color: rgba(246, 70, 93, 0.2);
  color: #F6465D;
}

.order-symbol-time {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-symbol {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
}

.order-time {
  font-size: 11px;
  color: #8E8E93;
}

.order-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  margin: 0 12px;
}

.order-price {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

.order-quantity {
  font-size: 12px;
  color: #8E8E93;
  font-variant-numeric: tabular-nums;
}

.order-right {
  flex: 0 0 auto;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: rgba(246, 70, 93, 0.15);
  border: 1px solid rgba(246, 70, 93, 0.3);
  border-radius: 6px;
  color: #F6465D;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: rgba(246, 70, 93, 0.25);
  border-color: rgba(246, 70, 93, 0.5);
}

.cancel-btn:active {
  opacity: 0.7;
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
  font-size: 28px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  margin-bottom: 4px;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.unrealized-pnl-value.positive {
  color: #0ECB81;
  text-shadow: 0 0 12px rgba(14, 203, 129, 0.5);
}

.unrealized-pnl-value.negative {
  color: #F6465D;
  text-shadow: 0 0 12px rgba(246, 70, 93, 0.5);
}

.unrealized-pnl-percent {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.unrealized-pnl-percent.positive {
  color: #0ECB81;
  text-shadow: 0 0 8px rgba(14, 203, 129, 0.4);
}

.unrealized-pnl-percent.negative {
  color: #F6465D;
  text-shadow: 0 0 8px rgba(246, 70, 93, 0.4);
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
  font-weight: 500;
}

.info-value {
  color: #FFFFFF;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-align: right;
  font-size: 14px;
}

.liquidation-price {
  color: #F6465D;
  font-weight: 700;
  font-size: 14px;
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

/* ========== 彻底重构的黑金样式 ========== */

/* 1. 弹窗基础容器 */
:deep(.van-popup.premium-tpsl-popup) {
  background: #0a0a0a !important; /* 纯深色底 */
  border-top: 1px solid rgba(212, 175, 55, 0.2);
  padding-bottom: env(safe-area-inset-bottom);
}

.premium-modal-container {
  padding: 12px 24px 32px;
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.03) 0%, rgba(0, 0, 0, 0) 100%);
}

.modal-drag-indicator {
  width: 36px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin: 0 auto 20px;
}

/* 2. 头部标题 */
.premium-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.header-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gold-dot {
  width: 6px;
  height: 6px;
  background: #D4AF37;
  border-radius: 50%;
  box-shadow: 0 0 8px #D4AF37;
}

.premium-modal-header h3 {
  color: #FFFFFF;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.5px;
  margin: 0;
}

.premium-close-btn {
  font-size: 22px;
  color: #4a4a4a;
  transition: color 0.3s;
}

.premium-close-btn:active { color: #D4AF37; }

/* 3. 输入组样式 */
.premium-form-group {
  margin-bottom: 24px;
}

.group-label-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.group-label-row label {
  color: #8E8E93;
  font-size: 13px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mark-price-ref {
  color: #4a4a4a;
  font-size: 12px;
  font-family: 'DIN Alternate', sans-serif;
}

/* 4. 核心输入框盒模型 */
.premium-input-box {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.03); /* 玻璃拟态底色 */
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 4px;
  transition: all 0.3s ease;
}

.premium-input-box:focus-within {
  border-color: #D4AF37;
  background: rgba(212, 175, 55, 0.05);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.1);
}

.step-btn {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 8px;
  color: #D4AF37;
  font-size: 24px;
  font-weight: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.step-btn:active {
  background: rgba(212, 175, 55, 0.2);
  transform: scale(0.95);
}

.input-inner-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.premium-input-box input {
  width: 100%;
  background: transparent;
  border: none;
  color: #FFFFFF;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
  padding: 0 40px;
  outline: none;
}

/* 移除数字输入框箭头 */
.premium-input-box input::-webkit-outer-spin-button,
.premium-input-box input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.mono-font {
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.input-suffix {
  position: absolute;
  right: 12px;
  color: #4a4a4a;
  font-size: 11px;
  font-weight: 700;
}

/* 5. 快捷选择标签 */
.quick-select-row {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.percent-tag {
  padding: 6px 12px;
  background: rgba(50, 215, 75, 0.1);
  color: #32D74B;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.percent-tag.sl {
  background: rgba(255, 69, 58, 0.1);
  color: #FF453A;
}

.percent-tag:active { opacity: 0.7; }

/* 6. 黄金渐变按钮 */
.premium-gold-button {
  width: 100%;
  margin-top: 12px;
  padding: 18px;
  background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%);
  border: none;
  border-radius: 14px;
  color: #000000;
  font-size: 16px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.premium-gold-button:active {
  transform: scale(0.97);
  box-shadow: 0 5px 10px rgba(212, 175, 55, 0.1);
  filter: brightness(0.9);
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
