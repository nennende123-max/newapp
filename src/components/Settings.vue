<template>
  <div class="settings-page">
    <van-nav-bar
      :title="uiText.title"
      left-arrow
      fixed
      placeholder
      :border="false"
      class="page-nav-bar"
      @click-left="router.back()"
    />

    <main class="settings-content">
      <section class="settings-card single-card">
        <button class="setting-row" type="button" @click="router.push('/security-center')">
          <span class="setting-icon">
            <van-icon name="shield-o" />
          </span>
          <span class="setting-title">{{ uiText.securityCenter }}</span>
          <van-icon name="arrow" class="row-arrow" />
        </button>
      </section>

      <section class="settings-card">
        <div class="setting-row static-row">
          <span class="setting-icon">
            <van-icon name="balance-o" />
          </span>
          <span class="setting-title">{{ uiText.currency }}</span>
          <span class="setting-value">{{ uiText.currencyValue }}</span>
        </div>

        <div class="setting-row static-row">
          <span class="setting-icon">
            <van-icon name="bullhorn-o" />
          </span>
          <span class="setting-title">{{ uiText.notifications }}</span>
          <van-switch
            v-model="pushEnabled"
            size="24"
            active-color="#F0B90B"
            inactive-color="#E5EAF0"
          />
        </div>

        <button class="setting-row" type="button" @click="handleClearCache">
          <span class="setting-icon">
            <van-icon name="delete-o" />
          </span>
          <span class="setting-title">{{ uiText.clearCache }}</span>
          <span class="setting-value">{{ cacheSizeDisplay }}</span>
          <van-icon name="arrow" class="row-arrow" />
        </button>

        <button class="setting-row" type="button" @click="handlePrivacyClick">
          <span class="setting-icon">
            <van-icon name="description-o" />
          </span>
          <span class="setting-title">{{ uiText.privacy }}</span>
          <van-icon name="arrow" class="row-arrow" />
        </button>

        <button class="setting-row" type="button" @click="handleAboutClick">
          <span class="setting-icon">
            <van-icon name="info-o" />
          </span>
          <span class="setting-title">{{ uiText.about }}</span>
          <span class="setting-value">{{ uiText.version }}</span>
          <van-icon name="arrow" class="row-arrow" />
        </button>
      </section>
    </main>

    <van-dialog
      v-model:show="showPrivacyDialog"
      :title="$t('settings.privacy_policy_title')"
      class-name="settings-dialog"
      :show-cancel-button="false"
      :confirm-button-text="$t('settings.privacy_policy_confirm')"
      @confirm="showPrivacyDialog = false"
    >
      <div class="privacy-content">
        <p><strong>{{ $t('settings.privacy_section1_title') }}</strong></p>
        <p>{{ $t('settings.privacy_section1_content') }}</p>
        <p><strong>{{ $t('settings.privacy_section2_title') }}</strong></p>
        <p>{{ $t('settings.privacy_section2_content') }}</p>
        <p><strong>{{ $t('settings.privacy_section3_title') }}</strong></p>
        <p>{{ $t('settings.privacy_section3_content') }}</p>
        <p><strong>{{ $t('settings.privacy_section4_title') }}</strong></p>
        <p>{{ $t('settings.privacy_section4_content') }}</p>
        <p><strong>{{ $t('settings.privacy_section5_title') }}</strong></p>
        <p>{{ $t('settings.privacy_section5_content') }}</p>
      </div>
    </van-dialog>

    <van-dialog
      v-model:show="showAboutDialog"
      :title="$t('settings.about_us_title')"
      class-name="settings-dialog"
      :show-cancel-button="false"
      :confirm-button-text="$t('settings.about_us_confirm')"
      @confirm="showAboutDialog = false"
    >
      <div class="about-content">
        <div class="about-logo">TF</div>
        <div class="about-version">{{ $t('settings.about_us_version') }}</div>
        <p>{{ $t('settings.about_us_content') }}</p>
        <p>{{ $t('settings.about_us_content2') }}</p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

const uiText = computed(() => ({
  title: t('settings.title'),
  securityCenter: t('settings.security_center'),
  currency: t('settings.currency_unit'),
  currencyValue: t('settings.currency_unit_value'),
  notifications: t('settings.notification'),
  clearCache: t('settings.clear_cache'),
  privacy: t('settings.privacy_policy'),
  about: t('settings.about_us'),
  version: t('settings.about_us_version')
}));

const cacheSizeDisplay = ref('24.5MB');
const pushEnabled = ref(localStorage.getItem('user_push_enabled') !== 'false');
const showPrivacyDialog = ref(false);
const showAboutDialog = ref(false);

watch(pushEnabled, (newVal) => {
  localStorage.setItem('user_push_enabled', String(newVal));
  showToast({
    message: newVal ? t('settings.notification_enabled') : t('settings.notification_disabled'),
    duration: 1500,
    position: 'bottom'
  });
});

