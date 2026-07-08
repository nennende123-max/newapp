<template>
  <div class="trade-page">
    <!-- ========== DEBUG MODE: 灞忓箷璋冭瘯闈㈡澘 ========== -->
    <div style="display: none; background: var(--color-debug-bg); color: var(--color-debug-text); padding: 10px; border: 2px solid var(--color-debug-text); font-family: monospace; z-index: 9999; margin-bottom: 10px; position: sticky; top: 0;">
      <p><strong>=== DEBUG MODE ===</strong></p>
      <p>Props Symbol: {{ props.initialSymbol || 'undefined' }}</p>
      <p>Symbol Value: {{ symbol }}</p>
      <p>Is Spot Mode (Computed): {{ isSpot }}</p>
      <p>Is Spot Mode (Old): {{ isSpotMode }}</p>
      <p>Screen Height: {{ screenHeight }}px</p>
      <p>Initial Mode: {{ props.initialMode || 'undefined' }}</p>
      <p>Force Trade Tab: {{ props.forceTradeTab || 'undefined' }}</p>
      <p>Active Trade Tab: {{ activeTradeTab }}</p>
    </div>

    <!-- 鍥哄畾椤堕儴瀵艰埅鏍?- 瀛愰〉闈㈡ā寮忛殣钘?-->
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

    <!-- 鍙粴鍔ㄥ唴瀹瑰尯鍩?-->
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
        <span class="pair-name">{{ displayTitle }}/USDT</span>
        <van-icon name="arrow-down" size="12" color="var(--color-text-primary)" style="margin-left: 4px" />
      </div>
      <div class="price-change" :class="{ positive: priceChange >= 0 }">
        {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
      </div>
    </div>

    <!-- 鐜拌揣浜ゆ槗鐣岄潰 - 涓ユ牸闅旂锛屼娇鐢ㄧ嫭绔嬬殑 v-if (DEBUG MODE: 浣跨敤 isSpot) -->
    <template v-if="isSpot">
      <div class="trade-panel-container">
        <div class="trade-main">
          <!-- 宸︿晶锛氱洏鍙ｅ尯 -->
          <div ref="orderBookContainerRef" class="orderbook-side left-panel">
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

          <!-- 鍙充晶锛氫氦鏄撹〃鍗?- DEBUG MODE: 寮哄埗閲嶅啓涓虹畝鍗曠粨鏋?-->
          <div ref="orderFormRef" class="right-form-panel flex flex-col flex-1" style="border: 1px solid var(--color-border);">
            <!-- 鐜拌揣妯″紡琛ㄥ崟 - 瀹屽叏鐙珛鐨?template 鍧?-->
            <template v-if="isSpot">
              <div class="spot-zone" style="border: 0; padding: 0; margin-top: 0;">
                <p style="display: none; color: var(--color-debug-accent); font-size: 12px; font-weight: bold;">[DEBUG: 杩欐槸鐜拌揣鍖哄煙]</p>
                <!-- 涔板叆/鍗栧嚭鍒囨崲 -->
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
          <span class="est-value">鈮?楼{{ formatFiatPrice(parseFloat(price) || lastPrice) }}</span>
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

                <!-- 鐜拌揣婊戝潡 -->
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
            <span v-if="orderSide === 'buy' && formatEstimatedFeeUSDT" class="fee-usdt-note">(鈮?{{ formatEstimatedFeeUSDT }} USDT)</span>
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
            <span class="avail-label">{{ t('trade.avail') }}:</span>
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
            <span class="avail-label">{{ t('trade.sellable') }}:</span>
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
            </template>

            <!-- 鍚堢害妯″紡琛ㄥ崟 - 瀹屽叏鐙珛鐨?template 鍧楋紙绂佹浣跨敤 v-else锛?-->
            <template v-if="!isSpot">
              <div class="futures-zone" style="border: 0; padding: 0; margin-top: 0;">
                <p style="display: none; color: var(--color-debug-alt); font-size: 12px; font-weight: bold;">[DEBUG: 杩欐槸鍚堢害鍖哄煙]</p>
                <!-- 璧勪骇淇℃伅闈㈡澘锛氬悎绾︽ā寮忎笓鐢?-->
                <div class="futures-asset-panel">
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

                <!-- 鍚堢害婊戝潡 -->
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

                <div class="estimated-received-row">
                  <span class="received-label">{{ t('trade.margin_amount') }}</span>
                  <span class="received-value">{{ futuresMargin > 0 ? futuresMargin.toFixed(2) : '0.00' }} USDT</span>
                </div>

                <!-- 鍚堢害鎿嶄綔鎸夐挳 -->
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
            </template>
          </div>
        </div>

        <!-- 鐜拌揣搴曢儴锛氬鎵樹笌璧勪骇 -->
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
    </template>

    <!-- 鍚堢害浜ゆ槗鐣岄潰 - 涓ユ牸闅旂锛屼娇鐢ㄧ嫭绔嬬殑 v-if锛堢姝娇鐢?v-else锛?DEBUG MODE: 浣跨敤 !isSpot) -->
    <template v-if="!isSpot">
      <div class="trade-panel-container">
        <!-- 鍚堢害鎺у埗鏍忥細鍏ㄤ粨鏂囨湰 + 鏉犳潌鍊嶆暟锛堝乏杈癸級锛岃祫閲戣垂鐜囷紙鍙宠竟锛?-->
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

      <!-- 鏍稿績浜ゆ槗鍖?- 宸﹀彸甯冨眬 -->
      <div class="futures-trade-main">
          <!-- 宸︿晶锛氱洏鍙ｅ尯 -->
          <div ref="orderBookContainerRef" class="futures-orderbook-side left-panel">
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

          <!-- 鍙充晶锛氫氦鏄撹〃鍗?- 鍚堢害妯″紡涓撶敤锛屾棤闇€ template 鍖呰９锛堝凡鍦ㄥ悎绾︽ā鏉垮唴锛?-->
          <div ref="orderFormRef" class="futures-form-side right-panel">
            <!-- 璧勪骇淇℃伅闈㈡澘锛氬悎绾︽ā寮忎笓鐢?-->
            <div class="futures-asset-panel">
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
            <!-- 鍚堢害妯″紡锛氫娇鐢?futuresPrice 瀛楁 -->
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
            <!-- 鍚堢害妯″紡锛氫娇鐢?futuresAmount 瀛楁 -->
            <input
              v-model="futuresAmount"
              type="number"
              :placeholder="t('trade.amount_placeholder')"
              class="input-field no-spinner"
              @input="handleFuturesAmountInput"
            />
            <span class="input-suffix">{{ currentCoinConfig.baseCoin }}</span>
          </div>

          <!-- 鏉犳潌婊戝潡锛氬悎绾︽ā寮忎笓鐢?-->
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

          <!-- 璐圭敤鍜屾€婚锛氭牴鎹ā寮忔樉绀轰笉鍚岀殑璁＄畻閫昏緫 -->
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

          <!-- 淇濊瘉閲戦噾棰濓細鍚堢害妯″紡涓撶敤 -->
          <div class="estimated-received-row">
            <span class="received-label">{{ t('trade.margin_amount') }}</span>
            <span class="received-value">{{ futuresMargin > 0 ? futuresMargin.toFixed(2) : '0.00' }} USDT</span>
          </div>

          <!-- 鎿嶄綔鎸夐挳锛氬悎绾︽ā寮忎笓鐢?- 寮€澶?寮€绌烘寜閽?-->
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

      <!-- 搴曢儴锛氭寔浠撶湅鏉?-->
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
          <!-- 鎸佹湁浠撲綅Tab锛氬悎绾︽ā寮忎笓鐢?-->
          <van-tab :title="t('trade.positions_tab', { count: positions.length })">
            <div class="positions-list">
              <div v-if="positions.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="orders-o" size="48" color="var(--color-text-secondary)" />
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
                  <!-- 宸︿晶锛氭搷浣滆鎯?-->
                  <div class="history-order-left">
                    <div class="history-order-header">
                      <!-- 寮哄钩璁㈠崟鐗规畩鏍囩 -->
                      <div 
                        v-if="order.type === 'liquidation' || order.type === 'LIQUIDATION'"
                        class="liquidation-badge"
                      >
                        {{ t('trade.forced_liquidation') }}
                      </div>
                      <!-- 鏅€氳鍗曟柟鍚戞爣绛?-->
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
                  
                  <!-- 鍙充晶锛氭牳蹇冪粨鏋滐紙鐩堜簭 + 鏃堕棿锛?-->
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

                <!-- IntersectionObserver 鐩戝惉鐩爣锛堣Е搴曢敋鐐癸級 -->
                <div ref="loadMoreTrigger" class="history-observer-target"></div>

                <!-- 搴曢儴鐘舵€佹爮 -->
                <div class="history-footer">
                  <!-- 鍔犺浇涓?-->
                  <div v-if="historyLoading" class="history-loading">
                    <van-loading type="spinner" color="var(--color-accent)" size="16px" />
                    <span class="loading-text">{{ t('common.loading') || '鍔犺浇涓?..' }}</span>
                  </div>
                  <!-- 娌℃湁鏇村浜?-->
                  <div v-else-if="!historyHasMore && futuresHistoryList.length > 0" class="history-no-more">
                    - 浠呭睍绀鸿繎 3 涓湀鐨勮褰?-
                  </div>
                </div>
              </div>
            </div>
          </van-tab>
        </van-tabs>
      </div>
    </div>
    </template>
    <!-- 鍙粴鍔ㄥ唴瀹瑰尯鍩熺粨鏉?-->
        </div>
    <!-- trade-scrollable-content 缁撴潫 -->

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

    <!-- 鏉犳潌閫夋嫨寮圭獥锛氫粎鍦ㄥ悎绾︽ā寮忎笅鏄剧ず -->
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

    <!-- 姝㈢泩姝㈡崯寮圭獥锛氫粎鍦ㄥ悎绾︽ā寮忎笅鏄剧ず -->
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
        <!-- 澶撮儴瑁呴グ绾?-->
        <div class="modal-drag-indicator"></div>
        
        <div class="premium-modal-header">
          <div class="header-title-wrap">
            <span class="gold-dot"></span>
          <h3>{{ t('trade.take_profit_stop_loss') }}</h3>
        </div>
          <van-icon name="cross" @click="showTPSLPopup = false" class="premium-close-btn" />
        </div>

        <div class="premium-tpsl-form">
          <!-- 姝㈢泩浠锋牸杈撳叆 -->
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

          <!-- 姝㈡崯浠锋牸杈撳叆 -->
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

            <!-- 閿欒鎻愮ず -->
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

          <!-- 鏍稿績鎵ц鎸夐挳 -->
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
import CryptoIcon from '../CryptoIcon.vue';

defineOptions({
  name: 'Trade'
});

// Props: 鏀寔瀛愰〉闈㈡ā寮?
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
  // 寮哄埗鎸囧畾浜ゆ槗绫诲瀷锛堝瓙椤甸潰浣跨敤锛?
  forceTradeTab: {
    type: String,
    default: null,
    validator: (value) => !value || value === 'spot' || value === 'futures'
  },
  // 鍒濆妯″紡锛堝瓙椤甸潰浣跨敤锛岀敤浜庢帶鍒剁晫闈㈡樉绀猴級
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

// 淇1锛氳绠楀睘鎬х粦瀹?pageTitle锛岃В鍐宠瑷€鍒囨崲闂
const pageTitle = computed(() => t('trade.title'));

// 鏍囬鏄剧ず閫昏緫锛氱Щ闄?姘哥画"浜屽瓧鐢ㄤ簬鏄剧ず锛屼絾鍦ㄩ€昏緫鍒ゆ柇涓繚鐣欏師濮嬪€?
const displayTitle = computed(() => {
  const title = symbol.value || '';
  return title.replace(/\s*姘哥画/g, '').trim();
});

// 鏀寔瀛愰〉闈㈡ā寮忥細浼樺厛浣跨敤props浼犲叆鐨剆ymbol锛屽惁鍒欎娇鐢ㄨ矾鐢卞弬鏁?
const symbol = ref(props.initialSymbol || route.query.symbol || 'BTC');

// 鏀寔浠?props 鎴栬矾鐢卞弬鏁拌幏鍙栧垵濮嬫柟鍚?
const orderSide = ref(
  props.initialSide || (route.query.side === 'buy' || route.query.side === 'sell' ? route.query.side : 'buy')
);

