import { defineStore } from 'pinia';
import { getPositions as getFuturesPositionsApi, setPositionTPSL } from '@/api/futures';
import { useAssetStore } from '@/stores/assets';

export const useTradeStore = defineStore('trade', {
  state: () => ({
    positions: [],
  }),
  actions: {
    async fetchPositions() {
      console.log('[TradeStore] 开始获取持仓列表...');
      try {
        const response = await getFuturesPositionsApi();
        const responseData = response.data || response;
        if (responseData && responseData.code === 200 && responseData.data) {
          this.positions = responseData.data.map(pos => {
            const margin = pos.margin || (pos.entry_price * pos.size / (pos.leverage || 20));
            const unrealizedPnl = pos.unrealized_pnl || 0;
            const unrealizedPnlPercent = margin > 0 ? (unrealizedPnl / margin) * 100 : 0;
            
            // 使用标准化字段名 take_profit 和 stop_loss
            const take_profit = pos.take_profit_price || pos.take_profit || null;
            const stop_loss = pos.stop_loss_price || pos.stop_loss || null;
            
            return {
              id: `${pos.symbol}_${pos.side}`,
              symbol: pos.symbol?.split('/')[0] || pos.symbol,
              side: pos.side?.toLowerCase() || 'long',
              quantity: pos.size || pos.quantity || 0,
              entryPrice: pos.entry_price || 0,
              leverage: pos.leverage || 20,
              margin: margin,
              liquidationPrice: pos.liquidation_price || 0,
              unrealizedPnl: unrealizedPnl,
              unrealizedPnlPercent: unrealizedPnlPercent,
              markPrice: pos.mark_price || 0,
              // 标准化字段名（使用 snake_case）
              take_profit: take_profit,
              stop_loss: stop_loss
            };
          });
          console.log('[TradeStore] 持仓列表获取成功:', this.positions);
          console.log('[TradeStore] Fetched positions with TP/SL:', this.positions);
          
          // 同步到 assets store
          const assetsStore = useAssetStore();
          if (assetsStore) {
            assetsStore.syncPositions(this.positions);
          }
        } else {
          this.positions = [];
          console.log('[TradeStore] 无持仓数据');
        }
      } catch (error) {
        console.error('[TradeStore] 获取持仓列表失败:', error);
        this.positions = [];
      }
    },
    async setTPSL(positionId, tp, sl) {
      console.log('[TradeStore] 设置止盈止损:', { positionId, tp, sl });
      try {
        // 从positionId中提取symbol（格式：BTC/USDT_long）
        const [symbol, side] = positionId.split('_');
        const symbolPair = symbol.includes('/') ? symbol : `${symbol}/USDT`;
        
        const response = await setPositionTPSL({
          symbol: symbolPair,
          take_profit: tp || null,
          stop_loss: sl || null
        });
        
        console.log('[TradeStore] Set response:', response.data);
        
        const responseData = response.data || response;
        if (responseData && responseData.code === 200) {
          console.log('[TradeStore] 止盈止损设置成功，刷新持仓列表...');
          await this.fetchPositions();
          console.log('[TradeStore] TPSL设置完成，持仓列表已刷新');
        } else {
          throw new Error(responseData?.message || '设置失败');
        }
      } catch (error) {
        console.error('[TradeStore] 设置止盈止损失败:', error);
        throw error;
      }
    },
  },
});
