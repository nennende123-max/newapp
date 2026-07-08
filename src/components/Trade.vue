<template>
  <div class="trade-page">
    <!-- 固定顶部导航栏 - 子页面模式隐藏 -->
    <div v-if="!isSubPage" class="trade-header">
      <div class="header-center">
        <span class="page-title">{{ pageTitle }}</span>
      </div>
      
      <div class="nav-right-icon-wrap" @click="goToKlineChart">
        <svg viewBox="0 0 1024 1024" class="kline-svg-icon">
          <path d="M896 128H128a64 64 0 0 0-64 64v640a64 64 0 0 0 64 64h768a64 64 0 0 0 64-64V192a64 64 0 0 0-64-64zM320 768H192V448h128v320zm256 0H448V256h128v512zm256 0H704V512h128v256z" fill="var(--color-brand-legacy)"></path>
        </svg>
      </div>
    </div>

    <!-- 可滚动内容区域 -->
    <div class="trade-scrollable-content">
    <div v-if="!isSubPage" class="trade-tabs">
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
        <van-icon name="arrow-down" size="12" color="var(--color-text-primary)" style="margin-left: 4px" />
      </div>
      <div class="zero-fee-badge">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z"/></svg>
        <span>限时0资金费率</span>
      </div>
      <div class="price-change" :class="{ positive: priceChange >= 0 }">
        {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
      </div>
    </div>

    <!-- 现货交易界面 -->
    <div v-if="activeTradeTab === 'spot'" class="trade-main">
      <div ref="orderBookContainerRef" class="orderbook-side">
        <div class="orderbook-header">
          <span class="header-price">{{ t('trade.price') }} (USDT)</span>
          <span class="header-quantity">{{ t('trade.amount') }} ({{ currentCoinConfig.baseCoin }})</span>
        </div>

        <div class="asks-list">
          <div 
            v-for="(ask, index) in displayedAsks" 
            :key="`ask-${index}`"
            class="order-row ask-row"
            :style="{ '--depth-width': getDepthWidth(ask.quantity, displayedAsks, 'asks') + '%' }"
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
            v-for="(bid, index) in displayedBids" 
            :key="`bid-${index}`"
            class="order-row bid-row"
            :style="{ '--depth-width': getDepthWidth(bid.quantity, displayedBids, 'bids') + '%' }"
            @click="selectPrice(bid.price, 'buy')"
          >
            <div class="depth-bar bid-depth"></div>
            <span class="price bid-price">{{ formatPrice(bid.price) }}</span>
            <span class="quantity">{{ formatQuantity(bid.quantity) }}</span>
          </div>
        </div>
      </div>

      <div ref="orderFormRef" class="form-side">
        <div class="buy-sell-toggle">
          <div 
            class="toggle-btn buy-btn" 
            :class="{ active: orderSide === 'buy' }"
            @click="switchOrderSide('buy')"
          >
            {{ t('trade.buy') }}
          </div>
          <div 
            class="toggle-btn sell-btn" 
            :class="{ active: orderSide === 'sell' }"
            @click="switchOrderSide('sell')"
          >
            {{ t('trade.sell') }}
          </div>
        </div>

        <div class="order-type-selector" @click="showOrderTypeSheet = true">
          <span>{{ orderType === 'limit' ? t('trade.limit_order') : t('trade.market_order') }}</span>
          <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
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
            active-color="var(--color-brand-legacy)"
            inactive-color="var(--color-surface-muted)"
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
              color="var(--color-brand-legacy)" 
              style="margin-left: 4px; cursor: pointer;" 
              @click.stop="openDeposit('USDT')" 
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
      <!-- 核心交易区 - 左右布局 -->
      <div class="futures-trade-main">
        <!-- 左侧：盘口区 (42%) -->
        <div ref="orderBookContainerRef" class="futures-orderbook-side">
          <div class="orderbook-header">
            <span class="header-price">{{ t('trade.price') }} (USDT)</span>
            <span class="header-quantity">{{ t('trade.amount') }} ({{ currentCoinConfig.baseCoin }})</span>
          </div>

          <div class="asks-list">
            <div 
              v-for="(ask, index) in displayedAsks" 
              :key="`ask-${index}`"
              class="order-row ask-row"
              :style="{ '--depth-width': getDepthWidth(ask.quantity, displayedAsks, 'asks') + '%' }"
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
              v-for="(bid, index) in displayedBids" 
              :key="`bid-${index}`"
              class="order-row bid-row"
              :style="{ '--depth-width': getDepthWidth(bid.quantity, displayedBids, 'bids') + '%' }"
              @click="selectFuturesPrice(bid.price)"
            >
              <div class="depth-bar bid-depth"></div>
              <span class="price bid-price">{{ formatPrice(bid.price) }}</span>
              <span class="quantity">{{ formatQuantity(bid.quantity) }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧：交易表单 (58%) -->
        <div ref="orderFormRef" class="futures-form-side">
          <!-- 买入/卖出切换栏：仅在现货模式下显示 -->
          <div v-if="isSpotMode" class="buy-sell-toggle">
            <div 
              class="toggle-btn buy-btn" 
              :class="{ active: orderSide === 'buy' }"
              @click="switchOrderSide('buy')"
            >
              {{ t('trade.buy') }}
            </div>
            <div 
              class="toggle-btn sell-btn" 
              :class="{ active: orderSide === 'sell' }"
              @click="switchOrderSide('sell')"
            >
              {{ t('trade.sell') }}
            </div>
          </div>

          <!-- 资产信息面板：合约模式下显示合约资产，现货模式下显示现货资产 -->
          <div v-if="!isSpotMode" class="futures-asset-panel">
            <div class="asset-row">
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.total_equity') }}</span>
                <span class="asset-value">{{ formatPrice(totalEquity) }} USDT</span>
              </div>
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.available_margin') }}</span>
                <span class="asset-value">{{ formatPrice(availableMargin) }} USDT</span>
              </div>
            </div>
            <div class="asset-row">
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.frozen_margin') }}</span>
                <span class="asset-value">{{ formatPrice(frozenMargin) }} USDT</span>
              </div>
              <div class="asset-item">
                <span class="asset-label">{{ t('trade.unrealized_pnl') }}</span>
                <span 
                  class="asset-value" 
                  :class="{ 'pnl-positive': totalUnrealizedPnl >= 0, 'pnl-negative': totalUnrealizedPnl < 0, 'pnl-flash': pnlChanged }"
                >
                  {{ totalUnrealizedPnl >= 0 ? '+' : '' }}{{ formatPrice(totalUnrealizedPnl) }} USDT
                </span>
              </div>
            </div>
          </div>
          <!-- 现货模式：显示可用余额 -->
          <div v-else class="available-row" style="margin-bottom: 16px; padding: 12px;">
            <div class="avail-item">
              <span class="avail-label">{{ t('trade.avail') }}：</span>
              <span class="avail-value">{{ formatAvailableBalance }}</span>
            </div>
            <div class="avail-item">
              <span class="avail-label">{{ t('trade.sellable') }}：</span>
              <span class="avail-value">{{ formatSellableBalance }}</span>
            </div>
          </div>

          <div class="form-tools-row" :class="{ 'futures-tools-row': !isSpotMode }">
            <div class="order-type-selector" @click="showOrderTypeSheet = true">
              <span>{{ orderType === 'limit' ? t('trade.limit_order') : t('trade.market_order') }}</span>
              <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
            </div>
            <button
              v-if="!isSpotMode"
              type="button"
              class="leverage-inline-btn"
              @click="showLeveragePopup = true"
            >
              <span>{{ currentLeverage }}x</span>
              <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
            </button>
          </div>

          <div class="input-row">
            <!-- 现货模式：使用 price 字段 -->
            <template v-if="isSpotMode">
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
            </template>
            <!-- 合约模式：使用 futuresPrice 字段 -->
            <template v-else>
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
            </template>
            <!-- 市价单时价格框显示“按市场最优价成交”，隐藏 USDT 单位，避免与提示文字重叠 -->
            <span v-if="orderType === 'limit'" class="input-suffix">USDT</span>
          </div>

          <div class="input-row">
            <!-- 现货模式：使用 amount 字段 -->
            <template v-if="isSpotMode">
              <input
                v-model="amount"
                type="number"
                min="0"
                step="0.0001"
                :placeholder="t('trade.amount_placeholder')"
                class="input-field no-spinner"
                @input="handleAmountInput"
              />
            </template>
            <!-- 合约模式：使用 futuresAmount 字段 -->
            <template v-else>
            <input
              v-model="futuresAmount"
              type="number"
              :placeholder="t('trade.amount_placeholder')"
              class="input-field no-spinner"
              @input="handleFuturesAmountInput"
            />
            </template>
            <span class="input-suffix">{{ currentCoinConfig.baseCoin }}</span>
          </div>

          <!-- 杠杆滑块：仅在合约模式下显示 -->
          <div v-if="!isSpotMode" class="slider-wrapper">
            <van-slider
              v-model="futuresSliderValue"
              :min="0"
              :max="100"
              :step="1"
              bar-height="4px"
              button-size="16px"
              active-color="var(--color-brand-legacy)"
              inactive-color="var(--color-surface-muted)"
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
          <!-- 现货模式：使用现货滑块 -->
          <div v-else class="slider-wrapper">
            <van-slider
              v-model="spotSliderValue"
              :min="0"
              :max="100"
              :step="1"
              bar-height="4px"
              button-size="16px"
              active-color="var(--color-brand-legacy)"
              inactive-color="var(--color-surface-muted)"
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

          <!-- 费用和总额：根据模式显示不同的计算逻辑 -->
          <div class="fee-estimate-row">
            <span class="fee-estimate-label">{{ t('trade.estimated_fee') }}({{ isSpotMode && orderSide === 'buy' ? currentCoinConfig.baseCoin : 'USDT' }})</span>
            <span class="fee-estimate-value">
              <template v-if="isSpotMode">
                {{ formatEstimatedFee }}
                <span v-if="orderSide === 'buy' && formatEstimatedFeeUSDT" class="fee-usdt-note">(≈ {{ formatEstimatedFeeUSDT }} USDT)</span>
              </template>
              <template v-else>
                {{ formatFuturesEstimatedFee }}
              </template>
            </span>
          </div>

          <div class="total-row">
            <span class="total-label">{{ t('trade.total') }}(USDT)</span>
            <span class="total-value">
              <template v-if="isSpotMode">
                {{ formatTotalAmount }}
              </template>
              <template v-else>
                {{ formatFuturesTotalAmount }}
              </template>
            </span>
          </div>

          <!-- 保证金金额：仅在合约模式下显示 -->
          <div v-if="!isSpotMode" class="estimated-received-row">
            <span class="received-label">{{ t('trade.margin_amount') }}</span>
            <span class="received-value">{{ futuresMargin > 0 ? futuresMargin.toFixed(2) : '0.00' }} USDT</span>
          </div>

          <div v-if="!isSpotMode" class="available-margin-row">
            <span class="available-margin-label">{{ t('trade.available_margin') }}</span>
            <span class="available-margin-value">{{ formatPrice(availableMargin) }} USDT</span>
          </div>

          <!-- 操作按钮：根据模式显示不同按钮 -->
          <div v-if="isSpotMode" class="futures-action-buttons-grid">
            <!-- 现货模式：买入/卖出按钮 -->
            <button 
              class="long-btn-grid"
              :disabled="!isOrderValid || isLoading"
              @click="handleSubmitOrder"
            >
              {{ orderSide === 'buy' ? t('trade.buy_btc').replace('BTC', symbol) : t('trade.sell_btc').replace('BTC', symbol) }}
            </button>
          </div>
          <div v-else class="futures-action-buttons-grid">
            <!-- 合约模式：开多/开空按钮 -->
            <button 
              class="long-btn-grid"
              :disabled="!isFuturesFormValid"
              @click="handleLong"
            >
              {{ t('trade.open_long') }}
            </button>
            <button 
              class="short-btn-grid"
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
          title-active-color="var(--color-brand-legacy)" 
          title-inactive-color="var(--color-text-secondary)" 
          line-width="30px" 
          line-height="3px" 
          color="var(--color-brand-legacy)" 
          :border="false"
          class="position-tabs"
        >
          <!-- 持有仓位Tab：仅在合约模式下显示 -->
          <van-tab v-if="!isSpotMode" :title="t('trade.positions_tab', { count: displayPositions.length })">
            <div class="positions-list">
              <div v-if="displayPositions.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="orders-o" size="48" color="var(--color-text-secondary)" />
                </div>
                <div class="empty-text">{{ t('trade.no_positions') }}</div>
              </div>
              <div 
                v-for="(position, index) in displayPositions" 
                :key="index"
                class="position-card"
              >
                <div class="position-card-main">
                  <div class="position-left">
                    <div class="position-symbol-row">
                      <span class="position-symbol">{{ position.symbol }}USDT</span>
                      <span 
                        class="position-side-badge" 
                        :class="isLongPosition(position) ? 'side-long' : 'side-short'"
                      >
                        {{ isLongPosition(position) ? t('trade.long') : t('trade.short') }}
                      </span>
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
                      <span class="info-label">{{ t('trade.entry_price') }}</span>
                      <span class="info-value">{{ formatPrice(position.entryPrice) }}</span>
                    </div>
                    <div class="position-info-row">
                      <span class="info-label">{{ t('trade.margin_amount') }} (USDT)</span>
                      <span class="info-value">{{ formatPrice(position.margin) }}</span>
                    </div>
                    <div class="position-info-row">
                      <span class="info-label">标记价格</span>
                      <span class="info-value">{{ formatPrice(position.markPrice || markPrice) }}</span>
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
              <div v-if="!futuresOrdersList || futuresOrdersList.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="orders-o" size="48" color="var(--color-text-secondary)" />
                </div>
                <div class="empty-text">{{ t('trade.no_orders') }}</div>
              </div>
              <div v-else>
                <div 
                  v-for="(order, index) in futuresOrdersList"
                  :key="order.order_id || `order-${index}`"
                  class="order-item"
                >
                  <div class="order-left">
                    <div class="order-side-badge" :class="order.side">
                      {{ order.side === 'buy' ? t('trade.buy') : t('trade.sell') }}
                    </div>
                    <div class="order-symbol-time">
                      <span class="order-symbol">{{ order.symbol || 'N/A' }}</span>
                      <span class="order-time">{{ formatOrderTime(order.timestamp) }}</span>
                    </div>
                  </div>
                  
                  <div class="order-center">
                    <div class="order-price">{{ formatPrice(order.price) }}</div>
                    <div class="order-quantity">{{ formatQuantity(order.quantity || order.amount) }} / {{ formatQuantity(order.quantity || order.amount) }}</div>
                  </div>
                  
                  <div class="order-right">
                    <button class="cancel-btn" @click="cancelOrder(order.order_id)">{{ t('trade.cancel') }}</button>
                  </div>
                </div>
              </div>
            </div>
          </van-tab>
          <van-tab :title="t('trade.trade_history_tab')">
            <div class="history-list">
              <div v-if="!futuresHistoryList || futuresHistoryList.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="orders-o" size="48" color="var(--color-text-secondary)" />
                </div>
                <div class="empty-text">{{ t('trade.no_orders') }}</div>
              </div>
              <div v-else>
                <div 
                  v-for="(order, index) in futuresHistoryList"
                  :key="order.order_id || `history-${index}`"
                  class="order-item history-order-item"
                  :class="{ 'liquidation-order': order.type === 'liquidation' || order.type === 'LIQUIDATION' }"
                >
                  <!-- 左侧：操作详情 -->
                  <div class="history-order-left">
                    <div class="history-order-header">
                      <!-- 强平订单特殊标签 -->
                      <div 
                        v-if="order.type === 'liquidation' || order.type === 'LIQUIDATION'"
                        class="liquidation-badge"
                      >
                        {{ t('trade.forced_liquidation') }}
                      </div>
                      <!-- 普通订单方向标签 -->
                      <div 
                        v-else
                        class="order-side-badge" 
                        :class="order.side"
                      >
                        {{ order.side === 'buy' ? t('trade.buy') : t('trade.sell') }}
                      </div>
                      <span class="history-order-symbol">{{ order.symbol || 'N/A' }}/USDT</span>
                    </div>
                    <div class="history-order-details">
                      <span class="history-order-price-quantity">
                        {{ formatQuantity(order.quantity || order.amount) }} @ {{ formatPrice(order.price) }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- 右侧：核心结果（盈亏 + 时间） -->
                  <div class="history-order-right">
                    <div 
                      v-if="order.realized_pnl !== undefined" 
                      class="history-order-pnl" 
                      :class="{ 
                        'pnl-positive': order.realized_pnl > 0, 
                        'pnl-negative': order.realized_pnl < 0,
                        'pnl-zero': order.realized_pnl === 0,
                        'pnl-liquidation': order.type === 'liquidation' || order.type === 'LIQUIDATION'
                      }"
                    >
                      {{ order.realized_pnl >= 0 ? '+' : '' }}{{ formatPrice(order.realized_pnl) }} USDT
                    </div>
                    <div class="history-order-time">{{ formatOrderTime(order.timestamp) }}</div>
                  </div>
                </div>

                <!-- IntersectionObserver 监听目标（触底锚点） -->
                <div ref="loadMoreTrigger" class="history-observer-target"></div>

                <!-- 底部状态栏 -->
                <div class="history-footer">
                  <!-- 加载中 -->
                  <div v-if="historyLoading" class="history-loading">
                    <van-loading type="spinner" color="var(--color-accent)" size="16px" />
                    <span class="loading-text">{{ t('common.loading') || '加载中...' }}</span>
                  </div>
                  <!-- 没有更多了 -->
                  <div v-else-if="!historyHasMore && futuresHistoryList.length > 0" class="history-no-more">
                    - 仅展示近 3 个月的记录 -
                  </div>
                </div>
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
            <div v-if="!spotOrdersList || spotOrdersList.length === 0" class="orders-empty-compact">
              <span class="empty-text-compact">{{ t('trade.no_orders') }}</span>
              </div>
            <div v-else class="orders-list-compact">
              <div 
                v-for="(order, index) in spotOrdersList"
                :key="order.order_id || `order-${index}`"
                class="order-item"
              >
                <div class="order-left">
                  <div class="order-side-badge" :class="order.side">
                    {{ order.side === 'buy' ? t('trade.buy') : t('trade.sell') }}
                  </div>
                  <div class="order-symbol-time">
                      <span class="order-symbol">{{ order.symbol || 'N/A' }}</span>
                    <span class="order-time">{{ formatOrderTime(order.timestamp) }}</span>
                  </div>
                </div>
                
                <div class="order-center">
                  <div class="order-price">{{ formatPrice(order.price) }}</div>
                    <div class="order-quantity">{{ formatQuantity(order.quantity || order.amount) }} / {{ formatQuantity(order.quantity || order.amount) }}</div>
                </div>
                
                <div class="order-right">
                    <button class="cancel-btn" @click="cancelOrder(order.order_id)">{{ t('trade.cancel') }}</button>
                </div>
              </div>
            </div>
          </div>

          <div v-else key="assets" class="assets-panel panel-full">
            <div class="assets-glass-card">
              <div class="assets-hud-strip">
                <div class="asset-hud-item">
                  <span class="asset-hud-label">{{ t('trade.avail') }}</span>
                  <span class="asset-hud-value">{{ formatAssetBalance(assetStore.getHolding(symbol), symbol) }} {{ symbol }}</span>
              </div>
                <div class="asset-hud-divider"></div>
                <div class="asset-hud-item">
                  <span class="asset-hud-label">{{ t('trade.frozen') }}</span>
                  <span class="asset-hud-value">{{ formatAssetBalance(assetStore.userAssets?.[`${symbol}_frozen`] || 0, symbol) }} {{ symbol }}</span>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
    </div>
    <!-- 可滚动内容区域结束 -->

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
            <CryptoIcon :symbol="coin.symbol" :size="32" variant="compact" />
            <div class="coin-select-meta">
              <div class="coin-name">{{ coin.symbol }}</div>
              <div class="coin-pair">{{ coin.symbol }}/USDT</div>
            </div>
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

    <!-- 杠杆选择弹窗：仅在合约模式下显示 -->
    <van-popup
      v-if="!isSpotMode"
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
            <van-icon v-if="currentLeverage === leverage" name="success" color="var(--color-brand-legacy)" />
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 止盈止损弹窗：仅在合约模式下显示 -->
    <van-popup
      v-if="!isSpotMode"
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
          <h3>{{ t('trade.take_profit_stop_loss') }}</h3>
        </div>
          <van-icon name="cross" @click="showTPSLPopup = false" class="premium-close-btn" />
        </div>

        <div class="premium-tpsl-form">
          <!-- 止盈价格输入 -->
          <div class="premium-form-group">
            <div class="group-label-row">
            <label>{{ t('trade.take_profit_price') }}</label>
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
              <label>{{ t('trade.stop_loss_price') }}</label>
              <span v-if="currentTPSLPosition?.position?.liquidationPrice" class="mark-price-ref">
                {{ t('trade.liquidation_price') }}: {{ formatPrice(currentTPSLPosition.position.liquidationPrice) }}
              </span>
            </div>
            
            <div class="premium-input-box">
              <button class="step-btn" @click="adjustTPSLPrice('stopLossPrice', -10)">-</button>
              <div class="input-inner-wrap">
                <input 
                  v-model="tpSlForm.stopLossPrice" 
                  type="number" 
                  placeholder="0.00"
                  class="mono-font"
                  :class="{ 'input-error': stopLossPriceError }"
                />
                <span class="input-suffix">USDT</span>
              </div>
              <button class="step-btn" @click="adjustTPSLPrice('stopLossPrice', 10)">+</button>
            </div>

            <!-- 错误提示 -->
            <div v-if="stopLossPriceError" class="tpsl-error-message">
              {{ stopLossPriceError }}
            </div>

            <div class="quick-select-row">
              <div 
                v-for="p in [0.02, 0.05, 0.1]" 
                :key="p" 
                class="percent-tag sl" 
                :class="{ 'disabled': isStopLossPercentDisabled(p) }"
                @click="setTPSLPercentage('stopLossPrice', p)"
              >
                -{{ p * 100 }}%
              </div>
            </div>
          </div>

          <!-- 核心执行按钮 -->
          <button 
            class="premium-gold-button" 
            :class="{ 'disabled': !isTPSLFormValid }"
            :disabled="!isTPSLFormValid"
            @click="confirmTPSL"
          >
            {{ t('trade.confirm') }}
          </button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated, onDeactivated, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, Icon, Popup, Empty, ActionSheet, Tabs, Tab, showConfirmDialog, Slider } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { useMarketStore } from '@/stores/market';
import { useAssetActions } from '@/composables/useAssetActions';
import { createOrder, getOrders, cancelOrder as cancelSpotOrderApi } from '@/api/trade';
import { createFuturesOrder, getPositions as getFuturesPositionsApi, closePosition as closeFuturesPositionApi, getFuturesOrders, cancelFuturesOrder as cancelFuturesOrderApi } from '@/api/futures';
import { formatAssetAmount } from '@/utils/format';
import CryptoIcon from './CryptoIcon.vue';

defineOptions({
  name: 'Trade'
});

// Props: 支持子页面模式
const props = defineProps({
  isSubPage: {
    type: Boolean,
    default: false
  },
  initialSymbol: {
    type: String,
    default: null
  },
  initialSide: {
    type: String,
    default: null
  },
  // 强制指定交易类型（子页面使用）
  forceTradeTab: {
    type: String,
    default: null,
    validator: (value) => !value || value === 'spot' || value === 'futures'
  },
  // 初始模式（子页面使用，用于控制界面显示）
  initialMode: {
    type: String,
    default: 'futures',
    validator: (value) => value === 'spot' || value === 'futures'
  }
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n(); 
const assetStore = useAssetStore();
const marketStore = useMarketStore();
const { openDeposit } = useAssetActions();

// 修复1：计算属性绑定 pageTitle，解决语言切换问题
const pageTitle = computed(() => t('trade.title'));

// 支持子页面模式：优先使用props传入的symbol，否则使用路由参数
const symbol = ref(props.initialSymbol || route.query.symbol || 'BTC');

// 支持从 props 或路由参数获取初始方向
const orderSide = ref(
  props.initialSide || (route.query.side === 'buy' || route.query.side === 'sell' ? route.query.side : 'buy')
);

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

// 子页面模式下，根据 forceTradeTab prop 设置初始标签页
// 主页面模式下，默认显示现货
const activeTradeTab = ref(props.forceTradeTab || 'spot');

// 判断是否为现货模式（用于控制界面元素显示）
const isSpotMode = computed(() => {
  // 子页面模式下，使用 initialMode prop
  if (props.isSubPage) {
    return props.initialMode === 'spot';
  }
  // 主页面模式下，根据 activeTradeTab 判断
  return activeTradeTab.value === 'spot';
});

// 子页面模式下，禁止切换标签页（因为标签切换器已被隐藏）
const canSwitchTab = computed(() => !props.isSubPage);
// orderSide 已在上面定义（支持 props 传入）
const orderType = ref('limit'); 
const price = ref('');
const amount = ref('');
const priceChange = ref(1.83);
const lastPrice = ref(92255.50);
const activeOrderTab = ref('orders');
const selectedPercent = ref(null);
const spotSliderValue = ref(0); // 现货滑块值 (0-100)
// 数据隔离：现货和合约订单分开存储
const spotOrdersList = ref([]);      // 现货订单列表
const futuresOrdersList = ref([]);   // 合约订单列表

// 注意：不再使用 ordersList computed，直接使用 spotOrdersList 和 futuresOrdersList
// const ordersList = computed(() => {
//   return activeTradeTab.value === 'spot' ? spotOrdersList.value : futuresOrdersList.value;
// });
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
// 现货模式下默认选中"当前委托"Tab（索引1），合约模式下默认选中"持有仓位"Tab（索引0）
// 注意：由于 van-tabs 需要 ref，我们使用 ref + watch 来实现动态切换
const resetSpotAmountInput = () => {
  amount.value = '';
  selectedPercent.value = null;
  spotSliderValue.value = 0;
};

const switchOrderSide = (side) => {
  if (side !== 'buy' && side !== 'sell') return;
  orderSide.value = side;
  resetSpotAmountInput();
};

const activePositionTab = ref(0);

// 监听 isSpotMode 变化，自动切换 Tab
watch(isSpotMode, (isSpot) => {
  if (props.isSubPage) {
    activePositionTab.value = isSpot ? 1 : 0; // 现货模式选中"当前委托"，合约模式选中"持有仓位"
  }
}, { immediate: true });

// 初始化时设置正确的 Tab
if (props.isSubPage && isSpotMode.value) {
  activePositionTab.value = 1; // 现货模式默认选中"当前委托"
}
const positions = ref([]);
const futuresHistoryList = ref([]);  // 合约历史订单列表
const historyPage = ref(1);  // 当前页码（从1开始）
const historyPageSize = ref(20);  // 每页条数
const historyHasMore = ref(true);  // 是否还有更多数据
const historyLoading = ref(false);  // 是否正在加载
const loadMoreTrigger = ref(null);  // IntersectionObserver 监听目标（绑定到底部那个看不见的 div）
let historyObserver = null;  // 存放观察器实例
const showTPSLPopup = ref(false);

// 资产信息计算属性（合约页面）
const usdtBalance = computed(() => {
  return assetStore.userAssets?.USDT || 0;
});

const frozenMargin = computed(() => {
  return assetStore.userAssets?.USDT_frozen || 0;
});

// 计算所有持仓占用的保证金总和（已占用保证金）
const totalPositionMargin = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.margin || 0), 0);
});