const coinConfigs = {
  // 涓绘祦楂樹环甯侊細浠锋牸淇濈暀2浣嶏紝鏁伴噺淇濈暀4-6浣?
  'BTC/USDT': { priceFixed: 2, amountFixed: 6, step: 0.01, baseCoin: 'BTC' },
  'ETH/USDT': { priceFixed: 2, amountFixed: 4, step: 0.01, baseCoin: 'ETH' },
  'BNB/USDT': { priceFixed: 2, amountFixed: 3, step: 0.1, baseCoin: 'BNB' },
  'SOL/USDT': { priceFixed: 2, amountFixed: 2, step: 0.01, baseCoin: 'SOL' },
  // 浣庝环甯侊細浠锋牸淇濈暀4浣?鐪嬫竻寰皬娉㈠姩)锛屾暟閲忎繚鐣?浣?涓嶉渶瑕佸お纰?
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

// 瀛愰〉闈㈡ā寮忎笅锛屾牴鎹?forceTradeTab prop 璁剧疆鍒濆鏍囩椤?
// 涓婚〉闈㈡ā寮忎笅锛岄粯璁ゆ樉绀虹幇璐?
const activeTradeTab = ref(props.forceTradeTab || 'spot');

// 寮哄埗淇 isSpot 閫昏緫 - DEBUG MODE
const isSpot = computed(() => {
  console.log('馃攳 [DEBUG] Calculating Mode for:', props.initialSymbol);
  if (!props.initialSymbol) {
    console.log('馃攳 [DEBUG] No symbol prop, defaulting to spot');
    return true; // 榛樿鐜拌揣
  }
  // 鍙鍚嶅瓧閲屽甫 '姘哥画'銆?SWAP'銆?USD' (濡傛灉鏄悎绾︾壒寰? 灏卞垽瀹氫负鍚堢害
  const isFutures = props.initialSymbol.includes('姘哥画') || props.initialSymbol.includes('SWAP') || props.initialSymbol.includes('swap');
  const result = !isFutures;
  console.log('馃攳 [DEBUG] Symbol check result:', { symbol: props.initialSymbol, isFutures, isSpot: result });
  return result;
});

// 淇濈暀鏃х殑 isSpotMode 浠ュ吋瀹圭幇鏈変唬鐮?
const isSpotMode = computed(() => {
  // 棣栧厛妫€鏌?symbol 鏄惁鍖呭惈鍚堢害鏍囪瘑
  const symbolText = symbol.value || '';
  if (symbolText.includes('姘哥画') || symbolText.includes('SWAP') || symbolText.includes('swap')) {
    return false; // 鏄悎绾?
  }
  
  // 瀛愰〉闈㈡ā寮忎笅锛屼娇鐢?initialMode prop
  if (props.isSubPage) {
    return props.initialMode === 'spot';
  }
  
  // 涓婚〉闈㈡ā寮忎笅锛屾牴鎹?activeTradeTab 鍒ゆ柇
  return activeTradeTab.value === 'spot';
});

// 娣诲姞璋冭瘯鏃ュ織
watch([isSpot, isSpotMode], ([newIsSpot, newIsSpotMode]) => {
  console.log('[TradePanel] Mode changed:', {
    isSpot: newIsSpot ? 'Spot' : 'Futures',
    isSpotMode: newIsSpotMode ? 'Spot' : 'Futures',
    symbol: symbol.value,
    propsSymbol: props.initialSymbol,
    initialMode: props.initialMode,
    activeTradeTab: activeTradeTab.value
  });
}, { immediate: true });

// 灞忓箷楂樺害鐩戞帶 - DEBUG MODE
const screenHeight = ref(typeof window !== 'undefined' ? window.innerHeight : 0);
const updateScreenHeight = () => {
  if (typeof window !== 'undefined') {
    screenHeight.value = window.innerHeight;
  }
};

// 瀛愰〉闈㈡ā寮忎笅锛岀姝㈠垏鎹㈡爣绛鹃〉锛堝洜涓烘爣绛惧垏鎹㈠櫒宸茶闅愯棌锛?
const canSwitchTab = computed(() => !props.isSubPage);
// orderSide 宸插湪涓婇潰瀹氫箟锛堟敮鎸?props 浼犲叆锛?
const orderType = ref('limit'); 
const price = ref('');
const amount = ref('');
const priceChange = ref(1.83);
const lastPrice = ref(92255.50);
const activeOrderTab = ref('orders');
const selectedPercent = ref(null);
const spotSliderValue = ref(0); // 鐜拌揣婊戝潡鍊?(0-100)
// 鏁版嵁闅旂锛氱幇璐у拰鍚堢害璁㈠崟鍒嗗紑瀛樺偍
const spotOrdersList = ref([]);      // 鐜拌揣璁㈠崟鍒楄〃
const futuresOrdersList = ref([]);   // 鍚堢害璁㈠崟鍒楄〃

// 娉ㄦ剰锛氫笉鍐嶄娇鐢?ordersList computed锛岀洿鎺ヤ娇鐢?spotOrdersList 鍜?futuresOrdersList
// const ordersList = computed(() => {
//   return activeTradeTab.value === 'spot' ? spotOrdersList.value : futuresOrdersList.value;
// });
const showOrderTypeSheet = ref(false);
const currentLeverage = ref(20); // 榛樿鏉犳潌20x
const isLoading = ref(false); // 涓嬪崟鍔犺浇鐘舵€?
const showLeveragePopup = ref(false);

// 鍚堢害浜ゆ槗鐩稿叧鍙橀噺
const marginMode = ref('cross'); // 'cross' 鍏ㄤ粨, 'isolated' 閫愪粨
const markPrice = ref(92255.50);
const futuresPrice = ref('');
const futuresAmount = ref('');
const selectedFuturesPercent = ref(null);
const futuresSliderValue = ref(0); // 鍚堢害婊戝潡鍊?(0-100)
// 鐜拌揣妯″紡涓嬮粯璁ら€変腑"褰撳墠濮旀墭"Tab锛堢储寮?锛夛紝鍚堢害妯″紡涓嬮粯璁ら€変腑"鎸佹湁浠撲綅"Tab锛堢储寮?锛?
// 娉ㄦ剰锛氱敱浜?van-tabs 闇€瑕?ref锛屾垜浠娇鐢?ref + watch 鏉ュ疄鐜板姩鎬佸垏鎹?
const activePositionTab = ref(0);

// 鐩戝惉 isSpotMode 鍙樺寲锛岃嚜鍔ㄥ垏鎹?Tab
watch(isSpotMode, (isSpot) => {
  if (props.isSubPage) {
    activePositionTab.value = isSpot ? 1 : 0; // 鐜拌揣妯″紡閫変腑"褰撳墠濮旀墭"锛屽悎绾︽ā寮忛€変腑"鎸佹湁浠撲綅"
  }
}, { immediate: true });

// 鍒濆鍖栨椂璁剧疆姝ｇ‘鐨?Tab
if (props.isSubPage && isSpotMode.value) {
  activePositionTab.value = 1; // 鐜拌揣妯″紡榛樿閫変腑"褰撳墠濮旀墭"
}
const positions = ref([]);
const futuresHistoryList = ref([]);  // 鍚堢害鍘嗗彶璁㈠崟鍒楄〃
const historyPage = ref(1);  // 褰撳墠椤电爜锛堜粠1寮€濮嬶級
const historyPageSize = ref(20);  // 姣忛〉鏉℃暟
const historyHasMore = ref(true);  // 鏄惁杩樻湁鏇村鏁版嵁
const historyLoading = ref(false);  // 鏄惁姝ｅ湪鍔犺浇
const loadMoreTrigger = ref(null);  // IntersectionObserver 鐩戝惉鐩爣锛堢粦瀹氬埌搴曢儴閭ｄ釜鐪嬩笉瑙佺殑 div锛?
let historyObserver = null;  // 瀛樻斁瑙傚療鍣ㄥ疄渚?
const showTPSLPopup = ref(false);

// 璧勪骇淇℃伅璁＄畻灞炴€э紙鍚堢害椤甸潰锛?
const usdtBalance = computed(() => {
  return assetStore.userAssets?.USDT || 0;
});

const frozenMargin = computed(() => {
  return assetStore.userAssets?.USDT_frozen || 0;
});

// 璁＄畻鎵€鏈夋寔浠撳崰鐢ㄧ殑淇濊瘉閲戞€诲拰锛堝凡鍗犵敤淇濊瘉閲戯級
const totalPositionMargin = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.margin || 0), 0);
});

const totalUnrealizedPnl = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.unrealizedPnl || 0), 0);
});

// 璐︽埛鏉冪泭 = 浣欓 + 鏈疄鐜扮泩浜?
const totalEquity = computed(() => {
  return usdtBalance.value + totalUnrealizedPnl.value;
});

// 鍙敤淇濊瘉閲?= 璐︽埛鏉冪泭 - 宸插崰鐢ㄤ繚璇侀噾 - 濮旀墭鍐荤粨
const availableMargin = computed(() => {
  const equity = totalEquity.value;
  const usedMargin = totalPositionMargin.value;
  const frozen = frozenMargin.value;
  const available = Math.max(0, equity - usedMargin - frozen);
  
  // 璋冭瘯鏃ュ織锛氶獙璇佸叕寮?璐︽埛鏉冪泭 = 鍙敤 + 鍗犵敤 + 鍐荤粨
  if (process.env.NODE_ENV === 'development' && positions.value.length > 0) {
    const sum = available + usedMargin + frozen;
    const diff = Math.abs(equity - sum);
    if (diff > 0.01) { // 鍏佽0.01鐨勮宸?
      console.warn(`[璧勪骇璁＄畻] 鍏紡楠岃瘉澶辫触: 璐︽埛鏉冪泭(${equity.toFixed(2)}) 鈮?鍙敤(${available.toFixed(2)}) + 鍗犵敤(${usedMargin.toFixed(2)}) + 鍐荤粨(${frozen.toFixed(2)}) = ${sum.toFixed(2)}, 宸€? ${diff.toFixed(2)}`);
    } else {
      console.log(`[璧勪骇璁＄畻] 鉁?鍏紡楠岃瘉閫氳繃: 璐︽埛鏉冪泭(${equity.toFixed(2)}) = 鍙敤(${available.toFixed(2)}) + 鍗犵敤(${usedMargin.toFixed(2)}) + 鍐荤粨(${frozen.toFixed(2)})`);
    }
  }
  
  return available;
});

// PnL 鍙樺寲闂儊鏁堟灉
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
// 璧勯噾璐圭巼锛堟瘡8灏忔椂鏇存柊涓€娆★紝閫氬父鑼冨洿鍦?-0.01% 鍒?0.01% 涔嬮棿锛?
const fundingRate = ref(0.0001); // 0.01% = 0.0001 

// 妯℃嫙甯佺浠锋牸鏁版嵁锛堜笌鍚庣 MOCK_MARKET_PRICES 淇濇寔涓€鑷达級
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
const maxVisibleRows = ref(12); // balanced orderbook depth for one-screen trading layout

// 缂撳瓨鏈€澶ф暟閲忓€硷紝閬垮厤閲嶅璁＄畻
const maxQuantityCache = {
  asks: null,
  bids: null,
  asksListHash: null,
  bidsListHash: null
};

/**
 * 鐢熸垚鍒楄〃鐨勭畝鍗曞搱甯屽€硷紝鐢ㄤ簬妫€娴嬪垪琛ㄦ槸鍚﹀彉鍖?
 * @param {Array} list - 璁㈠崟鍒楄〃
 * @returns {string} 鍝堝笇鍊?
 */
const getListHash = (list) => {
  if (!list || list.length === 0) return '';
  // 浣跨敤鍓嶅嚑涓拰鏈€鍚庝竴涓厓绱犵殑鏁伴噺鍊肩敓鎴愮畝鍗曞搱甯?
  const firstQty = list[0]?.quantity || 0;
  const lastQty = list[list.length - 1]?.quantity || 0;
  const length = list.length;
  return `${length}-${firstQty}-${lastQty}`;
};

// 鐢熸垚鐩樺彛鏁版嵁锛堢敓鎴愯冻澶熷鐨勬暟鎹紝渚涘姩鎬佹樉绀轰娇鐢級
const generateOrderBook = () => {
  const basePrice = lastPrice.value;
  const totalRows = 100; // 鐢熸垚100琛屾暟鎹紝纭繚鏈夎冻澶熺殑鏁版嵁濉厖
  
  // 鐢熸垚鍗栧崟锛堜粠楂樺埌浣庯級
  const newAsks = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (totalRows - i) * 0.01 + Math.random() * 0.1;
    const quantity = Math.random() * 5 + 0.00001;
    newAsks.push({
      price: basePrice + priceOffset,
      quantity: quantity
    });
  }
  asks.value = newAsks.sort((a, b) => a.price - b.price); // 鎸変环鏍间粠浣庡埌楂樻帓搴?
  
  // 鐢熸垚涔板崟锛堜粠浣庡埌楂橈級
  const newBids = [];
  for (let i = 0; i < totalRows; i++) {
    const priceOffset = (i + 1) * 0.01 + Math.random() * 0.1;
    const quantity = Math.random() * 5 + 0.00001;
    newBids.push({
      price: basePrice - priceOffset,
      quantity: quantity
    });
  }
  bids.value = newBids.sort((a, b) => b.price - a.price); // 鎸変环鏍间粠楂樺埌浣庢帓搴?
};

// 璁＄畻鍙樉绀虹殑鏈€澶ц鏁帮紙鏍规嵁鍙充晶瀹瑰櫒楂樺害锛?
const calculateMaxRows = () => {
  if (!orderFormRef.value) {
    return 20; // 榛樿鏄剧ず20琛岋紝閬垮厤鐣欑櫧杩囧ぇ
  }
  
  const rightSideHeight = orderFormRef.value.clientHeight;
  const headerHeight = 24; // orderbook-header 楂樺害
  const lastPriceHeight = 32; // last-price 楂樺害
  const rowHeight = 20; // 姣忚楂樺害
  
  // 鍙敤楂樺害 = 鍙充晶楂樺害 - 鐩樺彛澶撮儴 - 涓棿鏈€鏂颁环
  // 娉ㄦ剰锛氭垜浠笇鏈涘乏渚ф€婚珮搴﹀拰鍙充晶瀹屽叏涓€鑷?
  const availableHeight = rightSideHeight - headerHeight - lastPriceHeight;
  
  // 涔板崠鍗曞悇鍗犱竴鍗婇珮搴?
  const halfHeight = availableHeight / 2;
  const rowsPerSide = Math.floor(halfHeight / rowHeight);
  
  // 杩斿洖鍗曚晶搴旀樉绀虹殑琛屾暟锛屾渶灏忔樉绀?0琛岋紝鏈€澶?00琛?
  return Math.max(8, Math.min(12, rowsPerSide));
};

// 鍔ㄦ€佽绠楁樉绀虹殑涔板崠鍗曟暟閲?
const displayedAsks = computed(() => {
  // 鍗栧崟锛氬彇鏈€浣庣殑 n 琛岋紝骞跺€掑簭鎺掑垪锛堥珮浠峰湪涓婏紝浣庝环鍦ㄤ笅锛?
  return asks.value.slice(0, maxVisibleRows.value).reverse();
});

const displayedBids = computed(() => {
  // 涔板崟锛氬彇鏈€楂樼殑 n 琛岋紙楂樹环鍦ㄤ笂锛屼綆浠峰湪涓嬶級
  return bids.value.slice(0, maxVisibleRows.value);
});

// 鐩戝惉绐楀彛澶у皬鍙樺寲锛岄噸鏂拌绠楄鏁?
const handleResize = () => {
  maxVisibleRows.value = calculateMaxRows();
};

// 浣跨敤 ResizeObserver 鐩戝惉鍙充晶涓嬪崟鍖虹殑楂樺害鍙樺寲
let resizeObserver = null;

