import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import Vant from 'vant'
// 确保 Vant 样式在全局样式之前引入，保证图标字体优先级
import 'vant/lib/index.css'
// 引入全局样式（包含图标字体修复）
import './style.css'

const messages = {
  en: {
    common: {
      loading: 'Loading...',
      no_data: 'No Data',
      live_on_chain: '🚀 Live On-Chain:',
      left: 'Left'
    },
    home_btn: {
      deposit: 'Deposit',
      withdraw: 'Withdraw',
      earn: 'Earn',
      service: 'Service',
      team: 'My Team'
    },
    home: {
      slogan: 'The World\'s First Transparent Asset Platform',
      platform_transparency: 'Platform Transparency',
      audited_by_certik: 'Audited by CertiK',
      redirecting_certik: 'Redirecting to CertiK Scan...',
      treasury_tvl: 'TREASURY TVL',
      total_payout: 'TOTAL PAYOUT',
      '24h_txns': '24H TXNS',
      since_2025: 'Since 2025',
      on_chain: 'On-Chain',
      market_overview: 'Market Overview',
      all_markets: 'All Markets',
      ticker: {
        prefix: '🚀 Live On-Chain:',
        withdraw: 'User {user} just withdrew {amount} USDT (Tx: {tx})',
        battle: 'User {user} won Price Battle (+{amount} USDT)',
        treasury: 'Treasury added {amount} assets today',
        audit: 'Audit Radar: IDO #{id} verified by CertiK'
      }
    },
    tab: {
      home: 'Home',
      miner: 'Miner',
      ido: 'IDO',
      me: 'Me'
    },
    connect: 'Connect Wallet',

    // 充值页面（新增 subtitle）
    deposit: {
      title: 'Deposit Crypto',
      subtitle: 'Deposit USDT via supported networks',  // 新增
      net: 'Select Network',
      addr: 'Deposit Address',
      copy: 'Copy Address',
      tips: 'Send only USDT to this address. Sending any other coins may result in permanent loss.',
      copy_success: 'Address Copied!'
    },

    // 提现页面（新增 subtitle）
    withdraw: {
      title: 'Withdraw USDT',
      subtitle: 'Withdraw USDT to your wallet',
      net: 'Select Network',
      addr: 'Withdraw Address',
      addr_placeholder: 'Enter wallet address',
      amount: 'Amount',
      amount_placeholder: 'Enter amount',
      available_balance: 'Available Balance:',
      max: 'MAX',
      network_fee: 'Network Fee:',
      receive_amount: 'Receive Amount:',
      withdraw_btn: 'Withdraw',
      tip1: 'Ensure the network matches your wallet address',
      tip2: 'Double-check the address before confirming',
      tip3: 'Withdrawal may take 5-30 minutes to process',
      address_pasted: 'Address pasted',
      paste_failed: 'Failed to paste',
      submitted: 'Submitted',
      history_coming_soon: 'History feature coming soon',
      network_trc20: 'TRC20',
      network_erc20: 'ERC20',
      network_bsc: 'BSC'
    },

    mining: 'Cloud Mining',
    battle: 'Price Battle',
    round: 'Round',
    left: 'LEFT',
    feed: 'Real-time Feed: Binance & Coinbase Weighted',
    bullish: 'BULLISH',
    bearish: 'BEARISH',
    results: 'Recent Battle Results',
    market: 'Market',
    inst_power: 'Institutional Mining Power',
    update_db: 'Updating Database...',
    safe_sla: 'Safe & SLA Guaranteed',
    daily_rate: 'Daily Rate',
    cycle: 'Cycle',
    min_price: 'Min Price',
    rent_btn: 'Rent Machine Now',

    // 钱包/资产页面
    wallet: {
      est_total_value: 'Est. Total Value',
      wallet_connected: 'Wallet Connected',
      wallet_address: 'Wallet Address',
      deposit: 'Deposit',
      withdraw: 'Withdraw',
      transfer: 'Transfer',
      today_pnl: 'Today\'s PnL',
      account_breakdown: 'Assets Breakdown',
      spot_account: 'Spot Account',
      earn_account: 'Earn Account',
      ieo_locked: 'IEO Locked',
      referral_title: 'Invite Friends & Earn',
      referral_desc: 'When friends trade, you can earn up to',
      referral_rebate: 'rebate',
      referral_earned: 'Earned'
    },
    // 资产页面
    assets: {
      title: 'Assets',
      overview: 'Overview',
      spot: 'Spot',
      earn: 'Earn',
      est_total_value: 'Est. Total Value',
      deposit: 'Deposit',
      withdraw: 'Withdraw',
      transfer: 'Transfer',
      convert_small: 'Convert small assets to BNB',
      hide_zero: 'Hide 0 balances',
      search_placeholder: 'Search',
      no_earning_products: 'No active earning products',
      today_pnl: 'Today\'s PnL',
      asset_allocation: 'Asset Allocation',
      spot_account: 'Spot Account',
      earn_account: 'Earn Account',
      ido_pending: 'IEO Pending Unlock',
      ido_pending_desc: 'Pending unlock assets',
      usdt: 'TetherUS',
      btc: 'Bitcoin',
      beat: 'BEAT Token',
      zec: 'Zcash',
      aic: 'AI Comic',
      meme: 'Meme Coin'
    },

    // 理财页面
    earn: {
      title: 'Earn',
      search_placeholder: 'Search',
      tab: {
        hot: 'Hot',
        safe: 'Safe',
        high_yield: 'High Yield',
        simple: 'Simple',
        advanced: 'Advanced'
      },
      total_asset: 'Total Asset Value',
      cumulative_earnings: 'Cumulative Earnings',
      no_products_desc: 'No products available at the moment',
      subscribe: 'Subscribe',
      flexible: 'Flexible',
      days: ' Days',
      reference_annual: 'Reference Annualized',
      tiered_annual_rate: 'Tiered Annual Rate',
      term_days: 'Term (Days)',
      subscribe_amount: 'Subscription Amount',
      enter_amount: 'Enter Amount',
      max: 'MAX',
      available_balance: 'Available Balance',
      quantity_limit: 'Quantity Limit',
      min_investment: 'Minimum Investment',
      available_quota: 'Available Quota',
      individual_quota: 'Individual Total Quota',
      overview: 'Overview',
      real_time_apy: 'Real-time Annualized Yield',
      estimated_daily: 'Estimated Daily Earnings',
      apy_disclaimer: 'Annualized interest rate does not represent actual or estimated earnings calculated in fiat currency.',
      agreement_text: 'I have read and agree to the Wealth Management Service Agreement',
      confirm: 'Confirm',
      subscribe_success: 'Subscription successful',
      no_products: 'No products available',
      help_tooltip: 'Help',
      insufficient_balance: 'Insufficient balance'
    },

    // Earn Center
    miner: {
      total_assets: 'Earn Total Assets',
      total_profit: 'Total Profit',
      stable_earn: 'Stable Earn',
      revenue_record: 'Revenue Record',
      rules_center: 'Rules Center',
      cloud_mining: 'Cloud Mining',
      price_battle: 'Price Battle',
      mining_rules: '云挖矿规则',
      mining_rules_desc: 'After renting a miner, you will earn daily returns at a fixed rate. Returns will be automatically credited after the cycle ends.',
      battle_rules: 'Price Battle Rules',
      battle_rules_desc: 'Predict the price direction, place a bet and wait for the countdown to end. If correct, you get 1.8x payout; if wrong, you lose the bet amount.'
    },
    // Launchpad
    launchpad: {
      title: 'TruthFi Launchpad',
      subtitle: 'Access top-tier crypto projects before listing.',
      my_assets: 'My Assets',
      beat_holdings: 'BEAT Holdings',
      usdt_balance: 'USDT Balance',
      progress: 'Progress',
      status_live: 'LIVE',
      status_upcoming: 'UPCOMING',
      status_ended: 'ENDED',
      ido_price: 'IDO Price',
      total_raise: 'Total Raise',
      vesting: 'Vesting'
    },

    // 交易页面
    trade: {
      buy: 'Buy',
      sell: 'Sell',
      limit_order: 'Limit Order',
      market_order: 'Market Order',
      price: 'Price',
      price_placeholder: 'Enter price',
      amount: 'Amount',
      amount_placeholder: 'Enter amount',
      total: 'Total',
      avail: 'Avail',
      buy_btc: 'Buy BTC',
      sell_btc: 'Sell BTC',
      open_orders: 'Open Orders',
      no_orders: 'No open orders',
      cancel: 'Cancel',
      order_submitted: 'Order submitted',
      order_cancelled: 'Order cancelled',
      fill_all_fields: 'Please fill all fields',
      chart_coming_soon: 'Chart feature coming soon'
    },

    // 市场详情页面
    market: {
      buy: 'Buy',
      sell: 'Sell',
      orderbook: 'Order Book',
      recent_trades: 'Recent Trades',
      time: 'Time',
      price: 'Price',
      amount: 'Amount',
      '24h_high': '24h High',
      '24h_low': '24h Low',
      '24h_vol': '24h Vol',
      '24h_amt': '24h Amt',
      indicators_coming_soon: 'Indicators feature coming soon',
      settings_coming_soon: 'Settings feature coming soon',
      switch_symbol: 'Switch Symbol',
      search_placeholder: 'Search coin',
      name_vol: 'Name / Vol',
      last_price: 'Last Price',
      '24h_chg': '24h Chg%'
    },

    // 历史记录页面
    history: {
      title: 'History',
      empty: 'No records yet',
      transaction: 'Transaction',
      tab: {
        deposit: 'Deposit',
        withdraw: 'Withdraw',
        subscription: 'Subscription'
      },
      status: {
        success: 'Success',
        failed: 'Failed',
        pending: 'Pending'
      }
    },

    // 国库资金明细页面
    treasury: {
      title: 'Treasury Details',
      real_time_assets: 'Real-time Treasury Assets',
      security_level: 'Security Level',
      auditor: 'Audited by',
      net_inflow_30d: 'Last 30 Days Net Inflow',
      on_chain_records: 'Live Accumulation Records (On-Chain)',
      spot_fee: 'Spot Trading Fee',
      futures_fee: 'Futures Trading Fee',
      staking_reward: 'Staking Reward Distribution',
      liquidity_pool_fee: 'Liquidity Pool Fee',
      ido_platform_fee: 'IDO Platform Fee',
      margin_trading_fee: 'Margin Trading Fee',
      txid_copied: 'TxID Copied',
      copy_failed: 'Copy Failed'
    }
  },
  zh: {
    common: {
      loading: '加载中...',
      no_data: '暂无数据',
      live_on_chain: '🚀 链上实况:',
      left: '剩余'
    },
    home_btn: {
      deposit: '充值',
      withdraw: '提现',
      earn: '理财',
      service: '客服',
      team: '团队'
    },
    home: {
      slogan: '全球首个透明资产平台',
      platform_transparency: '平台透明度',
      audited_by_certik: 'Audited by CertiK',
      redirecting_certik: '正在跳转到 CertiK 扫描...',
      treasury_tvl: '国库资产',
      total_payout: '累计支出',
      '24h_txns': '24h 链上交易',
      since_2025: '自 2025 年起',
      on_chain: '链上数据',
      market_overview: '市场概览',
      all_markets: '所有市场',
      ticker: {
        prefix: '🚀 链上实况:',
        withdraw: '用户 {user} 刚刚提取 {amount} USDT (Tx: {tx})',
        battle: '用户 {user} 赢得了价格对决 (+{amount} USDT)',
        treasury: '国库今日新增资产 {amount}',
        audit: '审计雷达: IDO #{id} 已通过 CertiK 验证'
      }
    },
    tab: {
      home: '首页',
      miner: '赚币',
      ido: '认购',
      me: '我的'
    },
    connect: '连接钱包',

    // 充值页面（新增 subtitle）
    deposit: {
      title: '加密货币充值',
      subtitle: '通过支持的网络充值 USDT',  // 新增
      net: '选择网络',
      addr: '充值地址',
      copy: '复制地址',
      tips: '请仅向该地址转入 USDT，转入其他币种可能无法找回。',
      copy_success: '地址已复制！'
    },

    // 提现页面（新增 subtitle）
    withdraw: {
      title: '提现 USDT',
      subtitle: '将 USDT 提现到您的钱包',
      net: '选择网络',
      addr: '提现地址',
      addr_placeholder: '请输入钱包地址',
      amount: '金额',
      amount_placeholder: '请输入金额',
      available_balance: '可用余额：',
      max: '最大',
      network_fee: '网络费用：',
      receive_amount: '接收金额：',
      withdraw_btn: '提现',
      tip1: '请确保网络与您的钱包地址匹配',
      tip2: '确认前请仔细核对地址',
      tip3: '提现可能需要 5-30 分钟处理',
      address_pasted: '地址已粘贴',
      paste_failed: '粘贴失败',
      submitted: '已提交',
      history_coming_soon: '历史记录功能即将推出',
      network_trc20: 'TRC20',
      network_erc20: 'ERC20',
      network_bsc: 'BSC'
    },

    mining: '云挖矿',
    battle: '价格对决',
    round: '轮次',
    left: '剩余',
    feed: '实时数据: 币安 & Coinbase 加权',
    bullish: '看涨 (买多)',
    bearish: '看跌 (买空)',
    results: '近期对决结果',
    market: '市场',
    inst_power: '机构级算力池',
    update_db: '正在同步链上数据...',
    safe_sla: 'SLA 协议保障',
    daily_rate: '日收益率',
    cycle: '周期',
    min_price: '起购价',
    rent_btn: '立即租赁矿机',

    // 钱包/资产页面
    wallet: {
      est_total_value: '预估总资产',
      wallet_connected: '钱包已连接',
      wallet_address: '钱包地址',
      deposit: '充值',
      withdraw: '提现',
      transfer: '转账',
      today_pnl: '今日盈亏',
      account_breakdown: '账户资产分布',
      spot_account: '现货账户',
      earn_account: '赚币账户',
      ieo_locked: 'IEO 待解锁',
      referral_title: '邀请好友赚佣金',
      referral_desc: '好友交易，您最高可获',
      referral_rebate: '返佣',
      referral_earned: '已赚'
    },
    // 资产页面
    assets: {
      title: '资产',
      overview: '概览',
      spot: '现货',
      earn: '理财',
      est_total_value: '预估总资产',
      deposit: '充值',
      withdraw: '提现',
      transfer: '转账',
      convert_small: '将小额资产转换为 BNB',
      hide_zero: '隐藏零余额',
      search_placeholder: '搜索',
      no_earning_products: '暂无理财产品',
      today_pnl: '今日盈亏',
      asset_allocation: '账户资产分布',
      spot_account: '现货账户',
      earn_account: '赚币账户',
      ido_pending: 'IEO 待解锁',
      ido_pending_desc: '待解锁资产',
      usdt: '泰达币',
      btc: '比特币',
      beat: 'BEAT 代币',
      zec: 'Zcash',
      aic: 'AI 漫画',
      meme: '模因币'
    },

    // 理财页面
    earn: {
      title: '理财',
      search_placeholder: '搜索',
      tab: {
        hot: '热门',
        safe: '保本',
        high_yield: '高收益',
        simple: '稳健',
        advanced: '进阶'
      },
      subscribe: '申购',
      flexible: '活期',
      days: '天',
      reference_annual: '参考年化',
      tiered_annual_rate: '阶梯年利率',
      term_days: '期限(天)',
      subscribe_amount: '申购金额',
      enter_amount: '输入金额',
      max: '全部',
      available_balance: '可用余额',
      quantity_limit: '数量限制',
      min_investment: '最少可投',
      available_quota: '可用额度',
      individual_quota: '个人总额度',
      overview: '概览',
      real_time_apy: '实时年化收益率',
      estimated_daily: '估计每日收益',
      apy_disclaimer: '年利率并不表示以法币计算的实际或预计收益。',
      agreement_text: '我已阅读并同意 币安理财服务协议',
      confirm: '确认',
      subscribe_success: '申购成功',
      no_products: '暂无产品',
      no_products_desc: '暂无可用产品，请稍后再试',
      help_tooltip: '帮助',
      insufficient_balance: '余额不足',
      total_asset: '理财总资产',
      cumulative_earnings: '累计收益'
    },

    // 聚合赚币中心
    miner: {
      total_assets: '赚币账户总资产',
      total_profit: '累计收益',
      stable_earn: '稳健理财',
      revenue_record: '收益记录',
      rules_center: '规则中心',
      cloud_mining: '云挖矿',
      price_battle: '价格对决',
      mining_rules: '云挖矿规则',
      mining_rules_desc: '租用矿机后，每日按固定收益率获得收益。收益将在周期结束后自动到账。',
      battle_rules: '价格对决规则',
      battle_rules_desc: '预测价格涨跌方向，下注后等待倒计时结束。若预测正确，将获得1.8倍赔付；若预测错误，将损失下注金额。'
    },
    // Launchpad
    launchpad: {
      title: 'TruthFi 认购',
      subtitle: '在上市前抢先体验顶级加密项目。',
      my_assets: '我的资产',
      beat_holdings: 'BEAT 持仓',
      usdt_balance: 'USDT 余额',
      progress: '认购进度',
      status_live: '进行中',
      status_upcoming: '即将开始',
      status_ended: '已结束',
      ido_price: '认购价格',
      total_raise: '募资总额',
      vesting: '解锁规则'
    },

    // 交易页面
    trade: {
      buy: '买入',
      sell: '卖出',
      limit_order: '限价单',
      market_order: '市价单',
      price: '价格',
      price_placeholder: '请输入价格',
      amount: '数量',
      amount_placeholder: '请输入数量',
      total: '总额',
      avail: '可用',
      buy_btc: '买入 BTC',
      sell_btc: '卖出 BTC',
      open_orders: '当前委托',
      no_orders: '暂无委托订单',
      cancel: '撤单',
      order_submitted: '订单已提交',
      order_cancelled: '订单已取消',
      fill_all_fields: '请填写所有字段',
      chart_coming_soon: '图表功能即将推出'
    },

    // 市场详情页面
    market: {
      buy: '买入',
      sell: '卖出',
      orderbook: '盘口',
      recent_trades: '最新成交',
      time: '时间',
      price: '价格',
      amount: '数量',
      '24h_high': '24h最高',
      '24h_low': '24h最低',
      '24h_vol': '24h成交量',
      '24h_amt': '24h成交额',
      indicators_coming_soon: '指标功能即将推出',
      settings_coming_soon: '设置功能即将推出',
      switch_symbol: '切换币种',
      search_placeholder: '搜索币种',
      name_vol: '名称 / 成交额',
      last_price: '最新价',
      '24h_chg': '24h涨跌'
    },

    // 历史记录页面
    history: {
      title: '历史记录',
      empty: '暂无记录',
      transaction: '交易',
      tab: {
        deposit: '充值',
        withdraw: '提现',
        subscription: '认购'
      },
      status: {
        success: '成功',
        failed: '失败',
        pending: '进行中'
      }
    },

    // 国库资金明细页面
    treasury: {
      title: '国库资金明细',
      real_time_assets: '实时国库资产',
      security_level: '安全评级',
      auditor: '审计方',
      net_inflow_30d: '近 30 日资金净流入',
      on_chain_records: '实时归集记录 (On-Chain)',
      spot_fee: '现货交易手续费',
      futures_fee: '合约交易手续费',
      staking_reward: '质押奖励分配',
      liquidity_pool_fee: '流动性池手续费',
      ido_platform_fee: 'IDO 平台手续费',
      margin_trading_fee: '杠杆交易手续费',
      txid_copied: 'TxID 已复制',
      copy_failed: '复制失败'
    }
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  globalInjection: true,
  messages
})

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(i18n)
app.use(router)
app.use(Vant)
app.mount('#app')

