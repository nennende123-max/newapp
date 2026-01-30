<template>
  <div class="trade-page">
    <!-- 固定顶部导航栏 - 子页面模式隐藏 -->
    <div v-if="!isSubPage" class="trade-header">
      <div class="header-center">
        <span class="page-title">{{ pageTitle }}</span>
      </div>
      
      <div class="nav-right-icon-wrap" @click="goToKlineChart">
        <svg viewBox="0 0 1024 1024" class="kline-svg-icon">
          <path d="M896 128H128a64 64 0 0 0-64 64v640a64 64 0 0 0 64 64h768a64 64 0 0 0 64-64V192a64 64 0 0 0-64-64zM320 768H192V448h128v320zm256 0H448V256h128v512zm256 0H704V512h128v256z" fill="#FCD535"></path>
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
        <van-icon name="arrow-down" size="12" color="#FFFFFF" style="margin-left: 4px" />
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
      <!-- 合约控制栏：全仓文本 + 杠杆倍数（左边），资金费率（右边） - 仅在合约模式下显示 -->
      <div v-if="!isSpotMode" class="futures-control-bar">
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
              @click="() => { orderSide = 'buy'; spotSliderValue = 0; amount = ''; }"
            >
              {{ t('trade.buy') }}
            </div>
            <div 
              class="toggle-btn sell-btn" 
              :class="{ active: orderSide === 'sell' }"
              @click="() => { orderSide = 'sell'; spotSliderValue = 0; amount = ''; }"
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

          <div class="order-type-selector" @click="showOrderTypeSheet = true">
            <span>{{ orderType === 'limit' ? t('trade.limit_order') : t('trade.market_order') }}</span>
            <van-icon name="arrow-down" size="12" color="#848E9C" />
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
            <span class="input-suffix">USDT</span>
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
          <!-- 现货模式：使用现货滑块 -->
          <div v-else class="slider-wrapper">
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
          title-active-color="#FCD535" 
          title-inactive-color="#8E8E93" 
          line-width="30px" 
          line-height="3px" 
          color="#FCD535" 
          :border="false"
          class="position-tabs"
        >
          <!-- 持有仓位Tab：仅在合约模式下显示 -->
          <van-tab v-if="!isSpotMode" :title="t('trade.positions_tab', { count: positions.length })">
            <div class="positions-list">
              <div v-if="positions.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="orders-o" size="48" color="#8E8E93" />
                </div>
                <div class="empty-text">{{ t('trade.no_positions') }}</div>
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
                      <span class="info-label">{{ t('trade.entry_price') }}:</span>
                      <span 
                        class="info-value entry-price-value" 
                        :class="isLongPosition(position) ? 'side-long' : 'side-short'"
                      >
                        {{ formatPrice(position.entryPrice) }}
                      </span>
                    </div>
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
              <div v-if="!futuresOrdersList || futuresOrdersList.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="orders-o" size="48" color="#8E8E93" />
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
                  <van-icon name="orders-o" size="48" color="#8E8E93" />
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
                    <van-loading type="spinner" color="#D4AF37" size="16px" />
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
            <van-icon v-if="currentLeverage === leverage" name="success" color="#FCD535" />
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
      :overlay-style="{ backgroundColor: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(10px)' }"
      :style="{ height: 'auto', background: '#0a0a0a' }"
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
import { createOrder, getOrders, cancelOrder as cancelSpotOrderApi } from '@/api/trade';
import { createFuturesOrder, getPositions as getFuturesPositionsApi, closePosition as closeFuturesPositionApi, getFuturesOrders, cancelFuturesOrder as cancelFuturesOrderApi } from '@/api/futures';
import { formatAssetAmount } from '@/utils/format';

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
const maxVisibleRows = ref(50); // 默认最大可见行数

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
  return Math.max(10, Math.min(100, rowsPerSide));
};

// 动态计算显示的买卖单数量
const displayedAsks = computed(() => {
  // 卖单：取最低的 n 行，并倒序排列（高价在上，低价在下）
  return asks.value.slice(0, maxVisibleRows.value).reverse();
});