// 鍒濆鍖栫洏鍙ｅ姩鎬佽鏁拌绠?
const initOrderBookResizeObserver = () => {
  nextTick(() => {
    if (orderFormRef.value) {
      maxVisibleRows.value = calculateMaxRows();
      
      // 浣跨敤 ResizeObserver 鐩戝惉鍙充晶瀹瑰櫒楂樺害鍙樺寲锛屼粠鑰屽喅瀹氬乏渚ф樉绀哄灏戣
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
    // 鍒囨崲椤甸潰鏃朵篃鏇存柊浠锋牸
    updatePriceForSymbol(newSymbol);
  }
});

// 鐩戝惉浜ゆ槗鏍囩椤靛垏鎹紝閲嶆柊璁＄畻鐩樺彛琛屾暟
watch(activeTradeTab, () => {
  nextTick(() => {
    initOrderBookResizeObserver();
  });
});

watch(() => route.query.side, (newSide) => {
  if (newSide === 'buy' || newSide === 'sell') orderSide.value = newSide;
}, { immediate: true });

// 淇2锛氱洃鍚?symbol 鍙樺寲锛岃嚜鍔ㄦ洿鏂拌緭鍏ユ浠锋牸涓哄搴斿竵绉嶇殑鏈€鏂颁环
watch(symbol, (newSymbol) => {
  updatePriceForSymbol(newSymbol);
});

// 杈呭姪鍑芥暟锛氭牴鎹竵绉嶆洿鏂颁环鏍?
const updatePriceForSymbol = (newSymbol) => {
  lastPrice.value = coinPrices[newSymbol] || 92255.50;
  
  // 浠呭湪娌℃湁鐪熷疄娣卞害鏁版嵁鏃讹紝鐢熸垚妯℃嫙鏁版嵁浣滀负鍒濆鏄剧ず
  const realDepth = marketStore.depths[newSymbol];
  if (!realDepth || !realDepth.asks.length) {
  generateOrderBook();
  } else {
    asks.value = [...realDepth.asks];
    bids.value = [...realDepth.bids];
  }

  // 鍙湁鏄檺浠峰崟鏃讹紝鎵嶈嚜鍔ㄥ～鍏呬环鏍?
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
    
    // 鍚堢害浜ゆ槗浣跨敤鍚堢害璐︽埛浣欓
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
  // 1. 绠€鍗曞垽绌轰繚鎶?
  if (!assetStore.userAssets) return 0;
  
  // 2. 鏍规嵁褰撳墠鏄?涔?杩樻槸"鍗?鏉ュ喅瀹氭樉绀哄摢涓竵绉嶇殑鍐荤粨棰?
  // 涔板叆鏃?(Buy BTC) -> 鏄剧ず鍐荤粨鐨?USDT
  if (orderSide.value === 'buy') {
    return assetStore.userAssets['USDT_frozen'] || 0;
  }
  // 鍗栧嚭鏃?(Sell BTC) -> 鏄剧ず鍐荤粨鐨?BTC (鍗?symbol)
  else {
    const frozenKey = `${symbol.value}_frozen`;
    return assetStore.userAssets[frozenKey] || 0;
  }
});

// 鍒ゆ柇鎸佷粨鏂瑰悜鏄惁涓哄鍗?
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

// 鏍煎紡鍖栬祫浜ф暟閲忥紙浣跨敤缁熶竴鐨勬牸寮忓寲鍑芥暟锛?
// 鏍煎紡鍖栬祫浜т綑棰濓紙浣跨敤缁熶竴鐨勬牸寮忓寲鍑芥暟锛岀‘淇濆皬鏁颁綅姝ｇ‘锛?
const formatAssetBalance = (value, symbol = '') => {
  // 浣跨敤鐜版湁鐨?formatAssetAmount 鍑芥暟锛屽畠宸茬粡澶勭悊浜嗕笉鍚屽竵绉嶇殑灏忔暟浣?
  return formatAssetAmount(value, symbol);
};

/**
 * 璁＄畻璁㈠崟绨挎繁搴︽潯鐨勫搴︾櫨鍒嗘瘮
 * @param {number} quantity - 褰撳墠璁㈠崟鐨勬暟閲?
 * @param {Array} list - 璁㈠崟鍒楄〃锛坅sks 鎴?bids锛?
 * @param {string} type - 璁㈠崟绫诲瀷 ('asks' 鎴?'bids')
 * @param {Object} options - 鍙€夐厤缃?
 * @param {boolean} options.smooth - 鏄惁浣跨敤骞虫粦鏇茬嚎锛堝钩鏂规牴鍑芥暟锛変娇瑙嗚鏁堟灉鏇磋嚜鐒讹紝榛樿 true
 * @param {number} options.minWidth - 鏈€灏忓搴︾櫨鍒嗘瘮锛岄粯璁?0
 * @param {number} options.maxWidth - 鏈€澶у搴︾櫨鍒嗘瘮锛岄粯璁?100
 * @param {boolean} options.useCache - 鏄惁浣跨敤缂撳瓨锛岄粯璁?true
 * @returns {number} 娣卞害鏉″搴︾櫨鍒嗘瘮 (0-100)
 */
const getDepthWidth = (quantity, list, type, options = {}) => {
  // 鍙傛暟楠岃瘉
  if (!list || list.length === 0 || !quantity || quantity <= 0) {
    return options.minWidth || 0;
  }

  // 鑾峰彇鎴栬绠楁渶澶ф暟閲忥紙浣跨敤缂撳瓨浼樺寲鎬ц兘锛?
  let maxQuantity;
  const useCache = options.useCache !== false;
  const listHash = useCache ? getListHash(list) : null;
  const cacheKey = type === 'asks' ? 'asks' : 'bids';
  
  if (useCache && 
      maxQuantityCache[`${cacheKey}ListHash`] === listHash && 
      maxQuantityCache[cacheKey] !== null) {
    // 浣跨敤缂撳瓨鍊?
    maxQuantity = maxQuantityCache[cacheKey];
  } else {
    // 璁＄畻鏂扮殑鏈€澶ф暟閲?
    maxQuantity = Math.max(...list.map(item => item.quantity || 0));
    
    // 鏇存柊缂撳瓨
    if (useCache) {
      maxQuantityCache[cacheKey] = maxQuantity;
      maxQuantityCache[`${cacheKey}ListHash`] = listHash;
    }
  }
  
  // 杈圭晫鎯呭喌澶勭悊
  if (maxQuantity === 0) {
    return options.minWidth || 0;
  }
  
  if (maxQuantity < quantity) {
    return options.maxWidth || 100;
  }

  // 璁＄畻鍩虹姣斾緥
  const ratio = quantity / maxQuantity;
  
  // 搴旂敤骞虫粦鏇茬嚎锛堝钩鏂规牴鍑芥暟锛変娇瑙嗚鏁堟灉鏇磋嚜鐒?
  // 杩欐牱鍙互閬垮厤灏忔暟閲忚鍗曠殑娣卞害鏉¤繃灏忥紝鍚屾椂淇濇寔澶ф暟閲忚鍗曠殑瑙嗚绐佸嚭
  const smoothRatio = options.smooth !== false ? Math.sqrt(ratio) : ratio;
  
  // 璁＄畻鐧惧垎姣斿搴?
  const width = smoothRatio * 100;
  
  // 搴旂敤鏈€灏?鏈€澶у搴﹂檺鍒?
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
  
  // 鍙嶅悜璁＄畻鐧惧垎姣旓細鏍规嵁杈撳叆鐨勬暟閲忔洿鏂版粦鍧楀€?
  updateSpotSliderFromAmount();
};

// 鏍规嵁杈撳叆鐨勬暟閲忓弽鍚戣绠楁粦鍧楃櫨鍒嗘瘮
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
      // 涔板叆锛氭牴鎹暟閲忚绠楁€昏姳璐癸紝鍐嶈绠楃櫨鍒嗘瘮
      // percent = (amount * price / balance) * 100
      const totalCost = inputAmount * orderPrice;
      percent = Math.min(100, Math.max(0, (totalCost / balance) * 100));
    } else {
      // 鍗栧嚭锛氱洿鎺ヨ绠楃櫨鍒嗘瘮
      // percent = (amount / balance) * 100
      percent = Math.min(100, Math.max(0, (inputAmount / balance) * 100));
    }
    
    // 鐩存帴浣跨敤璁＄畻鍑虹殑鐧惧垎姣旓紙鍏佽浠绘剰绮惧害锛?
    spotSliderValue.value = Math.round(percent);
  } catch (error) {
    console.error('Error updating slider from amount:', error);
  }
};

// 婊戝潡鍙樺寲浜嬩欢澶勭悊
const onSpotSliderChange = (value) => {
  // 纭繚鍊煎湪鏈夋晥鑼冨洿鍐?
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
      // 涔板叆鎿嶄綔锛歛mount = (浣欓 * percent / 100) / price
      let scalingFactor = percent / 100;
      
      // 濡傛灉鏄?100%锛岄鐣欑紦鍐茬┖闂撮槻姝㈣绠楃簿搴︽孩鍑烘垨婊戠偣
      if (percent === 100) {
        // 闄愪环鍗曪細棰勭暀 0.1% 缂撳啿绌洪棿
        // 甯備环鍗曪細棰勭暀 0.5% 缂撳啿绌洪棿锛堥槻姝环鏍兼尝鍔ㄥ拰婊戠偣锛?
        scalingFactor = orderType.value === 'market' ? 0.995 : 0.999;
      }
      
      const totalCost = balance * scalingFactor;
      const calculatedAmount = totalCost / orderPrice;
      amount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(config.amountFixed) : '';
    } else {
      // 鍗栧嚭鎿嶄綔锛歛mount = 浣欓 * percent / 100
      let scalingFactor = percent / 100;
      
      // 濡傛灉鏄?100%锛岄鐣欐瀬灏忕紦鍐茬┖闂?
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

// ========== 璐圭巼甯搁噺 ==========
const SPOT_FEE_RATE = 0.001;   // 鐜拌揣 0.1%
const FUTURES_FEE_RATE = 0.0004; // 鍚堢害 0.04% (涓庡悗绔繚鎸佷竴鑷?

// ========== 鐜拌揣浜ゆ槗璁＄畻灞炴€?==========

// 鑾峰彇褰撳墠鏈夋晥鐨勪环鏍硷紙甯備环鍗曚娇鐢ㄥ綋鍓嶄环鏍硷紝闄愪环鍗曚娇鐢ㄧ敤鎴疯緭鍏ヤ环鏍硷級
const spotCurrentPrice = computed(() => {
  if (orderType.value === 'market') {
    return lastPrice.value; // 甯備环鍗曚娇鐢ㄦ渶鏂颁环鏍?
  }
  return parseFloat(price.value) || lastPrice.value; // 闄愪环鍗曚娇鐢ㄧ敤鎴疯緭鍏ワ紝鍚﹀垯浣跨敤鏈€鏂颁环鏍?
});

// 鐜拌揣棰勪及鎵嬬画璐?
const spotEstimatedFee = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  
  if (p <= 0 || a <= 0) return 0;
  
  if (orderSide.value === 'buy') {
    // 涔板叆锛氭墜缁垂浠庤幏寰楃殑甯佺涓墸闄わ紝鏄剧ず甯佺鍗曚綅
    return a * SPOT_FEE_RATE;
  } else {
    // 鍗栧嚭锛氭墜缁垂浠庤幏寰楃殑 USDT 涓墸闄わ紝鏄剧ず USDT 鍗曚綅
    return (p * a) * SPOT_FEE_RATE;
  }
});

// 鏍煎紡鍖栫幇璐ч浼版墜缁垂鏄剧ず
const formatEstimatedFee = computed(() => {
  const fee = spotEstimatedFee.value;
  if (fee <= 0) return '0.00';
  
  if (orderSide.value === 'buy') {
    // 涔板叆锛氭樉绀哄竵绉嶅崟浣?
    const config = currentCoinConfig.value;
    return fee.toFixed(config.amountFixed);
  } else {
    // 鍗栧嚭锛氭樉绀?USDT 鍗曚綅
    return formatAssetBalance(fee, 'USDT');
  }
});

// 涔板叆鏃剁殑鎵嬬画璐?USDT 绛夊€硷紙鐢ㄤ簬灏忓瓧澶囨敞锛?
const formatEstimatedFeeUSDT = computed(() => {
  if (orderSide.value !== 'buy') return '';
  const fee = spotEstimatedFee.value;
  if (fee <= 0) return '';
  
  const p = spotCurrentPrice.value;
  const feeUSDT = fee * p; // BTC鎵嬬画璐?* BTC浠锋牸 = USDT绛夊€?
  return feeUSDT > 0 ? formatAssetBalance(feeUSDT, 'USDT') : '';
});

// 鐜拌揣鎬婚锛堝悕涔変环鍊硷級
const spotTotal = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  
  if (p <= 0 || a <= 0) return 0;
  
  // 鎬婚 = 浠锋牸 * 鏁伴噺锛堝悕涔変环鍊硷級
  return p * a;
});

// 鏍煎紡鍖栫幇璐ф€婚鏄剧ず
const formatTotalAmount = computed(() => {
  const total = spotTotal.value;
  return total > 0 ? total.toFixed(2) : '0.00';
});

// 棰勪及鍒拌处閲戦锛堢敤鎴峰疄闄呰兘鎷垮埌鐨勬暟閲忥級
const formatEstimatedReceived = computed(() => {
  const p = spotCurrentPrice.value;
  const a = parseFloat(amount.value) || 0;
  if (p <= 0 || a <= 0) return '0.00';
  
  if (orderSide.value === 'buy') {
    // 涔板叆锛氬疄闄呭緱鍒扮殑甯佺 = amount - fee
    const fee = spotEstimatedFee.value;
    const received = a - fee;
    const config = currentCoinConfig.value;
    return received > 0 ? received.toFixed(config.amountFixed) + ' ' + currentCoinConfig.value.baseCoin : '0.00 ' + currentCoinConfig.value.baseCoin;
  } else {
    // 鍗栧嚭锛氬疄闄呭緱鍒扮殑 USDT = total - fee锛堢粺涓€浣跨敤 formatAssetBalance 纭繚 2 浣嶅皬鏁帮級
    const total = spotTotal.value;
    const fee = spotEstimatedFee.value;
    const received = total - fee;
    return received > 0 ? formatAssetBalance(received, 'USDT') + ' USDT' : '0.00 USDT';
  }
});

