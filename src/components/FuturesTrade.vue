<template>
  <div class="futures-trade-page">
    <!-- 顶部导航栏 -->
    <div class="trade-header">
      <div class="header-left" @click="$router.back()">
        <div class="header-action-left">
          <svg viewBox="0 0 1024 1024" class="custom-back-svg">
            <path d="M685.248 103.808L289.088 500l396.16 396.192 56.576-56.576L345.664 500l339.584-339.616z" fill="var(--color-brand-legacy)"></path>
          </svg>
        </div>
      </div>
      <div class="header-center">
        <span class="page-title">{{ $t('assets.futures') }}</span>
      </div>
      <div class="nav-right-icon-wrap" @click="goToKlineChart">
        <svg viewBox="0 0 1024 1024" class="kline-svg-icon">
          <path d="M896 128H128a64 64 0 0 0-64 64v640a64 64 0 0 0 64 64h768a64 64 0 0 0 64-64V192a64 64 0 0 0-64-64zM320 768H192V448h128v320zm256 0H448V256h128v512zm256 0H704V512h128v256z" fill="var(--color-brand-legacy)"></path>
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
        <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
      </button>
    </div>

    <!-- 交易对信息 -->
    <div class="pair-info">
      <div class="pair-selector" @click="showCoinSelect = true">
        <span class="pair-name">{{ symbol }}/USDT</span>
        <van-icon name="arrow-down" size="12" color="var(--color-text-primary)" style="margin-left: 4px" />
      </div>
      <div class="terminal-price">
        <strong>{{ formatPrice(markPrice) }}</strong>
        <span>Mark Price</span>
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
        <section class="trade-panel-block leverage-block">
          <div class="leverage-topline">
            <div class="margin-mode-toggle">
              <button class="mode-btn" :class="{ active: marginMode === 'cross' }" @click="marginMode = 'cross'">
                {{ $t('trade.full_position') }}
              </button>
              <button class="mode-btn" :class="{ active: marginMode === 'isolated' }" @click="marginMode = 'isolated'">
                {{ $t('trade.isolated_position') }}
              </button>
            </div>
            <button class="leverage-btn" @click="showLeveragePopup = true">
              <span>{{ currentLeverage }}x</span>
              <van-icon name="arrow-down" size="12" color="currentColor" />
            </button>
          </div>
          <p class="risk-note">Funding 0.0100% · Higher leverage increases liquidation risk.</p>
        </section>

        <section class="trade-panel-block order-type-tabs" role="tablist">
          <button :class="{ active: orderType === 'limit' }" @click="orderType = 'limit'">
            {{ $t('trade.limit_order') }}
          </button>
          <button :class="{ active: orderType === 'market' }" @click="onOrderTypeSelect({ value: 'market' })">
            {{ $t('trade.market_order') }}
          </button>
        </section>

        <section class="trade-panel-block input-block">
          <label class="terminal-label">{{ $t('trade.price') }}</label>
          <div class="terminal-input">
            <button @click="adjustOrderPrice(-currentCoinConfig.step)">−</button>
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
            <span>USDT</span>
            <button @click="adjustOrderPrice(currentCoinConfig.step)">+</button>
          </div>

          <label class="terminal-label">{{ $t('trade.amount') }}</label>
          <div class="terminal-input">
            <button @click="adjustOrderAmount(-currentCoinConfig.step)">−</button>
            <input
              v-model="amount"
              type="number"
              :placeholder="$t('trade.amount_placeholder')"
              class="input-field"
            />
            <span>{{ currentCoinConfig.baseCoin }}</span>
            <button @click="adjustOrderAmount(currentCoinConfig.step)">+</button>
          </div>
        </section>

        <section class="trade-panel-block account-metrics">
          <div class="info-row">
            <span>{{ $t('trade.avail') }}</span>
            <span class="info-value">{{ availableBalance.toFixed(2) }} USDT</span>
          </div>
          <div class="info-row">
            <span>Equity</span>
            <span class="info-value">{{ accountEquity.toFixed(2) }} USDT</span>
          </div>
          <div class="info-row">
            <span>{{ $t('trade.unrealized_pnl') }}</span>
            <span class="info-value" :class="{ positive: unrealizedPnl >= 0, negative: unrealizedPnl < 0 }">
              {{ unrealizedPnl >= 0 ? '+' : '-' }}{{ Math.abs(unrealizedPnl).toFixed(2) }} USDT
            </span>
          </div>
          <div class="info-row">
            <span>{{ $t('trade.estimated_fee') }}</span>
            <span class="info-value">{{ estimatedFee.toFixed(2) }} USDT</span>
          </div>
          <div class="info-row">
            <span>{{ $t('trade.total') }}</span>
            <span class="info-value">{{ totalValue.toFixed(2) }} USDT</span>
          </div>
        </section>

        <section class="trade-panel-block risk-slider-block">
          <input
            v-model.number="selectedPercent"
            class="risk-slider"
            type="range"
            min="0"
            max="100"
            step="1"
            @input="onPercentSliderInput"
          />
          <div class="percent-buttons">
            <button
              v-for="pct in [0, 25, 50, 75, 100]"
              :key="pct"
              class="percent-btn"
              :class="{ active: selectedPercent === pct }"
              @click="selectPercent(pct)"
            >
              {{ pct }}%
            </button>
          </div>
        </section>

        <section class="trade-panel-block terminal-actions">
          <button class="long-btn" :disabled="!isFormValid" @click="handleLong">
            {{ $t('trade.open_long') }}
          </button>
          <button class="short-btn" :disabled="!isFormValid" @click="handleShort">
            {{ $t('trade.open_short') }}
          </button>
        </section>
        <!-- 订单类型选择器 -->
        <div class="order-type-selector" @click="showOrderTypeSheet = true">
          <span>{{ orderType === 'limit' ? $t('trade.limit_order') : $t('trade.market_order') }}</span>
          <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
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
        title-active-color="var(--color-brand-legacy)" 
        title-inactive-color="var(--color-text-secondary)" 
        line-width="30px" 
        line-height="3px" 
        color="var(--color-brand-legacy)" 
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
      :overlay-style="{ backgroundColor: 'rgb(var(--color-shadow-rgb) / 0.85)', backdropFilter: 'blur(10px)' }"
      :style="{ height: 'auto', background: 'var(--color-bg)' }"
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
            <van-icon v-if="currentLeverage === leverage" name="success" color="var(--color-brand-legacy)" />
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
            <van-icon v-if="symbol === coin.symbol" name="success" color="var(--color-brand-legacy)" />
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
const maxVisibleRows = ref(5);

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
  return asks.value.slice(0, 5).reverse();
});

