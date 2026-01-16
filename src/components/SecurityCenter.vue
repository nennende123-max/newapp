<template>
  <div class="security-page">
    <van-nav-bar
      :title="$t('security.title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
      style="--van-nav-bar-background: #000000; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    <div class="content-wrapper">
      <!-- 安全分看板 -->
      <div class="security-banner">
        <div class="banner-content">
          <div class="security-level-text">{{ $t('security.security_level') }}：<span class="level-value">{{ $t('security.security_level_high') }}</span></div>
          <div class="security-tip">{{ $t('security.security_tip') }}</div>
        </div>
      </div>

      <!-- 功能列表：合并为一个卡片 -->
      <van-cell-group inset class="section-group">
        <van-cell :title="$t('security.phone_verification')" is-link center @click="handlePhoneClick">
          <template #icon>
            <van-icon name="phone-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
          <template #value>
            <span class="security-status-bound">{{ phoneStatus }}</span>
          </template>
        </van-cell>
        <van-cell :title="$t('security.google_authenticator')" is-link center @click="handleGoogleAuthClick">
          <template #icon>
            <van-icon name="shield-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
          <template #value>
            <span :class="googleAuthStatus === t('security.google_enabled') ? 'security-status-bound' : 'security-status-unbound'">
              {{ googleAuthStatus }}
            </span>
          </template>
        </van-cell>
        <van-cell :title="$t('security.fund_password_setting')" is-link center @click="handleFundPassword">
          <template #icon>
            <van-icon name="balance-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
          <template #value>
            <span class="security-status-bound">{{ fundPasswordStatus }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { t } = useI18n();

// 数据
const phoneStatus = ref('');
const googleAuthStatus = ref('');
const fundPasswordStatus = ref('');

// 加载手机验证状态
const loadPhoneStatus = () => {
  const phoneVerified = localStorage.getItem('phoneVerified');
  const phoneNumber = localStorage.getItem('phoneNumber');
  if (phoneVerified === 'true' && phoneNumber) {
    phoneStatus.value = phoneNumber;
  } else {
    phoneStatus.value = t('security.phone_unbound');
  }
};

// 加载谷歌验证状态
const loadGoogleAuthStatus = () => {
  const googleAuthEnabled = localStorage.getItem('googleAuthEnabled');
  const googleAuthStatusValue = localStorage.getItem('googleAuthStatus');
  // 兼容旧数据：检查是否存储了中文"已开启"，或新数据：googleAuthEnabled === 'true'
  if (googleAuthEnabled === 'true' || googleAuthStatusValue === '已开启') {
    googleAuthStatus.value = t('security.google_enabled');
  } else {
    googleAuthStatus.value = t('security.google_disabled');
  }
};

// 加载资金密码状态
const loadFundPasswordStatus = () => {
  const fundPasswordSet = localStorage.getItem('fundPasswordSet');
  if (fundPasswordSet === 'true') {
    fundPasswordStatus.value = t('security.fund_password_set');
  } else {
    fundPasswordStatus.value = t('security.fund_password_unset');
  }
};

// 页面加载时读取状态
onMounted(() => {
  loadPhoneStatus();
  loadGoogleAuthStatus();
  loadFundPasswordStatus();
});

// 页面激活时重新加载状态（从其他页面返回时）
onActivated(() => {
  loadPhoneStatus();
  loadGoogleAuthStatus();
  loadFundPasswordStatus();
});

// 方法
const handlePhoneClick = () => {
  router.push('/phone-verify');
};

const handleGoogleAuthClick = () => {
  // 如果已开启，显示提示
  if (googleAuthStatus.value === t('security.google_enabled')) {
    showToast({ 
      message: t('security.google_auth_status_enabled'), 
      duration: 1500,
      position: 'middle'
    });
    return;
  }
  // 如果未开启，跳转到设置页面
  router.push('/google-auth');
};

const handleFundPassword = () => {
  router.push('/fund-password');
};
</script>

<style scoped>
.security-page {
  min-height: 100vh;
  background-color: #0E0E0E;
  padding-top: 12px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.content-wrapper {
  padding: 12px 0 24px;
}

/* 安全分看板 - 优化高度和内边距 */
.security-banner {
  margin: 16px;
  padding: 28px 24px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.banner-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.security-level-text {
  font-size: 17px;
  color: #FFFFFF;
  font-weight: 500;
}

.level-value {
  color: #0ECB81;
  font-weight: 600;
}

.security-tip {
  font-size: 13px;
  color: #8E8E93;
  font-weight: 400;
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

/* 已绑定/已设置状态 - 绿色 */
.security-status-bound {
  color: #0ECB81 !important;
  font-weight: 500;
}

/* 未开启/未设置状态 - 红色并加粗 */
.security-status-unbound {
  color: #F6465D !important;
  font-weight: 600;
}

:deep(.van-cell::after) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
  left: 20px;
  right: 20px;
}

:deep(.van-cell:last-child::after) {
  display: none;
}
</style>
