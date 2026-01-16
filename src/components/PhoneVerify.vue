<template>
  <div class="phone-verify-page">
    <van-nav-bar
      :title="$t('security.phone_verify_title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
      style="--van-nav-bar-background: #000000; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    
    <div class="content-wrapper">
      <div class="description-text">
        {{ $t('security.phone_verify_description') }}
      </div>

      <div class="input-section">
        <div class="input-label">
          <van-icon name="phone-o" color="#FCD535" size="18" style="margin-right: 8px" />
          {{ $t('security.phone_verify_phone_label') }}
        </div>
        <van-field
          v-model="phoneNumber"
          type="tel"
          :placeholder="$t('security.phone_verify_phone_placeholder')"
          maxlength="11"
          clearable
          autocomplete="one-time-code"
          data-lpignore="true"
          class="phone-input"
          ref="phoneInputRef"
          @focus="handlePhoneFocus"
          @clear="handlePhoneClear"
          @click-right-icon="handlePhoneClear"
        />
      </div>

      <div class="input-section">
        <div class="input-label">
          <van-icon name="shield-o" color="#FCD535" size="18" style="margin-right: 8px" />
          {{ $t('security.phone_verify_code_label') }}
        </div>
        <div class="code-input-wrapper">
          <div class="code-input-container" @click.stop="handleCodeInputClick">
            <van-password-input
              :value="verifyCode"
              :length="6"
              :mask="false"
              :gutter="10"
              :focused="showCodeKeyboard"
              class="code-password-input"
            />
          </div>
          <van-button
            :disabled="countdown > 0 || !phoneNumber || phoneNumber.length !== 11"
            class="get-code-btn"
            @click="handleGetCode"
          >
            <span class="tabular-nums">{{ countdown > 0 ? $t('security.phone_verify_countdown', { seconds: countdown }) : $t('security.phone_verify_get_code') }}</span>
          </van-button>
        </div>
      </div>

      <van-number-keyboard
        v-model:show="showCodeKeyboard"
        :show-delete-key="true"
        theme="custom"
        extra-key=""
        :close-button-text="$t('common.complete')"
        teleport="body"
        :z-index="5000"
        class="custom-keyboard"
        @input="onCodeInput"
        @delete="onCodeDelete"
        @blur="showCodeKeyboard = false"
      />

      <div class="submit-section">
        <van-button
          block
          class="submit-btn"
          :disabled="!isFormValid"
          @click="handleSubmit"
        >
          {{ $t('security.phone_verify_submit') }}
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

// 数据
const phoneNumber = ref('');
const verifyCode = ref('');
const countdown = ref(0);
// 修复：默认不显示键盘
const showCodeKeyboard = ref(false);
const phoneInputRef = ref(null);
let countdownTimer = null;

// 震动反馈辅助函数
const vibrate = (duration = 10) => {
  if (window.navigator && window.navigator.vibrate) {
    window.navigator.vibrate(duration);
  }
};

// 处理手机号清除
const handlePhoneClear = () => {
  phoneNumber.value = '';
  verifyCode.value = ''; // 确保重置时清空所有状态
  vibrate(10); // 清除时震动反馈
  // 确保输入框重新获得焦点
  nextTick(() => {
    if (phoneInputRef.value) {
      phoneInputRef.value.focus();
    }
  });
};

// 处理手机号输入框聚焦
const handlePhoneFocus = () => {
  showCodeKeyboard.value = false;
  // 确保手机号输入框获得焦点
};

// 处理验证码输入区域点击
const handleCodeInputClick = () => {
  // 确保手机号输入框失去焦点
  if (document.activeElement) {
    document.activeElement.blur();
  }
  // 显示数字键盘
  showCodeKeyboard.value = true;
};

// 验证码键盘输入处理
// 修复：直接拼接字符串，移除可能导致问题的正则校验，确保输入绝对生效
const onCodeInput = (value) => {
  if (verifyCode.value.length < 6) {
    verifyCode.value += value.toString();
    vibrate(10);
  }
};

// 验证码删除处理
const onCodeDelete = () => {
  if (verifyCode.value.length > 0) {
    verifyCode.value = verifyCode.value.slice(0, -1);
    vibrate(10);
  }
};

// 监听手机号输入，当输入满11位时自动切换键盘
watch(phoneNumber, (newVal) => {
  if (newVal.length === 11) {
    // 收起系统键盘
    if (document.activeElement) {
      document.activeElement.blur();
    }
    // 延迟弹出验证码数字键盘
    setTimeout(() => {
      showCodeKeyboard.value = true;
    }, 300);
  }
});

// 页面加载时自动聚焦手机号输入框
onMounted(async () => {
  await nextTick();
  // 延迟一下，确保页面渲染完成
  setTimeout(() => {
    if (phoneInputRef.value) {
      phoneInputRef.value.focus();
    }
  }, 300);
});

// 组件卸载时清除定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer);
  }
});

// 表单验证
const isFormValid = computed(() => {
  return phoneNumber.value.length === 11 && verifyCode.value.length === 6;
});