const totalUnrealizedPnl = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.unrealizedPnl || 0), 0);
});

// 账户权益 = 余额 + 未实现盈亏
const totalEquity = computed(() => {
  return usdtBalance.value + totalUnrealizedPnl.value;
});

// 可用保证金 = 账户权益 - 已占用保证金 - 委托冻结
const availableMargin = computed(() => {
  const equity = totalEquity.value;
  const usedMargin = totalPositionMargin.value;
  const frozen = frozenMargin.value;
  const available = Math.max(0, equity - usedMargin - frozen);
  
  // 调试日志：验证公式 账户权益 = 可用 + 占用 + 冻结
  if (process.env.NODE_ENV === 'development' && positions.value.length > 0) {
    const sum = available + usedMargin + frozen;
    const diff = Math.abs(equity - sum);
    if (diff > 0.01) { // 允许0.01的误差
      console.warn(`[资产计算] 公式验证失败: 账户权益(${equity.toFixed(2)}) ≠ 可用(${available.toFixed(2)}) + 占用(${usedMargin.toFixed(2)}) + 冻结(${frozen.toFixed(2)}) = ${sum.toFixed(2)}, 差值: ${diff.toFixed(2)}`);
    } else {
      console.log(`[资产计算] ✓ 公式验证通过: 账户权益(${equity.toFixed(2)}) = 可用(${available.toFixed(2)}) + 占用(${usedMargin.toFixed(2)}) + 冻结(${frozen.toFixed(2)})`);
    }
  }
  
  return available;
});

// PnL 变化闪烁效果
const pnlChanged = ref(false);
let pnlFlashTimer = null;
watch(totalUnrealizedPnl, () => {
  pnlChanged.value = true;
  if (pnlFlashTimer) clearTimeout(pnlFlashTimer);
  pnlFlashTimer = setTimeout(() => {
    pnlChanged.value = false;
  }, 1000);
});
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
const orderBookContainerRef = ref(null);
const orderFormRef = ref(null);
const maxVisibleRows = ref(5); // compact 5-level orderbook for terminal layout

// 缓存最大数量值，避免重复计算
const maxQuantityCache = {
  asks: null,
  bids: null,
  asksListHash: null,
  bidsListHash: null
};

/**
 * 生成列表的简单哈希值，用于检测列表是否变化
 * @param {Array} list - 订单列表
 * @returns {string} 哈希值
 */
const getListHash = (list) => {
  if (!list || list.length === 0) return '';
  // 使用前几个和最后一个元素的数量值生成简单哈希
  const firstQty = list[0]?.quantity || 0;
  const lastQty = list[list.length - 1]?.quantity || 0;
  const length = list.length;
  return `${length}-${firstQty}-${lastQty}`;
};

// 生成盘口数据（生成足够多的数据，供动态显示使用）
const generateOrderBook = () => {
  const basePrice = lastPrice.value;
  const totalRows = 100; // 生成100行数据，确保有足够的数据填充
  
  // 生成卖单（从高到低）
  const newAsks = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (totalRows - i) * 0.01 + Math.random() * 0.1;
    const quantity = Math.random() * 5 + 0.00001;
    newAsks.push({
      price: basePrice + priceOffset,
      quantity: quantity
    });
  }
  asks.value = newAsks.sort((a, b) => a.price - b.price); // 按价格从低到高排序
  
  // 生成买单（从低到高）
  const newBids = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (i + 1) * 0.01 + Math.random() * 0.1;
    const quantity = Math.random() * 5 + 0.00001;
    newBids.push({
      price: basePrice - priceOffset,
      quantity: quantity
    });
  }
  bids.value = newBids.sort((a, b) => b.price - a.price); // 按价格从高到低排序
};

// 计算可显示的最大行数（根据右侧容器高度）
const calculateMaxRows = () => {
  if (!orderFormRef.value) {
    return 20; // 默认显示20行，避免留白过大
  }
  
  const rightSideHeight = orderFormRef.value.clientHeight;
  const headerHeight = 24; // orderbook-header 高度
  const lastPriceHeight = 32; // last-price 高度
  const rowHeight = 20; // 每行高度
  
  // 可用高度 = 右侧高度 - 盘口头部 - 中间最新价
  // 注意：我们希望左侧总高度和右侧完全一致
  const availableHeight = rightSideHeight - headerHeight - lastPriceHeight;
  
  // 买卖单各占一半高度
  const halfHeight = availableHeight / 2;
  const rowsPerSide = Math.floor(halfHeight / rowHeight);
  
  // 返回单侧应显示的行数，最小显示10行，最大100行
  return Math.max(8, Math.min(12, rowsPerSide));
};

// 动态计算显示的买卖单数量
const displayedAsks = computed(() => {
  // 卖单：取最低的 n 行，并倒序排列（高价在上，低价在下）
  return asks.value.slice(0, 5).reverse();
});

const displayedBids = computed(() => {
  // 买单：取最高的 n 行（高价在上，低价在下）
  return bids.value.slice(0, 5);
});

// 监听窗口大小变化，重新计算行数
const handleResize = () => {
  maxVisibleRows.value = calculateMaxRows();
};

// 使用 ResizeObserver 监听右侧下单区的高度变化
let resizeObserver = null;

// 初始化盘口动态行数计算
const initOrderBookResizeObserver = () => {
  nextTick(() => {
    if (orderFormRef.value) {
      maxVisibleRows.value = calculateMaxRows();
      
      // 使用 ResizeObserver 监听右侧容器高度变化，从而决定左侧显示多少行
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      resizeObserver = new ResizeObserver(() => {
        maxVisibleRows.value = calculateMaxRows();
      });
      resizeObserver.observe(orderFormRef.value);
    }
  });
};

watch(() => route.query.symbol, (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
    // 切换页面时也更新价格
    updatePriceForSymbol(newSymbol);
  }
});

// 监听交易标签页切换，重新计算盘口行数
watch(activeTradeTab, () => {
  nextTick(() => {
    initOrderBookResizeObserver();
  });
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
  
  // 仅在没有真实深度数据时，生成模拟数据作为初始显示
  const realDepth = marketStore.depths[newSymbol];
  if (!realDepth || !realDepth.asks.length) {
  generateOrderBook();
  } else {
    asks.value = [...realDepth.asks];
    bids.value = [...realDepth.bids];
  }

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

// 判断持仓方向是否为多单
const isLongPosition = (position) => {
  const side = position.side?.toLowerCase() || '';
  return side === 'long' || side === 'buy';
};

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
// 格式化资产余额（使用统一的格式化函数，确保小数位正确）
const formatAssetBalance = (value, symbol = '') => {
  // 使用现有的 formatAssetAmount 函数，它已经处理了不同币种的小数位
  return formatAssetAmount(value, symbol);
};

/**
 * 计算订单簿深度条的宽度百分比
 * @param {number} quantity - 当前订单的数量
 * @param {Array} list - 订单列表（asks 或 bids）
 * @param {string} type - 订单类型 ('asks' 或 'bids')
 * @param {Object} options - 可选配置
 * @param {boolean} options.smooth - 是否使用平滑曲线（平方根函数）使视觉效果更自然，默认 true
 * @param {number} options.minWidth - 最小宽度百分比，默认 0
 * @param {number} options.maxWidth - 最大宽度百分比，默认 100
 * @param {boolean} options.useCache - 是否使用缓存，默认 true
 * @returns {number} 深度条宽度百分比 (0-100)
 */
const getDepthWidth = (quantity, list, type, options = {}) => {
  // 参数验证
  if (!list || list.length === 0 || !quantity || quantity <= 0) {
    return options.minWidth || 0;
  }

  // 获取或计算最大数量（使用缓存优化性能）
  let maxQuantity;
  const useCache = options.useCache !== false;
  const listHash = useCache ? getListHash(list) : null;
  const cacheKey = type === 'asks' ? 'asks' : 'bids';
  
  if (useCache && 
      maxQuantityCache[`${cacheKey}ListHash`] === listHash && 
      maxQuantityCache[cacheKey] !== null) {
    // 使用缓存值
    maxQuantity = maxQuantityCache[cacheKey];
  } else {
    // 计算新的最大数量
    maxQuantity = Math.max(...list.map(item => item.quantity || 0));
    
    // 更新缓存
    if (useCache) {
      maxQuantityCache[cacheKey] = maxQuantity;
      maxQuantityCache[`${cacheKey}ListHash`] = listHash;
    }
  }
  
  // 边界情况处理
  if (maxQuantity === 0) {
    return options.minWidth || 0;
  }
  
  if (maxQuantity < quantity) {
    return options.maxWidth || 100;
  }

  // 计算基础比例
  const ratio = quantity / maxQuantity;
  
  // 应用平滑曲线（平方根函数）使视觉效果更自然
  // 这样可以避免小数量订单的深度条过小，同时保持大数量订单的视觉突出
  const smoothRatio = options.smooth !== false ? Math.sqrt(ratio) : ratio;
  
  // 计算百分比宽度
  const width = smoothRatio * 100;
  
  // 应用最小/最大宽度限制
  const minWidth = options.minWidth || 0;
  const maxWidth = options.maxWidth || 100;
  
  return Math.max(minWidth, Math.min(maxWidth, width));
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
      return;
    }
    
    const orderPrice = parseFloat(price.value) || lastPrice.value;
    if (!orderPrice || orderPrice <= 0) {
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
      amount.value = '';
      return; 
    }
    
    const config = currentCoinConfig.value;
    const orderPrice = parseFloat(price.value) || lastPrice.value;
    
    if (!orderPrice || orderPrice <= 0) {
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

// 可用余额：始终显示 USDT 余额（买入时用 USDT，卖出时也需要 USDT 支付手续费）
const formatAvailableBalance = computed(() => {
  const usdtBalance = assetStore?.usdtBalance || 0;
  return formatAssetBalance(usdtBalance, 'USDT') + ' USDT';
});

// 可卖余额：始终显示币种持仓（买入后可以卖币，卖出时也需要有币才能卖）
const formatSellableBalance = computed(() => {
  const coinBalance = assetStore?.getHolding(symbol.value) || 0;
  return formatAssetBalance(coinBalance, symbol.value) + ' ' + symbol.value;
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
      return;
    }
    
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value || markPrice.value);
    if (!orderPrice || orderPrice <= 0) {
      return;
    }
    
    // 基于可用保证金和杠杆计算最大可开仓位
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    
    if (maxAmount <= 0) {
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
      futuresAmount.value = '';
      return;
    }
    
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value || markPrice.value);
    if (!orderPrice || orderPrice <= 0) {
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

// 注意：此函数已废弃，现在直接使用后端返回的 unrealized_pnl
// 保留此函数以防其他地方调用，但不再覆盖后端返回的值
const updatePositionsPnl = () => {
  // 不再重新计算，直接使用后端返回的 unrealized_pnl
  // 只更新百分比（基于后端返回的 PnL）
  positions.value.forEach(position => {
    if (position.margin > 0) {
      position.unrealizedPnlPercent = (position.unrealizedPnl / position.margin) * 100;
    }
  });
};

// 提取后端返回的“真实”错误信息，避免只显示 axios 的 "Request failed with status code 500"
// 优先级：FastAPI detail(字符串) > detail(数组/校验错误) > message > 纯字符串 body > error > 兜底文案
const extractApiError = (error, fallback = '下单失败，请稍后重试') => {
  const data = error?.response?.data;
  if (data) {
    const { detail } = data;
    if (typeof detail === 'string' && detail.trim()) return detail;
    if (Array.isArray(detail) && detail.length) {
      const first = detail[0];
      if (first && first.msg) return first.msg;
      try { return JSON.stringify(detail); } catch { /* ignore */ }
    }
    if (typeof data.message === 'string' && data.message.trim()) return data.message;
    if (typeof data === 'string' && data.trim()) return data;
    if (data.error) return typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
  }
  // 只有在完全拿不到后端信息时才使用兜底文案（不直接暴露 "status code 500"）
  return fallback;
};

// 统一打印下单 payload，方便定位 500 等问题（不吞掉任何信息）
const logOrderPayload = (label, params) => {
  console.groupCollapsed(`📤 [合约下单] ${label}`);
  console.log('side       :', params.side);
  console.log('orderType  :', orderType.value);
  console.log('symbol     :', params.symbol);
  console.log('price      :', params.price, '(', typeof params.price, ')');
  console.log('amount     :', params.amount, '(', typeof params.amount, ')');
  console.log('leverage   :', params.leverage, '(', typeof params.leverage, ')');
  console.log('margin(估) :', futuresMargin.value);
  console.log('marginMode :', marginMode?.value ?? 'ISOLATED');
  console.log('payload    :', JSON.parse(JSON.stringify(params)));
  console.groupEnd();
};

// 统一打印接口错误（完整 status + body），不隐藏后端返回的 message / detail / data
const logOrderError = (label, error) => {
  console.group(`❌ [合约下单失败] ${label}`);
  console.error('HTTP status :', error?.response?.status);
  console.error('后端 body   :', error?.response?.data);
  console.error('原始 error  :', error);
  console.groupEnd();
};

// 提交合约订单（开多 / 开空共用逻辑），side: 'BUY' | 'SELL'
const submitFuturesOrder = async (side, failLabel) => {
  if (!isFuturesFormValid.value) {
    showToast({ message: t('trade.fill_all_fields'), position: 'top', duration: 2000 });
    return;
  }

  isLoading.value = true;

  try {
    const orderPrice = orderType.value === 'market' ? markPrice.value : parseFloat(futuresPrice.value);

    const params = {
      symbol: `${symbol.value}/USDT`,
      side,
      type: orderType.value.toUpperCase(),
      // 市价单也需要传价格给后端（用于估算），但执行价以后端市场价为准
      price: Number(orderPrice) || 0,
      amount: parseFloat(futuresAmount.value),
      leverage: currentLeverage.value
    };

    logOrderPayload(failLabel, params);

    const response = await createFuturesOrder(params);
    const responseData = response.data || response;
    console.log('📥 [合约下单] 接口返回:', responseData);

    if (responseData && responseData.code === 200) {
      showToast({
        message: responseData.message || t('trade.order_submitted'),
        icon: 'success',
        position: 'top',
        duration: 2000
      });

      // 刷新持仓列表和资产余额
      await fetchFuturesPositions();
      await assetStore.initData();

      // 刷新当前委托订单列表（合约）
      console.log('下单成功，正在强制刷新合约委托列表...');
      await fetchFuturesOrders();

      // 清空输入框
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
    } else {
      // 业务失败（HTTP 200 但 code 非 200）：优先显示后端 message
      const bizMessage = responseData?.message || t('trade.order_failed') || '下单失败，请稍后重试';
      showToast({ message: bizMessage, icon: 'fail', position: 'top', duration: 3500 });
    }
  } catch (error) {
    logOrderError(failLabel, error);
    // 顶部轻量提示，优先展示后端真实错误（detail / message），不再只显示 "status code 500"
    const errorMessage = extractApiError(error, t('trade.order_failed') || '下单失败，请稍后重试');
    showToast({ message: errorMessage, icon: 'fail', position: 'top', duration: 3500 });
  } finally {
    isLoading.value = false;
  }
};

const handleLong = () => submitFuturesOrder('BUY', '开多');

const handleShort = () => submitFuturesOrder('SELL', '开空');

const handleTakeProfitStopLoss = (position, index) => {
  currentTPSLPosition.value = { position, index };
  tpSlForm.value.takeProfitPrice = '';
  tpSlForm.value.stopLossPrice = '';
  showTPSLPopup.value = true;
};

const adjustTPSLPrice = (field, step) => {
  const currentVal = parseFloat(tpSlForm.value[field]) || markPrice.value;
  let newVal = currentVal + step;
  
  // 如果是止损价格调整，需要验证是否触及强平线
  if (field === 'stopLossPrice' && currentTPSLPosition.value?.position) {
    const position = currentTPSLPosition.value.position;
    const liquidationPrice = position.liquidationPrice;
    const isLong = position.side === 'long' || position.side === 'LONG';
    
    if (liquidationPrice > 0) {
      // 做多：止损价格必须大于强平价格
      if (isLong && newVal <= liquidationPrice) {
        // 自动修正为强平价 + 0.5%
        newVal = liquidationPrice * 1.005;
      }
      // 做空：止损价格必须小于强平价格
      else if (!isLong && newVal >= liquidationPrice) {
        // 自动修正为强平价 - 0.5%
        newVal = liquidationPrice * 0.995;
      }
    }
  }
  
  // 根据步长增减，保留2位小数
  tpSlForm.value[field] = newVal.toFixed(2);
};

const setTPSLPercentage = (field, percent) => {
  // 基于标记价格快速设置百分比偏移
  const basePrice = markPrice.value;
  let calculatedPrice;
  
  if (field === 'takeProfitPrice') {
    calculatedPrice = basePrice * (1 + percent);
  } else {
    // 止损价格：需要验证是否触及强平线
    calculatedPrice = basePrice * (1 - percent);
    
    // 如果有持仓信息，检查是否触及强平价格
    if (currentTPSLPosition.value?.position) {
      const position = currentTPSLPosition.value.position;
      const liquidationPrice = position.liquidationPrice;
      const isLong = position.side === 'long' || position.side === 'LONG';
      
      if (liquidationPrice > 0) {
        // 做多：止损价格必须大于强平价格
        if (isLong && calculatedPrice <= liquidationPrice) {
          // 自动修正为强平价 + 0.5%（给缓冲空间）
          calculatedPrice = liquidationPrice * 1.005;
        }
        // 做空：止损价格必须小于强平价格
        else if (!isLong && calculatedPrice >= liquidationPrice) {
          // 自动修正为强平价 - 0.5%（给缓冲空间）
          calculatedPrice = liquidationPrice * 0.995;
        }
      }
    }
  }
  
  tpSlForm.value[field] = calculatedPrice.toFixed(2);
};

// 验证止损价格是否合理
const validateStopLossPrice = () => {
  if (!currentTPSLPosition.value?.position) {
    return null; // 没有持仓信息，无法验证
  }
  
  const position = currentTPSLPosition.value.position;
  const liquidationPrice = position.liquidationPrice;
  const stopLossPrice = parseFloat(tpSlForm.value.stopLossPrice);
  
  if (!stopLossPrice || !liquidationPrice || liquidationPrice <= 0) {
    return null; // 没有输入或没有强平价格，无法验证
  }
  
  const isLong = position.side === 'long' || position.side === 'LONG';
  
  // 做多：止损价格必须大于强平价格
  if (isLong && stopLossPrice <= liquidationPrice) {
    return t('trade.stop_loss_above_liquidation', { price: formatPrice(liquidationPrice) }) || 
           `止损价格必须大于强平价格 (强平价: ${formatPrice(liquidationPrice)})`;
  }
  
  // 做空：止损价格必须小于强平价格
  if (!isLong && stopLossPrice >= liquidationPrice) {
    return t('trade.stop_loss_below_liquidation', { price: formatPrice(liquidationPrice) }) || 
           `止损价格必须小于强平价格 (强平价: ${formatPrice(liquidationPrice)})`;
  }
  
  return null; // 验证通过
};

// 计算属性：止损价格错误信息
const stopLossPriceError = computed(() => {
  return validateStopLossPrice();
});

// 计算属性：表单是否有效
const isTPSLFormValid = computed(() => {
  // 至少填写一个价格
  if (!tpSlForm.value.takeProfitPrice && !tpSlForm.value.stopLossPrice) {
    return false;
  }
  
  // 如果填写了止损价格，必须通过验证
  if (tpSlForm.value.stopLossPrice && stopLossPriceError.value) {
    return false;
  }
  
  return true;
});

// 检查止损百分比按钮是否应该禁用
const isStopLossPercentDisabled = (percent) => {
  if (!currentTPSLPosition.value?.position) {
    return false;
  }
  
  const position = currentTPSLPosition.value.position;
  const liquidationPrice = position.liquidationPrice;
  
  if (!liquidationPrice || liquidationPrice <= 0) {
    return false;
  }
  
  const basePrice = markPrice.value;
  const calculatedPrice = basePrice * (1 - percent);
  const isLong = position.side === 'long' || position.side === 'LONG';
  
  // 做多：如果计算出的价格 <= 强平价格，禁用
  if (isLong && calculatedPrice <= liquidationPrice) {
    return true;
  }
  
  // 做空：如果计算出的价格 >= 强平价格，禁用
  if (!isLong && calculatedPrice >= liquidationPrice) {
    return true;
  }
  
  return false;
};

const confirmTPSL = () => {
  if (!isTPSLFormValid.value) {
    if (stopLossPriceError.value) {
      showToast({ 
        message: stopLossPriceError.value, 
        icon: 'fail',
        duration: 3000 
      });
    } else {
      showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    }
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
      confirmButtonColor: 'var(--color-loss)'
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
        
        // 刷新当前委托订单列表（合约）
        console.log('平仓成功，正在强制刷新合约委托列表...');
        await fetchFuturesOrders();
        
        // 刷新历史成交订单列表（合约）
        console.log('[DEBUG] 平仓成功，正在刷新历史成交列表...');
        await fetchFuturesHistory();
        
        console.log('✅ 平仓成功，持仓列表、资产余额、委托列表和历史成交列表已刷新');
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

// 监听标记价格变化，更新未实现盈亏和盘口
watch(markPrice, () => {
  updatePositionsPnl();
  
  // 仅在没有真实深度数据且当前还没有数据时，才生成模拟数据作为填充
  if (!asks.value.length || !bids.value.length) {
    generateOrderBook();
  }
}, { immediate: true });

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
    // 只有当有真实数据时才覆盖，否则保留原有数据（或模拟数据）
    asks.value = [...newDepth.asks];
    bids.value = [...newDepth.bids];
  }
}, { immediate: true, deep: true });

const formatOrderTime = (timestamp) => {
  if (!timestamp) return '';
  // 后端返回的是秒级时间戳（Unix timestamp），需要转换为毫秒级
  // 如果时间戳小于 1e12，说明是秒级，需要乘以 1000
  const timestampMs = timestamp < 1e12 ? timestamp * 1000 : timestamp;
  const date = new Date(timestampMs);
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    console.warn(`[DEBUG] 无效的时间戳: ${timestamp}`);
    return '';
  }
  
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

const scrollToTop = () => { window.scrollTo({ top: 0, behavior: 'smooth' }); };

// 获取当前委托订单列表（合约订单）
// 获取现货当前委托订单列表
const fetchSpotOrders = async () => {
  try {
    const response = await getOrders({ status: 'NEW' });
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 过滤：只显示状态为 NEW、PENDING 或 OPEN 的订单
      const pendingOrders = responseData.data.filter(order => 
        order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
      );
      
      // 映射后端数据格式到前端显示格式
      spotOrdersList.value = pendingOrders.map(order => ({
        order_id: order.order_id,
        side: order.side ? order.side.toLowerCase() : 'buy',
        type: order.type ? order.type.toLowerCase() : 'limit',
        price: order.price || 0,
        quantity: order.quantity || order.amount || 0,
        amount: order.amount || order.quantity || 0,
        symbol: order.symbol ? (order.symbol.includes('/') ? order.symbol.split('/')[0] : order.symbol) : 'BTC',
        timestamp: order.timestamp || order.create_time || Date.now(),
        status: order.status || 'NEW'
      }));
    } else {
      spotOrdersList.value = [];
    }
  } catch (error) {
    console.error('❌ 获取现货订单列表失败:', error);
    spotOrdersList.value = [];
  }
};

// 获取合约当前委托订单列表
const fetchFuturesOrders = async () => {
  try {
    console.log('📤 [DEBUG] 开始获取合约委托订单...');
    const response = await getFuturesOrders({ status: 'NEW' });
    const responseData = response.data || response;
    console.log('📥 [DEBUG] 合约委托订单API返回:', responseData);
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 过滤：只显示状态为 NEW、PENDING 或 OPEN 的订单
      const pendingOrders = responseData.data.filter(order => 
        order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
      );
      
      // 映射后端数据格式到前端显示格式
      futuresOrdersList.value = pendingOrders.map(order => ({
        order_id: order.order_id,
        side: order.side ? order.side.toLowerCase() : 'buy',
        type: order.type ? order.type.toLowerCase() : 'limit',
        price: order.price || 0,
        quantity: order.quantity || order.amount || 0,
        amount: order.amount || order.quantity || 0,
        symbol: order.symbol ? (order.symbol.includes('/') ? order.symbol.split('/')[0] : order.symbol) : 'BTC',
        timestamp: order.timestamp || order.create_time || Date.now(),
        status: order.status || 'NEW'
      }));
      console.log('✅ [DEBUG] 合约委托订单列表已更新，数量:', futuresOrdersList.value.length);
      console.log('✅ [DEBUG] 合约委托订单详情:', futuresOrdersList.value);
    } else {
      futuresOrdersList.value = [];
      console.log('⚠️ [DEBUG] 合约委托订单列表为空');
    }
  } catch (error) {
    console.error('❌ 获取合约订单列表失败:', error);
    futuresOrdersList.value = [];
  }
};

