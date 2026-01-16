<template>
  <van-nav-bar
    :title="$t('support.title')"
    left-arrow
    fixed
    placeholder
    :border="false"
    @click-left="router.back()"
    style="
      background-color: #0E0E0E;
      --van-nav-bar-background: #0E0E0E;
      --van-nav-bar-title-text-color: #FCD535;
      --van-nav-bar-icon-color: #FCD535;
    "
  />

  <div class="support-page">
    <!-- 径向渐变背景 -->
    <div class="gradient-bg"></div>

    <!-- 中心引导区 -->
    <div class="center-guide">
      <div class="guide-icon">
        <van-icon name="service-o" size="64" color="#FCD535" />
      </div>
      <div class="guide-title">{{ $t('support.official_service') }}</div>
      <div class="guide-subtitle">{{ $t('support.service_subtitle') }}</div>

      <!-- 服务承诺 -->
      <div class="service-promise">
        <div class="promise-item">
          <div class="promise-icon">
            <van-icon name="shield-o" size="24" color="#FCD535" />
          </div>
          <div class="promise-label">{{ $t('support.privacy_encryption') }}</div>
        </div>
        <div class="promise-item">
          <div class="promise-icon">
            <van-icon name="clock-o" size="24" color="#FCD535" />
          </div>
          <div class="promise-label">{{ $t('support.fast_response') }}</div>
        </div>
        <div class="promise-item">
          <div class="promise-icon">
            <van-icon name="user-o" size="24" color="#FCD535" />
          </div>
          <div class="promise-label">{{ $t('support.human_service') }}</div>
        </div>
      </div>

      <!-- Telegram 社区入口 -->
      <div class="community-section">
        <van-cell
          :title="$t('support.telegram_community')"
          is-link
          @click="handleCommunityClick"
          class="telegram-cell"
        >
          <template #icon>
            <van-icon name="guide-o" size="18" color="#FCD535" style="margin-right: 10px" />
          </template>
        </van-cell>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="bottom-button-container">
      <van-button
        block
        class="contact-button"
        @click="handleContactService"
      >
        <van-icon name="service-o" size="18" style="margin-right: 8px;" />
        {{ $t('support.contact_service') }}
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast, showLoadingToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

// 联系客服
const handleContactService = () => {
  // 显示加载提示 - 纯净样式
  const toast = showLoadingToast({
    message: t('support.connecting'),
    forbidClick: true,
    loadingType: 'spinner',
    duration: 1500,
    position: 'middle'
  });

  // 1.5秒后显示结果提示
  setTimeout(() => {
    showToast({
      message: t('support.service_busy'),
      duration: 3000,
      position: 'middle'
    });
  }, 1500);
};

// Telegram 社区
const handleCommunityClick = () => {
  showToast({
    message: t('support.telegram_redirect'),
    duration: 2000,
    position: 'middle'
  });
};
</script>

<style scoped>
.support-page {
  background: #0E0E0E;
  background-image: linear-gradient(
    to bottom,
    rgba(212, 175, 55, 0.03) 0%,
    rgba(212, 175, 55, 0.01) 30%,
    transparent 50%,
    rgba(212, 175, 55, 0.01) 70%,
    rgba(212, 175, 55, 0.03) 100%
  );
  min-height: 100vh;
  padding: 16px;
  padding-bottom: 120px;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 40px;
  position: relative;
  overflow: hidden;
}

/* 径向渐变背景 */
.gradient-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at 50% 35%,
    rgba(212, 175, 55, 0.08) 0%,
    rgba(212, 175, 55, 0.03) 30%,
    transparent 60%
  );
  pointer-events: none;
  z-index: 0;
}

/* 中心引导区 */
.center-guide {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-top: calc(25vh - 80px);
  gap: 32px;
  position: relative;
  z-index: 1;
}

.guide-icon {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.guide-title {
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.guide-subtitle {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 400;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

/* 服务承诺 */
.service-promise {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  width: 100%;
  max-width: 320px;
  margin-top: 8px;
}

.promise-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.promise-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(252, 213, 53, 0.1);
  border: 1px solid rgba(252, 213, 53, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.promise-item:hover .promise-icon {
  background: rgba(252, 213, 53, 0.15);
  border-color: rgba(252, 213, 53, 0.3);
  transform: scale(1.05);
}

.promise-label {
  font-size: 12px;
  color: #8E8E93;
  font-weight: 500;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

/* Telegram 社区入口 */
.community-section {
  width: 100%;
  max-width: 600px;
  margin-top: 40px;
  position: relative;
  z-index: 1;
}

.telegram-cell {
  background: #1C1C1E;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

:deep(.telegram-cell .van-cell) {
  background: transparent !important;
  padding: 16px 20px !important;
}

:deep(.telegram-cell .van-cell__title) {
  color: #FFFFFF !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

:deep(.telegram-cell .van-cell:active) {
  background-color: rgba(255, 255, 255, 0.03) !important;
}

:deep(.telegram-cell .van-cell__right-icon) {
  color: #8E8E93 !important;
}

/* 底部按钮 */
.bottom-button-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: #0E0E0E;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
}

.contact-button {
  background: #FCD535;
  color: #0E0E0E;
  height: 56px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  box-shadow: 0 4px 15px rgba(252, 213, 53, 0.3);
}

.contact-button:active {
  opacity: 0.8;
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(252, 213, 53, 0.2);
}

/* Toast 样式优化 - 全局覆盖 */
</style>

<style>
/* 1. 核心修复：强制切除 Toast 容器底部可能溢出的系统 UI */
.van-toast--loading {
  overflow: hidden !important; /* 彻底防止内部元素溢出产生灰色背景 */
  padding-bottom: 20px !important; /* 统一内边距，确保底部与顶部对称 */
}

/* 2. 移除 Vant 默认在 Loading 模式下可能产生的伪元素进度背景 */
.van-toast--loading::before,
.van-toast--loading::after {
  display: none !important;
  content: none !important;
}

/* 3. 针对截图中的灰色条（可能是 van-toast__text 的背景或边距）：强制透明 */
.van-toast__text {
  background-color: transparent !important;
  margin-bottom: 0 !important;
}

/* 4. 保持黄色 Spinner 质感 */
.van-loading__spinner--spinner {
  color: #FCD535 !important;
}

.van-loading__spinner {
  color: #FCD535 !important;
}

/* 确保 Toast 整体样式 */
.van-toast--loading {
  background: rgba(28, 28, 30, 0.9) !important;
  backdrop-filter: blur(15px) !important;
  border-radius: 12px !important;
  padding: 20px 24px !important;
}

.van-toast--loading .van-toast__message {
  color: #FFFFFF !important;
  font-size: 14px !important;
  margin-top: 12px !important;
}

.van-toast--loading .van-loading {
  margin: 0 auto !important;
}
</style>
