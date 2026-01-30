<template>
  <div class="settings-page">
    <van-nav-bar
      :title="uiText.title"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
      style="--van-nav-bar-background: #0E0E0E; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    <div class="content-wrapper">
      <van-cell-group inset class="section-group">
        <van-cell :title="uiText.securityCenter" is-link to="/security-center" center>
          <template #icon>
            <van-icon name="shield-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
      </van-cell-group>
      <van-cell-group inset class="section-group">
        <van-cell :title="uiText.currency" :value="uiText.currencyValue" center>
          <template #icon>
            <van-icon name="balance-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
        <van-cell :title="uiText.notifications" center>
          <template #icon>
            <van-icon name="bullhorn-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
          <template #right-icon>
            <van-switch v-model="pushEnabled" size="20" active-color="#FCD535" inactive-color="#333" />
          </template>
        </van-cell>
        <van-cell :title="uiText.clearCache" is-link :value="cacheSizeDisplay" center @click="handleClearCache">
          <template #icon>
            <van-icon name="delete-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
        <van-cell :title="uiText.privacy" is-link center @click="handlePrivacyClick">
          <template #icon>
            <van-icon name="description" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
        <van-cell :title="uiText.about" is-link :value="uiText.version" center @click="handleAboutClick">
          <template #icon>
            <van-icon name="info-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 隐私政策对话框 -->
    <van-dialog
      v-model:show="showPrivacyDialog"
      :title="$t('settings.privacy_policy_title')"
      class-name="dark-dialog"
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

    <!-- 关于我们对话框 -->
    <van-dialog
      v-model:show="showAboutDialog"
      :title="$t('settings.about_us_title')"
      class-name="dark-dialog"
      :show-cancel-button="false"
      :confirm-button-text="$t('settings.about_us_confirm')"
      @confirm="showAboutDialog = false"
    >
      <div class="about-content">
        <div class="about-logo">
          <div class="logo-placeholder">TF</div>
        </div>
        <div class="about-version">{{ $t('settings.about_us_version') }}</div>
        <div class="about-description">
          <p>{{ $t('settings.about_us_content') }}</p>
          <p>{{ $t('settings.about_us_content2') }}</p>
        </div>
      </div>
    </van-dialog>

  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
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

// 缓存大小显示
const cacheSizeDisplay = ref('24.5MB');

// 从 localStorage 读取推送通知状态，默认 true
const pushEnabled = ref(localStorage.getItem('user_push_enabled') !== 'false');
const showPrivacyDialog = ref(false);
const showAboutDialog = ref(false);

// 监听推送通知开关变化
watch(pushEnabled, (newVal) => {
  localStorage.setItem('user_push_enabled', newVal.toString());
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
  background-color: #0E0E0E;
  padding-top: 12px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.content-wrapper {
  padding: 12px 0 24px;
}

/* Section Group 样式 */
.section-group {
  background: #1C1C1E !important;
  border: 1px solid rgba(255, 255, 255, 0.05) !important;
  border-radius: 12px !important;
  margin-bottom: 16px;
  overflow: hidden;
}

/* Cell 样式深度覆盖 */
:deep(.van-cell) {
  background: transparent !important;
  padding: 16px 20px !important;
  align-items: center;
  transition: background-color 0.15s ease;
}

:deep(.van-cell:active) {
  background-color: rgba(255, 255, 255, 0.03) !important;
}

:deep(.van-cell__title) {
  font-size: 15px !important;
  color: #FFFFFF !important;
  font-weight: 500 !important;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

:deep(.van-cell__value) {
  font-size: 14px !important;
  color: #8E8E93 !important;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

:deep(.van-cell::after) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
  left: 20px;
  right: 20px;
}

:deep(.van-cell:last-child::after) {
  display: none;
}

/* Switch 样式 */
:deep(.van-switch) {
  background-color: #333 !important;
}

:deep(.van-switch--on) {
  background-color: #FCD535 !important;
}

:deep(.van-switch__node) {
  background-color: #FFFFFF !important;
}

/* 隐私政策内容样式 */
.privacy-content {
  padding: 20px;
  color: #FFFFFF;
  font-size: 14px;
  line-height: 1.6;
  max-height: 60vh;
  overflow-y: auto;
}

.privacy-content p {
  margin-bottom: 16px;
}

.privacy-content strong {
  color: #FCD535;
  font-weight: 600;
}

/* 关于我们内容样式 */
.about-content {
  padding: 20px;
  color: #FFFFFF;
  text-align: center;
}

.about-logo {
  margin-bottom: 16px;
}

.logo-placeholder {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background: linear-gradient(135deg, #FCD535 0%, #D4AF37 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: #0E0E0E;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.about-version {
  font-size: 16px;
  color: #FCD535;
  font-weight: 600;
  margin-bottom: 20px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.about-description {
  text-align: left;
  font-size: 14px;
  line-height: 1.6;
  color: #FFFFFF;
}

.about-description p {
  margin-bottom: 16px;
}
</style>

<!-- 全局样式：Dialog 暗黑主题 -->
<style>
.dark-dialog.van-dialog,
.dark-dialog.van-dialog .van-dialog__content {
  background-color: #1C1C1E !important;
  border-radius: 12px;
}

.dark-dialog .van-dialog__header {
  color: #FFFFFF !important;
  padding-top: 24px;
  padding-bottom: 16px;
}

.dark-dialog .van-dialog__footer {
  background-color: #1C1C1E !important;
  border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.dark-dialog .van-dialog__confirm,
.dark-dialog .van-dialog__confirm .van-button__text {
  background: transparent !important;
  border: none !important;
  color: #FCD535 !important;
  font-weight: 600 !important;
}

.dark-dialog .van-dialog__footer .van-button {
  background: transparent !important;
  border: none !important;
  height: 50px;
  font-size: 16px;
}
</style>