import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAssetStore } from '@/stores/assets'

/**
 * 统一的充值 / 提现入口（去中心化 DApp 模式）
 *
 * 全局所有「充值 / 提现」按钮都应调用 openDeposit / openWithdraw，
 * 保证行为一致：
 *  - 钱包未连接：提示「请先连接钱包」并直接触发连接钱包流程
 *  - 钱包已连接：进入充值 / 提现界面（以当前连接钱包地址为来源 / 目标地址）
 *
 * 说明：连接状态与地址统一来自 assetStore（isWalletConnected / walletAddress），
 * 复用项目已有的钱包连接逻辑，不再各页面各写一套。
 */
export function useAssetActions() {
  const router = useRouter()
  const assetStore = useAssetStore()

  // 确保钱包已连接；未连接时提示并触发连接流程
  const ensureWalletConnected = async () => {
    if (assetStore.isWalletConnected) return true

    showToast({ message: '请先连接钱包', icon: 'warning', duration: 2000 })
    try {
      await assetStore.connectWallet()
    } catch (error) {
      // 用户取消或连接失败：保持在当前页，不进入操作流程
      return false
    }
    return assetStore.isWalletConnected
  }

  const openDeposit = async (token = 'USDT') => {
    if (!(await ensureWalletConnected())) return
    router.push({ path: '/deposit', query: { token } })
  }

  const openWithdraw = async (token = 'USDT') => {
    if (!(await ensureWalletConnected())) return
    router.push({ path: '/withdraw', query: { token } })
  }

  return { openDeposit, openWithdraw, ensureWalletConnected }
}

export default useAssetActions