// 鍙敤浣欓锛氬缁堟樉绀?USDT 浣欓锛堜拱鍏ユ椂鐢?USDT锛屽崠鍑烘椂涔熼渶瑕?USDT 鏀粯鎵嬬画璐癸級
const formatAvailableBalance = computed(() => {
  const usdtBalance = assetStore?.usdtBalance || 0;
  return formatAssetBalance(usdtBalance, 'USDT') + ' USDT';
});

// 鍙崠浣欓锛氬缁堟樉绀哄竵绉嶆寔浠擄紙涔板叆鍚庡彲浠ュ崠甯侊紝鍗栧嚭鏃朵篃闇€瑕佹湁甯佹墠鑳藉崠锛?
const formatSellableBalance = computed(() => {
  const coinBalance = assetStore?.getHolding(symbol.value) || 0;
  return formatAssetBalance(coinBalance, symbol.value) + ' ' + symbol.value;
});

// 浣跨敤 computed 鏉ュ疄鐜板搷搴斿紡缈昏瘧
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

// 鍚堢害浜ゆ槗鐩稿叧鏂规硶
const selectFuturesPrice = (priceValue) => {
  if (orderType.value === 'limit') {
    futuresPrice.value = priceValue.toString();
  }
};

// 鍚堢害婊戝潡鍙樺寲浜嬩欢澶勭悊
const onFuturesSliderChange = (value) => {
  // 纭繚鍊煎湪鏈夋晥鑼冨洿鍐?
  const clampedValue = Math.max(0, Math.min(100, value));
  futuresSliderValue.value = clampedValue;
  setFuturesAmountPercent(clampedValue);
};

// 鏍规嵁鍚堢害杈撳叆鐨勬暟閲忓弽鍚戣绠楁粦鍧楃櫨鍒嗘瘮
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
    
    // 鍩轰簬鍙敤淇濊瘉閲戝拰鏉犳潌璁＄畻鏈€澶у彲寮€浠撲綅
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    
    if (maxAmount <= 0) {
      return;
    }
    
    // percent = (inputAmount / maxAmount) * 100
    const percent = Math.min(100, Math.max(0, (inputAmount / maxAmount) * 100));
    
    // 鐩存帴浣跨敤璁＄畻鍑虹殑鐧惧垎姣旓紙鍏佽浠绘剰绮惧害锛?
    futuresSliderValue.value = Math.round(percent);
  } catch (error) {
    console.error('Error updating futures slider from amount:', error);
  }
};

// 鍚堢害鏁伴噺杈撳叆澶勭悊
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
  
  // 鍙嶅悜璁＄畻鐧惧垎姣旓細鏍规嵁杈撳叆鐨勬暟閲忔洿鏂版粦鍧楀€?
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
    
    // 鍩轰簬鍙敤淇濊瘉閲戝拰鏉犳潌璁＄畻鏈€澶у彲寮€浠撲綅
    // 鏈€澶у彲寮€鏁伴噺 = (鍙敤淇濊瘉閲?* 鏉犳潌鍊嶆暟) / 浠锋牸
    const maxAmount = (balance * currentLeverage.value) / orderPrice;
    
    // 濡傛灉鏄?100%锛岄鐣欐瀬灏忕紦鍐茬┖闂达紙闃叉璁＄畻绮惧害闂锛?
    let scalingFactor = percent / 100;
    if (percent === 100) {
      scalingFactor = 0.999; // 棰勭暀 0.1% 缂撳啿
    }
    
    const calculatedAmount = maxAmount * scalingFactor;
    futuresAmount.value = calculatedAmount > 0 ? calculatedAmount.toFixed(currentCoinConfig.value.amountFixed) : '';
  } catch (error) {
    console.error('Error setting futures amount percent:', error);
    futuresAmount.value = '';
  }
};

// ========== 鍚堢害浜ゆ槗璁＄畻灞炴€?==========

// 鑾峰彇褰撳墠鏈夋晥鐨勪环鏍硷紙甯備环鍗曚娇鐢ㄦ爣璁颁环鏍硷紝闄愪环鍗曚娇鐢ㄧ敤鎴疯緭鍏ヤ环鏍硷級
const futuresCurrentPrice = computed(() => {
  if (orderType.value === 'market') {
    return markPrice.value; // 甯備环鍗曚娇鐢ㄦ爣璁颁环鏍?
  }
  return parseFloat(futuresPrice.value) || markPrice.value; // 闄愪环鍗曚娇鐢ㄧ敤鎴疯緭鍏ワ紝鍚﹀垯浣跨敤鏍囪浠锋牸
});

// 鍚堢害鍚嶄箟浠峰€?
const futuresNotionalValue = computed(() => {
  const p = futuresCurrentPrice.value;
  const a = parseFloat(futuresAmount.value) || 0;
  
  if (p <= 0 || a <= 0) return 0;
  
  // 鍚嶄箟浠峰€?= 浠锋牸 * 鏁伴噺
  return p * a;
});

// 鍚堢害棰勪及鎵嬬画璐?
const futuresEstimatedFee = computed(() => {
  const notional = futuresNotionalValue.value;
  if (notional <= 0) return 0;
  
  // 鎵嬬画璐?= 鍚嶄箟浠峰€?* 璐圭巼
  return notional * FUTURES_FEE_RATE;
});

// 鏍煎紡鍖栧悎绾﹂浼版墜缁垂鏄剧ず
const formatFuturesEstimatedFee = computed(() => {
  const fee = futuresEstimatedFee.value;
  return fee > 0 ? fee.toFixed(4) : '0.00';
});

// 鍚堢害淇濊瘉閲戯紙鎵€闇€淇濊瘉閲戯級
const futuresMargin = computed(() => {
  const notional = futuresNotionalValue.value;
  const leverage = currentLeverage.value || 20;
  
  if (notional <= 0 || leverage <= 0) return 0;
  
  // 淇濊瘉閲?= 鍚嶄箟浠峰€?/ 鏉犳潌鍊嶆暟
  return notional / leverage;
});

// 鍚堢害鎬婚锛堟樉绀哄悕涔変环鍊硷紝涔熷彲浠ユ樉绀轰繚璇侀噾锛?
const futuresTotal = computed(() => {
  // 杩欓噷鏄剧ず鍚嶄箟浠峰€硷紝濡傛灉闇€瑕佹樉绀轰繚璇侀噾锛屽彲浠ユ敼涓?futuresMargin.value
  return futuresNotionalValue.value;
});

// 鏍煎紡鍖栧悎绾︽€婚鏄剧ず
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

// 娉ㄦ剰锛氭鍑芥暟宸插簾寮冿紝鐜板湪鐩存帴浣跨敤鍚庣杩斿洖鐨?unrealized_pnl
// 淇濈暀姝ゅ嚱鏁颁互闃插叾浠栧湴鏂硅皟鐢紝浣嗕笉鍐嶈鐩栧悗绔繑鍥炵殑鍊?
const updatePositionsPnl = () => {
  // 涓嶅啀閲嶆柊璁＄畻锛岀洿鎺ヤ娇鐢ㄥ悗绔繑鍥炵殑 unrealized_pnl
  // 鍙洿鏂扮櫨鍒嗘瘮锛堝熀浜庡悗绔繑鍥炵殑 PnL锛?
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
      
      // 鍒锋柊鎸佷粨鍒楄〃鍜岃祫浜т綑棰?
      await fetchFuturesPositions();
      await assetStore.initData();
      
      // 鍒锋柊褰撳墠濮旀墭璁㈠崟鍒楄〃锛堝悎绾︼級
      console.log('涓嬪崟鎴愬姛锛屾鍦ㄥ己鍒跺埛鏂板悎绾﹀鎵樺垪琛?..');
      await fetchFuturesOrders();
      
      // 娓呯┖杈撳叆妗?
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
      
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    console.error('鉂?鍚堢害寮€澶氬け璐?', error);
    
    let errorMessage = t('trade.order_failed') || 'Order failed, please try again';
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
      
      // 鍒锋柊鎸佷粨鍒楄〃鍜岃祫浜т綑棰?
      await fetchFuturesPositions();
      await assetStore.initData();
      
      // 鍒锋柊褰撳墠濮旀墭璁㈠崟鍒楄〃锛堝悎绾︼級
      console.log('涓嬪崟鎴愬姛锛屾鍦ㄥ己鍒跺埛鏂板悎绾﹀鎵樺垪琛?..');
      await fetchFuturesOrders();
      
      // 娓呯┖杈撳叆妗?
      futuresAmount.value = '';
      futuresPrice.value = '';
      selectedFuturesPercent.value = null;
      futuresSliderValue.value = 0;
      
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    console.error('鉂?鍚堢害寮€绌哄け璐?', error);
    
    let errorMessage = t('trade.order_failed') || 'Order failed, please try again';
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
  
  // 濡傛灉鏄鎹熶环鏍艰皟鏁达紝闇€瑕侀獙璇佹槸鍚﹁Е鍙婂己骞崇嚎
  if (field === 'stopLossPrice' && currentTPSLPosition.value?.position) {
    const position = currentTPSLPosition.value.position;
    const liquidationPrice = position.liquidationPrice;
    const isLong = position.side === 'long' || position.side === 'LONG';
    
    if (liquidationPrice > 0) {
      // 鍋氬锛氭鎹熶环鏍煎繀椤诲ぇ浜庡己骞充环鏍?
      if (isLong && newVal <= liquidationPrice) {
        // 鑷姩淇涓哄己骞充环 + 0.5%
        newVal = liquidationPrice * 1.005;
      }
      // 鍋氱┖锛氭鎹熶环鏍煎繀椤诲皬浜庡己骞充环鏍?
      else if (!isLong && newVal >= liquidationPrice) {
        // 鑷姩淇涓哄己骞充环 - 0.5%
        newVal = liquidationPrice * 0.995;
      }
    }
  }
  
  // 鏍规嵁姝ラ暱澧炲噺锛屼繚鐣?浣嶅皬鏁?
  tpSlForm.value[field] = newVal.toFixed(2);
};

const setTPSLPercentage = (field, percent) => {
  // 鍩轰簬鏍囪浠锋牸蹇€熻缃櫨鍒嗘瘮鍋忕Щ
  const basePrice = markPrice.value;
  let calculatedPrice;
  
  if (field === 'takeProfitPrice') {
    calculatedPrice = basePrice * (1 + percent);
  } else {
    // 姝㈡崯浠锋牸锛氶渶瑕侀獙璇佹槸鍚﹁Е鍙婂己骞崇嚎
    calculatedPrice = basePrice * (1 - percent);
    
    // 濡傛灉鏈夋寔浠撲俊鎭紝妫€鏌ユ槸鍚﹁Е鍙婂己骞充环鏍?
    if (currentTPSLPosition.value?.position) {
      const position = currentTPSLPosition.value.position;
      const liquidationPrice = position.liquidationPrice;
      const isLong = position.side === 'long' || position.side === 'LONG';
      
      if (liquidationPrice > 0) {
        // 鍋氬锛氭鎹熶环鏍煎繀椤诲ぇ浜庡己骞充环鏍?
        if (isLong && calculatedPrice <= liquidationPrice) {
          // 鑷姩淇涓哄己骞充环 + 0.5%锛堢粰缂撳啿绌洪棿锛?
          calculatedPrice = liquidationPrice * 1.005;
        }
        // 鍋氱┖锛氭鎹熶环鏍煎繀椤诲皬浜庡己骞充环鏍?
        else if (!isLong && calculatedPrice >= liquidationPrice) {
          // 鑷姩淇涓哄己骞充环 - 0.5%锛堢粰缂撳啿绌洪棿锛?
          calculatedPrice = liquidationPrice * 0.995;
        }
      }
    }
  }
  
  tpSlForm.value[field] = calculatedPrice.toFixed(2);
};

// 楠岃瘉姝㈡崯浠锋牸鏄惁鍚堢悊
const validateStopLossPrice = () => {
  if (!currentTPSLPosition.value?.position) {
    return null; // 娌℃湁鎸佷粨淇℃伅锛屾棤娉曢獙璇?
  }
  
  const position = currentTPSLPosition.value.position;
  const liquidationPrice = position.liquidationPrice;
  const stopLossPrice = parseFloat(tpSlForm.value.stopLossPrice);
  
  if (!stopLossPrice || !liquidationPrice || liquidationPrice <= 0) {
    return null; // 娌℃湁杈撳叆鎴栨病鏈夊己骞充环鏍硷紝鏃犳硶楠岃瘉
  }
  
  const isLong = position.side === 'long' || position.side === 'LONG';
  
  // 鍋氬锛氭鎹熶环鏍煎繀椤诲ぇ浜庡己骞充环鏍?
  if (isLong && stopLossPrice <= liquidationPrice) {
    return t('trade.stop_loss_above_liquidation', { price: formatPrice(liquidationPrice) }) || 
           `姝㈡崯浠锋牸蹇呴』澶т簬寮哄钩浠锋牸 (寮哄钩浠? ${formatPrice(liquidationPrice)})`;
  }
  
  // 鍋氱┖锛氭鎹熶环鏍煎繀椤诲皬浜庡己骞充环鏍?
  if (!isLong && stopLossPrice >= liquidationPrice) {
    return t('trade.stop_loss_below_liquidation', { price: formatPrice(liquidationPrice) }) || 
           `姝㈡崯浠锋牸蹇呴』灏忎簬寮哄钩浠锋牸 (寮哄钩浠? ${formatPrice(liquidationPrice)})`;
  }
  
  return null; // 楠岃瘉閫氳繃
};

// 璁＄畻灞炴€э細姝㈡崯浠锋牸閿欒淇℃伅
const stopLossPriceError = computed(() => {
  return validateStopLossPrice();
});

