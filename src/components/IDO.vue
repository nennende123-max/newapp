<template>
    <div class="ido-page">
      
      <div class="launchpad-header">
        <h2 class="page-title">{{ $t('launchpad.title') }}</h2>
        <p class="page-sub">{{ $t('launchpad.subtitle') }}</p>
      </div>

      <!-- My Assets Card -->
      <div class="assets-card">
        <h3 class="assets-title">{{ $t('launchpad.my_assets') }}</h3>
        <div class="assets-grid">
          <div class="asset-item">
            <div class="asset-label">{{ $t('launchpad.beat_holdings') }}</div>
            <div class="asset-value gold-text" v-if="assetStore.isWalletConnected">
              {{ formatNumber(assetStore.beatBalance) }} BEAT
            </div>
            <div class="asset-value gold-text" v-else>***</div>
          </div>
          <div class="asset-item">
            <div class="asset-label">{{ $t('launchpad.usdt_balance') }}</div>
            <div class="asset-value" v-if="assetStore.isWalletConnected">
              {{ formatNumber(assetStore.usdtBalance) }} USDT
            </div>
            <div class="asset-value" v-else>***</div>
          </div>
        </div>
        <div v-if="!assetStore.isWalletConnected" class="wallet-notice">
          <van-icon name="info-o" />
          <span>{{ $t('connect') === '连接钱包' ? '请连接钱包以查看资产' : 'Please connect wallet to view assets' }}</span>
        </div>
      </div>
  
      <div class="project-list">
        
        <!-- 进行中项目 -->
        <div v-if="liveProject" class="project-card live-card">
          <div class="status-badge live status-live">
            <span class="pulse-dot"></span> {{ $t('launchpad.status_live') }}
          </div>
  
          <div class="card-header">
            <div class="project-logo" :class="liveProject.logoClass">{{ liveProject.logoText }}</div>
            <div class="project-info">
              <h3 class="project-name">{{ liveProject.name }} <span class="ticker">{{ liveProject.ticker }}</span></h3>
              <div class="tags">
                <span class="tag" v-for="tag in liveProject.tags" :key="tag">{{ tag }}</span>
                <span class="tag audit-tag" v-if="liveProject.auditor">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                  {{ liveProject.auditor }}
                </span>
              </div>
            </div>
          </div>

          <!-- 实时成交跑马灯 -->
          <div v-if="liveMessage" class="live-ticker">
            <div class="ticker-content">{{ liveMessage }}</div>
          </div>
  
          <div class="progress-section">
            <div class="progress-info">
              <span>{{ $t('launchpad.progress') }}</span>
              <span class="gold-text">{{ Math.round(displayProgress) }}%</span>
            </div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" :style="{ width: displayProgress + '%', transition: 'width 1s ease-out' }"></div>
            </div>
            <div class="raise-detail">
              <span>{{ formatRaised(displayCurrentRaised) }} / {{ formatRaised(liveProject.targetRaise) }} USDT</span>
            </div>
          </div>
  
          <div class="data-grid">
            <div class="data-item">
              <span class="label">{{ $t('launchpad.ido_price') }}</span>
              <span class="value">${{ liveProject.price.toFixed(3) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ $t('launchpad.total_raise') }}</span>
              <span class="value">${{ formatTotalRaise(liveProject.targetRaise) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ $t('launchpad.vesting') }}</span>
              <span class="value highlight">{{ liveProject.vesting }}</span>
            </div>
          </div>
  
          <button 
            class="action-btn"
            :class="isJoined ? 'joined-btn' : (!assetStore.isWalletConnected ? 'disabled-btn' : 'primary-btn')"
            :disabled="isJoined || !assetStore.isWalletConnected"
            @click="handleParticipate"
          >
            <span v-if="!assetStore.isWalletConnected">{{ $t('connect') }}</span>
            <span v-else-if="isJoined">{{ $t('connect') === '连接钱包' ? '已参与' : 'Joined' }}</span>
            <span v-else>{{ $t('connect') === '连接钱包' ? '立即参与' : 'Participate Now' }}</span>
          </button>
        </div>
  
        <!-- 即将开始项目 -->
        <div v-if="upcomingProject" class="project-card upcoming-card">
          <div class="status-badge upcoming">
            <van-icon name="clock" /> {{ $t('launchpad.status_upcoming') }}
          </div>
  
          <div class="card-header">
            <div class="project-logo" :class="upcomingProject.logoClass">{{ upcomingProject.logoText }}</div>
            <div class="project-info">
              <h3 class="project-name">{{ upcomingProject.name }} <span class="ticker">{{ upcomingProject.ticker }}</span></h3>
              <div class="tags">
                <span class="tag" v-for="tag in upcomingProject.tags" :key="tag">{{ tag }}</span>
                <span class="tag audit-tag" v-if="upcomingProject.auditor">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                  {{ upcomingProject.auditor }}
                </span>
              </div>
            </div>
          </div>
  
          <div class="countdown-box">
            <p>Subscription starts in:</p>
            <div class="timer">{{ countdownDisplay }}</div>
          </div>
  
          <div class="data-grid">
            <div class="data-item">
              <span class="label">{{ $t('launchpad.ido_price') }}</span>
              <span class="value">${{ upcomingProject.price.toFixed(3) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ $t('launchpad.total_raise') }}</span>
              <span class="value">${{ formatTotalRaise(upcomingProject.targetRaise) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ $t('launchpad.ido_price') === '认购价格' ? '最少可投' : 'Min Alloc' }}</span>
              <span class="value">{{ upcomingProject.minAlloc }} USDT</span>
            </div>
          </div>
  
          <button class="action-btn secondary-btn">Set Reminder</button>
        </div>
  
         <div class="project-card ended-card">
          <div class="status-badge ended">{{ $t('launchpad.status_ended') }}</div>
          <div class="card-header">
            <div class="project-logo grey">DF</div>
            <div class="project-info">
              <h3 class="project-name">DeFi Prime <span class="ticker">DFP</span></h3>
              <div class="tags">
                <span class="tag">DeFi</span>
                <span class="tag text-green">ROI: 450%</span>
              </div>
            </div>
          </div>
          <div class="ended-info">
            Raise Completed: <span class="gold-text">$800,000</span> (100%)
          </div>
        </div>
  
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed, ref, onMounted, onUnmounted, onActivated, onDeactivated } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { showConfirmDialog, showToast } from 'vant';
  import { useAssetStore } from '@/stores/assets';

  defineOptions({
    name: 'IDO'
  });

  const { t } = useI18n();
  const assetStore = useAssetStore();

  // 格式化数字显示
  const formatNumber = (value) => {
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  // 币种池 - 备用项目数据
  const coinPool = [
    {
      name: 'NeuroChain AI',
      ticker: 'NCAI',
      logoText: 'AI',
      logoClass: '',
      tags: ['AI Infra'],
      auditor: 'Audited by CertiK',
      price: 0.045,
      targetRaise: 500000,
      minAlloc: 100,
      vesting: '20% TGE'
    },
    {
      name: 'GameMaster',
      ticker: 'GMT',
      logoText: 'GM',
      logoClass: 'blue',
      tags: ['GameFi'],
      auditor: 'SlowMist',
      price: 0.12,
      targetRaise: 1200000,
      minAlloc: 100,
      vesting: '25% TGE'
    },
    {
      name: 'DeFi Prime',
      ticker: 'DFP',
      logoText: 'DF',
      logoClass: 'grey',
      tags: ['DeFi'],
      auditor: 'CertiK',
      price: 0.08,
      targetRaise: 800000,
      minAlloc: 50,
      vesting: '30% TGE'
    },
    {
      name: 'MetaVerse Pro',
      ticker: 'MVP',
      logoText: 'MV',
      logoClass: '',
      tags: ['Metaverse'],
      auditor: 'PeckShield',
      price: 0.15,
      targetRaise: 1500000,
      minAlloc: 200,
      vesting: '20% TGE'
    },
    {
      name: 'Web3 Bridge',
      ticker: 'W3B',
      logoText: 'W3',
      logoClass: 'blue',
      tags: ['Infrastructure'],
      auditor: 'SlowMist',
      price: 0.06,
      targetRaise: 600000,
      minAlloc: 100,
      vesting: '25% TGE'
    }
  ];

  // localStorage 存储键
  const STORAGE_KEY_PROGRESS = 'truthfi_ido_progress';
  const STORAGE_KEY_CURRENT_RAISED = 'truthfi_ido_current_raised';
  const STORAGE_KEY_TARGET_TIME = 'truthfi_ido_target_time';
  const STORAGE_KEY_LIVE_PROJECT = 'truthfi_ido_live_project';
  const STORAGE_KEY_UPCOMING_PROJECT = 'truthfi_ido_upcoming_project';

  // 从 localStorage 读取或初始化进度
  const getStoredProgress = () => {
    const stored = localStorage.getItem(STORAGE_KEY_PROGRESS);
    return stored ? Number(stored) : 84;
  };

  const getStoredCurrentRaised = () => {
    const stored = localStorage.getItem(STORAGE_KEY_CURRENT_RAISED);
    return stored ? Number(stored) : 420000;
  };

  // 从 localStorage 读取或初始化倒计时目标时间
  const getStoredTargetTime = () => {
    const stored = localStorage.getItem(STORAGE_KEY_TARGET_TIME);
    if (stored) {
      return Number(stored);
    }
    // 如果没有存储，生成12小时59分55秒后的时间
    const targetTime = Date.now() + (12 * 3600 * 1000 + 59 * 60 * 1000 + 55 * 1000);
    localStorage.setItem(STORAGE_KEY_TARGET_TIME, targetTime.toString());
    return targetTime;
  };

  // 项目列表 - 使用 ref 管理
  const liveProject = ref({
    id: 1,
    name: 'NeuroChain AI',
    ticker: 'NCAI',
    logoText: 'AI',
    logoClass: '',
    tags: ['AI Infra'],
    auditor: 'Audited by CertiK',
    price: 0.045,
    minAlloc: 100,
    status: 'live',
    targetRaise: 500000,
    currentRaised: getStoredCurrentRaised(),
    progress: getStoredProgress(),
    vesting: '20% TGE',
    startTime: Date.now()
  });

  const upcomingProject = ref({
    id: 2,
    name: 'GameMaster',
    ticker: 'GMT',
    logoText: 'GM',
    logoClass: 'blue',
    tags: ['GameFi'],
    auditor: 'SlowMist',
    price: 0.12,
    minAlloc: 100,
    status: 'upcoming',
    targetRaise: 1200000,
    vesting: '25% TGE',
    startTime: getStoredTargetTime()
  });

  // 显示值（用于平滑动画）- 从存储读取
  const displayCurrentRaised = ref(getStoredCurrentRaised());
  const displayProgress = ref(getStoredProgress());

  // 当前项目信息（用于认购逻辑）
  const currentProject = computed(() => ({
    name: liveProject.value.name,
    ticker: liveProject.value.ticker,
    price: liveProject.value.price,
    minAlloc: liveProject.value.minAlloc
  }));

  // 实时成交跑马灯消息
  const liveMessage = ref('');

  // 倒计时显示
  const countdownDisplay = ref('04d : 12h : 30m');

  // 生成随机地址
  const generateRandomAddress = () => {
    return '0x' + Math.random().toString(16).substr(2, 4).toUpperCase();
  };

  // 生成随机金额
  const generateRandomAmount = () => {
    return Math.floor(Math.random() * 1900) + 100; // 100-2000 USDT
  };

  // 格式化募资金额
  const formatRaised = (value) => {
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  // 格式化总募资额
  const formatTotalRaise = (value) => {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(0) + 'K';
    }
    return value.toString();
  };

  // 平滑动画更新数值
  const animateValue = (startValue, endValue, duration = 1000) => {
    const startTime = Date.now();
    const difference = endValue - startValue;
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // 使用缓动函数（ease-out）
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + difference * easeOut;
      
      displayCurrentRaised.value = Math.floor(currentValue);
      const calculatedProgress = Math.min(
        (displayCurrentRaised.value / liveProject.value.targetRaise) * 100,
        100
      );
      displayProgress.value = calculatedProgress;
      
      // 在动画过程中也实时保存进度到 localStorage
      localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, displayCurrentRaised.value.toString());
      localStorage.setItem(STORAGE_KEY_PROGRESS, calculatedProgress.toString());
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        // 动画完成时，确保最终值已保存
        localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, displayCurrentRaised.value.toString());
        localStorage.setItem(STORAGE_KEY_PROGRESS, calculatedProgress.toString());
      }
    };
    
    animate();
  };

  // 核心联动逻辑 - 项目轮播
  const triggerProjectRotation = () => {
    // 1. 将即将开始的变成进行中
    Object.assign(liveProject.value, {
      ...upcomingProject.value,
      status: 'live',
      currentRaised: 0,
      progress: 0,
      startTime: Date.now() // 立即开始
    });
    
    // 重置显示值
    displayCurrentRaised.value = 0;
    displayProgress.value = 0;

    // 清除旧的存储并保存新的
    localStorage.setItem(STORAGE_KEY_PROGRESS, '0');
    localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, '0');

    // 2. 随机生成一个新的即将开始项目
    const availableCoins = coinPool.filter(coin => 
      coin.name !== liveProject.value.name
    );
    const nextCoin = availableCoins[Math.floor(Math.random() * availableCoins.length)];
    
    // 随机生成12-24小时后的开始时间
    const hoursUntilStart = 12 + Math.random() * 12;
    const newTargetTime = Date.now() + hoursUntilStart * 60 * 60 * 1000;
    Object.assign(upcomingProject.value, {
      ...nextCoin,
      status: 'upcoming',
      startTime: newTargetTime
    });

    // 保存新的倒计时目标时间
    localStorage.setItem(STORAGE_KEY_TARGET_TIME, newTargetTime.toString());

    showToast({
      message: `${liveProject.value.name} 认购已开始！`,
      icon: 'success',
      duration: 2000
    });
  };

  // 更新倒计时
  const updateCountdown = () => {
    if (!upcomingProject.value || upcomingProject.value.status !== 'upcoming') {
      return;
    }

    const now = Date.now();
    // 优先使用存储的目标时间，确保刷新后不变
    const storedTargetTime = localStorage.getItem(STORAGE_KEY_TARGET_TIME);
    const targetTime = storedTargetTime ? Number(storedTargetTime) : upcomingProject.value.startTime;
    
    // 如果存储的时间与项目时间不一致，同步更新
    if (targetTime !== upcomingProject.value.startTime) {
      upcomingProject.value.startTime = targetTime;
    }
    
    const diff = targetTime - now;

    if (diff <= 0) {
      // 倒计时结束，触发项目轮播
      triggerProjectRotation();
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    countdownDisplay.value = `${String(days).padStart(2, '0')}d : ${String(hours).padStart(2, '0')}h : ${String(minutes).padStart(2, '0')}m : ${String(seconds).padStart(2, '0')}s`;
  };

  // 模拟定时器
  let simulationTimer = null;
  let countdownTimer = null;
  let animationFrameId = null;

  // 启动模拟
  const startSimulation = () => {
    simulationTimer = setInterval(() => {
      // 只更新进行中的项目
      if (liveProject.value.status === 'live' && displayProgress.value < 100) {
        // 1. 更新资金（目标值）
        const increase = Math.floor(Math.random() * 1500) + 100; // 100-1600 USDT
        const newTarget = liveProject.value.currentRaised + increase;
        const maxRaised = liveProject.value.targetRaise;
        
        if (newTarget >= maxRaised) {
          // 达到100%
          liveProject.value.currentRaised = maxRaised;
          liveProject.value.progress = 100;
          
          // 保存到 localStorage
          localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, maxRaised.toString());
          localStorage.setItem(STORAGE_KEY_PROGRESS, '100');
          
          // 平滑动画到100%
          animateValue(displayCurrentRaised.value, maxRaised);
          
          // 延迟切换状态，等待动画完成
          setTimeout(() => {
            liveProject.value.status = 'ended';
            liveMessage.value = '';
            
            // 触发项目轮播
            setTimeout(() => {
              triggerProjectRotation();
            }, 2000);
          }, 1000);
        } else {
          // 更新目标值
          liveProject.value.currentRaised = newTarget;
          
          // 计算新进度
          const newProgress = (newTarget / liveProject.value.targetRaise) * 100;
          liveProject.value.progress = newProgress;
          
          // 【关键】实时保存到 localStorage
          localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, newTarget.toString());
          localStorage.setItem(STORAGE_KEY_PROGRESS, newProgress.toString());
          
          // 平滑动画更新显示值
          animateValue(displayCurrentRaised.value, newTarget);
          
          // 2. 更新跑马灯消息
          const address = generateRandomAddress();
          const amount = generateRandomAmount();
          liveMessage.value = `🚀 用户 ${address} 刚刚认购了 ${amount.toLocaleString()} USDT`;
          
          // 3秒后淡出消息
          setTimeout(() => {
            if (liveMessage.value.includes(address)) {
              liveMessage.value = '';
            }
          }, 3000);
        }
      }
    }, 3000); // 每3秒更新一次
  };

  // 启动倒计时
  const startCountdown = () => {
    updateCountdown(); // 立即更新一次
    countdownTimer = setInterval(() => {
      updateCountdown();
    }, 1000); // 每秒更新
  };

  // 停止模拟
  const stopSimulation = () => {
    if (simulationTimer) {
      clearInterval(simulationTimer);
      simulationTimer = null;
    }
    if (countdownTimer) {
      clearInterval(countdownTimer);
      countdownTimer = null;
    }
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
  };

  // 检查用户是否已经认购过该项目
  const isJoined = computed(() => {
    return assetStore.idoRecords.some(record => 
      record.name === currentProject.name || record.ticker === currentProject.ticker
    );
  });

  // 处理认购逻辑
  const handleParticipate = async () => {
    // 检查钱包连接状态
    if (!assetStore.isWalletConnected) {
      showToast({
        message: t('connect') === '连接钱包' ? '请先连接钱包' : 'Please connect wallet first',
        icon: 'fail'
      });
      return;
    }
    
    if (isJoined.value) {
      return; // 已经认购过，按钮已禁用
    }

    try {
      // 第一步：弹出确认对话框
      await showConfirmDialog({
        title: t('connect') === '连接钱包' ? '确认认购' : 'Confirm Subscription',
        message: t('connect') === '连接钱包' ? '确认认购 100 USDT？' : 'Confirm subscription for 100 USDT?',
        confirmButtonText: t('earn.confirm') || (t('connect') === '连接钱包' ? '确认' : 'Confirm'),
        cancelButtonText: t('connect') === '连接钱包' ? '取消' : 'Cancel',
        confirmButtonColor: '#FCD535'
      });

      // 第二步：用户确认后，调用 store 的 joinIDO 方法
      const success = assetStore.joinIDO(currentProject);

      // 第三步：反馈结果
      if (success) {
        showToast({
          message: t('earn.subscribe_success') || (t('connect') === '连接钱包' ? '认购成功' : 'Subscription successful'),
          icon: 'success',
          duration: 2000
        });
        // 按钮状态会自动更新（通过 isJoined computed）
      } else {
        // 检查是否已认购
        const alreadyJoined = assetStore.idoRecords.some(record => 
          record.name === currentProject.name || record.ticker === currentProject.ticker
        );
        
        if (alreadyJoined) {
          showToast({
            message: t('connect') === '连接钱包' ? '您已认购过该项目' : 'You have already subscribed to this project',
            duration: 2000
          });
        } else {
          showToast({
            message: t('earn.insufficient_balance') || (t('connect') === '连接钱包' ? '余额不足' : 'Insufficient balance'),
            duration: 2000
          });
        }
      }
    } catch (error) {
      // 用户取消了确认对话框
      // 不需要处理，静默取消
    }
  };

  // 初始化函数
  const initializePage = () => {
    startSimulation();
    startCountdown();
  };

  // 生命周期钩子
  onMounted(() => {
    initializePage();
  });

  onActivated(() => {
    // Keep-alive 激活时重新初始化
    initializePage();
  });

  onDeactivated(() => {
    // Keep-alive 停用时停止模拟
    stopSimulation();
  });

  onUnmounted(() => {
    stopSimulation();
  });
  </script>
  
  <style scoped>
  .ido-page {
    background-color: #0E0E0E;
    min-height: 100vh;
    padding: 16px;
    padding-bottom: 80px; /* 留出底部导航空间 */
    color: #fff;
  }
  
  /* 1. 头部 */
  .launchpad-header {
    margin-bottom: 24px;
  }
  .page-title {
    font-size: 28px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .gold-text { color: #FCD535; }
  .page-sub {
    color: #8E8E93;
    font-size: 13px;
    margin-top: 5px;
  }
  
  /* 2. 卡片通用样式 */
  .project-card {
    background: #1C1C1E;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
    border: 1px solid rgba(255,255,255,0.05);
  }
  
  /* 状态标签 */
  .status-badge {
    position: absolute;
    top: 16px;
    right: 16px;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .live { background: rgba(14, 203, 129, 0.2); color: #0ECB81; }
  .upcoming { background: rgba(252, 213, 53, 0.2); color: #FCD535; }
  .ended { background: #2B3139; color: #8E8E93; }
  
  /* 呼吸灯效果 - 优化版 */
  .pulse-dot {
    width: 6px; height: 6px;
    background-color: #0ECB81;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(14, 203, 129, 0.7); }
    70% { box-shadow: 0 0 0 6px rgba(14, 203, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(14, 203, 129, 0); }
  }

  /* LIVE 标签呼吸灯动画 */
  .status-live {
    animation: statusPulse 2s infinite;
  }

  @keyframes statusPulse {
    0% { box-shadow: 0 0 0 0 rgba(14, 203, 129, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(14, 203, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(14, 203, 129, 0); }
  }

  /* 实时成交跑马灯 */
  .live-ticker {
    margin-bottom: 12px;
    padding: 8px 12px;
    background: rgba(14, 203, 129, 0.1);
    border-radius: 6px;
    border: 1px solid rgba(14, 203, 129, 0.2);
    overflow: hidden;
    position: relative;
  }

  .ticker-content {
    font-size: 12px;
    color: #0ECB81;
    white-space: nowrap;
    animation: tickerFade 3s ease-in-out infinite;
    font-weight: 500;
  }

  @keyframes tickerFade {
    0% { opacity: 0; transform: translateX(10px); }
    20% { opacity: 1; transform: translateX(0); }
    80% { opacity: 1; transform: translateX(0); }
    100% { opacity: 0; transform: translateX(-10px); }
  }
  
  /* 头部信息 */
  .card-header {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }
  .project-logo {
    width: 48px; height: 48px;
    background: #FCD535; color: #000;
    border-radius: 12px;
    display: flex; justify-content: center; align-items: center;
    font-weight: 900; font-size: 16px;
  }
  .project-logo.blue { background: #627EEA; color: #fff; }
  .project-logo.grey { background: #2B3139; color: #8E8E93; }
  
  .project-info {
    display: flex; flex-direction: column; justify-content: center;
  }
  .project-name {
    font-size: 16px; margin: 0 0 6px 0; font-weight: 700;
  }
  .ticker {
    font-size: 12px; color: #8E8E93; font-weight: 400; margin-left: 4px;
  }
  .tags { display: flex; gap: 6px; }
  .tag {
    font-size: 9px; padding: 2px 6px; background: #2B3139; color: #8E8E93;
    border-radius: 3px;
  }
  .audit-tag {
    background: rgba(14, 203, 129, 0.1); color: #0ECB81;
    display: flex; align-items: center; gap: 3px;
  }
  
  /* 进度条 */
  .progress-section { margin-bottom: 20px; }
  .progress-info {
    display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; color: #EAECEF;
  }
  .progress-bar-bg {
    width: 100%; height: 6px; background: #2B3139; border-radius: 3px; overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%; background: #FCD535; border-radius: 3px;
    transition: width 1s ease-out;
  }
  .raise-detail {
    font-size: 10px; color: #5E5E5E; text-align: right; margin-top: 4px; font-family: monospace;
  }
  
  /* 数据网格 */
  .data-grid {
    display: flex; justify-content: space-between;
    margin-bottom: 20px; background: #161A1E; padding: 12px; border-radius: 8px;
  }
  .data-item { display: flex; flex-direction: column; gap: 4px; }
  .label { font-size: 10px; color: #8E8E93; }
  .value { font-size: 13px; font-weight: 600; color: #EAECEF; }
  .highlight { color: #FCD535; }
  
  /* 倒计时 */
  .countdown-box {
    background: rgba(252, 213, 53, 0.05);
    padding: 12px; border-radius: 8px; text-align: center;
    margin-bottom: 20px; border: 1px dashed rgba(252, 213, 53, 0.3);
  }
  .countdown-box p { margin: 0 0 4px 0; font-size: 10px; color: #FCD535; }
  .timer { font-family: 'DIN Alternate', monospace; font-size: 16px; font-weight: 700; color: #fff; }
  
  /* 按钮 */
  .action-btn {
    width: 100%; padding: 12px; border: none; border-radius: 8px;
    font-weight: 600; font-size: 14px; cursor: pointer;
    transition: all 0.3s ease;
  }
  .primary-btn { background: var(--color-brand); color: #000; border-radius: var(--radius-button); }
  .primary-btn:active { opacity: 0.8; }
  .secondary-btn { background: #2B3139; color: #fff; }
  .secondary-btn:active { background: #363c45; }
  .joined-btn {
    background: #2B3139;
    color: #8E8E93;
    cursor: not-allowed;
    opacity: 0.6;
  }
  .joined-btn:disabled {
    opacity: 0.6;
  }
  .disabled-btn {
    background: #2B3139;
    color: #8E8E93;
    cursor: not-allowed;
    opacity: 0.6;
  }
  .disabled-btn:disabled {
    opacity: 0.6;
  }
  .wallet-notice {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 10px;
    background: rgba(252, 213, 53, 0.1);
    border-radius: 8px;
    font-size: 12px;
    color: #FCD535;
  }
  .wallet-notice .van-icon {
    font-size: 14px;
  }
  
  .ended-card { opacity: 0.7; }
  .ended-info { font-size: 12px; color: #8E8E93; margin-top: 10px; }
  .text-green { color: #0ECB81; }

  /* My Assets Card */
  .assets-card {
    background: #1C1C1E;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.05);
  }
  .assets-title {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 16px 0;
  }
  .assets-grid {
    display: flex;
    gap: 16px;
  }
  .asset-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    background: #161A1E;
    border-radius: 8px;
  }
  .asset-label {
    font-size: 11px;
    color: #8E8E93;
    font-weight: 500;
  }
  .asset-value {
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF;
    font-family: 'DIN Alternate', sans-serif;
    font-variant-numeric: tabular-nums;
  }
  .asset-value.gold-text {
    color: #FCD535;
  }
  </style>