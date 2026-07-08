<template>
  <div class="referral-page" ref="pageRef">
    <van-nav-bar
      :title="t('referral.title')"
      left-arrow
      @click-left="router.back()"
      fixed
      placeholder
      safe-area-inset-top
      :border="false"
      class="custom-nav-bar"
    />

    <div class="referral-content">
      <!-- 消息通知横条 -->
      <div class="notice-bar">
        <van-icon name="volume-o" class="notice-icon" />
        <span class="notice-text">Alex 成功邀请 5 人，获得 250 USDT 返佣</span>
        <span class="notice-time">2 分钟前</span>
        <van-icon name="arrow" class="notice-arrow" />
      </div>

      <!-- 返佣收益主卡片 -->
      <section class="card hero-card">
        <div class="hero-top">
          <span class="hero-tag">{{ t('referral.title') }}</span>
          <span class="hero-commission">{{ t('referral.total_commission') }} 40%</span>
        </div>

        <div class="hero-label">{{ t('referral.total_earned') }} (USDT)</div>

        <div class="hero-amount">
          <span class="hero-number">{{ formatNumber(animatedTotalEarned) }}</span>
          <span class="hero-unit">USDT</span>
        </div>

        <div class="hero-chips">
          <div class="hero-chip">
            <van-icon name="friends-o" />
            <span>{{ t('referral.invite_count') }} {{ inviteCount }}</span>
          </div>
          <div class="hero-chip">
            <van-icon name="balance-o" />
            <span>可提现 500 USDT</span>
          </div>
        </div>

        <div class="hero-actions">
          <button class="btn-primary" type="button" @click="handleInvite">
            <van-icon name="friends-o" size="18" />
            <span>立即邀请</span>
          </button>
          <button class="btn-outline" type="button" @click="goToWithdraw">
            {{ t('referral.go_withdraw') }}
          </button>
        </div>
      </section>

      <!-- 邀请链接卡片 -->
      <section class="card link-card">
        <div class="card-title">
          <van-icon name="link-o" />
          <span>邀请链接</span>
        </div>
        <div class="link-row">
          <van-icon name="coupon-o" class="link-icon" />
          <span class="link-text">{{ inviteCode }}</span>
          <button class="copy-btn" type="button" @click="handleCopyCode">
            <van-icon name="copy-o" />
            <span>复制</span>
          </button>
        </div>
        <div class="link-row">
          <van-icon name="globe-o" class="link-icon" />
          <span class="link-text">{{ inviteLink.replace(/^https?:\/\//, '') }}</span>
          <button class="copy-btn" type="button" @click="handleCopyLink">
            <van-icon name="copy-o" />
            <span>复制</span>
          </button>
        </div>
      </section>

      <!-- 返佣设置卡片 -->
      <section class="card setting-card">
        <div class="card-title">
          <van-icon name="clock-o" />
          <span>{{ t('referral.commission_setting') }}</span>
        </div>
        <div class="setting-shares">
          <div class="share-item">
            <span class="share-label">{{ t('referral.my_share') }}</span>
            <span class="share-value">{{ myShare }}%</span>
          </div>
          <div class="share-item right">
            <span class="share-label">{{ t('referral.friend_share') }}</span>
            <span class="share-value">{{ friendShare }}%</span>
          </div>
        </div>
        <van-slider
          v-model="myShare"
          :min="0"
          :max="40"
          :step="1"
          bar-height="4px"
          button-size="18px"
          active-color="#F5B51B"
          inactive-color="#E5E7EB"
          class="rebate-slider"
        />
      </section>

      <!-- 数据统计四宫格 -->
      <section class="card stats-grid">
        <div class="stat-cell">
          <div class="stat-icon gold"><van-icon name="friends-o" /></div>
          <div class="stat-body">
            <span class="stat-label">{{ t('referral.invite_count') }}</span>
            <span class="stat-value">
              {{ formatNumber(animatedInviteCount) }}<em class="stat-unit">{{ t('referral.people') }}</em>
            </span>
          </div>
        </div>

        <div class="stat-cell">
          <div class="stat-icon gray"><van-icon name="balance-o" /></div>
          <div class="stat-body">
            <span class="stat-label">{{ t('referral.trading_volume') }}</span>
            <span class="stat-value">{{ formatTradingVolume(tradingVolume) }}</span>
          </div>
        </div>

        <div class="stat-cell">
          <div class="stat-icon green"><van-icon name="gold-coin-o" /></div>
          <div class="stat-body">
            <span class="stat-label">{{ t('referral.yesterday_earnings') }}</span>
            <span class="stat-value green-text">
              +{{ formatNumber(yesterdayEarnings) }}<em class="stat-unit">USDT</em>
            </span>
          </div>
        </div>

        <div class="stat-cell">
          <div class="stat-icon lvl"><van-icon name="medal-o" /></div>
          <div class="stat-body">
            <span class="stat-label">{{ t('referral.current_level') }}</span>
            <span class="stat-value level">
              <em class="lv">{{ currentLevel.split(' ')[0] }}</em>{{ currentLevel.slice(currentLevel.indexOf(' ') + 1) }}
            </span>
            <div class="stat-progress">
              <div class="stat-progress-fill" :style="{ width: levelProgress + '%' }"></div>
            </div>
            <span class="stat-progress-text">{{ t('referral.need_more', { count: needMoreForNextLevel }) }}</span>
          </div>
        </div>
      </section>

      <!-- 邀请记录 / 佣金明细 -->
      <section class="card records-card">
        <van-tabs
          v-model:active="activeRecordTab"
          background="transparent"
          title-active-color="#101828"
          title-inactive-color="#667085"
          color="#F5B51B"
          line-width="28px"
          line-height="3px"
          :border="false"
          class="record-tabs"
        >
          <van-tab :title="t('referral.invite_records')">
            <div class="records-list">
              <div v-if="inviteRecords.length === 0" class="empty-state">
                <van-icon name="friends-o" />
                <div class="empty-text">{{ t('referral.no_invite_records') }}</div>
              </div>
              <div v-else class="records-content">
                <div v-for="(record, index) in inviteRecords" :key="index" class="record-item">
                  <div class="record-left">
                    <div class="record-avatar">{{ record.user[0] }}</div>
                    <div class="record-info">
                      <div class="record-user">{{ maskUser(record.user) }}</div>
                      <div class="record-time">{{ formatTime(record.registerTime) }}</div>
                    </div>
                  </div>
                  <div class="record-right">
                    <span class="record-status" :class="record.status">{{ getStatusLabel(record.status) }}</span>
                    <van-icon name="arrow" class="record-arrow" />
                  </div>
                </div>
              </div>
            </div>
          </van-tab>

          <van-tab :title="t('referral.commission_details')">
            <div class="records-list">
              <div v-if="commissionRecords.length === 0" class="empty-state">
                <van-icon name="gold-coin-o" />
                <div class="empty-text">{{ t('referral.no_commission_records') }}</div>
              </div>
              <div v-else class="records-content">
                <div v-for="(record, index) in commissionRecords" :key="index" class="record-item">
                  <div class="record-left">
                    <div class="record-avatar">{{ record.user[0] }}</div>
                    <div class="record-info">
                      <div class="record-user">{{ maskUser(record.user) }}</div>
                      <div class="record-desc">{{ record.type }}</div>
                    </div>
                  </div>
                  <div class="record-right">
                    <span class="record-amount">+{{ formatNumber(record.amount) }} USDT</span>
                    <span class="record-time">{{ formatTime(record.time) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </van-tab>
        </van-tabs>
      </section>
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
        <div class="invite-popup-header">
          <div class="popup-title">{{ t('referral.invite_now') }}</div>
          <van-icon name="cross" @click="showInvitePopup = false" class="popup-close-icon" />
        </div>

        <div class="share-options">
          <div class="share-option-item" @click="handleShareLink">
            <div class="share-icon-wrapper">
              <van-icon name="link-o" size="32" color="var(--color-brand-legacy)" />
            </div>
            <div class="share-label">{{ t('referral.share_link') }}</div>
          </div>

          <div class="share-option-item" @click="handleShareQR">
            <div class="share-icon-wrapper">
              <van-icon name="qr-invalid" size="32" color="var(--color-brand-legacy)" />
            </div>
            <div class="share-label">{{ t('referral.share_qr') }}</div>
          </div>

          <div class="share-option-item" @click="handleShareImage">
            <div class="share-icon-wrapper">
              <van-icon name="photo-o" size="32" color="var(--color-brand-legacy)" />
            </div>
            <div class="share-label">{{ t('referral.share_image') }}</div>
          </div>
        </div>

        <div class="invite-info-section">
          <div class="info-item">
            <div class="info-label">{{ t('referral.invite_code') }}</div>
            <div class="info-value-wrapper">
              <span class="info-value gold-text">{{ inviteCode }}</span>
              <van-icon
                name="copy-o"
                size="18"
                color="var(--color-brand-legacy)"
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
                color="var(--color-brand-legacy)"
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
          <van-icon name="cross" @click="showQRPopup = false" class="popup-close-icon" />
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
          <van-icon name="cross" @click="showPosterPopup = false" class="popup-close-icon" />
        </div>
        <div class="poster-container">
          <div ref="posterRef" class="poster-canvas-wrapper">
            <div class="poster-content">
              <div class="poster-bg"></div>

              <div class="poster-logo-section">
                <div class="poster-logo">
                  <BinanceLogo :size="40" class="logo-img" />
                </div>
                <div class="poster-app-name">TruthFi</div>
              </div>

              <div class="poster-title">{{ t('referral.invite_now') }}</div>

              <div class="poster-invite-code-section">
                <div class="poster-code-label">{{ t('referral.invite_code') }}</div>
                <div class="poster-code-value">{{ inviteCode }}</div>
              </div>

              <div class="poster-qr-section">
                <canvas ref="posterQRCanvas" class="poster-qr-canvas"></canvas>
              </div>

              <div class="poster-footer">
                <div class="poster-footer-text">{{ t('referral.scan_to_join') }}</div>
              </div>
            </div>
          </div>

          <div class="poster-actions">
            <van-button class="save-poster-btn" type="primary" block @click="savePoster">
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
import { getThemeColor } from '@/styles/theme';
import { useAssetActions } from '@/composables/useAssetActions';

defineOptions({
  name: 'ReferralIndex'
});

const router = useRouter();
const { t, locale } = useI18n();
const { openWithdraw } = useAssetActions();

const pageRef = ref(null);
const isScrolled = ref(false);

const useCountUp = (targetValue, duration = 1500) => {
  const currentValue = ref(0);
  let animationFrame = null;
  let startTime = null;
  let startValue = 0;

  const animate = (timestamp) => {
    if (!startTime) startTime = timestamp;
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);

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

const totalEarned = 12450.88;
const inviteCount = 12;
const tradingVolume = 1200000; // $1.2M
const yesterdayEarnings = 124.50;
const currentLevel = 'Lv.2 \u9ed1\u91d1';
const needMoreForNextLevel = 3;

const { currentValue: animatedTotalEarned, start: startTotalEarned } = useCountUp(totalEarned, 1500);
const { currentValue: animatedInviteCount, start: startInviteCount } = useCountUp(inviteCount, 1500);

const myShare = ref(20);
const friendShare = computed(() => 40 - myShare.value);

const inviteCode = ref('829301');
const inviteLink = computed(() => `https://truthfi.app/invite/${inviteCode.value}`);
const isChineseLocale = computed(() => String(locale.value).toLowerCase().startsWith('zh'));
const copyActionLabel = computed(() => isChineseLocale.value ? '\u590d\u5236' : 'Copy');
const splitLabel = computed(() => isChineseLocale.value ? '\u8fd4\u4f63\u5206\u914d' : 'Reward Split');

const announcements = computed(() => [
  { icon: 'volume-o', text: 'Alex 成功邀请 5 人，获得 250 USDT 返佣' },
  { icon: 'friends-o', text: t('referral.announcement_invite', { user: 'Alex', count: '5' }) },
  { icon: 'gold-coin-o', text: t('referral.announcement_earn', { user: 'User_1234', amount: '120.50' }) }
]);

const marqueeSpeed = computed(() => announcements.value.length * 4);

const inviteRecords = ref([
  { user: 'User_8829', registerTime: Date.now() - 86400000 * 2, status: 'active' },
  { user: 'User_1234', registerTime: Date.now() - 86400000 * 5, status: 'active' },
  { user: 'User_5678', registerTime: Date.now() - 86400000 * 10, status: 'inactive' }
]);

const commissionRecords = ref([
  { user: 'User_8829', type: t('referral.commission_spot'), amount: 12.50, time: Date.now() - 3600000 },
  { user: 'User_1234', type: t('referral.commission_earn'), amount: 8.30, time: Date.now() - 7200000 },
  { user: 'User_5678', type: t('referral.commission_futures'), amount: 15.20, time: Date.now() - 10800000 }
]);

const levelProgress = computed(() => {
  const currentLevelRequirement = 10;
  const nextLevelRequirement = 15;
  const progress = ((inviteCount - currentLevelRequirement) / (nextLevelRequirement - currentLevelRequirement)) * 100;
  return Math.min(Math.max(progress, 0), 100);
});

const formatNumber = (value) => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

const formatTradingVolume = (value) => {
  if (value >= 1000000) {
    return '$' + (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return '$' + (value / 1000).toFixed(0) + 'K';
  }
  return '$' + value.toLocaleString('en-US');
};

const maskUser = (user) => {
  if (user.length <= 6) return user;
  return user.slice(0, 3) + '***' + user.slice(-3);
};

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

const getStatusLabel = (status) => {
  if (status === 'active') {
    return t('referral.status_active');
  } else if (status === 'inactive') {
    return t('referral.status_inactive');
  }
  return status;
};

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

const goToWithdraw = () => {
  openWithdraw('USDT');
};

const showInvitePopup = ref(false);
const showQRPopup = ref(false);
const showPosterPopup = ref(false);

const qrCanvas = ref(null);
const posterQRCanvas = ref(null);
const posterRef = ref(null);

const handleInvite = () => {
  showInvitePopup.value = true;
};

const handleShareLink = () => {
  handleCopyLink();
  showInvitePopup.value = false;
};

const generateQRCode = async (canvas, text, size = 200) => {
  try {
    await QRCode.toCanvas(canvas, text, {
      width: size,
      margin: 2,
      color: {
        dark: getThemeColor('--color-qr-dark'),
        light: getThemeColor('--color-qr-light')
      },
      errorCorrectionLevel: 'H'
    });
  } catch (error) {
    console.error('QR generate failed', error);
    showToast({
      message: t('referral.qr_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

const handleShareQR = async () => {
  showInvitePopup.value = false;
  showQRPopup.value = true;

  await nextTick();
  if (qrCanvas.value) {
    await generateQRCode(qrCanvas.value, inviteLink.value, 250);
  }
};

const generatePoster = async () => {
  showInvitePopup.value = false;
  showPosterPopup.value = true;

  await nextTick();

  if (posterQRCanvas.value) {
    await generateQRCode(posterQRCanvas.value, inviteLink.value, 180);
  }

  await new Promise(resolve => setTimeout(resolve, 300));
};

const handleShareImage = async () => {
  await generatePoster();
};

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
    const canvas = await html2canvas(posterRef.value, {
      backgroundColor: getThemeColor('--color-bg'),
      scale: 2,
      useCORS: true,
      logging: false,
      width: posterRef.value.offsetWidth,
      height: posterRef.value.offsetHeight
    });

    canvas.toBlob((blob) => {
      if (!blob) {
        showToast({
          message: t('referral.poster_generate_failed'),
          icon: 'fail',
          duration: 2000
        });
        return;
      }

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
    console.error('poster generate failed', error);
    showToast({
      message: t('referral.poster_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  isScrolled.value = scrollTop > 10;
};

const activeRecordTab = ref(0);

onMounted(() => {
  startTotalEarned(totalEarned);
  startInviteCount(inviteCount);

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* =====================================================================
   邀请返佣页 —— 高级金融 App 风格（浅色）
   页面结构：导航 / 通知横条 / 收益主卡 / 邀请链接 / 返佣设置 / 数据四宫格 / 记录
   ===================================================================== */
.referral-page {
  min-height: 100vh;
  background: #f5f7fb;
  color: #101828;
}

.custom-nav-bar {
  --van-nav-bar-height: 56px;
  --van-nav-bar-background: #ffffff;
  --van-nav-bar-title-text-color: #101828;
  --van-nav-bar-icon-color: #101828;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  font-size: 18px;
  font-weight: 700;
}

:deep(.custom-nav-bar .van-icon) {
  font-size: 22px;
}

.referral-content {
  max-width: 520px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

/* 卡片通用 */
.card {
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  box-sizing: border-box;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #101828;
  font-size: 18px;
  font-weight: 700;
}

.card-title .van-icon {
  font-size: 20px;
  color: #101828;
}

/* ---------- 通知横条 ---------- */
.notice-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 44px;
  margin: -16px -16px 0;
  padding: 0 16px;
  background: #ffffff;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.notice-icon {
  flex: 0 0 auto;
  font-size: 16px;
  color: #667085;
}

.notice-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #667085;
  font-size: 14px;
}

.notice-time {
  flex: 0 0 auto;
  color: #667085;
  font-size: 14px;
}

.notice-arrow {
  flex: 0 0 auto;
  font-size: 16px;
  color: #98a2b3;
}

/* ---------- 返佣收益主卡片 ---------- */
.hero-card {
  position: relative;
  overflow: hidden;
  padding: 24px;
  background:
    radial-gradient(circle at 90% 18%, rgba(245, 181, 27, 0.12), transparent 38%),
    #ffffff;
}

.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.hero-tag {
  padding: 6px 12px;
  border-radius: 999px;
  background: #f2f4f7;
  color: #101828;
  font-size: 13px;
  font-weight: 600;
}

.hero-commission {
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(245, 181, 27, 0.16);
  color: #a16207;
  font-size: 14px;
  font-weight: 700;
}

.hero-label {
  margin-top: 18px;
  color: #667085;
  font-size: 16px;
  font-weight: 700;
}

.hero-amount {
  margin-top: 10px;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.hero-number {
  color: #101828;
  font-size: clamp(44px, 12.5vw, 54px);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.hero-unit {
  color: #e6a400;
  font-size: 18px;
  font-weight: 800;
}

.hero-chips {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #f2f4f7;
  color: #101828;
  font-size: 14px;
  font-weight: 700;
}

.hero-chip .van-icon {
  font-size: 16px;
  color: #667085;
}

.hero-actions {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 12px;
}

.btn-primary,
.btn-outline {
  height: 56px;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  border: 0;
  background: linear-gradient(135deg, #f7c82f 0%, #f5b51b 100%);
  color: #101828;
  font-weight: 800;
}

.btn-outline {
  border: 1px solid rgba(16, 24, 40, 0.7);
  background: #ffffff;
  color: #101828;
  font-weight: 700;
}

.btn-primary:active,
.btn-outline:active {
  opacity: 0.9;
}

/* ---------- 邀请链接卡片 ---------- */
.link-card {
  padding: 18px 20px;
}

.link-card .card-title {
  margin-bottom: 6px;
}

.link-row {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  min-height: 48px;
}

.link-row + .link-row {
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.link-icon {
  font-size: 18px;
  color: #98a2b3;
}

.link-text {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #344054;
  font-size: 15px;
  font-weight: 600;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: #344054;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.copy-btn .van-icon {
  font-size: 16px;
}

.copy-btn:active {
  opacity: 0.6;
}

/* ---------- 返佣设置卡片 ---------- */
.setting-card {
  padding: 22px 20px;
}

.setting-card .card-title {
  margin-bottom: 18px;
}

.setting-shares {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.share-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.share-item.right {
  align-items: flex-end;
}

.share-label {
  color: #667085;
  font-size: 14px;
  font-weight: 500;
}

.share-value {
  color: #101828;
  font-size: 24px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.rebate-slider {
  margin: 6px 2px 2px;
}

:deep(.rebate-slider .van-slider__button) {
  width: 18px;
  height: 18px;
  background: #f5b51b;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 4px rgba(245, 181, 27, 0.4);
}

/* ---------- 数据统计四宫格 ---------- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  overflow: hidden;
  padding: 0;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.stat-cell {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  min-height: 92px;
  padding: 14px 16px;
  box-sizing: border-box;
}

.stat-cell:nth-child(odd) {
  border-right: 1px solid rgba(15, 23, 42, 0.06);
}

.stat-cell:nth-child(-n + 2) {
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.stat-icon.gold {
  background: rgba(245, 181, 27, 0.10);
  color: #b7791f;
}

.stat-icon.gray {
  background: #f4f6fa;
  color: #667085;
}

.stat-icon.green {
  background: rgba(22, 163, 74, 0.10);
  color: #16a34a;
}

.stat-icon.lvl {
  background: #f4f6fa;
  color: #f5b51b;
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.stat-label {
  color: #667085;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.3;
}

.stat-value {
  display: flex;
  align-items: baseline;
  color: #101828;
  font-size: 19px;
  font-weight: 800;
  line-height: 1.25;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.stat-value.green-text {
  color: #16a34a;
}

.stat-value.level {
  color: #101828;
  font-size: 18px;
}

.stat-value.level .lv {
  font-style: normal;
  margin-right: 4px;
  color: #f5b51b;
}

.stat-unit {
  font-style: normal;
  margin-left: 3px;
  font-size: 13px;
  font-weight: 700;
  color: #667085;
}

.stat-value.green-text .stat-unit {
  color: #16a34a;
}

.stat-progress {
  width: 88px;
  max-width: 100%;
  margin-top: 6px;
  height: 4px;
  border-radius: 999px;
  background: #e5e7eb;
  overflow: hidden;
}

.stat-progress-fill {
  height: 100%;
  background: #f5b51b;
  border-radius: 999px;
}

.stat-progress-text {
  margin-top: 4px;
  color: #667085;
  font-size: 12px;
  font-weight: 500;
}

/* ---------- 邀请记录 / 佣金明细 ---------- */
.records-card {
  padding: 6px 0 6px;
}

:deep(.record-tabs .van-tabs__wrap) {
  padding: 0 8px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

:deep(.record-tabs .van-tab) {
  font-size: 16px;
  font-weight: 700;
}

:deep(.record-tabs .van-tabs__line) {
  border-radius: 999px;
}

.records-list {
  padding: 4px 16px 8px;
}

.records-content {
  display: flex;
  flex-direction: column;
}

.record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 72px;
}

.record-item + .record-item {
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.record-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

.record-avatar {
  flex: 0 0 44px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(245, 181, 27, 0.16);
  color: #b7791f;
  font-size: 16px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.record-user {
  color: #101828;
  font-size: 16px;
  font-weight: 700;
}

.record-time,
.record-desc {
  color: #667085;
  font-size: 14px;
}

.record-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
}

.record-status {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.record-status.active {
  background: rgba(22, 163, 74, 0.12);
  color: #16a34a;
}

.record-status.inactive {
  background: #f2f4f7;
  color: #667085;
}

.record-arrow {
  font-size: 16px;
  color: #98a2b3;
}

.record-amount {
  color: #16a34a;
  font-size: 16px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 20px;
}

.empty-state .van-icon {
  font-size: 56px;
  color: #cbd5e1;
}

.empty-text {
  color: #667085;
  font-size: 14px;
}

@media (max-width: 360px) {
  .hero-number {
    font-size: 42px;
  }

  .btn-primary,
  .btn-outline {
    height: 52px;
    font-size: 15px;
  }
}

/* =====================================================================
   分享 / 二维码 / 海报弹窗（保留原交互，仅沿用主题变量适配深浅）
   ===================================================================== */
:deep(.van-icon),
:deep([class*="van-icon"]) {
  font-family: 'vant-icon', 'vant-iconfont', 'vant-icons', 'iconfont', 'vant', sans-serif !important;
  font-style: normal !important;
  font-weight: normal !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
}

:deep(.invite-share-popup .van-popup) {
  background: var(--color-bg-input) !important;
  border-top: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.2) !important;
}

.invite-popup-content {
  padding: 24px 20px 32px;
  background: var(--color-bg-input);
  border-radius: 20px 20px 0 0;
}

.invite-popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

.popup-close-icon {
  font-size: 20px;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px;
}

.popup-close-icon:active {
  color: var(--color-brand-legacy);
  transform: scale(0.9);
}

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
  padding: 12px;
  border-radius: 12px;
  min-width: 80px;
}

.share-option-item:active {
  transform: scale(0.95);
  background: rgb(var(--color-brand-legacy-rgb) / 0.05);
}

.share-icon-wrapper {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgb(var(--color-brand-legacy-rgb) / 0.1);
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.2);
  border-radius: 16px;
}

.share-label {
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 500;
  text-align: center;
}

.invite-info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: rgb(var(--color-surface-rgb) / 0.6);
  border-radius: 12px;
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.15);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 12px;
  color: var(--color-text-secondary);
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
  background: rgb(var(--color-shadow-rgb) / 0.3);
  border-radius: 8px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
}

.info-value {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  word-break: break-all;
}

.info-value.link-text {
  color: var(--color-text-primary);
  font-size: 13px;
}

.gold-text {
  color: var(--color-brand-legacy);
}

.copy-action-icon {
  flex-shrink: 0;
  cursor: pointer;
  padding: 4px;
}

.copy-action-icon:active {
  transform: scale(0.9);
  opacity: 0.7;
}

:deep(.invite-share-popup .van-overlay),
:deep(.qr-popup .van-overlay),
:deep(.poster-popup .van-overlay) {
  background: rgb(var(--color-shadow-rgb) / 0.7) !important;
  backdrop-filter: blur(4px);
}

:deep(.qr-popup .van-popup) {
  background: var(--color-bg-input) !important;
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.2) !important;
}

.qr-popup-content {
  padding: 24px 20px 32px;
  background: var(--color-bg-input);
  border-radius: 20px;
  min-width: 300px;
  max-width: 90vw;
}

.qr-popup-header,
.poster-popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.qr-code-wrapper {
  background: var(--color-qr-light);
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgb(var(--color-shadow-rgb) / 0.3);
}

.qr-canvas {
  display: block;
}

.qr-tip {
  font-size: 14px;
  color: var(--color-text-secondary);
  text-align: center;
}

:deep(.poster-popup .van-popup) {
  background: var(--color-bg-input) !important;
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.2) !important;
  max-width: 95vw;
  max-height: 95vh;
  overflow: hidden !important;
  display: flex;
  flex-direction: column;
}

.poster-popup-content {
  padding: 20px;
  background: var(--color-bg-input);
  border-radius: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(95vh - 40px);
  display: flex;
  flex-direction: column;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.poster-popup-content::-webkit-scrollbar {
  display: none;
}

.poster-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.poster-container::-webkit-scrollbar {
  display: none;
}

.poster-canvas-wrapper {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.poster-content {
  position: relative;
  width: 100%;
  padding: 40px 30px;
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-bg-card) 100%);
  border-radius: 20px;
  border: 2px solid rgb(var(--color-brand-legacy-rgb) / 0.3);
  box-shadow: 0 8px 32px rgb(var(--color-shadow-rgb) / 0.5);
  overflow: hidden;
  box-sizing: border-box;
}

.poster-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, rgb(var(--color-brand-legacy-rgb) / 0.15) 0%, transparent 70%);
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
  background: rgb(var(--color-brand-legacy-rgb) / 0.1);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgb(var(--color-brand-legacy-rgb) / 0.3);
  padding: 12px;
}

.poster-app-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-brand-legacy);
  letter-spacing: 2px;
}

.poster-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.poster-invite-code-section {
  background: rgb(var(--color-surface-rgb) / 0.8);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.2);
  position: relative;
  z-index: 1;
}

.poster-code-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: center;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.poster-code-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-brand-legacy);
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
  background: var(--color-qr-light);
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgb(var(--color-shadow-rgb) / 0.3);
}

.poster-footer {
  text-align: center;
  position: relative;
  z-index: 1;
}

.poster-footer-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.poster-actions {
  margin-top: 20px;
}

.save-poster-btn {
  background: linear-gradient(135deg, var(--color-brand-legacy) 0%, var(--color-brand) 100%);
  color: var(--color-text-on-accent);
  border: none;
  font-weight: 600;
  height: 48px;
  border-radius: 12px;
}

.save-poster-btn:active {
  opacity: 0.9;
}

/* =====================================================================
   深色主题 —— 仅覆盖颜色 / 背景 / 边框 / 阴影，几何与浅色完全一致，
   切换主题不产生位移（对齐 App 深色设计 token）。
   ===================================================================== */
:global(html[data-theme='dark']) .referral-page {
  background: #08111f !important;
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .custom-nav-bar {
  --van-nav-bar-background: #0f1726 !important;
  --van-nav-bar-title-text-color: #f8fafc !important;
  --van-nav-bar-icon-color: #cbd5e1 !important;
  border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page :deep(.custom-nav-bar .van-nav-bar__title) {
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .card {
  background: #151f31 !important;
  border-color: rgba(255, 255, 255, 0.07) !important;
  box-shadow: none !important;
}

:global(html[data-theme='dark']) .referral-page .hero-card {
  background:
    radial-gradient(circle at 90% 18%, rgba(245, 181, 27, 0.14), transparent 40%),
    #151f31 !important;
}

:global(html[data-theme='dark']) .referral-page .card-title,
:global(html[data-theme='dark']) .referral-page .card-title .van-icon {
  color: #f8fafc !important;
}

/* 通知横条 */
:global(html[data-theme='dark']) .referral-page .notice-bar {
  background: #0f1726 !important;
  border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .notice-icon,
:global(html[data-theme='dark']) .referral-page .notice-text,
:global(html[data-theme='dark']) .referral-page .notice-time {
  color: #94a3b8 !important;
}

/* 主卡片 */
:global(html[data-theme='dark']) .referral-page .hero-tag {
  background: rgba(255, 255, 255, 0.06) !important;
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .hero-commission {
  background: rgba(245, 181, 27, 0.16) !important;
  color: #f5b51b !important;
}

:global(html[data-theme='dark']) .referral-page .hero-label {
  color: #cbd5e1 !important;
}

:global(html[data-theme='dark']) .referral-page .hero-number {
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .hero-unit {
  color: #f5b51b !important;
}

:global(html[data-theme='dark']) .referral-page .hero-chip {
  background: #111a2b !important;
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .hero-chip .van-icon {
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .btn-outline {
  background: #111a2b !important;
  color: #f8fafc !important;
  border-color: rgba(255, 255, 255, 0.18) !important;
}

/* 邀请链接 */
:global(html[data-theme='dark']) .referral-page .link-row + .link-row {
  border-top-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .link-icon {
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .link-text {
  color: #cbd5e1 !important;
}

:global(html[data-theme='dark']) .referral-page .copy-btn {
  color: #f5b51b !important;
}

/* 返佣设置 */
:global(html[data-theme='dark']) .referral-page .share-label {
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .share-value {
  color: #f8fafc !important;
}

/* 数据四宫格 */
:global(html[data-theme='dark']) .referral-page .stat-cell:nth-child(odd) {
  border-right-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .stat-cell:nth-child(-n + 2) {
  border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .stat-icon.gray,
:global(html[data-theme='dark']) .referral-page .stat-icon.lvl {
  background: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .stat-icon.gray {
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .stat-icon.lvl {
  color: #f5b51b !important;
}

:global(html[data-theme='dark']) .referral-page .stat-icon.gold {
  background: rgba(245, 181, 27, 0.12) !important;
  color: #f5b51b !important;
}

:global(html[data-theme='dark']) .referral-page .stat-icon.green {
  background: rgba(22, 199, 132, 0.12) !important;
  color: #16c784 !important;
}

:global(html[data-theme='dark']) .referral-page .stat-label,
:global(html[data-theme='dark']) .referral-page .stat-unit,
:global(html[data-theme='dark']) .referral-page .stat-progress-text {
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .stat-value {
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .stat-value.green-text,
:global(html[data-theme='dark']) .referral-page .stat-value.green-text .stat-unit {
  color: #16c784 !important;
}

:global(html[data-theme='dark']) .referral-page .stat-value.level {
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .stat-value.level .lv {
  color: #f5b51b !important;
}

:global(html[data-theme='dark']) .referral-page .stat-progress {
  background: rgba(255, 255, 255, 0.10) !important;
}

/* 记录 */
:global(html[data-theme='dark']) .referral-page :deep(.record-tabs .van-tabs__wrap) {
  border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .record-item + .record-item {
  border-top-color: rgba(255, 255, 255, 0.06) !important;
}

:global(html[data-theme='dark']) .referral-page .record-avatar {
  background: rgba(245, 181, 27, 0.16) !important;
  color: #f5b51b !important;
}

:global(html[data-theme='dark']) .referral-page .record-user {
  color: #f8fafc !important;
}

:global(html[data-theme='dark']) .referral-page .record-time,
:global(html[data-theme='dark']) .referral-page .record-desc {
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .record-status.active {
  background: rgba(22, 199, 132, 0.14) !important;
  color: #16c784 !important;
}

:global(html[data-theme='dark']) .referral-page .record-status.inactive {
  background: rgba(255, 255, 255, 0.06) !important;
  color: #94a3b8 !important;
}

:global(html[data-theme='dark']) .referral-page .record-amount {
  color: #16c784 !important;
}

:global(html[data-theme='dark']) .referral-page .empty-text {
  color: #94a3b8 !important;
}
</style>
