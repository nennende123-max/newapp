<template>
  <div class="fund-password-page">
    <van-nav-bar
      :title="$t('security.fund_password_title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
      style="--van-nav-bar-background: #000000; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    
    <div class="content-wrapper" :class="{ 'keyboard-open': showKeyboard }">
      <div class="step-indicator">
        <transition name="fade" mode="out-in">
          <div class="step-text" :key="currentStep">
            {{ currentStep === 1 ? $t('security.fund_password_step1') : $t('security.fund_password_step2') }}
          </div>
        </transition>
        <div class="step-dots">
          <div class="dot" :class="{ active: currentStep === 1 }"></div>
          <div class="dot" :class="{ active: currentStep === 2 }"></div>
        </div>
      </div>

      <div class="password-container" @click.stop="showKeyboard = true">
        <van-password-input
          :value="password"
          :length="6"
          :mask="!showPassword"
          :gutter="10"
          :focused="showKeyboard"
          class="password-input"
        />
        <div class="eye-toggle" @click.stop="togglePasswordVisibility">
          <van-icon :name="showPassword ? 'eye' : 'eye-o'" size="20" color="#8E8E93" />
        </div>
      </div>

      <div class="hint-text">
        {{ currentStep === 1 ? $t('security.fund_password_hint') : $t('security.fund_password_confirm_hint') }}
      </div>

      <van-number-keyboard
        v-model:show="showKeyboard"
        :show-delete-key="true"
        theme="custom"
        extra-key=""
        :close-button-text="$t('common.complete')"
        teleport="body"
        :z-index="3000"
        class="custom-keyboard"
        @input="onInput"
        @delete="onDelete"
        @blur="showKeyboard = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

// 数据
const currentStep = ref(1); // 1: 输入密码, 2: 确认密码
const password = ref('');
const firstPassword = ref(''); // 第一次输入的密码
// 修复：默认不显示键盘
const showKeyboard = ref(false);
const showPassword = ref(false); // 控制密码显示/隐藏

// 切换密码显示/隐藏
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

// 监听步骤变化，确保键盘显示和状态重置
watch(currentStep, async (newStep, oldStep) => {
  if (newStep === 2 && oldStep === 1) {
    // 进入第二步时，重置密码并确保键盘显示
    password.value = '';
    await nextTick();
    // 增加小延时以保证状态同步
    setTimeout(() => {
      showKeyboard.value = true;
    }, 100);
  }
});

// 监听密码输入
watch(password, (newVal) => {
  // 当输入满6位时，自动进入下一步
  if (newVal.length === 6 && currentStep.value === 1) {
    firstPassword.value = newVal; // 保存第一次输入的密码
    setTimeout(() => {
      currentStep.value = 2;
      password.value = ''; // 清空输入框，准备确认输入
    }, 300);
  }
  
  // 确认密码时，输入满6位后自动验证
  if (newVal.length === 6 && currentStep.value === 2) {
    setTimeout(() => {
      handleConfirm();
    }, 300);
  }
});

// 键盘输入处理（优化后的逻辑）
const onInput = (value) => {
  // 提前拦截，防止数组溢出
  if (password.value.length >= 6) {
    return;
  }
  // 确保只接受数字
  if (!/^\d$/.test(value)) {
    return;
  }
  // 限制长度为6位
  password.value += value;
  
  // 添加轻微的震动反馈（如果设备支持）
  if (window.navigator && window.navigator.vibrate) {
    window.navigator.vibrate(10);
  }
};

// 删除处理
const onDelete = () => {
  if (password.value.length > 0) {
    password.value = password.value.slice(0, -1);
  }
};