// 获取合约历史成交订单列表（支持分页）
const fetchFuturesHistory = async (isRefresh = false) => {
  // 防止重复加载
  if (historyLoading.value) {
    return;
  }

  try {
    historyLoading.value = true;

    // 刷新时重置状态
    if (isRefresh) {
      futuresHistoryList.value = [];
      historyPage.value = 1;
      historyHasMore.value = true;
    }

    // 计算 skip（偏移量）
    const skip = (historyPage.value - 1) * historyPageSize.value;

    console.log(`📤 [DEBUG] 获取合约历史成交订单 - 页码: ${historyPage.value}, skip: ${skip}, limit: ${historyPageSize.value}`);
    
    const response = await getFuturesOrders({ 
      status: 'HISTORY',
      skip: skip,
      limit: historyPageSize.value
    });
    const responseData = response.data || response;
    console.log('📥 [DEBUG] 合约历史成交订单API返回:', responseData);
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 映射后端数据格式到前端显示格式
      const newOrders = responseData.data.map(order => ({
        order_id: order.order_id,
        side: order.side ? order.side.toLowerCase() : 'buy',
        type: order.type ? order.type.toLowerCase() : 'market',
        price: order.price || 0,
        quantity: order.quantity || order.amount || 0,
        amount: order.amount || order.quantity || 0,
        symbol: order.symbol ? (order.symbol.includes('/') ? order.symbol.split('/')[0] : order.symbol) : 'BTC',
        timestamp: order.timestamp || order.create_time || Date.now(),
        status: order.status || 'FILLED',
        realized_pnl: order.realized_pnl || 0,
        fee: order.fee || 0
      }));

      // 追加数据（刷新时直接替换）
      if (isRefresh) {
        futuresHistoryList.value = newOrders;
      } else {
        futuresHistoryList.value = [...futuresHistoryList.value, ...newOrders];
      }

      // 判断是否还有更多数据
      if (newOrders.length < historyPageSize.value) {
        historyHasMore.value = false;
        console.log('⚠️ [DEBUG] 已加载所有数据，没有更多了');
      } else {
        historyPage.value += 1;  // 页码自增，准备加载下一页
      }

      console.log(`✅ [DEBUG] 合约历史成交订单列表已更新，当前总数: ${futuresHistoryList.value.length}, 本次加载: ${newOrders.length}`);
    } else {
      if (isRefresh) {
        futuresHistoryList.value = [];
      }
      historyHasMore.value = false;
      console.log('⚠️ [DEBUG] 合约历史成交订单列表为空');
    }
  } catch (error) {
    console.error('❌ 获取合约历史成交订单失败:', error);
    if (isRefresh) {
      futuresHistoryList.value = [];
    }
    historyHasMore.value = false;
  } finally {
    historyLoading.value = false;
  }
};

// 初始化历史记录滚动监听（IntersectionObserver）
const initHistoryObserver = () => {
  // 1. 如果已经有了，先断开，防止重复
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }

  // 2. 创建新的观察器
  historyObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      // 核心逻辑：如果底部元素出现了 + 还有更多数据 + 没在加载中
      if (
        entry &&
        entry.isIntersecting &&
        historyHasMore.value &&
        !historyLoading.value
      ) {
        console.log('[DEBUG] 触底了，自动加载下一页...');
        fetchFuturesHistory(false); // false 代表不是刷新，而是追加
      }
    },
    {
      root: null, // 使用视口作为根
      rootMargin: '0px', // 不扩展根边距
      threshold: 0.1 // 当目标元素 10% 可见时触发
    }
  );

  // 3. 开始观察底部元素（使用 nextTick 确保 DOM 已渲染）
  nextTick(() => {
    if (loadMoreTrigger.value) {
      historyObserver.observe(loadMoreTrigger.value);
      console.log('[DEBUG] IntersectionObserver 已初始化并开始监听历史记录列表');
    } else {
      console.warn('[DEBUG] loadMoreTrigger 未找到，无法初始化 IntersectionObserver');
    }
  });
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
      // 映射后端数据格式到前端显示格式（直接使用后端返回的 unrealized_pnl）
      positions.value = responseData.data.map(pos => {
        const margin = pos.margin || (pos.entry_price * pos.size / (pos.leverage || 20));
        const unrealizedPnl = pos.unrealized_pnl || 0;
        const unrealizedPnlPercent = margin > 0 ? (unrealizedPnl / margin) * 100 : 0;
        
        return {
          symbol: pos.symbol?.split('/')[0] || pos.symbol, // "BTC/USDT" -> "BTC"
          side: pos.side?.toLowerCase() || 'long', // LONG -> long, SHORT -> short
          quantity: pos.size || pos.quantity || 0,
          entryPrice: pos.entry_price || 0,
          leverage: pos.leverage || 20,
          margin: margin,
          liquidationPrice: pos.liquidation_price || 0,
          unrealizedPnl: unrealizedPnl, // 直接使用后端返回的值
          unrealizedPnlPercent: unrealizedPnlPercent, // 基于后端 PnL 计算百分比
          markPrice: pos.mark_price || markPrice.value
        };
      });
      
      console.log('✅ 持仓数据（使用后端 PnL）:', positions.value);
      
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

/**
 * ⚠️ 仅开发环境（import.meta.env.DEV）用于预览「持仓卡片」UI 的 mock 数据。
 * - 只有在开发环境 且 真实持仓为空 时才会显示。
 * - 生产环境（打包后 import.meta.env.DEV === false）永远不会显示。
 * - 不覆盖、不污染真实接口数据（positions 仍是唯一真实数据源）。
 */
const DEV_MOCK_POSITION = {
  symbol: 'BTC',            // 模板会拼成 BTCUSDT
  side: 'long',
  quantity: 0.005,
  entryPrice: 108400.00,
  leverage: 20,
  margin: 433.65,
  liquidationPrice: 0,
  unrealizedPnl: 75.18,
  unrealizedPnlPercent: 17.34,
  markPrice: 92000.00,
  __mockPreview: true       // 标记：仅用于本地预览
};

// 持仓列表的“展示层”：真实有数据时用真实数据；仅在开发环境且真实持仓为空时回退到 mock 预览
const displayPositions = computed(() => {
  if (positions.value && positions.value.length > 0) {
    return positions.value;
  }
  if (import.meta.env.DEV) {
    return [DEV_MOCK_POSITION];
  }
  return [];
});

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
      
      // 刷新当前委托订单列表（现货）
      await fetchSpotOrders();

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

const cancelOrder = async (orderId) => {
  // 根据当前 Tab 确定订单类型
  const isSpot = activeTradeTab.value === 'spot';
  
  // 从对应的订单列表中查找订单
  const orderList = isSpot ? spotOrdersList.value : futuresOrdersList.value;
  const order = orderList.find(o => o.order_id === orderId);
  
  if (!order || !order.order_id) {
    showToast({ message: t('trade.order_not_found'), icon: 'fail' });
    return;
  }

  try {
    // 根据当前 Tab 调用对应的撤单接口
    let response;
    if (isSpot) {
      // 现货撤单
      response = await cancelSpotOrderApi(order.order_id);
    } else {
      // 合约撤单
      response = await cancelFuturesOrderApi(order.order_id);
    }
    
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({ 
        message: t('trade.order_cancelled'), 
        icon: 'success',
        duration: 2000 
      });
      
      // 刷新订单列表和资产余额
      if (isSpot) {
        await fetchSpotOrders();
      } else {
        await fetchFuturesOrders();
      }
      await assetStore.initData();
      
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
    // 根据当前 Tab 获取对应的订单列表
    if (activeTradeTab.value === 'spot') {
      await fetchSpotOrders();
    } else {
      await fetchFuturesOrders();
      await fetchFuturesPositions();
    }
  }
};

// 监听 Tab 切换，加载对应的数据（immediate: true 确保初始化时也执行）
watch(activeTradeTab, async (newTab) => {
  if (assetStore.isWalletConnected) {
    if (newTab === 'futures') {
      // 切换到合约 Tab，获取持仓列表和订单列表
      console.log('📤 [DEBUG] watch activeTradeTab: 切换到合约 Tab，刷新订单列表...');
      await fetchFuturesPositions();
      await fetchFuturesOrders();
      await fetchFuturesHistory();
      // 启动定时刷新
      startPositionsRefresh();
    } else if (newTab === 'spot') {
      // 切换到现货 Tab，获取订单列表
      console.log('📤 [DEBUG] watch activeTradeTab: 切换到现货 Tab，刷新订单列表...');
      await fetchSpotOrders();
      // 停止定时刷新（现货不需要）
      stopPositionsRefresh();
    }
  }
}, { immediate: true });

// 监听 forceTradeTab prop 变化（子页面模式）
watch(() => props.forceTradeTab, (newTab) => {
  if (props.isSubPage && newTab && newTab !== activeTradeTab.value) {
    console.log(`📤 [DEBUG] forceTradeTab changed: ${activeTradeTab.value} -> ${newTab}`);
    activeTradeTab.value = newTab;
  }
}, { immediate: true });

// 子页面模式下，禁止手动切换标签页（防止用户通过其他方式切换）
watch(activeTradeTab, (newTab, oldTab) => {
  if (props.isSubPage && props.forceTradeTab && newTab !== props.forceTradeTab) {
    // 如果子页面模式下有 forceTradeTab，但 activeTradeTab 被修改了，恢复为 forceTradeTab
    console.warn(`⚠️ [WARN] 子页面模式下 activeTradeTab 被修改为 ${newTab}，已恢复为 ${props.forceTradeTab}`);
    activeTradeTab.value = props.forceTradeTab;
  }
});

// 监听持仓Tab切换，加载对应的数据
watch(activePositionTab, async (newTab) => {
  if (assetStore.isWalletConnected && activeTradeTab.value === 'futures') {
    if (newTab === 0) {
      // Tab 0: 持仓列表
      await fetchFuturesPositions();
    } else if (newTab === 1) {
      // Tab 1: 当前委托
      await fetchFuturesOrders();
    } else if (newTab === 2) {
      // Tab 2: 历史成交
      console.log('[DEBUG] 切换到历史成交Tab，正在刷新历史成交列表...');
      await fetchFuturesHistory(true);  // 刷新模式
      // 初始化 IntersectionObserver（在 nextTick 中确保 DOM 已渲染）
      await nextTick();
      initHistoryObserver();
    }
  }
});

// 定时刷新持仓数据的定时器
let positionsRefreshTimer = null;

// 启动定时刷新持仓数据
const startPositionsRefresh = () => {
  // 清除旧的定时器（如果存在）
  stopPositionsRefresh();
  
  // 只在合约 Tab 且钱包已连接时刷新
  if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
    positionsRefreshTimer = setInterval(async () => {
      try {
        await fetchFuturesPositions();
        // 同时刷新资产数据（包含未实现盈亏）
        await assetStore.initData();
      } catch (error) {
        console.error('❌ 定时刷新持仓失败:', error);
      }
    }, 5000); // 每5秒刷新一次
  }
};

// 停止定时刷新
const stopPositionsRefresh = () => {
  if (positionsRefreshTimer) {
    clearInterval(positionsRefreshTimer);
    positionsRefreshTimer = null;
  }
};

onMounted(async () => {
  await initializeTrade();
  
  // 子页面模式下，根据 forceTradeTab 加载对应数据
  if (props.isSubPage) {
    if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
      console.log('📤 [DEBUG] onMounted (子页面-合约模式): 加载合约数据...');
      await fetchFuturesPositions();
      await fetchFuturesOrders();
      await fetchFuturesHistory();
      startPositionsRefresh();
    } else if (activeTradeTab.value === 'spot' && assetStore.isWalletConnected) {
      console.log('📤 [DEBUG] onMounted (子页面-现货模式): 加载现货数据...');
      await fetchSpotOrders();
    }
  } else {
    // 主页面模式下，确保合约 Tab 也加载订单列表（如果当前在合约 Tab）
    if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
      console.log('📤 [DEBUG] onMounted: 当前在合约 Tab，强制刷新合约订单列表...');
      await fetchFuturesOrders();
    }
  // 启动定时刷新持仓数据（每5秒）
  startPositionsRefresh();
  }
  
  // 初始化盘口动态行数计算
  initOrderBookResizeObserver();

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);

  // 如果当前在历史成交Tab，初始化 IntersectionObserver（在 nextTick 中确保 DOM 已渲染）
  if (activePositionTab.value === 2) {
    await nextTick();
    initHistoryObserver();
  }
});

// Keep-alive 激活时
onActivated(() => {
  initializeTrade();
  
  // 重新启动定时刷新（防止页面切换时定时器被清除）
  startPositionsRefresh();
  
  // 重新初始化盘口动态行数计算
  initOrderBookResizeObserver();
});

// Keep-alive 停用时
onDeactivated(() => {
  // 组件失活时清除定时器
  stopPositionsRefresh();
  
  // 清理 IntersectionObserver
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
});

// 组件卸载时
onUnmounted(() => {
  // 清理 IntersectionObserver
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
  // 组件卸载时清除定时器
  stopPositionsRefresh();
  
  // 清理 ResizeObserver
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* ========== 全局容器 - Fixed Inset-0 架构 ========== */
.trade-page {
  position: fixed;
  inset: 0; /* top: 0, right: 0, bottom: 0, left: 0 */
  background-color: var(--color-bg); /* 最深黑 */
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
  z-index: 0;
  overflow: hidden; /* 防止整体页面滚动 */
}

/* 可滚动内容区域 - Safe Padding Strategy */
.trade-scrollable-content {
  flex: 1;
  overflow-y: auto; /* 内容区域可滚动 */
  overflow-x: hidden;
  padding-bottom: 128px; /* pb-32 = 128px，防止内容被底部全局导航栏遮挡 */
  scrollbar-width: thin;
  scrollbar-color: rgb(var(--color-brand-rgb) / 0.3) transparent;
}

.trade-scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.trade-scrollable-content::-webkit-scrollbar-track {
  background: transparent;
}

.trade-scrollable-content::-webkit-scrollbar-thumb {
  background: rgb(var(--color-brand-rgb) / 0.3);
  border-radius: 3px;
}

.trade-scrollable-content::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--color-brand-rgb) / 0.5);
}

/* ========== 顶部导航栏 ========== */
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px; /* h-12 = 48px */
  padding: 0 16px;
  background-color: var(--color-bg-card); /* bg-gray-900 */
  flex-shrink: 0; /* 防止被压缩 */
  z-index: 20;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  color: var(--color-text-primary);
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
  fill: var(--color-brand-legacy);
  display: block;
}

/* ========== 标签栏：现货/杠杆 ========== */
.trade-tabs {
  display: flex;
  padding: 0 16px;
  gap: 24px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.trade-tabs .tab-item {
  padding: 12px 0;
  font-size: 14px;
  color: var(--color-text-muted);
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;
}

.trade-tabs .tab-item.active {
  color: var(--color-text-primary);
  font-weight: 600;
}

.trade-tabs .tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-brand-legacy);
}

/* ========== 交易对信息 ========== */
.pair-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.pair-selector { display: flex; align-items: center; cursor: pointer; }
.pair-name { font-size: 16px; font-weight: 700; color: var(--color-text-primary); }
.price-change { font-size: 14px; font-weight: 600; padding: 4px 8px; border-radius: 4px; }
.price-change.positive { color: var(--color-earn); background-color: rgb(var(--color-earn-rgb) / 0.1); }
.price-change.negative { color: var(--color-loss); background-color: rgb(var(--color-loss-rgb) / 0.1); }

/* ========== 核心交易区 - 统一布局结构 ========== */
.trade-main, .futures-trade-main {
  display: flex;
  flex-direction: row;
  gap: 8px; /* gap-2 = 8px */
  padding: 8px; /* p-2 = 8px */
  align-items: flex-start; /* items-start - 确保顶部对齐 */
  /* 使用自然流式布局，不限制高度 */
}

/* ========== 左侧：盘口区 (60%) - 黑金赛博朋克风格 ========== */
.orderbook-side, .futures-orderbook-side {
  width: 60%; /* w-[60%] - 与现货页面一致 */
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, var(--color-bg) 100%);
  border-radius: 8px;
  overflow: visible; /* 允许内容自然显示 */
  padding: 0;
  align-self: flex-start; /* 使用 flex-start，确保高度由内容决定 */
  border: 1px solid rgb(var(--color-brand-rgb) / 0.08);
  box-shadow: 0 0 20px rgb(var(--color-shadow-rgb) / 0.5);
  /* 使用自然高度，显示完整的 15-20 行 */
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 10px;
  color: var(--color-text-secondary);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.03);
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  margin-top: 0; /* 确保顶部对齐 */
}

.header-price { flex: 1; text-align: left; }
.header-quantity { flex: 1; text-align: right; }

