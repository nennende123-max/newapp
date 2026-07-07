<template>
  <div class="ido-page">
      <div class="launchpad-toolbar">
        <van-field
          v-model="searchQuery"
          left-icon="search"
          clearable
          class="launchpad-search"
          placeholder="搜索项目 / Search"
        />
        <div class="status-filters">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            :class="{ active: activeStatusFilter === filter.value }"
            @click="activeStatusFilter = filter.value"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>
      <div class="project-list">
        
        <!-- 杩涜涓」鐩?-->
        <div v-if="liveProject && projectVisible(liveProject)" class="project-card live-card clickable-card" @click="openSubscribePage(liveProject)">
          <div class="status-badge live status-live">
            <span class="pulse-dot"></span> {{ t('launchpad.status_live') }}
          </div>
  
          <div class="card-header">
            <div class="project-logo" :class="liveProject.logoClass">{{ liveProject.logoText }}</div>
            <div class="project-info">
              <h3 class="project-name">{{ liveProject.name }}</h3>
              <div class="token-symbol">{{ liveProject.ticker }}</div>
              <div class="tag-groups">
                <div class="category-tags">
                  <span class="tag category-tag" v-for="tag in liveProject.tags" :key="tag">{{ tag }}</span>
                </div>
                <div v-if="liveProject.performanceTags?.length" class="performance-tags">
                  <span class="tag performance-tag" v-for="tag in liveProject.performanceTags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 瀹炴椂鎴愪氦璺戦┈鐏?-->
          <div v-if="liveMessage" class="live-ticker">
            <div class="ticker-content">{{ liveMessage }}</div>
          </div>
  
          <div class="progress-section">
            <div class="progress-info">
              <span>{{ t('launchpad.progress') }}</span>
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
              <span class="label">{{ t('launchpad.ido_price') }}</span>
              <span class="value">${{ liveProject.price.toFixed(3) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ t('launchpad.total_raise') }}</span>
              <span class="value">${{ formatTotalRaise(liveProject.targetRaise) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ t('launchpad.participants') }}</span>
              <span class="value highlight participant-value">{{ formatInteger(displayParticipants) }}</span>
            </div>
          </div>
  
          <button 
            class="action-btn"
            :class="isJoined ? 'joined-btn' : 'primary-btn'"
            :disabled="isJoined"
            @click.stop="openSubscribePage(liveProject)"
          >
            <span>{{ isJoined ? t('launchpad.joined') : t('launchpad.subscribe_now') }}</span>
          </button>
        </div>
  
        <!-- 鍗冲皢寮€濮嬮」鐩?-->
        <div v-if="upcomingProject && projectVisible(upcomingProject)" class="project-card upcoming-card">
          <div class="status-badge upcoming">
            <van-icon name="clock" /> {{ t('launchpad.status_upcoming') }}
          </div>
  
          <div class="card-header">
            <div class="project-logo" :class="upcomingProject.logoClass">{{ upcomingProject.logoText }}</div>
            <div class="project-info">
              <h3 class="project-name">{{ upcomingProject.name }}</h3>
              <div class="token-symbol">{{ upcomingProject.ticker }}</div>
              <div class="tag-groups">
                <div class="category-tags">
                  <span class="tag category-tag" v-for="tag in upcomingProject.tags" :key="tag">{{ tag }}</span>
                </div>
                <div v-if="upcomingProject.performanceTags?.length" class="performance-tags">
                  <span class="tag performance-tag" v-for="tag in upcomingProject.performanceTags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </div>
          </div>
  
          <div class="countdown-box">
            <p>{{ t('launchpad.subscription_starts_in') }}</p>
            <div class="timer">{{ countdownDisplay }}</div>
          </div>
  
          <div class="data-grid">
            <div class="data-item">
              <span class="label">{{ t('launchpad.ido_price') }}</span>
              <span class="value">${{ upcomingProject.price.toFixed(3) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ t('launchpad.total_raise') }}</span>
              <span class="value">${{ formatTotalRaise(upcomingProject.targetRaise) }}</span>
            </div>
            <div class="data-item">
              <span class="label">{{ t('launchpad.min_alloc') }}</span>
              <span class="value">{{ upcomingProject.minAlloc }} USDT</span>
            </div>
          </div>
  
          <button class="action-btn secondary-btn" @click="handleReminder">{{ t('launchpad.set_reminder') }}</button>
        </div>
  
         <div v-if="projectVisible(endedProject)" class="project-card ended-card">
          <div class="status-badge ended">{{ t('launchpad.status_ended') }}</div>
          <div class="card-header">
            <div class="project-logo grey">DF</div>
            <div class="project-info">
              <h3 class="project-name">DeFi Prime</h3>
              <div class="token-symbol">DFP</div>
              <div class="tag-groups">
                <div class="category-tags">
                  <span class="tag category-tag">DeFi</span>
                </div>
                <div class="performance-tags">
                  <span class="tag performance-tag success">ROI: 450%</span>
                </div>
              </div>
            </div>
          </div>
          <div class="ended-info">
            {{ t('launchpad.raise_completed') }}: <span class="gold-text">$800,000</span> (100%)
          </div>
        </div>
  
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed, ref, onMounted, onUnmounted, onActivated, onDeactivated } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { showToast } from 'vant';
  import { useAssetStore } from '@/stores/assets';
  import { useRouter } from 'vue-router';
  import { formatInteger, formatNumber } from '@/utils/format';

  defineOptions({
    name: 'IDO'
  });

  const { t } = useI18n();
  const assetStore = useAssetStore();
  const router = useRouter();
  const searchQuery = ref('');
  const activeStatusFilter = ref('all');
  const statusFilters = computed(() => [
    { label: t('launchpad.filter_all'), value: 'all' },
    { label: t('launchpad.status_upcoming'), value: 'upcoming' },
    { label: t('launchpad.status_live'), value: 'live' },
    { label: t('launchpad.status_ended'), value: 'ended' }
  ]);
  const toFiniteNumber = (value, fallback = 0) => {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  };

  const asArray = (value) => Array.isArray(value) ? value : [];

  // 甯佺姹?- 澶囩敤椤圭洰鏁版嵁
  const coinPool = [
    {
      name: 'NeuroChain AI',
      ticker: 'NCAI',
      logoText: 'AI',
      logoClass: '',
      tags: ['AI Infra'],
      performanceTags: ['APY: 18%', 'Rewards Boost: +12%'],
      price: 0.045,
      targetRaise: 500000,
      minAlloc: 100,
      participantsBase: 18000
    },
    {
      name: 'GameMaster',
      ticker: 'GMT',
      logoText: 'GM',
      logoClass: 'blue',
      tags: ['GameFi'],
      performanceTags: ['ROI: 320%'],
      price: 0.12,
      targetRaise: 1200000,
      minAlloc: 100,
      participantsBase: 18000
    },
    {
      name: 'DeFi Prime',
      ticker: 'DFP',
      logoText: 'DF',
      logoClass: 'grey',
      tags: ['DeFi'],
      performanceTags: ['ROI: 450%'],
      price: 0.08,
      targetRaise: 800000,
      minAlloc: 50,
      participantsBase: 18000
    },
    {
      name: 'MetaVerse Pro',
      ticker: 'MVP',
      logoText: 'MV',
      logoClass: '',
      tags: ['NFT'],
      performanceTags: ['Rewards Boost: +18%'],
      price: 0.15,
      targetRaise: 1500000,
      minAlloc: 200,
      participantsBase: 18000
    },
    {
      name: 'Web3 Bridge',
      ticker: 'W3B',
      logoText: 'W3',
      logoClass: 'blue',
      tags: ['Layer2', 'DeFi'],
      performanceTags: ['APY: 15%'],
      price: 0.06,
      targetRaise: 600000,
      minAlloc: 100,
      participantsBase: 18000
    }
  ];

  // localStorage 瀛樺偍閿?
  const STORAGE_KEY_PROGRESS = 'truthfi_ido_progress';
  const STORAGE_KEY_CURRENT_RAISED = 'truthfi_ido_current_raised';
  const STORAGE_KEY_TARGET_TIME = 'truthfi_ido_target_time';
  const STORAGE_KEY_LIVE_PROJECT = 'truthfi_ido_live_project';
  const STORAGE_KEY_UPCOMING_PROJECT = 'truthfi_ido_upcoming_project';

  // 浠?localStorage 璇诲彇鎴栧垵濮嬪寲杩涘害
  const getStoredProgress = () => {
    const stored = localStorage.getItem(STORAGE_KEY_PROGRESS);
    return stored ? toFiniteNumber(stored, 84) : 84;
  };

  const getRaisedFromProgress = (targetRaise, progress) => {
    return Math.round(toFiniteNumber(targetRaise) * toFiniteNumber(progress) / 100);
  };

  const getStoredCurrentRaised = () => getRaisedFromProgress(500000, getStoredProgress());

  // 浠?localStorage 璇诲彇鎴栧垵濮嬪寲鍊掕鏃剁洰鏍囨椂闂?
  const getStoredTargetTime = () => {
    const stored = localStorage.getItem(STORAGE_KEY_TARGET_TIME);
    if (stored) {
      return toFiniteNumber(stored, Date.now());
    }
    // 濡傛灉娌℃湁瀛樺偍锛岀敓鎴?2灏忔椂59鍒?5绉掑悗鐨勬椂闂?
    const targetTime = Date.now() + (12 * 3600 * 1000 + 59 * 60 * 1000 + 55 * 1000);
    localStorage.setItem(STORAGE_KEY_TARGET_TIME, targetTime.toString());
    return targetTime;
  };

  // 椤圭洰鍒楄〃 - 浣跨敤 ref 绠＄悊
  const liveProject = ref({
    id: 1,
    name: 'NeuroChain AI',
    ticker: 'NCAI',
    logoText: 'AI',
    logoClass: '',
    tags: ['AI Infra'],
    performanceTags: ['APY: 18%', 'Rewards Boost: +12%'],
    price: 0.045,
    minAlloc: 100,
    status: 'live',
    targetRaise: 500000,
    currentRaised: getStoredCurrentRaised(),
    progress: getStoredProgress(),
    participantsBase: 18000,
    startTime: Date.now()
  });

  const upcomingProject = ref({
    id: 2,
    name: 'GameMaster',
    ticker: 'GMT',
    logoText: 'GM',
    logoClass: 'blue',
    tags: ['GameFi'],
    performanceTags: ['ROI: 320%'],
    price: 0.12,
    minAlloc: 100,
    status: 'upcoming',
    targetRaise: 1200000,
    participantsBase: 18000,
    startTime: getStoredTargetTime()
  });

  const endedProject = {
    id: 3,
    name: 'DeFi Prime',
    ticker: 'DFP',
    status: 'ended',
    tags: ['DeFi']
  };

  const projectVisible = (project) => {
    if (!project) return false;
    const keyword = searchQuery.value.trim().toLowerCase();
    const statusMatched = activeStatusFilter.value === 'all' || project.status === activeStatusFilter.value;
    if (!statusMatched) return false;
    if (!keyword) return true;
    return [project.name, project.ticker, ...(project.tags || [])]
      .filter(Boolean)
      .some(item => String(item).toLowerCase().includes(keyword));
  };

  // 鏄剧ず鍊硷紙鐢ㄤ簬骞虫粦鍔ㄧ敾锛? 浠庡瓨鍌ㄨ鍙?
  const displayCurrentRaised = ref(getStoredCurrentRaised());
  const displayProgress = ref(getStoredProgress());
  const PARTICIPANT_MULTIPLIER = 1500;
  const calculateParticipants = (progress, base = 18000) => {
    return Math.round(toFiniteNumber(base, 18000) + (toFiniteNumber(progress) / 100) * PARTICIPANT_MULTIPLIER);
  };
  const displayParticipants = computed(() => calculateParticipants(displayProgress.value, liveProject.value.participantsBase));

  // 褰撳墠椤圭洰淇℃伅锛堢敤浜庤璐€昏緫锛?
  const currentProject = computed(() => ({
    name: liveProject.value.name,
    ticker: liveProject.value.ticker,
    price: liveProject.value.price,
    minAlloc: liveProject.value.minAlloc
  }));

  const liveTickerEvent = ref(null);
  const liveMessage = computed(() => {
    if (!liveTickerEvent.value) return '';
    return t('launchpad.ticker_subscribed', liveTickerEvent.value);
  });

  // 鍊掕鏃舵樉绀?
  const countdownDisplay = ref('04d : 12h : 30m');

  // 鐢熸垚闅忔満鍦板潃
  const generateRandomAddress = () => {
    return '0x' + Math.random().toString(16).substr(2, 4).toUpperCase();
  };

  // 鐢熸垚闅忔満閲戦
  const generateRandomAmount = () => {
    return Math.floor(Math.random() * 1900) + 100; // 100-2000 USDT
  };

  // 鏍煎紡鍖栧嫙璧勯噾棰?
  const formatRaised = (value) => {
    return toFiniteNumber(value).toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  // 鏍煎紡鍖栨€诲嫙璧勯
  const formatTotalRaise = (value) => {
    const amount = toFiniteNumber(value);
    if (amount >= 1000000) {
      return (amount / 1000000).toFixed(1) + 'M';
    } else if (amount >= 1000) {
      return (amount / 1000).toFixed(0) + 'K';
    }
    return amount.toString();
  };

  // 骞虫粦鍔ㄧ敾鏇存柊鏁板€?
  const animateValue = (startValue, endValue, duration = 1000) => {
    const startTime = Date.now();
    const difference = endValue - startValue;
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // 浣跨敤缂撳姩鍑芥暟锛坋ase-out锛?
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + difference * easeOut;
      
      displayCurrentRaised.value = Math.floor(currentValue);
      const targetRaise = toFiniteNumber(liveProject.value.targetRaise, 1);
      const calculatedProgress = Math.min((displayCurrentRaised.value / targetRaise) * 100, 100);
      displayProgress.value = calculatedProgress;
      liveProject.value.progress = calculatedProgress;
      liveProject.value.currentRaised = displayCurrentRaised.value;
      
      // 鍦ㄥ姩鐢昏繃绋嬩腑涔熷疄鏃朵繚瀛樿繘搴﹀埌 localStorage
      localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, displayCurrentRaised.value.toString());
      localStorage.setItem(STORAGE_KEY_PROGRESS, calculatedProgress.toString());
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        // 鍔ㄧ敾瀹屾垚鏃讹紝纭繚鏈€缁堝€煎凡淇濆瓨
        localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, displayCurrentRaised.value.toString());
        localStorage.setItem(STORAGE_KEY_PROGRESS, calculatedProgress.toString());
      }
    };
    
    animate();
  };

  // 鏍稿績鑱斿姩閫昏緫 - 椤圭洰杞挱
  const triggerProjectRotation = () => {
    // 1. 灏嗗嵆灏嗗紑濮嬬殑鍙樻垚杩涜涓?
    Object.assign(liveProject.value, {
      ...upcomingProject.value,
      status: 'live',
      currentRaised: 0,
      progress: 0,
      startTime: Date.now() // 绔嬪嵆寮€濮?
    });
    
    // 閲嶇疆鏄剧ず鍊?
    displayCurrentRaised.value = 0;
    displayProgress.value = 0;

    // 娓呴櫎鏃х殑瀛樺偍骞朵繚瀛樻柊鐨?
    localStorage.setItem(STORAGE_KEY_PROGRESS, '0');
    localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, '0');

    // 2. 闅忔満鐢熸垚涓€涓柊鐨勫嵆灏嗗紑濮嬮」鐩?
    const availableCoins = coinPool.filter(coin => 
      coin.name !== liveProject.value.name
    );
    const nextCoin = availableCoins[Math.floor(Math.random() * availableCoins.length)];
    
    // 闅忔満鐢熸垚12-24灏忔椂鍚庣殑寮€濮嬫椂闂?
    const hoursUntilStart = 12 + Math.random() * 12;
    const newTargetTime = Date.now() + hoursUntilStart * 60 * 60 * 1000;
    Object.assign(upcomingProject.value, {
      ...nextCoin,
      status: 'upcoming',
      startTime: newTargetTime
    });

    // 淇濆瓨鏂扮殑鍊掕鏃剁洰鏍囨椂闂?
    localStorage.setItem(STORAGE_KEY_TARGET_TIME, newTargetTime.toString());

    showToast({
      message: t('launchpad.subscription_started', { project: liveProject.value.name }),
      icon: 'success',
      duration: 2000
    });
  };

  // 鏇存柊鍊掕鏃?
  const updateCountdown = () => {
    if (!upcomingProject.value || upcomingProject.value.status !== 'upcoming') {
      return;
    }

    const now = Date.now();
    // 浼樺厛浣跨敤瀛樺偍鐨勭洰鏍囨椂闂达紝纭繚鍒锋柊鍚庝笉鍙?
    const storedTargetTime = localStorage.getItem(STORAGE_KEY_TARGET_TIME);
    const targetTime = storedTargetTime ? Number(storedTargetTime) : upcomingProject.value.startTime;
    
    // 濡傛灉瀛樺偍鐨勬椂闂翠笌椤圭洰鏃堕棿涓嶄竴鑷达紝鍚屾鏇存柊
    if (targetTime !== upcomingProject.value.startTime) {
      upcomingProject.value.startTime = targetTime;
    }
    
    const diff = targetTime - now;

    if (diff <= 0) {
      // 鍊掕鏃剁粨鏉燂紝瑙﹀彂椤圭洰杞挱
      triggerProjectRotation();
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    countdownDisplay.value = `${String(days).padStart(2, '0')}d : ${String(hours).padStart(2, '0')}h : ${String(minutes).padStart(2, '0')}m : ${String(seconds).padStart(2, '0')}s`;
  };

  // 妯℃嫙瀹氭椂鍣?
  let simulationTimer = null;
  let countdownTimer = null;
  let animationFrameId = null;

  // 鍚姩妯℃嫙
  const startSimulation = () => {
    simulationTimer = setInterval(() => {
      // 鍙洿鏂拌繘琛屼腑鐨勯」鐩?
      if (liveProject.value.status === 'live' && displayProgress.value < 100) {
        // 1. 鏇存柊璧勯噾锛堢洰鏍囧€硷級
        const increase = Math.floor(Math.random() * 1500) + 100; // 100-1600 USDT
        const newTarget = liveProject.value.currentRaised + increase;
        const maxRaised = liveProject.value.targetRaise;
        
        if (newTarget >= maxRaised) {
          // 杈惧埌100%
          liveProject.value.currentRaised = maxRaised;
          liveProject.value.progress = 100;
          
          // 淇濆瓨鍒?localStorage
          localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, maxRaised.toString());
          localStorage.setItem(STORAGE_KEY_PROGRESS, '100');
          
          // 骞虫粦鍔ㄧ敾鍒?00%
          animateValue(displayCurrentRaised.value, maxRaised);
          
          // 寤惰繜鍒囨崲鐘舵€侊紝绛夊緟鍔ㄧ敾瀹屾垚
          setTimeout(() => {
            liveProject.value.status = 'ended';
            liveTickerEvent.value = null;
            
            // 瑙﹀彂椤圭洰杞挱
            setTimeout(() => {
              triggerProjectRotation();
            }, 2000);
          }, 1000);
        } else {
          // 鏇存柊鐩爣鍊?
          liveProject.value.currentRaised = newTarget;
          
          // 璁＄畻鏂拌繘搴?
          const newProgress = (newTarget / liveProject.value.targetRaise) * 100;
          liveProject.value.progress = newProgress;
          
          // 銆愬叧閿€戝疄鏃朵繚瀛樺埌 localStorage
          localStorage.setItem(STORAGE_KEY_CURRENT_RAISED, newTarget.toString());
          localStorage.setItem(STORAGE_KEY_PROGRESS, newProgress.toString());
          
          // 骞虫粦鍔ㄧ敾鏇存柊鏄剧ず鍊?
          animateValue(displayCurrentRaised.value, newTarget);
          
          // 2. 鏇存柊璺戦┈鐏秷鎭?
          const address = generateRandomAddress();
          const amount = generateRandomAmount();
          liveTickerEvent.value = {
            user: address,
            amount: amount.toLocaleString('en-US')
          };
          
          // 3绉掑悗娣″嚭娑堟伅
          setTimeout(() => {
            if (liveTickerEvent.value?.user === address) {
              liveTickerEvent.value = null;
            }
          }, 3000);
        }
      }
    }, 3000); // 姣?绉掓洿鏂颁竴娆?
  };

  // 鍚姩鍊掕鏃?
  const startCountdown = () => {
    updateCountdown(); // 绔嬪嵆鏇存柊涓€娆?
    countdownTimer = setInterval(() => {
      updateCountdown();
    }, 1000); // 姣忕鏇存柊
  };

  // 鍋滄妯℃嫙
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

  // 妫€鏌ョ敤鎴锋槸鍚﹀凡缁忚璐繃璇ラ」鐩?
  const isJoined = computed(() => {
    return asArray(assetStore.idoRecords).some(record => 
      record.name === currentProject.value.name || record.ticker === currentProject.value.ticker
    );
  });

  // 澶勭悊璁よ喘閫昏緫
  const openSubscribePage = (project) => {
    if (!project) return;
    const tags = asArray(project.tags);
    const performanceTags = asArray(project.performanceTags);
    const price = Math.max(0.000001, toFiniteNumber(project.price, 0.045));
    const targetRaise = toFiniteNumber(project.targetRaise, 500000);
    const progress = toFiniteNumber(project.progress, displayProgress.value);
    const currentRaised = toFiniteNumber(project.currentRaised, displayCurrentRaised.value);
    router.push({
      path: '/ido/subscribe',
      query: {
        name: project.name || 'Launchpad Project',
        ticker: project.ticker || 'GMT',
        logoText: project.logoText || 'LP',
        tags: tags.join(','),
        performanceTags: performanceTags.join(','),
        price,
        targetRaise,
        minAlloc: toFiniteNumber(project.minAlloc, 100),
        progress,
        raised: currentRaised,
        participants: calculateParticipants(progress, project.participantsBase),
        tokenSupply: Math.floor(targetRaise / price)
      }
    });
  };

  const handleParticipate = () => {
    openSubscribePage(liveProject.value);
  };

  const handleReminder = () => {
    showToast({
      message: t('launchpad.reminder_enabled'),
      icon: 'success',
      duration: 1800
    });
  };

  // 鍒濆鍖栧嚱鏁?
  const initializePage = () => {
    stopSimulation();
    startSimulation();
    startCountdown();
  };

  // 鐢熷懡鍛ㄦ湡閽╁瓙
  onMounted(() => {
    initializePage();
  });

  onActivated(() => {
    // Keep-alive 婵€娲绘椂閲嶆柊鍒濆鍖?
    initializePage();
  });

  onDeactivated(() => {
    // Keep-alive 鍋滅敤鏃跺仠姝㈡ā鎷?
    stopSimulation();
  });

  onUnmounted(() => {
    stopSimulation();
  });
  </script>
  
  <style scoped>
  .ido-page {
    background-color: var(--color-bg);
    min-height: 100vh;
    padding: 16px;
    padding-bottom: 80px; /* 鐣欏嚭搴曢儴瀵艰埅绌洪棿 */
    color: var(--color-text-primary);
  }
  
  .gold-text { color: var(--color-brand-legacy); }

  .launchpad-toolbar {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;
  }

  .launchpad-search {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgb(var(--color-border-rgb) / 0.08);
    background: var(--color-bg-card);
  }

  .status-filters {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
  }

  .status-filters button {
    height: 32px;
    border: 1px solid rgb(var(--color-border-rgb) / 0.08);
    border-radius: 999px;
    background: var(--color-bg-card);
    color: var(--color-text-secondary);
    font-size: 12px;
    font-weight: 700;
  }

  .status-filters button.active {
    color: var(--color-text-primary);
    background: rgb(var(--color-brand-rgb) / 0.12);
    border-color: rgb(var(--color-brand-rgb) / 0.25);
  }

  /* 2. 鍗＄墖閫氱敤鏍峰紡 */
  .project-card {
    background: var(--color-bg-card);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
    border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  }
  
  /* 鐘舵€佹爣绛?*/
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
  .live { background: rgb(var(--color-earn-rgb) / 0.2); color: var(--color-earn); }
  .upcoming { background: rgb(var(--color-brand-legacy-rgb) / 0.2); color: var(--color-brand-legacy); }
  .ended { background: var(--color-surface-muted); color: var(--color-text-secondary); }
  
  /* 鍛煎惛鐏晥鏋?- 浼樺寲鐗?*/
  .pulse-dot {
    width: 6px; height: 6px;
    background-color: var(--color-earn);
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgb(var(--color-earn-rgb) / 0.7); }
    70% { box-shadow: 0 0 0 6px rgb(var(--color-earn-rgb) / 0); }
    100% { box-shadow: 0 0 0 0 rgb(var(--color-earn-rgb) / 0); }
  }

  /* LIVE 鏍囩鍛煎惛鐏姩鐢?*/
  .status-live {
    animation: statusPulse 2s infinite;
  }

  @keyframes statusPulse {
    0% { box-shadow: 0 0 0 0 rgb(var(--color-earn-rgb) / 0.4); }
    70% { box-shadow: 0 0 0 10px rgb(var(--color-earn-rgb) / 0); }
    100% { box-shadow: 0 0 0 0 rgb(var(--color-earn-rgb) / 0); }
  }

  /* 瀹炴椂鎴愪氦璺戦┈鐏?*/
  .live-ticker {
    margin-bottom: 12px;
    padding: 8px 12px;
    background: rgb(var(--color-earn-rgb) / 0.1);
    border-radius: 6px;
    border: 1px solid rgb(var(--color-earn-rgb) / 0.2);
    overflow: hidden;
    position: relative;
  }

  .ticker-content {
    font-size: 12px;
    color: var(--color-earn);
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
  
  /* 澶撮儴淇℃伅 */
  .card-header {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 20px;
  }
  .project-logo {
    width: 48px; height: 48px;
    background: var(--color-brand-legacy); color: var(--color-text-on-accent);
    border-radius: 12px;
    display: flex; justify-content: center; align-items: center;
    font-weight: 900; font-size: 16px;
  }
  .project-logo.blue { background: var(--color-coin-eth); color: var(--color-text-primary); }
  .project-logo.grey { background: var(--color-surface-muted); color: var(--color-text-secondary); }
  
  .project-info {
    display: flex; flex-direction: column; justify-content: center;
    min-width: 0;
    flex: 1;
  }
  .project-name {
    font-size: 16px; margin: 0 0 6px 0; font-weight: 700;
  }
  .ticker {
    font-size: 12px; color: var(--color-text-secondary); font-weight: 400; margin-left: 4px;
  }
  .token-symbol {
    width: fit-content;
    margin: -2px 0 6px;
    color: var(--color-text-secondary);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
  .tag-groups {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .category-tags,
  .performance-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .tag {
    width: fit-content;
    font-size: 9px;
    line-height: 1;
    padding: 4px 7px;
    border-radius: 999px;
    font-weight: 700;
  }
  .category-tag {
    background: var(--color-surface-muted);
    color: var(--color-text-secondary);
    border: 1px solid var(--color-border-subtle);
  }
  .performance-tag {
    background: rgb(var(--color-primary-rgb) / 0.12);
    color: var(--color-primary-hover);
    border: 1px solid rgb(var(--color-primary-rgb) / 0.22);
  }
  .performance-tag.success {
    background: rgb(var(--color-success-rgb) / 0.1);
    color: var(--color-success);
    border-color: rgb(var(--color-success-rgb) / 0.2);
  }
  
  /* 杩涘害鏉?*/
  .progress-section { margin-bottom: 20px; }
  .progress-info {
    display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; color: var(--color-text-primary);
  }
  .progress-bar-bg {
    width: 100%; height: 6px; background: var(--color-surface-muted); border-radius: 3px; overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%; background: var(--color-brand-legacy); border-radius: 3px;
    transition: width 1s ease-out;
  }
  .raise-detail {
    font-size: 10px; color: var(--color-text-muted); text-align: right; margin-top: 4px; font-family: monospace;
  }
  
  /* 鏁版嵁缃戞牸 */
  .data-grid {
    display: flex; justify-content: space-between;
    margin-bottom: 20px; background: var(--color-bg-elevated); padding: 12px; border-radius: 8px;
  }
  .data-item { display: flex; flex-direction: column; gap: 4px; }
  .label { font-size: 10px; color: var(--color-text-secondary); }
  .value { font-size: 13px; font-weight: 600; color: var(--color-text-primary); }
  .highlight { color: var(--color-brand-legacy); }
  
  /* 鍊掕鏃?*/
  .countdown-box {
    background: rgb(var(--color-brand-legacy-rgb) / 0.05);
    padding: 12px; border-radius: 8px; text-align: center;
    margin-bottom: 20px; border: 1px dashed rgb(var(--color-brand-legacy-rgb) / 0.3);
  }
  .countdown-box p { margin: 0 0 4px 0; font-size: 10px; color: var(--color-brand-legacy); }
  .timer { font-family: 'DIN Alternate', monospace; font-size: 16px; font-weight: 700; color: var(--color-text-primary); }
  
  /* 鎸夐挳 */
  .action-btn {
    width: 100%; padding: 12px; border: none; border-radius: 8px;
    font-weight: 600; font-size: 14px; cursor: pointer;
    transition: all 0.3s ease;
  }
  .primary-btn { background: var(--color-brand); color: var(--color-text-on-accent); border-radius: var(--radius-button); }
  .primary-btn:active { opacity: 0.8; }
  .secondary-btn { background: var(--color-surface-muted); color: var(--color-text-primary); }
  .secondary-btn:active { background: var(--color-surface-muted); }
  .joined-btn {
    background: var(--color-surface-muted);
    color: var(--color-text-secondary);
    cursor: not-allowed;
    opacity: 0.6;
  }
  .joined-btn:disabled {
    opacity: 0.6;
  }
  .disabled-btn {
    background: var(--color-surface-muted);
    color: var(--color-text-secondary);
    cursor: not-allowed;
    opacity: 0.6;
  }
  .disabled-btn:disabled {
    opacity: 0.6;
  }
  .ended-card { opacity: 0.7; }
  .ended-info { font-size: 12px; color: var(--color-text-secondary); margin-top: 10px; }
  .text-green { color: var(--color-earn); }

  .project-card.clickable-card {
    cursor: pointer;
  }

  .project-card.clickable-card:active {
    transform: translateY(1px);
  }

  /* Subscription product polish */
  .ido-page {
    background:
      linear-gradient(180deg, rgb(var(--color-primary-rgb) / 0.07) 0, rgb(var(--color-primary-rgb) / 0) 220px),
      var(--color-surface-1);
  }

  .project-card {
    background: var(--color-surface-2);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-md);
    border-radius: 18px;
  }

  .status-badge {
    border-radius: 999px;
    padding: 8px 12px;
  }

  .live {
    background: rgb(var(--color-success-rgb) / 0.12);
    color: var(--color-success);
    border: 1px solid rgb(var(--color-success-rgb) / 0.18);
  }

  .upcoming {
    background: rgb(var(--color-warning-rgb) / 0.12);
    color: var(--color-warning);
    border: 1px solid rgb(var(--color-warning-rgb) / 0.18);
  }

  .project-logo {
    border-radius: 14px;
    box-shadow: inset 0 -1px 0 rgb(var(--color-shadow-rgb) / 0.12);
  }

  .project-name {
    font-size: 18px;
    color: var(--color-text-primary);
  }

  .category-tag {
    background: var(--color-surface-1);
    border-color: var(--color-border);
  }

  .progress-bar-bg {
    height: 7px;
    background: var(--color-surface-muted);
  }

  .progress-bar-fill {
    background: linear-gradient(90deg, var(--color-primary-hover), var(--color-primary));
  }

  .data-grid {
    background: var(--color-surface-1);
    border: 1px solid var(--color-border-subtle);
    border-radius: 14px;
    padding: 14px 16px;
  }

  .action-btn {
    min-height: 50px;
    border-radius: 12px;
    font-weight: 800;
  }

  .primary-btn {
    background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
    color: var(--color-text-on-accent);
    border: 1px solid rgb(var(--color-primary-rgb) / 0.42);
    box-shadow: 0 10px 22px rgb(var(--color-primary-rgb) / 0.2);
  }

  .secondary-btn {
    background: var(--color-surface-2);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border-strong);
    box-shadow: var(--shadow-sm);
  }

  .disabled-btn,
  .joined-btn {
    background: var(--color-surface-muted);
    color: var(--color-text-muted);
    border: 1px solid var(--color-border);
  }
  </style>
