<template>
  <div class="referral-page" ref="pageRef">
    <!-- 背景光晕效果 -->
    <div class="background-glow"></div>
    
    <!-- 沉浸式导航栏 -->
    <van-nav-bar
      :title="t('referral.title')"
      left-arrow
      @click-left="router.back()"
      fixed
      placeholder
      safe-area-inset-top
      :border="false"
      :class="['custom-nav-bar', { 'scrolled': isScrolled }]"
    />

    <!-- 主要内容区域 -->
    <div class="referral-content">
      <!-- 顶部通告栏（跑马灯） -->
      <div class="announcement-marquee">
        <div class="marquee-wrapper" :style="{ animationDuration: marqueeSpeed + 's' }">
          <div 
            v-for="(announcement, index) in announcements" 
            :key="`first-${index}`"
            class="marquee-item"
          >
            <span class="marquee-icon">{{ announcement.icon }}</span>
            <span class="marquee-text">{{ announcement.text }}</span>
          </div>
          <div 
            v-for="(announcement, index) in announcements" 
            :key="`second-${index}`"
            class="marquee-item"
          >
            <span class="marquee-icon">{{ announcement.icon }}</span>
            <span class="marquee-text">{{ announcement.text }}</span>
          </div>
        </div>
      </div>

      <!-- 核心收益看板 -->
      <div class="hero-section glass-card">
        <div class="hero-content">
          <div class="coin-icon-wrapper">
            <div class="coin-icon-3d">
              <van-icon name="gold-coin-o" size="48" color="#FCD535" />
            </div>
          </div>
          <div class="hero-stats">
            <div class="hero-label">{{ t('referral.total_earned') }} (USDT)</div>
            <div class="hero-value gold-text">
              {{ formatNumber(animatedTotalEarned) }}
            </div>
          </div>
        </div>
        <van-button 
          class="withdraw-btn"
          type="primary"
          block
          @click="goToWithdraw"
        >
          {{ t('referral.go_withdraw') }}
        </van-button>
      </div>

      <!-- 返佣设置与分享 -->
      <div class="action-section glass-card">
        <div class="action-header">
          <div class="header-title">{{ t('referral.commission_setting') }}</div>
          <div class="header-total gold-text">{{ t('referral.total_commission') }}: 40%</div>
        </div>

        <!-- 比例滑块 -->
        <div class="slider-container">
          <div class="slider-labels">
            <div class="slider-label-left">
              <span class="label-text">{{ t('referral.my_share') }}</span>
              <span class="label-value gold-text">{{ myShare }}%</span>
            </div>
            <div class="slider-label-right">
              <span class="label-text">{{ t('referral.friend_share') }}</span>
              <span class="label-value gold-text">{{ friendShare }}%</span>
            </div>
          </div>
          <van-slider
            v-model="myShare"
            :min="0"
            :max="40"
            :step="1"
            active-color="#FCD535"
            inactive-color="rgba(255, 255, 255, 0.1)"
            bar-height="4px"
            button-size="20px"
            class="commission-slider"
          />
        </div>

        <!-- 复制区 -->
        <div class="copy-section">
          <div class="copy-item">
            <div class="copy-label">{{ t('referral.invite_code') }}</div>
            <div class="copy-value-wrapper">
              <div class="copy-value">{{ inviteCode }}</div>
              <van-icon 
                name="copy" 
                size="18" 
                color="#FCD535" 
                class="copy-icon"
                @click="handleCopyCode"
              />
            </div>
          </div>
          <div class="copy-item">
            <div class="copy-label">{{ t('referral.invite_link') }}</div>
            <div class="copy-value-wrapper">
              <div class="copy-value link-value">{{ inviteLink }}</div>
              <van-icon 
                name="copy" 
                size="18" 
                color="#FCD535" 
                class="copy-icon"
                @click="handleCopyLink"
              />
            </div>
          </div>
        </div>

        <!-- 立即邀请按钮 -->
        <van-button 
          class="invite-btn"
          type="primary"
          block
          @click="handleInvite"
        >
          <van-icon name="friends-o" size="18" />
          {{ t('referral.invite_now') }}
        </van-button>
      </div>

      <!-- 数据仪表盘 -->
      <div class="dashboard-section">
        <div class="dashboard-grid">
          <div class="dashboard-card glass-card">
            <div class="dashboard-icon">
              <van-icon name="friends-o" size="24" color="#FCD535" />
            </div>
            <div class="dashboard-content">
              <div class="dashboard-label">{{ t('referral.invite_count') }}</div>
              <div class="dashboard-value gold-text">
                {{ formatNumber(animatedInviteCount) }}
                <span class="dashboard-unit">{{ t('referral.people') }}</span>
              </div>
            </div>
          </div>

          <div class="dashboard-card glass-card">
            <div class="dashboard-icon">
              <van-icon name="balance-o" size="24" color="#FCD535" />
            </div>
            <div class="dashboard-content">
              <div class="dashboard-label">{{ t('referral.trading_volume') }}</div>
              <div class="dashboard-value gold-text">
                {{ formatTradingVolume(tradingVolume) }}
              </div>
            </div>
          </div>

          <div class="dashboard-card glass-card">
            <div class="dashboard-icon">
              <van-icon name="gold-coin-o" size="24" color="#0ECB81" />
            </div>
            <div class="dashboard-content">
              <div class="dashboard-label">{{ t('referral.yesterday_earnings') }}</div>
              <div class="dashboard-value text-green">
                +{{ formatNumber(yesterdayEarnings) }} USDT
              </div>
            </div>
          </div>

          <div class="dashboard-card glass-card">
            <div class="dashboard-icon">
              <van-icon name="medal-o" size="24" color="#FCD535" />
            </div>
            <div class="dashboard-content">
              <div class="dashboard-label">{{ t('referral.current_level') }}</div>
              <div class="dashboard-value">
                <span class="level-text gold-text">{{ currentLevel }}</span>
                <div class="level-progress">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: levelProgress + '%' }"
                    ></div>
                  </div>
                  <div class="progress-text">
                    {{ t('referral.need_more', { count: needMoreForNextLevel }) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 邀请记录列表 -->
      <div class="records-section glass-card">
        <van-tabs 
          v-model:active="activeRecordTab" 
          background="transparent" 
          title-active-color="#FCD535" 
          title-inactive-color="#8E8E93" 
          line-width="30px" 
          line-height="3px" 
          color="#FCD535" 
          :border="false"
          class="record-tabs"
        >
          <van-tab :title="t('referral.invite_records')">
            <div class="records-list">
              <div v-if="inviteRecords.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="friends-o" size="64" color="#8E8E93" />
                </div>
                <div class="empty-text">{{ t('referral.no_invite_records') }}</div>
                <van-button 
                  class="empty-action-btn"
                  @click="handleInvite"
                >
                  {{ t('referral.invite_now') }}
                </van-button>
              </div>
              <div v-else class="records-content">
                <div 
                  v-for="(record, index) in inviteRecords" 
                  :key="index"
                  class="record-item"
                >
                  <div class="record-left">
                    <div class="record-avatar">{{ record.user[0] }}</div>
                    <div class="record-info">
                      <div class="record-user">{{ maskUser(record.user) }}</div>
                      <div class="record-time">{{ formatTime(record.registerTime) }}</div>
                    </div>
                  </div>
                  <div class="record-right">
                    <div 
                      class="record-status"
                      :class="record.status"
                    >
                      {{ getStatusLabel(record.status) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </van-tab>

          <van-tab :title="t('referral.commission_details')">
            <div class="records-list">
              <div v-if="commissionRecords.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="gold-coin-o" size="64" color="#8E8E93" />
                </div>
                <div class="empty-text">{{ t('referral.no_commission_records') }}</div>
              </div>
              <div v-else class="records-content">
                <div 
                  v-for="(record, index) in commissionRecords" 
                  :key="index"
                  class="record-item"
                >
                  <div class="record-left">
                    <div class="record-avatar">{{ record.user[0] }}</div>
                    <div class="record-info">
                      <div class="record-user">{{ maskUser(record.user) }}</div>
                      <div class="record-desc">{{ record.type }}</div>
                    </div>
                  </div>
                  <div class="record-right">
                    <div class="record-amount gold-text">
                      +{{ formatNumber(record.amount) }} USDT
                    </div>
                    <div class="record-time">{{ formatTime(record.time) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </van-tab>
        </van-tabs>
      </div>
    </div>

    <!-- 邀请分享弹窗 -->
    <van-popup
      v-model:show="showInvitePopup"
      position="bottom"
      :style="{ height: 'auto', maxHeight: '80vh' }"
      round
      class="invite-share-popup"
      :close-on-click-overlay="true"
    >
      <div class="invite-popup-content">
        <!-- 弹窗头部 -->
        <div class="invite-popup-header">
          <div class="popup-title">{{ t('referral.invite_now') }}</div>
          <van-icon 
            name="cross" 
            @click="showInvitePopup = false" 
            class="popup-close-icon"
          />
        </div>

        <!-- 分享选项 -->
        <div class="share-options">
          <div 
            class="share-option-item"
            @click="handleShareLink"
          >
            <div class="share-icon-wrapper">
              <van-icon name="link-o" size="32" color="#FCD535" />
            </div>
            <div class="share-label">{{ t('referral.share_link') }}</div>
          </div>

          <div 
            class="share-option-item"
            @click="handleShareQR"
          >
            <div class="share-icon-wrapper">
              <van-icon name="qr-invalid" size="32" color="#FCD535" />
            </div>
            <div class="share-label">{{ t('referral.share_qr') }}</div>
          </div>

          <div 
            class="share-option-item"
            @click="handleShareImage"
          >
            <div class="share-icon-wrapper">
              <van-icon name="photo-o" size="32" color="#FCD535" />
            </div>
            <div class="share-label">{{ t('referral.share_image') }}</div>
          </div>
        </div>

        <!-- 邀请码和链接展示 -->
        <div class="invite-info-section">
          <div class="info-item">
            <div class="info-label">{{ t('referral.invite_code') }}</div>
            <div class="info-value-wrapper">
              <span class="info-value gold-text">{{ inviteCode }}</span>
              <van-icon 
                name="copy-o" 
                size="18" 
                color="#FCD535"
                class="copy-action-icon"
                @click.stop="handleCopyCode"
              />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">{{ t('referral.invite_link') }}</div>
            <div class="info-value-wrapper">
              <span class="info-value link-text">{{ inviteLink }}</span>
              <van-icon 
                name="copy-o" 
                size="18" 
                color="#FCD535"
                class="copy-action-icon"
                @click.stop="handleCopyLink"
              />
            </div>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 二维码弹窗 -->
    <van-popup
      v-model:show="showQRPopup"
      position="center"
      round
      class="qr-popup"
      :close-on-click-overlay="true"
    >
      <div class="qr-popup-content">
        <div class="qr-popup-header">
          <div class="popup-title">{{ t('referral.share_qr') }}</div>
          <van-icon 
            name="cross" 
            @click="showQRPopup = false" 
            class="popup-close-icon"
          />
        </div>
        <div class="qr-container">
          <div class="qr-code-wrapper">
            <canvas ref="qrCanvas" class="qr-canvas"></canvas>
          </div>
          <div class="qr-tip">{{ t('referral.scan_to_invite') }}</div>
        </div>
      </div>
    </van-popup>

    <!-- 海报弹窗 -->
    <van-popup
      v-model:show="showPosterPopup"
      position="center"
      round
      class="poster-popup"
      :close-on-click-overlay="true"
    >
      <div class="poster-popup-content">
        <div class="poster-popup-header">
          <div class="popup-title">{{ t('referral.share_image') }}</div>
          <van-icon 
            name="cross" 
            @click="showPosterPopup = false" 
            class="popup-close-icon"
          />
        </div>
        <div class="poster-container">
          <div ref="posterRef" class="poster-canvas-wrapper">
            <!-- 海报内容 -->
            <div class="poster-content">
              <!-- 背景渐变 -->
              <div class="poster-bg"></div>
              
              <!-- Logo 区域 -->
              <div class="poster-logo-section">
                <div class="poster-logo">
                  <BinanceLogo :size="40" class="logo-img" />
                </div>
                <div class="poster-app-name">TruthFi</div>
              </div>

              <!-- 主标题 -->
              <div class="poster-title">{{ t('referral.invite_now') }}</div>
              
              <!-- 邀请码 -->
              <div class="poster-invite-code-section">
                <div class="poster-code-label">{{ t('referral.invite_code') }}</div>
                <div class="poster-code-value">{{ inviteCode }}</div>
              </div>

              <!-- 二维码 -->
              <div class="poster-qr-section">
                <canvas ref="posterQRCanvas" class="poster-qr-canvas"></canvas>
              </div>

              <!-- 底部提示 -->
              <div class="poster-footer">
                <div class="poster-footer-text">{{ t('referral.scan_to_join') }}</div>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="poster-actions">
            <van-button 
              class="save-poster-btn"
              type="primary"
              block
              @click="savePoster"
            >
              {{ t('referral.save_poster') }}
            </van-button>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import QRCode from 'qrcode';
import html2canvas from 'html2canvas';
import BinanceLogo from '@/components/BinanceLogo.vue';

defineOptions({
  name: 'ReferralIndex'
});

const router = useRouter();
const { t, locale } = useI18n();

// 页面引用（用于滚动监听）
const pageRef = ref(null);

// 滚动状态
const isScrolled = ref(false);

// 数字滚动动画 Hook
const useCountUp = (targetValue, duration = 1500) => {
  const currentValue = ref(0);
  let animationFrame = null;
  let startTime = null;
  let startValue = 0;

  const animate = (timestamp) => {
    if (!startTime) startTime = timestamp;
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // 使用 easeOutQuart 缓动函数
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    currentValue.value = startValue + (targetValue - startValue) * easeOutQuart;
    
    if (progress < 1) {
      animationFrame = requestAnimationFrame(animate);
    } else {
      currentValue.value = targetValue;
    }
  };

  const start = (newTarget) => {
    startValue = currentValue.value;
    startTime = null;
    if (animationFrame) cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(animate);
  };

  const stop = () => {
    if (animationFrame) {
      cancelAnimationFrame(animationFrame);
      animationFrame = null;
    }
  };

  return { currentValue, start, stop };
};

// 统计数据
const totalEarned = 12450.88;
const inviteCount = 12;
const tradingVolume = 1200000; // $1.2M
const yesterdayEarnings = 124.50;
const currentLevel = 'Lv.2 黑金';
const needMoreForNextLevel = 3;

// 使用 useCountUp Hook
const { currentValue: animatedTotalEarned, start: startTotalEarned } = useCountUp(totalEarned, 1500);
const { currentValue: animatedInviteCount, start: startInviteCount } = useCountUp(inviteCount, 1500);

// 返佣设置
const myShare = ref(20);
const friendShare = computed(() => 40 - myShare.value);

// 邀请码和链接
const inviteCode = ref('829301');
const inviteLink = computed(() => `https://truthfi.app/invite/${inviteCode.value}`);

// 通告栏数据
const announcements = computed(() => [
  { icon: '🚀', text: t('referral.announcement_withdraw', { user: 'U_9281', amount: '500' }) },
  { icon: '🎉', text: t('referral.announcement_invite', { user: 'Alex', count: '5' }) },
  { icon: '💰', text: t('referral.announcement_earn', { user: 'User_1234', amount: '120.50' }) }
]);

const marqueeSpeed = computed(() => announcements.value.length * 4);

// 邀请记录
const inviteRecords = ref([
  { user: 'User_8829', registerTime: Date.now() - 86400000 * 2, status: 'active' },
  { user: 'User_1234', registerTime: Date.now() - 86400000 * 5, status: 'active' },
  { user: 'User_5678', registerTime: Date.now() - 86400000 * 10, status: 'inactive' }
]);

// 返佣明细
const commissionRecords = ref([
  { user: 'User_8829', type: t('referral.commission_spot'), amount: 12.50, time: Date.now() - 3600000 },
  { user: 'User_1234', type: t('referral.commission_earn'), amount: 8.30, time: Date.now() - 7200000 },
  { user: 'User_5678', type: t('referral.commission_futures'), amount: 15.20, time: Date.now() - 10800000 }
]);

// 等级进度
const levelProgress = computed(() => {
  // 假设当前等级需要10人，已邀请12人，进度为120%，但显示为100%
  const currentLevelRequirement = 10;
  const nextLevelRequirement = 15;
  const progress = ((inviteCount - currentLevelRequirement) / (nextLevelRequirement - currentLevelRequirement)) * 100;
  return Math.min(Math.max(progress, 0), 100);
});

// 格式化数字
const formatNumber = (value) => {
  return value.toLocaleString('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  });
};

// 格式化交易额
const formatTradingVolume = (value) => {
  if (value >= 1000000) {
    return '$' + (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return '$' + (value / 1000).toFixed(0) + 'K';
  }
  return '$' + value.toLocaleString('en-US');
};

// 掩码用户账号
const maskUser = (user) => {
  if (user.length <= 6) return user;
  return user.slice(0, 3) + '***' + user.slice(-3);
};

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 3600000) {
    return Math.floor(diff / 60000) + t('referral.minutes_ago');
  } else if (diff < 86400000) {
    return Math.floor(diff / 3600000) + t('referral.hours_ago');
  } else if (diff < 86400000 * 7) {
    return Math.floor(diff / 86400000) + t('referral.days_ago');
  } else {
    const localeStr = locale.value === 'zh' ? 'zh-CN' : 'en-US';
    return date.toLocaleDateString(localeStr, { month: 'short', day: 'numeric' });
  }
};

// 获取状态标签
const getStatusLabel = (status) => {
  if (status === 'active') {
    return t('referral.status_active');
  } else if (status === 'inactive') {
    return t('referral.status_inactive');
  }
  return status;
};

// 复制邀请码
const handleCopyCode = async () => {
  try {
    await navigator.clipboard.writeText(inviteCode.value);
    showToast({
      message: t('referral.copy_success'),
      icon: 'success',
      duration: 2000
    });
  } catch (error) {
    showToast({
      message: t('referral.copy_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 复制邀请链接
const handleCopyLink = async () => {
  try {
    await navigator.clipboard.writeText(inviteLink.value);
    showToast({
      message: t('referral.copy_success'),
      icon: 'success',
      duration: 2000
    });
  } catch (error) {
    showToast({
      message: t('referral.copy_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 去提现
const goToWithdraw = () => {
  router.push('/withdraw');
};

// 弹窗显示状态
const showInvitePopup = ref(false);
const showQRPopup = ref(false);
const showPosterPopup = ref(false);

// 二维码和海报相关引用
const qrCanvas = ref(null);
const posterQRCanvas = ref(null);
const posterRef = ref(null);

// 立即邀请
const handleInvite = () => {
  showInvitePopup.value = true;
};

// 分享链接
const handleShareLink = () => {
  handleCopyLink();
  showInvitePopup.value = false;
};

// 生成二维码
const generateQRCode = async (canvas, text, size = 200) => {
  try {
    await QRCode.toCanvas(canvas, text, {
      width: size,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      },
      errorCorrectionLevel: 'H'
    });
  } catch (error) {
    console.error('生成二维码失败:', error);
    showToast({
      message: t('referral.qr_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 分享二维码
const handleShareQR = async () => {
  showInvitePopup.value = false;
  showQRPopup.value = true;
  
  await nextTick();
  if (qrCanvas.value) {
    await generateQRCode(qrCanvas.value, inviteLink.value, 250);
  }
};

// 生成海报
const generatePoster = async () => {
  showInvitePopup.value = false;
  showPosterPopup.value = true;
  
  await nextTick();
  
  // 先生成海报中的二维码
  if (posterQRCanvas.value) {
    await generateQRCode(posterQRCanvas.value, inviteLink.value, 180);
  }
  
  // 等待二维码渲染完成
  await new Promise(resolve => setTimeout(resolve, 300));
};

// 分享图片（生成海报）
const handleShareImage = async () => {
  await generatePoster();
};

// 保存海报
const savePoster = async () => {
  if (!posterRef.value) {
    showToast({
      message: t('referral.poster_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
    return;
  }

  try {
    // 使用 html2canvas 生成图片
    const canvas = await html2canvas(posterRef.value, {
      backgroundColor: '#0E0E0E',
      scale: 2, // 提高清晰度
      useCORS: true,
      logging: false,
      width: posterRef.value.offsetWidth,
      height: posterRef.value.offsetHeight
    });

    // 转换为 blob
    canvas.toBlob((blob) => {
      if (!blob) {
        showToast({
          message: t('referral.poster_generate_failed'),
          icon: 'fail',
          duration: 2000
        });
        return;
      }

      // 创建下载链接
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `TruthFi-Invite-${inviteCode.value}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      showToast({
        message: t('referral.poster_saved'),
        icon: 'success',
        duration: 2000
      });
    }, 'image/png', 0.95);
  } catch (error) {
    console.error('生成海报失败:', error);
    showToast({
      message: t('referral.poster_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 滚动监听
const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  isScrolled.value = scrollTop > 10;
};

// 标签页切换
const activeRecordTab = ref(0);

onMounted(() => {
  // 启动数字滚动动画
  startTotalEarned(totalEarned);
  startInviteCount(inviteCount);
  
  // 监听滚动
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // 初始检查
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.referral-page {
  min-height: 100vh;
  background-color: #0E0E0E;
  color: #FFFFFF;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 80px;
}

/* 背景光晕效果 */
.background-glow {
  position: fixed;
  top: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(
    circle,
    rgba(252, 213, 53, 0.15) 0%,
    rgba(212, 175, 55, 0.08) 30%,
    transparent 70%
  );
  pointer-events: none;
  z-index: 0;
  animation: glowPulse 4s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.6;
    transform: translateX(-50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.1);
  }
}

/* 沉浸式导航栏 */
.custom-nav-bar {
  --van-nav-bar-background: transparent;
  --van-nav-bar-title-text-color: #FFFFFF;
  --van-nav-bar-icon-color: #FCD535;
  --van-nav-bar-height: 46px;
  backdrop-filter: blur(10px);
  transition: background-color 0.3s ease;
  position: relative;
  z-index: 100;
}

.custom-nav-bar.scrolled {
  --van-nav-bar-background: rgba(14, 14, 14, 0.95);
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  font-weight: 700 !important;
  font-size: 18px !important;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 主要内容 */
.referral-content {
  position: relative;
  z-index: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
}

/* 顶部通告栏（跑马灯） */
.announcement-marquee {
  height: 32px;
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
  overflow: hidden;
  position: relative;
  margin-top: 46px;
}

.marquee-wrapper {
  display: flex;
  gap: 32px;
  animation: marquee linear infinite;
  white-space: nowrap;
  will-change: transform;
  height: 100%;
  align-items: center;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.marquee-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  font-size: 12px;
  color: #8E8E93;
  white-space: nowrap;
}

.marquee-icon {
  font-size: 14px;
}

.marquee-text {
  color: #FFFFFF;
}

/* 磨砂玻璃卡片 */
.glass-card {
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(212, 175, 55, 0.2);
  padding: 20px;
  margin: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(252, 213, 53, 0.5) 50%,
    transparent 100%
  );
}

.glass-card:active {
  transform: scale(0.98);
  border-color: rgba(252, 213, 53, 0.4);
}

/* 核心收益看板 */
.hero-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 0;
}

.hero-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.coin-icon-wrapper {
  flex-shrink: 0;
}

.coin-icon-3d {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(252, 213, 53, 0.2) 0%, rgba(212, 175, 55, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 16px rgba(252, 213, 53, 0.2),
    inset 0 2px 4px rgba(255, 255, 255, 0.1);
  animation: coinFloat 3s ease-in-out infinite;
}

@keyframes coinFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-8px) rotate(5deg);
  }
}

.hero-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-label {
  font-size: 12px;
  color: #8E8E93;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hero-value {
  font-size: 36px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
  line-height: 1.2;
}

.gold-text {
  color: #FCD535;
  text-shadow: 0 0 10px rgba(252, 213, 53, 0.3);
}

.text-green {
  color: #0ECB81;
}

.withdraw-btn {
  height: 44px;
  background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
  color: #000000;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(252, 213, 53, 0.3);
}

.withdraw-btn:active {
  opacity: 0.9;
  transform: scale(0.98);
}

/* 返佣设置与分享 */
.action-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

.header-total {
  font-size: 14px;
  font-weight: 600;
}

.slider-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-label-left,
.slider-label-right {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label-text {
  font-size: 12px;
  color: #8E8E93;
}

.label-value {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
}

.commission-slider {
  margin: 8px 0;
}

:deep(.commission-slider .van-slider__button) {
  background: #FCD535;
  box-shadow: 0 2px 8px rgba(252, 213, 53, 0.4);
  border: 2px solid #000000;
}

:deep(.commission-slider .van-slider__bar) {
  background: #FCD535;
}

.copy-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.copy-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.copy-label {
  font-size: 12px;
  color: #8E8E93;
  font-weight: 500;
}

.copy-value-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.copy-value {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  color: #FCD535;
  word-break: break-all;
}

.link-value {
  font-size: 12px;
  color: #8E8E93;
}

.copy-icon {
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.copy-icon:active {
  transform: scale(1.2);
}

.invite-btn {
  height: 48px;
  background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
  color: #000000;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(252, 213, 53, 0.3);
  margin-top: 8px;
}

.invite-btn:active {
  opacity: 0.9;
  transform: scale(0.98);
}

/* 数据仪表盘 */
.dashboard-section {
  padding: 0 16px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.dashboard-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  margin: 0;
}

.dashboard-icon {
  width: 40px;
  height: 40px;
  background: rgba(252, 213, 53, 0.15);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dashboard-label {
  font-size: 11px;
  color: #8E8E93;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dashboard-value {
  font-size: 20px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
  line-height: 1.2;
}

.dashboard-unit {
  font-size: 14px;
  font-weight: 600;
  margin-left: 2px;
}

.level-text {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  display: block;
}

.level-progress {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FCD535 0%, #F0B90B 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
  box-shadow: 0 0 8px rgba(252, 213, 53, 0.4);
}

.progress-text {
  font-size: 10px;
  color: #8E8E93;
}

/* 邀请记录列表 */
.records-section {
  display: flex;
  flex-direction: column;
  min-height: 400px;
  margin-bottom: 0;
}

.record-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.record-tabs .van-tabs__wrap) {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 0 20px;
}

:deep(.record-tabs .van-tab) {
  font-size: 14px;
  font-weight: 600;
  padding: 12px 0;
}

:deep(.record-tabs .van-tabs__content) {
  flex: 1;
  overflow-y: auto;
}

:deep(.record-tabs .van-tab__panel) {
  height: 100%;
  overflow-y: auto;
}

.records-list {
  padding: 16px 20px;
  min-height: 300px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: #8E8E93;
  margin-bottom: 24px;
}

.empty-action-btn {
  padding: 10px 24px;
  background: rgba(252, 213, 53, 0.15);
  color: #FCD535;
  border: 1px solid rgba(252, 213, 53, 0.3);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.empty-action-btn:active {
  background: rgba(252, 213, 53, 0.25);
}

.records-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}

.record-item:active {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(252, 213, 53, 0.2);
}

.record-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.record-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(252, 213, 53, 0.3) 0%, rgba(212, 175, 55, 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #FCD535;
  flex-shrink: 0;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.record-user {
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
}

.record-time,
.record-desc {
  font-size: 12px;
  color: #8E8E93;
}

.record-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.record-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.record-status.active {
  background: rgba(14, 203, 129, 0.15);
  color: #0ECB81;
}

.record-status.inactive {
  background: rgba(142, 142, 147, 0.15);
  color: #8E8E93;
}

.record-amount {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
}

/* 确保 Vant 图标字体不被全局字体覆盖 */
:deep(.van-icon),
:deep([class*="van-icon"]),
.van-icon,
[class*="van-icon"] {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
  font-style: normal !important;
  font-weight: normal !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
}

/* 邀请分享弹窗样式 */
:deep(.invite-share-popup .van-popup) {
  background: #141414 !important;
  border-top: 1px solid rgba(252, 213, 53, 0.2) !important;
}

.invite-popup-content {
  padding: 24px 20px 32px;
  background: #141414;
  border-radius: 20px 20px 0 0;
}

.invite-popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: #FFFFFF;
  letter-spacing: -0.5px;
}

.popup-close-icon {
  font-size: 20px;
  color: #8E8E93;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 4px;
}

.popup-close-icon:active {
  color: #FCD535;
  transform: scale(0.9);
}

/* 分享选项 */
.share-options {
  display: flex;
  justify-content: space-around;
  margin-bottom: 32px;
  padding: 0 8px;
}

.share-option-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 12px;
  border-radius: 12px;
  min-width: 80px;
}

.share-option-item:active {
  transform: scale(0.95);
  background: rgba(252, 213, 53, 0.05);
}

.share-icon-wrapper {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(252, 213, 53, 0.1);
  border: 1px solid rgba(252, 213, 53, 0.2);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.share-option-item:active .share-icon-wrapper {
  background: rgba(252, 213, 53, 0.2);
  border-color: rgba(252, 213, 53, 0.4);
  box-shadow: 0 0 12px rgba(252, 213, 53, 0.3);
}

.share-label {
  font-size: 13px;
  color: #FFFFFF;
  font-weight: 500;
  text-align: center;
}

/* 邀请信息区域 */
.invite-info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: rgba(28, 28, 30, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(252, 213, 53, 0.15);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 12px;
  color: #8E8E93;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.info-value-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-value {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  word-break: break-all;
}

.info-value.link-text {
  color: #FFFFFF;
  font-size: 13px;
}

.copy-action-icon {
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 4px;
}

.copy-action-icon:active {
  transform: scale(0.9);
  opacity: 0.7;
}

/* 弹窗遮罩层 */
:deep(.invite-share-popup .van-overlay) {
  background: rgba(0, 0, 0, 0.7) !important;
  backdrop-filter: blur(4px);
}

/* 二维码弹窗样式 */
:deep(.qr-popup .van-popup) {
  background: #141414 !important;
  border: 1px solid rgba(252, 213, 53, 0.2) !important;
}

.qr-popup-content {
  padding: 24px 20px 32px;
  background: #141414;
  border-radius: 20px;
  min-width: 300px;
  max-width: 90vw;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.qr-code-wrapper {
  background: #FFFFFF;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.qr-canvas {
  display: block;
}

.qr-tip {
  font-size: 14px;
  color: #8E8E93;
  text-align: center;
}

/* 海报弹窗样式 */
:deep(.poster-popup .van-popup) {
  background: #141414 !important;
  border: 1px solid rgba(252, 213, 53, 0.2) !important;
  max-width: 95vw;
  max-height: 95vh;
  overflow: hidden !important; /* 改为 hidden，防止出现滚动条 */
  display: flex;
  flex-direction: column;
}

/* 隐藏滚动条 - 兼容所有浏览器 */
:deep(.poster-popup .van-popup),
:deep(.poster-popup-content),
:deep(.poster-container),
:deep(.poster-canvas-wrapper) {
  /* Firefox */
  scrollbar-width: none !important;
  /* Webkit (Chrome, Safari, Edge) */
  -ms-overflow-style: none !important;
}

:deep(.poster-popup .van-popup)::-webkit-scrollbar,
:deep(.poster-popup-content)::-webkit-scrollbar,
:deep(.poster-container)::-webkit-scrollbar,
:deep(.poster-canvas-wrapper)::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

.poster-popup-content {
  padding: 20px;
  background: #141414;
  border-radius: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(95vh - 40px); /* 减去上下 padding */
  display: flex;
  flex-direction: column;
  /* 确保内容从顶部开始显示，不被截断 */
  align-items: stretch;
  /* 隐藏滚动条 - 兼容所有浏览器 */
  scrollbar-width: none !important; /* Firefox */
  -ms-overflow-style: none !important; /* IE/Edge */
}

/* Webkit 浏览器滚动条隐藏 */
.poster-popup-content::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  background: transparent !important;
}

.poster-popup-content::-webkit-scrollbar-track {
  display: none !important;
  background: transparent !important;
}

.poster-popup-content::-webkit-scrollbar-thumb {
  display: none !important;
  background: transparent !important;
}

/* 海报弹窗头部样式 */
.poster-popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0; /* 防止头部被压缩 */
}

.poster-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  min-height: 0; /* 允许 flex 子元素收缩 */
  overflow-y: auto;
  overflow-x: hidden;
  /* 隐藏滚动条 */
  scrollbar-width: none !important;
  -ms-overflow-style: none !important;
}

.poster-container::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

.poster-canvas-wrapper {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  background: transparent;
  flex-shrink: 0; /* 防止海报被压缩 */
  /* 确保海报完整显示 */
  display: flex;
  flex-direction: column;
}

.poster-content {
  position: relative;
  width: 100%;
  padding: 40px 30px;
  background: linear-gradient(135deg, #0E0E0E 0%, #1C1C1E 100%);
  border-radius: 20px;
  border: 2px solid rgba(252, 213, 53, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  /* 确保内容完整显示，不被截断 */
  box-sizing: border-box;
  min-height: fit-content;
}

.poster-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 0%, rgba(252, 213, 53, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.poster-logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.poster-logo {
  width: 64px;
  height: 64px;
  background: rgba(252, 213, 53, 0.1);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(252, 213, 53, 0.3);
  padding: 12px;
}


.poster-app-name {
  font-size: 24px;
  font-weight: 700;
  color: #FCD535;
  letter-spacing: 2px;
}

.poster-title {
  font-size: 20px;
  font-weight: 600;
  color: #FFFFFF;
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.poster-invite-code-section {
  background: rgba(28, 28, 30, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid rgba(252, 213, 53, 0.2);
  position: relative;
  z-index: 1;
}

.poster-code-label {
  font-size: 12px;
  color: #8E8E93;
  text-align: center;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.poster-code-value {
  font-size: 32px;
  font-weight: 700;
  color: #FCD535;
  text-align: center;
  font-family: 'DIN Alternate', monospace;
  letter-spacing: 4px;
}

.poster-qr-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.poster-qr-canvas {
  background: #FFFFFF;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.poster-footer {
  text-align: center;
  position: relative;
  z-index: 1;
}

.poster-footer-text {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 500;
}

.poster-actions {
  margin-top: 20px;
}

.save-poster-btn {
  background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
  color: #000000;
  border: none;
  font-weight: 600;
  height: 48px;
  border-radius: 12px;
}

.save-poster-btn:active {
  opacity: 0.9;
}

/* 二维码弹窗遮罩 */
:deep(.qr-popup .van-overlay),
:deep(.poster-popup .van-overlay) {
  background: rgba(0, 0, 0, 0.8) !important;
  backdrop-filter: blur(4px);
}
</style>
