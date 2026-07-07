<template>
  <div class="fund-password-page">
    <van-nav-bar
      :title="$t('security.fund_password_title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="handleBack"
      style="--van-nav-bar-background: var(--color-bg); --van-nav-bar-title-text-color: var(--color-brand-legacy); --van-nav-bar-icon-color: var(--color-brand-legacy);"
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

      <div class="password-container" @click.stop="handlePasswordContainerClick">
        <!-- 自定义密码输入框，替代 van-password-input 以解决渲染冲突 -->
        <div class="custom-password-input">
          <div 
            v-for="i in 6" 
            :key="i" 
            class="password-item"
            :class="{ 
              'is-filled': password.length >= i,
              'is-focused': showKeyboard && password.length === i - 1
            }"
          >
            <template v-if="password.length >= i">
              {{ showPassword ? password[i-1] : '●' }}
            </template>
          </div>
        </div>
        <div class="eye-toggle" @click.stop="togglePasswordVisibility">
          <van-icon :name="showPassword ? 'eye' : 'eye-o'" size="20" color="var(--color-text-secondary)" />
        </div>
      </div>

      <div class="hint-text">
        {{ currentStep === 1 ? $t('security.fund_password_hint') : $t('security.fund_password_confirm_hint') }}
      </div>

      <van-number-keyboard
        ref="keyboardRef"
        v-model="password"
        v-model:show="showKeyboard"
        :show-delete-key="true"
        theme="custom"
        extra-key=""
        :close-button-text="$t('common.complete')"
        :z-index="3000"
        class="custom-keyboard"
        @delete="onDelete"
        @blur="closeKeyboard"
        @input="onInput"
        @update:model-value="onInput"
        @close="closeKeyboard"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue';
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
const keyboardRef = ref(null);

// 切换密码显示/隐藏
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
  // watch 会自动调用 updatePasswordInputDisplay
};

// 关闭键盘
const closeKeyboard = () => {
  showKeyboard.value = false;
  if (document.activeElement) {
    document.activeElement.blur();
  }
};

// 返回处理
const handleBack = () => {
  closeKeyboard();
  router.back();
};

// 点击密码输入容器时显示键盘
const handlePasswordContainerClick = () => {
  console.log('🟡 Password container clicked, showing keyboard');
  if (document.activeElement) {
    document.activeElement.blur();
  }
  showKeyboard.value = true;
  console.log('🟡 showKeyboard set to:', showKeyboard.value);
  // 延迟检查键盘是否真的显示了，并添加点击事件监听
  setTimeout(() => {
    console.log('🟡 After 100ms, showKeyboard:', showKeyboard.value);
    const keyboardEl = document.querySelector('.van-number-keyboard');
    console.log('🟡 Keyboard element found:', !!keyboardEl);
    if (keyboardEl) {
      console.log('🟡 Keyboard element:', keyboardEl);
      console.log('🟡 Keyboard display style:', window.getComputedStyle(keyboardEl).display);
      
      // 为 PC 端添加点击事件监听
      const keys = keyboardEl.querySelectorAll('.van-key');
      console.log('🟡 Found keyboard keys:', keys.length);
      keys.forEach((key, index) => {
        // 移除之前的事件监听器（如果有）
        const newKey = key.cloneNode(true);
        key.parentNode.replaceChild(newKey, key);
        
        // 添加点击事件
        newKey.addEventListener('click', (e) => {
          e.stopPropagation();
          const keyText = newKey.textContent.trim();
          console.log('🟢 Key clicked:', keyText, 'index:', index);
          
          if (keyText === '删除' || keyText === 'Delete' || newKey.classList.contains('van-key--delete')) {
            onDelete();
          } else if (keyText === '完成' || keyText === 'Done' || newKey.classList.contains('van-key--close')) {
            closeKeyboard();
          } else if (/^\d$/.test(keyText)) {
            // 数字键
            const currentValue = password.value || '';
            if (currentValue.length < 6) {
              password.value = currentValue + keyText;
              console.log('✅ Added digit, password:', password.value);
              // watch 会自动调用 updatePasswordInputDisplay
            }
          }
        });
      });
    }
  }, 200);
};

// 统一的更新输入框显示函数
const updatePasswordInputDisplay = () => {
  // 使用自定义实现后不再需要手动操作 DOM
};

// 监听步骤变化，确保键盘显示和状态重置
watch(currentStep, async (newStep, oldStep) => {
  if (newStep === 2 && oldStep === 1) {
    // 进入第二步时，重置密码并确保键盘显示
    password.value = '';
    await nextTick();
    updatePasswordInputDisplay(); // 清空后更新显示
    // 增加小延时以保证状态同步
    setTimeout(() => {
      showKeyboard.value = true;
    }, 100);
  }
});

// 监听密码输入
watch(password, (newVal) => {
  // 更新显示
  updatePasswordInputDisplay();
  
  // 当输入满6位时，自动进入下一步
  if (newVal.length === 6 && currentStep.value === 1) {
    firstPassword.value = newVal; // 保存第一次输入的密码
    // 关闭键盘
    closeKeyboard();
    setTimeout(() => {
      currentStep.value = 2;
      password.value = ''; // 清空输入框，准备确认输入
      updatePasswordInputDisplay(); // 清空后更新显示
      // 延迟后重新打开键盘让用户输入确认密码
      setTimeout(() => {
        showKeyboard.value = true;
      }, 500);
    }, 300);
  }
  
  // 确认密码时，输入满6位后自动验证
  if (newVal.length === 6 && currentStep.value === 2) {
    // 关闭键盘
    closeKeyboard();
    setTimeout(() => {
      handleConfirm();
    }, 300);
  }
});