.asks-list, .bids-list {
  display: flex;
  flex-direction: column;
  /* 移除 overflow: hidden，允许自然显示所有行 */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.asks-list::-webkit-scrollbar,
.bids-list::-webkit-scrollbar {
  display: none;
}

.order-row {
  position: relative;
  height: 22px;
  line-height: 22px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s ease;
}

.order-row:hover {
  background-color: rgb(var(--color-border-rgb) / 0.02);
}

.depth-bar {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: var(--depth-width, 0%);
  height: 100%;
  z-index: 0;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 赛博朋克红色渐变 - 卖单 */
.ask-depth { 
  background: linear-gradient(to left, 
    rgb(var(--color-loss-rgb) / 0.25) 0%, 
    rgb(var(--color-loss-rgb) / 0.15) 50%,
    rgb(var(--color-loss-rgb) / 0.05) 100%
  );
  box-shadow: inset -2px 0 8px rgb(var(--color-loss-rgb) / 0.2);
}

/* 赛博朋克绿色渐变 - 买单 */
.bid-depth { 
  background: linear-gradient(to left, 
    rgb(var(--color-earn-rgb) / 0.25) 0%, 
    rgb(var(--color-earn-rgb) / 0.15) 50%,
    rgb(var(--color-earn-rgb) / 0.05) 100%
  );
  box-shadow: inset -2px 0 8px rgb(var(--color-earn-rgb) / 0.2);
}

.order-row .price { 
  position: relative; 
  z-index: 1; 
  font-size: 13px; 
  font-weight: 600; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: -0.2px;
}

.ask-price { 
  color: var(--color-loss); 
  text-align: left; 
  flex: 1;
  font-weight: 600;
  text-shadow: 0 0 6px rgb(var(--color-loss-rgb) / 0.4);
}

.bid-price { 
  color: var(--color-earn); 
  text-align: left; 
  flex: 1;
  font-weight: 600;
  text-shadow: 0 0 6px rgb(var(--color-earn-rgb) / 0.4);
}

.order-row .quantity { 
  position: relative; 
  z-index: 1; 
  font-size: 13px; 
  color: var(--color-text-secondary); 
  text-align: right; 
  flex: 1; 
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.last-price {
  flex-shrink: 0;
  height: 48px;
  background: linear-gradient(180deg, rgb(var(--color-brand-rgb) / 0.05) 0%, rgb(var(--color-brand-rgb) / 0.02) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.15);
  border-bottom: 1px solid rgb(var(--color-brand-rgb) / 0.15);
  padding: 0;
  margin: 0;
  position: relative;
}

.last-price::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgb(var(--color-brand-rgb) / 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.price-main { 
  font-size: 20px; 
  font-weight: 800; 
  color: var(--color-text-primary); 
  font-variant-numeric: tabular-nums; 
  line-height: 1.2;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: -0.5px;
  text-shadow: 0 0 12px rgb(var(--color-brand-rgb) / 0.4);
  transition: all 0.3s ease;
}

.price-fiat { 
  font-size: 11px; 
  color: var(--color-text-secondary); 
  font-variant-numeric: tabular-nums; 
  line-height: 1; 
  margin-top: 4px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.last-price.up .price-main { 
  color: var(--color-earn);
  text-shadow: 0 0 12px rgb(var(--color-earn-rgb) / 0.5);
}

.last-price.down .price-main { 
  color: var(--color-loss);
  text-shadow: 0 0 12px rgb(var(--color-loss-rgb) / 0.5);
}

.form-side {
  width: 40%; /* w-[40%] - 与现货页面一致 */
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* 使用自然流式布局，不限制高度 */
}

.buy-sell-toggle {
  display: flex;
  gap: 0;
  background: rgb(var(--color-border-rgb) / 0.03);
  border-radius: 8px;
  padding: 3px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  position: relative;
  margin-top: 0; /* 确保顶部对齐，与 orderbook-header 对齐 */
}

.toggle-btn {
  flex: 1;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--color-text-secondary);
  position: relative;
  z-index: 1;
}

.buy-btn.active { 
  background: linear-gradient(135deg, var(--color-earn) 0%, var(--color-earn) 100%);
  color: var(--color-text-on-accent);
  box-shadow: 0 0 20px rgb(var(--color-earn-rgb) / 0.3), inset 0 1px 0 rgb(var(--color-border-rgb) / 0.2);
  text-shadow: 0 1px 2px rgb(var(--color-shadow-rgb) / 0.3);
}

.sell-btn.active { 
  background: linear-gradient(135deg, var(--color-loss) 0%, var(--color-loss) 100%);
  color: var(--color-text-primary);
  box-shadow: 0 0 20px rgb(var(--color-loss-rgb) / 0.3), inset 0 1px 0 rgb(var(--color-border-rgb) / 0.1);
  text-shadow: 0 1px 2px rgb(var(--color-shadow-rgb) / 0.3);
}

.toggle-btn:not(.active):hover {
  color: var(--color-accent);
}

.order-type-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  padding: 10px 14px;
  background: rgb(var(--color-border-rgb) / 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgb(var(--color-brand-rgb) / 0.15);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  margin-top: 0; /* 确保顶部对齐，与 orderbook-header 对齐 */
}

.order-type-selector:hover {
  background: rgb(var(--color-brand-rgb) / 0.05);
  border-color: rgb(var(--color-brand-rgb) / 0.25);
}

.order-type-selector:active { 
  background: rgb(var(--color-brand-rgb) / 0.08);
  transform: scale(0.98);
}

.leverage-control-bar { margin-bottom: 8px; }
.leverage-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgb(var(--color-border-rgb) / 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgb(var(--color-brand-rgb) / 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.leverage-btn:hover {
  background: rgb(var(--color-brand-rgb) / 0.1);
  border-color: rgb(var(--color-brand-rgb) / 0.3);
  box-shadow: 0 4px 12px rgb(var(--color-brand-rgb) / 0.2);
}

.leverage-btn:active {
  background: rgb(var(--color-brand-rgb) / 0.15);
  transform: scale(0.98);
}

.leverage-value { 
  color: var(--color-accent); 
  font-weight: 800; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.4);
}
.leverage-popup, :deep(.leverage-popup .van-popup) { background: var(--color-bg-card); }
.leverage-popup-content { padding: 20px; height: 100%; display: flex; flex-direction: column; }
.leverage-popup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.leverage-popup-title { font-size: 18px; font-weight: 700; color: var(--color-text-primary); margin: 0; }
.close-icon { font-size: 20px; color: var(--color-text-muted); cursor: pointer; }
.leverage-options { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.leverage-option {
  display: flex; align-items: center; justify-content: space-between; padding: 12px 16px;
  background-color: var(--color-bg-input); border: 1px solid rgb(var(--color-border-rgb) / 0.05); border-radius: 8px;
  font-size: 14px; font-weight: 600; color: var(--color-text-primary); cursor: pointer;
}
.leverage-option.active { background-color: rgb(var(--color-brand-legacy-rgb) / 0.1); border-color: var(--color-brand-legacy); color: var(--color-brand-legacy); }

.input-row {
  display: flex;
  align-items: center;
  background: rgb(var(--color-border-rgb) / 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgb(var(--color-brand-rgb) / 0.15);
  border-radius: 8px;
  padding: 0 14px;
  height: 44px;
  gap: 8px;
  transition: all 0.3s ease;
}

.input-row:focus-within {
  border-color: var(--color-accent);
  background: rgb(var(--color-brand-rgb) / 0.05);
  box-shadow: 
    0 0 20px rgb(var(--color-brand-rgb) / 0.15), 
    inset 0 0 20px rgb(var(--color-brand-rgb) / 0.05),
    inset 0 0 30px rgb(var(--color-brand-rgb) / 0.08); /* 内发光效果 */
}

.input-label { 
  font-size: 12px; 
  color: var(--color-text-secondary); 
  white-space: nowrap; 
  min-width: 80px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.input-field { 
  flex: 1; 
  background: transparent; 
  border: none; 
  color: var(--color-text-primary); 
  font-size: 16px; 
  font-variant-numeric: tabular-nums; 
  outline: none;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-weight: 600;
}

.input-field::placeholder { 
  color: rgb(var(--color-text-muted-rgb) / 0.5);
}

/* 输入框单位标签（后缀） */
.input-suffix {
  font-size: 13px;
  color: var(--color-accent); /* text-yellow-500 / Gold */
  font-weight: 600;
  white-space: nowrap;
  margin-left: 4px;
  opacity: 0.8;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

/* 修复3：隐藏数字输入框默认的上下箭头 */
.no-spinner::-webkit-inner-spin-button,
.no-spinner::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.no-spinner {
  -moz-appearance: textfield;
}

.market-price-input { 
  color: rgb(var(--color-text-muted-rgb) / 0.6) !important; 
  cursor: not-allowed; 
  opacity: 0.6;
  font-style: italic;
}

.estimated-row { 
  display: flex;
  justify-content: space-between; 
  align-items: center;
  padding: 8px 4px; 
  font-size: 11px;
}

.est-label { 
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 600;
  font-size: 10px;
}

.est-value { 
  color: var(--color-text-primary);
  font-weight: 700;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}

/* 滑块容器样式 - 黑金定制 */
.slider-wrapper {
  padding: 16px 8px;
  margin-bottom: 16px;
  position: relative;
}

/* 刻度标签栏 - 交互式节点 */
.slider-marks {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 4px 0;
  margin-top: 8px;
  position: relative;
}

.mark-item {
  font-size: 10px;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  min-width: 36px;
  text-align: center;
  font-weight: 600;
  position: relative;
  background: rgb(var(--color-border-rgb) / 0.02);
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.mark-item:hover {
  color: var(--color-accent);
  background: rgb(var(--color-brand-rgb) / 0.1);
  border-color: rgb(var(--color-brand-rgb) / 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgb(var(--color-brand-rgb) / 0.2);
}

.mark-item:active {
  transform: translateY(0) scale(0.95);
}

/* 自定义滑块按钮样式 - 发光钻石 */
.custom-slider-button {
  width: 28px;
  height: 28px;
  color: var(--color-text-on-accent);
  font-size: 10px;
  line-height: 28px;
  text-align: center;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-strong) 100%);
  border-radius: 50%;
  font-weight: 800;
  box-shadow: 
    0 0 20px rgb(var(--color-brand-rgb) / 0.6),
    0 4px 12px rgb(var(--color-shadow-rgb) / 0.3),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
  border: 2px solid rgb(var(--color-border-rgb) / 0.2);
  transform: scale(1);
  transition: all 0.3s ease;
}

.custom-slider-button:hover {
  transform: scale(1.1);
  box-shadow: 
    0 0 30px rgb(var(--color-brand-rgb) / 0.8),
    0 6px 16px rgb(var(--color-shadow-rgb) / 0.4),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.4);
}

/* Vant Slider 自定义样式 */
:deep(.van-slider) {
  margin: 0;
}

:deep(.van-slider__bar) {
  background: linear-gradient(90deg, var(--color-accent) 0%, rgb(var(--color-brand-rgb) / 0.3) 100%);
  height: 3px;
  border-radius: 2px;
  box-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.4);
}

:deep(.van-slider__track) {
  background: rgb(var(--color-brand-rgb) / 0.1);
  height: 3px;
  border-radius: 2px;
}

/* 保留旧样式以兼容（如果其他地方还在使用） */
.percent-row { display: flex; gap: 8px; }
.percent-btn {
  flex: 1; height: 32px; display: flex; align-items: center; justify-content: center;
  background-color: var(--color-bg-card); border-radius: 4px; font-size: 12px; color: var(--color-text-primary); cursor: pointer;
}
.percent-btn.active { background-color: var(--color-brand-legacy); color: var(--color-text-on-accent); font-weight: 600; }

.fee-estimate-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 10px 14px;
  background: rgb(var(--color-border-rgb) / 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; 
  height: auto; 
  margin-bottom: 8px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.fee-estimate-label { 
  font-size: 11px; 
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.fee-estimate-value { 
  font-size: 13px; 
  color: var(--color-text-primary); 
  font-weight: 700; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  display: flex; 
  align-items: center; 
  gap: 4px;
}

.fee-usdt-note { 
  font-size: 10px; 
  color: var(--color-text-secondary); 
  font-weight: 400; 
  margin-left: 4px;
}

.discount-badge { 
  font-size: 11px; 
  color: var(--color-accent); 
  font-weight: 600;
  text-shadow: 0 0 4px rgb(var(--color-brand-rgb) / 0.4);
}

.total-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 10px 14px;
  background: rgb(var(--color-border-rgb) / 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; 
  height: auto; 
  margin-bottom: 8px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.total-label { 
  font-size: 11px; 
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.total-value { 
  font-size: 14px; 
  color: var(--color-text-primary); 
  font-weight: 700; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.estimated-received-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 14px 16px;
  background: rgb(var(--color-brand-rgb) / 0.06);
  backdrop-filter: blur(10px);
  border-radius: 8px; 
  height: auto; 
  margin-bottom: 16px;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.15);
  box-shadow: 0 0 20px rgb(var(--color-brand-rgb) / 0.1), inset 0 0 20px rgb(var(--color-brand-rgb) / 0.05);
}

.received-label { 
  font-size: 12px; 
  color: rgb(var(--color-brand-rgb) / 0.8); 
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.received-value { 
  font-size: 16px; 
  color: var(--color-accent); 
  font-weight: 800; 
  font-variant-numeric: tabular-nums; 
  letter-spacing: -0.3px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.4);
}

.available-row { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
  padding: 0 4px;
}

.avail-item { 
  display: flex; 
  align-items: center; 
  justify-content: flex-end; 
  font-size: 11px;
  padding: 6px 0;
}

.avail-label { 
  color: var(--color-text-secondary); 
  margin-right: 6px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-size: 10px;
}

.avail-value { 
  color: var(--color-text-primary); 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-weight: 700;
  font-size: 12px;
}

/* 可用余额行 - 移到按钮上方，更易读 */
.available-balance-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  margin-top: 8px;
  margin-bottom: 0;
}

.available-balance-label {
  font-size: 12px;
  color: var(--color-text-secondary); /* Grey */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.available-balance-value {
  font-size: 15px;
  color: var(--color-text-primary); /* Bright White/Gold */
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.3); /* 轻微金色发光 */
}

.submit-btn {
  width: 100%; 
  height: 48px; 
  border: none; 
  border-radius: 8px; 
  font-size: 16px; 
  font-weight: 800;
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgb(var(--color-border-rgb) / 0.2), transparent);
  transition: left 0.5s ease;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn.buy { 
  background: var(--color-brand);
  color: var(--color-text-on-accent);
  box-shadow: 0 4px 16px rgb(var(--color-brand-rgb) / 0.25);
}

.submit-btn.buy:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgb(var(--color-brand-rgb) / 0.35);
  transform: translateY(-2px);
}

.submit-btn.sell { 
  background: var(--color-loss);
  color: var(--color-text-primary);
  box-shadow: 0 4px 16px rgb(var(--color-loss-rgb) / 0.25);
}

.submit-btn.sell:hover:not(:disabled) {
  box-shadow: 0 6px 30px rgb(var(--color-loss-rgb) / 0.5), inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
  transform: translateY(-2px);
}

.submit-btn:disabled { 
  opacity: 0.4; 
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.submit-btn:active:not(:disabled) { 
  transform: translateY(0) scale(0.98);
}

/* ========== 底部：委托与资产 - 自然流式布局 ========== */
.bottom-section { 
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  box-shadow: 0 -4px 20px rgb(var(--color-shadow-rgb) / 0.5);
  display: flex;
  flex-direction: column;
  margin-top: 8px; /* mt-2 = 8px，与交易表单的间距 */
  padding: 0 8px; /* px-2 = 8px */
  /* 使用自然流式布局，不限制高度 */
}

.bottom-tabs { 
  display: flex; 
  padding: 8px 16px; 
  gap: 32px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  flex-shrink: 0; /* 防止被压缩 */
  position: sticky;
  top: 0;
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  z-index: 10;
  backdrop-filter: blur(10px);
}

.bottom-tabs .tab-item {
  font-size: 14px; 
  color: var(--color-text-secondary); 
  cursor: pointer; 
  padding-bottom: 8px; 
  position: relative; 
  transition: all 0.3s ease;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.bottom-tabs .tab-item:hover {
  color: rgb(var(--color-brand-rgb) / 0.7);
}

.bottom-tabs .tab-item.active { 
  color: var(--color-accent); 
  font-weight: 700;
}

.bottom-tabs .tab-item.active::after {
  content: ''; 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  right: 0; 
  height: 3px; 
  background: linear-gradient(90deg, var(--color-accent) 0%, var(--color-accent-strong) 100%);
  box-shadow: 0 0 12px rgb(var(--color-brand-rgb) / 0.6);
  border-radius: 2px 2px 0 0;
}

.bottom-content {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.98) 0%, var(--color-bg) 100%);
  /* 移除固定高度和 overflow，使用自然流式布局 */
}

.panel-full {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  width: 100%;
}

.orders-panel, .assets-panel { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  min-height: 60px; /* 确保有最小高度 */
  width: 100%;
  overflow: visible; /* 确保内容可见 */
}

/* ========== 紧凑订单列表 - 固定高度滚动 ========== */
.orders-list-compact { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
  min-height: 60px; /* 确保有最小高度 */
  max-height: 200px; /* 增加最大高度，显示更多订单 */
  overflow-y: auto; /* 内部滚动 */
  overflow-x: hidden;
  padding: 4px 4px 4px 0; /* 为滚动条留出空间 */
  scrollbar-width: none; /* Firefox 隐藏滚动条 */
  -ms-overflow-style: none; /* IE/Edge 隐藏滚动条 */
}

.orders-list-compact::-webkit-scrollbar {
  display: none; /* Chrome/Safari 隐藏滚动条 */
}

.orders-empty-compact {
  display: flex; 
  align-items: center; 
  justify-content: center;
  height: 60px; /* 紧凑的空状态高度 */
  padding: 0;
}

.empty-text-compact {
  font-size: 12px; 
  color: var(--color-text-secondary); 
  font-weight: 500;
}

/* 紧凑空状态样式已在上面定义 */

.order-item {
  display: flex; 
  align-items: center; 
  padding: 10px 12px; /* 减少内边距，更紧凑 */
  background: rgb(var(--color-border-rgb) / 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; /* 更小的圆角 */
  border: 1px solid rgb(var(--color-brand-rgb) / 0.1); 
  transition: all 0.2s ease;
  flex-shrink: 0; /* 防止压缩 */
}

.order-item:hover {
  background: rgb(var(--color-brand-rgb) / 0.05);
  border-color: rgb(var(--color-brand-rgb) / 0.2);
}

.order-item:active { 
  background: rgb(var(--color-brand-rgb) / 0.08);
}

.order-left { 
  display: flex;
  align-items: center;
  gap: 8px; 
  flex: 0 0 auto; 
  min-width: 100px; /* 稍微减小 */
}

.order-side-badge { 
  padding: 3px 6px; /* 更紧凑 */
  border-radius: 4px; 
  font-size: 10px; /* 更小字体 */
  font-weight: 700; 
  white-space: nowrap; 
}

.order-side-badge.buy { 
  background-color: rgb(var(--color-earn-rgb) / 0.15); 
  color: var(--color-earn); 
}

.order-side-badge.sell { 
  background-color: rgb(var(--color-loss-rgb) / 0.15); 
  color: var(--color-loss); 
}

/* 强平订单标签样式 - 醒目的红色标签 */
.liquidation-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background-color: rgb(var(--color-loss-rgb) / 0.2); /* bg-red-500/20 - 浅红色背景 */
  color: var(--color-loss); /* text-red-500 - 鲜艳的红色 */
  border: 1px solid rgb(var(--color-loss-rgb) / 0.3); /* 细红线边框 */
  box-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.2);
}

/* 强平订单整体样式 */
.order-item.liquidation-order {
  border-left: 3px solid var(--color-loss); /* 左侧红色边框标识 */
  background-color: rgb(var(--color-loss-rgb) / 0.05); /* 轻微红色背景 */
}

/* 强平订单的已实现盈亏样式 - 巨额负数红色加粗 */
.order-pnl.pnl-liquidation {
  font-weight: 900;
  font-size: 14px;
  color: var(--color-loss) !important; /* 强制红色 */
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.5);
}

.order-pnl.pnl-liquidation.pnl-negative {
  color: var(--color-loss) !important; /* text-red-600 - 更深的红色 */
  font-weight: 900;
  text-shadow: 
    0 0 10px rgb(var(--color-loss-rgb) / 0.6),
    0 0 20px rgb(var(--color-loss-rgb) / 0.3);
}

.order-symbol-time { 
  display: flex; 
  flex-direction: column; 
  gap: 2px; /* 更紧凑 */
}

.order-symbol { 
  font-size: 12px; /* 更小 */
  font-weight: 700; 
  color: var(--color-text-primary); 
}

.order-time { 
  font-size: 10px; /* 更小 */
  color: var(--color-text-secondary); 
  font-family: 'DIN Alternate', monospace; 
}

.order-center { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  gap: 2px; /* 更紧凑 */
  padding: 0 10px; 
  min-width: 0; 
}

.order-price { 
  font-size: 13px; /* 更小 */
  font-weight: 700; 
  color: var(--color-text-primary); 
  font-family: 'DIN Alternate', monospace; 
}

.order-quantity { 
  font-size: 11px; /* 更小 */
  color: var(--color-text-secondary); 
  font-family: 'DIN Alternate', monospace; 
}

.order-right { 
  flex: 0 0 auto;
}

/* ========== 历史成交列表 Pro Max 布局 ========== */
.history-order-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 16px;
  gap: 16px;
}

/* 左侧：操作详情 */
.history-order-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0; /* 允许收缩 */
}

.history-order-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.history-order-symbol {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

.history-order-details {
  display: flex;
  align-items: center;
}

.history-order-price-quantity {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}

/* 右侧：核心结果（盈亏 + 时间） */
.history-order-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-start;
  gap: 4px;
  flex-shrink: 0;
  min-width: 120px; /* 确保有足够空间显示盈亏 */
}

.history-order-pnl {
  font-size: 16px; /* text-base - 大字号 */
  font-weight: 800; /* font-bold - 加粗 */
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-align: right;
  line-height: 1.2;
}

.history-order-pnl.pnl-positive {
  color: var(--color-earn); /* 正数绿色 */
}

.history-order-pnl.pnl-negative {
  color: var(--color-loss); /* 负数红色 */
}

.history-order-pnl.pnl-zero {
  color: var(--color-text-secondary); /* 0 显示灰色 */
  font-weight: 600;
}

.history-order-pnl.pnl-liquidation {
  color: var(--color-loss) !important;
  font-weight: 900;
  font-size: 17px; /* 强平订单更大字号 */
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.5);
}

.history-order-pnl.pnl-liquidation.pnl-negative {
  color: var(--color-loss) !important;
  text-shadow: 
    0 0 10px rgb(var(--color-loss-rgb) / 0.6),
    0 0 20px rgb(var(--color-loss-rgb) / 0.3);
}

.history-order-time {
  font-size: 10px; /* text-xs */
  color: var(--color-text-secondary); /* text-gray-500 */
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-align: right;
  white-space: nowrap;
}

/* IntersectionObserver 监听目标（触底锚点） */
.history-observer-target {
  height: 1px;
  width: 100%;
  flex-shrink: 0;
}

/* 底部状态栏 */
.history-footer {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

/* 加载中状态 */
.history-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--color-accent);
}

.loading-text {
  font-size: 12px;
  color: var(--color-accent);
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 没有更多数据状态 */
.history-no-more {
  font-size: 10px; /* text-xs */
  color: var(--color-text-muted); /* text-gray-600 */
  text-align: center;
  padding: 16px 0;
  letter-spacing: 0.3px; /* tracking-wider */
  font-weight: 500;
  opacity: 0.7;
}

.cancel-btn { 
  padding: 5px 12px; /* 更紧凑 */
  background: rgb(var(--color-loss-rgb) / 0.1); 
  color: var(--color-loss); 
  border: 1px solid rgb(var(--color-loss-rgb) / 0.2); 
  border-radius: 6px; 
  font-size: 11px; /* 更小 */
  font-weight: 600; 
  transition: all 0.2s ease;
  cursor: pointer;
}

.cancel-btn:hover {
  background: rgb(var(--color-loss-rgb) / 0.15);
  border-color: rgb(var(--color-loss-rgb) / 0.3);
}

.cancel-btn:active { 
  background: rgb(var(--color-loss-rgb) / 0.2); 
}

/* ========== 资产玻璃拟态卡片 ========== */
.assets-glass-card {
  background: rgb(var(--color-border-rgb) / 0.05); /* bg-white/5 */
  border-radius: 12px; /* rounded-xl */
  padding: 16px; /* p-4 */
  margin-top: 16px; /* mt-4 */
  border: 1px solid rgb(var(--color-border-rgb) / 0.1); /* border border-white/10 */
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgb(var(--color-shadow-rgb) / 0.3);
}

/* ========== 紧凑资产 HUD 条 - 单行水平布局 ========== */
.assets-hud-strip {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  height: 48px; /* 固定高度，非常紧凑 */
  padding: 0;
  background: transparent; /* 透明背景 */
}

.asset-hud-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex: 1;
  padding: 0 12px;
}

.asset-hud-divider {
  width: 1px;
  height: 24px;
  background: rgb(var(--color-brand-rgb) / 0.15);
  flex-shrink: 0;
}

.asset-hud-label { 
  font-size: 10px; /* 非常小的标签 */
  color: var(--color-text-secondary); 
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1;
}

.asset-hud-value { 
  font-size: 14px; /* 适中大小的数值 */
  font-weight: 800; 
  color: var(--color-accent); 
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 6px rgb(var(--color-brand-rgb) / 0.3);
  letter-spacing: -0.2px;
  line-height: 1.2;
  white-space: nowrap;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.coin-select-popup { 
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%) !important;
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
}

.coin-select-container { 
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  background: transparent;
}

.coin-select-header { 
  padding: 20px 16px 16px; 
  border-bottom: 1px solid rgb(var(--color-brand-rgb) / 0.1); 
  flex-shrink: 0;
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, transparent 100%);
}

.coin-select-title { 
  font-size: 18px; 
  font-weight: 800; 
  color: var(--color-accent); 
  margin: 0; 
  text-align: left;
  text-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.3);
}

.coin-list { 
  flex: 1; 
  overflow-y: auto; 
  padding: 0;
  scrollbar-width: thin;
  scrollbar-color: rgb(var(--color-brand-rgb) / 0.3) transparent;
}

.coin-list::-webkit-scrollbar {
  width: 6px;
}

.coin-list::-webkit-scrollbar-track {
  background: transparent;
}

.coin-list::-webkit-scrollbar-thumb {
  background: rgb(var(--color-brand-rgb) / 0.3);
  border-radius: 3px;
}

.coin-list::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--color-brand-rgb) / 0.5);
}

.coin-item { 
  padding: 16px; 
  display: flex; 
  flex-direction: row;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05); 
  cursor: pointer; 
  transition: all 0.3s ease;
  position: relative;
}

.coin-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--color-accent) 0%, var(--color-accent-strong) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.coin-item:hover {
  background: rgb(var(--color-brand-rgb) / 0.05);
}

.coin-item:active { 
  background: rgb(var(--color-brand-rgb) / 0.08);
}

.coin-item-active { 
  background: rgb(var(--color-brand-rgb) / 0.08);
  border-left: 3px solid var(--color-accent);
}

.coin-item-active::before {
  opacity: 1;
}

.coin-name { 
  font-size: 16px; 
  font-weight: 700; 
  color: var(--color-text-primary); 
  margin: 0;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.coin-item-active .coin-name {
  color: var(--color-accent);
  text-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.4);
}