const displayedBids = computed(() => {
  // 买单：取最高的 n 行（高价在上，低价在下）
  return bids.value.slice(0, maxVisibleRows.value);
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
      
      // 刷新当前委托订单列表（合约）
      console.log('下单成功，正在强制刷新合约委托列表...');
      await fetchFuturesOrders();
      
      // 清空输入框
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
      
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
      
      // 刷新当前委托订单列表（合约）
      console.log('下单成功，正在强制刷新合约委托列表...');
      await fetchFuturesOrders();
      
      // 清空输入框
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
      
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
  background-color: #050505; /* 最深黑 */
  color: #FFFFFF;
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
  scrollbar-color: rgba(212, 175, 55, 0.3) transparent;
}

.trade-scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.trade-scrollable-content::-webkit-scrollbar-track {
  background: transparent;
}

.trade-scrollable-content::-webkit-scrollbar-thumb {
  background: rgba(212, 175, 55, 0.3);
  border-radius: 3px;
}

.trade-scrollable-content::-webkit-scrollbar-thumb:hover {
  background: rgba(212, 175, 55, 0.5);
}

/* ========== 顶部导航栏 ========== */
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px; /* h-12 = 48px */
  padding: 0 16px;
  background-color: #1C1C1E; /* bg-gray-900 */
  flex-shrink: 0; /* 防止被压缩 */
  z-index: 20;
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
  background: linear-gradient(180deg, rgba(5, 5, 5, 0.95) 0%, #050505 100%);
  border-radius: 8px;
  overflow: visible; /* 允许内容自然显示 */
  padding: 0;
  align-self: flex-start; /* 使用 flex-start，确保高度由内容决定 */
  border: 1px solid rgba(212, 175, 55, 0.08);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  /* 使用自然高度，显示完整的 15-20 行 */
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 10px;
  color: #8E8E93;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
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
  background-color: rgba(255, 255, 255, 0.02);
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
    rgba(246, 70, 93, 0.25) 0%, 
    rgba(246, 70, 93, 0.15) 50%,
    rgba(246, 70, 93, 0.05) 100%
  );
  box-shadow: inset -2px 0 8px rgba(246, 70, 93, 0.2);
}

/* 赛博朋克绿色渐变 - 买单 */
.bid-depth { 
  background: linear-gradient(to left, 
    rgba(14, 203, 129, 0.25) 0%, 
    rgba(14, 203, 129, 0.15) 50%,
    rgba(14, 203, 129, 0.05) 100%
  );
  box-shadow: inset -2px 0 8px rgba(14, 203, 129, 0.2);
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
  color: #F6465D; 
  text-align: left; 
  flex: 1;
  font-weight: 600;
  text-shadow: 0 0 6px rgba(246, 70, 93, 0.4);
}

.bid-price { 
  color: #0ECB81; 
  text-align: left; 
  flex: 1;
  font-weight: 600;
  text-shadow: 0 0 6px rgba(14, 203, 129, 0.4);
}

