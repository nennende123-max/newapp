<template>
  <div class="security-page">
    <van-nav-bar
      :title="$t('security.title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      class="page-nav-bar"
      @click-left="router.back()"
    />

    <main class="security-content">
      <section class="security-hero">
        <span class="hero-badge">{{ $t('security.status_secure') }}</span>
        <div class="security-score-ring">
          <van-icon name="shield-o" />
        </div>
        <div class="security-copy">
          <div class="security-level-text">
            {{ $t('security.security_level') }}：<span>{{ $t('security.security_level_high') }}</span>
          </div>
          <p>{{ $t('security.security_tip') }}</p>
        </div>
      </section>

      <section class="security-list">
        <button class="security-row" type="button" @click="handleGoogleAuthClick">
          <span class="security-icon">
            <van-icon name="shield-o" />
          </span>
          <span class="security-title">{{ $t('security.google_authenticator') }}</span>
          <span :class="['status-pill', googleAuthEnabled ? 'is-enabled' : 'is-disabled']">
            {{ googleAuthStatus }}
          </span>
          <van-icon name="arrow" class="row-arrow" />
        </button>

        <button class="security-row" type="button" @click="handleFundPassword">
          <span class="security-icon">
            <van-icon name="balance-o" />
          </span>
          <span class="security-title">{{ $t('security.fund_password_setting') }}</span>
          <span :class="['status-pill', fundPasswordEnabled ? 'is-enabled' : 'is-warn']">
            {{ fundPasswordStatus }}
          </span>
          <van-icon name="arrow" class="row-arrow" />
        </button>
      </section>

      <section class="security-advice">
        <van-icon name="info-o" class="advice-icon" />
        <p>{{ $t('security.advice') }}</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onActivated, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

const googleAuthEnabled = ref(false);
const fundPasswordEnabled = ref(false);

const googleAuthStatus = computed(() => (
  googleAuthEnabled.value ? t('security.google_enabled') : t('security.google_disabled')
));

const fundPasswordStatus = computed(() => (
  fundPasswordEnabled.value ? t('security.fund_password_set') : t('security.fund_password_unset')
));

const loadSecurityStatus = () => {
  const googleAuthStatusValue = localStorage.getItem('googleAuthStatus');
  googleAuthEnabled.value = localStorage.getItem('googleAuthEnabled') === 'true'
    || googleAuthStatusValue === '已开启'
    || googleAuthStatusValue === '已启用';

  fundPasswordEnabled.value = localStorage.getItem('fundPasswordSet') === 'true'
    || Boolean(localStorage.getItem('fundPassword'));
};

onMounted(loadSecurityStatus);
onActivated(loadSecurityStatus);

const handleGoogleAuthClick = () => {
  if (googleAuthEnabled.value) {
    showToast({
      message: t('security.google_auth_status_enabled'),
      duration: 1500,
      position: 'middle'
    });
    return;
  }

  router.push('/google-auth');
};

const handleFundPassword = () => {
  router.push('/fund-password');
};
</script>

<style scoped>
/* ==== 几何 / 结构（浅深两色共用，切换主题不产生位移） ==== */
.security-page {
  min-height: 100vh;
  background: #F5F7FA;
  color: #111827;
}

:deep(.page-nav-bar) {
  --van-nav-bar-height: 56px;
  --van-nav-bar-background: #FFFFFF;
  --van-nav-bar-title-text-color: #111827;
  --van-nav-bar-icon-color: #334155;
  border-bottom: 1px solid #E8EEF5;
}

:deep(.page-nav-bar .van-nav-bar__title) {
  font-size: 18px;
  font-weight: 700;
}

.security-content {
  padding: 24px 16px 32px;
  box-sizing: border-box;
}

/* 安全等级卡片 */
.security-hero {
  position: relative;
  min-height: 116px;
  padding: 20px;
  border-radius: 18px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 16px;
}

.hero-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #16A34A;
  background: rgba(22, 163, 74, 0.10);
  border: 1px solid rgba(22, 163, 74, 0.22);
}

.security-score-ring {
  width: 64px;
  height: 64px;
  flex: 0 0 64px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 26px;
  color: #16A34A;
  background: rgba(22, 163, 74, 0.10);
  border: 1px solid rgba(22, 163, 74, 0.28);
  box-sizing: border-box;
}

.security-copy {
  min-width: 0;
}

.security-level-text {
  color: #111827;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.3;
}

.security-level-text span {
  color: #16A34A;
  font-weight: 700;
}

.security-copy p {
  margin: 8px 0 0;
  color: #64748B;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.45;
}

/* 设置项列表 */
.security-list {
  margin-top: 14px;
  overflow: hidden;
  border-radius: 18px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-sizing: border-box;
}

.security-row {
  appearance: none;
  -webkit-appearance: none;
  box-sizing: border-box;
  width: 100%;
  min-height: 88px;
  margin: 0;
  padding: 0 18px;
  border: 0;
  border-bottom: 1px solid #EEF2F7;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr) auto 18px;
  align-items: center;
  gap: 12px;
  text-align: left;
  font: inherit;
  cursor: pointer;
}