.coin-pair { 
  font-size: 12px; 
  color: var(--color-text-secondary); 
  margin-top: 6px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}
:deep(.van-empty__description) { color: var(--color-text-muted); font-size: 12px; }

/* 修复3：ActionSheet 黑金风格 */
.custom-action-sheet {
  --van-action-sheet-background: var(--color-bg-card);
  --van-action-sheet-item-background: var(--color-bg-card);
  --van-action-sheet-item-text-color: var(--color-text-primary);
  --van-action-sheet-cancel-padding-top: 8px;
  --van-action-sheet-cancel-padding-color: var(--color-bg);
  --van-popup-background: var(--color-bg-card);
}

:deep(.van-action-sheet__item), :deep(.van-action-sheet__cancel) {
  background-color: var(--color-bg-card);
  color: var(--color-text-primary);
}

:deep(.van-action-sheet__item:active), :deep(.van-action-sheet__cancel:active) {
  background-color: var(--color-surface-muted);
}

:deep(.van-action-sheet__gap) {
  background-color: var(--color-bg);
  height: 8px;
}

:deep(.van-action-sheet__header) {
  background-color: var(--color-bg-card);
  color: var(--color-text-primary);
  font-weight: 700;
}

/* ========== 合约交易样式 - 自然流式布局 ========== */
.futures-trade-container {
  display: flex;
  flex-direction: column;
  /* 移除固定高度和 overflow，使用自然流式布局 */
}

/* 顶部控制栏 - 与现货页面的 pair-info 高度完全一致 */
.futures-control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px; /* 与 pair-info 完全一致 */
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, var(--color-bg) 100%);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05); /* 与 pair-info 一致 */
  gap: 12px;
  box-sizing: border-box;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.margin-mode-text {
  font-size: 12px;
  color: rgb(var(--color-brand-rgb) / 0.8);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.control-right {
  display: flex;
  align-items: center;
}

.funding-rate-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  padding: 8px 12px;
  background: rgb(var(--color-border-rgb) / 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.1);
}

.funding-rate-label {
  font-size: 10px;
  color: var(--color-text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.funding-rate-value {
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.funding-rate-value.positive {
  color: var(--color-earn);
  text-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.4);
}

.funding-rate-value.negative {
  color: var(--color-loss);
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.4);
}

/* 中间交易区域 - 自然流式布局 */
.futures-trade-main {
  display: flex;
  gap: 8px;
  padding: 8px 8px 8px 0;
  align-items: flex-start;
  /* 移除固定高度和 overflow，使用自然流式布局 */
}

/* 合约盘口样式已与现货共享，无需重复定义 */

/* 资产信息面板 */
.futures-asset-panel {
  background: rgb(var(--color-bg-rgb) / 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgb(var(--color-border-rgb) / 0.08);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  font-size: 11px;
}

.asset-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 8px;
}

.asset-row:last-child {
  margin-bottom: 0;
}

.asset-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.asset-label {
  color: var(--color-text-secondary);
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.asset-value {
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.asset-value.pnl-positive {
  color: var(--color-earn);
}

.asset-value.pnl-negative {
  color: var(--color-loss);
}

.asset-value.pnl-flash {
  animation: pnl-flash 0.3s ease-in-out;
}

@keyframes pnl-flash {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
    transform: scale(1.05);
  }
}

.futures-form-side {
  width: 40%; /* w-[40%] - 与现货页面一致 */
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* 使用自然流式布局，不限制高度 */
}

.futures-action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
  padding-top: 16px;
}

/* 合约页面按钮 - Grid 布局，确保总高度与现货页面一致 */
.futures-action-buttons-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* grid-cols-2 */
  gap: 8px; /* gap-2 = 8px */
  margin-top: 16px; /* mt-4 = 16px */
  padding-top: 16px;
}

.long-btn, .short-btn {
  width: 100%;
  height: 52px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
}

.long-btn::before, .short-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgb(var(--color-border-rgb) / 0.2), transparent);
  transition: left 0.5s ease;
}

.long-btn:hover::before, .short-btn:hover::before {
  left: 100%;
}

/* 开多按钮 - 霓虹绿色渐变 */
.long-btn {
  background: linear-gradient(135deg, var(--color-earn) 0%, var(--color-earn) 50%, var(--color-earn) 100%);
  color: var(--color-text-on-accent);
  box-shadow: 
    0 4px 20px rgb(var(--color-earn-rgb) / 0.4),
    0 0 30px rgb(var(--color-earn-rgb) / 0.2),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
  text-shadow: 0 1px 2px rgb(var(--color-shadow-rgb) / 0.3);
}

.long-btn:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgb(var(--color-earn-rgb) / 0.6),
    0 0 40px rgb(var(--color-earn-rgb) / 0.3),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.4);
  transform: translateY(-2px);
}

.long-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

/* 开空按钮 - 霓虹红色渐变 */
.short-btn {
  background: linear-gradient(135deg, var(--color-loss) 0%, var(--color-loss) 50%, var(--color-loss) 100%);
  color: var(--color-text-primary);
  box-shadow: 
    0 4px 20px rgb(var(--color-loss-rgb) / 0.4),
    0 0 30px rgb(var(--color-loss-rgb) / 0.2),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.2);
  text-shadow: 0 1px 2px rgb(var(--color-shadow-rgb) / 0.3);
}

.short-btn:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgb(var(--color-loss-rgb) / 0.6),
    0 0 40px rgb(var(--color-loss-rgb) / 0.3),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
  transform: translateY(-2px);
}

.short-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.long-btn:disabled, .short-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.5);
  box-shadow: none;
}

/* Grid 布局按钮样式 - 确保总高度与现货页面单个按钮一致（48px） */
.long-btn-grid, .short-btn-grid {
  width: 100%;
  height: 48px; /* 与现货页面 submit-btn 高度一致 */
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
}

.long-btn-grid::before, .short-btn-grid::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgb(var(--color-border-rgb) / 0.2), transparent);
  transition: left 0.5s ease;
}

.long-btn-grid:hover::before, .short-btn-grid:hover::before {
  left: 100%;
}

/* 开多按钮 - Grid 版本 - 霓虹绿色渐变 */
.long-btn-grid {
  background: linear-gradient(to right, var(--color-earn) 0%, var(--color-earn) 100%); /* emerald-500 to green-600 */
  color: var(--color-text-primary);
  font-weight: 800;
  box-shadow: 
    0 4px 20px rgb(var(--color-earn-rgb) / 0.3), /* shadow-lg shadow-green-500/30 */
    0 0 30px rgb(var(--color-earn-rgb) / 0.15),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.2);
  text-shadow: 0 1px 2px rgb(var(--color-shadow-rgb) / 0.3);
}
.long-btn-grid:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgb(var(--color-earn-rgb) / 0.5),
    0 0 40px rgb(var(--color-earn-rgb) / 0.25),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
  transform: translateY(-2px);
}

.long-btn-grid:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

/* 开空按钮 - Grid 版本 - 霓虹红色渐变 */
.short-btn-grid {
  background: linear-gradient(to right, var(--color-loss) 0%, var(--color-loss) 100%); /* rose-500 to red-600 */
  color: var(--color-text-primary);
  font-weight: 800;
  box-shadow: 
    0 4px 20px rgb(var(--color-loss-rgb) / 0.3), /* shadow-lg shadow-red-500/30 */
    0 0 30px rgb(var(--color-loss-rgb) / 0.15),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.2);
  text-shadow: 0 1px 2px rgb(var(--color-shadow-rgb) / 0.3);
}

.short-btn-grid:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgb(var(--color-loss-rgb) / 0.5),
    0 0 40px rgb(var(--color-loss-rgb) / 0.25),
    inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
  transform: translateY(-2px);
}

.short-btn-grid:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.long-btn-grid:disabled, .short-btn-grid:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.5);
  box-shadow: none;
}

/* 底部面板 - 自然流式布局 */
.futures-bottom-section {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  box-shadow: 0 -4px 20px rgb(var(--color-shadow-rgb) / 0.5);
  display: flex;
  flex-direction: column;
  margin-top: 8px; /* mt-2 = 8px，与交易表单的间距 */
  padding: 0 8px; /* px-2 = 8px */
  /* 使用自然流式布局，不限制高度 */
}

.position-tabs {
  display: flex;
  flex-direction: column;
  /* 移除固定高度和 overflow，使用自然流式布局 */
}

:deep(.position-tabs .van-tabs__wrap) {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  flex-shrink: 0; /* 防止被压缩 */
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
  height: 48px; /* 固定标签栏高度 */
  padding: 8px 16px; /* 与现货页面一致 */
}

/* 统一标签页样式，与现货页面一致 */
:deep(.position-tabs .van-tab) {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-bottom: 8px;
  transition: all 0.3s ease;
}

:deep(.position-tabs .van-tab--active) {
  color: var(--color-accent);
  font-weight: 700;
}

:deep(.position-tabs .van-tabs__line) {
  background: linear-gradient(90deg, var(--color-accent) 0%, var(--color-accent-strong) 100%);
  box-shadow: 0 0 12px rgb(var(--color-brand-rgb) / 0.6);
  border-radius: 2px 2px 0 0;
  height: 3px;
}

:deep(.position-tabs .van-tabs__content) {
  /* 移除固定高度和 overflow，使用自然流式布局 */
  position: relative;
}

:deep(.position-tabs .van-tab__panel) {
  width: 100%;
  /* 移除固定高度和 overflow，使用自然流式布局 */
  transition: opacity 0.2s ease;
}

:deep(.position-tabs .van-tab__panel::-webkit-scrollbar) {
  width: 6px;
}

:deep(.position-tabs .van-tab__panel::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.position-tabs .van-tab__panel::-webkit-scrollbar-thumb) {
  background: rgb(var(--color-brand-rgb) / 0.3);
  border-radius: 3px;
}

:deep(.position-tabs .van-tab__panel::-webkit-scrollbar-thumb:hover) {
  background: rgb(var(--color-brand-rgb) / 0.5);
}

.positions-list, .orders-list, .history-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 20px;
  box-sizing: border-box;
  /* 使用自然流式布局，不限制高度 */
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px; /* 最小高度，确保空状态可见 */
  padding: 40px 20px;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
  width: 100%;
  box-sizing: border-box;
}

.empty-state .empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
  filter: drop-shadow(0 0 8px rgb(var(--color-brand-rgb) / 0.2));
}

.empty-state .empty-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.position-card {
  background: rgb(var(--color-border-rgb) / 0.05); /* bg-white/5 - 玻璃拟态效果 */
  backdrop-filter: blur(16px); /* backdrop-blur-md */
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.1); /* border-white/10 */
  box-shadow: 0 4px 20px rgb(var(--color-shadow-rgb) / 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.position-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgb(var(--color-brand-rgb) / 0.3), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.position-card:hover {
  background: rgb(var(--color-brand-rgb) / 0.05);
  border-color: rgb(var(--color-brand-rgb) / 0.25);
  box-shadow: 0 8px 32px rgb(var(--color-shadow-rgb) / 0.4);
  transform: translateY(-2px);
}

.position-card:hover::before {
  opacity: 1;
}

.position-card-main {
  display: grid;
  grid-template-columns: 1fr 1.8fr 1fr;
  gap: 20px;
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

/* 持仓方向标签 - 多/空 */
.position-side-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.position-side-badge.side-long {
  background-color: rgb(var(--color-border-rgb) / 0.08);
  color: var(--color-earn);
  box-shadow: none;
}

.position-side-badge.side-short {
  background-color: rgb(var(--color-border-rgb) / 0.08);
  color: var(--color-loss);
  box-shadow: none;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.unrealized-pnl-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.unrealized-pnl-value {
  font-size: 32px; /* text-3xl - 更大更醒目 */
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  margin-bottom: 8px;
  line-height: 1.1;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: -0.5px;
}

.unrealized-pnl-value.positive {
  color: var(--color-earn);
  text-shadow: 
    0 0 20px rgb(var(--color-earn-rgb) / 0.6),
    0 0 40px rgb(var(--color-earn-rgb) / 0.3);
}

.unrealized-pnl-value.negative {
  color: var(--color-loss);
  text-shadow: 
    0 0 20px rgb(var(--color-loss-rgb) / 0.6),
    0 0 40px rgb(var(--color-loss-rgb) / 0.3);
}

.unrealized-pnl-percent {
  font-size: 17px;
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
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 16px;
  align-content: start;
}

.position-info-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

/* 开仓均价颜色 - 根据方向变化 */
.entry-price-value.side-long {
  color: var(--color-earn); /* 多单绿色 */
  text-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.4);
}

.entry-price-value.side-short {
  color: var(--color-loss); /* 空单红色 */
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.4);
}

.liquidation-price {
  color: var(--color-loss);
  font-weight: 800;
  font-size: 14px;
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.4);
}

.position-actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
}

.action-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.tp-sl-btn {
  background: rgb(var(--color-brand-rgb) / 0.1);
  color: var(--color-accent);
  border: 1px solid rgb(var(--color-brand-rgb) / 0.3);
  backdrop-filter: blur(10px);
}

.tp-sl-btn:hover {
  background: rgb(var(--color-brand-rgb) / 0.15);
  border-color: rgb(var(--color-brand-rgb) / 0.4);
  box-shadow: 0 4px 12px rgb(var(--color-brand-rgb) / 0.2);
  transform: translateY(-2px);
}

.tp-sl-btn:active {
  background: rgb(var(--color-brand-rgb) / 0.2);
  transform: translateY(0);
}

.close-btn {
  background: rgb(var(--color-loss-rgb) / 0.1);
  color: var(--color-loss);
  border: 1px solid rgb(var(--color-loss-rgb) / 0.3);
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgb(var(--color-loss-rgb) / 0.15);
  border-color: rgb(var(--color-loss-rgb) / 0.4);
  box-shadow: 0 4px 12px rgb(var(--color-loss-rgb) / 0.2);
  transform: translateY(-2px);
}

.close-btn:active {
  background: rgb(var(--color-loss-rgb) / 0.2);
  transform: translateY(0);
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

.premium-gold-button.disabled {
  background: rgb(var(--color-border-rgb) / 0.1);
  color: rgb(var(--color-border-rgb) / 0.3);
  cursor: not-allowed;
  filter: none;
}

.premium-gold-button.disabled:active {
  transform: none;
}

/* 错误提示样式 */
.tpsl-error-message {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-loss);
  font-weight: 600;
  padding: 8px 12px;
  background: rgb(var(--color-loss-rgb) / 0.1);
  border-radius: 6px;
  border-left: 3px solid var(--color-loss);
}

/* 输入框错误状态 */
.input-error {
  border-color: var(--color-loss) !important;
  background: rgb(var(--color-loss-rgb) / 0.05) !important;
}

/* 百分比按钮禁用状态 */
.percent-tag.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
  background: rgb(var(--color-border-rgb) / 0.05) !important;
  color: rgb(var(--color-border-rgb) / 0.3) !important;
}

/* Compact viewport tuning */
.orderbook-header { padding: 5px 10px !important; min-height: 22px !important; }
.order-row { height: 18px !important; line-height: 18px !important; padding: 0 10px !important; }
.order-row .price,
.order-row .quantity { font-size: 12px !important; line-height: 18px !important; }
.last-price { height: 40px !important; min-height: 40px !important; }
.price-main { font-size: 18px !important; line-height: 1.1 !important; }
.price-fiat { font-size: 10px !important; }
.right-form-panel,
.right-trade-form,
.form-side,
.futures-form-side { gap: 6px !important; padding: 6px !important; }
.toggle-btn { height: 36px !important; font-size: 14px !important; }
.order-type-selector { min-height: 42px !important; padding: 8px 12px !important; }
.input-row { min-height: 42px !important; height: 42px !important; padding: 0 12px !important; }
.estimated-row { padding: 4px !important; }
.slider-wrapper { padding: 10px 8px 6px !important; margin-bottom: 6px !important; }
.slider-marks { padding-top: 6px !important; margin-top: 4px !important; }
.mark-item { padding: 4px 6px !important; min-width: 28px !important; }
.fee-estimate-row,
.total-row,
.estimated-received-row { padding: 8px 12px !important; margin-bottom: 6px !important; }
.available-row { gap: 2px !important; padding: 6px 10px !important; }
.avail-item { padding: 3px 0 !important; }
.submit-btn { height: 44px !important; min-height: 44px !important; }

/* Premium compact futures terminal polish */
.futures-trade-container {
  background: #f5f6f8 !important;
}

.futures-control-bar {
  margin: 0 12px 8px !important;
  padding: 8px 10px !important;
  min-height: 42px !important;
  border-radius: 14px !important;
  background: #ffffff !important;
  border: 1px solid #eaecef !important;
  box-shadow: 0 2px 8px rgb(17 24 39 / 0.04) !important;
}

.control-left {
  gap: 8px !important;
  min-width: 0 !important;
}

.margin-mode-text {
  color: #c99400 !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  white-space: nowrap !important;
}

.funding-rate-info {
  min-width: 94px !important;
  padding: 0 !important;
  background: transparent !important;
  border: 0 !important;
  text-align: right !important;
}

.funding-rate-label {
  color: #6b7280 !important;
  font-size: 10px !important;
}

.funding-rate-value {
  font-size: 12px !important;
  font-weight: 700 !important;
}

.futures-trade-main {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, 0.8fr) !important;
  align-items: stretch !important;
  gap: 8px !important;
  padding: 0 12px 10px !important;
}

.futures-orderbook-side,
.futures-form-side {
  height: 328px !important;
  min-height: 328px !important;
  max-height: 328px !important;
  border-radius: 14px !important;
  border: 1px solid #e5e7eb !important;
  background: #ffffff !important;
  box-shadow: 0 3px 12px rgb(17 24 39 / 0.06) !important;
  overflow: hidden !important;
}

.futures-orderbook-side {
  padding: 8px 8px 10px !important;
  display: flex !important;
  flex-direction: column !important;
}

.futures-orderbook-side .orderbook-header {
  height: 24px !important;
  min-height: 24px !important;
  padding: 0 6px 4px !important;
  color: #6b7280 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: 0 !important;
  border-bottom: 0 !important;
}

.futures-orderbook-side .asks-list,
.futures-orderbook-side .bids-list {
  flex: 0 0 auto !important;
  height: 102px !important;
  overflow: hidden !important;
}

.futures-orderbook-side .order-row {
  height: 20px !important;
  line-height: 20px !important;
  padding: 0 6px !important;
  border-radius: 5px !important;
}

.futures-orderbook-side .order-row .price,
.futures-orderbook-side .order-row .quantity {
  min-width: 0 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  font-size: 12px !important;
  line-height: 20px !important;
  letter-spacing: -0.35px !important;
}

.futures-orderbook-side .ask-price,
.futures-orderbook-side .bid-price {
  flex: 1.1 !important;
  text-shadow: none !important;
}

.futures-orderbook-side .quantity {
  flex: 0.9 !important;
}

.futures-orderbook-side .ask-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(239 68 68 / 0.14) 100%) !important;
  box-shadow: none !important;
}

.futures-orderbook-side .bid-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(22 163 74 / 0.14) 100%) !important;
  box-shadow: none !important;
}