const handleClearCache = () => {
  cacheSizeDisplay.value = '0KB';
  showToast({
    message: t('settings.cache_cleared'),
    duration: 1500,
    position: 'middle'
  });
};

const handlePrivacyClick = () => {
  showPrivacyDialog.value = true;
};

const handleAboutClick = () => {
  showAboutDialog.value = true;
};
</script>

<style scoped>
.settings-page {
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

.settings-content {
  padding: 24px 18px 32px;
}

.settings-card {
  overflow: hidden;
  margin-bottom: 16px;
  background: #FFFFFF;
  border: 1px solid #EEF2F6;
  border-radius: 10px;
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
}

.single-card {
  margin-bottom: 16px;
}

.setting-row {
  width: 100%;
  min-height: 56px;
  padding: 0 18px;
  border: 0;
  border-bottom: 1px solid #F1F4F8;
  background: transparent;
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.setting-row:last-child {
  border-bottom: 0;
}

.setting-row:active {
  background: #F8FAFC;
}

.static-row:active {
  background: transparent;
}

.setting-icon {
  color: #F0B90B;
  font-size: 18px;
  display: grid;
  place-items: center;
}

.setting-title {
  min-width: 0;
  color: #111827;
  font-size: 15px;
  font-weight: 500;
}

.setting-value {
  color: #64748B;
  font-size: 14px;
  font-weight: 500;
}

.row-arrow {
  color: #94A3B8;
  font-size: 18px;
}

:deep(.van-switch__node) {
  box-shadow: 0 2px 7px rgba(15, 23, 42, 0.14);
}

.privacy-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 18px 20px;
  color: #334155;
  font-size: 14px;
  line-height: 1.6;
}

.privacy-content p,
.about-content p {
  margin: 0 0 14px;
}

.privacy-content strong {
  color: #111827;
}

.about-content {
  padding: 22px 22px 8px;
  color: #334155;
  font-size: 14px;
  line-height: 1.6;
  text-align: center;
}

.about-logo {
  width: 62px;
  height: 62px;
  margin: 0 auto 12px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
  color: #111827;
  font-size: 24px;
  font-weight: 900;
}

.about-version {
  margin-bottom: 16px;
  color: #B7791F;
  font-weight: 800;
}
</style>

<style>
.settings-page {
  background: #F5F7FA !important;
}

.settings-page .settings-content {
  box-sizing: border-box !important;
  padding: 24px 18px 32px !important;
}

.settings-page .settings-card {
  display: block !important;
  overflow: hidden !important;
  margin: 0 0 16px !important;
  background: #FFFFFF !important;
  border: 1px solid rgba(226, 232, 240, 0.9) !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06) !important;
}

.settings-page .setting-row {
  appearance: none !important;
  -webkit-appearance: none !important;
  box-sizing: border-box !important;
  width: 100% !important;
  min-height: 62px !important;
  margin: 0 !important;
  padding: 0 18px !important;
  border-top: 0 !important;
  border-right: 0 !important;
  border-left: 0 !important;
  border-bottom: 1px solid #F1F4F8 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  display: grid !important;
  grid-template-columns: 22px minmax(0, 1fr) auto auto !important;
  align-items: center !important;
  gap: 12px !important;
  text-align: left !important;
  font: inherit !important;
}

.settings-page .setting-row:last-child {
  border-bottom: 0 !important;
}

.settings-page .setting-row:active {
  background: #F8FAFC !important;
}

.settings-page .static-row:active {
  background: transparent !important;
}

.settings-page .setting-icon {
  color: #F0B90B !important;
  font-size: 18px !important;
  display: grid !important;
  place-items: center !important;
}

.settings-page .setting-title {
  min-width: 0 !important;
  color: #111827 !important;
  font-size: 15.5px !important;
  font-weight: 650 !important;
  line-height: 1.2 !important;
}

.settings-page .setting-value {
  color: #64748B !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
}

.settings-page .row-arrow {
  color: #94A3B8 !important;
  font-size: 18px !important;
}

.settings-page .van-switch {
  justify-self: end !important;
}

@media (max-width: 360px) {
  .settings-page .settings-content {
    padding-left: 14px !important;
    padding-right: 14px !important;
  }

  .settings-page .setting-row {
    min-height: 58px !important;
    padding: 0 15px !important;
    gap: 10px !important;
  }

  .settings-page .setting-title {
    font-size: 15px !important;
  }
}

.settings-dialog.van-dialog,
.settings-dialog.van-dialog .van-dialog__content {
  background: #FFFFFF !important;
  border-radius: 14px;
}

.settings-dialog .van-dialog__header {
  color: #111827 !important;
  font-weight: 800;
}

.settings-dialog .van-dialog__confirm,
.settings-dialog .van-dialog__confirm .van-button__text {
  color: #F0B90B !important;
  font-weight: 700 !important;
}
</style>
