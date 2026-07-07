<template>
  <div class="referral-page" ref="pageRef">
    <!-- 闁煎啿鏈▍娆撳礂婢跺顎為柡浣哥墛閻?-->
    <div class="background-glow"></div>
    
    <!-- 婵炲苯顦伴煫鍫濐嚕韫囨搩鍤ら柤鍓蹭簼閻?-->
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

    <!-- 濞戞挻妲掗々锕傚礃閸涱収鍟囬柛鏍ф惈閻?-->
    <div class="referral-content">
      <!-- 濡炪倕鐖奸崕鎾焻濮橆剚鍟為柡宥呴獜缁辨瑧鎹勯幋锔规敩闁诲浚鍨界槐?-->
      <div class="announcement-marquee">
        <div class="marquee-wrapper" :style="{ animationDuration: marqueeSpeed + 's' }">
          <div 
            v-for="(announcement, index) in announcements" 
            :key="`first-${index}`"
            class="marquee-item"
          >
            <span class="marquee-icon">
              <van-icon :name="announcement.icon" />
            </span>
            <span class="marquee-text">{{ announcement.text }}</span>
          </div>
          <div 
            v-for="(announcement, index) in announcements" 
            :key="`second-${index}`"
            class="marquee-item"
          >
            <span class="marquee-icon">
              <van-icon :name="announcement.icon" />
            </span>
            <span class="marquee-text">{{ announcement.text }}</span>
          </div>
        </div>
      </div>

      <!-- 闁哄秶顭堢缓楣冨绩閸撲焦鎶勯柣顏勵儐濠?-->
      <div class="hero-section glass-card">
        <div class="hero-orb hero-orb-a"></div>
        <div class="hero-orb hero-orb-b"></div>
        <div class="hero-content">
          <div class="coin-icon-wrapper">
            <div class="coin-icon-3d">
              <van-icon name="gold-coin-o" size="48" color="var(--color-brand-legacy)" />
            </div>
          </div>
          <div class="hero-stats">
            <div class="hero-kicker">{{ t('referral.title') }}</div>
            <div class="hero-label">{{ t('referral.total_earned') }} (USDT)</div>
            <div class="hero-value gold-text">
              {{ formatNumber(animatedTotalEarned) }}
            </div>
            <div class="hero-meta">
              <span>{{ t('referral.invite_count') }} {{ inviteCount }}</span>
              <span>{{ t('referral.total_commission') }} 40%</span>
            </div>
          </div>
        </div>
        <div class="rebate-action-row">
          <button class="hero-invite-button" type="button" @click="handleInvite">
            <van-icon name="friends-o" size="18" />
            <span>立即邀请</span>
          </button>
        <van-button 
          class="withdraw-btn"
          type="primary"
          block
          @click="goToWithdraw"
        >
          {{ t('referral.go_withdraw') }}
        </van-button>
        </div>
      </div>

      <div class="invite-link-card glass-card">
        <div class="section-title-row">
          <van-icon name="link-o" />
          <span>邀请链接</span>
        </div>
        <div class="invite-link-row">
          <van-icon name="coupon-o" />
          <span>{{ inviteCode }}</span>
          <button type="button" @click="handleCopyCode">
            <van-icon name="copy-o" />
            复制
          </button>
        </div>
        <div class="invite-link-row">
          <van-icon name="globe-o" />
          <span>{{ inviteLink.replace(/^https?:\/\//, '') }}</span>
          <button type="button" @click="handleCopyLink">
            <van-icon name="copy-o" />
            复制
          </button>
        </div>
      </div>

      <!-- 閺夆晜鏌ч崜鎴犳媼閸撗呮瀭濞戞挸楠搁崹搴㈢?-->
      <div class="action-section glass-card">
        <div class="action-header">
          <div>
            <div class="section-eyebrow">{{ splitLabel }}</div>
            <div class="header-title">{{ t('referral.commission_setting') }}</div>
          </div>
          <div class="header-total gold-text">{{ t('referral.total_commission') }} 40%</div>
        </div>

        <!-- 婵絾鏌х欢銉ヮ煥閹存繃鍋?-->
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
            active-color="var(--color-brand-legacy)"
            inactive-color="rgb(var(--color-border-rgb) / 0.1)"
            bar-height="4px"
            button-size="20px"
            class="commission-slider"
          />
        </div>

        <!-- 濠㈣泛绉撮崺妤呭礌?-->
        <div class="copy-section">
          <div class="copy-item">
            <div class="copy-label">{{ t('referral.invite_code') }}</div>
            <div class="copy-value-wrapper">
              <div class="copy-value">{{ inviteCode }}</div>
              <button class="copy-pill" type="button" @click="handleCopyCode">
                <van-icon name="copy" size="16" />
                {{ copyActionLabel }}
              </button>
            </div>
          </div>
          <div class="copy-item">
            <div class="copy-label">{{ t('referral.invite_link') }}</div>
            <div class="copy-value-wrapper">
              <div class="copy-value link-value">{{ inviteLink }}</div>
              <button class="copy-pill" type="button" @click="handleCopyLink">
                <van-icon name="copy" size="16" />
                {{ copyActionLabel }}
              </button>
            </div>
          </div>
        </div>

        <!-- 缂佹柨顑呭畵鍡涙焽閳ь剛鎷犻柨瀣樆闂?-->
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

      <!-- 闁轰胶澧楀畵浣圭椤忓洢鈧啴鎯?-->
      <div class="dashboard-section">
        <div class="dashboard-grid">
          <div class="dashboard-card glass-card">
            <div class="dashboard-icon">
              <van-icon name="friends-o" size="24" color="var(--color-brand-legacy)" />
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
              <van-icon name="balance-o" size="24" color="var(--color-brand-legacy)" />
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
              <van-icon name="gold-coin-o" size="24" color="var(--color-earn)" />
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
              <van-icon name="medal-o" size="24" color="var(--color-brand-legacy)" />
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

      <!-- 闂侇厸鍋撻悹鍥╂焿椤斿洩銇愰弴鐐茬仚閻?-->
      <div class="records-section glass-card">
        <van-tabs 
          v-model:active="activeRecordTab" 
          background="transparent" 
          title-active-color="var(--color-brand-legacy)" 
          title-inactive-color="var(--color-text-secondary)" 
          line-width="30px" 
          line-height="3px" 
          color="var(--color-brand-legacy)" 
          :border="false"
          class="record-tabs"
        >
          <van-tab :title="t('referral.invite_records')">
            <div class="records-list">
              <div v-if="inviteRecords.length === 0" class="empty-state">
                <div class="empty-icon">
                  <van-icon name="friends-o" size="64" color="var(--color-text-secondary)" />
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
                  <van-icon name="gold-coin-o" size="64" color="var(--color-text-secondary)" />
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

    <!-- 闂侇厸鍋撻悹鍥у槻閸ㄥ孩绂嶉銏ｅ墾缂?-->
    <van-popup
      v-model:show="showInvitePopup"
      position="bottom"
      :style="{ height: 'auto', maxHeight: '80vh' }"
      round
      class="invite-share-popup"
      :close-on-click-overlay="true"
    >
      <div class="invite-popup-content">
        <!-- 鐎殿喖婀遍悰銉﹀緞閹绢喖鍔?-->
        <div class="invite-popup-header">
          <div class="popup-title">{{ t('referral.invite_now') }}</div>
          <van-icon 
            name="cross" 
            @click="showInvitePopup = false" 
            class="popup-close-icon"
          />
        </div>

        <!-- 闁告帒妫旈棅鈺呮焻婢舵劑鈧?-->
        <div class="share-options">
          <div 
            class="share-option-item"
            @click="handleShareLink"
          >
            <div class="share-icon-wrapper">
              <van-icon name="link-o" size="32" color="var(--color-brand-legacy)" />
            </div>
            <div class="share-label">{{ t('referral.share_link') }}</div>
          </div>

          <div 
            class="share-option-item"
            @click="handleShareQR"
          >
            <div class="share-icon-wrapper">
              <van-icon name="qr-invalid" size="32" color="var(--color-brand-legacy)" />
            </div>
            <div class="share-label">{{ t('referral.share_qr') }}</div>
          </div>

          <div 
            class="share-option-item"
            @click="handleShareImage"
          >
            <div class="share-icon-wrapper">
              <van-icon name="photo-o" size="32" color="var(--color-brand-legacy)" />
            </div>
            <div class="share-label">{{ t('referral.share_image') }}</div>
          </div>
        </div>

        <!-- 闂侇厸鍋撻悹鍥棑閻栨粓宕畝鍕嚑闁规亽鍎遍惈宥囩矆?-->
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

    <!-- 濞存粌鐬煎ǎ顕€鎯嶆担姝屽墾缂?-->
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

    <!-- 婵炴挳鏀辨慨銈咁嚕閸︻厾宕?-->
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
            <!-- 婵炴挳鏀辨慨銈夊礃閸涱収鍟?-->
            <div class="poster-content">
              <!-- 闁煎啿鏈▍娆忋€掗幇顒€缍?-->
              <div class="poster-bg"></div>
              
              <!-- Logo 闁告牕鎼悡?-->
              <div class="poster-logo-section">
                <div class="poster-logo">
                  <BinanceLogo :size="40" class="logo-img" />
                </div>
                <div class="poster-app-name">TruthFi</div>
              </div>

              <!-- 濞戞挾绮悥锝嗭紣?-->
              <div class="poster-title">{{ t('referral.invite_now') }}</div>
              
              <!-- 闂侇厸鍋撻悹鍥棑閻?-->
              <div class="poster-invite-code-section">
                <div class="poster-code-label">{{ t('referral.invite_code') }}</div>
                <div class="poster-code-value">{{ inviteCode }}</div>
              </div>

              <!-- 濞存粌鐬煎ǎ顕€鎯?-->
              <div class="poster-qr-section">
                <canvas ref="posterQRCanvas" class="poster-qr-canvas"></canvas>
              </div>

              <!-- 閹煎瓨娲熼崕鎾箵閹邦喓浠?-->
              <div class="poster-footer">
                <div class="poster-footer-text">{{ t('referral.scan_to_join') }}</div>
              </div>
            </div>
          </div>
          
          <!-- 闁瑰灝绉崇紞鏃堝箰婢舵劖灏?-->
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
import { getThemeColor } from '@/styles/theme';
import { useAssetActions } from '@/composables/useAssetActions';

defineOptions({
  name: 'ReferralIndex'
});

const router = useRouter();
const { t, locale } = useI18n();
const { openWithdraw } = useAssetActions();

// 濡炪倗鏁诲鏉款嚕閺囩姵鏆忛柨娑樼墢閺併倖绂嶆惔銏㈡硦闁告柣鍔庡ú鍐触椤掑﹦绀?
const pageRef = ref(null);

// 婵犲﹥鑹炬慨鈺呮偐閼哥鍋?
const isScrolled = ref(false);

// 闁轰焦婢橀悺褍顭ㄥ顒€袟闁告柣鍔庨弫?Hook
const useCountUp = (targetValue, duration = 1500) => {
  const currentValue = ref(0);
  let animationFrame = null;
  let startTime = null;
  let startValue = 0;

  const animate = (timestamp) => {
    if (!startTime) startTime = timestamp;
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // 濞达綀娉曢弫?easeOutQuart 缂傚倹鎸告慨鈺呭礄閼恒儲娈?
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

// 缂備胶鍠曢鎼佸极閻楀牆绁?
const totalEarned = 12450.88;
const inviteCount = 12;
const tradingVolume = 1200000; // $1.2M
const yesterdayEarnings = 124.50;
const currentLevel = 'Lv.2 \u9ed1\u91d1';
const needMoreForNextLevel = 3;

// 濞达綀娉曢弫?useCountUp Hook
const { currentValue: animatedTotalEarned, start: startTotalEarned } = useCountUp(totalEarned, 1500);
const { currentValue: animatedInviteCount, start: startInviteCount } = useCountUp(inviteCount, 1500);

// 閺夆晜鏌ч崜鎴犳媼閸撗呮瀭
const myShare = ref(20);
const friendShare = computed(() => 40 - myShare.value);

// 闂侇厸鍋撻悹鍥棑閻栨粓宕畝鍕嚑闁?
const inviteCode = ref('829301');
const inviteLink = computed(() => `https://truthfi.app/invite/${inviteCode.value}`);
const isChineseLocale = computed(() => String(locale.value).toLowerCase().startsWith('zh'));
const copyActionLabel = computed(() => isChineseLocale.value ? '\u590d\u5236' : 'Copy');
const splitLabel = computed(() => isChineseLocale.value ? '\u8fd4\u4f63\u5206\u914d' : 'Reward Split');

// 闂侇偅鑹鹃幉锟犲冀韫囨梹娈堕柟?
const announcements = computed(() => [
  { icon: 'volume-o', text: 'Alex 成功邀请 5 人，获得 250 USDT 返佣' },
  { icon: 'friends-o', text: t('referral.announcement_invite', { user: 'Alex', count: '5' }) },
  { icon: 'gold-coin-o', text: t('referral.announcement_earn', { user: 'User_1234', amount: '120.50' }) }
]);

const marqueeSpeed = computed(() => announcements.value.length * 4);

// 闂侇厸鍋撻悹鍥╂焿椤斿洩銇?
const inviteRecords = ref([
  { user: 'User_8829', registerTime: Date.now() - 86400000 * 2, status: 'active' },
  { user: 'User_1234', registerTime: Date.now() - 86400000 * 5, status: 'active' },
  { user: 'User_5678', registerTime: Date.now() - 86400000 * 10, status: 'inactive' }
]);

// 閺夆晜鏌ч崜鎴﹀及鎼达絿鐭?
const commissionRecords = ref([
  { user: 'User_8829', type: t('referral.commission_spot'), amount: 12.50, time: Date.now() - 3600000 },
  { user: 'User_1234', type: t('referral.commission_earn'), amount: 8.30, time: Date.now() - 7200000 },
  { user: 'User_5678', type: t('referral.commission_futures'), amount: 15.20, time: Date.now() - 10800000 }
]);

// 缂佹稑顦辨鍥ㄦ交濞戞ê顔?
const levelProgress = computed(() => {
  // 闁稿娲╅鏇°亹閹惧啿顤呯紒娑橆槺妤犲洭妫侀埀顒傛啺?0濞存粎灏ㄧ槐婵嗩啅閺屻儱鈧鎷?2濞存粎灏ㄧ槐婵囨交濞戞ê顔婂☉?20%闁挎稑濂旂徊楣冨及閸撗佷粵濞?00%
  const currentLevelRequirement = 10;
  const nextLevelRequirement = 15;
  const progress = ((inviteCount - currentLevelRequirement) / (nextLevelRequirement - currentLevelRequirement)) * 100;
  return Math.min(Math.max(progress, 0), 100);
});

// 闁哄秶鍘х槐锟犲礌閺嶃劍娈堕悗?
const formatNumber = (value) => {
  return value.toLocaleString('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  });
};

// 闁哄秶鍘х槐锟犲礌閺嶏附鍞夐柡鍕崌椤?
const formatTradingVolume = (value) => {
  if (value >= 1000000) {
    return '$' + (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return '$' + (value / 1000).toFixed(0) + 'K';
  }
  return '$' + value.toLocaleString('en-US');
};

// 闁硅　鏅濋悥婊堟偨閵婏箑鐓曢悹鎰剁畱瑜?
const maskUser = (user) => {
  if (user.length <= 6) return user;
  return user.slice(0, 3) + '***' + user.slice(-3);
};

// 闁哄秶鍘х槐锟犲礌閺嶃劍顦ч梻?
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

// 闁兼儳鍢茶ぐ鍥偐閼哥鍋撴担鍦灱缂?
const getStatusLabel = (status) => {
  if (status === 'active') {
    return t('referral.status_active');
  } else if (status === 'inactive') {
    return t('referral.status_inactive');
  }
  return status;
};

// 濠㈣泛绉撮崺妤呮焽閳ь剛鎷犳搴ｅ灣
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

// 濠㈣泛绉撮崺妤呮焽閳ь剛鎷犻悜鑺ユ嚑闁?
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

// 闁告绮ぐ渚€鎮?
const goToWithdraw = () => {
  openWithdraw('USDT');
};

// 鐎殿喖婀遍悰銉╁及閸撗佷粵闁绘鍩栭埀?
const showInvitePopup = ref(false);
const showQRPopup = ref(false);
const showPosterPopup = ref(false);

// 濞存粌鐬煎ǎ顕€鎯嶆担鍛婂婵炴挳鏀辨慨銈夋儎缁嬪灝褰犵€殿喗娲滈弫?
const qrCanvas = ref(null);
const posterQRCanvas = ref(null);
const posterRef = ref(null);

// 缂佹柨顑呭畵鍡涙焽閳ь剛鎷?
const handleInvite = () => {
  showInvitePopup.value = true;
};

// 闁告帒妫旈棅鈺呮煣閻愵剙澶?
const handleShareLink = () => {
  handleCopyLink();
  showInvitePopup.value = false;
};

// 闁汇垻鍠愰崹姘瀹€鈧ǎ顕€鎯?
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
    console.error('闁汇垻鍠愰崹姘瀹€鈧ǎ顕€鎯嶆担鎼炰杭閻?', error);
    showToast({
      message: t('referral.qr_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 闁告帒妫旈棅鈺傜瀹€鈧ǎ顕€鎯?
const handleShareQR = async () => {
  showInvitePopup.value = false;
  showQRPopup.value = true;
  
  await nextTick();
  if (qrCanvas.value) {
    await generateQRCode(qrCanvas.value, inviteLink.value, 250);
  }
};

// 闁汇垻鍠愰崹姘归柨瀣?
const generatePoster = async () => {
  showInvitePopup.value = false;
  showPosterPopup.value = true;
  
  await nextTick();
  
  // 闁稿繐鐗忛弫鎾诲箣閹邦厽宕抽柟韬插劙閼垫垿鎯冮崟顏嗙檶缂備礁顕悥?
  if (posterQRCanvas.value) {
    await generateQRCode(posterQRCanvas.value, inviteLink.value, 180);
  }
  
  // 缂佹稑顦欢鐔哥瀹€鈧ǎ顕€鎯嶆担纭咁洬闁哄本鎸搁悾顒勫箣?
  await new Promise(resolve => setTimeout(resolve, 300));
};

// 闁告帒妫旈棅鈺呭炊閸撗冾暬闁挎稑鐗忛弫鎾诲箣閹邦厽宕抽柟韬插劵缁?
const handleShareImage = async () => {
  await generatePoster();
};

// 濞ｅ洦绻傞悺銊ッ归柨瀣?
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
    // 濞达綀娉曢弫?html2canvas 闁汇垻鍠愰崹姘跺炊閸撗冾暬
    const canvas = await html2canvas(posterRef.value, {
      backgroundColor: getThemeColor('--color-bg'),
      scale: 2, // 闁圭粯鍔欓悵顔笺€掗崨顔界彴閹?
      useCORS: true,
      logging: false,
      width: posterRef.value.offsetWidth,
      height: posterRef.value.offsetHeight
    });

    // 閺夌儐鍓氬畷鍙夌▔?blob
    canvas.toBlob((blob) => {
      if (!blob) {
        showToast({
          message: t('referral.poster_generate_failed'),
          icon: 'fail',
          duration: 2000
        });
        return;
      }

      // 闁告帗绋戠紓鎾寸▔鐎ｎ厽绁伴梺鍓у亾鐢?
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
    console.error('闁汇垻鍠愰崹姘归柨瀣撳鎯扮簿鐟?', error);
    showToast({
      message: t('referral.poster_generate_failed'),
      icon: 'fail',
      duration: 2000
    });
  }
};

// 婵犲﹥鑹炬慨鈺呮儎閹存繃鍎?
const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  isScrolled.value = scrollTop > 10;
};

// 闁哄秴娲ㄩ閿嬨亜闂堟稑鐎奸柟?
const activeRecordTab = ref(0);

onMounted(() => {
  // 闁告凹鍨版慨鈺呭极閺夎法鎽熸繝濠冭壘婵晠宕濋妸褎鏆?
  startTotalEarned(totalEarned);
  startInviteCount(inviteCount);
  
  // 闁烩晜鍨甸幆澶婎煥濮橆剙袟
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // 闁告帗绻傞～鎰涢埀顒勫蓟?
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.referral-page {
  min-height: 100vh;
  background-color: var(--color-bg);
  color: var(--color-text-primary);
  position: relative;
  overflow-x: hidden;
  padding-bottom: 80px;
}

/* 闁煎啿鏈▍娆撳礂婢跺顎為柡浣哥墛閻?*/
.background-glow {
  position: fixed;
  top: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(
    circle,
    rgb(var(--color-brand-legacy-rgb) / 0.15) 0%,
    rgb(var(--color-brand-rgb) / 0.08) 30%,
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

/* 婵炲苯顦伴煫鍫濐嚕韫囨搩鍤ら柤鍓蹭簼閻?*/
.custom-nav-bar {
  --van-nav-bar-background: transparent;
  --van-nav-bar-title-text-color: var(--color-text-primary);
  --van-nav-bar-icon-color: var(--color-brand-legacy);
  --van-nav-bar-height: 46px;
  backdrop-filter: blur(10px);
  transition: background-color 0.3s ease;
  position: relative;
  z-index: 100;
}

.custom-nav-bar.scrolled {
  --van-nav-bar-background: rgb(var(--color-bg-rgb) / 0.95);
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  font-weight: 700 !important;
  font-size: 18px !important;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

/* 濞戞挻妲掗々锕傚礃閸涱収鍟?*/
.referral-content {
  position: relative;
  z-index: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
}

/* 濡炪倕鐖奸崕鎾焻濮橆剚鍟為柡宥呴獜缁辨瑧鎹勯幋锔规敩闁诲浚鍨界槐?*/
.announcement-marquee {
  height: 32px;
  background: rgb(var(--color-surface-rgb) / 0.6);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgb(var(--color-brand-rgb) / 0.1);
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
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.marquee-icon {
  width: 22px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgb(var(--color-brand-legacy-rgb) / 0.12);
  color: var(--color-brand-legacy);
  font-size: 14px;
  flex: 0 0 22px;
}

.marquee-text {
  color: var(--color-text-primary);
}

/* 缁句勘鍔庨悥鐐烘偝閼姐倖瀚呴柛妤嬬磿婢?*/
.glass-card {
  background: rgb(var(--color-surface-rgb) / 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.2);
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
    rgb(var(--color-brand-legacy-rgb) / 0.5) 50%,
    transparent 100%
  );
}

.glass-card:active {
  transform: scale(0.98);
  border-color: rgb(var(--color-brand-legacy-rgb) / 0.4);
}

/* 闁哄秶顭堢缓楣冨绩閸撲焦鎶勯柣顏勵儐濠?*/
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
  background: linear-gradient(135deg, rgb(var(--color-brand-legacy-rgb) / 0.2) 0%, rgb(var(--color-brand-rgb) / 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8px 16px rgb(var(--color-brand-legacy-rgb) / 0.2),
    inset 0 2px 4px rgb(var(--color-border-rgb) / 0.1);
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
  color: var(--color-text-secondary);
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
  color: var(--color-brand-legacy);
  text-shadow: 0 0 10px rgb(var(--color-brand-legacy-rgb) / 0.3);
}

.text-green {
  color: var(--color-earn);
}

.withdraw-btn {
  height: 44px;
  background: linear-gradient(135deg, var(--color-brand-legacy) 0%, var(--color-brand) 100%);
  color: var(--color-text-on-accent);
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 4px 12px rgb(var(--color-brand-legacy-rgb) / 0.3);
}

.withdraw-btn:active {
  opacity: 0.9;
  transform: scale(0.98);
}

/* 閺夆晜鏌ч崜鎴犳媼閸撗呮瀭濞戞挸楠搁崹搴㈢?*/
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
  color: var(--color-text-primary);
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
  color: var(--color-text-secondary);
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
  background: var(--color-brand-legacy);
  box-shadow: 0 2px 8px rgb(var(--color-brand-legacy-rgb) / 0.4);
  border: 2px solid var(--color-bg);
}

:deep(.commission-slider .van-slider__bar) {
  background: var(--color-brand-legacy);
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
  color: var(--color-text-secondary);
  font-weight: 500;
}

.copy-value-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgb(var(--color-shadow-rgb) / 0.3);
  border-radius: 8px;
  border: 1px solid rgb(var(--color-brand-rgb) / 0.2);
}

.copy-value {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  color: var(--color-brand-legacy);
  word-break: break-all;
}

.link-value {
  font-size: 12px;
  color: var(--color-text-secondary);
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
  background: linear-gradient(135deg, var(--color-brand-legacy) 0%, var(--color-brand) 100%);
  color: var(--color-text-on-accent);
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgb(var(--color-brand-legacy-rgb) / 0.3);
  margin-top: 8px;
}

.invite-btn:active {
  opacity: 0.9;
  transform: scale(0.98);
}

/* 闁轰胶澧楀畵浣圭椤忓洢鈧啴鎯?*/
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
  background: rgb(var(--color-brand-legacy-rgb) / 0.15);
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
  color: var(--color-text-secondary);
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
  background: rgb(var(--color-border-rgb) / 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand-legacy) 0%, var(--color-brand) 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
  box-shadow: 0 0 8px rgb(var(--color-brand-legacy-rgb) / 0.4);
}

.progress-text {
  font-size: 10px;
  color: var(--color-text-secondary);
}

/* 闂侇厸鍋撻悹鍥╂焿椤斿洩銇愰弴鐐茬仚閻?*/
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
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.05);
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
  color: var(--color-text-secondary);
  margin-bottom: 24px;
}

.empty-action-btn {
  padding: 10px 24px;
  background: rgb(var(--color-brand-legacy-rgb) / 0.15);
  color: var(--color-brand-legacy);
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.3);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.empty-action-btn:active {
  background: rgb(var(--color-brand-legacy-rgb) / 0.25);
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
  background: rgb(var(--color-shadow-rgb) / 0.2);
  border-radius: 12px;
  border: 1px solid rgb(var(--color-border-rgb) / 0.05);
  transition: all 0.2s ease;
}

.record-item:active {
  background: rgb(var(--color-shadow-rgb) / 0.3);
  border-color: rgb(var(--color-brand-legacy-rgb) / 0.2);
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
  background: linear-gradient(135deg, rgb(var(--color-brand-legacy-rgb) / 0.3) 0%, rgb(var(--color-brand-rgb) / 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-brand-legacy);
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
  color: var(--color-text-primary);
}

.record-time,
.record-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
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
  background: rgb(var(--color-earn-rgb) / 0.15);
  color: var(--color-earn);
}

.record-status.inactive {
  background: rgb(var(--color-text-muted-rgb) / 0.15);
  color: var(--color-text-secondary);
}

.record-amount {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', 'Roboto', 'Helvetica Neue', 'Arial', monospace !important;
}


/* Premium referral UI refresh */
.referral-page {
  background:
    radial-gradient(circle at 16% 2%, rgb(var(--color-brand-legacy-rgb) / 0.18), transparent 28%),
    linear-gradient(180deg, var(--color-surface-1) 0%, var(--color-bg) 48%, var(--color-surface-1) 100%);
}

.announcement-marquee {
  height: 34px;
  background: rgb(var(--color-surface-2-rgb) / 0.82);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--color-border-subtle);
}

.marquee-text {
  font-weight: 700;
}

.glass-card {
  background: linear-gradient(180deg, rgb(var(--color-surface-rgb) / 0.96), rgb(var(--color-surface-2-rgb) / 0.92));
  border: 1px solid rgb(var(--color-border-rgb) / 0.9);
  border-radius: 22px;
  box-shadow: 0 16px 36px rgb(var(--color-shadow-rgb) / 0.08);
}

.glass-card:active {
  transform: translateY(1px);
}

.hero-section {
  padding: 26px;
  background:
    linear-gradient(135deg, rgb(var(--color-surface-rgb) / 0.98), rgb(var(--color-brand-legacy-rgb) / 0.08)),
    var(--color-surface-2);
}

.hero-orb {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
  filter: blur(2px);
}

.hero-orb-a {
  width: 190px;
  height: 190px;
  right: -82px;
  top: -72px;
  background: radial-gradient(circle, rgb(var(--color-brand-legacy-rgb) / 0.22), transparent 68%);
}

.hero-orb-b {
  width: 120px;
  height: 120px;
  left: -48px;
  bottom: -44px;
  background: radial-gradient(circle, rgb(var(--color-primary-rgb) / 0.13), transparent 70%);
}

.hero-content,
.withdraw-btn {
  position: relative;
  z-index: 1;
}

.coin-icon-3d {
  width: 86px;
  height: 86px;
  background:
    radial-gradient(circle at 35% 30%, rgb(var(--color-surface-rgb) / 0.9), transparent 36%),
    linear-gradient(135deg, rgb(var(--color-brand-legacy-rgb) / 0.24) 0%, rgb(var(--color-brand-rgb) / 0.12) 100%);
  box-shadow: 0 18px 34px rgb(var(--color-brand-legacy-rgb) / 0.22), inset 0 2px 4px rgb(var(--color-border-rgb) / 0.1);
}

.hero-kicker,
.section-eyebrow {
  width: fit-content;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgb(var(--color-brand-legacy-rgb) / 0.11);
  color: var(--color-primary-hover);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.hero-value {
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -0.03em;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-meta span {
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border-subtle);
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 800;
}

.withdraw-btn {
  height: 48px;
  background: var(--color-surface-2);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-strong);
  border-radius: 14px;
  font-weight: 900;
  box-shadow: var(--shadow-sm);
}

.action-section {
  gap: 18px;
}

.header-title {
  margin-top: 8px;
  font-size: 20px;
  font-weight: 900;
}

.header-total {
  padding: 8px 11px;
  border-radius: 999px;
  background: rgb(var(--color-brand-legacy-rgb) / 0.1);
  font-size: 13px;
  font-weight: 900;
}

.slider-container {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgb(var(--color-surface-rgb) / 0.75), rgb(var(--color-surface-2-rgb) / 0.5));
  border: 1px solid var(--color-border-subtle);
}

.copy-value-wrapper {
  padding: 10px 10px 10px 14px;
  background: var(--color-surface-1);
  border-radius: 14px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.copy-pill {
  flex: 0 0 auto;
  border: 0;
  border-radius: 999px;
  padding: 8px 11px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgb(var(--color-brand-legacy-rgb) / 0.13);
  color: var(--color-primary-hover);
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
}

.copy-pill:active {
  transform: scale(0.96);
}

.invite-btn {
  height: 52px;
  border-radius: 16px;
  font-weight: 900;
  box-shadow: 0 14px 28px rgb(var(--color-brand-legacy-rgb) / 0.24);
}

.dashboard-grid {
  gap: 14px;
}

.dashboard-card {
  min-height: 118px;
  padding: 18px;
  border-radius: 18px;
}

.dashboard-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
}

.dashboard-label {
  text-transform: none;
  letter-spacing: 0;
  font-size: 12px;
}

.dashboard-value {
  font-size: 24px;
  font-weight: 900;
}

.records-section {
  padding: 8px 0 20px;
}

:deep(.record-tabs .van-tabs__wrap) {
  border-bottom: 0;
}

:deep(.record-tabs .van-tab) {
  font-size: 15px;
  font-weight: 900;
}

.records-list {
  padding: 18px 20px;
}

.records-content {
  gap: 10px;
}

.record-item {
  padding: 14px;
  background: var(--color-surface-1);
  border-radius: 16px;
  border: 1px solid var(--color-border-subtle);
  box-shadow: var(--shadow-sm);
}

.record-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, rgb(var(--color-brand-legacy-rgb) / 0.24) 0%, rgb(var(--color-brand-rgb) / 0.12) 100%);
}

.record-user {
  font-size: 15px;
  font-weight: 900;
}

.record-status {
  border-radius: 999px;
  padding: 5px 10px;
}
/* 缁绢収鍠曠换?Vant 闁搞儳鍋撻悥锝団偓娑欍仦缂嶅绋夊鍫蕉闁稿繈鍔岄惇顒傗偓娑欍仦缂嶅鎲伴崱娆愮０ */
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

/* 闂侇厸鍋撻悹鍥у槻閸ㄥ孩绂嶉銏ｅ墾缂佹劖顨嗛悧鍗烆嚕?*/
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
  transition: all 0.2s ease;
  padding: 4px;
}

.popup-close-icon:active {
  color: var(--color-brand-legacy);
  transform: scale(0.9);
}

/* 闁告帒妫旈棅鈺呮焻婢舵劑鈧?*/
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
  transition: all 0.3s ease;
}

.share-option-item:active .share-icon-wrapper {
  background: rgb(var(--color-brand-legacy-rgb) / 0.2);
  border-color: rgb(var(--color-brand-legacy-rgb) / 0.4);
  box-shadow: 0 0 12px rgb(var(--color-brand-legacy-rgb) / 0.3);
}

.share-label {
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 500;
  text-align: center;
}

/* 闂侇厸鍋撻悹鍥腹娣囧﹪骞侀姘殬闁?*/
.invite-info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: rgb(var(--color-surface-rgb) / 0.6);
  backdrop-filter: blur(10px);
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

/* 鐎殿喖婀遍悰銉╂焼椤旀儳鍏婇悘?*/
:deep(.invite-share-popup .van-overlay) {
  background: rgb(var(--color-shadow-rgb) / 0.7) !important;
  backdrop-filter: blur(4px);
}

/* 濞存粌鐬煎ǎ顕€鎯嶆担姝屽墾缂佹劖顨嗛悧鍗烆嚕?*/
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

/* 婵炴挳鏀辨慨銈咁嚕閸︻厾宕堕柡宥呭槻缁?*/
:deep(.poster-popup .van-popup) {
  background: var(--color-bg-input) !important;
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.2) !important;
  max-width: 95vw;
  max-height: 95vh;
  overflow: hidden !important; /* 闁衡偓闁稖绀?hidden闁挎稑鐭傚Σ璇差潰閵忕姴姣夐柣婊呭缁挳宕濋妸锔借拫 */
  display: flex;
  flex-direction: column;
}

/* 闂傚懏鍔樺Λ灞筋煥濮橆剙袟闁?- 闁稿繒鍘ч鎰板箥閳ь剟寮垫径瀣偦閻熸瑥鐗嗗▍?*/
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
  background: var(--color-bg-input);
  border-radius: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(95vh - 40px); /* 闁告垵绻愰獮鎾寸▔婵犱胶鐟?padding */
  display: flex;
  flex-direction: column;
  /* 缁绢収鍠曠换姘跺礃閸涱収鍟囧ù鐘查叄閵嗗﹪鏌堥妸銉х；濠殿喖顑嗗Ο澶岀矆閻氬绀夊☉鎾崇Х椤箓骞嬮鍛劷 */
  align-items: stretch;
  /* 闂傚懏鍔樺Λ灞筋煥濮橆剙袟闁?- 闁稿繒鍘ч鎰板箥閳ь剟寮垫径瀣偦閻熸瑥鐗嗗▍?*/
  scrollbar-width: none !important; /* Firefox */
  -ms-overflow-style: none !important; /* IE/Edge */
}

/* Webkit 婵炴潙绻楅～宥夊闯閵婏妇娉婇柛鏂诲妽濞碱垶姊鹃幇顖涱棏 */
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

/* 婵炴挳鏀辨慨銈咁嚕閸︻厾宕跺鑸垫尦閸庢挳寮藉畡鎵 */
.poster-popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgb(var(--color-border-rgb) / 0.08);
  flex-shrink: 0; /* 闂傚啫寮堕娑欏緞閹绢喖鍔ラ悶姘煎亜鐢洨绱?*/
}

.poster-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  min-height: 0; /* 闁稿繋娴囬?flex 閻庢稒鍔曢崢鎾舵閻樿櫕鏆紓?*/
  overflow-y: auto;
  overflow-x: hidden;
  /* 闂傚懏鍔樺Λ灞筋煥濮橆剙袟闁?*/
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
  flex-shrink: 0; /* 闂傚啫寮堕娑樏归柨瀣撻悶姘煎亜鐢洨绱?*/
  /* 缁绢収鍠曠换姘归柨瀣撻悗鐟版湰閺嗭綁寮伴崜褋浠?*/
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
  /* 缁绢収鍠曠换姘跺礃閸涱収鍟囬悗鐟版湰閺嗭綁寮伴崜褋浠涢柨娑樺缁楀鎮锝呯劵闁?*/
  box-sizing: border-box;
  min-height: fit-content;
}