.futures-orderbook-side .last-price {
  height: 70px !important;
  min-height: 70px !important;
  margin: 0 !important;
  border: 1px solid rgb(240 185 11 / 0.28) !important;
  border-radius: 12px !important;
  background: linear-gradient(180deg, #fff9e8 0%, #ffffff 100%) !important;
}

.futures-orderbook-side .price-main {
  color: #16a34a !important;
  font-size: 22px !important;
  line-height: 1.1 !important;
  font-weight: 800 !important;
  letter-spacing: -0.8px !important;
  text-shadow: none !important;
}

.futures-orderbook-side .price-fiat {
  color: #6b7280 !important;
  font-size: 10px !important;
  margin-top: 4px !important;
}

.futures-form-side {
  padding: 8px !important;
  display: grid !important;
  grid-template-rows: 34px 42px 42px 44px 30px 30px 36px 46px !important;
  gap: 6px !important;
  align-content: start !important;
}

.futures-form-side .futures-asset-panel {
  display: none !important;
}

.futures-form-side .order-type-selector,
.futures-form-side .input-row,
.futures-form-side .fee-estimate-row,
.futures-form-side .total-row,
.futures-form-side .estimated-received-row,
.futures-form-side .futures-action-buttons-grid {
  min-width: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
}

.futures-form-side .order-type-selector {
  height: 34px !important;
  min-height: 34px !important;
  padding: 0 10px !important;
  border-radius: 10px !important;
  background: #f7f8fa !important;
  border: 1px solid #eaecef !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}

.futures-form-side .input-row {
  height: 42px !important;
  min-height: 42px !important;
  padding: 0 10px !important;
  gap: 6px !important;
  border-radius: 10px !important;
  background: #f7f8fa !important;
  border: 1px solid #eaecef !important;
}

.futures-form-side .input-field {
  min-width: 0 !important;
  width: 100% !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  letter-spacing: -0.3px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.futures-form-side .input-field::placeholder {
  color: #a3a9b5 !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}

.futures-form-side .input-suffix {
  flex: 0 0 auto !important;
  max-width: 36px !important;
  color: #9ca3af !important;
  font-size: 10px !important;
  font-weight: 800 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.futures-form-side .slider-wrapper {
  height: 44px !important;
  min-height: 44px !important;
  padding: 6px 10px 0 !important;
  margin: 0 !important;
}

.futures-form-side .custom-slider-button {
  width: 24px !important;
  height: 24px !important;
  line-height: 24px !important;
  font-size: 9px !important;
}

.futures-form-side .slider-marks {
  padding: 4px 0 0 !important;
  margin: 0 !important;
}

.futures-form-side .mark-item {
  min-width: auto !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  color: #6b7280 !important;
  font-size: 10px !important;
  font-weight: 700 !important;
}

.futures-form-side .fee-estimate-row,
.futures-form-side .total-row {
  height: 30px !important;
  padding: 0 10px !important;
  border: 0 !important;
  background: transparent !important;
}

.futures-form-side .fee-estimate-label,
.futures-form-side .total-label,
.futures-form-side .received-label {
  min-width: 0 !important;
  color: #6b7280 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: -0.2px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.futures-form-side .fee-estimate-value,
.futures-form-side .total-value,
.futures-form-side .received-value {
  max-width: 72px !important;
  color: #111827 !important;
  font-size: 12px !important;
  font-weight: 800 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.futures-form-side .estimated-received-row {
  height: 36px !important;
  padding: 0 10px !important;
  border-radius: 10px !important;
  background: #fff8e1 !important;
  border: 1px solid #f8e2a0 !important;
}

.futures-form-side .futures-action-buttons-grid {
  height: 46px !important;
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 8px !important;
}

.futures-form-side .long-btn-grid,
.futures-form-side .short-btn-grid {
  height: 46px !important;
  min-height: 46px !important;
  padding: 0 !important;
  border-radius: 11px !important;
  font-size: 14px !important;
  font-weight: 800 !important;
  white-space: nowrap !important;
}

.futures-bottom-section {
  margin-top: 0 !important;
}

@media (max-width: 390px) {
  .futures-trade-main {
    grid-template-columns: minmax(0, 1fr) minmax(0, 0.78fr) !important;
    gap: 6px !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
  }

  .futures-orderbook-side,
  .futures-form-side {
    height: 320px !important;
    min-height: 320px !important;
    max-height: 320px !important;
  }

  .futures-orderbook-side .order-row .price,
  .futures-orderbook-side .order-row .quantity {
    font-size: 11px !important;
  }

  .futures-form-side {
    padding: 7px !important;
    gap: 5px !important;
  }
}

/* Final light trading workspace alignment: spot + futures */
.trade-page {
  font-variant-numeric: tabular-nums;
}

.trade-main,
.futures-trade-main {
  display: grid !important;
  grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr) !important;
  gap: 10px !important;
  align-items: stretch !important;
  padding: 10px 12px 12px !important;
  min-width: 0 !important;
  background: transparent !important;
}

.orderbook-side,
.form-side,
.futures-orderbook-side,
.futures-form-side {
  width: auto !important;
  min-width: 0 !important;
  height: 500px !important;
  min-height: 500px !important;
  max-height: 500px !important;
  background: #ffffff !important;
  border: 1px solid #eaecef !important;
  border-radius: 14px !important;
  box-shadow: 0 2px 10px rgb(17 24 39 / 0.05) !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
}

.orderbook-side,
.futures-orderbook-side {
  display: flex !important;
  flex-direction: column !important;
  padding: 12px 10px !important;
}

.orderbook-side .orderbook-header,
.futures-orderbook-side .orderbook-header {
  height: 28px !important;
  min-height: 28px !important;
  padding: 0 6px 6px !important;
  color: #6b7280 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
  border-bottom: 0 !important;
}

.orderbook-side .asks-list,
.orderbook-side .bids-list,
.futures-orderbook-side .asks-list,
.futures-orderbook-side .bids-list {
  flex: 0 0 auto !important;
  height: 160px !important;
  overflow: hidden !important;
}

.orderbook-side .order-row,
.futures-orderbook-side .order-row {
  height: 32px !important;
  line-height: 32px !important;
  padding: 0 6px !important;
  border-radius: 6px !important;
}

.orderbook-side .order-row .price,
.orderbook-side .order-row .quantity,
.futures-orderbook-side .order-row .price,
.futures-orderbook-side .order-row .quantity {
  min-width: 0 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace !important;
  font-size: 13px !important;
  line-height: 32px !important;
  font-variant-numeric: tabular-nums !important;
}

.orderbook-side .order-row .price,
.futures-orderbook-side .order-row .price {
  flex: 1.05 !important;
  text-align: left !important;
  font-weight: 600 !important;
  letter-spacing: -0.35px !important;
}

.orderbook-side .order-row .quantity,
.futures-orderbook-side .order-row .quantity {
  flex: 0.95 !important;
  text-align: right !important;
  color: #4b5563 !important;
  font-weight: 500 !important;
  letter-spacing: -0.3px !important;
}

.orderbook-side .ask-depth,
.futures-orderbook-side .ask-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(var(--color-loss-rgb) / 0.13) 100%) !important;
  box-shadow: none !important;
}

.orderbook-side .bid-depth,
.futures-orderbook-side .bid-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(var(--color-earn-rgb) / 0.13) 100%) !important;
  box-shadow: none !important;
}

.orderbook-side .ask-price,
.futures-orderbook-side .ask-price {
  color: var(--color-loss) !important;
  text-shadow: none !important;
}

.orderbook-side .bid-price,
.futures-orderbook-side .bid-price {
  color: var(--color-earn) !important;
  text-shadow: none !important;
}

.orderbook-side .last-price,
.futures-orderbook-side .last-price {
  height: 72px !important;
  min-height: 72px !important;
  margin: 0 !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.20) !important;
  border-radius: 12px !important;
  background: linear-gradient(180deg, rgb(var(--color-brand-rgb) / 0.045), #ffffff) !important;
}

.orderbook-side .price-main,
.futures-orderbook-side .price-main {
  color: var(--color-earn) !important;
  font-size: 25px !important;
  font-weight: 700 !important;
  line-height: 1.08 !important;
  letter-spacing: -0.8px !important;
  text-shadow: none !important;
}

.orderbook-side .price-fiat,
.futures-orderbook-side .price-fiat {
  color: #6b7280 !important;
  font-size: 12px !important;
  line-height: 1 !important;
  margin-top: 5px !important;
}

.form-side,
.futures-form-side {
  padding: 12px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  align-content: stretch !important;
}

.futures-form-side {
  display: flex !important;
}

.form-side .buy-sell-toggle {
  height: 50px !important;
  min-height: 50px !important;
  padding: 3px !important;
  margin: 0 !important;
  border-radius: 12px !important;
}

.form-side .toggle-btn {
  height: 42px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
}

.form-side .order-type-selector,
.futures-form-side .order-type-selector {
  height: 46px !important;
  min-height: 46px !important;
  padding: 0 12px !important;
  margin: 0 !important;
  border-radius: 12px !important;
  background: #ffffff !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.16) !important;
  font-size: 15px !important;
  font-weight: 700 !important;
  color: #111827 !important;
}

.form-side .input-row,
.futures-form-side .input-row {
  height: 56px !important;
  min-height: 56px !important;
  padding: 0 12px !important;
  margin: 0 !important;
  gap: 6px !important;
  border-radius: 12px !important;
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
}

.form-side .input-row:focus-within,
.futures-form-side .input-row:focus-within {
  border-color: rgb(var(--color-brand-rgb) / 0.55) !important;
  box-shadow: 0 0 0 3px rgb(var(--color-brand-rgb) / 0.08) !important;
}

.form-side .input-label,
.futures-form-side .input-label {
  min-width: auto !important;
  max-width: 72px !important;
  color: #6b7280 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: -0.2px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.form-side .input-field,
.futures-form-side .input-field {
  min-width: 0 !important;
  width: 100% !important;
  color: #111827 !important;
  font-size: 17px !important;
  font-weight: 700 !important;
  letter-spacing: -0.35px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.form-side .input-field::placeholder,
.futures-form-side .input-field::placeholder {
  color: #a3a9b5 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}

.form-side .input-suffix,
.futures-form-side .input-suffix {
  flex: 0 0 auto !important;
  max-width: 40px !important;
  color: #9ca3af !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.form-side .estimated-row {
  min-height: 22px !important;
  padding: 0 4px !important;
  margin: -2px 0 !important;
}

.form-side .est-label,
.form-side .est-value {
  font-size: 11px !important;
  white-space: nowrap !important;
}

.form-side .slider-wrapper,
.futures-form-side .slider-wrapper {
  height: 52px !important;
  min-height: 52px !important;
  padding: 10px 10px 0 !important;
  margin: 0 !important;
}

.form-side .custom-slider-button,
.futures-form-side .custom-slider-button {
  width: 26px !important;
  height: 26px !important;
  line-height: 26px !important;
  font-size: 9px !important;
}

.form-side .slider-marks,
.futures-form-side .slider-marks {
  padding: 5px 0 0 !important;
  margin: 0 !important;
}

.form-side .mark-item,
.futures-form-side .mark-item {
  min-width: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  color: #6b7280 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
}

.form-side .fee-estimate-row,
.form-side .total-row,
.form-side .estimated-received-row,
.futures-form-side .fee-estimate-row,
.futures-form-side .total-row,
.futures-form-side .estimated-received-row {
  height: 28px !important;
  min-height: 28px !important;
  padding: 0 4px !important;
  margin: 0 !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
}

.form-side .estimated-received-row,
.futures-form-side .estimated-received-row {
  height: 42px !important;
  min-height: 42px !important;
  padding: 0 10px !important;
  border-radius: 12px !important;
  background: rgb(var(--color-brand-rgb) / 0.07) !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.16) !important;
}

.form-side .fee-estimate-label,
.form-side .total-label,
.form-side .received-label,
.futures-form-side .fee-estimate-label,
.futures-form-side .total-label,
.futures-form-side .received-label {
  min-width: 0 !important;
  color: #6b7280 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: -0.2px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.form-side .fee-estimate-value,
.form-side .total-value,
.form-side .received-value,
.futures-form-side .fee-estimate-value,
.futures-form-side .total-value,
.futures-form-side .received-value {
  max-width: 82px !important;
  color: #111827 !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.form-side .available-row {
  min-height: 42px !important;
  padding: 4px 8px !important;
  margin: 0 !important;
  gap: 0 !important;
  border: 0 !important;
  background: transparent !important;
}

.form-side .avail-item {
  min-width: 0 !important;
  height: 19px !important;
  padding: 0 !important;
  justify-content: flex-end !important;
}

.form-side .avail-label,
.form-side .avail-value {
  font-size: 12px !important;
  white-space: nowrap !important;
}

.form-side .submit-btn,
.futures-form-side .long-btn-grid,
.futures-form-side .short-btn-grid {
  height: 54px !important;
  min-height: 54px !important;
  border-radius: 12px !important;
  font-size: 16px !important;
  font-weight: 800 !important;
  white-space: nowrap !important;
}

.form-side .submit-btn,
.futures-form-side .futures-action-buttons-grid {
  margin-top: auto !important;
}

.futures-form-side .futures-action-buttons-grid {
  height: 54px !important;
  min-height: 54px !important;
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 8px !important;
}

.futures-form-side .futures-asset-panel {
  display: none !important;
}

.futures-control-bar {
  height: 48px !important;
  min-height: 48px !important;
  margin: 8px 12px 0 !important;
  padding: 6px 10px !important;
  border-radius: 14px !important;
  background: #ffffff !important;
  border: 1px solid #eaecef !important;
  box-shadow: 0 2px 8px rgb(17 24 39 / 0.04) !important;
}

.futures-control-bar .leverage-btn {
  height: 36px !important;
  min-height: 36px !important;
  padding: 0 14px !important;
  border-radius: 12px !important;
}

.futures-control-bar .funding-rate-info {
  min-width: 96px !important;
  padding: 0 !important;
  background: transparent !important;
  border: 0 !important;
}

.futures-bottom-section,
.bottom-section {
  position: relative !important;
  z-index: 1 !important;
  margin-top: 8px !important;
  background: #ffffff !important;
}

@media (max-width: 390px) {
  .trade-main,
  .futures-trade-main {
    grid-template-columns: minmax(0, 1.06fr) minmax(0, 0.94fr) !important;
    gap: 8px !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
  }

  .orderbook-side,
  .form-side,
  .futures-orderbook-side,
  .futures-form-side {
    height: 492px !important;
    min-height: 492px !important;
    max-height: 492px !important;
  }

  .orderbook-side,
  .futures-orderbook-side,
  .form-side,
  .futures-form-side {
    padding-left: 8px !important;
    padding-right: 8px !important;
  }

  .form-side .input-field,
  .futures-form-side .input-field {
    font-size: 16px !important;
  }
}

/* Final professional sizing pass: balanced, breathable, no clipping */
.trade-main,
.futures-trade-main {
  grid-template-columns: minmax(0, 1.06fr) minmax(0, 0.94fr) !important;
  gap: 10px !important;
  padding: 10px 14px 12px !important;
}

.orderbook-side,
.form-side,
.futures-orderbook-side,
.futures-form-side {
  height: 456px !important;
  min-height: 456px !important;
  max-height: 456px !important;
}

.orderbook-side,
.futures-orderbook-side {
  padding: 10px 10px !important;
}

.orderbook-side .orderbook-header,
.futures-orderbook-side .orderbook-header {
  height: 26px !important;
  min-height: 26px !important;
  padding: 0 6px 4px !important;
  font-size: 12px !important;
}

.orderbook-side .asks-list,
.orderbook-side .bids-list,
.futures-orderbook-side .asks-list,
.futures-orderbook-side .bids-list {
  height: 150px !important;
}

.orderbook-side .order-row,
.futures-orderbook-side .order-row {
  height: 30px !important;
  line-height: 30px !important;
}

.orderbook-side .order-row .price,
.orderbook-side .order-row .quantity,
.futures-orderbook-side .order-row .price,
.futures-orderbook-side .order-row .quantity {
  font-size: 12.5px !important;
  line-height: 30px !important;
}

.orderbook-side .last-price,
.futures-orderbook-side .last-price {
  height: 66px !important;
  min-height: 66px !important;
}

.orderbook-side .price-main,
.futures-orderbook-side .price-main {
  font-size: 24px !important;
}

.form-side,
.futures-form-side {
  padding: 10px !important;
  gap: 5px !important;
  overflow: hidden !important;
}

.form-side .estimated-row {
  display: none !important;
}

.form-side .buy-sell-toggle {
  height: 44px !important;
  min-height: 44px !important;
  padding: 3px !important;
  border-radius: 12px !important;
}

.form-side .toggle-btn {
  height: 36px !important;
  font-size: 15px !important;
  border-radius: 10px !important;
}

.form-side .order-type-selector,
.futures-form-side .order-type-selector {
  height: 40px !important;
  min-height: 40px !important;
  padding: 0 11px !important;
  border-radius: 11px !important;
  font-size: 14px !important;
}

.form-side .input-row,
.futures-form-side .input-row {
  height: 44px !important;
  min-height: 44px !important;
  padding: 0 10px !important;
  border-radius: 11px !important;
}

.form-side .input-label,
.futures-form-side .input-label {
  max-width: 68px !important;
  font-size: 11px !important;
}

.form-side .input-field,
.futures-form-side .input-field {
  font-size: 15px !important;
  font-weight: 700 !important;
}

.form-side .input-field::placeholder,
.futures-form-side .input-field::placeholder {
  font-size: 13px !important;
}

.form-side .slider-wrapper,
.futures-form-side .slider-wrapper {
  height: 42px !important;
  min-height: 42px !important;
  padding: 7px 8px 0 !important;
}

.form-side .custom-slider-button,
.futures-form-side .custom-slider-button {
  width: 24px !important;
  height: 24px !important;
  line-height: 24px !important;
  font-size: 9px !important;
}

.form-side .slider-marks,
.futures-form-side .slider-marks {
  padding-top: 4px !important;
}

.form-side .mark-item,
.futures-form-side .mark-item {
  font-size: 10px !important;
  letter-spacing: -0.35px !important;
}

.form-side .fee-estimate-row,
.form-side .total-row,
.futures-form-side .fee-estimate-row,
.futures-form-side .total-row {
  height: 24px !important;
  min-height: 24px !important;
  padding: 0 3px !important;
}

.form-side .estimated-received-row,
.futures-form-side .estimated-received-row {
  height: 34px !important;
  min-height: 34px !important;
  padding: 0 9px !important;
  border-radius: 10px !important;
}

.form-side .fee-estimate-label,
.form-side .total-label,
.form-side .received-label,
.futures-form-side .fee-estimate-label,
.futures-form-side .total-label,
.futures-form-side .received-label {
  font-size: 11px !important;
}

.form-side .fee-estimate-value,
.form-side .total-value,
.form-side .received-value,
.futures-form-side .fee-estimate-value,
.futures-form-side .total-value,
.futures-form-side .received-value {
  max-width: 74px !important;
  font-size: 12px !important;
}

.form-side .available-row {
  min-height: 32px !important;
  height: 32px !important;
  padding: 0 6px !important;
}

.form-side .avail-item {
  height: 16px !important;
}

.form-side .avail-label,
.form-side .avail-value {
  font-size: 11px !important;
}

.form-side .submit-btn,
.futures-form-side .long-btn-grid,
.futures-form-side .short-btn-grid {
  height: 48px !important;
  min-height: 48px !important;
  border-radius: 11px !important;
  font-size: 15px !important;
}

.futures-form-side .futures-action-buttons-grid {
  height: 48px !important;
  min-height: 48px !important;
}

.futures-control-bar {
  height: 44px !important;
  min-height: 44px !important;
  margin: 8px 14px 0 !important;
}

.futures-control-bar .leverage-btn {
  height: 32px !important;
  min-height: 32px !important;
}

.futures-bottom-section,
.bottom-section {
  margin-top: 6px !important;
}

@media (max-width: 390px) {
  .trade-main,
  .futures-trade-main {
    grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr) !important;
    gap: 8px !important;
    padding: 8px 10px 10px !important;
  }

  .orderbook-side,
  .form-side,
  .futures-orderbook-side,
  .futures-form-side {
    height: 448px !important;
    min-height: 448px !important;
    max-height: 448px !important;
  }

  .orderbook-side .order-row .price,
  .orderbook-side .order-row .quantity,
  .futures-orderbook-side .order-row .price,
  .futures-orderbook-side .order-row .quantity {
    font-size: 12px !important;
  }

  .form-side,
  .futures-form-side {
    padding: 8px !important;
    gap: 5px !important;
  }

  .form-side .input-field,
  .futures-form-side .input-field {
    font-size: 14px !important;
  }

  .form-side .fee-estimate-value,
  .form-side .total-value,
  .form-side .received-value,
  .futures-form-side .fee-estimate-value,
  .futures-form-side .total-value,
  .futures-form-side .received-value {
    max-width: 64px !important;
  }
}

/* Micro layout pass: prevent text crowding and rebalance CTAs */
.trade-main,
.futures-trade-main {
  grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr) !important;
}

.form-side,
.futures-form-side {
  gap: 6px !important;
}

.form-side .buy-sell-toggle {
  height: 42px !important;
  min-height: 42px !important;
}

.form-side .toggle-btn {
  height: 34px !important;
  font-size: 14px !important;
  line-height: 1 !important;
}

.form-side .order-type-selector,
.futures-form-side .order-type-selector {
  height: 38px !important;
  min-height: 38px !important;
  padding: 0 10px !important;
  font-size: 13px !important;
}

.form-side .input-row,
.futures-form-side .input-row {
  height: 42px !important;
  min-height: 42px !important;
  padding: 0 9px !important;
  display: grid !important;
  grid-template-columns: minmax(0, auto) minmax(0, 1fr) auto !important;
  align-items: center !important;
}

.form-side .input-row > template,
.futures-form-side .input-row > template {
  min-width: 0 !important;
}

.form-side .input-label,
.futures-form-side .input-label {
  max-width: 56px !important;
  font-size: 10px !important;
  line-height: 1 !important;
  letter-spacing: -0.35px !important;
}

.form-side .input-field,
.futures-form-side .input-field {
  min-width: 0 !important;
  font-size: 13px !important;
  line-height: 1 !important;
  letter-spacing: -0.45px !important;
}

.form-side .input-field::placeholder,
.futures-form-side .input-field::placeholder {
  font-size: 12px !important;
}

.form-side .input-suffix,
.futures-form-side .input-suffix {
  max-width: 30px !important;
  font-size: 9px !important;
  margin-left: 2px !important;
}

.form-side .slider-wrapper,
.futures-form-side .slider-wrapper {
  height: 40px !important;
  min-height: 40px !important;
  padding: 6px 8px 0 !important;
}

.form-side .custom-slider-button,
.futures-form-side .custom-slider-button {
  width: 22px !important;
  height: 22px !important;
  line-height: 22px !important;
  font-size: 8px !important;
  box-shadow: 0 4px 10px rgb(var(--color-brand-rgb) / 0.28) !important;
}

.form-side .slider-marks,
.futures-form-side .slider-marks {
  display: grid !important;
  grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
  gap: 0 !important;
}

.form-side .mark-item,
.futures-form-side .mark-item {
  font-size: 9px !important;
  line-height: 1 !important;
  letter-spacing: -0.55px !important;
  text-align: center !important;
}

.form-side .fee-estimate-row,
.form-side .total-row,
.futures-form-side .fee-estimate-row,
.futures-form-side .total-row {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, auto) !important;
  gap: 5px !important;
}

.form-side .estimated-received-row,
.futures-form-side .estimated-received-row {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, auto) !important;
  gap: 6px !important;
}

.form-side .fee-estimate-label,
.form-side .total-label,
.form-side .received-label,
.futures-form-side .fee-estimate-label,
.futures-form-side .total-label,
.futures-form-side .received-label {
  font-size: 10px !important;
  line-height: 1.1 !important;
  letter-spacing: -0.45px !important;
}

.form-side .fee-estimate-value,
.form-side .total-value,
.form-side .received-value,
.futures-form-side .fee-estimate-value,
.futures-form-side .total-value,
.futures-form-side .received-value {
  max-width: 68px !important;
  font-size: 11px !important;
  line-height: 1.1 !important;
  letter-spacing: -0.45px !important;
}

.fee-usdt-note {
  display: none !important;
}

.form-side .available-row {
  height: 28px !important;
  min-height: 28px !important;
  padding: 0 4px !important;
}

.form-side .avail-item {
  height: 14px !important;
  line-height: 14px !important;
}

.form-side .avail-label,
.form-side .avail-value {
  font-size: 10px !important;
  line-height: 14px !important;
  letter-spacing: -0.35px !important;
}

.form-side .submit-btn,
.futures-form-side .long-btn-grid,
.futures-form-side .short-btn-grid {
  height: 44px !important;
  min-height: 44px !important;
  border-radius: 10px !important;
  font-size: 14px !important;
  letter-spacing: 0 !important;
}

.futures-form-side .futures-action-buttons-grid {
  height: 44px !important;
  min-height: 44px !important;
  gap: 7px !important;
}

.futures-control-bar {
  height: 42px !important;
  min-height: 42px !important;
}

.futures-control-bar .margin-mode-text,
.futures-control-bar .leverage-btn span {
  font-size: 12px !important;
}

.futures-control-bar .funding-rate-label {
  font-size: 9px !important;
}

.futures-control-bar .funding-rate-value {
  font-size: 11px !important;
}

.orderbook-side .order-row .price,
.orderbook-side .order-row .quantity,
.futures-orderbook-side .order-row .price,
.futures-orderbook-side .order-row .quantity {
  font-size: 12px !important;
  letter-spacing: -0.55px !important;
}

@media (max-width: 390px) {
  .trade-main,
  .futures-trade-main {
    grid-template-columns: minmax(0, 1fr) minmax(0, 0.88fr) !important;
    gap: 7px !important;
  }

  .form-side,
  .futures-form-side {
    padding: 7px !important;
    gap: 5px !important;
  }

  .form-side .input-row,
  .futures-form-side .input-row {
    padding: 0 7px !important;
  }

  .form-side .input-label,
  .futures-form-side .input-label {
    max-width: 48px !important;
    font-size: 9px !important;
  }

  .form-side .input-field,
  .futures-form-side .input-field {
    font-size: 12px !important;
  }

  .form-side .fee-estimate-value,
  .form-side .total-value,
  .form-side .received-value,
  .futures-form-side .fee-estimate-value,
  .futures-form-side .total-value,
  .futures-form-side .received-value {
    max-width: 56px !important;
    font-size: 10px !important;
  }

  .form-side .submit-btn,
  .futures-form-side .long-btn-grid,
  .futures-form-side .short-btn-grid {
    height: 42px !important;
    min-height: 42px !important;
    font-size: 13px !important;
  }
}

/* Final trade form typography pass: keep every input row visually calm and consistent. */
.trade-page {
  --trade-input-muted: #6b7280;
  --trade-input-value: #111827;
  --trade-input-placeholder: #9ca3af;
  --trade-input-hairline: #e5e7eb;
  --trade-input-soft-border: #edf0f4;
}

.futures-control-bar {
  display: none !important;
}

.futures-form-side .form-tools-row {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 72px !important;
  align-items: center !important;
  gap: 8px !important;
  width: 100% !important;
}

.futures-form-side .form-tools-row .order-type-selector {
  width: 100% !important;
  min-width: 0 !important;
  height: 42px !important;
  min-height: 42px !important;
  padding: 0 10px !important;
  border-color: rgba(245, 158, 11, 0.22) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04) !important;
}

.futures-form-side .form-tools-row .order-type-selector span {
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.leverage-inline-btn {
  width: 72px !important;
  height: 42px !important;
  min-height: 42px !important;
  padding: 0 8px !important;
  border: 1px solid var(--trade-input-hairline) !important;
  border-radius: 12px !important;
  background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%) !important;
  color: var(--color-text-primary) !important;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06) !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 3px !important;
  font-size: 12px !important;
  line-height: 1 !important;
  font-weight: 700 !important;
  letter-spacing: 0 !important;
  cursor: pointer !important;
}

.leverage-inline-btn:active {
  transform: translateY(1px) !important;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
}

.form-side .input-row,
.futures-form-side .input-row {
  color: var(--trade-input-muted) !important;
  border-color: var(--trade-input-soft-border) !important;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.03) !important;
}

.form-side .input-label,
.futures-form-side .input-label,
.form-side .input-suffix,
.futures-form-side .input-suffix {
  color: var(--trade-input-muted) !important;
  font-size: 11px !important;
  line-height: 1.2 !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
}

.form-side .input-field,
.futures-form-side .input-field {
  color: var(--trade-input-value) !important;
  font-size: 12px !important;
  line-height: 1.2 !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
  font-family: inherit !important;
}

.form-side .input-field::placeholder,
.futures-form-side .input-field::placeholder,
.form-side .market-price-input,
.futures-form-side .market-price-input {
  color: var(--trade-input-placeholder) !important;
  font-size: 11px !important;
  line-height: 1.2 !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
  font-style: normal !important;
  opacity: 1 !important;
}

.form-side .market-price-input,
.futures-form-side .market-price-input {
  cursor: default !important;
  -webkit-text-fill-color: var(--trade-input-placeholder) !important;
}

