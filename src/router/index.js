import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Miner from '../components/Miner.vue'
import IDO from '../components/IDO.vue'
import Me from '../components/Me.vue'
import Deposit from '../components/Deposit.vue'
import Withdraw from '../components/Withdraw.vue'
import Trade from '../components/Trade.vue'
import MarketDetail from '../components/MarketDetail.vue'
import History from '../components/History.vue'
import EarnList from '../components/EarnList.vue'
import EarnSubscribe from '../components/EarnSubscribe.vue'
import AllMarkets from '../components/AllMarkets.vue'
import TreasuryDetail from '../components/TreasuryDetail.vue'
import ChainExplorer from '../components/ChainExplorer.vue'
import UserProfile from '../components/UserProfile.vue'
import Support from '../components/Support.vue'
import Settings from '../components/Settings.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/miner', component: Miner },
  { path: '/ido', component: IDO },
  { path: '/me', component: Me },
  { path: '/deposit', name: 'Deposit', component: Deposit },
  { path: '/withdraw', name: 'Withdraw', component: Withdraw },
  { path: '/trade', name: 'Trade', component: Trade },
  { path: '/market', name: 'MarketDetail', component: MarketDetail },
  { path: '/history', name: 'History', component: History },
  { path: '/earn', name: 'EarnList', component: EarnList },
  { path: '/earn/subscribe', name: 'EarnSubscribe', component: EarnSubscribe },
  { path: '/all-markets', name: 'AllMarkets', component: AllMarkets },
  { path: '/treasury', name: 'Treasury', component: TreasuryDetail, meta: { title: 'Treasury Audit' } },
  { path: '/chain-explorer', name: 'ChainExplorer', component: ChainExplorer },
  { path: '/profile', name: 'UserProfile', component: UserProfile },
  { path: '/support', name: 'Support', component: Support },
  { path: '/settings', name: 'Settings', component: Settings }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

