<template>
  <!-- 遮罩层：深黑色半透明 + 高斯模糊 -->
  <Transition name="fade">
    <div 
      v-if="show" 
      class="disconnect-dialog-overlay"
      @click.self="handleCancel"
    >
      <!-- 弹窗主体：Glassmorphism 效果 -->
      <div class="disconnect-dialog-container">
        <!-- 标题区域 -->
        <div class="disconnect-dialog-header">
          <h3 class="disconnect-dialog-title">
            {{ t('auth.disconnectConfirm') }}
          </h3>
        </div>

        <!-- 内容区域 -->
        <div class="disconnect-dialog-body">
          <p class="disconnect-dialog-message">
            {{ t('auth.disconnectMessage') }}
          </p>
        </div>

        <!-- 按钮区域 -->
        <div class="disconnect-dialog-footer">
          <!-- 辅按钮 (Cancel)：纯文本样式，减少视觉噪音 -->
          <button 
            class="disconnect-dialog-btn disconnect-dialog-btn-cancel"
            @click="handleCancel"
          >
            {{ t('auth.disconnectCancelBtn') }}
          </button>

          <!-- 主按钮 (Disconnect)：红色渐变 + 发光效果 -->
          <button 
            class="disconnect-dialog-btn disconnect-dialog-btn-confirm"
            @click="handleConfirm"
          >
            {{ t('auth.disconnectConfirmBtn') }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['confirm', 'cancel']);

const handleConfirm = () => {
  emit('confirm');
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
/* 遮罩层：深黑色半透明 + 高斯模糊 */
.disconnect-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 弹窗主体：Glassmorphism 效果 */
.disconnect-dialog-container {
  width: 100%;
  max-width: 400px;
  /* 深色渐变半透明背景 */
  background: linear-gradient(to bottom, rgba(31, 31, 31, 0.9), rgba(17, 17, 17, 0.9));
  /* 强力背景模糊 */
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 16px;
  /* 精细边框，营造玻璃边缘反光感 */
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
}

/* 标题区域：p-8 内边距，不让文字贴边 */
.disconnect-dialog-header {
  padding: 32px 32px 16px 32px;
}

.disconnect-dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #FFFFFF;
  margin: 0;
  line-height: 1.5;
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
}

/* 内容区域：p-8 内边距，不让文字贴边 */
.disconnect-dialog-body {
  padding: 0 32px 32px 32px;
}

.disconnect-dialog-message {
  font-size: 15px;
  line-height: 1.7;
  color: #8E8E93;
  margin: 0;
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
}

/* 按钮区域 */
.disconnect-dialog-footer {
  display: flex;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 按钮基础样式 */
.disconnect-dialog-btn {
  flex: 1;
  height: 56px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
}

/* 辅按钮 (Cancel)：纯文本样式 */
.disconnect-dialog-btn-cancel {
  color: #8E8E93;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.disconnect-dialog-btn-cancel:hover {
  color: #FFFFFF;
  background-color: rgba(255, 255, 255, 0.05);
}

.disconnect-dialog-btn-cancel:active {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 主按钮 (Disconnect)：红色渐变 + 发光效果 */
.disconnect-dialog-btn-confirm {
  color: #FF453A;
  font-weight: 600;
  position: relative;
  background: linear-gradient(135deg, rgba(255, 69, 58, 0.15), rgba(255, 69, 58, 0.08));
}

.disconnect-dialog-btn-confirm:hover {
  color: #FFFFFF;
  background: linear-gradient(135deg, rgba(255, 69, 58, 0.25), rgba(255, 69, 58, 0.15));
  /* 轻微发光效果 */
  box-shadow: 0 0 20px rgba(255, 69, 58, 0.2), 0 0 40px rgba(255, 69, 58, 0.1);
}

.disconnect-dialog-btn-confirm:active {
  background: linear-gradient(135deg, rgba(255, 69, 58, 0.3), rgba(255, 69, 58, 0.2));
  box-shadow: 0 0 30px rgba(255, 69, 58, 0.3), 0 0 60px rgba(255, 69, 58, 0.15);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active .disconnect-dialog-container,
.fade-leave-active .disconnect-dialog-container {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.fade-enter-from .disconnect-dialog-container,
.fade-leave-to .disconnect-dialog-container {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}
</style>