// 璁＄畻灞炴€э細琛ㄥ崟鏄惁鏈夋晥
const isTPSLFormValid = computed(() => {
  // 鑷冲皯濉啓涓€涓环鏍?
  if (!tpSlForm.value.takeProfitPrice && !tpSlForm.value.stopLossPrice) {
    return false;
  }
  
  // 濡傛灉濉啓浜嗘鎹熶环鏍硷紝蹇呴』閫氳繃楠岃瘉
  if (tpSlForm.value.stopLossPrice && stopLossPriceError.value) {
    return false;
  }
  
  return true;
});

// 妫€鏌ユ鎹熺櫨鍒嗘瘮鎸夐挳鏄惁搴旇绂佺敤
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
  
  // 鍋氬锛氬鏋滆绠楀嚭鐨勪环鏍?<= 寮哄钩浠锋牸锛岀鐢?
  if (isLong && calculatedPrice <= liquidationPrice) {
    return true;
  }
  
  // 鍋氱┖锛氬鏋滆绠楀嚭鐨勪环鏍?>= 寮哄钩浠锋牸锛岀鐢?
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
        
        // 鍒锋柊鎸佷粨鍒楄〃鍜岃祫浜т綑棰?
        await fetchFuturesPositions();
        await assetStore.initData();
        
        // 鍒锋柊褰撳墠濮旀墭璁㈠崟鍒楄〃锛堝悎绾︼級
        console.log('骞充粨鎴愬姛锛屾鍦ㄥ己鍒跺埛鏂板悎绾﹀鎵樺垪琛?..');
        await fetchFuturesOrders();
        
        // 鍒锋柊鍘嗗彶鎴愪氦璁㈠崟鍒楄〃锛堝悎绾︼級
        console.log('[DEBUG] 骞充粨鎴愬姛锛屾鍦ㄥ埛鏂板巻鍙叉垚浜ゅ垪琛?..');
        await fetchFuturesHistory();
        
        console.log('[DEBUG] Close position succeeded; refreshed positions, assets, orders, and history.');
      } else {
        throw new Error(responseData?.message || t('trade.close_failed'));
      }
    } catch (error) {
      console.error('鉂?骞充粨澶辫触:', error);
      
      let errorMessage = t('trade.close_failed') || '骞充粨澶辫触锛岃閲嶈瘯';
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
    // 鐢ㄦ埛鍙栨秷
  }
};

// 鐩戝惉鏍囪浠锋牸鍙樺寲锛屾洿鏂版湭瀹炵幇鐩堜簭鍜岀洏鍙?
watch(markPrice, () => {
  updatePositionsPnl();
  
  // 浠呭湪娌℃湁鐪熷疄娣卞害鏁版嵁涓斿綋鍓嶈繕娌℃湁鏁版嵁鏃讹紝鎵嶇敓鎴愭ā鎷熸暟鎹綔涓哄～鍏?
  if (!asks.value.length || !bids.value.length) {
    generateOrderBook();
  }
}, { immediate: true });

// 浠?marketStore 鑾峰彇鏍囪浠锋牸
watch(() => marketStore.getTicker(symbol.value), (ticker) => {
  if (ticker) {
    markPrice.value = ticker.price || markPrice.value;
    priceChange.value = ticker.change || priceChange.value;
  }
}, { immediate: true });

// 鐩戝惉甯佺瀵瑰簲鐨勭湡瀹炴繁搴︽暟鎹彉鍖?
watch(() => marketStore.depths[symbol.value], (newDepth) => {
  if (newDepth && newDepth.asks && newDepth.bids) {
    // 鍙湁褰撴湁鐪熷疄鏁版嵁鏃舵墠瑕嗙洊锛屽惁鍒欎繚鐣欏師鏈夋暟鎹紙鎴栨ā鎷熸暟鎹級
    asks.value = [...newDepth.asks];
    bids.value = [...newDepth.bids];
  }
}, { immediate: true, deep: true });

const formatOrderTime = (timestamp) => {
  if (!timestamp) return '';
  // 鍚庣杩斿洖鐨勬槸绉掔骇鏃堕棿鎴筹紙Unix timestamp锛夛紝闇€瑕佽浆鎹负姣绾?
  // 濡傛灉鏃堕棿鎴冲皬浜?1e12锛岃鏄庢槸绉掔骇锛岄渶瑕佷箻浠?1000
  const timestampMs = timestamp < 1e12 ? timestamp * 1000 : timestamp;
  const date = new Date(timestampMs);
  
  // 妫€鏌ユ棩鏈熸槸鍚︽湁鏁?
  if (isNaN(date.getTime())) {
    console.warn(`[DEBUG] 鏃犳晥鐨勬椂闂存埑: ${timestamp}`);
    return '';
  }
  
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

const scrollToTop = () => { window.scrollTo({ top: 0, behavior: 'smooth' }); };

// 鑾峰彇褰撳墠濮旀墭璁㈠崟鍒楄〃锛堝悎绾﹁鍗曪級
// 鑾峰彇鐜拌揣褰撳墠濮旀墭璁㈠崟鍒楄〃
const fetchSpotOrders = async () => {
  try {
    const response = await getOrders({ status: 'NEW' });
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 杩囨护锛氬彧鏄剧ず鐘舵€佷负 NEW銆丳ENDING 鎴?OPEN 鐨勮鍗?
      const pendingOrders = responseData.data.filter(order => 
        order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
      );
      
      // 鏄犲皠鍚庣鏁版嵁鏍煎紡鍒板墠绔樉绀烘牸寮?
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
    console.error('鉂?鑾峰彇鐜拌揣璁㈠崟鍒楄〃澶辫触:', error);
    spotOrdersList.value = [];
  }
};

// 鑾峰彇鍚堢害褰撳墠濮旀墭璁㈠崟鍒楄〃
const fetchFuturesOrders = async () => {
  try {
    console.log('馃摛 [DEBUG] 寮€濮嬭幏鍙栧悎绾﹀鎵樿鍗?..');
    const response = await getFuturesOrders({ status: 'NEW' });
    const responseData = response.data || response;
    console.log('馃摜 [DEBUG] 鍚堢害濮旀墭璁㈠崟API杩斿洖:', responseData);
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 杩囨护锛氬彧鏄剧ず鐘舵€佷负 NEW銆丳ENDING 鎴?OPEN 鐨勮鍗?
      const pendingOrders = responseData.data.filter(order => 
        order.status === 'NEW' || order.status === 'PENDING' || order.status === 'OPEN'
      );
      
      // 鏄犲皠鍚庣鏁版嵁鏍煎紡鍒板墠绔樉绀烘牸寮?
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
      console.log('鉁?[DEBUG] 鍚堢害濮旀墭璁㈠崟鍒楄〃宸叉洿鏂帮紝鏁伴噺:', futuresOrdersList.value.length);
      console.log('鉁?[DEBUG] 鍚堢害濮旀墭璁㈠崟璇︽儏:', futuresOrdersList.value);
    } else {
      futuresOrdersList.value = [];
      console.log('鈿狅笍 [DEBUG] 鍚堢害濮旀墭璁㈠崟鍒楄〃涓虹┖');
    }
  } catch (error) {
    console.error('鉂?鑾峰彇鍚堢害璁㈠崟鍒楄〃澶辫触:', error);
    futuresOrdersList.value = [];
  }
};

// 鑾峰彇鍚堢害鍘嗗彶鎴愪氦璁㈠崟鍒楄〃锛堟敮鎸佸垎椤碉級
const fetchFuturesHistory = async (isRefresh = false) => {
  // 闃叉閲嶅鍔犺浇
  if (historyLoading.value) {
    return;
  }

  try {
    historyLoading.value = true;

    // 鍒锋柊鏃堕噸缃姸鎬?
    if (isRefresh) {
      futuresHistoryList.value = [];
      historyPage.value = 1;
      historyHasMore.value = true;
    }

    // 璁＄畻 skip锛堝亸绉婚噺锛?
    const skip = (historyPage.value - 1) * historyPageSize.value;

    console.log(`馃摛 [DEBUG] 鑾峰彇鍚堢害鍘嗗彶鎴愪氦璁㈠崟 - 椤电爜: ${historyPage.value}, skip: ${skip}, limit: ${historyPageSize.value}`);
    
    const response = await getFuturesOrders({ 
      status: 'HISTORY',
      skip: skip,
      limit: historyPageSize.value
    });
    const responseData = response.data || response;
    console.log('馃摜 [DEBUG] 鍚堢害鍘嗗彶鎴愪氦璁㈠崟API杩斿洖:', responseData);
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 鏄犲皠鍚庣鏁版嵁鏍煎紡鍒板墠绔樉绀烘牸寮?
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

      // 杩藉姞鏁版嵁锛堝埛鏂版椂鐩存帴鏇挎崲锛?
      if (isRefresh) {
        futuresHistoryList.value = newOrders;
      } else {
        futuresHistoryList.value = [...futuresHistoryList.value, ...newOrders];
      }

      // 鍒ゆ柇鏄惁杩樻湁鏇村鏁版嵁
      if (newOrders.length < historyPageSize.value) {
        historyHasMore.value = false;
        console.log('[DEBUG] All futures history loaded; no more records.');
      } else {
        historyPage.value += 1;  // 椤电爜鑷锛屽噯澶囧姞杞戒笅涓€椤?
      }

      console.log(`鉁?[DEBUG] 鍚堢害鍘嗗彶鎴愪氦璁㈠崟鍒楄〃宸叉洿鏂帮紝褰撳墠鎬绘暟: ${futuresHistoryList.value.length}, 鏈鍔犺浇: ${newOrders.length}`);
    } else {
      if (isRefresh) {
        futuresHistoryList.value = [];
      }
      historyHasMore.value = false;
      console.log('鈿狅笍 [DEBUG] 鍚堢害鍘嗗彶鎴愪氦璁㈠崟鍒楄〃涓虹┖');
    }
  } catch (error) {
    console.error('鉂?鑾峰彇鍚堢害鍘嗗彶鎴愪氦璁㈠崟澶辫触:', error);
    if (isRefresh) {
      futuresHistoryList.value = [];
    }
    historyHasMore.value = false;
  } finally {
    historyLoading.value = false;
  }
};

// 鍒濆鍖栧巻鍙茶褰曟粴鍔ㄧ洃鍚紙IntersectionObserver锛?
const initHistoryObserver = () => {
  // 1. 濡傛灉宸茬粡鏈変簡锛屽厛鏂紑锛岄槻姝㈤噸澶?
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }

  // 2. 鍒涘缓鏂扮殑瑙傚療鍣?
  historyObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      // 鏍稿績閫昏緫锛氬鏋滃簳閮ㄥ厓绱犲嚭鐜颁簡 + 杩樻湁鏇村鏁版嵁 + 娌″湪鍔犺浇涓?
      if (
        entry &&
        entry.isIntersecting &&
        historyHasMore.value &&
        !historyLoading.value
      ) {
        console.log('[DEBUG] 瑙﹀簳浜嗭紝鑷姩鍔犺浇涓嬩竴椤?..');
        fetchFuturesHistory(false); // false 浠ｈ〃涓嶆槸鍒锋柊锛岃€屾槸杩藉姞
      }
    },
    {
      root: null, // 浣跨敤瑙嗗彛浣滀负鏍?
      rootMargin: '0px', // 涓嶆墿灞曟牴杈硅窛
      threshold: 0.1 // 褰撶洰鏍囧厓绱?10% 鍙鏃惰Е鍙?
    }
  );

  // 3. 寮€濮嬭瀵熷簳閮ㄥ厓绱狅紙浣跨敤 nextTick 纭繚 DOM 宸叉覆鏌擄級
  nextTick(() => {
    if (loadMoreTrigger.value) {
      historyObserver.observe(loadMoreTrigger.value);
      console.log('[DEBUG] IntersectionObserver initialized for futures history.');
    } else {
      console.warn('[DEBUG] loadMoreTrigger 鏈壘鍒帮紝鏃犳硶鍒濆鍖?IntersectionObserver');
    }
  });
};

// 鑾峰彇鍚堢害鎸佷粨鍒楄〃
const fetchFuturesPositions = async () => {
  try {
    // 妫€鏌ラ挶鍖呮槸鍚﹁繛鎺?
    if (!assetStore.isWalletConnected) {
      positions.value = [];
      return;
    }
    
    const response = await getFuturesPositionsApi();
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200 && responseData.data) {
      // 鏄犲皠鍚庣鏁版嵁鏍煎紡鍒板墠绔樉绀烘牸寮忥紙鐩存帴浣跨敤鍚庣杩斿洖鐨?unrealized_pnl锛?
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
          unrealizedPnl: unrealizedPnl, // 鐩存帴浣跨敤鍚庣杩斿洖鐨勫€?
          unrealizedPnlPercent: unrealizedPnlPercent, // 鍩轰簬鍚庣 PnL 璁＄畻鐧惧垎姣?
          markPrice: pos.mark_price || markPrice.value
        };
      });
      
      console.log('鉁?鎸佷粨鏁版嵁锛堜娇鐢ㄥ悗绔?PnL锛?', positions.value);
      
      console.log('鉁?鑾峰彇鍚堢害鎸佷粨鎴愬姛:', positions.value);
    } else {
      positions.value = [];
      console.warn('鈿狅笍 鑾峰彇鍚堢害鎸佷粨澶辫触:', responseData);
    }
  } catch (error) {
    console.error('鉂?鑾峰彇鍚堢害鎸佷粨澶辫触:', error);
    positions.value = [];
  }
};

