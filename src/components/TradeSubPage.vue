<template>
  <div class="trade-sub-page">
    <!-- 顶部导航栏 - 玻璃拟态效果 -->
    <div class="trade-sub-navbar">
      <div class="navbar-left">
        <van-icon 
          name="arrow-left" 
          size="20" 
          color="var(--color-accent)" 
          class="back-icon"
          @click="handleBack"
        />
      </div>
      <div class="navbar-center">
        <span class="navbar-title">{{ formattedTitle }}</span>
      </div>
      <div class="navbar-right">
        <div class="lang-icon-wrapper" @click="handleLanguageClick">
          <van-icon name="globe-o" size="18" color="var(--color-accent)" />
        </div>
      </div>
    </div>

    <!-- 主体内容：使用 TradePanel 组件 -->
    <div class="trade-sub-content">
      <!-- Tab 切换：现货/合约 -->
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

      <!-- 交易对信息 -->
      <div class="pair-info">
        <div class="pair-selector" @click="showCoinSelect = true">
          <span class="pair-name">{{ symbol }}/USDT</span>
          <van-icon name="arrow-down" size="12" color="var(--color-text-primary)" style="margin-left: 4px" />
        </div>
        <div class="price-change" :class="{ positive: priceChange >= 0 }">
          {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
        </div>
      </div>

      <!-- 核心交易区域：使用 TradePanel 组件 -->
      <TradePanel 
        :initial-symbol="symbol"
        :force-trade-tab="activeTradeTab"
        :initial-mode="activeTradeTab"
        :is-sub-page="true"
        :key="`${activeTradeTab}-${symbol}`"
      />

      <!-- 现货交易界面（保留原有代码作为备用） -->
      <div v-if="false && activeTradeTab === 'spot'" class="trade-container">
        <div class="trade-main">
          <!-- 左侧：盘口区 -->
          <div ref="orderBookContainerRef" class="orderbook-side left-order-book">
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

          <!-- 右侧：交易表单 -->
          <div ref="orderFormRef" class="form-side right-trade-form">
          <div class="buy-sell-toggle">
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
              <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
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
        <div class="trade-container">
          <div class="futures-trade-main">
            <!-- 左侧：盘口区 -->
            <div ref="orderBookContainerRef" class="futures-orderbook-side left-order-book">
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

            <!-- 右侧：交易表单 -->
            <div ref="orderFormRef" class="futures-form-side right-trade-form">
              <!-- 资产信息面板：合约模式下显示合约资产 -->
              <div class="futures-asset-panel asset-info">
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

            <div class="order-type-selector" @click="showOrderTypeSheet = true">
              <span>{{ orderType === 'limit' ? t('trade.limit_order') : t('trade.market_order') }}</span>
              <van-icon name="arrow-down" size="12" color="var(--color-text-muted)" />
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
              <span class="input-suffix">USDT</span>
            </div>

            <div class="input-row">
              <input
                v-model="futuresAmount"
                type="number"
                :placeholder="t('trade.amount_placeholder')"
                class="input-field no-spinner"
                @input="handleFuturesAmountInput"
              />
              <span class="input-suffix">{{ currentCoinConfig.baseCoin }}</span>
            </div>

            <!-- 杠杆滑块：仅在合约模式下显示 -->
            <div class="slider-wrapper">
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

            <!-- 费用和总额 -->
            <div class="fee-estimate-row">
              <span class="fee-estimate-label">{{ t('trade.estimated_fee') }}(USDT)</span>
              <span class="fee-estimate-value">
                {{ formatFuturesEstimatedFee }}
              </span>
            </div>

            <div class="total-row">
              <span class="total-label">{{ t('trade.total') }}(USDT)</span>
              <span class="total-value">
                {{ formatFuturesTotalAmount }}
              </span>
            </div>

            <!-- 保证金金额：仅在合约模式下显示 -->
            <div class="estimated-received-row">
              <span class="received-label">{{ t('trade.margin_amount') }}</span>
              <span class="received-value">{{ futuresMargin > 0 ? futuresMargin.toFixed(2) : '0.00' }} USDT</span>
            </div>

            <!-- 操作按钮：合约模式：开多/开空按钮 -->
            <div class="futures-action-buttons-grid">
              <button 
                class="long-btn-grid"
                :disabled="!isFuturesFormValid || isLoading"
                @click="handleLong"
              >
                {{ t('trade.open_long') }}
              </button>
              <button 
                class="short-btn-grid"
                :disabled="!isFuturesFormValid || isLoading"
                @click="handleShort"
              >
                {{ t('trade.open_short') }}
              </button>
              </div>
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
                      <!-- 止盈止损显示 - 使用标准化字段名 take_profit 和 stop_loss -->
                      <div v-if="position.take_profit || position.stop_loss" class="tpsl-display">
                        <span v-if="position.take_profit" class="tpsl-item tp-item">
                          止盈: {{ formatPrice(position.take_profit) }}
                        </span>
                        <span v-if="position.stop_loss" class="tpsl-item sl-item">
                          止损: {{ formatPrice(position.stop_loss) }}
                        </span>
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

                  <!-- TP/SL Display Section (Local Memory) -->
                  <div class="tpsl-display-section">
                    <div class="tpsl-col">
                      <span class="tpsl-label">止盈 (TP)</span>
                      <span class="tpsl-value tp-value">
                        {{ position.tp || position.take_profit || position.takeProfit || '--' }}
                      </span>
                    </div>
                    <div class="tpsl-col">
                      <span class="tpsl-label">止损 (SL)</span>
                      <span class="tpsl-value sl-value">
                        {{ position.sl || position.stop_loss || position.stopLoss || '--' }}
                      </span>
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
                <div v-if="futuresOrdersList.length === 0" class="empty-state">
                  {{ t('trade.no_orders') }}
                </div>
                <div v-else>
                  <div 
                    v-for="(order, index) in futuresOrdersList"
                    :key="order.order_id || index"
                    class="order-item"
                  >
                    <div class="order-left">
                      <div class="order-side-badge" :class="order.side.toLowerCase()">
                        {{ order.side === 'BUY' ? t('trade.buy') : t('trade.sell') }}
                      </div>
                      <div class="order-symbol-time">
                        <span class="order-symbol">{{ order.symbol }}</span>
                        <span class="order-time">{{ formatOrderTime(order.timestamp) }}</span>
                      </div>
                    </div>
                    
                    <div class="order-center">
                      <div class="order-price">{{ formatPrice(order.price) }}</div>
                      <div class="order-quantity">{{ formatQuantity(order.quantity || order.amount) }} / {{ formatQuantity(order.quantity || order.amount) }}</div>
                    </div>
                    
                    <div class="order-right">
                      <button class="cancel-btn" @click="cancelFuturesOrder(order.order_id)">{{ t('trade.cancel') }}</button>
                    </div>
                  </div>
                </div>
              </div>
            </van-tab>
            <van-tab :title="t('trade.trade_history_tab')">
              <div class="history-list">
                <div v-if="futuresHistoryList.length === 0" class="empty-state">
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
                          :class="order.side.toLowerCase()"
                        >
                          {{ order.side === 'BUY' ? t('trade.buy') : t('trade.sell') }}
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

      <!-- 现货底部：委托与资产 -->
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

    <!-- 订单类型选择弹窗 -->
    <van-action-sheet
      v-model:show="showOrderTypeSheet"
      :actions="orderTypeOptions"
      @select="onOrderTypeSelect"
      :cancel-text="t('common.cancel')"
      :title="t('trade.select_order_type')"
      class="custom-action-sheet" 
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
        <div class="modal-drag-indicator"></div>
        
        <div class="premium-modal-header">
          <div class="header-title-wrap">
            <span class="gold-dot"></span>
            <h3>{{ t('trade.take_profit_stop_loss') }}</h3>
          </div>
          <van-icon name="cross" @click="showTPSLPopup = false" class="premium-close-btn" />
        </div>

        <div class="premium-tpsl-form">
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

          <div class="premium-form-group">
            <div class="group-label-row">
              <label>{{ t('trade.stop_loss_price') }}</label>
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

          <button class="premium-gold-button" @click="confirmTPSL">
            {{ t('trade.confirm') }}
          </button>
        </div>
      </div>
    </van-popup>

    <!-- 语言选择弹窗 -->
    <LanguageSelect ref="langRef" />

    <!-- 语言选择弹窗 -->
    <LanguageSelect ref="langRef" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated, onDeactivated, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, Icon, Popup, Empty, ActionSheet, Tabs, Tab, showConfirmDialog, Slider } from 'vant';