const displayedBids = computed(() => {
  if (!bids.value || !Array.isArray(bids.value) || bids.value.length === 0) {
    return [];
  }
  return bids.value.slice(0, 5);
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

const unrealizedPnl = computed(() => {
  return positions.value.reduce((sum, position) => sum + (Number(position.unrealizedPnl) || 0), 0);
});

const accountEquity = computed(() => {
  return availableBalance.value + unrealizedPnl.value;
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

const adjustOrderPrice = (delta) => {
  if (orderType.value !== 'limit') return;
  const basePrice = parseFloat(price.value || markPrice.value || 0);
  const nextPrice = Math.max(0, basePrice + Number(delta || 0));
  price.value = nextPrice.toFixed(currentCoinConfig.value.priceFixed);
};

const adjustOrderAmount = (delta) => {
  const baseAmount = parseFloat(amount.value || 0);
  const nextAmount = Math.max(0, baseAmount + Number(delta || 0));
  amount.value = nextAmount.toFixed(currentCoinConfig.value.amountFixed);
  selectedPercent.value = null;
};

// 选择百分比
const selectPercent = (pct) => {
  selectedPercent.value = pct;
  if (pct === 0) {
    amount.value = '';
    return;
  }
  const balance = availableBalance.value;
  const maxAmount = balance / (orderType.value === 'market' ? markPrice.value : parseFloat(price.value || markPrice.value));
  amount.value = (maxAmount * (pct / 100)).toFixed(currentCoinConfig.value.amountFixed);
};

const onPercentSliderInput = () => {
  selectPercent(Number(selectedPercent.value) || 0);
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
      confirmButtonColor: 'var(--color-loss)'
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
      confirmButtonColor: 'var(--color-loss)'
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
  border-color: rgb(var(--color-earn-rgb) / 0.3);  /* 成交绿色边框 */
}
.order-item.cancelled {
  border-color: rgb(var(--color-loss-rgb) / 0.3);  /* 取消红色边框 */
}
.order-status {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}
.order-pnl {
  font-size: 12px;
  margin-top: 4px;
}
.order-pnl.positive {
  color: var(--color-earn);
}
.order-pnl.negative {
  color: var(--color-loss);
}


.futures-trade-page {
  min-height: 100vh;
  background-color: var(--color-bg);
  color: var(--color-text-primary);
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  padding-bottom: 300px; /* 关键：防止内容被底部全局导航栏（60px）遮挡 - 增加足够的缓冲空间 */
}

/* 顶部导航栏 */
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  color: var(--color-brand-legacy);
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
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.margin-mode-toggle {
  display: flex;
  gap: 8px;
  flex: 1;
}

.mode-btn {
  flex: 1;
  padding: 8px 16px;
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  border-radius: 8px;
  text-align: center;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn.active {
  background-color: var(--color-brand-legacy);
  color: var(--color-text-on-accent);
  border-color: var(--color-brand-legacy);
  font-weight: 600;
}

.leverage-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  border-radius: 8px;
  color: var(--color-brand-legacy);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.leverage-btn:active {
  background-color: var(--color-surface-muted);
}

/* 交易对信息 */
.pair-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: var(--color-bg);
}

.pair-selector {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.pair-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.price-change {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-loss);
}

.price-change.positive {
  color: var(--color-earn);
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
  background-color: var(--color-bg);
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
  color: var(--color-text-muted);
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
  background-color: rgb(var(--color-border-rgb) / 0.02);
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
  background-color: var(--color-loss);
  opacity: 0.2;
}

.bid-depth {
  background-color: var(--color-earn);
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
  color: var(--color-loss);
  font-weight: 600;
  text-shadow: 0 0 6px rgb(var(--color-loss-rgb) / 0.4);
}

.bid-price {
  color: var(--color-earn);
  font-weight: 600;
  text-shadow: 0 0 6px rgb(var(--color-earn-rgb) / 0.4);
}

.quantity {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.last-price {
  flex-shrink: 0;
  height: 32px;
  background-color: var(--color-bg-card);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.05);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  padding: 0;
}

.last-price.up {
  background-color: rgb(var(--color-earn-rgb) / 0.05);
}

.last-price.down {
  background-color: rgb(var(--color-loss-rgb) / 0.05);
}

.price-main {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

.price-fiat {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

/* 右侧表单区 */
.form-side {
  flex: 0 0 58%;
  background-color: var(--color-bg);
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
  background-color: var(--color-bg-card);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary);
}

.input-row {
  width: 100%;
}

.input-field {
  width: 100%;
  padding: 14px 16px;
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

.input-field:focus {
  outline: none;
  border-color: var(--color-brand-legacy);
}

.input-field.market-price-input {
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.percent-buttons {
  display: flex;
  gap: 8px;
}

.percent-btn {
  flex: 1;
  padding: 10px;
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.percent-btn.active {
  background-color: var(--color-brand-legacy);
  color: var(--color-text-on-accent);
  border-color: var(--color-brand-legacy);
  font-weight: 600;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.info-value {
  color: var(--color-text-primary);
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
  background-color: var(--color-earn);
  color: var(--color-text-on-accent);
}

.long-btn:hover:not(:disabled) {
  background-color: var(--color-earn);
}

.short-btn {
  background-color: var(--color-loss);
  color: var(--color-text-primary);
}

.short-btn:hover:not(:disabled) {
  background-color: var(--color-loss);
}

.long-btn:disabled, .short-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 持仓区域 */
.positions-section {
  background-color: var(--color-bg);
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  background-color: var(--color-bg);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.order-item:hover {
  background-color: var(--color-surface-muted);
  border-color: rgb(var(--color-border-rgb) / 0.12);
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
  background-color: rgb(var(--color-earn-rgb) / 0.2);
  color: var(--color-earn);
}

.order-side-badge.sell {
  background-color: rgb(var(--color-loss-rgb) / 0.2);
  color: var(--color-loss);
}

.order-symbol-time {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-symbol {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.order-time {
  font-size: 11px;
  color: var(--color-text-secondary);
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
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

.order-quantity {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

.order-right {
  flex: 0 0 auto;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: rgb(var(--color-loss-rgb) / 0.15);
  border: 1px solid rgb(var(--color-loss-rgb) / 0.3);
  border-radius: 6px;
  color: var(--color-loss);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: rgb(var(--color-loss-rgb) / 0.25);
  border-color: rgb(var(--color-loss-rgb) / 0.5);
}

.cancel-btn:active {
  opacity: 0.7;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

/* 专业持仓卡片 */
.position-card {
  background-color: var(--color-bg-card);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

.position-perpetual {
  font-size: 11px;
  color: var(--color-text-secondary);
  padding: 2px 6px;
  background-color: rgb(var(--color-border-rgb) / 0.05);
  border-radius: 4px;
}

.position-leverage {
  font-size: 13px;
  color: var(--color-brand-legacy);
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
  color: var(--color-text-secondary);
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
  color: var(--color-earn);
  text-shadow: 0 0 12px rgb(var(--color-earn-rgb) / 0.5);
}

.unrealized-pnl-value.negative {
  color: var(--color-loss);
  text-shadow: 0 0 12px rgb(var(--color-loss-rgb) / 0.5);
}

.unrealized-pnl-percent {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.unrealized-pnl-percent.positive {
  color: var(--color-earn);
  text-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.4);
}

.unrealized-pnl-percent.negative {
  color: var(--color-loss);
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.4);
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
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 500;
}

.info-value {
  color: var(--color-text-primary);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-align: right;
  font-size: 14px;
}

.liquidation-price {
  color: var(--color-loss);
  font-weight: 700;
  font-size: 14px;
}

.position-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.1);
  color: var(--color-brand-legacy);
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.3);
}

.tp-sl-btn:active {
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.2);
}

.close-btn {
  background-color: rgb(var(--color-loss-rgb) / 0.1);
  color: var(--color-loss);
  border: 1px solid rgb(var(--color-loss-rgb) / 0.3);
}

.close-btn:active {
  background-color: rgb(var(--color-loss-rgb) / 0.2);
}

/* ========== 彻底重构的黑金样式 ========== */

/* 1. 弹窗基础容器 */
:deep(.van-popup.premium-tpsl-popup) {
  background: var(--color-bg) !important; /* 纯深色底 */
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.2);
  padding-bottom: env(safe-area-inset-bottom);
}

.premium-modal-container {
  padding: 12px 24px 32px;
  background: linear-gradient(180deg, rgb(var(--color-brand-rgb) / 0.03) 0%, rgb(var(--color-shadow-rgb) / 0) 100%);
}

.modal-drag-indicator {
  width: 36px;
  height: 4px;
  background: rgb(var(--color-border-rgb) / 0.1);
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
  background: var(--color-accent);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--color-accent);
}

.premium-modal-header h3 {
  color: var(--color-text-primary);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.5px;
  margin: 0;
}

.premium-close-btn {
  font-size: 22px;
  color: var(--color-text-muted);
  transition: color 0.3s;
}

.premium-close-btn:active { color: var(--color-accent); }

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
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mark-price-ref {
  color: var(--color-text-muted);
  font-size: 12px;
  font-family: 'DIN Alternate', sans-serif;
}

/* 4. 核心输入框盒模型 */
.premium-input-box {
  display: flex;
  align-items: center;
  background: rgb(var(--color-border-rgb) / 0.03); /* 玻璃拟态底色 */
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  border-radius: 12px;
  padding: 4px;
  transition: all 0.3s ease;
}

.premium-input-box:focus-within {
  border-color: var(--color-accent);
  background: rgb(var(--color-brand-rgb) / 0.05);
  box-shadow: 0 0 20px rgb(var(--color-brand-rgb) / 0.1);
}

.step-btn {
  width: 44px;
  height: 44px;
  background: rgb(var(--color-border-rgb) / 0.05);
  border: none;
  border-radius: 8px;
  color: var(--color-accent);
  font-size: 24px;
  font-weight: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.step-btn:active {
  background: rgb(var(--color-brand-rgb) / 0.2);
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
  color: var(--color-text-primary);
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
  color: var(--color-text-muted);
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
  background: rgb(var(--color-earn-rgb) / 0.1);
  color: var(--color-earn);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.percent-tag.sl {
  background: rgb(var(--color-loss-rgb) / 0.1);
  color: var(--color-loss);
}

.percent-tag:active { opacity: 0.7; }

/* 6. 黄金渐变按钮 */
.premium-gold-button {
  width: 100%;
  margin-top: 12px;
  padding: 18px;
  background: linear-gradient(135deg, var(--color-accent-strong) 0%, var(--color-accent) 100%);
  border: none;
  border-radius: 14px;
  color: var(--color-text-on-accent);
  font-size: 16px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 10px 20px rgb(var(--color-brand-rgb) / 0.2);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.premium-gold-button:active {
  transform: scale(0.97);
  box-shadow: 0 5px 10px rgb(var(--color-brand-rgb) / 0.1);
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
  color: var(--color-text-primary);
}

.close-icon {
  cursor: pointer;
  color: var(--color-text-secondary);
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
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  border-radius: 8px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-variant-numeric: tabular-nums;
}

.leverage-option:active {
  background-color: var(--color-surface-muted);
}

.leverage-option.active {
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.1);
  border-color: var(--color-brand-legacy);
  color: var(--color-brand-legacy);
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
  background-color: var(--color-bg-card);
  border-radius: 8px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.coin-item:active {
  background-color: var(--color-surface-muted);
}

.coin-item.active {
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.1);
  border-color: var(--color-brand-legacy);
  color: var(--color-brand-legacy);
}

/* 深度覆盖弹窗背景 */
:deep(.leverage-popup .van-popup),
:deep(.coin-select-popup .van-popup) {
  background: var(--color-bg-card) !important;
}

:deep(.van-action-sheet) {
  background: var(--color-bg-card) !important;
}

:deep(.van-action-sheet__item) {
  background: var(--color-bg-card) !important;
  color: var(--color-text-primary) !important;
}

:deep(.van-action-sheet__item:active) {
  background-color: rgb(var(--color-border-rgb) / 0.05) !important;
}

/* ========== Pro Futures Terminal Refinement ========== */
.futures-trade-page {
  --terminal-bg: #0b0e11;
  --terminal-surface: #0f1115;
  --terminal-card: #151a21;
  --terminal-card-soft: #11161d;
  --terminal-border: #232a35;
  --terminal-text: #e5e7eb;
  --terminal-muted: #9ca3af;
  --terminal-long: #22c55e;
  --terminal-short: #ef4444;
  --terminal-yellow: #f0b90b;
  background: var(--terminal-bg);
  color: var(--terminal-text);
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto Mono', sans-serif;
  font-variant-numeric: tabular-nums;
  padding-bottom: 92px;
}

.trade-header,
.pair-info,
.positions-section,
:deep(.position-tabs .van-tabs__wrap) {
  background: var(--terminal-bg);
  border-color: var(--terminal-border);
}

.futures-control-bar {
  display: none;
}

.trade-header {
  height: 52px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--terminal-border);
}

.page-title {
  color: var(--terminal-text);
  font-size: 17px;
  font-weight: 700;
}

.pair-info {
  min-height: 66px;
  padding: 10px 14px;
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 10px;
  border-bottom: 1px solid var(--terminal-border);
}

.pair-name {
  color: var(--terminal-text);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.2px;
}

.terminal-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.1;
}

.terminal-price strong {
  color: var(--terminal-text);
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-size: 31px;
  font-weight: 800;
  letter-spacing: -1px;
}

.terminal-price span {
  margin-top: 4px;
  color: var(--terminal-muted);
  font-size: 11px;
  font-weight: 500;
}

.price-change {
  min-width: 72px;
  height: 30px;
  align-self: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgb(239 68 68 / 0.14);
  color: var(--terminal-short);
  font-size: 14px;
  font-weight: 800;
}

.price-change.positive {
  background: rgb(34 197 94 / 0.14);
  color: var(--terminal-long);
}

.trade-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 10px;
  align-items: stretch;
  padding: 10px;
  background: var(--terminal-bg);
}

.orderbook-side,
.form-side {
  width: auto;
  min-height: 520px;
  background: var(--terminal-card);
  border: 1px solid var(--terminal-border);
  border-radius: 14px;
  box-shadow: 0 10px 24px rgb(0 0 0 / 0.18);
  overflow: hidden;
}

.orderbook-side {
  padding: 10px 8px;
}

.orderbook-header {
  padding: 0 4px 8px;
  color: var(--terminal-muted);
  font-size: 11px;
  font-weight: 600;
}

.order-row {
  height: 22px;
  line-height: 22px;
  padding: 0 6px;
  border-radius: 5px;
  transition: background 160ms ease, transform 160ms ease;
}

.order-row:hover {
  background: rgb(255 255 255 / 0.045);
  transform: translateX(1px);
}

.depth-bar {
  opacity: 1;
  border-radius: 5px;
}

.ask-depth {
  background: linear-gradient(90deg, transparent, rgb(239 68 68 / 0.16));
}

.bid-depth {
  background: linear-gradient(90deg, transparent, rgb(34 197 94 / 0.16));
}

.price,
.quantity {
  font-size: 12px;
  font-weight: 600;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.ask-price {
  color: #ff6b72;
  text-shadow: none;
}

.bid-price {
  color: #34d27a;
  text-shadow: none;
}

.quantity {
  color: #aeb6c2;
  font-weight: 500;
}

.last-price {
  height: 72px;
  margin: 10px 2px;
  border: 1px solid rgb(240 185 11 / 0.34);
  border-radius: 12px;
  background: linear-gradient(180deg, rgb(240 185 11 / 0.08), rgb(240 185 11 / 0.025));
  box-shadow: 0 0 18px rgb(240 185 11 / 0.12);
  animation: terminalPulse 2.6s ease-in-out infinite;
}

.last-price.up,
.last-price.down {
  background: linear-gradient(180deg, rgb(240 185 11 / 0.08), rgb(240 185 11 / 0.025));
}

.price-main {
  color: var(--terminal-yellow);
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.7px;
}

.price-fiat {
  color: var(--terminal-muted);
  font-size: 11px;
}

.form-side {
  flex: initial;
  padding: 10px;
  gap: 8px;
  overflow: hidden;
}

.form-side > .order-type-selector,
.form-side > .input-row,
.form-side > .percent-buttons,
.form-side > .info-row,
.form-side > div.futures-action-buttons {
  display: none;
}

.trade-panel-block {
  background: var(--terminal-card-soft);
  border: 1px solid var(--terminal-border);
  border-radius: 12px;
  padding: 10px;
}

.leverage-block {
  padding: 9px 10px;
}

.leverage-topline {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
}

.margin-mode-toggle {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.mode-btn,
.leverage-btn {
  height: 32px;
  border: 1px solid var(--terminal-border);
  border-radius: 8px;
  background: #0f141b;
  color: var(--terminal-muted);
  font-size: 12px;
  font-weight: 700;
}

.mode-btn.active,
.leverage-btn {
  color: var(--terminal-yellow);
  border-color: rgb(240 185 11 / 0.32);
  background: rgb(240 185 11 / 0.08);
}

.leverage-btn {
  min-width: 62px;
  justify-content: center;
  padding: 0 10px;
}

.risk-note {
  margin: 7px 0 0;
  color: var(--terminal-muted);
  font-size: 11px;
  line-height: 1.35;
}

.order-type-tabs {
  height: 40px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 0 6px;
  align-items: end;
  background: transparent;
  border-color: transparent;
}

.order-type-tabs button {
  height: 36px;
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--terminal-muted);
  font-size: 13px;
  font-weight: 800;
}

.order-type-tabs button.active {
  color: var(--terminal-text);
  border-bottom-color: var(--terminal-yellow);
}

.input-block {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.terminal-label {
  color: var(--terminal-muted);
  font-size: 11px;
  font-weight: 700;
}

.terminal-input {
  height: 40px;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto 28px;
  gap: 6px;
  align-items: center;
  padding: 0 6px;
  border: 1px solid var(--terminal-border);
  border-radius: 9px;
  background: #0e1319;
  transition: border 160ms ease, box-shadow 160ms ease;
}

.terminal-input:focus-within {
  border-color: rgb(240 185 11 / 0.7);
  box-shadow: 0 0 0 3px rgb(240 185 11 / 0.10);
}

.terminal-input button {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 7px;
  background: #151c25;
  color: var(--terminal-muted);
  font-size: 16px;
  font-weight: 800;
}

.terminal-input button:active {
  transform: scale(0.94);
}

.terminal-input span {
  color: var(--terminal-muted);
  font-size: 11px;
  font-weight: 800;
}

.input-field {
  height: 38px;
  padding: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
  color: var(--terminal-text);
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-size: 13px;
  font-weight: 700;
}

.input-field:focus {
  border: 0;
  box-shadow: none;
}

.input-field::placeholder {
  color: #687180;
  font-weight: 600;
}

.account-metrics {
  display: grid;
  gap: 6px;
  padding: 9px 10px;
}

.info-row {
  font-size: 11px;
  color: var(--terminal-muted);
}

.info-value {
  color: var(--terminal-text);
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-size: 12px;
  font-weight: 700;
}

.info-value.positive {
  color: var(--terminal-long);
}

.info-value.negative {
  color: var(--terminal-short);
}

.risk-slider-block {
  padding: 10px;
}

.risk-slider {
  width: 100%;
  height: 4px;
  appearance: none;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--terminal-yellow), #394150);
  outline: none;
}

.risk-slider::-webkit-slider-thumb {
  width: 14px;
  height: 14px;
  appearance: none;
  border: 2px solid var(--terminal-bg);
  border-radius: 999px;
  background: var(--terminal-yellow);
  box-shadow: 0 0 0 3px rgb(240 185 11 / 0.18);
}

.percent-buttons {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 5px;
  margin-top: 10px;
}

.percent-btn {
  height: 26px;
  padding: 0;
  border-color: var(--terminal-border);
  border-radius: 7px;
  background: #0f141b;
  color: var(--terminal-muted);
  font-size: 11px;
  font-weight: 700;
}

.percent-btn.active {
  background: rgb(240 185 11 / 0.12);
  border-color: rgb(240 185 11 / 0.42);
  color: var(--terminal-yellow);
}

.terminal-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: auto;
  padding: 0;
  background: transparent;
  border: 0;
}

.long-btn,
.short-btn {
  height: 46px;
  padding: 0;
  border-radius: 11px;
  color: #ffffff;
  font-size: 14px;
  font-weight: 800;
  box-shadow: 0 10px 18px rgb(0 0 0 / 0.20);
}

.long-btn {
  background: linear-gradient(180deg, #2bd576, #16a34a);
}

.short-btn {
  background: linear-gradient(180deg, #ff6b6b, #dc2626);
}

.long-btn:hover:not(:disabled),
.short-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.04);
}

.long-btn:active:not(:disabled),
.short-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.long-btn:disabled,
.short-btn:disabled {
  opacity: 0.45;
  filter: saturate(0.55);
}

.positions-section {
  margin: 0 10px 90px;
  background: var(--terminal-card);
  border: 1px solid var(--terminal-border);
  border-radius: 14px;
  overflow: hidden;
}

.positions-list,
.orders-list,
.history-list {
  background: var(--terminal-card);
}

.empty-state,
.order-status,
.order-time,
.order-quantity,
.info-label {
  color: var(--terminal-muted);
}

.position-card,
.order-item {
  background: var(--terminal-card-soft);
  border-color: var(--terminal-border);
}

@keyframes terminalPulse {
  0%, 100% {
    box-shadow: 0 0 14px rgb(240 185 11 / 0.10);
  }
  50% {
    box-shadow: 0 0 24px rgb(240 185 11 / 0.20);
  }
}

@media (max-width: 390px) {
  .trade-main {
    gap: 8px;
    padding: 8px;
  }

  .orderbook-side,
  .form-side {
    min-height: 500px;
  }

  .terminal-price strong {
    font-size: 28px;
  }
}

/* Keep futures page aligned with app light theme */
.futures-trade-page {
  --terminal-bg: var(--color-bg);
  --terminal-surface: var(--color-bg);
  --terminal-card: #ffffff;
  --terminal-card-soft: #ffffff;
  --terminal-border: #eaecef;
  --terminal-text: var(--color-text-primary);
  --terminal-muted: var(--color-text-secondary);
  background: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
}

.futures-trade-page .trade-header,
.futures-trade-page .pair-info,
.futures-trade-page .positions-section,
.futures-trade-page :deep(.position-tabs .van-tabs__wrap) {
  background: var(--color-bg) !important;
  border-color: #eaecef !important;
}

.futures-trade-page .trade-main {
  grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr) !important;
  gap: 10px !important;
  padding: 10px 12px 12px !important;
  background: transparent !important;
}

.futures-trade-page .orderbook-side,
.futures-trade-page .form-side {
  height: 500px !important;
  min-height: 500px !important;
  max-height: 500px !important;
  background: #ffffff !important;
  border: 1px solid #eaecef !important;
  border-radius: 14px !important;
  box-shadow: 0 2px 10px rgb(17 24 39 / 0.05) !important;
}

.futures-trade-page .order-row {
  height: 32px !important;
  line-height: 32px !important;
}

.futures-trade-page .last-price {
  height: 72px !important;
  min-height: 72px !important;
  border-color: rgb(var(--color-brand-rgb) / 0.20) !important;
  background: linear-gradient(180deg, rgb(var(--color-brand-rgb) / 0.045), #ffffff) !important;
}

.futures-trade-page .price-main {
  color: var(--color-earn) !important;
  font-size: 25px !important;
  text-shadow: none !important;
}

.futures-trade-page .terminal-price strong {
  color: var(--color-text-primary) !important;
}

.futures-trade-page .trade-panel-block,
.futures-trade-page .terminal-input,
.futures-trade-page .mode-btn,
.futures-trade-page .leverage-btn {
  background: #ffffff !important;
  border-color: #eaecef !important;
  color: var(--color-text-primary) !important;
}

.futures-trade-page .terminal-actions {
  background: transparent !important;
  border: 0 !important;
}

.futures-trade-page .input-field {
  color: var(--color-text-primary) !important;
}

/* Dark mode refit audit: scoped late overrides for standalone futures page. */
:global(html[data-theme='dark']) .futures-trade-page {
  --terminal-bg: var(--color-bg);
  --terminal-surface: var(--color-surface-1);
  --terminal-card: var(--color-bg-card);
  --terminal-card-soft: var(--color-bg-input);
  --terminal-border: var(--color-border);
  --terminal-text: var(--color-text-primary);
  --terminal-muted: var(--color-text-secondary);
  background: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
}

:global(html[data-theme='dark']) .futures-trade-page .trade-header,
:global(html[data-theme='dark']) .futures-trade-page .pair-info,
:global(html[data-theme='dark']) .futures-trade-page .positions-section,
:global(html[data-theme='dark']) .futures-trade-page :deep(.position-tabs .van-tabs__wrap) {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
}

:global(html[data-theme='dark']) .futures-trade-page .orderbook-side,
:global(html[data-theme='dark']) .futures-trade-page .form-side,
:global(html[data-theme='dark']) .futures-trade-page .trade-panel-block,
:global(html[data-theme='dark']) .futures-trade-page .terminal-input,
:global(html[data-theme='dark']) .futures-trade-page .mode-btn,
:global(html[data-theme='dark']) .futures-trade-page .leverage-btn,
:global(html[data-theme='dark']) .futures-trade-page .last-price {
  background: var(--color-bg-card) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .futures-trade-page .input-field,
:global(html[data-theme='dark']) .futures-trade-page .terminal-price strong {
  color: var(--color-text-primary) !important;
  -webkit-text-fill-color: var(--color-text-primary) !important;
}
</style>