const handleSubmitOrder = async () => {
  // 绗竴姝ワ細琛ㄥ崟鏍￠獙
  const amountValue = parseFloat(amount.value);
  if (isNaN(amountValue) || amountValue <= 0) {
    showToast({ message: t('trade.amount_invalid'), icon: 'fail' });
    return;
  }
  
  if (!isOrderValid.value) {
    showToast({ message: t('trade.fill_all_fields'), duration: 2000 });
    return;
  }

  // 绗簩姝ワ細璁剧疆鍔犺浇鐘舵€?
  isLoading.value = true;

  try {
    // 绗笁姝ワ細鏋勯€犲彂閫佺粰鍚庣鐨勫弬鏁板璞?
    const orderPrice = orderType.value === 'market' ? lastPrice.value : parseFloat(price.value);
    
    const params = {
      symbol: `${symbol.value}/USDT`, // 纭繚鏍煎紡涓?"BTC/USDT"
      side: orderSide.value.toUpperCase(), // 杞崲涓哄ぇ鍐欙細'BUY' 鎴?'SELL'
      type: orderType.value.toUpperCase(), // 杞崲涓哄ぇ鍐欙細'LIMIT' 鎴?'MARKET'
      price: orderType.value === 'market' ? orderPrice : parseFloat(price.value), // 甯備环鍗曚紶褰撳墠甯傚満浠凤紝闄愪环鍗曚紶鐢ㄦ埛杈撳叆鐨勪环鏍?
      amount: parseFloat(amount.value),
      use_beat_discount: false // 鏆傛椂涓嶄娇鐢?BEAT 鎶樻墸
    };

    console.log('馃摛 鍙戦€佷笅鍗曡姹?', params);

    // 绗洓姝ワ細璋冪敤鍚庣 API
    const response = await createOrder(params);
    

    // 绗簲姝ワ細鎴愬姛澶勭悊
    // 娉ㄦ剰锛歛xios 杩斿洖鐨勬槸 response 瀵硅薄锛屽悗绔暟鎹湪 response.data 涓?
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      // 鏄剧ず鎴愬姛鎻愮ず
      showToast({
        message: orderType.value === 'market' 
          ? t('trade.market_order_submitted') 
          : t('trade.limit_order_submitted'),
        icon: 'success',
        duration: 2000
      });

      // 鍏抽敭锛氬埛鏂扮敤鎴疯祫浜т綑棰?
      await assetStore.initData();
      
      // 鍒锋柊褰撳墠濮旀墭璁㈠崟鍒楄〃锛堢幇璐э級
      await fetchSpotOrders();

      // 娓呯┖杈撳叆妗?
      if (orderType.value === 'limit') {
        price.value = '';
      }
      amount.value = '';
      selectedPercent.value = null;
      spotSliderValue.value = 0; // 閲嶇疆婊戝潡

      console.log('[DEBUG] Spot order submitted; refreshed assets and orders.');
    } else {
      throw new Error(responseData?.message || t('trade.order_failed'));
    }
  } catch (error) {
    // 绗叚姝ワ細澶辫触澶勭悊
    console.error('鉂?涓嬪崟澶辫触:', error);
    
    let errorMessage = t('trade.order_failed') || '璁㈠崟鎻愪氦澶辫触锛岃閲嶈瘯';
    
    // 灏濊瘯浠庨敊璇搷搴斾腑鎻愬彇閿欒淇℃伅
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
    // 绗竷姝ワ細閲嶇疆鍔犺浇鐘舵€?
    isLoading.value = false;
  }
};

const cancelOrder = async (orderId) => {
  // 鏍规嵁褰撳墠 Tab 纭畾璁㈠崟绫诲瀷
  const isSpot = activeTradeTab.value === 'spot';
  
  // 浠庡搴旂殑璁㈠崟鍒楄〃涓煡鎵捐鍗?
  const orderList = isSpot ? spotOrdersList.value : futuresOrdersList.value;
  const order = orderList.find(o => o.order_id === orderId);
  
  if (!order || !order.order_id) {
    showToast({ message: t('trade.order_not_found'), icon: 'fail' });
    return;
  }

  try {
    // 鏍规嵁褰撳墠 Tab 璋冪敤瀵瑰簲鐨勬挙鍗曟帴鍙?
    let response;
    if (isSpot) {
      // 鐜拌揣鎾ゅ崟
      response = await cancelSpotOrderApi(order.order_id);
    } else {
      // 鍚堢害鎾ゅ崟
      response = await cancelFuturesOrderApi(order.order_id);
    }
    
    const responseData = response.data || response;
    
    if (responseData && responseData.code === 200) {
      showToast({ 
        message: t('trade.order_cancelled'), 
        icon: 'success',
        duration: 2000 
      });
      
      // 鍒锋柊璁㈠崟鍒楄〃鍜岃祫浜т綑棰?
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
    console.error('鉂?鎾ら攢璁㈠崟澶辫触:', error);
    
    let errorMessage = t('trade.cancel_failed') || '鎾ら攢璁㈠崟澶辫触锛岃閲嶈瘯';
    
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
  // 1. 鏇存柊 symbol
  symbol.value = newSymbol;
  
  // 2. 鍏抽棴甯佺閫夋嫨寮圭獥
  showCoinSelect.value = false;
  
  // 3. 娓呯┖ amount 杈撳叆妗?
  amount.value = '';
  
  // 4. 閲嶇疆鐧惧垎姣旀寜閽姸鎬佸拰婊戝潡鍊?
  selectedPercent.value = null;
  spotSliderValue.value = 0;
  
  // 5. 鏇存柊浠锋牸涓烘柊甯佺鐨勫綋鍓嶅競浠?
  updatePriceForSymbol(newSymbol);
  
  // 6. 鏇存柊 URL 鍙傛暟锛堜娇鐢?replace 閬垮厤浜х敓鍘嗗彶璁板綍锛?
  router.replace({ 
    path: '/trade', 
    query: { 
      symbol: newSymbol, 
      side: orderSide.value 
    } 
  });
  
  // 7. 鏄剧ず鍒囨崲鎴愬姛鎻愮ず
  showToast({ 
    message: t('trade.switched_to', { symbol: `${newSymbol}/USDT` }), 
    duration: 1500 
  });
};

// 鍒濆鍖栧嚱鏁?
const initializeTrade = async () => {
  generateOrderBook();
  // 棣栨杩涘叆涔熷垵濮嬪寲浠锋牸
  updatePriceForSymbol(symbol.value);
  
  // 纭繚 WebSocket 杩炴帴锛堢敤浜庡悎绾︿氦鏄撶殑鏍囪浠锋牸锛?
  marketStore.ensureConnection();
  
  // 妫€鏌ラ挶鍖呰繛鎺ョ姸鎬?
  if (assetStore.isWalletConnected) {
    // 鏍规嵁褰撳墠 Tab 鑾峰彇瀵瑰簲鐨勮鍗曞垪琛?
    if (activeTradeTab.value === 'spot') {
      await fetchSpotOrders();
    } else {
      await fetchFuturesOrders();
      await fetchFuturesPositions();
    }
  }
};

// 鐩戝惉 Tab 鍒囨崲锛屽姞杞藉搴旂殑鏁版嵁锛坕mmediate: true 纭繚鍒濆鍖栨椂涔熸墽琛岋級
watch(activeTradeTab, async (newTab) => {
  if (assetStore.isWalletConnected) {
    if (newTab === 'futures') {
      // 鍒囨崲鍒板悎绾?Tab锛岃幏鍙栨寔浠撳垪琛ㄥ拰璁㈠崟鍒楄〃
      console.log('馃摛 [DEBUG] watch activeTradeTab: 鍒囨崲鍒板悎绾?Tab锛屽埛鏂拌鍗曞垪琛?..');
      await fetchFuturesPositions();
      await fetchFuturesOrders();
      await fetchFuturesHistory();
      // 鍚姩瀹氭椂鍒锋柊
      startPositionsRefresh();
    } else if (newTab === 'spot') {
      // 鍒囨崲鍒扮幇璐?Tab锛岃幏鍙栬鍗曞垪琛?
      console.log('馃摛 [DEBUG] watch activeTradeTab: 鍒囨崲鍒扮幇璐?Tab锛屽埛鏂拌鍗曞垪琛?..');
      await fetchSpotOrders();
      // 鍋滄瀹氭椂鍒锋柊锛堢幇璐т笉闇€瑕侊級
      stopPositionsRefresh();
    }
  }
}, { immediate: true });

// 鐩戝惉 forceTradeTab prop 鍙樺寲锛堝瓙椤甸潰妯″紡锛?
watch(() => props.forceTradeTab, (newTab) => {
  if (props.isSubPage && newTab && newTab !== activeTradeTab.value) {
    console.log(`馃摛 [DEBUG] forceTradeTab changed: ${activeTradeTab.value} -> ${newTab}`);
    activeTradeTab.value = newTab;
  }
}, { immediate: true });

// 瀛愰〉闈㈡ā寮忎笅锛岀姝㈡墜鍔ㄥ垏鎹㈡爣绛鹃〉锛堥槻姝㈢敤鎴烽€氳繃鍏朵粬鏂瑰紡鍒囨崲锛?
watch(activeTradeTab, (newTab, oldTab) => {
  if (props.isSubPage && props.forceTradeTab && newTab !== props.forceTradeTab) {
    // 濡傛灉瀛愰〉闈㈡ā寮忎笅鏈?forceTradeTab锛屼絾 activeTradeTab 琚慨鏀逛簡锛屾仮澶嶄负 forceTradeTab
    console.warn(`鈿狅笍 [WARN] 瀛愰〉闈㈡ā寮忎笅 activeTradeTab 琚慨鏀逛负 ${newTab}锛屽凡鎭㈠涓?${props.forceTradeTab}`);
    activeTradeTab.value = props.forceTradeTab;
  }
});

// 鐩戝惉鎸佷粨Tab鍒囨崲锛屽姞杞藉搴旂殑鏁版嵁
watch(activePositionTab, async (newTab) => {
  if (assetStore.isWalletConnected && activeTradeTab.value === 'futures') {
    if (newTab === 0) {
      // Tab 0: 鎸佷粨鍒楄〃
      await fetchFuturesPositions();
    } else if (newTab === 1) {
      // Tab 1: 褰撳墠濮旀墭
      await fetchFuturesOrders();
    } else if (newTab === 2) {
      // Tab 2: 鍘嗗彶鎴愪氦
      console.log('[DEBUG] 鍒囨崲鍒板巻鍙叉垚浜ab锛屾鍦ㄥ埛鏂板巻鍙叉垚浜ゅ垪琛?..');
      await fetchFuturesHistory(true);  // 鍒锋柊妯″紡
      // 鍒濆鍖?IntersectionObserver锛堝湪 nextTick 涓‘淇?DOM 宸叉覆鏌擄級
      await nextTick();
      initHistoryObserver();
    }
  }
});

// 瀹氭椂鍒锋柊鎸佷粨鏁版嵁鐨勫畾鏃跺櫒
let positionsRefreshTimer = null;

// 鍚姩瀹氭椂鍒锋柊鎸佷粨鏁版嵁
const startPositionsRefresh = () => {
  // 娓呴櫎鏃х殑瀹氭椂鍣紙濡傛灉瀛樺湪锛?
  stopPositionsRefresh();
  
  // 鍙湪鍚堢害 Tab 涓旈挶鍖呭凡杩炴帴鏃跺埛鏂?
  if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
    positionsRefreshTimer = setInterval(async () => {
      try {
        await fetchFuturesPositions();
        // 鍚屾椂鍒锋柊璧勪骇鏁版嵁锛堝寘鍚湭瀹炵幇鐩堜簭锛?
        await assetStore.initData();
      } catch (error) {
        console.error('鉂?瀹氭椂鍒锋柊鎸佷粨澶辫触:', error);
      }
    }, 5000); // 姣?绉掑埛鏂颁竴娆?
  }
};

// 鍋滄瀹氭椂鍒锋柊
const stopPositionsRefresh = () => {
  if (positionsRefreshTimer) {
    clearInterval(positionsRefreshTimer);
    positionsRefreshTimer = null;
  }
};

onMounted(async () => {
  // DEBUG MODE: 鏇存柊灞忓箷楂樺害
  updateScreenHeight();
  window.addEventListener('resize', updateScreenHeight);
  
  // 璋冭瘯杈撳嚭锛氱‘璁ゅ綋鍓嶆ā寮?
  console.log('[TradePanel] Current Mode:', isSpotMode.value ? 'Spot' : 'Futures');
  console.log('[TradePanel] isSpot (DEBUG):', isSpot.value ? 'Spot' : 'Futures');
  console.log('[TradePanel] activeTradeTab:', activeTradeTab.value);
  console.log('[TradePanel] props:', {
    isSubPage: props.isSubPage,
    initialMode: props.initialMode,
    forceTradeTab: props.forceTradeTab,
    initialSymbol: props.initialSymbol
  });
  await initializeTrade();
  
  // 瀛愰〉闈㈡ā寮忎笅锛屾牴鎹?forceTradeTab 鍔犺浇瀵瑰簲鏁版嵁
  if (props.isSubPage) {
    if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
      console.log('馃摛 [DEBUG] onMounted (瀛愰〉闈?鍚堢害妯″紡): 鍔犺浇鍚堢害鏁版嵁...');
      await fetchFuturesPositions();
      await fetchFuturesOrders();
      await fetchFuturesHistory();
      startPositionsRefresh();
    } else if (activeTradeTab.value === 'spot' && assetStore.isWalletConnected) {
      console.log('馃摛 [DEBUG] onMounted (瀛愰〉闈?鐜拌揣妯″紡): 鍔犺浇鐜拌揣鏁版嵁...');
      await fetchSpotOrders();
    }
  } else {
    // 涓婚〉闈㈡ā寮忎笅锛岀‘淇濆悎绾?Tab 涔熷姞杞借鍗曞垪琛紙濡傛灉褰撳墠鍦ㄥ悎绾?Tab锛?
    if (activeTradeTab.value === 'futures' && assetStore.isWalletConnected) {
      console.log('馃摛 [DEBUG] onMounted: 褰撳墠鍦ㄥ悎绾?Tab锛屽己鍒跺埛鏂板悎绾﹁鍗曞垪琛?..');
      await fetchFuturesOrders();
    }
  // 鍚姩瀹氭椂鍒锋柊鎸佷粨鏁版嵁锛堟瘡5绉掞級
  startPositionsRefresh();
  }
  
  // 鍒濆鍖栫洏鍙ｅ姩鎬佽鏁拌绠?
  initOrderBookResizeObserver();

  // 鐩戝惉绐楀彛澶у皬鍙樺寲
  window.addEventListener('resize', handleResize);

  // 濡傛灉褰撳墠鍦ㄥ巻鍙叉垚浜ab锛屽垵濮嬪寲 IntersectionObserver锛堝湪 nextTick 涓‘淇?DOM 宸叉覆鏌擄級
  if (activePositionTab.value === 2) {
    await nextTick();
    initHistoryObserver();
  }
});