.security-row:last-child {
  border-bottom: 0;
}

.security-row:active {
  background: #F5F7FA;
}

.security-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 20px;
  color: #64748B;
  background: #F3F5F9;
  border: 1px solid #E8EEF5;
  box-sizing: border-box;
}

.security-title {
  color: #111827;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.3;
}

.status-pill {
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
  box-sizing: border-box;
}

.is-enabled {
  color: #16A34A;
  background: rgba(22, 163, 74, 0.12);
  border: 1px solid rgba(22, 163, 74, 0.20);
}

.is-disabled {
  color: #EF4444;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.20);
}

.is-warn {
  color: #B45309;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.24);
}

.row-arrow {
  color: #94A3B8;
  font-size: 18px;
}

/* 底部建议提示 */
.security-advice {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(245, 181, 27, 0.08);
  border: 1px solid rgba(245, 181, 27, 0.18);
  box-sizing: border-box;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.advice-icon {
  flex: 0 0 auto;
  margin-top: 1px;
  font-size: 16px;
  color: #B7860B;
}

.security-advice p {
  margin: 0;
  color: #64748B;
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 360px) {
  .security-content {
    padding-left: 12px;
    padding-right: 12px;
  }

  .security-level-text {
    font-size: 16px;
  }

  .security-row {
    grid-template-columns: 36px minmax(0, 1fr) auto 16px;
    gap: 10px;
    padding: 0 14px;
  }
}
</style>

<style>
/* =====================================================================
   深色主题 —— 仅覆盖颜色 / 背景 / 边框色 / 阴影，绝不改动几何，
   浅色与深色布局像素级一致（配色对齐 Binance / OKX 深色设置页）
   ===================================================================== */
html[data-theme='dark'] .security-page {
  background: #08111F !important;
  color: #F8FAFC !important;
}

html[data-theme='dark'] .security-page .page-nav-bar {
  --van-nav-bar-background: #0F1726 !important;
  --van-nav-bar-title-text-color: #F8FAFC !important;
  --van-nav-bar-icon-color: #CBD5E1 !important;
  border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

/* 安全等级卡片：略浅于页面的渐变深蓝 */
html[data-theme='dark'] .security-page .security-hero {
  background: linear-gradient(135deg, #151F31 0%, #111A2B 100%) !important;
  border-color: rgba(255, 255, 255, 0.07) !important;
}

html[data-theme='dark'] .security-page .hero-badge {
  color: #16C784 !important;
  background: rgba(22, 199, 132, 0.12) !important;
  border-color: rgba(22, 199, 132, 0.18) !important;
}

html[data-theme='dark'] .security-page .security-score-ring {
  color: #16C784 !important;
  background: rgba(22, 199, 132, 0.10) !important;
  border-color: rgba(22, 199, 132, 0.28) !important;
}

html[data-theme='dark'] .security-page .security-level-text {
  color: #F8FAFC !important;
}

html[data-theme='dark'] .security-page .security-level-text span {
  color: #16C784 !important;
}

html[data-theme='dark'] .security-page .security-copy p {
  color: #CBD5E1 !important;
}

/* 设置项列表卡片 */
html[data-theme='dark'] .security-page .security-list {
  background: #151F31 !important;
  border-color: rgba(255, 255, 255, 0.07) !important;
}

html[data-theme='dark'] .security-page .security-row {
  border-bottom-color: rgba(255, 255, 255, 0.06) !important;
}

html[data-theme='dark'] .security-page .security-row:active {
  background: rgba(255, 255, 255, 0.03) !important;
}

/* 内层图标底 */
html[data-theme='dark'] .security-page .security-icon {
  color: #CBD5E1 !important;
  background: #111A2B !important;
  border-color: rgba(255, 255, 255, 0.06) !important;
}

html[data-theme='dark'] .security-page .security-title {
  color: #F8FAFC !important;
}

html[data-theme='dark'] .security-page .row-arrow {
  color: #94A3B8 !important;
}

/* 状态胶囊：深色克制配色（不再是浅白底） */
html[data-theme='dark'] .security-page .is-enabled {
  color: #16C784 !important;
  background: rgba(22, 199, 132, 0.12) !important;
  border-color: rgba(22, 199, 132, 0.18) !important;
}

html[data-theme='dark'] .security-page .is-disabled {
  color: #F6465D !important;
  background: rgba(246, 70, 93, 0.12) !important;
  border-color: rgba(246, 70, 93, 0.18) !important;
}

html[data-theme='dark'] .security-page .is-warn {
  color: #F59E0B !important;
  background: rgba(245, 158, 11, 0.12) !important;
  border-color: rgba(245, 158, 11, 0.18) !important;
}

/* 底部建议提示 */
html[data-theme='dark'] .security-page .security-advice {
  background: rgba(245, 181, 27, 0.08) !important;
  border-color: rgba(245, 181, 27, 0.16) !important;
}

html[data-theme='dark'] .security-page .advice-icon {
  color: #F5B51B !important;
}

html[data-theme='dark'] .security-page .security-advice p {
  color: #CBD5E1 !important;
}
</style>