// 获取验证码
const handleGetCode = () => {
  // 验证手机号格式
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phoneNumber.value)) {
    showToast({
      message: t('security.phone_verify_invalid_phone'),
      duration: 2000,
      position: 'middle'
    });
    return;
  }

  // 开始倒计时
  countdown.value = 60;
  
  // 清除之前的定时器
  if (countdownTimer) {
    clearInterval(countdownTimer);
  }

  countdownTimer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(countdownTimer);
      countdownTimer = null;
    }
  }, 1000);

  // 震动反馈
  vibrate(10);

  // 模拟发送验证码
  showToast({
    message: t('security.phone_verify_code_sent'),
    duration: 1500,
    position: 'middle'
  });

  // 自动弹出验证码键盘
  setTimeout(() => {
    showCodeKeyboard.value = true;
  }, 500);
};

// 提交表单
const handleSubmit = () => {
  if (!isFormValid.value) {
    showToast({
      message: t('security.phone_verify_fill_all'),
      duration: 2000,
      position: 'middle'
    });
    return;
  }

  // 验证手机号格式
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phoneNumber.value)) {
    showToast({
      message: t('security.phone_verify_invalid_phone'),
      duration: 2000,
      position: 'middle'
    });
    return;
  }

  // 验证码格式检查
  if (verifyCode.value.length !== 6) {
    showToast({
      message: t('security.phone_verify_code_required'),
      duration: 2000,
      position: 'middle'
    });
    return;
  }

  // 保存手机号到 localStorage（掩码处理）
  const maskedPhone = phoneNumber.value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  localStorage.setItem('phoneVerified', 'true');
  localStorage.setItem('phoneNumber', maskedPhone);

  // 震动反馈
  vibrate(10);

  showToast({
    message: t('security.phone_verify_binding_success'),
    icon: 'success',
    duration: 1500,
    position: 'middle'
  });

  // 延迟跳转回安全中心
  setTimeout(() => {
    router.push('/security-center');
  }, 1500);
};
</script>

<style scoped>
.phone-verify-page {
  min-height: 100vh;
  background-color: #0E0E0E;
  padding-top: 12px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.content-wrapper {
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 说明文字 */
.description-text {
  font-size: 14px;
  color: #8E8E93;
  text-align: center;
  line-height: 1.5;
  padding: 0 20px;
  margin-bottom: 40px; /* 拉开与输入区的距离，增加页面呼吸感 */
}

/* 输入区域 */
.input-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-label {
  font-size: 15px;
  color: #FFFFFF;
  font-weight: 500;
  display: flex;
  align-items: center;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

/* 手机号输入框 */
:deep(.phone-input .van-cell) {
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0;
}

:deep(.phone-input .van-field__control) {
  background-color: transparent;
  padding: 14px 16px;
  color: #FFFFFF;
  font-size: 16px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

:deep(.phone-input .van-field__control::placeholder) {
  color: #8E8E93;
}

:deep(.phone-input .van-field__control:focus) {
  border-color: #FCD535;
}

:deep(.phone-input .van-cell:focus-within) {
  border-color: #FCD535;
  background-color: rgba(252, 213, 53, 0.05);
  box-shadow: 0 0 10px rgba(252, 213, 53, 0.15); /* 聚焦时的微弱黄色外发光效果 */
}

/* 清除图标美化 */
:deep(.phone-input .van-field__clear) {
  color: #8E8E93 !important;
  margin-right: 12px;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

:deep(.phone-input .van-field__clear:active) {
  transform: scale(0.85); /* 点击时的缩放动画 */
  opacity: 0.7;
}

/* 解决白色建议框 (CSS 注入) */
:deep(.phone-input input:-webkit-autofill),
:deep(.phone-input input:-webkit-autofill:hover),
:deep(.phone-input input:-webkit-autofill:focus) {
  -webkit-box-shadow: 0 0 0px 1000px #1C1C1E inset !important;
  -webkit-text-fill-color: #FFFFFF !important;
  transition: background-color 5000s ease-in-out 0s;
}

/* 验证码输入区域 */
.code-input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center; /* 确保验证码格子与按钮中轴线对齐 */
}

.code-input-container {
  flex: 1;
  cursor: pointer;
}

/* 验证码密码输入框样式 */
:deep(.code-password-input .van-password-input__item) {
  width: 40px;
  height: 48px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 18px;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
}

:deep(.code-password-input .van-password-input__item--focus) {
  border-color: #FCD535;
  background-color: rgba(252, 213, 53, 0.1);
}

:deep(.code-password-input .van-password-input__item--filled) {
  border-color: #FCD535;
}

/* 获取验证码按钮 */
.get-code-btn {
  background-color: #FCD535;
  color: #0E0E0E;
  border: none;
  border-radius: 8px;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  min-width: 100px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  transition: all 0.3s ease;
}

.get-code-btn:active {
  opacity: 0.8;
  transform: scale(0.98);
}

.get-code-btn:disabled {
  background-color: rgba(255, 255, 255, 0.05) !important;
  color: rgba(252, 213, 53, 0.3) !important;
  opacity: 1;
}

/* 提交按钮区域 */
.submit-section {
  margin-top: 20px;
}

.submit-btn {
  background-color: #FCD535;
  color: #0E0E0E;
  border: none;
  border-radius: 12px;
  height: 56px;
  font-size: 16px;
  font-weight: 700;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
  box-shadow: 0 4px 16px rgba(252, 213, 53, 0.2); /* 增加悬浮感 */
  transition: all 0.3s ease;
}

.submit-btn:active {
  opacity: 0.8;
  transform: scale(0.98);
}

.submit-btn:disabled {
  background-color: #333;
  color: #8E8E93;
  opacity: 0.5;
}

.tabular-nums {
  font-variant-numeric: tabular-nums;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
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
  pointer-events: auto !important; /* 强制响应点击 */
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