// Keep-alive 婵€娲绘椂
onActivated(() => {
  initializeTrade();
  
  // 閲嶆柊鍚姩瀹氭椂鍒锋柊锛堥槻姝㈤〉闈㈠垏鎹㈡椂瀹氭椂鍣ㄨ娓呴櫎锛?
  startPositionsRefresh();
  
  // 閲嶆柊鍒濆鍖栫洏鍙ｅ姩鎬佽鏁拌绠?
  initOrderBookResizeObserver();
});

// Keep-alive 鍋滅敤鏃?
onDeactivated(() => {
  // 缁勪欢澶辨椿鏃舵竻闄ゅ畾鏃跺櫒
  stopPositionsRefresh();
  
  // 娓呯悊 IntersectionObserver
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
});

// 缁勪欢鍗歌浇鏃?
onUnmounted(() => {
  // DEBUG MODE: 娓呯悊灞忓箷楂樺害鐩戝惉
  window.removeEventListener('resize', updateScreenHeight);
  
  // 娓呯悊 IntersectionObserver
  if (historyObserver) {
    historyObserver.disconnect();
    historyObserver = null;
  }
  // 缁勪欢鍗歌浇鏃舵竻闄ゅ畾鏃跺櫒
  stopPositionsRefresh();
  
  // 娓呯悊 ResizeObserver
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* ========== 鍏ㄥ眬瀹瑰櫒 - Fixed Inset-0 鏋舵瀯 ========== */
.trade-page {
  position: fixed;
  inset: 0; /* top: 0, right: 0, bottom: 0, left: 0 */
  background-color: var(--color-bg); /* 鏈€娣遍粦 */
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
  z-index: 0;
  overflow: hidden; /* 闃叉鏁翠綋椤甸潰婊氬姩 */
}

/* 鍙粴鍔ㄥ唴瀹瑰尯鍩?- Safe Padding Strategy */
.trade-scrollable-content {
  flex: 1;
  overflow-y: auto; /* 鍐呭鍖哄煙鍙粴鍔?*/
  overflow-x: hidden;
  padding-bottom: 128px; /* pb-32 = 128px锛岄槻姝㈠唴瀹硅搴曢儴鍏ㄥ眬瀵艰埅鏍忛伄鎸?*/
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

/* ========== 椤堕儴瀵艰埅鏍?========== */
.trade-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px; /* h-12 = 48px */
  padding: 0 16px;
  background-color: var(--color-bg-card); /* bg-gray-900 */
  flex-shrink: 0; /* 闃叉琚帇缂?*/
  z-index: 20;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.header-center {
  flex: 1; /* 鍗犳嵁宸︿晶绌洪棿 */
  display: flex;
  align-items: center;
  justify-content: flex-start; /* 鏍囬闈犲乏瀵归綈 */
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
  justify-content: flex-end; /* 鍥炬爣闈犲彸 */
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

/* ========== 鏍囩鏍忥細鐜拌揣/鏉犳潌 ========== */
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

/* ========== 浜ゆ槗瀵逛俊鎭?========== */
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

/* ========== 浜ゆ槗闈㈡澘瀹瑰櫒 - 鏍囧噯 Flex 甯冨眬 ========== */
.trade-panel-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  position: relative; /* 浣跨敤 relative锛岀姝?absolute */
  /* 绉婚櫎 min-height 鍜?height: 100%锛岃鍐呭鑷劧楂樺害 */
}

/* ========== 鏍稿績浜ゆ槗鍖?- 缁熶竴甯冨眬缁撴瀯锛氬乏鍙冲悇鍗?50% ========== */
.trade-main, .futures-trade-main {
  display: flex !important;
  flex-direction: row !important;
  gap: 8px;
  padding: 8px;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
  flex-wrap: nowrap; /* 闃叉鎹㈣ */
  position: relative; /* 浣跨敤 relative锛岀姝?absolute */
}

/* ========== 宸︿晶锛氱洏鍙ｅ尯 (50%) - 浣跨敤 flex: 1 鑷劧鍒嗛厤 ========== */
.orderbook-side, 
.futures-orderbook-side,
.left-panel {
  flex: 1 !important; /* 宸﹀彸鍚勫崰 50% */
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, var(--color-bg) 100%);
  border-radius: 8px;
  overflow: visible;
  padding: 0;
  align-self: flex-start;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.08);
  box-shadow: 0 0 20px rgb(var(--color-shadow-rgb) / 0.5);
  position: relative; /* 浣跨敤 relative锛岀姝?absolute */
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
  margin-top: 0; /* 纭繚椤堕儴瀵归綈 */
}

.header-price { flex: 1; text-align: left; }
.header-quantity { flex: 1; text-align: right; }

.asks-list, .bids-list {
  display: flex;
  flex-direction: column;
  /* 绉婚櫎 overflow: hidden锛屽厑璁歌嚜鐒舵樉绀烘墍鏈夎 */
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

/* 璧涘崥鏈嬪厠绾㈣壊娓愬彉 - 鍗栧崟 */
.ask-depth { 
  background: linear-gradient(to left, 
    rgb(var(--color-loss-rgb) / 0.25) 0%, 
    rgb(var(--color-loss-rgb) / 0.15) 50%,
    rgb(var(--color-loss-rgb) / 0.05) 100%
  );
  box-shadow: inset -2px 0 8px rgb(var(--color-loss-rgb) / 0.2);
}

/* 璧涘崥鏈嬪厠缁胯壊娓愬彉 - 涔板崟 */
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

/* ========== 鍙充晶锛氫氦鏄撹〃鍗?(50%) - 浣跨敤 flex: 1 鑷劧鍒嗛厤 ========== */
.form-side,
.futures-form-side,
.right-panel {
  flex: 1 !important; /* 宸﹀彸鍚勫崰 50% */
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-sizing: border-box;
  position: relative; /* 浣跨敤 relative锛岀姝?absolute */
}

/* 鐜拌揣鍜屽悎绾︽ā寮忓鍣?- 纭繚瀹屽叏闅旂锛屼娇鐢?flex-col 鑷劧鎺掑垪 */
.spot-mode-container,
.futures-mode-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  position: relative; /* 浣跨敤 relative锛岀姝?absolute */
  /* 绉婚櫎浠讳綍鍙兘瀵艰嚧閲嶅彔鐨勬牱寮忥紝璁╁厓绱犺嚜鐒舵帓鍒?*/
}

.buy-sell-toggle {
  display: flex;
  gap: 0;
  background: rgb(var(--color-border-rgb) / 0.03);
  border-radius: 8px;
  padding: 3px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  position: relative;
  margin-top: 0; /* 纭繚椤堕儴瀵归綈锛屼笌 orderbook-header 瀵归綈 */
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
  margin-top: 0; /* 纭繚椤堕儴瀵归綈锛屼笌 orderbook-header 瀵归綈 */
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
    inset 0 0 30px rgb(var(--color-brand-rgb) / 0.08); /* 鍐呭彂鍏夋晥鏋?*/
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

/* 杈撳叆妗嗗崟浣嶆爣绛撅紙鍚庣紑锛?*/
.input-suffix {
  font-size: 13px;
  color: var(--color-accent); /* text-yellow-500 / Gold */
  font-weight: 600;
  white-space: nowrap;
  margin-left: 4px;
  opacity: 0.8;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
}

/* 淇3锛氶殣钘忔暟瀛楄緭鍏ユ榛樿鐨勪笂涓嬬澶?*/
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

/* 婊戝潡瀹瑰櫒鏍峰紡 - 榛戦噾瀹氬埗 */
.slider-wrapper {
  padding: 16px 8px;
  margin-bottom: 16px;
  position: relative;
}

/* 鍒诲害鏍囩鏍?- 浜や簰寮忚妭鐐?*/
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

/* 鑷畾涔夋粦鍧楁寜閽牱寮?- 鍙戝厜閽荤煶 */
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

/* Vant Slider 鑷畾涔夋牱寮?*/
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

/* 淇濈暀鏃ф牱寮忎互鍏煎锛堝鏋滃叾浠栧湴鏂硅繕鍦ㄤ娇鐢級 */
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

/* 鍙敤浣欓琛?- 绉诲埌鎸夐挳涓婃柟锛屾洿鏄撹 */
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
  text-shadow: 0 0 8px rgb(var(--color-brand-rgb) / 0.3); /* 杞诲井閲戣壊鍙戝厜 */
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

/* ========== 搴曢儴锛氬鎵樹笌璧勪骇 - 鑷劧娴佸紡甯冨眬 ========== */
.bottom-section { 
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  box-shadow: 0 -4px 20px rgb(var(--color-shadow-rgb) / 0.5);
  display: flex;
  flex-direction: column;
  margin-top: 8px; /* mt-2 = 8px锛屼笌浜ゆ槗琛ㄥ崟鐨勯棿璺?*/
  padding: 0 8px; /* px-2 = 8px */
  /* 浣跨敤鑷劧娴佸紡甯冨眬锛屼笉闄愬埗楂樺害 */
}

.bottom-tabs { 
  display: flex; 
  padding: 8px 16px; 
  gap: 32px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  flex-shrink: 0; /* 闃叉琚帇缂?*/
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
  /* 绉婚櫎鍥哄畾楂樺害鍜?overflow锛屼娇鐢ㄨ嚜鐒舵祦寮忓竷灞€ */
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
  min-height: 60px; /* 纭繚鏈夋渶灏忛珮搴?*/
  width: 100%;
  overflow: visible; /* 纭繚鍐呭鍙 */
}

/* ========== 绱у噾璁㈠崟鍒楄〃 - 鍥哄畾楂樺害婊氬姩 ========== */
.orders-list-compact { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
  min-height: 60px; /* 纭繚鏈夋渶灏忛珮搴?*/
  max-height: 200px; /* 澧炲姞鏈€澶ч珮搴︼紝鏄剧ず鏇村璁㈠崟 */
  overflow-y: auto; /* 鍐呴儴婊氬姩 */
  overflow-x: hidden;
  padding: 4px 4px 4px 0; /* 涓烘粴鍔ㄦ潯鐣欏嚭绌洪棿 */
  scrollbar-width: none; /* Firefox 闅愯棌婊氬姩鏉?*/
  -ms-overflow-style: none; /* IE/Edge 闅愯棌婊氬姩鏉?*/
}

.orders-list-compact::-webkit-scrollbar {
  display: none; /* Chrome/Safari 闅愯棌婊氬姩鏉?*/
}

.orders-empty-compact {
  display: flex; 
  align-items: center; 
  justify-content: center;
  height: 60px; /* 绱у噾鐨勭┖鐘舵€侀珮搴?*/
  padding: 0;
}

.empty-text-compact {
  font-size: 12px; 
  color: var(--color-text-secondary); 
  font-weight: 500;
}

/* 绱у噾绌虹姸鎬佹牱寮忓凡鍦ㄤ笂闈㈠畾涔?*/

.order-item {
  display: flex; 
  align-items: center; 
  padding: 10px 12px; /* 鍑忓皯鍐呰竟璺濓紝鏇寸揣鍑?*/
  background: rgb(var(--color-border-rgb) / 0.02);
  backdrop-filter: blur(10px);
  border-radius: 8px; /* 鏇村皬鐨勫渾瑙?*/
  border: 1px solid rgb(var(--color-brand-rgb) / 0.1); 
  transition: all 0.2s ease;
  flex-shrink: 0; /* 闃叉鍘嬬缉 */
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
  min-width: 100px; /* 绋嶅井鍑忓皬 */
}

.order-side-badge { 
  padding: 3px 6px; /* 鏇寸揣鍑?*/
  border-radius: 4px; 
  font-size: 10px; /* 鏇村皬瀛椾綋 */
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

/* 寮哄钩璁㈠崟鏍囩鏍峰紡 - 閱掔洰鐨勭孩鑹叉爣绛?*/
.liquidation-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background-color: rgb(var(--color-loss-rgb) / 0.2); /* bg-red-500/20 - 娴呯孩鑹茶儗鏅?*/
  color: var(--color-loss); /* text-red-500 - 椴滆壋鐨勭孩鑹?*/
  border: 1px solid rgb(var(--color-loss-rgb) / 0.3); /* 缁嗙孩绾胯竟妗?*/
  box-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.2);
}

/* 寮哄钩璁㈠崟鏁翠綋鏍峰紡 */
.order-item.liquidation-order {
  border-left: 3px solid var(--color-loss); /* 宸︿晶绾㈣壊杈规鏍囪瘑 */
  background-color: rgb(var(--color-loss-rgb) / 0.05); /* 杞诲井绾㈣壊鑳屾櫙 */
}

/* 寮哄钩璁㈠崟鐨勫凡瀹炵幇鐩堜簭鏍峰紡 - 宸ㄩ璐熸暟绾㈣壊鍔犵矖 */
.order-pnl.pnl-liquidation {
  font-weight: 900;
  font-size: 14px;
  color: var(--color-loss) !important; /* 寮哄埗绾㈣壊 */
  text-shadow: 0 0 8px rgb(var(--color-loss-rgb) / 0.5);
}

.order-pnl.pnl-liquidation.pnl-negative {
  color: var(--color-loss) !important; /* text-red-600 - 鏇存繁鐨勭孩鑹?*/
  font-weight: 900;
  text-shadow: 
    0 0 10px rgb(var(--color-loss-rgb) / 0.6),
    0 0 20px rgb(var(--color-loss-rgb) / 0.3);
}

.order-symbol-time { 
  display: flex; 
  flex-direction: column; 
  gap: 2px; /* 鏇寸揣鍑?*/
}

.order-symbol { 
  font-size: 12px; /* 鏇村皬 */
  font-weight: 700; 
  color: var(--color-text-primary); 
}

.order-time { 
  font-size: 10px; /* 鏇村皬 */
  color: var(--color-text-secondary); 
  font-family: 'DIN Alternate', monospace; 
}

.order-center { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  gap: 2px; /* 鏇寸揣鍑?*/
  padding: 0 10px; 
  min-width: 0; 
}

.order-price { 
  font-size: 13px; /* 鏇村皬 */
  font-weight: 700; 
  color: var(--color-text-primary); 
  font-family: 'DIN Alternate', monospace; 
}

.order-quantity { 
  font-size: 11px; /* 鏇村皬 */
  color: var(--color-text-secondary); 
  font-family: 'DIN Alternate', monospace; 
}

.order-right { 
  flex: 0 0 auto;
}

/* ========== 鍘嗗彶鎴愪氦鍒楄〃 Pro Max 甯冨眬 ========== */
.history-order-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 16px;
  gap: 16px;
}