// 确认密码
const handleConfirm = () => {
  // 验证两次输入是否一致
  if (password.value !== firstPassword.value) {
    showToast({
      message: t('security.fund_password_mismatch'),
      duration: 2000,
      position: 'middle',
      forbidClick: true
    });
    // 重置到第一步
    currentStep.value = 1;
    password.value = '';
    firstPassword.value = '';
    // 确保键盘显示，用户可以立即重新输入
    showKeyboard.value = true;
    return;
  }
  
  // 密码一致，保存到 localStorage
  localStorage.setItem('fundPassword', password.value);
  
  showToast({
    message: t('security.fund_password_success'),
    icon: 'success',
    duration: 1500,
    position: 'middle',
    forbidClick: true
  });
  
  // 延迟跳转回安全中心
  setTimeout(() => {
    router.push('/security-center');
  }, 1500);
};
</script>

<style scoped>
.fund-password-page {
  min-height: 100vh;
  background-color: #000000; /* 纯黑背景，使黄色元素更突出 */
  padding-top: 12px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.content-wrapper {
  padding: 24px 20px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  transition: padding-bottom 0.3s ease, margin-bottom 0.3s ease;
  min-height: calc(100vh - 60px);
}

.content-wrapper.keyboard-open {
  padding-bottom: 320px; /* 键盘弹出时增加底部间距 */
  margin-bottom: 0;
}

/* 步骤指示器 */
.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.step-text {
  font-size: 16px;
  color: #FFFFFF;
  font-weight: 500;
  text-align: center;
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px; /* 增加文字间距，提升高级感 */
}

/* 步骤文字淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.step-dots {
  display: flex;
  gap: 12px;
  align-items: center;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.dot.active {
  background-color: #FCD535;
  width: 24px;
  border-radius: 4px;
}

/* 密码输入容器 */
.password-container {
  width: 100%;
  max-width: 320px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  padding-right: 50px; /* 为眼睛图标留出空间 */
}

/* 眼睛图标切换按钮 */
.eye-toggle {
  position: absolute;
  right: 0;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s ease;
  z-index: 10;
}

.eye-toggle:active {
  opacity: 0.6;
  transform: scale(0.9);
}

/* 密码输入框样式覆盖 */
:deep(.password-input .van-password-input__item) {
  width: 48px;
  height: 48px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 20px;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

:deep(.password-input .van-password-input__item--focus) {
  border-color: #FCD535;
  background-color: rgba(252, 213, 53, 0.1);
  box-shadow: 0 0 8px rgba(252, 213, 53, 0.4); /* 输入框呼吸灯：黄色阴影 */
}

:deep(.password-input .van-password-input__item--filled) {
  border-color: #FCD535;
}

/* 提示文字 */
.hint-text {
  font-size: 13px;
  color: #8E8E93;
  text-align: center;
  line-height: 1.5;
  padding: 0 20px;
  transition: margin-bottom 0.3s ease;
}

.content-wrapper.keyboard-open .hint-text {
  margin-bottom: 0;
}
</style>

<style>
.custom-keyboard.van-number-keyboard {
  background-color: #0E0E0E !important;
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding-bottom: env(safe-area-inset-bottom) !important;
}

.custom-keyboard .van-key {
  background-color: #1C1C1E !important;
  color: #FFFFFF !important; /* 强制文字白色 */
  border-radius: 8px !important;
  margin: 0 0 6px 0 !important;
  box-shadow: 0 2px 0 rgba(0,0,0,0.5) !important;
  font-family: 'DIN Alternate', sans-serif !important;
  font-size: 24px !important;
  height: 54px !important;
}

.custom-keyboard .van-key:active {
  background-color: #FCD535 !important;
  color: #000000 !important; /* 按下变黑 */
  transform: translateY(2px);
  box-shadow: none !important;
}

.custom-keyboard .van-key--close {
  background-color: #FCD535 !important;
  color: #000000 !important;
  font-weight: 700 !important;
  font-size: 16px !important;
}

.custom-keyboard .van-key--delete, 
.custom-keyboard .van-key--gray {
  background-color: #2B3139 !important;
}

.custom-keyboard .van-key--delete .van-key__icon {
  font-size: 22px !important;
  color: #FFFFFF !important;
}
</style>