.order-row .quantity { 
  position: relative; 
  z-index: 1; 
  font-size: 13px; 
  color: #8E8E93; 
  text-align: right; 
  flex: 1; 
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.last-price {
  flex-shrink: 0;
  height: 48px;
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.05) 0%, rgba(212, 175, 55, 0.02) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgba(212, 175, 55, 0.15);
  border-bottom: 1px solid rgba(212, 175, 55, 0.15);
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
  background: radial-gradient(circle at center, rgba(212, 175, 55, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.price-main { 
  font-size: 20px; 
  font-weight: 800; 
  color: #FFFFFF; 
  font-variant-numeric: tabular-nums; 
  line-height: 1.2;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: -0.5px;
  text-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
  transition: all 0.3s ease;
}

.price-fiat { 
  font-size: 11px; 
  color: #8E8E93; 
  font-variant-numeric: tabular-nums; 
  line-height: 1; 
  margin-top: 4px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.last-price.up .price-main { 
  color: #0ECB81;
  text-shadow: 0 0 12px rgba(14, 203, 129, 0.5);
}

.last-price.down .price-main { 
  color: #F6465D;
  text-shadow: 0 0 12px rgba(246, 70, 93, 0.5);
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
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 3px;
  border: 1px solid rgba(255, 255, 255, 0.05);
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
  color: #8E8E93;
  position: relative;
  z-index: 1;
}

.buy-btn.active { 
  background: linear-gradient(135deg, #00FFA3 0%, #00D98B 100%);
  color: #000000;
  box-shadow: 0 0 20px rgba(0, 255, 163, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.sell-btn.active { 
  background: linear-gradient(135deg, #FF2E50 0%, #E63950 100%);
  color: #FFFFFF;
  box-shadow: 0 0 20px rgba(255, 46, 80, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.toggle-btn:not(.active):hover {
  color: #D4AF37;
}

.order-type-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 8px;
  font-size: 13px;
  color: #FFFFFF;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  margin-top: 0; /* 确保顶部对齐，与 orderbook-header 对齐 */
}

.order-type-selector:hover {
  background: rgba(212, 175, 55, 0.05);
  border-color: rgba(212, 175, 55, 0.25);
}

.order-type-selector:active { 
  background: rgba(212, 175, 55, 0.08);
  transform: scale(0.98);
}

.leverage-control-bar { margin-bottom: 8px; }
.leverage-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: #FFFFFF;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.leverage-btn:hover {
  background: rgba(212, 175, 55, 0.1);
  border-color: rgba(212, 175, 55, 0.3);
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
}

.leverage-btn:active {
  background: rgba(212, 175, 55, 0.15);
  transform: scale(0.98);
}

.leverage-value { 
  color: #D4AF37; 
  font-weight: 800; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
}
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
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 8px;
  padding: 0 14px;
  height: 44px;
  gap: 8px;
  transition: all 0.3s ease;
}

.input-row:focus-within {
  border-color: #D4AF37;
  background: rgba(212, 175, 55, 0.05);
  box-shadow: 
    0 0 20px rgba(212, 175, 55, 0.15), 
    inset 0 0 20px rgba(212, 175, 55, 0.05),
    inset 0 0 30px rgba(212, 175, 55, 0.08); /* 内发光效果 */
}

.input-label { 
  font-size: 12px; 
  color: #8E8E93; 
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
  color: #FFFFFF; 
  font-size: 16px; 
  font-variant-numeric: tabular-nums; 
  outline: none;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-weight: 600;
}

.input-field::placeholder { 
  color: rgba(142, 142, 147, 0.5);
}

/* 输入框单位标签（后缀） */
.input-suffix {
  font-size: 13px;
  color: #D4AF37; /* text-yellow-500 / Gold */
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
  color: rgba(142, 142, 147, 0.6) !important; 
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
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 600;
  font-size: 10px;
}

.est-value { 
  color: #FFFFFF;
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
  color: #8E8E93;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  min-width: 36px;
  text-align: center;
  font-weight: 600;
  position: relative;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.mark-item:hover {
  color: #D4AF37;
  background: rgba(212, 175, 55, 0.1);
  border-color: rgba(212, 175, 55, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(212, 175, 55, 0.2);
}

.mark-item:active {
  transform: translateY(0) scale(0.95);
}

/* 自定义滑块按钮样式 - 发光钻石 */
.custom-slider-button {
  width: 28px;
  height: 28px;
  color: #000;
  font-size: 10px;
  line-height: 28px;
  text-align: center;
  background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
  border-radius: 50%;
  font-weight: 800;
  box-shadow: 
    0 0 20px rgba(212, 175, 55, 0.6),
    0 4px 12px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  transform: scale(1);
  transition: all 0.3s ease;
}

.custom-slider-button:hover {
  transform: scale(1.1);
  box-shadow: 
    0 0 30px rgba(212, 175, 55, 0.8),
    0 6px 16px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

/* Vant Slider 自定义样式 */
:deep(.van-slider) {
  margin: 0;
}

:deep(.van-slider__bar) {
  background: linear-gradient(90deg, #D4AF37 0%, rgba(212, 175, 55, 0.3) 100%);
  height: 3px;
  border-radius: 2px;
  box-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
}

:deep(.van-slider__track) {
  background: rgba(212, 175, 55, 0.1);
  height: 3px;
  border-radius: 2px;
}

/* 保留旧样式以兼容（如果其他地方还在使用） */
.percent-row { display: flex; gap: 8px; }
.percent-btn {
  flex: 1; height: 32px; display: flex; align-items: center; justify-content: center;
  background-color: #1C1C1E; border-radius: 4px; font-size: 12px; color: #EAECEF; cursor: pointer;
}
.percent-btn.active { background-color: #FCD535; color: #000000; font-weight: 600; }

.fee-estimate-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; 
  height: auto; 
  margin-bottom: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.fee-estimate-label { 
  font-size: 11px; 
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.fee-estimate-value { 
  font-size: 13px; 
  color: #FFFFFF; 
  font-weight: 700; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  display: flex; 
  align-items: center; 
  gap: 4px;
}

.fee-usdt-note { 
  font-size: 10px; 
  color: #8E8E93; 
  font-weight: 400; 
  margin-left: 4px;
}

.discount-badge { 
  font-size: 11px; 
  color: #D4AF37; 
  font-weight: 600;
  text-shadow: 0 0 4px rgba(212, 175, 55, 0.4);
}

.total-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; 
  height: auto; 
  margin-bottom: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.total-label { 
  font-size: 11px; 
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.total-value { 
  font-size: 14px; 
  color: #FFFFFF; 
  font-weight: 700; 
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.estimated-received-row {
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 14px 16px;
  background: rgba(212, 175, 55, 0.06);
  backdrop-filter: blur(10px);
  border-radius: 8px; 
  height: auto; 
  margin-bottom: 16px;
  border: 1px solid rgba(212, 175, 55, 0.15);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.1), inset 0 0 20px rgba(212, 175, 55, 0.05);
}

.received-label { 
  font-size: 12px; 
  color: rgba(212, 175, 55, 0.8); 
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.received-value { 
  font-size: 16px; 
  color: #D4AF37; 
  font-weight: 800; 
  font-variant-numeric: tabular-nums; 
  letter-spacing: -0.3px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
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
  color: #8E8E93; 
  margin-right: 6px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-size: 10px;
}

.avail-value { 
  color: #FFFFFF; 
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
  color: #8E8E93; /* Grey */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.available-balance-value {
  font-size: 15px;
  color: #FFFFFF; /* Bright White/Gold */
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.3); /* 轻微金色发光 */
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn.buy { 
  background: linear-gradient(135deg, #00FFA3 0%, #00D98B 100%);
  color: #000000;
  box-shadow: 0 4px 20px rgba(0, 255, 163, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.submit-btn.buy:hover:not(:disabled) {
  box-shadow: 0 6px 30px rgba(0, 255, 163, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.submit-btn.sell { 
  background: linear-gradient(135deg, #FF2E50 0%, #E63950 100%);
  color: #FFFFFF;
  box-shadow: 0 4px 20px rgba(255, 46, 80, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.submit-btn.sell:hover:not(:disabled) {
  box-shadow: 0 6px 30px rgba(255, 46, 80, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
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
  background: linear-gradient(180deg, #050505 0%, rgba(5, 5, 5, 0.98) 100%);
  border-top: 1px solid rgba(212, 175, 55, 0.1);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0; /* 防止被压缩 */
  position: sticky;
  top: 0;
  background: linear-gradient(180deg, #050505 0%, rgba(5, 5, 5, 0.98) 100%);
  z-index: 10;
  backdrop-filter: blur(10px);
}

.bottom-tabs .tab-item {
  font-size: 14px; 
  color: #8E8E93; 
  cursor: pointer; 
  padding-bottom: 8px; 
  position: relative; 
  transition: all 0.3s ease;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.bottom-tabs .tab-item:hover {
  color: rgba(212, 175, 55, 0.7);
}

.bottom-tabs .tab-item.active { 
  color: #D4AF37; 
  font-weight: 700;
}

.bottom-tabs .tab-item.active::after {
  content: ''; 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  right: 0; 
  height: 3px; 
  background: linear-gradient(90deg, #D4AF37 0%, #FFD700 100%);
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.6);
  border-radius: 2px 2px 0 0;
}

.bottom-content {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgba(5, 5, 5, 0.98) 0%, #050505 100%);
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
  color: #8E8E93; 
  font-weight: 500;
}

/* 紧凑空状态样式已在上面定义 */

.order-item {
  display: flex; 
  align-items: center; 
  padding: 10px 12px; /* 减少内边距，更紧凑 */
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; /* 更小的圆角 */
  border: 1px solid rgba(212, 175, 55, 0.1); 
  transition: all 0.2s ease;
  flex-shrink: 0; /* 防止压缩 */
}

.order-item:hover {
  background: rgba(212, 175, 55, 0.05);
  border-color: rgba(212, 175, 55, 0.2);
}

.order-item:active { 
  background: rgba(212, 175, 55, 0.08);
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
  background-color: rgba(0, 255, 163, 0.15); 
  color: #00FFA3; 
}

.order-side-badge.sell { 
  background-color: rgba(255, 46, 80, 0.15); 
  color: #FF2E50; 
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
  background-color: rgba(239, 68, 68, 0.2); /* bg-red-500/20 - 浅红色背景 */
  color: #EF4444; /* text-red-500 - 鲜艳的红色 */
  border: 1px solid rgba(239, 68, 68, 0.3); /* 细红线边框 */
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.2);
}

/* 强平订单整体样式 */
.order-item.liquidation-order {
  border-left: 3px solid #EF4444; /* 左侧红色边框标识 */
  background-color: rgba(239, 68, 68, 0.05); /* 轻微红色背景 */
}

/* 强平订单的已实现盈亏样式 - 巨额负数红色加粗 */
.order-pnl.pnl-liquidation {
  font-weight: 900;
  font-size: 14px;
  color: #EF4444 !important; /* 强制红色 */
  text-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.order-pnl.pnl-liquidation.pnl-negative {
  color: #DC2626 !important; /* text-red-600 - 更深的红色 */
  font-weight: 900;
  text-shadow: 
    0 0 10px rgba(220, 38, 38, 0.6),
    0 0 20px rgba(220, 38, 38, 0.3);
}

.order-symbol-time { 
  display: flex; 
  flex-direction: column; 
  gap: 2px; /* 更紧凑 */
}

.order-symbol { 
  font-size: 12px; /* 更小 */
  font-weight: 700; 
  color: #FFFFFF; 
}

.order-time { 
  font-size: 10px; /* 更小 */
  color: #8E8E93; 
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
  color: #FFFFFF; 
  font-family: 'DIN Alternate', monospace; 
}

.order-quantity { 
  font-size: 11px; /* 更小 */
  color: #8E8E93; 
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
  color: #FFFFFF;
  font-variant-numeric: tabular-nums;
}

.history-order-details {
  display: flex;
  align-items: center;
}

.history-order-price-quantity {
  font-size: 11px;
  color: #8E8E93;
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
  color: #0ECB81; /* 正数绿色 */
}

.history-order-pnl.pnl-negative {
  color: #F6465D; /* 负数红色 */
}

.history-order-pnl.pnl-zero {
  color: #8E8E93; /* 0 显示灰色 */
  font-weight: 600;
}

.history-order-pnl.pnl-liquidation {
  color: #EF4444 !important;
  font-weight: 900;
  font-size: 17px; /* 强平订单更大字号 */
  text-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.history-order-pnl.pnl-liquidation.pnl-negative {
  color: #DC2626 !important;
  text-shadow: 
    0 0 10px rgba(220, 38, 38, 0.6),
    0 0 20px rgba(220, 38, 38, 0.3);
}

.history-order-time {
  font-size: 10px; /* text-xs */
  color: #8E8E93; /* text-gray-500 */
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
  color: #D4AF37;
}

.loading-text {
  font-size: 12px;
  color: #D4AF37;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 没有更多数据状态 */
.history-no-more {
  font-size: 10px; /* text-xs */
  color: #6B7280; /* text-gray-600 */
  text-align: center;
  padding: 16px 0;
  letter-spacing: 0.3px; /* tracking-wider */
  font-weight: 500;
  opacity: 0.7;
}

.cancel-btn { 
  padding: 5px 12px; /* 更紧凑 */
  background: rgba(255, 46, 80, 0.1); 
  color: #FF2E50; 
  border: 1px solid rgba(255, 46, 80, 0.2); 
  border-radius: 6px; 
  font-size: 11px; /* 更小 */
  font-weight: 600; 
  transition: all 0.2s ease;
  cursor: pointer;
}

.cancel-btn:hover {
  background: rgba(255, 46, 80, 0.15);
  border-color: rgba(255, 46, 80, 0.3);
}

.cancel-btn:active { 
  background: rgba(255, 46, 80, 0.2); 
}

/* ========== 资产玻璃拟态卡片 ========== */
.assets-glass-card {
  background: rgba(255, 255, 255, 0.05); /* bg-white/5 */
  border-radius: 12px; /* rounded-xl */
  padding: 16px; /* p-4 */
  margin-top: 16px; /* mt-4 */
  border: 1px solid rgba(255, 255, 255, 0.1); /* border border-white/10 */
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
  background: rgba(212, 175, 55, 0.15);
  flex-shrink: 0;
}

.asset-hud-label { 
  font-size: 10px; /* 非常小的标签 */
  color: #8E8E93; 
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1;
}

.asset-hud-value { 
  font-size: 14px; /* 适中大小的数值 */
  font-weight: 800; 
  color: #D4AF37; 
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 6px rgba(212, 175, 55, 0.3);
  letter-spacing: -0.2px;
  line-height: 1.2;
  white-space: nowrap;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.coin-select-popup { 
  background: linear-gradient(180deg, #050505 0%, rgba(5, 5, 5, 0.98) 100%) !important;
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

.coin-select-container { 
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  background: transparent;
}

.coin-select-header { 
  padding: 20px 16px 16px; 
  border-bottom: 1px solid rgba(212, 175, 55, 0.1); 
  flex-shrink: 0;
  background: linear-gradient(180deg, rgba(5, 5, 5, 0.95) 0%, transparent 100%);
}

.coin-select-title { 
  font-size: 18px; 
  font-weight: 800; 
  color: #D4AF37; 
  margin: 0; 
  text-align: left;
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.3);
}

.coin-list { 
  flex: 1; 
  overflow-y: auto; 
  padding: 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(212, 175, 55, 0.3) transparent;
}

.coin-list::-webkit-scrollbar {
  width: 6px;
}

.coin-list::-webkit-scrollbar-track {
  background: transparent;
}

.coin-list::-webkit-scrollbar-thumb {
  background: rgba(212, 175, 55, 0.3);
  border-radius: 3px;
}

.coin-list::-webkit-scrollbar-thumb:hover {
  background: rgba(212, 175, 55, 0.5);
}

.coin-item { 
  padding: 16px; 
  display: flex; 
  flex-direction: column; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.05); 
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
  background: linear-gradient(180deg, #D4AF37 0%, #FFD700 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.coin-item:hover {
  background: rgba(212, 175, 55, 0.05);
}

.coin-item:active { 
  background: rgba(212, 175, 55, 0.08);
}

.coin-item-active { 
  background: rgba(212, 175, 55, 0.08);
  border-left: 3px solid #D4AF37;
}

.coin-item-active::before {
  opacity: 1;
}

.coin-name { 
  font-size: 16px; 
  font-weight: 700; 
  color: #FFFFFF; 
  margin: 0;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.coin-item-active .coin-name {
  color: #D4AF37;
  text-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
}

.coin-pair { 
  font-size: 12px; 
  color: #8E8E93; 
  margin-top: 6px;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}
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
  background: linear-gradient(180deg, rgba(5, 5, 5, 0.95) 0%, #050505 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05); /* 与 pair-info 一致 */
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
  color: rgba(212, 175, 55, 0.8);
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
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  border: 1px solid rgba(212, 175, 55, 0.1);
}

.funding-rate-label {
  font-size: 10px;
  color: #8E8E93;
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
  color: #00FFA3;
  text-shadow: 0 0 8px rgba(0, 255, 163, 0.4);
}

.funding-rate-value.negative {
  color: #FF2E50;
  text-shadow: 0 0 8px rgba(255, 46, 80, 0.4);
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
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  color: #8E8E93;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.asset-value {
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.asset-value.pnl-positive {
  color: #32D74B;
}

.asset-value.pnl-negative {
  color: #FF453A;
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.long-btn:hover::before, .short-btn:hover::before {
  left: 100%;
}

/* 开多按钮 - 霓虹绿色渐变 */
.long-btn {
  background: linear-gradient(135deg, #00FFA3 0%, #00D98B 50%, #00C97A 100%);
  color: #000000;
  box-shadow: 
    0 4px 20px rgba(0, 255, 163, 0.4),
    0 0 30px rgba(0, 255, 163, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.long-btn:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgba(0, 255, 163, 0.6),
    0 0 40px rgba(0, 255, 163, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.long-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

/* 开空按钮 - 霓虹红色渐变 */
.short-btn {
  background: linear-gradient(135deg, #FF2E50 0%, #E63950 50%, #D62847 100%);
  color: #FFFFFF;
  box-shadow: 
    0 4px 20px rgba(255, 46, 80, 0.4),
    0 0 30px rgba(255, 46, 80, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.short-btn:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgba(255, 46, 80, 0.6),
    0 0 40px rgba(255, 46, 80, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.long-btn-grid:hover::before, .short-btn-grid:hover::before {
  left: 100%;
}

/* 开多按钮 - Grid 版本 - 霓虹绿色渐变 */
.long-btn-grid {
  background: linear-gradient(to right, #10b981 0%, #059669 100%); /* emerald-500 to green-600 */
  color: #FFFFFF;
  font-weight: 800;
  box-shadow: 
    0 4px 20px rgba(16, 185, 129, 0.3), /* shadow-lg shadow-green-500/30 */
    0 0 30px rgba(16, 185, 129, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
.long-btn-grid:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgba(16, 185, 129, 0.5),
    0 0 40px rgba(16, 185, 129, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.long-btn-grid:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

/* 开空按钮 - Grid 版本 - 霓虹红色渐变 */
.short-btn-grid {
  background: linear-gradient(to right, #f43f5e 0%, #e11d48 100%); /* rose-500 to red-600 */
  color: #FFFFFF;
  font-weight: 800;
  box-shadow: 
    0 4px 20px rgba(244, 63, 94, 0.3), /* shadow-lg shadow-red-500/30 */
    0 0 30px rgba(244, 63, 94, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.short-btn-grid:hover:not(:disabled) {
  box-shadow: 
    0 6px 30px rgba(244, 63, 94, 0.5),
    0 0 40px rgba(244, 63, 94, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
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
  background: linear-gradient(180deg, #050505 0%, rgba(5, 5, 5, 0.98) 100%);
  border-top: 1px solid rgba(212, 175, 55, 0.1);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
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
  background: linear-gradient(180deg, #050505 0%, rgba(5, 5, 5, 0.98) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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
  color: #8E8E93;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-bottom: 8px;
  transition: all 0.3s ease;
}

:deep(.position-tabs .van-tab--active) {
  color: #D4AF37;
  font-weight: 700;
}

:deep(.position-tabs .van-tabs__line) {
  background: linear-gradient(90deg, #D4AF37 0%, #FFD700 100%);
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.6);
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
  background: rgba(212, 175, 55, 0.3);
  border-radius: 3px;
}

:deep(.position-tabs .van-tab__panel::-webkit-scrollbar-thumb:hover) {
  background: rgba(212, 175, 55, 0.5);
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
  color: #8E8E93;
  font-size: 14px;
  font-weight: 500;
  width: 100%;
  box-sizing: border-box;
}

.empty-state .empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
  filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.2));
}

.empty-state .empty-text {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 500;
}

.position-card {
  background: rgba(255, 255, 255, 0.05); /* bg-white/5 - 玻璃拟态效果 */
  backdrop-filter: blur(16px); /* backdrop-blur-md */
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1); /* border-white/10 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
  background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.position-card:hover {
  background: rgba(212, 175, 55, 0.05);
  border-color: rgba(212, 175, 55, 0.25);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
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
  background-color: #0ECB81; /* 绿底 */
  color: #FFFFFF; /* 白字 */
  box-shadow: 0 0 8px rgba(14, 203, 129, 0.3);
}

.position-side-badge.side-short {
  background-color: #F6465D; /* 红底 */
  color: #FFFFFF; /* 白字 */
  box-shadow: 0 0 8px rgba(246, 70, 93, 0.3);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.unrealized-pnl-label {
  font-size: 11px;
  color: #8E8E93;
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
  color: #0ECB81;
  text-shadow: 
    0 0 20px rgba(14, 203, 129, 0.6),
    0 0 40px rgba(14, 203, 129, 0.3);
}

.unrealized-pnl-value.negative {
  color: #F6465D;
  text-shadow: 
    0 0 20px rgba(246, 70, 93, 0.6),
    0 0 40px rgba(246, 70, 93, 0.3);
}

.unrealized-pnl-percent {
  font-size: 17px;
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
  color: #8E8E93;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

/* 开仓均价颜色 - 根据方向变化 */
.entry-price-value.side-long {
  color: #0ECB81; /* 多单绿色 */
  text-shadow: 0 0 8px rgba(14, 203, 129, 0.4);
}

.entry-price-value.side-short {
  color: #F6465D; /* 空单红色 */
  text-shadow: 0 0 8px rgba(246, 70, 93, 0.4);
}

.liquidation-price {
  color: #F6465D;
  font-weight: 800;
  font-size: 14px;
  text-shadow: 0 0 8px rgba(255, 46, 80, 0.4);
}

.position-actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid rgba(212, 175, 55, 0.1);
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
  background: rgba(212, 175, 55, 0.1);
  color: #D4AF37;
  border: 1px solid rgba(212, 175, 55, 0.3);
  backdrop-filter: blur(10px);
}

.tp-sl-btn:hover {
  background: rgba(212, 175, 55, 0.15);
  border-color: rgba(212, 175, 55, 0.4);
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2);
  transform: translateY(-2px);
}

.tp-sl-btn:active {
  background: rgba(212, 175, 55, 0.2);
  transform: translateY(0);
}

.close-btn {
  background: rgba(255, 46, 80, 0.1);
  color: #FF2E50;
  border: 1px solid rgba(255, 46, 80, 0.3);
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 46, 80, 0.15);
  border-color: rgba(255, 46, 80, 0.4);
  box-shadow: 0 4px 12px rgba(255, 46, 80, 0.2);
  transform: translateY(-2px);
}

.close-btn:active {
  background: rgba(255, 46, 80, 0.2);
  transform: translateY(0);
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

.premium-gold-button.disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.3);
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
  color: #FF453A;
  font-weight: 600;
  padding: 8px 12px;
  background: rgba(255, 69, 58, 0.1);
  border-radius: 6px;
  border-left: 3px solid #FF453A;
}

/* 输入框错误状态 */
.input-error {
  border-color: #FF453A !important;
  background: rgba(255, 69, 58, 0.05) !important;
}

/* 百分比按钮禁用状态 */
.percent-tag.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
  background: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.3) !important;
}
</style>