/* 宸︿晶锛氭搷浣滆鎯?*/
.history-order-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0; /* 鍏佽鏀剁缉 */
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

/* 鍙充晶锛氭牳蹇冪粨鏋滐紙鐩堜簭 + 鏃堕棿锛?*/
.history-order-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-start;
  gap: 4px;
  flex-shrink: 0;
  min-width: 120px; /* 纭繚鏈夎冻澶熺┖闂存樉绀虹泩浜?*/
}

.history-order-pnl {
  font-size: 16px; /* text-base - 澶у瓧鍙?*/
  font-weight: 800; /* font-bold - 鍔犵矖 */
  font-variant-numeric: tabular-nums;
  font-family: 'Roboto Mono', 'DIN Alternate', monospace;
  text-align: right;
  line-height: 1.2;
}

.history-order-pnl.pnl-positive {
  color: var(--color-earn); /* 姝ｆ暟缁胯壊 */
}

.history-order-pnl.pnl-negative {
  color: var(--color-loss); /* 璐熸暟绾㈣壊 */
}

.history-order-pnl.pnl-zero {
  color: var(--color-text-secondary); /* 0 鏄剧ず鐏拌壊 */
  font-weight: 600;
}

.history-order-pnl.pnl-liquidation {
  color: var(--color-loss) !important;
  font-weight: 900;
  font-size: 17px; /* 寮哄钩璁㈠崟鏇村ぇ瀛楀彿 */
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

/* IntersectionObserver 鐩戝惉鐩爣锛堣Е搴曢敋鐐癸級 */
.history-observer-target {
  height: 1px;
  width: 100%;
  flex-shrink: 0;
}

/* 搴曢儴鐘舵€佹爮 */
.history-footer {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

/* 鍔犺浇涓姸鎬?*/
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

/* 娌℃湁鏇村鏁版嵁鐘舵€?*/
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
  padding: 5px 12px; /* 鏇寸揣鍑?*/
  background: rgb(var(--color-loss-rgb) / 0.1); 
  color: var(--color-loss); 
  border: 1px solid rgb(var(--color-loss-rgb) / 0.2); 
  border-radius: 6px; 
  font-size: 11px; /* 鏇村皬 */
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

/* ========== 璧勪骇鐜荤拑鎷熸€佸崱鐗?========== */
.assets-glass-card {
  background: rgb(var(--color-border-rgb) / 0.05); /* bg-white/5 */
  border-radius: 12px; /* rounded-xl */
  padding: 16px; /* p-4 */
  margin-top: 16px; /* mt-4 */
  border: 1px solid rgb(var(--color-border-rgb) / 0.1); /* border border-white/10 */
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgb(var(--color-shadow-rgb) / 0.3);
}

/* ========== 绱у噾璧勪骇 HUD 鏉?- 鍗曡姘村钩甯冨眬 ========== */
.assets-hud-strip {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  height: 48px; /* 鍥哄畾楂樺害锛岄潪甯哥揣鍑?*/
  padding: 0;
  background: transparent; /* 閫忔槑鑳屾櫙 */
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
  font-size: 10px; /* 闈炲父灏忕殑鏍囩 */
  color: var(--color-text-secondary); 
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1;
}

.asset-hud-value { 
  font-size: 14px; /* 閫備腑澶у皬鐨勬暟鍊?*/
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

.coin-select-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
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

/* 淇3锛欰ctionSheet 榛戦噾椋庢牸 */
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

/* ========== 鍚堢害浜ゆ槗鏍峰紡 - 鑷劧娴佸紡甯冨眬 ========== */
.futures-trade-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  position: relative; /* 浣跨敤 relative锛岀姝?absolute */
  display: flex;
  flex-direction: column;
  /* 绉婚櫎鍥哄畾楂樺害鍜?overflow锛屼娇鐢ㄨ嚜鐒舵祦寮忓竷灞€ */
}

/* 椤堕儴鎺у埗鏍?- 涓庣幇璐ч〉闈㈢殑 pair-info 楂樺害瀹屽叏涓€鑷?*/
.futures-control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px; /* 涓?pair-info 瀹屽叏涓€鑷?*/
  background: linear-gradient(180deg, rgb(var(--color-bg-rgb) / 0.95) 0%, var(--color-bg) 100%);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05); /* 涓?pair-info 涓€鑷?*/
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

/* 涓棿浜ゆ槗鍖哄煙 - 鑷劧娴佸紡甯冨眬 */
.futures-trade-main {
  display: flex;
  gap: 8px;
  padding: 8px 8px 8px 0;
  align-items: flex-start;
  /* 绉婚櫎鍥哄畾楂樺害鍜?overflow锛屼娇鐢ㄨ嚜鐒舵祦寮忓竷灞€ */
}

/* 鍚堢害鐩樺彛鏍峰紡宸蹭笌鐜拌揣鍏变韩锛屾棤闇€閲嶅瀹氫箟 */

/* 璧勪骇淇℃伅闈㈡澘 */
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
  width: 40%; /* w-[40%] - 涓庣幇璐ч〉闈竴鑷?*/
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* 浣跨敤鑷劧娴佸紡甯冨眬锛屼笉闄愬埗楂樺害 */
}

.futures-action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
  padding-top: 16px;
}

/* 鍚堢害椤甸潰鎸夐挳 - Grid 甯冨眬锛岀‘淇濇€婚珮搴︿笌鐜拌揣椤甸潰涓€鑷?*/
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

/* 寮€澶氭寜閽?- 闇撹櫣缁胯壊娓愬彉 */
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

/* 寮€绌烘寜閽?- 闇撹櫣绾㈣壊娓愬彉 */
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

/* Grid 甯冨眬鎸夐挳鏍峰紡 - 纭繚鎬婚珮搴︿笌鐜拌揣椤甸潰鍗曚釜鎸夐挳涓€鑷达紙48px锛?*/
.long-btn-grid, .short-btn-grid {
  width: 100%;
  height: 48px; /* 涓庣幇璐ч〉闈?submit-btn 楂樺害涓€鑷?*/
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

/* 寮€澶氭寜閽?- Grid 鐗堟湰 - 闇撹櫣缁胯壊娓愬彉 */
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

/* 寮€绌烘寜閽?- Grid 鐗堟湰 - 闇撹櫣绾㈣壊娓愬彉 */
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

/* 搴曢儴闈㈡澘 - 鑷劧娴佸紡甯冨眬 */
.futures-bottom-section {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-top: 1px solid rgb(var(--color-brand-rgb) / 0.1);
  box-shadow: 0 -4px 20px rgb(var(--color-shadow-rgb) / 0.5);
  display: flex;
  flex-direction: column;
  margin-top: 8px; /* mt-2 = 8px锛屼笌浜ゆ槗琛ㄥ崟鐨勯棿璺?*/
  padding: 0 8px; /* px-2 = 8px */
  /* 浣跨敤鑷劧娴佸紡甯冨眬锛屼笉闄愬埗楂樺害 */
}

.position-tabs {
  display: flex;
  flex-direction: column;
  /* 绉婚櫎鍥哄畾楂樺害鍜?overflow锛屼娇鐢ㄨ嚜鐒舵祦寮忓竷灞€ */
}

:deep(.position-tabs .van-tabs__wrap) {
  background: linear-gradient(180deg, var(--color-bg) 0%, rgb(var(--color-bg-rgb) / 0.98) 100%);
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
  flex-shrink: 0; /* 闃叉琚帇缂?*/
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
  height: 48px; /* 鍥哄畾鏍囩鏍忛珮搴?*/
  padding: 8px 16px; /* 涓庣幇璐ч〉闈竴鑷?*/
}

/* 缁熶竴鏍囩椤垫牱寮忥紝涓庣幇璐ч〉闈竴鑷?*/
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
  /* 绉婚櫎鍥哄畾楂樺害鍜?overflow锛屼娇鐢ㄨ嚜鐒舵祦寮忓竷灞€ */
  position: relative;
}

:deep(.position-tabs .van-tab__panel) {
  width: 100%;
  /* 绉婚櫎鍥哄畾楂樺害鍜?overflow锛屼娇鐢ㄨ嚜鐒舵祦寮忓竷灞€ */
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
  /* 浣跨敤鑷劧娴佸紡甯冨眬锛屼笉闄愬埗楂樺害 */
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px; /* 鏈€灏忛珮搴︼紝纭繚绌虹姸鎬佸彲瑙?*/
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
  background: rgb(var(--color-border-rgb) / 0.05); /* bg-white/5 - 鐜荤拑鎷熸€佹晥鏋?*/
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

/* 鎸佷粨鏂瑰悜鏍囩 - 澶?绌?*/
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
  font-size: 32px; /* text-3xl - 鏇村ぇ鏇撮啋鐩?*/
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

/* 寮€浠撳潎浠烽鑹?- 鏍规嵁鏂瑰悜鍙樺寲 */
.entry-price-value.side-long {
  color: var(--color-earn); /* 澶氬崟缁胯壊 */
  text-shadow: 0 0 8px rgb(var(--color-earn-rgb) / 0.4);
}

.entry-price-value.side-short {
  color: var(--color-loss); /* 绌哄崟绾㈣壊 */
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

/* ========== 褰诲簳閲嶆瀯鐨勯粦閲戞牱寮?========== */

/* 1. 寮圭獥鍩虹瀹瑰櫒 */
:deep(.van-popup.premium-tpsl-popup) {
  background: var(--color-bg) !important; /* 绾繁鑹插簳 */
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

/* 2. 澶撮儴鏍囬 */
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

/* 3. 杈撳叆缁勬牱寮?*/
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

/* 4. 鏍稿績杈撳叆妗嗙洅妯″瀷 */
.premium-input-box {
  display: flex;
  align-items: center;
  background: rgb(var(--color-border-rgb) / 0.03); /* 鐜荤拑鎷熸€佸簳鑹?*/
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

/* 绉婚櫎鏁板瓧杈撳叆妗嗙澶?*/
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

/* 5. 蹇嵎閫夋嫨鏍囩 */
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

/* 6. 榛勯噾娓愬彉鎸夐挳 */
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

/* 閿欒鎻愮ず鏍峰紡 */
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

/* 杈撳叆妗嗛敊璇姸鎬?*/
.input-error {
  border-color: var(--color-loss) !important;
  background: rgb(var(--color-loss-rgb) / 0.05) !important;
}

/* 鐧惧垎姣旀寜閽鐢ㄧ姸鎬?*/
.percent-tag.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
  background: rgb(var(--color-border-rgb) / 0.05) !important;
  color: rgb(var(--color-border-rgb) / 0.3) !important;
}

/* Trading form polish */
.right-form-panel {
  background: var(--color-surface-2) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: 14px !important;
  box-shadow: var(--shadow-md) !important;
  padding: 6px !important;
}

.buy-sell-toggle {
  background: var(--color-surface-1);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 4px;
}

.toggle-btn {
  border-radius: 10px;
  color: var(--color-text-secondary);
}

.buy-btn.active {
  background: rgb(var(--color-success-rgb) / 0.12) !important;
  color: var(--color-success) !important;
  border: 1px solid rgb(var(--color-success-rgb) / 0.28) !important;
  box-shadow: none !important;
  text-shadow: none !important;
}

.sell-btn.active {
  background: rgb(var(--color-danger-rgb) / 0.12) !important;
  color: var(--color-danger) !important;
  border: 1px solid rgb(var(--color-danger-rgb) / 0.28) !important;
  box-shadow: none !important;
  text-shadow: none !important;
}

.order-type-selector,
.input-row,
.fee-estimate-row,
.total-row,
.estimated-received-row {
  background: var(--color-surface-2) !important;
  border: 1px solid var(--color-border) !important;
  box-shadow: var(--shadow-sm) !important;
  border-radius: 12px !important;
}

.input-row {
  min-height: 52px;
  height: auto;
  padding: 0 14px;
}

.input-row:focus-within {
  border-color: var(--color-primary-border) !important;
  box-shadow: 0 0 0 3px var(--color-focus-ring) !important;
  background: var(--color-surface-2) !important;
}

.input-label {
  min-width: 0;
  flex-shrink: 0;
  max-width: 46%;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text-secondary);
  letter-spacing: 0;
}

.input-field {
  min-width: 0;
  text-align: right;
  color: var(--color-text-primary);
  font-size: 15px;
}

.input-field::placeholder {
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 600;
}

.estimated-received-row {
  background: rgb(var(--color-primary-rgb) / 0.08) !important;
  border-color: rgb(var(--color-primary-rgb) / 0.18) !important;
  box-shadow: none !important;
}

.received-label,
.received-value {
  color: var(--color-primary-hover) !important;
  text-shadow: none !important;
}

.available-row {
  background: var(--color-surface-1);
  border: 1px solid var(--color-border-subtle);
  border-radius: 12px;
  padding: 10px 12px;
}

.avail-item {
  justify-content: space-between;
}

.submit-btn {
  border-radius: 12px;
  box-shadow: none !important;
}

.submit-btn:disabled {
  background: var(--color-surface-muted) !important;
  color: var(--color-text-muted) !important;
  border: 1px solid var(--color-border) !important;
  opacity: 1;
  filter: none;
}

/* Compact viewport tuning */
.orderbook-header { padding: 5px 10px !important; min-height: 22px !important; }
.order-row { height: 18px !important; line-height: 18px !important; padding: 0 10px !important; }
.order-row .price,
.order-row .quantity { font-size: 12px !important; line-height: 18px !important; }
.last-price { height: 40px !important; min-height: 40px !important; }
.price-main { font-size: 18px !important; line-height: 1.1 !important; }
.price-fiat { font-size: 10px !important; }
.right-form-panel { gap: 6px !important; padding: 6px !important; }
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