@media (max-width: 390px) {
  .futures-form-side .form-tools-row {
    grid-template-columns: minmax(0, 1fr) 66px !important;
    gap: 6px !important;
  }

  .leverage-inline-btn {
    width: 66px !important;
    font-size: 11px !important;
  }

  .form-side .input-field,
  .futures-form-side .input-field {
    font-size: 11px !important;
  }

  .form-side .input-field::placeholder,
  .futures-form-side .input-field::placeholder,
  .form-side .market-price-input,
  .futures-form-side .market-price-input {
    font-size: 10.5px !important;
  }
}

/* =====================================================================
   FIGURE-2 HIGH-FIDELITY REDESIGN (futures / 合约 view)
   Pure visual layer: clean white surfaces, light borders, soft shadows,
   consistent radii + typography. No markup / logic changes.
   Kept last so it wins the cascade over earlier tuning passes.
   ===================================================================== */

/* ---- Page shell ---- */
.trade-page {
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-variant-numeric: tabular-nums;
}

.trade-page .futures-trade-container {
  background: #ffffff !important;
}

/* ---- 现货 / 合约 tabs ---- */
.trade-page .trade-tabs {
  padding: 0 16px !important;
  gap: 28px !important;
  border-bottom: 1px solid #eaecef !important;
}

.trade-page .trade-tabs .tab-item {
  padding: 12px 0 !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  color: #6b7280 !important;
}

.trade-page .trade-tabs .tab-item.active {
  color: #111827 !important;
  font-weight: 700 !important;
}

.trade-page .trade-tabs .tab-item.active::after {
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%) !important;
  width: 32px !important;
  height: 3px !important;
  border-radius: 2px !important;
  background: var(--color-brand-legacy) !important;
}

/* ---- Trade page in-app header (title + kline) ---- */
.trade-page .trade-header {
  height: 52px !important;
  background: #ffffff !important;
  border-bottom: 1px solid #eaecef !important;
}

/* ---- Pair info row ---- */
.trade-page .pair-info {
  padding: 14px 16px !important;
  min-height: 60px !important;
  border-bottom: 1px solid #eaecef !important;
}

.trade-page .pair-name {
  font-size: 22px !important;
  font-weight: 800 !important;
  letter-spacing: -0.4px !important;
  color: #111827 !important;
}

.trade-page .price-change {
  font-size: 14px !important;
  font-weight: 700 !important;
  padding: 6px 12px !important;
  border-radius: 8px !important;
}

.trade-page .price-change.positive {
  color: #16a34a !important;
  background: rgb(22 163 74 / 0.10) !important;
}

.trade-page .price-change.negative {
  color: #ef4444 !important;
  background: rgb(239 68 68 / 0.10) !important;
}

/* ---- Two-column trade area ---- */
.trade-page .futures-trade-main {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
  gap: 12px !important;
  padding: 12px 16px !important;
  align-items: stretch !important;
  background: transparent !important;
}

.trade-page .futures-orderbook-side,
.trade-page .futures-form-side {
  width: auto !important;
  min-width: 0 !important;
  height: 472px !important;
  min-height: 472px !important;
  max-height: 472px !important;
  box-sizing: border-box !important;
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 16px rgb(0 0 0 / 0.04) !important;
  overflow: hidden !important;
}

/* ---- Order-book card ---- */
.trade-page .futures-orderbook-side {
  display: flex !important;
  flex-direction: column !important;
  padding: 12px !important;
}

.trade-page .futures-orderbook-side .orderbook-header {
  height: 26px !important;
  min-height: 26px !important;
  padding: 0 6px 6px !important;
  color: #6b7280 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  border-bottom: 0 !important;
}

.trade-page .futures-orderbook-side .asks-list,
.trade-page .futures-orderbook-side .bids-list {
  flex: 0 0 auto !important;
  height: 170px !important;
  overflow: hidden !important;
}

.trade-page .futures-orderbook-side .order-row {
  height: 34px !important;
  line-height: 34px !important;
  padding: 0 6px !important;
  border-radius: 6px !important;
}

.trade-page .futures-orderbook-side .order-row .price,
.trade-page .futures-orderbook-side .order-row .quantity {
  font-family: var(--font-number) !important;
  font-size: 13px !important;
  line-height: 34px !important;
  letter-spacing: -0.2px !important;
  font-variant-numeric: tabular-nums !important;
}

.trade-page .futures-orderbook-side .order-row .quantity {
  color: #6b7280 !important;
  font-weight: 500 !important;
}

.trade-page .futures-orderbook-side .ask-price { color: #ef4444 !important; text-shadow: none !important; }
.trade-page .futures-orderbook-side .bid-price { color: #16a34a !important; text-shadow: none !important; }

.trade-page .futures-orderbook-side .ask-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(239 68 68 / 0.12) 100%) !important;
}
.trade-page .futures-orderbook-side .bid-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(22 163 74 / 0.12) 100%) !important;
}

.trade-page .futures-orderbook-side .last-price {
  height: 78px !important;
  min-height: 78px !important;
  margin: 2px 0 !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.35) !important;
  border-radius: 12px !important;
  background: linear-gradient(180deg, rgb(var(--color-brand-rgb) / 0.08), #ffffff) !important;
  box-shadow: none !important;
  animation: none !important;
}

.trade-page .futures-orderbook-side .price-main {
  color: #16a34a !important;
  font-size: 30px !important;
  font-weight: 800 !important;
  letter-spacing: -0.8px !important;
  text-shadow: none !important;
}

.trade-page .futures-orderbook-side .price-fiat {
  color: #6b7280 !important;
  font-size: 12px !important;
  margin-top: 5px !important;
}

/* ---- Order panel card ---- */
.trade-page .futures-form-side {
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
  padding: 12px !important;
  overflow: hidden !important;
}

.trade-page .futures-form-side .futures-asset-panel { display: none !important; }

/* order-type + leverage buttons row */
.trade-page .futures-form-side .form-tools-row {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 96px !important;
  gap: 10px !important;
  width: 100% !important;
}

.trade-page .futures-form-side .form-tools-row .order-type-selector {
  width: 100% !important;
  height: 48px !important;
  min-height: 48px !important;
  padding: 0 14px !important;
  border-radius: 12px !important;
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  box-shadow: none !important;
  color: #111827 !important;
  font-size: 14px !important;
  font-weight: 600 !important;
}

.trade-page .leverage-inline-btn {
  width: 96px !important;
  height: 48px !important;
  min-height: 48px !important;
  border-radius: 12px !important;
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  box-shadow: none !important;
  color: #111827 !important;
  font-size: 14px !important;
  font-weight: 700 !important;
}

/* inputs */
.trade-page .futures-form-side .input-row {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: center !important;
  height: 50px !important;
  min-height: 50px !important;
  padding: 0 14px !important;
  gap: 8px !important;
  border-radius: 12px !important;
  background: #ffffff !important;
  border: 1px solid #e5e7eb !important;
  box-shadow: none !important;
}

.trade-page .futures-form-side .input-row:focus-within {
  border-color: rgb(var(--color-brand-rgb) / 0.55) !important;
  box-shadow: 0 0 0 3px rgb(var(--color-brand-rgb) / 0.10) !important;
}

.trade-page .futures-form-side .input-field {
  min-width: 0 !important;
  width: 100% !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
  color: #111827 !important;
  font-family: var(--font-number) !important;
}

.trade-page .futures-form-side .input-field::placeholder,
.trade-page .futures-form-side .market-price-input {
  color: #9ca3af !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  -webkit-text-fill-color: #9ca3af !important;
}