// 监听显示/隐藏状态变化
watch(showPassword, () => {
  updatePasswordInputDisplay();
});

// 键盘输入处理（优化后的逻辑）
const onInput = (value) => {
  console.log('🟢🟢🟢 onInput EVENT TRIGGERED! 🟢🟢🟢');
  console.log('=== onInput START ===');
  console.log('Received value:', value, 'type:', typeof value);
  
  // Vant 4 的 van-number-keyboard 通过 v-model 传递完整值字符串
  const newValue = String(value || '').replace(/\D/g, ''); // 只保留数字
  console.log('Cleaned value:', newValue);
  
  // 限制长度为6位
  if (newValue.length <= 6) {
    password.value = newValue;
    console.log('✅ Updated password to:', password.value);
    
    // watch 会自动调用 updatePasswordInputDisplay
    
    // 添加轻微的震动反馈（如果设备支持）
    if (window.navigator && window.navigator.vibrate) {
      window.navigator.vibrate(10);
    }
  } else {
    console.log('⚠️ Value too long, truncating to 6 digits');
    password.value = newValue.slice(0, 6);
    // watch 会自动调用 updatePasswordInputDisplay
  }
  
  console.log('=== onInput END ===');
};

// 删除处理
const onDelete = () => {
  console.log('🔴 Delete button clicked');
  if (password.value.length > 0) {
    password.value = password.value.slice(0, -1);
    console.log('After delete, password:', password.value);
    // watch 会自动调用 updatePasswordInputDisplay
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
      forbidClick: true,
      className: 'custom-toast'
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
  localStorage.setItem('fundPasswordSet', 'true');
  
  showToast({
    message: t('security.fund_password_success'),
    icon: 'success',
    duration: 1500,
    position: 'middle',
    forbidClick: true,
    className: 'custom-toast'
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
  background-color: var(--color-bg); /* 纯黑背景，使黄色元素更突出 */
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
  color: var(--color-text-primary);
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
  background-color: rgb(var(--color-border-rgb) / 0.2);
  transition: all 0.3s ease;
}

.dot.active {
  background-color: var(--color-brand-legacy);
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

/* 自定义密码输入框样式 */
.custom-password-input {
  display: flex;
  gap: 10px;
  justify-content: center;
  width: 100%;
}

.password-item {
  width: 48px;
  height: 48px;
  background-color: var(--color-bg-card);
  border: 1px solid rgb(var(--color-border-rgb) / 0.1);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  transition: all 0.2s ease;
}

.password-item.is-filled {
  border-color: var(--color-brand-legacy);
}

.password-item.is-focused {
  border-color: var(--color-brand-legacy);
  background-color: rgb(var(--color-brand-legacy-rgb) / 0.1);
  box-shadow: 0 0 8px rgb(var(--color-brand-legacy-rgb) / 0.3);
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

/* 提示文字 */
.hint-text {
  font-size: 13px;
  color: var(--color-text-secondary);
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
  background-color: var(--color-bg) !important;
  border-top: 1px solid rgb(var(--color-border-rgb) / 0.1) !important;
  padding-bottom: env(safe-area-inset-bottom) !important;
}

.custom-keyboard .van-key {
  background-color: var(--color-bg-card) !important;
  color: var(--color-text-primary) !important; /* 强制文字白色 */
  border-radius: 8px !important;
  margin: 0 0 6px 0 !important;
  box-shadow: 0 2px 0 rgb(var(--color-shadow-rgb) / 0.5) !important;
  font-family: 'DIN Alternate', sans-serif !important;
  font-size: 24px !important;
  height: 54px !important;
  pointer-events: auto !important;
  cursor: pointer !important;
}

.custom-keyboard .van-key:active {
  background-color: var(--color-brand-legacy) !important;
  color: var(--color-text-on-accent) !important; /* 按下变黑 */
  transform: translateY(2px);
  box-shadow: none !important;
}

.custom-keyboard .van-key--close {
  background-color: var(--color-brand-legacy) !important;
  color: var(--color-text-on-accent) !important;
  font-weight: 700 !important;
  font-size: 16px !important;
}

.custom-keyboard .van-key--delete, 
.custom-keyboard .van-key--gray {
  background-color: var(--color-surface-muted) !important;
}

.custom-keyboard .van-key--delete .van-key__icon {
  font-size: 22px !important;
  color: var(--color-text-primary) !important;
}

</style>

<style>
/* Toast 黑金风格 - 全局样式（Toast 是动态添加到 body 的） */
.custom-toast.van-toast {
  background-color: var(--color-bg-card) !important;
  border: 1px solid rgb(var(--color-brand-legacy-rgb) / 0.3) !important;
  box-shadow: 0 4px 20px rgb(var(--color-brand-legacy-rgb) / 0.2), 0 0 0 1px rgb(var(--color-brand-legacy-rgb) / 0.1) inset !important;
  border-radius: 12px !important;
  padding: 20px 24px !important;
  min-width: 200px !important;
  backdrop-filter: blur(10px) !important;
}

.custom-toast .van-toast__text {
  color: var(--color-text-primary) !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  font-family: 'DIN Alternate', 'Roboto', sans-serif !important;
  letter-spacing: 0.5px !important;
}

.custom-toast .van-toast__icon {
  color: var(--color-brand-legacy) !important;
  font-size: 48px !important;
}

.custom-toast.van-toast--success .van-toast__icon {
  color: var(--color-brand-legacy) !important;
}

.custom-toast.van-toast--fail .van-toast__icon {
  color: var(--color-loss) !important;
}
</style>