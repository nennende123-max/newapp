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
import SecurityCenter from '../components/SecurityCenter.vue'
import FundPassword from '../components/FundPassword.vue'
import PhoneVerify from '../components/PhoneVerify.vue'
import GoogleAuth from '../components/GoogleAuth.vue'
import FuturesTrade from '../components/FuturesTrade.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/miner', component: Miner },
  { path: '/ido', component: IDO },
  { path: '/me', component: Me },
  { path: '/deposit', name: 'Deposit', component: Deposit },
  { path: '/withdraw', name: 'Withdraw', component: Withdraw },
  { path: '/trade', name: 'Trade', component: Trade },
  { path: '/futures', name: 'FuturesTrade', component: FuturesTrade },
  { path: '/market', name: 'MarketDetail', component: MarketDetail },
  { path: '/history', name: 'History', component: History },
  { path: '/earn', name: 'EarnList', component: EarnList,meta: { hideTabbar: true } },
  { path: '/earn/subscribe', name: 'EarnSubscribe', component: EarnSubscribe },
  { path: '/all-markets', name: 'AllMarkets', component: AllMarkets },
  { path: '/treasury', name: 'Treasury', component: TreasuryDetail, meta: { hideTabbar: true } },
  { path: '/chain-explorer', name: 'ChainExplorer', component: ChainExplorer ,meta: { hideTabbar: true }},
  { path: '/profile', name: 'UserProfile', component: UserProfile },
  { path: '/support', name: 'Support', component: Support },
  { path: '/settings', name: 'Settings', component: Settings },
  { path: '/security-center', name: 'SecurityCenter', component: SecurityCenter },
  { path: '/fund-password', name: 'FundPassword', component: FundPassword },
  { path: '/phone-verify', name: 'PhoneVerify', component: PhoneVerify },
  { path: '/google-auth', name: 'GoogleAuth', component: GoogleAuth }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