import { useAssetStore } from '@/stores/assets';
import { useMarketStore } from '@/stores/market';
import { useTradeStore } from '@/stores/trade';
import { createOrder, getOrders, cancelOrder as cancelSpotOrderApi } from '@/api/trade';
import TradePanel from '@/components/trade/TradePanel.vue';
import { createFuturesOrder, getPositions as getFuturesPositionsApi, closePosition as closeFuturesPositionApi, getFuturesOrders, cancelFuturesOrder as cancelFuturesOrderApi, setPositionTPSL } from '@/api/futures';
import { formatAssetAmount } from '@/utils/format';
import LanguageSelect from './LanguageSelect.vue';

defineOptions({
  name: 'TradeSubPage'
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const langRef = ref(null);
const assetStore = useAssetStore();
const marketStore = useMarketStore();
const tradeStore = useTradeStore();

// 从URL参数获取交易对、方向和交易类型
const symbol = ref(route.query.symbol || 'BTC');
const orderSide = ref(route.query.side === 'buy' || route.query.side === 'sell' ? route.query.side : 'buy');

// 智能解析交易类型
const detectTradeType = () => {
  if (route.query.type === 'spot' || route.query.type === 'futures') {
    return route.query.type;
  }
  const symbolStr = String(symbol.value || '').toUpperCase();
  const futuresSymbols = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TRX', 'BEAT', 'AIC'];
  const baseSymbol = symbolStr.replace('/USDT', '').replace('USDT', '');
  if (symbolStr.includes('USDT') && !futuresSymbols.includes(baseSymbol)) {
    return 'spot';
  }
  return 'futures';
};

const activeTradeTab = ref(detectTradeType());

// 计算显示标题 - 强制移除"永续"二字
const formattedTitle = computed(() => {
  const symbolText = `${symbol.value}/USDT`;
  // 强制移除 "永续" 及可能的空格
  return symbolText.replace(/\s*永续/g, '').trim();
});

// 保留 displayTitle 以兼容旧代码
const displayTitle = formattedTitle;

// 币种配置
const coinConfigs = {
  'BTC/USDT': { priceFixed: 2, amountFixed: 6, step: 0.01, baseCoin: 'BTC' },
  'ETH/USDT': { priceFixed: 2, amountFixed: 4, step: 0.01, baseCoin: 'ETH' },
  'BNB/USDT': { priceFixed: 2, amountFixed: 3, step: 0.1, baseCoin: 'BNB' },
  'SOL/USDT': { priceFixed: 2, amountFixed: 2, step: 0.01, baseCoin: 'SOL' },
  'DOGE/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'DOGE' },
  'TRX/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'TRX' },
  'BEAT/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'BEAT' },
  'AIC/USDT': { priceFixed: 4, amountFixed: 2, step: 0.0001, baseCoin: 'AIC' }
};

const selectedCoin = computed(() => `${symbol.value}/USDT`);
const currentCoinConfig = computed(() => coinConfigs[selectedCoin.value] || coinConfigs['BTC/USDT']);

// 现货交易相关变量
const showCoinSelect = ref(false);
const coinList = ref([
  { symbol: 'BTC' }, { symbol: 'ETH' }, { symbol: 'BNB' }, { symbol: 'SOL' },
  { symbol: 'DOGE' }, { symbol: 'TRX' }, { symbol: 'BEAT' }, { symbol: 'AIC' }
]);
const orderType = ref('limit');
const price = ref('');
const amount = ref('');
const priceChange = ref(1.83);
const lastPrice = ref(92255.50);
const activeOrderTab = ref('orders');
const selectedPercent = ref(null);
const spotSliderValue = ref(0);
const spotOrdersList = ref([]);
const showOrderTypeSheet = ref(false);
const isLoading = ref(false);

// 合约交易相关变量
const currentLeverage = ref(20);
const showLeveragePopup = ref(false);
const marginMode = ref('cross');
const markPrice = ref(92255.50);
const futuresPrice = ref('');
const futuresAmount = ref('');
const selectedFuturesPercent = ref(null);
const futuresSliderValue = ref(0);
const activePositionTab = ref(0);
const positions = ref([]);
const futuresOrdersList = ref([]);
const futuresHistoryList = ref([]);
const historyPage = ref(1);
const historyPageSize = ref(20);
const historyHasMore = ref(true);
const historyLoading = ref(false);
const loadMoreTrigger = ref(null);
let historyObserver = null;
const showTPSLPopup = ref(false);
const currentTPSLPosition = ref(null);
const tpSlForm = ref({
  takeProfitPrice: '',
  stopLossPrice: ''
});

// ========== 客户端内存功能：使用 localStorage 记住用户的 TP/SL 输入 ==========
// 创建唯一的存储键（基于交易对）
const getTPSLStorageKey = (symbol) => {
  if (!symbol) return null;
  // 标准化 symbol：移除 /USDT，统一格式
  const normalizedSymbol = symbol.replace('/USDT', '').replace('USDT', '').toUpperCase();
  return `tpsl_mem_${normalizedSymbol}`;
};

// 保存 TP/SL 到 localStorage
const saveTPSLToLocalStorage = (symbol, tp, sl) => {
  const key = getTPSLStorageKey(symbol);
  if (!key) return;
  
  try {
    const data = {
      tp: tp || null,
      sl: sl || null,
      timestamp: Date.now()
    };
    localStorage.setItem(key, JSON.stringify(data));
    console.log('[localStorage] 已保存 TP/SL:', { key, data });
  } catch (error) {
    console.error('[localStorage] 保存失败:', error);
  }
};

// 从 localStorage 读取 TP/SL
const loadTPSLFromLocalStorage = (symbol) => {
  const key = getTPSLStorageKey(symbol);
  if (!key) return null;
  
  try {
    const stored = localStorage.getItem(key);
    if (stored) {
      const data = JSON.parse(stored);
      console.log('[localStorage] 已读取 TP/SL:', { key, data });
      return data;
    }
  } catch (error) {
    console.error('[localStorage] 读取失败:', error);
  }
  return null;
};
const fundingRate = ref(0.0001);

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

// 盘口数据
const asks = ref([]);
const bids = ref([]);
const orderBookContainerRef = ref(null);
const orderFormRef = ref(null);
const maxVisibleRows = ref(12);

// 币种价格数据（默认值，会被币安 API 覆盖）
const coinPrices = ref({
  'BTC': 92255.0,
  'ETH': 3100.0,
  'BNB': 590.0,
  'SOL': 145.0,
  'DOGE': 0.12,
  'TRX': 0.15,
  'BEAT': 1.2,
  'AIC': 2.0
});

// 从币安 API 获取价格
const fetchPriceFromBinance = async (symbolName) => {
  try {
    // 标准化交易对名称（BTC -> BTCUSDT）
    let binanceSymbol = symbolName.toUpperCase();
    if (binanceSymbol === 'ETF BTC' || binanceSymbol === 'ETFBTC') {
      binanceSymbol = 'BTCUSDT';
    } else if (!binanceSymbol.endsWith('USDT')) {
      binanceSymbol = binanceSymbol + 'USDT';
    }
    
    // 尝试币安官方 API
    let url = `https://api.binance.com/api/v3/ticker/price?symbol=${binanceSymbol}`;
    let response;
    
    try {
      response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      // 如果跨域失败，使用无 CORS 限制的 API
      console.warn(`[Price] 主 API 失败，尝试备用 API:`, error);
      url = `https://data-api.binance.vision/api/v3/ticker/price?symbol=${binanceSymbol}`;
      response = await fetch(url);
    }
    
    const data = await response.json();
    
    if (data && data.price) {
      const price = parseFloat(data.price);
      coinPrices.value[symbolName] = price;
      
      // 更新当前交易对的价格
      if (symbolName === symbol.value) {
        lastPrice.value = price;
        markPrice.value = price;
        
        // 更新价格变化百分比（需要24h数据）
        await fetchPriceChangeFromBinance(symbolName);
      }
      
      console.log(`[Price] ${symbolName} 价格更新: ${price}`);
      return price;
    }
  } catch (error) {
    console.error(`[Price] 获取 ${symbolName} 价格失败:`, error);
    // 使用默认价格
    return coinPrices.value[symbolName] || 92255.50;
  }
};

// 从币安 API 获取24h价格变化
const fetchPriceChangeFromBinance = async (symbolName) => {
  try {
    let binanceSymbol = symbolName.toUpperCase();
    if (binanceSymbol === 'ETF BTC' || binanceSymbol === 'ETFBTC') {
      binanceSymbol = 'BTCUSDT';
    } else if (!binanceSymbol.endsWith('USDT')) {
      binanceSymbol = binanceSymbol + 'USDT';
    }
    
    let url = `https://api.binance.com/api/v3/ticker/24hr?symbol=${binanceSymbol}`;
    let response;
    
    try {
      response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      url = `https://data-api.binance.vision/api/v3/ticker/24hr?symbol=${binanceSymbol}`;
      response = await fetch(url);
    }
    
    const data = await response.json();
    
    if (data && data.priceChangePercent !== undefined) {
      priceChange.value = parseFloat(data.priceChangePercent);
    }
  } catch (error) {
    console.error(`[Price] 获取 ${symbolName} 24h变化失败:`, error);
  }
};

// 返回上一页
const handleBack = () => {
  router.back();
};

// 打开语言选择
const handleLanguageClick = () => {
  if (langRef.value) {
    langRef.value.open();
  }
};

// 格式化函数
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

const formatAssetBalance = (value, symbol = '') => {
  return formatAssetAmount(value, symbol);
};

const formatOrderTime = (timestamp) => {
  if (!timestamp) return '';
  const timestampMs = timestamp < 1e12 ? timestamp * 1000 : timestamp;
  const date = new Date(timestampMs);
  if (isNaN(date.getTime())) return '';
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

const formatUnrealizedPnl = (pnl) => {
  if (!pnl && pnl !== 0) return '0.00';
  return Math.abs(pnl).toFixed(2);
};

// 生成盘口数据
const generateOrderBook = () => {
  const basePrice = lastPrice.value;
  const totalRows = 100;
  
  const newAsks = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (totalRows - i) * 0.01 + Math.random() * 0.1;
    const quantity = Math.random() * 5 + 0.00001;
    newAsks.push({
      price: basePrice + priceOffset,
      quantity: quantity
    });
  }
  asks.value = newAsks.sort((a, b) => a.price - b.price);
  
  const newBids = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (i + 1) * 0.01 + Math.random() * 0.1;
    const quantity = Math.random() * 5 + 0.00001;
    newBids.push({
      price: basePrice - priceOffset,
      quantity: quantity
    });
  }
  bids.value = newBids.sort((a, b) => b.price - a.price);
};

// 计算深度条宽度
const getDepthWidth = (quantity, list, type) => {
  if (!list || list.length === 0 || !quantity || quantity <= 0) return 0;
  const maxQuantity = Math.max(...list.map(item => item.quantity || 0));
  if (maxQuantity === 0) return 0;
  if (maxQuantity < quantity) return 100;
  const ratio = quantity / maxQuantity;
  const smoothRatio = Math.sqrt(ratio);
  return smoothRatio * 100;
};

const displayedAsks = computed(() => {
  return asks.value.slice(0, maxVisibleRows.value).reverse();
});

const displayedBids = computed(() => {
  return bids.value.slice(0, maxVisibleRows.value);
});

// 选择价格
const selectPrice = (selectedPrice, side) => {
  const config = currentCoinConfig.value;
  price.value = selectedPrice.toFixed(config.priceFixed);
  if (side !== orderSide.value) orderSide.value = side;
};

const selectFuturesPrice = (priceValue) => {
  if (orderType.value === 'limit') {
    futuresPrice.value = priceValue.toString();
  }
};

// 更新价格
const updatePriceForSymbol = async (newSymbol) => {
  // 先从币安 API 获取真实价格
  await fetchPriceFromBinance(newSymbol);
  
  // 使用更新后的价格
  lastPrice.value = coinPrices.value[newSymbol] || 92255.50;
  markPrice.value = coinPrices.value[newSymbol] || 92255.50;
  
  const realDepth = marketStore.depths[newSymbol];
  if (!realDepth || !realDepth.asks.length) {
    generateOrderBook();
  } else {
    asks.value = [...realDepth.asks];
    bids.value = [...realDepth.bids];
  }

  if (orderType.value === 'limit') {
    price.value = lastPrice.value.toFixed(currentCoinConfig.value.priceFixed);
  }
};

// 可用余额
const availableBalance = computed(() => {
  try {
    if (activeTradeTab.value === 'futures') {
      return assetStore?.usdtBalance || 0;
    }
    if (orderSide.value === 'buy') return assetStore?.usdtBalance || 0;
    else return assetStore?.getHolding(symbol.value) || 0;
  } catch (error) {
    console.error('Error getting available balance:', error);
    return 0;
  }
});

// 现货计算属性
const spotCurrentPrice = computed(() => {
  if (orderType.value === 'market') {
    return lastPrice.value;
  }
  return parseFloat(price.value) || lastPrice.value;
});

const SPOT_FEE_RATE = 0.001;
const FUTURES_FEE_RATE = 0.0004;

const spotEstimatedFee = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  if (p <= 0 || a <= 0) return 0;
  if (orderSide.value === 'buy') {
    return a * SPOT_FEE_RATE;
  } else {
    return (p * a) * SPOT_FEE_RATE;
  }
});