.trade-page .futures-form-side .input-suffix {
  flex: 0 0 auto !important;
  max-width: none !important;
  color: #9ca3af !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}

/* slider */
.trade-page .futures-form-side .slider-wrapper {
  height: auto !important;
  min-height: 44px !important;
  padding: 8px 4px 0 !important;
  margin: 0 !important;
}

.trade-page .futures-form-side .custom-slider-button {
  width: 26px !important;
  height: 26px !important;
  line-height: 26px !important;
  font-size: 9px !important;
}

.trade-page .futures-form-side .slider-marks {
  display: flex !important;
  justify-content: space-between !important;
  grid-template-columns: none !important;
  padding: 10px 2px 0 !important;
  margin: 0 !important;
}

.trade-page .futures-form-side .mark-item {
  min-width: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  color: #6b7280 !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 0 !important;
}

/* fee + total rows */
.trade-page .futures-form-side .fee-estimate-row,
.trade-page .futures-form-side .total-row {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  height: 24px !important;
  min-height: 24px !important;
  padding: 0 2px !important;
  margin: 0 !important;
  background: transparent !important;
  border: 0 !important;
}

.trade-page .futures-form-side .fee-estimate-label,
.trade-page .futures-form-side .total-label {
  color: #6b7280 !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
}

.trade-page .futures-form-side .fee-estimate-value,
.trade-page .futures-form-side .total-value {
  max-width: none !important;
  color: #111827 !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  font-family: var(--font-number) !important;
}

/* margin row (soft yellow strip) */
.trade-page .futures-form-side .estimated-received-row {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  height: 42px !important;
  min-height: 42px !important;
  padding: 0 12px !important;
  border-radius: 8px !important;
  background: rgb(var(--color-brand-rgb) / 0.10) !important;
  border: 0 !important;
}

.trade-page .futures-form-side .received-label {
  color: #6b7280 !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
}

.trade-page .futures-form-side .received-value {
  max-width: none !important;
  color: #111827 !important;
  font-size: 13px !important;
  font-weight: 800 !important;
  font-family: var(--font-number) !important;
}

/* available balance (single clean row) */
.trade-page .futures-form-side .available-margin-row {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  height: 30px !important;
  min-height: 30px !important;
  padding: 0 2px !important;
  margin: 0 !important;
  background: transparent !important;
  border: 0 !important;
}

.trade-page .futures-form-side .available-margin-label {
  color: #6b7280 !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

.trade-page .futures-form-side .available-margin-value {
  color: #111827 !important;
  font-size: 14px !important;
  font-weight: 800 !important;
  font-family: var(--font-number) !important;
}

/* long / short buttons (soft tinted, colored text + border) */
.trade-page .futures-form-side .futures-action-buttons-grid {
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 10px !important;
  height: 48px !important;
  min-height: 48px !important;
  margin-top: auto !important;
  padding-top: 0 !important;
}

.trade-page .futures-form-side .long-btn-grid,
.trade-page .futures-form-side .short-btn-grid {
  height: 48px !important;
  min-height: 48px !important;
  border-radius: 12px !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  font-family: inherit !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
  text-shadow: none !important;
  box-shadow: none !important;
}

.trade-page .futures-form-side .long-btn-grid {
  background: rgb(22 163 74 / 0.12) !important;
  color: #16a34a !important;
  border: 1px solid rgb(22 163 74 / 0.5) !important;
}

.trade-page .futures-form-side .short-btn-grid {
  background: rgb(239 68 68 / 0.12) !important;
  color: #ef4444 !important;
  border: 1px solid rgb(239 68 68 / 0.5) !important;
}

.trade-page .futures-form-side .long-btn-grid:active:not(:disabled) {
  background: rgb(22 163 74 / 0.18) !important;
}
.trade-page .futures-form-side .short-btn-grid:active:not(:disabled) {
  background: rgb(239 68 68 / 0.18) !important;
}

/* disabled state stays legible (no washed-out grey) */
.trade-page .futures-form-side .long-btn-grid:disabled {
  opacity: 1 !important;
  filter: none !important;
  background: rgb(22 163 74 / 0.07) !important;
  color: rgb(22 163 74 / 0.55) !important;
  border-color: rgb(22 163 74 / 0.25) !important;
}
.trade-page .futures-form-side .short-btn-grid:disabled {
  opacity: 1 !important;
  filter: none !important;
  background: rgb(239 68 68 / 0.07) !important;
  color: rgb(239 68 68 / 0.55) !important;
  border-color: rgb(239 68 68 / 0.25) !important;
}

.trade-page .futures-form-side .long-btn-grid::before,
.trade-page .futures-form-side .short-btn-grid::before {
  display: none !important;
}

/* ---- Position / orders bottom section ---- */
.trade-page .futures-bottom-section {
  margin-top: 10px !important;
  padding: 0 !important;
  background: #ffffff !important;
  border-top: 1px solid #eaecef !important;
  box-shadow: none !important;
}

.trade-page :deep(.position-tabs .van-tabs__wrap) {
  height: 56px !important;
  background: #ffffff !important;
  border-bottom: 1px solid #eaecef !important;
}

.trade-page :deep(.position-tabs .van-tab) {
  font-size: 14px !important;
  color: #6b7280 !important;
}

.trade-page :deep(.position-tabs .van-tab--active) {
  color: #111827 !important;
  font-weight: 700 !important;
}

.trade-page .positions-list,
.trade-page .orders-list,
.trade-page .history-list {
  padding: 14px 16px !important;
  background: #ffffff !important;
}

/* empty state */
.trade-page .empty-state {
  min-height: 240px !important;
  color: #9ca3af !important;
}
.trade-page .empty-state .empty-icon {
  opacity: 0.5 !important;
  filter: none !important;
}
.trade-page .empty-state .empty-text {
  color: #9ca3af !important;
}

/* ---- Position card ---- */
.trade-page .position-card {
  background: #ffffff !important;
  backdrop-filter: none !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 16px rgb(0 0 0 / 0.04) !important;
  padding: 16px !important;
  gap: 14px !important;
}

.trade-page .position-card:hover {
  transform: none !important;
  background: #ffffff !important;
  border-color: #e5e7eb !important;
  box-shadow: 0 4px 16px rgb(0 0 0 / 0.04) !important;
}
.trade-page .position-card::before { display: none !important; }

.trade-page .position-symbol {
  font-size: 18px !important;
  font-weight: 800 !important;
  color: #111827 !important;
}

.trade-page .position-perpetual {
  background: #f3f4f6 !important;
  color: #6b7280 !important;
  border-radius: 6px !important;
}

.trade-page .position-side-badge {
  text-transform: none !important;
  letter-spacing: 0 !important;
  border-radius: 6px !important;
  padding: 3px 8px !important;
}
.trade-page .position-side-badge.side-long {
  background: rgb(22 163 74 / 0.12) !important;
  color: #16a34a !important;
}
.trade-page .position-side-badge.side-short {
  background: rgb(239 68 68 / 0.12) !important;
  color: #ef4444 !important;
}

.trade-page .position-leverage {
  color: #c99400 !important;
  font-weight: 800 !important;
}

.trade-page .unrealized-pnl-label {
  text-transform: none !important;
  letter-spacing: 0 !important;
  color: #6b7280 !important;
  font-weight: 500 !important;
}

.trade-page .unrealized-pnl-value {
  font-size: 28px !important;
  font-weight: 800 !important;
}
.trade-page .unrealized-pnl-value.positive { color: #16a34a !important; text-shadow: none !important; }
.trade-page .unrealized-pnl-value.negative { color: #ef4444 !important; text-shadow: none !important; }
.trade-page .unrealized-pnl-percent.positive { color: #16a34a !important; text-shadow: none !important; }
.trade-page .unrealized-pnl-percent.negative { color: #ef4444 !important; text-shadow: none !important; }

.trade-page .position-right .info-label {
  text-transform: none !important;
  letter-spacing: 0 !important;
  color: #6b7280 !important;
  font-size: 11px !important;
}
.trade-page .position-right .info-value {
  color: #111827 !important;
  font-size: 13px !important;
}
.trade-page .entry-price-value.side-long,
.trade-page .entry-price-value.side-short,
.trade-page .liquidation-price {
  text-shadow: none !important;
}

.trade-page .position-actions {
  border-top: 1px solid #f0f2f5 !important;
  padding-top: 14px !important;
  gap: 10px !important;
}

.trade-page .action-btn {
  height: 44px !important;
  padding: 0 !important;
  border-radius: 10px !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
}

.trade-page .tp-sl-btn {
  background: #ffffff !important;
  color: #c99400 !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.6) !important;
  backdrop-filter: none !important;
}
.trade-page .close-btn {
  background: #ffffff !important;
  color: #ef4444 !important;
  border: 1px solid rgb(239 68 68 / 0.5) !important;
  backdrop-filter: none !important;
}

/* ---- Responsive guards (375 / 390 / 414) ---- */
@media (max-width: 414px) {
  .trade-page .futures-trade-main {
    padding: 12px !important;
    gap: 10px !important;
  }
  .trade-page .futures-form-side .form-tools-row {
    grid-template-columns: minmax(0, 1fr) 84px !important;
    gap: 8px !important;
  }
  .trade-page .leverage-inline-btn {
    width: 84px !important;
  }
}

@media (max-width: 375px) {
  .trade-page .futures-orderbook-side .price-main {
    font-size: 27px !important;
  }
  .trade-page .futures-form-side .input-field {
    font-size: 14px !important;
  }
}

/* =====================================================================
   FIGURE-2 PASS 2 — fixes for order panel (半宽约束下的按钮/单位/滑杆),
   single-line key-value rows, and global font refinement.
   Appended last so it wins the cascade.
   ===================================================================== */

/* ---- Global font refinement (中文 + 英文 + 数字统一) ---- */
.trade-page {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif !important;
  --font-number: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* 数字区域统一等宽数字对齐（不影响 van-icon 图标字体） */
.trade-page .input-field,
.trade-page .fee-estimate-value,
.trade-page .total-value,
.trade-page .received-value,
.trade-page .available-margin-value,
.trade-page .price-main,
.trade-page .price-fiat,
.trade-page .position-right .info-value,
.trade-page .unrealized-pnl-value,
.trade-page .unrealized-pnl-percent,
.trade-page .position-leverage,
.trade-page .order-price,
.trade-page .order-amount {
  font-variant-numeric: tabular-nums !important;
  font-feature-settings: "tnum" !important;
}

/* 交易对标题 BTC/USDT */
.trade-page .pair-name {
  font-size: 22px !important;
  font-weight: 800 !important;
  line-height: 1.2 !important;
}

/* ---- Order type / leverage buttons: 均分且完整显示“市价单/限价单” ---- */
.trade-page .futures-form-side .form-tools-row {
  grid-template-columns: minmax(0, 1fr) auto !important;
  gap: 8px !important;
}

.trade-page .futures-form-side .form-tools-row .order-type-selector {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  padding: 0 10px !important;
  overflow: visible !important;
  font-size: 13px !important;
  white-space: nowrap !important;
}
.trade-page .futures-form-side .form-tools-row .order-type-selector > span {
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
  flex: 0 1 auto !important;
  min-width: 0 !important;
}
.trade-page .futures-form-side .form-tools-row .order-type-selector .van-icon {
  flex: 0 0 auto !important;
}

/* 杠杆按钮：宽度自适应内容，不再挤压左侧下单类型按钮 */
.trade-page .leverage-inline-btn {
  width: auto !important;
  min-width: 54px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  padding: 0 10px !important;
  font-size: 13px !important;
  white-space: nowrap !important;
}
.trade-page .leverage-inline-btn > span { white-space: nowrap !important; }
.trade-page .leverage-inline-btn .van-icon { flex: 0 0 auto !important; }

/* ---- Inputs: 数字与单位垂直居中；市价单提示不与单位重叠 ---- */
.trade-page .futures-form-side .input-field {
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}
.trade-page .futures-form-side .input-suffix {
  display: inline-flex !important;
  align-items: center !important;
  white-space: nowrap !important;
}

/* ---- Slider marks 不被遮挡 ---- */
.trade-page .futures-form-side .slider-wrapper {
  min-height: 58px !important;
  padding: 10px 6px 6px !important;
}
.trade-page .futures-form-side .slider-marks {
  padding: 12px 2px 0 !important;
}

/* ---- Key-value rows: 单行显示（标签左、金额右），避免难看换行 ---- */
.trade-page .futures-form-side .fee-estimate-row,
.trade-page .futures-form-side .total-row,
.trade-page .futures-form-side .estimated-received-row,
.trade-page .futures-form-side .available-margin-row {
  flex-wrap: nowrap !important;
  gap: 8px !important;
}
.trade-page .futures-form-side .fee-estimate-label,
.trade-page .futures-form-side .total-label,
.trade-page .futures-form-side .received-label,
.trade-page .futures-form-side .available-margin-label {
  white-space: nowrap !important;
  flex: 0 0 auto !important;
}
.trade-page .futures-form-side .fee-estimate-value,
.trade-page .futures-form-side .total-value,
.trade-page .futures-form-side .received-value,
.trade-page .futures-form-side .available-margin-value {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  text-align: right !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* 数字字重收敛：不要过粗（500/600 为主，当前价/盈亏保留大字重） */
.trade-page .futures-form-side .fee-estimate-value,
.trade-page .futures-form-side .total-value { font-weight: 600 !important; }
.trade-page .futures-form-side .received-value,
.trade-page .futures-form-side .available-margin-value { font-weight: 700 !important; }

/* ---- Position card 字体层级微调 ---- */
.trade-page .position-symbol { font-size: 20px !important; font-weight: 800 !important; line-height: 1.2 !important; }
.trade-page .unrealized-pnl-value { line-height: 1.2 !important; }
.trade-page .position-right .info-value { font-weight: 600 !important; }

@media (max-width: 390px) {
  .trade-page .futures-form-side .form-tools-row .order-type-selector { font-size: 12px !important; padding: 0 8px !important; }
  .trade-page .leverage-inline-btn { min-width: 50px !important; font-size: 12px !important; padding: 0 8px !important; }
  .trade-page .futures-form-side .available-margin-label,
  .trade-page .futures-form-side .available-margin-value,
  .trade-page .futures-form-side .received-label,
  .trade-page .futures-form-side .received-value { font-size: 12px !important; }
}

/* =====================================================================
   PREMIUM REFINEMENT PASS — 合约交易高级化
   实色主操作按钮 / 干净克制的盘口 / 精致的持仓卡片。
   追加在最后以赢得层叠优先级。
   ===================================================================== */

/* ---- 主操作按钮：实色、白字、克制阴影，建立强视觉层级 ---- */
.trade-page .futures-form-side .futures-action-buttons-grid { gap: 10px !important; }

/* 合约「开多」(有兄弟按钮时) 与 「开空」使用实色；现货单按钮维持原样 */
.trade-page .futures-form-side .long-btn-grid:not(:only-child),
.trade-page .futures-form-side .short-btn-grid {
  border: none !important;
  color: #ffffff !important;
  letter-spacing: 0.3px !important;
  transition: transform 0.12s ease, box-shadow 0.2s ease, background 0.2s ease !important;
}
.trade-page .futures-form-side .long-btn-grid:not(:only-child) {
  background: linear-gradient(180deg, #18c884 0%, #10b877 100%) !important;
  box-shadow: 0 6px 16px rgb(16 184 119 / 0.28) !important;
}
.trade-page .futures-form-side .short-btn-grid {
  background: linear-gradient(180deg, #ff5b6a 0%, #f6465d 100%) !important;
  box-shadow: 0 6px 16px rgb(246 70 93 / 0.28) !important;
}
.trade-page .futures-form-side .long-btn-grid:not(:only-child):active:not(:disabled) {
  transform: translateY(1px) !important;
  box-shadow: 0 3px 10px rgb(16 184 119 / 0.24) !important;
  background: linear-gradient(180deg, #10b877, #0c9c66) !important;
}
.trade-page .futures-form-side .short-btn-grid:active:not(:disabled) {
  transform: translateY(1px) !important;
  box-shadow: 0 3px 10px rgb(246 70 93 / 0.24) !important;
  background: linear-gradient(180deg, #f6465d, #e23a51) !important;
}
.trade-page .futures-form-side .long-btn-grid:not(:only-child):disabled,
.trade-page .futures-form-side .short-btn-grid:disabled {
  background: #eef1f4 !important;
  color: #b6bcc6 !important;
  border: none !important;
  box-shadow: none !important;
  opacity: 1 !important;
  filter: none !important;
}

/* ---- 盘口最新价：中性精致卡片，颜色随涨跌 ---- */
.trade-page .futures-orderbook-side .last-price,
.trade-page .orderbook-side .last-price {
  border: 1px solid #eef0f3 !important;
  background: #f7f8fa !important;
  border-radius: 12px !important;
}
.trade-page .last-price.up .price-main { color: #10b877 !important; }
.trade-page .last-price.down .price-main { color: #f6465d !important; }
.trade-page .futures-orderbook-side .price-main,
.trade-page .orderbook-side .price-main {
  font-weight: 700 !important;
  letter-spacing: -0.6px !important;
}
.trade-page .futures-orderbook-side .price-fiat,
.trade-page .orderbook-side .price-fiat { color: #9ca3af !important; }

/* ---- 盘口深度条与数字更克制统一 ---- */
.trade-page .futures-orderbook-side .ask-depth,
.trade-page .orderbook-side .ask-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(246 70 93 / 0.09) 100%) !important;
}
.trade-page .futures-orderbook-side .bid-depth,
.trade-page .orderbook-side .bid-depth {
  background: linear-gradient(90deg, transparent 0%, rgb(16 184 119 / 0.09) 100%) !important;
}
.trade-page .futures-orderbook-side .ask-price,
.trade-page .orderbook-side .ask-price { color: #f6465d !important; }
.trade-page .futures-orderbook-side .bid-price,
.trade-page .orderbook-side .bid-price { color: #10b877 !important; }
.trade-page .order-row { transition: background 0.15s ease !important; }
.trade-page .order-row:active { background: #f2f4f7 !important; }

/* ---- 订单类型 / 杠杆 / 输入框：干净描边卡片 ---- */
.trade-page .futures-form-side .order-type-selector,
.trade-page .leverage-inline-btn {
  background: #f7f8fa !important;
  border: 1px solid #eaecef !important;
  color: #111827 !important;
  border-radius: 12px !important;
}
.trade-page .futures-form-side .input-row {
  background: #f7f8fa !important;
  border: 1px solid #eaecef !important;
}
.trade-page .futures-form-side .input-row:focus-within {
  background: #ffffff !important;
  border-color: rgb(var(--color-brand-rgb) / 0.5) !important;
  box-shadow: 0 0 0 3px rgb(var(--color-brand-rgb) / 0.08) !important;
}
.trade-page .futures-form-side .estimated-received-row {
  background: rgb(var(--color-brand-rgb) / 0.06) !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.14) !important;
}

/* ---- 持仓卡片：精致化层级 ---- */
.trade-page .position-card {
  border: 1px solid #edeff2 !important;
  box-shadow: 0 6px 20px rgb(17 24 39 / 0.05) !important;
  padding: 18px !important;
}
.trade-page .position-card-main {
  grid-template-columns: 1fr 1.5fr 1.1fr !important;
  gap: 12px !important;
}
.trade-page .position-perpetual {
  background: #f3f4f6 !important;
  color: #8a919e !important;
  font-size: 10px !important;
  padding: 2px 6px !important;
}
.trade-page .position-leverage {
  display: inline-block !important;
  margin-top: 4px !important;
  padding: 2px 8px !important;
  background: rgb(var(--color-brand-rgb) / 0.12) !important;
  color: #b8860b !important;
  border-radius: 6px !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}
.trade-page .unrealized-pnl-label { font-size: 11px !important; margin-bottom: 6px !important; }
.trade-page .unrealized-pnl-value { font-size: 26px !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }
.trade-page .unrealized-pnl-percent { font-size: 14px !important; font-weight: 600 !important; }

/* ---- 持仓操作按钮：次操作描边 + 平仓红色调 ---- */
.trade-page .position-actions { gap: 10px !important; }
.trade-page .tp-sl-btn {
  background: #ffffff !important;
  color: #6b7280 !important;
  border: 1px solid #e5e7eb !important;
}
.trade-page .tp-sl-btn:active { background: #f5f6f8 !important; }
.trade-page .close-btn {
  background: rgb(246 70 93 / 0.10) !important;
  color: #f6465d !important;
  border: 1px solid rgb(246 70 93 / 0.4) !important;
}
.trade-page .close-btn:active { background: rgb(246 70 93 / 0.18) !important; }

/* ---- 底部标签：金色下划线，去掉发光 ---- */
.trade-page :deep(.position-tabs .van-tabs__line) {
  background: var(--color-brand) !important;
  box-shadow: none !important;
  height: 3px !important;
  border-radius: 2px !important;
}

/* ---- 顶部控制条：保证金模式文字 ---- */
.trade-page .margin-mode-text { color: #b8860b !important; }

/* =====================================================================
   LAYOUT FIX — 开多/开空按钮完整显示 + 持仓卡片信息不再拥挤
   ===================================================================== */

/* 合约下单卡片改为内容自适应高度，主操作按钮不再被裁剪 */
.trade-page .futures-trade-main { align-items: stretch !important; }
.trade-page .futures-orderbook-side,
.trade-page .futures-form-side {
  height: auto !important;
  min-height: 468px !important;
  max-height: none !important;
}
.trade-page .futures-form-side {
  display: flex !important;
  flex-direction: column !important;
  overflow: visible !important;
}
.trade-page .futures-form-side .futures-action-buttons-grid {
  margin-top: auto !important;
  padding-top: 4px !important;
}

/* 盘口自适应拉伸后，买卖档位向中间价对齐，空白留在远端更自然 */
.trade-page .futures-orderbook-side {
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}
.trade-page .futures-orderbook-side .orderbook-header,
.trade-page .futures-orderbook-side .last-price { flex: 0 0 auto !important; }
.trade-page .futures-orderbook-side .asks-list {
  flex: 1 1 auto !important;
  height: auto !important;
  min-height: 120px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-end !important;
  overflow: hidden !important;
}
.trade-page .futures-orderbook-side .bids-list {
  flex: 1 1 auto !important;
  height: auto !important;
  min-height: 120px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start !important;
  overflow: hidden !important;
}
.trade-page .futures-orderbook-side .last-price { margin: 8px 0 !important; }

/* ---- 持仓卡片：改为竖向分区，信息清晰不拥挤 ---- */
.trade-page .position-card-main {
  display: flex !important;
  flex-direction: column !important;
  gap: 14px !important;
}

/* 头部：交易对 + 方向 + 永续 在左，杠杆在右 */
.trade-page .position-left {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  min-width: 0 !important;
  width: 100% !important;
}
.trade-page .position-symbol-row {
  margin-bottom: 0 !important;
  flex-wrap: nowrap !important;
  white-space: nowrap !important;
  min-width: 0 !important;
}
.trade-page .position-perpetual { white-space: nowrap !important; }
.trade-page .position-leverage { margin: 0 0 0 auto !important; flex: 0 0 auto !important; }

/* 未实现盈亏：左对齐主区，作为视觉焦点 */
.trade-page .position-center {
  text-align: left !important;
  align-items: flex-start !important;
  justify-content: flex-start !important;
  padding: 0 !important;
}
.trade-page .unrealized-pnl-label { margin-bottom: 4px !important; }
.trade-page .unrealized-pnl-value { margin-bottom: 4px !important; }

/* 关键数据：三等分小面板，标签在上、数值在下，绝不截断 */
.trade-page .position-right {
  display: grid !important;
  grid-template-columns: repeat(3, 1fr) !important;
  gap: 10px !important;
  background: #f7f8fa !important;
  border: 1px solid #eef0f3 !important;
  border-radius: 12px !important;
  padding: 12px !important;
}
.trade-page .position-info-row {
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
  min-width: 0 !important;
}
.trade-page .position-right .info-label {
  font-size: 11px !important;
  color: #6b7280 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
.trade-page .position-right .info-value {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: #111827 !important;
  white-space: nowrap !important;
}

/* =====================================================================
   SPOT REFINEMENT — 现货下单区高级化（分段式买卖切换 + 实色主按钮）
   ===================================================================== */

/* 买/卖 切换：分段控件，选中为白底 + 品牌色文字 */
.trade-page .form-side .buy-sell-toggle {
  background: #f2f4f7 !important;
  border: 1px solid #eaecef !important;
  border-radius: 12px !important;
  padding: 4px !important;
}
.trade-page .form-side .toggle-btn {
  background: transparent !important;
  color: #6b7280 !important;
  border-radius: 9px !important;
  box-shadow: none !important;
  text-shadow: none !important;
  font-weight: 700 !important;
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease !important;
}
.trade-page .form-side .buy-btn.active {
  background: #ffffff !important;
  color: #10b877 !important;
  box-shadow: 0 1px 4px rgb(17 24 39 / 0.10) !important;
  text-shadow: none !important;
}
.trade-page .form-side .sell-btn.active {
  background: #ffffff !important;
  color: #f6465d !important;
  box-shadow: 0 1px 4px rgb(17 24 39 / 0.10) !important;
  text-shadow: none !important;
}

/* 主下单按钮：买=实色绿，卖=实色红，白字，克制阴影 */
.trade-page .form-side .submit-btn {
  border: none !important;
  color: #ffffff !important;
  box-shadow: none !important;
  text-shadow: none !important;
  letter-spacing: 0.3px !important;
  transition: transform 0.12s ease, box-shadow 0.2s ease, background 0.2s ease !important;
}
.trade-page .form-side .submit-btn::before { display: none !important; }
.trade-page .form-side .submit-btn.buy {
  background: linear-gradient(180deg, #18c884 0%, #10b877 100%) !important;
  box-shadow: 0 6px 16px rgb(16 184 119 / 0.28) !important;
}
.trade-page .form-side .submit-btn.sell {
  background: linear-gradient(180deg, #ff5b6a 0%, #f6465d 100%) !important;
  box-shadow: 0 6px 16px rgb(246 70 93 / 0.28) !important;
}
.trade-page .form-side .submit-btn.buy:active:not(:disabled) {
  transform: translateY(1px) !important;
  box-shadow: 0 3px 10px rgb(16 184 119 / 0.24) !important;
  background: linear-gradient(180deg, #10b877, #0c9c66) !important;
}
.trade-page .form-side .submit-btn.sell:active:not(:disabled) {
  transform: translateY(1px) !important;
  box-shadow: 0 3px 10px rgb(246 70 93 / 0.24) !important;
  background: linear-gradient(180deg, #f6465d, #e23a51) !important;
}
.trade-page .form-side .submit-btn:disabled {
  opacity: 1 !important;
  filter: none !important;
  background: #eef1f4 !important;
  color: #b6bcc6 !important;
  box-shadow: none !important;
}

/* 预估到账高亮行更柔和统一 */
.trade-page .form-side .estimated-received-row {
  background: rgb(var(--color-brand-rgb) / 0.06) !important;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.14) !important;
  border-radius: 12px !important;
}

/* =====================================================================
   PROMO + BUTTON COLOR — 限时0资金费率徽标 + 开多/开空保留色彩身份
   ===================================================================== */

/* 币种旁「限时0资金费率」促销徽标 */
.trade-page .pair-info .zero-fee-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 3px !important;
  margin-left: 8px !important;
  padding: 3px 9px !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, #fff3df 0%, #ffe7c7 100%) !important;
  border: 1px solid rgb(233 137 12 / 0.30) !important;
  color: #e0850b !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  line-height: 1 !important;
  white-space: nowrap !important;
  letter-spacing: 0 !important;
}
.trade-page .pair-info .zero-fee-badge svg {
  width: 11px !important;
  height: 11px !important;
  flex: 0 0 auto !important;
}
.trade-page .pair-info .price-change { margin-left: auto !important; }

/* 开多/开空 未激活（禁用）时仍保留绿/红色彩，仅降低明度 —— 与主流交易所一致 */
.trade-page .futures-form-side .long-btn-grid:not(:only-child):disabled {
  background: linear-gradient(180deg, #18c884 0%, #10b877 100%) !important;
  color: #ffffff !important;
  opacity: 0.5 !important;
  filter: none !important;
  box-shadow: none !important;
  border: none !important;
}
.trade-page .futures-form-side .short-btn-grid:disabled {
  background: linear-gradient(180deg, #ff5b6a 0%, #f6465d 100%) !important;
  color: #ffffff !important;
  opacity: 0.5 !important;
  filter: none !important;
  box-shadow: none !important;
  border: none !important;
}

/* 现货主按钮禁用态同样保留色彩，保持一致 */
.trade-page .form-side .submit-btn.buy:disabled {
  background: linear-gradient(180deg, #18c884 0%, #10b877 100%) !important;
  color: #ffffff !important;
  opacity: 0.5 !important;
  filter: none !important;
  box-shadow: none !important;
}
.trade-page .form-side .submit-btn.sell:disabled {
  background: linear-gradient(180deg, #ff5b6a 0%, #f6465d 100%) !important;
  color: #ffffff !important;
  opacity: 0.5 !important;
  filter: none !important;
  box-shadow: none !important;
}

/* =====================================================================
   深色模式适配 —— 交易页此前使用硬编码浅色，深色下需重映射到主题变量
   （买卖/开多开空的绿红主色保持不变，仅调整卡片/输入/文字/边框）
   ===================================================================== */
:global(html[data-theme='dark']) .trade-page .futures-trade-container {
  background: var(--color-surface-1) !important;
}

/* 盘口 / 下单卡片 */
:global(html[data-theme='dark']) .trade-page .orderbook-side,
:global(html[data-theme='dark']) .trade-page .form-side,
:global(html[data-theme='dark']) .trade-page .futures-orderbook-side,
:global(html[data-theme='dark']) .trade-page .futures-form-side {
  background: var(--color-surface-2) !important;
  border-color: var(--color-border) !important;
  box-shadow: none !important;
}

/* 盘口表头 / 数量列 / 法币价 */
:global(html[data-theme='dark']) .trade-page .orderbook-header,
:global(html[data-theme='dark']) .trade-page .orderbook-header span,
:global(html[data-theme='dark']) .trade-page .quantity {
  color: var(--color-text-secondary) !important;
}
:global(html[data-theme='dark']) .trade-page .price-fiat {
  color: var(--color-text-muted) !important;
}

/* 最新价卡片 */
:global(html[data-theme='dark']) .trade-page .last-price {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
}

/* 订单类型 / 杠杆按钮 / 输入行 */
:global(html[data-theme='dark']) .trade-page .order-type-selector,
:global(html[data-theme='dark']) .trade-page .leverage-inline-btn,
:global(html[data-theme='dark']) .trade-page .input-row {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
}
:global(html[data-theme='dark']) .trade-page .input-field {
  color: var(--color-text-primary) !important;
  background: transparent !important;
}
:global(html[data-theme='dark']) .trade-page .input-field::placeholder {
  color: var(--color-text-muted) !important;
}

/* 键值行文字 */
:global(html[data-theme='dark']) .trade-page .fee-estimate-label,
:global(html[data-theme='dark']) .trade-page .total-label,
:global(html[data-theme='dark']) .trade-page .received-label,
:global(html[data-theme='dark']) .trade-page .available-margin-label,
:global(html[data-theme='dark']) .trade-page .avail-label {
  color: var(--color-text-secondary) !important;
}
:global(html[data-theme='dark']) .trade-page .fee-estimate-value,
:global(html[data-theme='dark']) .trade-page .total-value,
:global(html[data-theme='dark']) .trade-page .received-value,
:global(html[data-theme='dark']) .trade-page .available-margin-value,
:global(html[data-theme='dark']) .trade-page .avail-value {
  color: var(--color-text-primary) !important;
}

/* 买/卖 分段控件 */
:global(html[data-theme='dark']) .trade-page .buy-sell-toggle {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
}
:global(html[data-theme='dark']) .trade-page .buy-sell-toggle .toggle-btn:not(.active) {
  color: var(--color-text-secondary) !important;
}

/* 禁用主按钮底色（无 buy/sell/long/short 色彩身份时） */
:global(html[data-theme='dark']) .trade-page .submit-btn:disabled:not(.buy):not(.sell) {
  background: var(--color-surface-muted) !important;
  color: var(--color-text-muted) !important;
}

/* 底部区（持仓/委托/成交） */
:global(html[data-theme='dark']) .trade-page .futures-bottom-section,
:global(html[data-theme='dark']) .trade-page .bottom-section {
  background: var(--color-surface-2) !important;
  border-top-color: var(--color-border) !important;
}

/* 持仓卡片 */
:global(html[data-theme='dark']) .trade-page .position-card {
  background: var(--color-surface-2) !important;
  border-color: var(--color-border) !important;
  box-shadow: none !important;
}
:global(html[data-theme='dark']) .trade-page .position-symbol,
:global(html[data-theme='dark']) .trade-page .info-value {
  color: var(--color-text-primary) !important;
}
:global(html[data-theme='dark']) .trade-page .position-perpetual {
  background: var(--color-surface-muted) !important;
  color: var(--color-text-secondary) !important;
}
:global(html[data-theme='dark']) .trade-page .position-right {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
}
:global(html[data-theme='dark']) .trade-page .info-label,
:global(html[data-theme='dark']) .trade-page .unrealized-pnl-label {
  color: var(--color-text-secondary) !important;
}

/* 止盈止损次操作按钮 */
:global(html[data-theme='dark']) .trade-page .tp-sl-btn {
  background: var(--color-surface-1) !important;
  color: var(--color-text-secondary) !important;
  border-color: var(--color-border) !important;
}

/* 空状态文案 */
:global(html[data-theme='dark']) .trade-page .empty-state {
  color: var(--color-text-muted) !important;
}

/* 交易对信息分隔线 */
:global(html[data-theme='dark']) .trade-page .pair-info {
  border-bottom-color: var(--color-border) !important;
}

/* 限时0资金费率徽标（深色下更暗的金色调） */
:global(html[data-theme='dark']) .trade-page .pair-info .zero-fee-badge {
  background: rgb(233 137 12 / 0.14) !important;
  border-color: rgb(233 137 12 / 0.30) !important;
  color: #f0b24a !important;
}

/* 页面根：深色下此前被硬编码为 background:#ffffff，会整屏泛白，必须回退到深色底 */
:global(html[data-theme='dark']) .trade-page {
  background: var(--color-bg) !important;
  background-color: var(--color-bg) !important;
}

/* 顶部页内头部 / 交易对信息栏 */
:global(html[data-theme='dark']) .trade-page .trade-header {
  background: var(--color-surface-1) !important;
  border-bottom-color: var(--color-border) !important;
}
/* 交易对名称此前为 #111827，深色下几乎不可见 */
:global(html[data-theme='dark']) .trade-page .pair-name {
  color: var(--color-text-primary) !important;
}

/* 两列卡片阴影/描边在深色下收敛 */
:global(html[data-theme='dark']) .trade-page .futures-orderbook-side,
:global(html[data-theme='dark']) .trade-page .futures-form-side {
  background: var(--color-surface-2) !important;
  border-color: var(--color-border) !important;
  box-shadow: none !important;
}

/* 盘口买卖挡位次要文字（此前硬编码 #6b7280 尚可，但统一为 token 更清晰） */
:global(html[data-theme='dark']) .trade-page .futures-orderbook-side .order-row .quantity,
:global(html[data-theme='dark']) .trade-page .futures-orderbook-side .price-fiat,
:global(html[data-theme='dark']) .trade-page .futures-orderbook-side .orderbook-header {
  color: var(--color-text-secondary) !important;
}

/* 持仓/委托 Tab 容器与列表 */
:global(html[data-theme='dark']) .trade-page .position-tabs .van-tabs__wrap {
  background: var(--color-surface-2) !important;
}
:global(html[data-theme='dark']) .trade-page .positions-list,
:global(html[data-theme='dark']) .trade-page .orders-list,
:global(html[data-theme='dark']) .trade-page .history-list {
  background: var(--color-surface-2) !important;
}

/* 平仓次操作按钮 */
:global(html[data-theme='dark']) .trade-page .close-btn {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
}

/* 买/卖分段控件选中态：深色下用浅色表面而非纯白刺眼 */
:global(html[data-theme='dark']) .trade-page .form-side .buy-btn.active,
:global(html[data-theme='dark']) .trade-page .form-side .sell-btn.active {
  background: var(--color-surface-elevated, #1f2a3d) !important;
}

.coin-select-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* Dark mode refit audit: final in-component override for late white redesign rules. */
:global(html[data-theme='dark']) .trade-page,
:global(html[data-theme='dark']) .trade-page .futures-trade-container,
:global(html[data-theme='dark']) .trade-page .trade-main,
:global(html[data-theme='dark']) .trade-page .futures-trade-main {
  background: var(--color-bg) !important;
  background-color: var(--color-bg) !important;
  color: var(--color-text-primary) !important;
}

:global(html[data-theme='dark']) .trade-page .trade-tabs,
:global(html[data-theme='dark']) .trade-page .trade-header,
:global(html[data-theme='dark']) .trade-page .pair-info,
:global(html[data-theme='dark']) .trade-page .futures-control-bar,
:global(html[data-theme='dark']) .trade-page .bottom-tabs,
:global(html[data-theme='dark']) .trade-page :deep(.position-tabs .van-tabs__wrap) {
  background: var(--color-surface-1) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .trade-page .orderbook-side,
:global(html[data-theme='dark']) .trade-page .form-side,
:global(html[data-theme='dark']) .trade-page .futures-orderbook-side,
:global(html[data-theme='dark']) .trade-page .futures-form-side,
:global(html[data-theme='dark']) .trade-page .position-card,
:global(html[data-theme='dark']) .trade-page .orders-empty-compact,
:global(html[data-theme='dark']) .trade-page .assets-glass-card,
:global(html[data-theme='dark']) .trade-page .positions-list,
:global(html[data-theme='dark']) .trade-page .orders-list,
:global(html[data-theme='dark']) .trade-page .history-list {
  background: var(--color-bg-card) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .trade-page .buy-sell-toggle,
:global(html[data-theme='dark']) .trade-page .order-type-selector,
:global(html[data-theme='dark']) .trade-page .leverage-inline-btn,
:global(html[data-theme='dark']) .trade-page .input-row,
:global(html[data-theme='dark']) .trade-page .last-price,
:global(html[data-theme='dark']) .trade-page .position-right,
:global(html[data-theme='dark']) .trade-page .position-perpetual,
:global(html[data-theme='dark']) .trade-page .tp-sl-btn,
:global(html[data-theme='dark']) .trade-page .close-btn {
  background: var(--color-bg-input) !important;
  border-color: var(--color-border) !important;
  color: var(--color-text-primary) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .trade-page .input-row:focus-within {
  background: var(--color-bg-input) !important;
  border-color: var(--color-primary-border) !important;
  box-shadow: 0 0 0 3px var(--color-focus-ring) !important;
}

:global(html[data-theme='dark']) .trade-page .pair-name,
:global(html[data-theme='dark']) .trade-page .tab-item.active,
:global(html[data-theme='dark']) .trade-page .input-field,
:global(html[data-theme='dark']) .trade-page .fee-estimate-value,
:global(html[data-theme='dark']) .trade-page .total-value,
:global(html[data-theme='dark']) .trade-page .received-value,
:global(html[data-theme='dark']) .trade-page .available-margin-value,
:global(html[data-theme='dark']) .trade-page .avail-value,
:global(html[data-theme='dark']) .trade-page .position-symbol,
:global(html[data-theme='dark']) .trade-page .position-right .info-value {
  color: var(--color-text-primary) !important;
  -webkit-text-fill-color: var(--color-text-primary) !important;
}

:global(html[data-theme='dark']) .trade-page .tab-item,
:global(html[data-theme='dark']) .trade-page .orderbook-header,
:global(html[data-theme='dark']) .trade-page .quantity,
:global(html[data-theme='dark']) .trade-page .input-label,
:global(html[data-theme='dark']) .trade-page .input-suffix,
:global(html[data-theme='dark']) .trade-page .fee-estimate-label,
:global(html[data-theme='dark']) .trade-page .total-label,
:global(html[data-theme='dark']) .trade-page .received-label,
:global(html[data-theme='dark']) .trade-page .available-margin-label,
:global(html[data-theme='dark']) .trade-page .avail-label,
:global(html[data-theme='dark']) .trade-page .position-right .info-label,
:global(html[data-theme='dark']) .trade-page .unrealized-pnl-label {
  color: var(--color-text-secondary) !important;
}

:global(html[data-theme='dark']) .trade-page .input-field::placeholder,
:global(html[data-theme='dark']) .trade-page .market-price-input,
:global(html[data-theme='dark']) .trade-page .empty-text,
:global(html[data-theme='dark']) .trade-page .price-fiat {
  color: var(--color-text-muted) !important;
  -webkit-text-fill-color: var(--color-text-muted) !important;
}

</style>
