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
          <span :class="['status-pill', fundPasswordEnabled ? 'is-enabled' : 'is-soft']">
            {{ fundPasswordStatus }}
          </span>
          <van-icon name="arrow" class="row-arrow" />
        </button>
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
.security-page {
  min-height: 100vh;
  background: #F5F7FA;
  color: #111827;
}

:deep(.page-nav-bar) {
  --van-nav-bar-background: #FFFFFF;
  --van-nav-bar-title-text-color: #111827;
  --van-nav-bar-icon-color: #F0B90B;
  border-bottom: 1px solid #E6EBF2;
}

:deep(.page-nav-bar .van-nav-bar__title) {
  font-size: 17px;
  font-weight: 800;
}

.security-content {
  padding: 30px 14px 32px;
}

.security-hero {
  min-height: 106px;
  padding: 22px 24px;
  border-radius: 16px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
  display: flex;
  align-items: center;
  gap: 16px;
}

.security-score-ring {
  width: 62px;
  height: 62px;
  flex: 0 0 62px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: #16A34A;
  font-size: 27px;
  background:
    linear-gradient(#FFFFFF, #FFFFFF) padding-box,
    conic-gradient(#16A34A 0 86%, #E5E7EB 86% 100%) border-box;
  border: 3px solid transparent;
  box-shadow: 0 10px 22px rgba(22, 163, 74, 0.12);
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
  font-weight: 900;
}

.security-copy p {
  margin: 8px 0 0;
  color: #64748B;
  font-size: 13px;
  line-height: 1.45;
}

.security-list {
  margin-top: 16px;
  overflow: hidden;
  border-radius: 16px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}

.security-row {
  width: 100%;
  min-height: 76px;
  padding: 0 18px 0 20px;
  border: 0;
  border-bottom: 1px solid #F1F4F8;
  background: transparent;
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto 18px;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.security-row:last-child {
  border-bottom: 0;
}

.security-row:active {
  background: #F8FAFC;
}

.security-icon {
  color: #F0B90B;
  font-size: 18px;
  display: grid;
  place-items: center;
}

.security-title {
  color: #111827;
  font-size: 15.5px;
  font-weight: 650;
  line-height: 1.35;
}

.status-pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
  white-space: nowrap;
}

.is-enabled,
.is-soft {
  color: #059669;
  background: #EAFBF2;
  border: 1px solid #BEEBD0;
}

.is-disabled {
  color: #EF4444;
  background: #FFF0F0;
  border: 1px solid #FFD1D1;
}

.row-arrow {
  color: #94A3B8;
  font-size: 18px;
}

@media (max-width: 360px) {
  .security-content {
    padding-left: 12px;
    padding-right: 12px;
  }

  .security-hero {
    padding: 18px;
  }

  .security-level-text {
    font-size: 16px;
  }

  .security-row {
    grid-template-columns: 20px minmax(0, 1fr) auto 16px;
    gap: 10px;
    padding: 0 14px;
  }
}
</style>

<style>
.security-page {
  background: #F5F7FA !important;
}

.security-page .security-content {
  box-sizing: border-box !important;
}

.security-page .security-hero,
.security-page .security-list {
  box-sizing: border-box !important;
  display: flex !important;
}

.security-page .security-list {
  display: block !important;
}

.security-page .security-row {
  appearance: none !important;
  -webkit-appearance: none !important;
  box-sizing: border-box !important;
  width: 100% !important;
  min-height: 76px !important;
  margin: 0 !important;
  padding: 0 18px 0 20px !important;
  border-top: 0 !important;
  border-right: 0 !important;
  border-left: 0 !important;
  border-bottom: 1px solid #F1F4F8 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  display: grid !important;
  grid-template-columns: 22px minmax(0, 1fr) auto 18px !important;
  align-items: center !important;
  gap: 12px !important;
  text-align: left !important;
  font: inherit !important;
}

.security-page .security-row:last-child {
  border-bottom: 0 !important;
}

.security-page .security-row:active {
  background: #F8FAFC !important;
}

.security-page .security-title,
.security-page .status-pill {
  line-height: 1.2 !important;
}
</style>