const formatEstimatedFee = computed(() => {
  const fee = spotEstimatedFee.value;
  if (fee <= 0) return '0.00';
  if (orderSide.value === 'buy') {
    const config = currentCoinConfig.value;
    return fee.toFixed(config.amountFixed);
  } else {
    return formatAssetBalance(fee, 'USDT');
  }
});

const formatEstimatedFeeUSDT = computed(() => {
  if (orderSide.value !== 'buy') return '';
  const fee = spotEstimatedFee.value;
  if (fee <= 0) return '';
  const p = spotCurrentPrice.value;
  const feeUSDT = fee * p;
  return feeUSDT > 0 ? formatAssetBalance(feeUSDT, 'USDT') : '';
});

const spotTotal = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  if (p <= 0 || a <= 0) return 0;
  return p * a;
});

const formatTotalAmount = computed(() => {
  const total = spotTotal.value;
  return total > 0 ? total.toFixed(2) : '0.00';
});

const formatEstimatedReceived = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  if (p <= 0 || a <= 0) return '0.00';
  if (orderSide.value === 'buy') {
    const fee = spotEstimatedFee.value;
    const received = a - fee;
    const config = currentCoinConfig.value;
    return received > 0 ? received.toFixed(config.amountFixed) + ' ' + currentCoinConfig.value.baseCoin : '0.00 ' + currentCoinConfig.value.baseCoin;
  } else {
    const total = spotTotal.value;
    const fee = spotEstimatedFee.value;
    const received = total - fee;
    return received > 0 ? formatAssetBalance(received, 'USDT') + ' USDT' : '0.00 USDT';
  }
});

const formatAvailableBalance = computed(() => {
  const usdtBalance = assetStore?.usdtBalance || 0;
  return formatAssetBalance(usdtBalance, 'USDT') + ' USDT';
});

const formatSellableBalance = computed(() => {
  const coinBalance = assetStore?.getHolding(symbol.value) || 0;
  return formatAssetBalance(coinBalance, symbol.value) + ' ' + symbol.value;
});

// 合约计算属性
const futuresCurrentPrice = computed(() => {
  if (orderType.value === 'market') {
    return markPrice.value;
  }
  return parseFloat(futuresPrice.value) || markPrice.value;
});

const futuresNotionalValue = computed(() => {
  const p = futuresCurrentPrice.value;
  const a = parseFloat(futuresAmount.value) || 0;
  if (p <= 0 || a <= 0) return 0;
  return p * a;
});

const futuresEstimatedFee = computed(() => {
  const notional = futuresNotionalValue.value;
  if (notional <= 0) return 0;
  return notional * FUTURES_FEE_RATE;
});

const formatFuturesEstimatedFee = computed(() => {
  const fee = futuresEstimatedFee.value;
  return fee > 0 ? fee.toFixed(4) : '0.00';
});

const futuresMargin = computed(() => {
  const notional = futuresNotionalValue.value;
  const leverage = currentLeverage.value || 20;
  if (notional <= 0 || leverage <= 0) return 0;
  return notional / leverage;
});