.poster-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  backdrop-filter: blur(10px);
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

/* 濞存粌鐬煎ǎ顕€鎯嶆担姝屽墾缂佹劖顨婃导鍕磾?*/
:deep(.qr-popup .van-overlay),
:deep(.poster-popup .van-overlay) {
  background: rgb(var(--color-shadow-rgb) / 0.8) !important;
  backdrop-filter: blur(4px);
}

@media (max-width: 380px) {
  .hero-section {
    padding: 22px;
  }

  .hero-content {
    gap: 14px;
  }

  .coin-icon-3d {
    width: 72px;
    height: 72px;
  }

  .hero-value {
    font-size: 34px;
  }

  .dashboard-grid {
    gap: 10px;
  }

  .dashboard-card {
    padding: 15px;
  }
}
/* Targeted airy premium referral refresh */
.referral-page {
  background:
    linear-gradient(180deg, #F3F6FA 0%, #F8FAFC 46%, #F3F6FA 100%) !important;
  padding-bottom: 34px !important;
}

.background-glow {
  display: none !important;
}

.custom-nav-bar {
  --van-nav-bar-background: #FFFFFF !important;
  --van-nav-bar-title-text-color: #111827 !important;
  --van-nav-bar-icon-color: #F0B90B !important;
  --van-nav-bar-height: 56px !important;
  border-bottom: 1px solid #E6EBF2 !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  color: #111827 !important;
  font-size: 18px !important;
  font-weight: 900 !important;
}

.referral-content {
  padding: 0 18px 28px !important;
  gap: 18px !important;
  max-width: 520px !important;
  margin: 0 auto !important;
}

.announcement-marquee {
  height: 34px !important;
  margin: 0 -18px 4px !important;
  background: linear-gradient(90deg, #FFFFFF 0%, #FFF8E6 50%, #FFFFFF 100%) !important;
  border-top: 0 !important;
  border-bottom: 1px solid #F1E2B8 !important;
  box-shadow: none !important;
}

.marquee-icon {
  width: 24px !important;
  height: 24px !important;
  color: #F0B90B !important;
  background: #FFF4D6 !important;
}

.marquee-text {
  color: #111827 !important;
  font-size: 12px !important;
  font-weight: 800 !important;
}

.glass-card {
  border-radius: 16px !important;
  background: #FFFFFF !important;
  border: 1px solid #E8EEF5 !important;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06) !important;
}

.hero-section {
  margin: 0 !important;
  padding: 22px 20px 18px !important;
  border-radius: 16px !important;
  background:
    linear-gradient(135deg, #FFFFFF 0%, #FFF7DB 100%) !important;
  overflow: hidden !important;
}

.hero-orb {
  display: none !important;
}

.hero-content {
  align-items: center !important;
  gap: 18px !important;
}

.coin-icon-3d {
  width: 78px !important;
  height: 78px !important;
  border-radius: 50% !important;
  background: #FFF4D6 !important;
  box-shadow: inset 0 0 0 1px #F7D98B, 0 12px 22px rgba(240, 185, 11, 0.13) !important;
}

.hero-kicker,
.section-eyebrow {
  padding: 5px 10px !important;
  background: #FFF4D6 !important;
  color: #C88700 !important;
  letter-spacing: 0 !important;
}

.hero-label {
  margin-top: 10px !important;
  color: #64748B !important;
  font-size: 14px !important;
  font-weight: 700 !important;
}

.hero-value {
  margin-top: 6px !important;
  font-size: 40px !important;
  line-height: 1 !important;
  letter-spacing: 0 !important;
}

.hero-meta {
  margin-top: 10px !important;
  gap: 8px !important;
}

.hero-meta span {
  padding: 6px 10px !important;
  border: 0 !important;
  background: #EEF2F7 !important;
  color: #64748B !important;
}

.withdraw-btn {
  height: 50px !important;
  margin-top: 18px !important;
  border-radius: 12px !important;
  background: #FFFFFF !important;
  color: #111827 !important;
  border: 1px solid #DDE5EF !important;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.06) !important;
}

.action-section {
  margin: 0 !important;
  padding: 22px 20px !important;
  gap: 18px !important;
}

.action-header {
  align-items: flex-start !important;
}

.header-title {
  margin-top: 8px !important;
  color: #111827 !important;
  font-size: 22px !important;
  line-height: 1.2 !important;
}

.header-total {
  padding: 7px 12px !important;
  background: #FFF4D6 !important;
  color: #C88700 !important;
}

.slider-container {
  padding: 18px 18px 20px !important;
  border-radius: 16px !important;
  background: #F8FAFC !important;
  border: 1px solid #E8EEF5 !important;
}

.copy-section {
  gap: 14px !important;
}

.copy-label {
  color: #64748B !important;
  font-size: 12px !important;
  margin-bottom: 8px !important;
}

.copy-value-wrapper {
  min-height: 54px !important;
  border-radius: 14px !important;
  background: #F8FAFC !important;
  border: 1px solid #E8EEF5 !important;
  box-shadow: none !important;
}

.copy-value {
  color: #C88700 !important;
  font-weight: 900 !important;
}

.copy-value.link-value {
  color: #64748B !important;
  font-size: 12px !important;
}

.copy-pill {
  min-width: 58px !important;
  justify-content: center !important;
  background: #FFF4D6 !important;
  color: #C88700 !important;
}

.invite-btn {
  height: 54px !important;
  border-radius: 12px !important;
  background: linear-gradient(180deg, #FCD535 0%, #F0B90B 100%) !important;
  color: #111827 !important;
  border: 0 !important;
  box-shadow: 0 12px 24px rgba(240, 185, 11, 0.22) !important;
}

.dashboard-section {
  margin: 0 !important;
}

.dashboard-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 14px !important;
}

.dashboard-card {
  min-height: 132px !important;
  padding: 18px !important;
  border-radius: 16px !important;
}

.dashboard-icon {
  width: 46px !important;
  height: 46px !important;
  border-radius: 14px !important;
  background: #FFF4D6 !important;
}

.dashboard-label {
  color: #64748B !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}

.dashboard-value {
  margin-top: 8px !important;
  font-size: 27px !important;
  line-height: 1.1 !important;
}

.records-section {
  margin: 0 !important;
  padding: 10px 0 20px !important;
  border-radius: 16px !important;
  min-height: 360px !important;
}

.records-list {
  padding: 18px 20px !important;
}

.record-item {
  padding: 16px !important;
  border-radius: 16px !important;
  background: #F8FAFC !important;
  border: 1px solid #E8EEF5 !important;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.04) !important;
}

.record-avatar {
  background: #FFF4D6 !important;
  color: #C88700 !important;
}

@media (max-width: 380px) {
  .referral-content {
    padding-left: 14px !important;
    padding-right: 14px !important;
  }

  .announcement-marquee {
    margin-left: -14px !important;
    margin-right: -14px !important;
  }

  .hero-section {
    padding: 18px !important;
  }

  .coin-icon-3d {
    width: 64px !important;
    height: 64px !important;
  }

  .hero-value {
    font-size: 32px !important;
  }

  .action-section {
    padding: 20px 18px !important;
  }
}

/* Screenshot-aligned referral page */
.referral-page {
  background: #f5f7fb !important;
  color: #10182f !important;
}

.background-glow {
  display: none !important;
}

.custom-nav-bar {
  --van-nav-bar-height: 64px !important;
  --van-nav-bar-background: #ffffff !important;
  --van-nav-bar-title-text-color: #10182f !important;
  --van-nav-bar-icon-color: #10182f !important;
  border-bottom: 1px solid #dfe4ec !important;
  box-shadow: none !important;
}

:deep(.custom-nav-bar .van-nav-bar__title) {
  font-size: 21px !important;
  font-weight: 950 !important;
  letter-spacing: 0 !important;
}

:deep(.custom-nav-bar .van-icon) {
  font-size: 24px !important;
}

.referral-content {
  padding: 0 16px 26px !important;
  max-width: 520px !important;
  margin: 0 auto !important;
  gap: 16px !important;
}

.announcement-marquee {
  height: 48px !important;
  margin: 0 -16px 8px !important;
  padding: 0 16px !important;
  background: #ffffff !important;
  border-top: 0 !important;
  border-bottom: 1px solid #dfe4ec !important;
  box-shadow: none !important;
}

.marquee-wrapper {
  width: 100% !important;
  height: 48px !important;
  animation: none !important;
  transform: none !important;
  display: flex !important;
  align-items: center !important;
}

.marquee-item {
  width: 100% !important;
  flex: 1 1 auto !important;
  padding: 0 !important;
  gap: 10px !important;
}

.marquee-item:nth-child(n + 2) {
  display: none !important;
}

.marquee-icon {
  width: 24px !important;
  height: 24px !important;
  color: #10182f !important;
  background: transparent !important;
}

.marquee-text {
  color: #667085 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  white-space: nowrap !important;
}

.announcement-marquee::after {
  content: "2 分钟前  ›";
  position: absolute;
  right: 16px;
  top: 0;
  height: 48px;
  display: flex;
  align-items: center;
  padding-left: 16px;
  background: #ffffff;
  color: #667085;
  font-size: 14px;
  font-weight: 500;
}

.glass-card,
.hero-section,
.action-section,
.invite-link-card,
.records-section {
  background: #ffffff !important;
  border: 1px solid #e3e8f0 !important;
  border-radius: 18px !important;
  box-shadow: 0 14px 32px rgba(16, 24, 40, 0.06) !important;
}

.hero-section {
  position: relative !important;
  padding: 22px 20px 20px !important;
  margin: 0 !important;
  overflow: hidden !important;
  background: linear-gradient(135deg, #ffffff 0%, #ffffff 70%, #fff7e5 100%) !important;
}

.hero-orb,
.coin-icon-wrapper {
  display: none !important;
}

.hero-content {
  display: block !important;
}

.hero-stats {
  width: 100% !important;
}

.hero-kicker {
  display: inline-flex !important;
  align-items: center !important;
  min-height: 30px !important;
  padding: 0 16px !important;
  border-radius: 999px !important;
  background: #f0f2f6 !important;
  color: #10182f !important;
  font-size: 14px !important;
  font-weight: 900 !important;
}

.hero-label {
  margin-top: 30px !important;
  color: #667085 !important;
  font-size: 18px !important;
  font-weight: 800 !important;
}

.hero-value {
  margin-top: 12px !important;
  color: #10182f !important;
  font-size: clamp(44px, 11vw, 60px) !important;
  line-height: 0.95 !important;
  font-weight: 950 !important;
  letter-spacing: 0 !important;
  text-shadow: none !important;
}

.hero-value::after {
  content: " USDT";
  margin-left: 8px;
  color: #eda600;
  font-size: 18px;
  font-weight: 950;
}

.hero-meta {
  margin-top: 24px !important;
  gap: 12px !important;
  flex-wrap: wrap !important;
}

.hero-meta span {
  min-height: 42px !important;
  padding: 0 14px !important;
  border-radius: 10px !important;
  background: #f4f6f9 !important;
  color: #10182f !important;
  font-size: 15px !important;
  font-weight: 850 !important;
}

.hero-meta span:nth-child(2) {
  position: absolute;
  top: 22px;
  right: 20px;
  min-height: 34px !important;
  border-radius: 999px !important;
  background: #fff2da !important;
}

.hero-meta::after {
  content: "可提现  500 USDT";
  min-height: 42px;
  padding: 0 14px;
  border-radius: 10px;
  background: #f4f6f9;
  color: #10182f;
  display: inline-flex;
  align-items: center;
  font-size: 15px;
  font-weight: 850;
}

.rebate-action-row {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 16px;
  margin-top: 24px;
}

.hero-invite-button,
.withdraw-btn {
  width: 100% !important;
  height: 54px !important;
  margin: 0 !important;
  border-radius: 10px !important;
  font-size: 16px !important;
  font-weight: 950 !important;
}

.hero-invite-button {
  border: 0;
  color: #10182f;
  background: linear-gradient(135deg, #ffd75a 0%, #f4b719 100%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 10px 22px rgba(240, 185, 11, 0.18);
}

.withdraw-btn {
  background: #ffffff !important;
  color: #10182f !important;
  border: 1.5px solid #10182f !important;
  box-shadow: none !important;
}

.invite-link-card {
  padding: 18px 20px 14px !important;
}

.section-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #10182f;
  font-size: 17px;
  font-weight: 950;
  padding-bottom: 16px;
}

.section-title-row .van-icon {
  font-size: 22px;
}

.invite-link-row {
  min-height: 48px;
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  border-top: 1px solid #edf1f5;
  color: #344054;
  font-size: 16px;
  font-weight: 650;
}

.invite-link-row > span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.invite-link-row button {
  border: 0;
  background: transparent;
  color: #344054;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
}

.action-section {
  padding: 18px 20px 24px !important;
  margin: 0 !important;
}

.section-eyebrow,
.header-total,
.action-section .copy-section,
.action-section .invite-btn {
  display: none !important;
}

.action-header {
  margin-bottom: 20px !important;
}

.action-header::before {
  content: "";
  width: 0;
  height: 0;
}

.header-title {
  margin: 0 !important;
  color: #10182f !important;
  font-size: 18px !important;
  font-weight: 950 !important;
}

.header-title::before {
  content: "◷";
  margin-right: 12px;
  font-size: 24px;
  font-weight: 500;
  vertical-align: -2px;
}

.slider-container {
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
}

.slider-labels {
  margin-bottom: 26px !important;
}

.slider-label-left,
.slider-label-right {
  align-items: center !important;
  gap: 10px !important;
}

.label-text {
  color: #667085 !important;
  font-size: 15px !important;
  font-weight: 600 !important;
}

.label-value {
  color: #10182f !important;
  font-size: 22px !important;
  font-weight: 900 !important;
}

.dashboard-section {
  margin: 0 !important;
  overflow: hidden !important;
  border: 1px solid #e3e8f0 !important;
  border-radius: 18px !important;
  background: #ffffff !important;
  box-shadow: 0 14px 32px rgba(16, 24, 40, 0.06) !important;
}

.dashboard-grid {
  gap: 0 !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
}

.dashboard-card {
  min-height: 108px !important;
  padding: 20px 18px !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  display: grid !important;
  grid-template-columns: 54px minmax(0, 1fr) !important;
  align-items: center !important;
  gap: 14px !important;
}

.dashboard-card:nth-child(odd) {
  border-right: 1px solid #e8edf3 !important;
}

.dashboard-card:nth-child(-n + 2) {
  border-bottom: 1px solid #e8edf3 !important;
}

.dashboard-icon {
  width: 48px !important;
  height: 48px !important;
  border-radius: 50% !important;
  background: #f4f6f9 !important;
}

.dashboard-card:nth-child(3) .dashboard-icon {
  background: #e8f7ee !important;
}

.dashboard-label {
  color: #667085 !important;
  font-size: 14px !important;
  font-weight: 650 !important;
}

.dashboard-value {
  margin-top: 5px !important;
  color: #10182f !important;
  font-size: 21px !important;
  font-weight: 950 !important;
  line-height: 1.14 !important;
}

.dashboard-unit {
  font-size: 13px !important;
}

.text-green {
  color: #13964f !important;
}

.progress-bar {
  height: 4px !important;
  background: #e5e9ef !important;
}

.progress-fill {
  background: #f0b90b !important;
}

.progress-text {
  margin-top: 7px !important;
  color: #667085 !important;
  font-size: 12px !important;
}

.records-section {
  padding: 8px 14px 14px !important;
  margin: 0 !important;
  min-height: 0 !important;
}

:deep(.record-tabs .van-tabs__nav) {
  padding: 0 0 10px !important;
}

:deep(.record-tabs .van-tab) {
  font-size: 17px !important;
  font-weight: 900 !important;
}

.records-list {
  padding: 0 8px !important;
}

.records-content {
  gap: 0 !important;
}

.record-item {
  min-height: 70px !important;
  padding: 12px 0 !important;
  border: 0 !important;
  border-top: 1px solid #edf1f5 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.record-avatar {
  width: 44px !important;
  height: 44px !important;
  background: #fff4df !important;
  color: #10182f !important;
  font-weight: 900 !important;
}

.record-user {
  color: #10182f !important;
  font-size: 17px !important;
  font-weight: 950 !important;
}

.record-time,
.record-desc {
  color: #667085 !important;
  font-size: 14px !important;
}

.record-status {
  padding: 6px 12px !important;
  border-radius: 999px !important;
  font-size: 14px !important;
  font-weight: 800 !important;
}

.record-status.active {
  background: #dff7e9 !important;
  color: #13964f !important;
}

.record-status.inactive {
  background: #f2f4f7 !important;
  color: #667085 !important;
}

@media (max-width: 380px) {
  .referral-content {
    padding-left: 12px !important;
    padding-right: 12px !important;
  }

  .announcement-marquee {
    margin-left: -12px !important;
    margin-right: -12px !important;
  }

  .hero-section {
    padding: 20px 16px 18px !important;
  }

  .hero-value {
    font-size: 42px !important;
  }

  .rebate-action-row {
    gap: 10px;
  }

  .hero-invite-button,
  .withdraw-btn {
    height: 50px !important;
    font-size: 15px !important;
  }
}
</style>