const futuresTotal = computed(() => {
  return futuresNotionalValue.value;
});

const formatFuturesTotalAmount = computed(() => {
  const total = futuresTotal.value;
  return total > 0 ? total.toFixed(2) : '0.00';
});

const isOrderValid = computed(() => {
  const a = parseFloat(amount.value);
  if (orderType.value === 'market') return a > 0;
  else {
    const p = parseFloat(price.value);
    return p > 0 && a > 0;
  }
});

const isFuturesFormValid = computed(() => {
  if (orderType.value === 'limit') {
    return futuresPrice.value && futuresAmount.value && parseFloat(futuresPrice.value) > 0 && parseFloat(futuresAmount.value) > 0;
  }
  return futuresAmount.value && parseFloat(futuresAmount.value) > 0;
});

// 订单类型选项
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
const selectLeverage = (leverage) => {
  currentLeverage.value = leverage;
  showLeveragePopup.value = false;
};

// 滑块处理
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
  updateSpotSliderFromAmount();
};

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
      const totalCost = inputAmount * orderPrice;
      percent = Math.min(100, Math.max(0, (totalCost / balance) * 100));
    } else {
      percent = Math.min(100, Math.max(0, (inputAmount / balance) * 100));
    }
    spotSliderValue.value = Math.round(percent);
  } catch (error) {
    console.error('Error updating slider from amount:', error);
  }
};

const onSpotSliderChange = (value) => {
  const clampedValue = Math.max(0, Math.min(100, value));
  spotSliderValue.value = clampedValue;
  setAmountPercent(clampedValue);
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
      let scalingFactor = percent / 100;
      if (percent === 100) {
        scalingFactor = orderType.value === 'market' ? 0.995 : 0.999;
      }
      const totalCost = balance * scalingFactor;
      const calculatedAmount = totalCost / orderPrice;
      amount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(config.amountFixed) : '';
    } else {
      let scalingFactor = percent / 100;
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

// 合约滑块处理
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
  updateFuturesSliderFromAmount();
};

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
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    if (maxAmount <= 0) {
      return;
    }
    const percent = Math.min(100, Math.max(0, (inputAmount / maxAmount) * 100));
    futuresSliderValue.value = Math.round(percent);
  } catch (error) {
    console.error('Error updating futures slider from amount:', error);
  }
};

const selectFuturesPercent = (percent) => {
  selectedFuturesPercent.value = percent;
  setFuturesAmountPercent(percent);
};

// 合约滑块变化事件处理
const onFuturesSliderChange = (value) => {
  const clampedValue = Math.max(0, Math.min(100, value));
  futuresSliderValue.value = clampedValue;
  setFuturesAmountPercent(clampedValue);
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
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    let scalingFactor = percent / 100;
    if (percent === 100) {
      scalingFactor = 0.999;
    }
    const calculatedAmount = maxAmount * scalingFactor;
    futuresAmount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(currentCoinConfig.value.amountFixed) : '';
  } catch (error) {
    console.error('Error setting futures amount percent:', error);
    futuresAmount.value = '';
  }
};

// 下单处理
const handleSubmitOrder = async () => {
  const amountValue = parseFloat(amount.value);
  if (isNaN(amountValue) || amountValue <= 0) {
    showToast({ message: t('trade.amount_invalid'), icon: 'fail' });
    return;
  }
  if (!isOrderValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }
  isLoading.value = true;
  try {
    const orderPrice = orderType.value === 'market' ? lastPrice.value : parseFloat(price.value);
    const params = {
      symbol: `${symbol.value}/USDT`,
      side: orderSide.value.toUpperCase(),
      type: orderType.value.toUpperCase(),
      price: orderType.value === 'market' ? orderPrice : parseFloat(price.value),
      amount: parseFloat(amount.value),
      use_beat_discount: false
    };
    const response = await createOrder(params);
    const responseData = response.data || response;
    if (responseData && responseData.code === 200) {
      showToast({
        message: orderType.value === 'market' ? t('trade.market_order_submitted') : t('trade.limit_order_submitted'),
        icon: 'success',
        duration: 2000
      });
      await assetStore.initData();
      await fetchSpotOrders();
      if (orderType.value === 'limit') {
        price.value = '';
      }
      amount.value = '';
      selectedPercent.value = null;
      spotSliderValue.value = 0;
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    console.error('❌ 下单失败:', error);
    let errorMessage = t('trade.order_failed') || '订单提交失败，请重试';
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
      await fetchFuturesPositions();
      await assetStore.initData();
      await fetchFuturesOrders();
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
      await fetchFuturesPositions();
      await assetStore.initData();
      await fetchFuturesOrders();
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

// 撤单
const cancelOrder = async (orderId) => {
  const isSpot = activeTradeTab.value === 'spot';
  const orderList = isSpot ? spotOrdersList.value : futuresOrdersList.value;
  const order = orderList.find(o => o.order_id === orderId);
  if (!order || !order.order_id) {
    showToast({ message: t('trade.order_not_found'), icon: 'fail' });
    return;
  }
  try {
    let response;
    if (isSpot) {
      response = await cancelSpotOrderApi(order.order_id);
    } else {
      response = await cancelFuturesOrderApi(order.order_id);
    }
    const responseData = response.data || response;
    if (responseData && responseData.code === 200) {
      showToast({
        message: t('trade.order_cancelled'),
        icon: 'success',
        duration: 2000
      });
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

const cancelFuturesOrder = cancelOrder;

// 切换币种
const switchCoin = (newSymbol) => {
  symbol.value = newSymbol;
  showCoinSelect.value = false;
  amount.value = '';
  selectedPercent.value = null;
  spotSliderValue.value = 0;
  updatePriceForSymbol(newSymbol);
  router.replace({
    path: route.path,
    query: {
      ...route.query,
      symbol: newSymbol,
      side: orderSide.value
    }
  });
  showToast({
    message: t('trade.switched_to', { symbol: `${newSymbol}/USDT` }),
    duration: 1500
  });
};

// 获取订单列表
const fetchSpotOrders = async () => {
  try {
    const response = await getOrders({ status: 'NEW' });
    const responseData = response.data || response;
    if (responseData && responseData.code === 200 && responseData.data) {
      const pendingOrders = responseData.data.filter(order =>
        order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
      );
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

const fetchFuturesOrders = async () => {
  try {
    const response = await getFuturesOrders({ status: 'NEW' });
    const responseData = response.data || response;
    if (responseData && responseData.code === 200 && responseData.data) {
      const pendingOrders = responseData.data.filter(order =>
        order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
      );
      futuresOrdersList.value = pendingOrders.map(order => ({
        order_id: order.order_id,
        side: order.side ? order.side.toUpperCase() : 'BUY',
        type: order.type ? order.type.toLowerCase() : 'limit',
        price: order.price || 0,
        quantity: order.quantity || order.amount || 0,
        amount: order.amount || order.quantity || 0,
        symbol: order.symbol ? (order.symbol.includes('/') ? order.symbol.split('/')[0] : order.symbol) : 'BTC',
        timestamp: order.timestamp || order.create_time || Date.now(),
        status: order.status || 'NEW'
      }));
    } else {
      futuresOrdersList.value = [];
    }
  } catch (error) {
    console.error('❌ 获取合约订单列表失败:', error);
    futuresOrdersList.value = [];
  }
};

const fetchFuturesHistory = async (isRefresh = false) => {
  if (historyLoading.value) return;
  try {
    historyLoading.value = true;
    if (isRefresh) {
      futuresHistoryList.value = [];
      historyPage.value = 1;
      historyHasMore.value = true;
    }
    const skip = (historyPage.value - 1) * historyPageSize.value;
    const response = await getFuturesOrders({
      status: 'HISTORY',
      skip: skip,
      limit: historyPageSize.value
    });
    const responseData = response.data || response;
    if (responseData && responseData.code === 200 && responseData.data) {
      const newOrders = responseData.data.map(order => ({
        order_id: order.order_id,
        side: order.side ? order.side.toUpperCase() : 'BUY',
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
      if (isRefresh) {
        futuresHistoryList.value = newOrders;
      } else {
        futuresHistoryList.value = [...futuresHistoryList.value, ...newOrders];
      }
      if (newOrders.length < historyPageSize.value) {
        historyHasMore.value = false;
      } else {
        historyPage.value += 1;
      }
    } else {
      if (isRefresh) {
        futuresHistoryList.value = [];
      }
      historyHasMore.value = false;
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

const fetchFuturesPositions = async () => {
  try {
    if (!assetStore.isWalletConnected) {
      positions.value = [];
      return;
    }
    const response = await getFuturesPositionsApi();
    const responseData = response.data || response;
    if (responseData && responseData.code === 200 && responseData.data) {
      positions.value = responseData.data.map(pos => {
        const margin = pos.margin || (pos.entry_price * pos.size / (pos.leverage || 20));
        const unrealizedPnl = pos.unrealized_pnl || 0;
        const unrealizedPnlPercent = margin > 0 ? (unrealizedPnl / margin) * 100 : 0;
        
        // 使用标准化字段名 take_profit 和 stop_loss
        const take_profit = pos.take_profit_price || pos.take_profit || null;
        const stop_loss = pos.stop_loss_price || pos.stop_loss || null;
        
        const positionData = {
          id: `${pos.symbol?.split('/')[0] || pos.symbol}_${pos.side?.toLowerCase() || 'long'}`,
          symbol: pos.symbol?.split('/')[0] || pos.symbol,
          side: pos.side?.toLowerCase() || 'long',
          quantity: pos.size || pos.quantity || 0,
          entryPrice: pos.entry_price || 0,
          leverage: pos.leverage || 20,
          margin: margin,
          liquidationPrice: pos.liquidation_price || 0,
          unrealizedPnl: unrealizedPnl,
          unrealizedPnlPercent: unrealizedPnlPercent,
          markPrice: pos.mark_price || markPrice.value,
          // 标准化字段名（使用 snake_case）
          take_profit: take_profit,
          stop_loss: stop_loss
        };
        
        // 调试日志：输出原始数据
        console.log('[fetchFuturesPositions] Position Data:', {
          symbol: positionData.symbol,
          take_profit,
          stop_loss,
          original: pos,
          mapped: positionData
        });
        
        // ========== 加载 localStorage 中的 TP/SL（Local Memory 功能） ==========
        const localData = loadTPSLFromLocalStorage(positionData.symbol);
        if (localData && (localData.tp || localData.sl)) {
          // 如果 localStorage 有数据，优先使用 localStorage 的值
          positionData.tp = localData.tp || positionData.take_profit;
          positionData.sl = localData.sl || positionData.stop_loss;
          positionData.take_profit = localData.tp || positionData.take_profit;
          positionData.stop_loss = localData.sl || positionData.stop_loss;
          positionData.takeProfit = localData.tp || positionData.take_profit;
          positionData.stopLoss = localData.sl || positionData.stop_loss;
          
          console.log('[Local Memory] 从 localStorage 恢复 TP/SL:', {
            symbol: positionData.symbol,
            tp: localData.tp,
            sl: localData.sl
          });
        } else {
          // 如果没有 localStorage 数据，设置所有格式的字段
          positionData.tp = take_profit;
          positionData.sl = stop_loss;
          positionData.takeProfit = take_profit;
          positionData.stopLoss = stop_loss;
        }
        
        return positionData;
      });
      
      // 同步到 assetsStore
      if (assetStore && assetStore.syncPositions) {
        assetStore.syncPositions(positions.value);
      }
      
      // 调试日志：输出每个持仓的 TP/SL 数据
      positions.value.forEach((pos, idx) => {
        console.log(`[fetchFuturesPositions] Card rendered with position [${idx}]:`, {
          symbol: pos.symbol,
          take_profit: pos.take_profit || '-',
          stop_loss: pos.stop_loss || '-',
          position: pos
        });
      });
    } else {
      positions.value = [];
      // 同步空数组到 assetsStore
      if (assetStore && assetStore.syncPositions) {
        assetStore.syncPositions([]);
      }
    }
  } catch (error) {
    console.error('❌ 获取合约持仓失败:', error);
    positions.value = [];
  }
};

// 持仓相关
const isLongPosition = (position) => {
  const side = position.side?.toLowerCase() || '';
  return side === 'long' || side === 'buy';
};

const handleTakeProfitStopLoss = (position, index) => {
  // ========== 关键修正：确保传入的是响应式对象（从positions数组直接取引用） ==========
  // 优先使用positions数组中的响应式对象，而不是传入的position（可能是拷贝）
  const reactivePosition = positions.value[index] || position;
  
  // 保存响应式对象的引用和索引
  currentTPSLPosition.value = { 
    position: reactivePosition,  // 使用响应式对象
    index 
  };
  
  // 调试日志
  console.log('🔄 打开止盈止损弹窗，持仓数据（响应式对象）:', reactivePosition);
  
  // 使用标准化字段名 take_profit 和 stop_loss
  const take_profit = reactivePosition.take_profit || null;
  const stop_loss = reactivePosition.stop_loss || null;
  
  tpSlForm.value.takeProfitPrice = (take_profit && take_profit > 0) ? take_profit.toString() : '';
  tpSlForm.value.stopLossPrice = (stop_loss && stop_loss > 0) ? stop_loss.toString() : '';
  
  console.log('[handleTakeProfitStopLoss] 回显数据:', {
    take_profit,
    stop_loss,
    form: {
      takeProfitPrice: tpSlForm.value.takeProfitPrice,
      stopLossPrice: tpSlForm.value.stopLossPrice
    }
  });
  
  showTPSLPopup.value = true;
};

const adjustTPSLPrice = (field, step) => {
  const currentVal = parseFloat(tpSlForm.value[field]) || markPrice.value;
  let newVal = currentVal + step;
  tpSlForm.value[field] = newVal.toFixed(2);
};

const setTPSLPercentage = (field, percent) => {
  const basePrice = markPrice.value;
  let calculatedPrice;
  if (field === 'takeProfitPrice') {
    calculatedPrice = basePrice * (1 + percent);
  } else {
    calculatedPrice = basePrice * (1 - percent);
  }
  tpSlForm.value[field] = calculatedPrice.toFixed(2);
};

const confirmTPSL = async () => {
  if (!currentTPSLPosition.value?.position) {
    showToast({
      message: t('trade.position_not_found') || '持仓不存在',
      icon: 'fail',
      duration: 2000
    });
    return;
  }

  const position = currentTPSLPosition.value.position;
  const takeProfitPrice = parseFloat(tpSlForm.value.takeProfitPrice) || 0;
  const stopLossPrice = parseFloat(tpSlForm.value.stopLossPrice) || 0;

  // 至少需要设置一个价格
  if (takeProfitPrice <= 0 && stopLossPrice <= 0) {
    showToast({
      message: t('trade.fill_all_fields') || '请至少设置一个止盈或止损价格',
      icon: 'fail',
      duration: 2000
    });
    return;
  }

  try {
    isLoading.value = true;
    const symbolPair = position.symbol.includes('/') ? position.symbol : `${position.symbol}/USDT`;
    
    const response = await setPositionTPSL({
      symbol: symbolPair,
      take_profit: takeProfitPrice > 0 ? takeProfitPrice : null,
      stop_loss: stopLossPrice > 0 ? stopLossPrice : null
    });

    const responseData = response.data || response;
    if (responseData && responseData.code === 200) {
      // ========== 保存到 localStorage（在 API 调用成功后） ==========
      saveTPSLToLocalStorage(
        position.symbol,
        takeProfitPrice > 0 ? takeProfitPrice : null,
        stopLossPrice > 0 ? stopLossPrice : null
      );
      
      showToast({
        message: responseData.message || t('trade.take_profit_stop_loss') + ' ' + t('trade.order_submitted'),
        icon: 'success',
        duration: 2000
      });
      
      // ========== 核心修复：请求成功后，立即强制修改本地 Store 中的数据 ==========
      const positionIndex = currentTPSLPosition.value?.index;
      if (positionIndex !== undefined && positions.value[positionIndex]) {
        const targetPosition = positions.value[positionIndex];
        
        // 确保是同一个仓位
        if (targetPosition.symbol === position.symbol) {
          console.log("🚨 [confirmTPSL] 正在强制更新本地 TP/SL:", {
            symbol: symbolPair,
            take_profit: takeProfitPrice,
            stop_loss: stopLossPrice
          });
          
          // 强制写入，标准化字段名为 take_profit 和 stop_loss
          const new_take_profit = takeProfitPrice > 0 ? takeProfitPrice : null;
          const new_stop_loss = stopLossPrice > 0 ? stopLossPrice : null;
          
          // 使用 Vue 的响应式赋值（targetPosition 是响应式对象）
          // 更新所有可能的字段名（支持多种格式）
          targetPosition.take_profit = new_take_profit;
          targetPosition.stop_loss = new_stop_loss;
          targetPosition.tp = new_take_profit;  // 短字段名（用于显示）
          targetPosition.sl = new_stop_loss;    // 短字段名（用于显示）
          targetPosition.takeProfit = new_take_profit;  // camelCase（兼容）
          targetPosition.stopLoss = new_stop_loss;      // camelCase（兼容）
          
          // 同时更新currentTPSLPosition中的引用
          currentTPSLPosition.value.position = targetPosition;
          
          console.log("✅ [confirmTPSL] 本地 TP/SL 已更新:", {
            symbol: targetPosition.symbol,
            take_profit: targetPosition.take_profit,
            stop_loss: targetPosition.stop_loss,
            tp: targetPosition.tp,
            sl: targetPosition.sl,
            position: targetPosition
          });
        }
      }
      
      showTPSLPopup.value = false;
      currentTPSLPosition.value = null;
      // 清空表单
      tpSlForm.value.takeProfitPrice = '';
      tpSlForm.value.stopLossPrice = '';
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    console.error('❌ 设置止盈止损失败:', error);
    let errorMessage = t('trade.order_failed') || '设置失败，请重试';
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
        await fetchFuturesPositions();
        await assetStore.initData();
        await fetchFuturesOrders();
        await fetchFuturesHistory();
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

// 初始化
const initializeTrade = async () => {
  generateOrderBook();
  await updatePriceForSymbol(symbol.value);
  marketStore.ensureConnection();
  if (assetStore.isWalletConnected) {
    if (activeTradeTab.value === 'spot') {
      await fetchSpotOrders();
    } else {
      await fetchFuturesOrders();
      await fetchFuturesPositions();
    }
  }
};

// 监听 Tab 切换
watch(activeTradeTab, async (newTab) => {
  if (assetStore.isWalletConnected) {
    if (newTab === 'futures') {
      await fetchFuturesPositions();
      await fetchFuturesOrders();
      await fetchFuturesHistory();
    } else if (newTab === 'spot') {
      await fetchSpotOrders();
    }
  }
}, { immediate: true });

// 监听持仓Tab切换
watch(activePositionTab, async (newTab) => {
  if (assetStore.isWalletConnected && activeTradeTab.value === 'futures') {
    if (newTab === 0) {
      await fetchFuturesPositions();
    } else if (newTab === 1) {
      await fetchFuturesOrders();
    } else if (newTab === 2) {
      await fetchFuturesHistory(true);
      await nextTick();
      initHistoryObserver();
    }
  }
});

// 监听 positions 变化，输出调试日志（模拟 PositionCard 的 onMounted）
watch(positions, (newPositions) => {
  newPositions.forEach((position, index) => {
    console.log(`[PositionCard] Card rendered with position [${index}]:`, {
      symbol: position.symbol,
      take_profit: position.take_profit || '-',
      stop_loss: position.stop_loss || '-',
      position: position
    });
  });
}, { deep: true });

// 监听标记价格变化
// ========== 监听弹窗打开，优先从 localStorage 读取，回退到 position 数据 ==========
watch(showTPSLPopup, (isOpen) => {
  if (isOpen && currentTPSLPosition.value?.position) {
    const position = currentTPSLPosition.value.position;
    const symbol = position.symbol;
    
    console.log("🔄 弹窗已打开，正在回填数据...", position);
    
    // ========== Step 1: 优先从 localStorage 读取用户上次输入的值 ==========
    const localData = loadTPSLFromLocalStorage(symbol);
    
    let saved_take_profit = '';
    let saved_stop_loss = '';
    
    if (localData && (localData.tp || localData.sl)) {
      // 从 localStorage 读取
      saved_take_profit = localData.tp ? String(localData.tp) : '';
      saved_stop_loss = localData.sl ? String(localData.sl) : '';
      console.log('[watch showTPSLPopup] 从 localStorage 读取:', { tp: saved_take_profit, sl: saved_stop_loss });
    } else {
      // ========== Step 2: Fallback - 从 position 对象读取 ==========
      const p = position;
      saved_take_profit = p.take_profit ? String(p.take_profit) : '';
      saved_stop_loss = p.stop_loss ? String(p.stop_loss) : '';
      console.log('[watch showTPSLPopup] 从 position 对象读取:', { take_profit: saved_take_profit, stop_loss: saved_stop_loss });
    }
    
    // 赋值给输入框 (v-model)
    tpSlForm.value.takeProfitPrice = saved_take_profit;
    tpSlForm.value.stopLossPrice = saved_stop_loss;
    
    console.log('[watch showTPSLPopup] Dialog opened with prop:', position, 'TP:', tpSlForm.value.takeProfitPrice, 'SL:', tpSlForm.value.stopLossPrice);
    console.log('[watch showTPSLPopup] 最终回填结果:', {
      source: localData ? 'localStorage' : 'position',
      take_profit: saved_take_profit,
      stop_loss: saved_stop_loss,
      form: {
        takeProfitPrice: tpSlForm.value.takeProfitPrice,
        stopLossPrice: tpSlForm.value.stopLossPrice
      }
    });
  } else if (!isOpen) {
    // 弹窗关闭时清空表单
    tpSlForm.value.takeProfitPrice = '';
    tpSlForm.value.stopLossPrice = '';
  }
});

watch(markPrice, () => {
  if (!asks.value.length || !bids.value.length) {
    generateOrderBook();
  }
}, { immediate: true });

watch(() => marketStore.getTicker(symbol.value), (ticker) => {
  if (ticker) {
    markPrice.value = ticker.price || markPrice.value;
    priceChange.value = ticker.change || priceChange.value;
  }
}, { immediate: true });

watch(() => marketStore.depths[symbol.value], (newDepth) => {
  if (newDepth && newDepth.asks && newDepth.bids) {
    asks.value = [...newDepth.asks];
    bids.value = [...newDepth.bids];
  }
}, { immediate: true, deep: true });

watch(() => route.query.symbol, async (newSymbol) => {
  if (newSymbol) {
    symbol.value = newSymbol;
    await updatePriceForSymbol(newSymbol);
  }
});

watch(() => route.query.side, (newSide) => {
  if (newSide === 'buy' || newSide === 'sell') orderSide.value = newSide;
}, { immediate: true });

watch(symbol, async (newSymbol) => {
  await updatePriceForSymbol(newSymbol);
});

// 定时更新价格（每5秒）
let priceUpdateTimer = null;
const startPriceUpdate = () => {
  stopPriceUpdate();
  priceUpdateTimer = setInterval(async () => {
    try {
      await fetchPriceFromBinance(symbol.value);
    } catch (error) {
      console.error('定时更新价格失败:', error);
    }
  }, 5000);
};

const stopPriceUpdate = () => {
  if (priceUpdateTimer) {
    clearInterval(priceUpdateTimer);
    priceUpdateTimer = null;
  }
};

// IntersectionObserver 初始化
const initHistoryObserver = () => {
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
  historyObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      if (
        entry &&
        entry.isIntersecting &&
        historyHasMore.value &&
        !historyLoading.value
      ) {
        fetchFuturesHistory(false);
      }
    },
    {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    }
  );
  nextTick(() => {
    if (loadMoreTrigger.value) {
      historyObserver.observe(loadMoreTrigger.value);
    }
  });
};

// 定时刷新持仓
let positionsRefreshTimer = null;
const startPositionsRefresh = () => {
  stopPositionsRefresh();
  if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
    positionsRefreshTimer = setInterval(async () => {
      try {
        await fetchFuturesPositions();
        await assetStore.initData();
      } catch (error) {
        console.error('❌ 定时刷新持仓失败:', error);
      }
    }, 5000);
  }
};

const stopPositionsRefresh = () => {
  if (positionsRefreshTimer) {
    clearInterval(positionsRefreshTimer);
    positionsRefreshTimer = null;
  }
};

onMounted(async () => {
  await initializeTrade();
  startPriceUpdate(); // 启动价格定时更新
  if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
    await fetchFuturesPositions();
    await fetchFuturesOrders();
    await fetchFuturesHistory();
    startPositionsRefresh();
  } else if (activeTradeTab.value === 'spot' && assetStore.isWalletConnected) {
    await fetchSpotOrders();
  }
});

onActivated(() => {
  initializeTrade();
  startPositionsRefresh();
});

onDeactivated(() => {
  stopPositionsRefresh();
  stopPriceUpdate();
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
});

onUnmounted(() => {
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
  stopPositionsRefresh();
  stopPriceUpdate();
});
</script>

<style scoped>
.trade-sub-page {
  width: 100%;
  height: 100vh;
  background-color: var(--color-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 交易容器 - 严格的 Flex 布局包装 */
.trade-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  /* 移除 min-height，让内容自然高度 */
}

/* 顶部导航栏 - 玻璃拟态效果 */
.trade-sub-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 52px;
  background: rgb(var(--color-shadow-rgb) / 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 1000;
  box-shadow: 0 2px 10px rgb(var(--color-shadow-rgb) / 0.3);
}

.navbar-left {
  flex: 0 0 auto;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.back-icon {
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 6px;
  border-radius: 50%;
}

.back-icon:hover {
  background-color: rgb(var(--color-brand-rgb) / 0.1);
  transform: scale(1.1);
}

.back-icon:active {
  transform: scale(0.95);
}

.navbar-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.navbar-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
  text-align: center;
}

.navbar-right {
  flex: 0 0 auto;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.lang-icon-wrapper {
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lang-icon-wrapper:hover {
  background-color: rgb(var(--color-brand-rgb) / 0.1);
  transform: scale(1.1);
}

.lang-icon-wrapper:active {
  transform: scale(0.95);
}

/* 主体内容区域 */
.trade-sub-content {
  flex: 1;
  margin-top: 52px;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 10px; /* 减少底部 padding，紧凑布局 */
  background-color: var(--color-bg);
  color: var(--color-text-primary);
}

/* Tab 切换：现货/合约 */
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

/* 交易对信息 */
.pair-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.pair-selector {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.pair-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.price-change {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.price-change.positive {
  color: var(--color-earn);
  background-color: rgb(var(--color-earn-rgb) / 0.1);
}

.price-change.negative {
  color: var(--color-loss);
  background-color: rgb(var(--color-loss-rgb) / 0.1);
}

/* 核心交易区 - 强制横向布局 */
.trade-main,
.futures-trade-main {
  display: flex !important;
  flex-direction: row !important;
  gap: 8px;
  padding: 8px;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
  flex-wrap: nowrap; /* 防止换行 */
  /* 移除 min-height，让内容自然高度 */
}

/* 盘口区 - 确保固定宽度，不被压缩 */
.orderbook-side,
.futures-orderbook-side,
.left-order-book {
  width: 60% !important;
  min-width: 0; /* 允许 flex 收缩 */
  flex: 0 0 60% !important; /* flex-grow: 0, flex-shrink: 0, flex-basis: 60% */
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, var(--color-bg) 100%);
  border-radius: 8px;
  overflow: visible;
  padding: 0;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.08);
  box-shadow: 0 0 20px rgb(var(--color-shadow-rgb) / 0.5);
  align-self: flex-start; /* 确保顶部对齐 */
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  padding: 6px 12px; /* 减少 padding，紧凑布局 */
  font-size: 10px; /* 保持小字号 */
  color: var(--color-text-secondary);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.03);
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  line-height: 1.2; /* 紧凑行高 */
}

.header-price {
  flex: 1;
  text-align: left;
}

.header-quantity {
  flex: 1;
  text-align: right;
}

.asks-list,
.bids-list {
  display: flex;
  flex-direction: column;
}

.order-row {
  position: relative;
  height: 20px; /* 减少高度，紧凑布局 */
  line-height: 20px; /* 匹配高度 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s ease;
  font-size: 11px; /* 紧凑字号 */
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

.ask-depth {
  background: linear-gradient(to left,
    rgb(var(--color-loss-rgb) / 0.25) 0%,
    rgb(var(--color-loss-rgb) / 0.15) 50%,
    rgb(var(--color-loss-rgb) / 0.05) 100%
  );
  box-shadow: inset -2px 0 8px rgb(var(--color-loss-rgb) / 0.2);
}

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
  font-size: 11px; /* 减小字号，紧凑布局 */
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: -0.2px;
}

.ask-price {
  color: var(--color-loss);
  text-align: left;
  flex: 1;
  text-shadow: 0 0 6px rgb(var(--color-loss-rgb) / 0.4);
}

.bid-price {
  color: var(--color-earn);
  text-align: left;
  flex: 1;
  text-shadow: 0 0 6px rgb(var(--color-earn-rgb) / 0.4);
}

.order-row .quantity {
  position: relative;
  z-index: 1;
  font-size: 11px; /* 减小字号，紧凑布局 */
  color: var(--color-text-secondary);
  text-align: right;
  flex: 1;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.last-price {
  flex-shrink: 0;
  height: 40px; /* 减少高度，紧凑布局 */
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

.price-main {
  font-size: 18px; /* 稍微减小字号，紧凑布局 */
  font-weight: 800;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1.1; /* 紧凑行高 */
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: -0.5px;
  text-shadow: 0 0 12px rgb(var(--color-brand-rgb) / 0.4);
  transition: all 0.3s ease;
}

.price-fiat {
  font-size: 10px; /* 减小字号 */
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  margin-top: 2px; /* 减少间距 */
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

/* 交易表单 - 确保固定宽度，不被压缩 */
.form-side,
.futures-form-side,
.right-trade-form {
  width: 40% !important;
  min-width: 0; /* 允许 flex 收缩 */
  flex: 0 0 40% !important; /* flex-grow: 0, flex-shrink: 0, flex-basis: 40% */
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-sizing: border-box;
}

/* 资产信息面板 */
.asset-info {
  flex-shrink: 0;
}

.buy-sell-toggle {
  display: flex;
  gap: 0;
  background: rgb(var(--color-border-rgb) / 0.03);
  border-radius: 8px;
  padding: 3px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  position: relative;
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
}

.order-type-selector:hover {
  background: rgb(var(--color-brand-rgb) / 0.05);
  border-color: rgb(var(--color-brand-rgb) / 0.25);
}

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
    inset 0 0 20px rgb(var(--color-brand-rgb) / 0.05);
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
  color: var(--color-accent);
  font-weight: 600;
  white-space: nowrap;
  margin-left: 4px;
  opacity: 0.8;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

.no-spinner::-webkit-inner-spin-button,
.no-spinner::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.no-spinner {
  -moz-appearance: textfield;
  appearance: textfield;
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

.slider-wrapper {
  padding: 16px 8px;
  margin-bottom: 16px;
  position: relative;
}

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
}

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

.submit-btn.buy {
  background: linear-gradient(135deg, var(--color-earn) 0%, var(--color-earn) 100%);
  color: var(--color-text-on-accent);
  box-shadow: 0 4px 20px rgb(var(--color-earn-rgb) / 0.4), inset 0 1px 0 rgb(var(--color-border-rgb) / 0.3);
}

.submit-btn.sell {
  background: linear-gradient(135deg, var(--color-loss) 0%, var(--color-loss) 100%);
  color: var(--color-text-primary);
  box-shadow: 0 4px 20px rgb(var(--color-loss-rgb) / 0.4), inset 0 1px 0 rgb(var(--color-border-rgb) / 0.2);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

/* 合约交易样式 */
.futures-trade-container {
  display: flex;
  flex-direction: column;
}

/* 合约交易主区域 - 强制横向布局 */
.futures-trade-main {
  display: flex !important;
  flex-direction: row !important;
  gap: 8px;
  padding: 8px;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
  flex-wrap: nowrap; /* 防止换行 */
}

/* 顶部控制栏 - 与现货页面的 pair-info 高度完全一致 */
.futures-control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, var(--color-bg) 100%);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
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


/* 持仓看板 */
/* 底部面板 - 紧凑布局，紧贴交易面板 */
.futures-bottom-section,
.bottom-section {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  box-shadow: 0 -4px 20px rgb(var(--color-shadow-rgb) / 0.5);
  display: flex;
  flex-direction: column;
  margin-top: 12px; /* 减少 margin，紧贴交易面板 */
  padding: 0 8px;
  /* 移除 min-height，让内容自然高度 */
}

.positions-list,
.orders-list,
.history-list {
  padding: 12px; /* 减少 padding，紧凑布局 */
  display: flex;
  flex-direction: column;
  gap: 10px; /* 减少 gap */
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 40px 20px;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.position-card {
  background: rgb(var(--color-border-rgb) / 0.05);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  box-shadow: 0 4px 20px rgb(var(--color-shadow-rgb) / 0.3);
}

.position-card-main {
  display: grid;
  grid-template-columns: 1fr 1.8fr 1fr;
  gap: 20px;
  align-items: start;
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
  background-color: var(--color-earn);
  color: var(--color-text-primary);
  box-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.3);
}

.position-side-badge.side-short {
  background-color: var(--color-loss);
  color: var(--color-text-primary);
  box-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.3);
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
  font-size: 32px;
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

/* 止盈止损显示（旧版，保留兼容） */
.tpsl-display {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  width: 100%;
}

/* TP/SL Display Section (Local Memory) - 新版 */
.tpsl-display-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background: rgb(var(--color-shadow-rgb) / 0.2);
  border: 1px solid rgb(var(--color-border-rgb) / 1);
  border-radius: 8px;
}

.tpsl-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tpsl-col:last-child {
  text-align: right;
}

.tpsl-label {
  font-size: 10px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tpsl-value {
  font-size: 14px;
  font-weight: 700;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
}

.tpsl-value.tp-value {
  color: var(--color-earn);
  text-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.3);
}

.tpsl-value.sl-value {
  color: var(--color-loss);
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.3);
}

.tpsl-item {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  letter-spacing: 0.3px;
}

.tpsl-item.tp-item {
  color: var(--color-accent);
}

.tpsl-item.sl-item {
  color: var(--color-text-secondary);
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
  color: var(--color-earn);
  text-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.4);
}

.entry-price-value.side-short {
  color: var(--color-loss);
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.4);
}

.liquidation-price {
  color: var(--color-loss);
  font-weight: 800;
  font-size: 14px;
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.4);
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
  min-width: 0;
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
  min-width: 120px;
}

.history-order-pnl {
  font-size: 16px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-align: right;
  line-height: 1.2;
}

.history-order-pnl.pnl-positive {
  color: var(--color-earn);
}

.history-order-pnl.pnl-negative {
  color: var(--color-loss);
}

.history-order-pnl.pnl-zero {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.history-order-pnl.pnl-liquidation {
  color: var(--color-loss) !important;
  font-weight: 900;
  font-size: 17px;
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.5);
}

.history-order-pnl.pnl-liquidation.pnl-negative {
  color: var(--color-loss) !important;
  text-shadow: 
    0 0 10px rgb(var(--color-loss-rgb) / 0.6),
    0 0 20px rgb(var(--color-loss-rgb) / 0.3);
}

.history-order-time {
  font-size: 10px;
  color: var(--color-text-secondary);
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
  font-size: 10px;
  color: var(--color-text-muted);
  text-align: center;
  padding: 16px 0;
  letter-spacing: 0.3px;
  font-weight: 500;
  opacity: 0.7;
}

/* 强平订单标签 */
.liquidation-badge {
  padding: 3px 8px;
  background-color: var(--color-loss);
  color: var(--color-text-primary);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.5);
}

.liquidation-order {
  background: rgb(var(--color-loss-rgb) / 0.05);
  border-left: 3px solid var(--color-loss);
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
}

.close-btn {
  background: rgb(var(--color-loss-rgb) / 0.1);
  color: var(--color-loss);
  border: 1px solid rgb(var(--color-loss-rgb) / 0.3);
}

/* 订单列表 */
.order-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: rgb(var(--color-border-rgb) / 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  transition: all 0.2s ease;
}

.order-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
  min-width: 100px;
}

.order-side-badge {
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 10px;
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

.order-symbol-time {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.order-symbol {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.order-time {
  font-size: 10px;
  color: var(--color-text-secondary);
  font-family: 'DIN Alternate', monospace;
}

.order-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 10px;
  min-width: 0;
}

.order-price {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'DIN Alternate', monospace;
}

.order-quantity {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-family: 'DIN Alternate', monospace;
}

.order-right {
  flex: 0 0 auto;
}

.cancel-btn {
  padding: 5px 12px;
  background: rgb(var(--color-loss-rgb) / 0.1);
  color: var(--color-loss);
  border: 1px solid rgb(var(--color-loss-rgb) / 0.2);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
}

.cancel-btn:hover {
  background: rgb(var(--color-loss-rgb) / 0.15);
  border-color: rgb(var(--color-loss-rgb) / 0.3);
}

/* 底部区域 */
.bottom-section {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  box-shadow: 0 -4px 20px rgb(var(--color-shadow-rgb) / 0.5);
  display: flex;
  flex-direction: column;
  margin-top: 8px;
  padding: 0 8px;
}

.bottom-tabs {
  display: flex;
  padding: 8px 16px;
  gap: 32px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  flex-shrink: 0;
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
}

.orders-panel,
.assets-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 60px;
  width: 100%;
}

.orders-list-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 60px;
  max-height: 200px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px 4px 4px 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.orders-list-compact::-webkit-scrollbar {
  display: none;
}

.orders-empty-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  padding: 0;
}

.empty-text-compact {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.assets-glass-card {
  background: rgb(var(--color-border-rgb) / 0.05);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgb(var(--color-shadow-rgb) / 0.3);
}

.assets-hud-strip {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  height: 48px;
  padding: 0;
  background: transparent;
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
  font-size: 10px;
  color: var(--color-text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1;
}

.asset-hud-value {
  font-size: 14px;
  font-weight: 800;
  color: var(--color-accent);
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 6px rgb(var(--color-brand-rgb) / 0.3);
  letter-spacing: -0.2px;
  line-height: 1.2;
  white-space: nowrap;
}

/* 弹窗样式 */
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

.coin-item {
  padding: 16px;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.coin-item:hover {
  background: rgb(var(--color-brand-rgb) / 0.05);
}

.coin-item-active {
  background: rgb(var(--color-brand-rgb) / 0.08);
  border-left: 3px solid var(--color-accent);
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

.custom-action-sheet {
  --van-action-sheet-background: var(--color-bg-card);
  --van-action-sheet-item-background: var(--color-bg-card);
  --van-action-sheet-item-text-color: var(--color-text-primary);
}

.leverage-popup {
  background: var(--color-bg-card);
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
  color: var(--color-text-primary);
  margin: 0;
}

.close-icon {
  font-size: 20px;
  color: var(--color-text-muted);
  cursor: pointer;
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
  background-color: var(--color-bg-input);
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  cursor: pointer;
}

.leverage-option.active {
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.1);
  border-color: var(--color-brand-legacy);
  color: var(--color-brand-legacy);
}

/* 止盈止损弹窗 */
.premium-tpsl-popup {
  background: var(--color-bg) !important;
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.2);
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
  cursor: pointer;
}

.premium-close-btn:active {
  color: var(--color-accent);
}

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

.premium-input-box {
  display: flex;
  align-items: center;
  background: rgb(var(--color-border-rgb) / 0.03);
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

.premium-input-box input::-webkit-outer-spin-button,
.premium-input-box input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.mono-font {
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

/* 止盈止损弹窗中的 input-suffix */
.premium-input-box .input-suffix {
  position: absolute;
  right: 12px;
  color: var(--color-text-muted);
  font-size: 11px;
  font-weight: 700;
}

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

.percent-tag:active {
  opacity: 0.7;
}

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
  cursor: pointer;
}

.premium-gold-button:active {
  transform: scale(0.97);
  box-shadow: 0 5px 10px rgb(var(--color-brand-rgb) / 0.1);
  filter: brightness(0.9);
}

.premium-gold-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Vant Slider 样式 */
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

/* Vant Tabs 样式 */
:deep(.position-tabs .van-tabs__wrap) {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
  height: 48px;
  padding: 8px 16px;
}

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

/* 转场动画 - 从右滑入 */
.trade-sub-page {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 隐藏滚动条但保持滚动功能 */
.trade-sub-content::-webkit-scrollbar {
  width: 0;
  background: transparent;
}

.trade-sub-content {
  scrollbar-width: none;
  -ms-overflow-style: none;
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
</style>
