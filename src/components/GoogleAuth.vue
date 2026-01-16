<template>
  <div class="google-auth-page">
    <van-nav-bar
      :title="$t('security.google_auth_title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
      style="--van-nav-bar-background: #000000; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    
    <div class="content-wrapper">
      <div class="description-text">
        {{ $t('security.google_auth_description') }}
      </div>

      <div class="qr-container">
        <div class="qr-placeholder">
          <div class="qr-grid">
            <div class="qr-grid-row" v-for="i in 25" :key="i">
              <div class="qr-grid-cell" v-for="j in 25" :key="j" :class="{ filled: (i + j) % 3 === 0 }"></div>
            </div>
          </div>
        </div>
        <div class="qr-hint">
          <span>{{ $t('security.google_auth_qr_hint') }}</span>
          <span class="refresh-qr" @click="refreshQRCode">
            <van-icon name="replay" size="14" color="#FCD535" />
            {{ $t('security.google_auth_refresh_qr') }}
          </span>
        </div>
      </div>

      <div class="secret-key-section">
        <div class="secret-key-label">{{ $t('security.google_auth_secret_title') }}</div>
        <div class="secret-key-container">
          <div class="secret-key-value">{{ formattedSecretKey }}</div>
          <van-icon 
            name="doc-on-doc-o" 
            size="18" 
            color="#FCD535" 
            class="copy-icon"
            @click="handleCopySecretKey"
          />
        </div>
      </div>

      <div class="code-section">
        <div class="input-label">
          <van-icon name="shield-o" color="#FCD535" size="18" style="margin-right: 8px" />
          {{ $t('security.google_auth_code_placeholder') }}
        </div>
        <div class="code-input-container" ref="codeInputRef" @click.stop="handleCodeInputClick">
          <van-password-input
            :value="verifyCode"
            :length="6"
            :mask="false"
            :gutter="10"
            :focused="showCodeKeyboard"
            class="code-password-input"
          />
        </div>
      </div>

      <div class="hint-text">
        {{ $t('security.google_auth_code_hint') }}
      </div>

      <div class="submit-section">
        <van-button
          block
          class="submit-btn"
          :disabled="verifyCode.length !== 6"
          @click="handleSubmit"
        >
          {{ $t('security.google_auth_enable_btn') }}
        </van-button>
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';

const router = useRouter();
const { t } = useI18n();

// 数据
const verifyCode = ref('');
// 修复：默认不弹出键盘
const showCodeKeyboard = ref(false);
const codeInputRef = ref(null);

// 生成16位随机密钥
const generateSecretKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let key = '';
  for (let i = 0; i < 16; i++) {
    key += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return key;
};

const secretKey = ref(generateSecretKey());

// 格式化密钥显示（每4位一组，空格分隔）
const formattedSecretKey = computed(() => {
  const key = secretKey.value;
  return `${key.slice(0, 4)} ${key.slice(4, 8)} ${key.slice(8, 12)} ${key.slice(12, 16)}`;
});

// 刷新二维码
const refreshQRCode = () => {
  secretKey.value = generateSecretKey();
  showToast({
    message: t('security.google_auth_qr_refreshed'),
    duration: 1500,
    position: 'middle'
  });
};

// 复制密钥
const handleCopySecretKey = async () => {
  try {
    await navigator.clipboard.writeText(secretKey.value);
    showToast({
      message: t('security.google_auth_secret_copied'),
      icon: 'success',
      duration: 1500,
      position: 'middle'
    });
  } catch (err) {
    showToast({
      message: t('common.copy_failed'),
      duration: 1500,
      position: 'middle'
    });
  }
};

// 修复：点击输入框时，先失焦其他元素，再显示键盘
const handleCodeInputClick = () => {
  if (document.activeElement) {
    document.activeElement.blur();
  }
  showCodeKeyboard.value = true;
};

// 验证码键盘输入处理
const onCodeInput = (value) => {
  // 确保只接受数字
  if (!/^\d$/.test(value)) {
    return;
  }
  // 优化输入逻辑：确保不超过6位
  if (verifyCode.value.length < 6) {
    verifyCode.value += value;
    if (window.navigator?.vibrate) window.navigator.vibrate(10);
  }
};

// 验证码删除处理
const onCodeDelete = () => {
  if (verifyCode.value.length > 0) {
    verifyCode.value = verifyCode.value.slice(0, -1);
    if (window.navigator?.vibrate) window.navigator.vibrate(10);
  }
};

// 提交表单
const handleSubmit = () => {
  if (verifyCode.value.length !== 6) {
    showToast({
      message: t('security.google_auth_code_required'),
      duration: 2000,
      position: 'middle'
    });
    return;
  }

  // 验证码格式检查（只允许数字）
  const codeRegex = /^\d{6}$/;
  if (!codeRegex.test(verifyCode.value)) {
    showToast({
      message: t('security.google_auth_code_invalid'),
      duration: 2000,
      position: 'middle'
    });
    return;
  }

  // 保存谷歌验证状态到 localStorage
  localStorage.setItem('googleAuthEnabled', 'true');
  localStorage.setItem('googleAuthStatus', '已开启');
  localStorage.setItem('googleAuthSecretKey', secretKey.value);

  showToast({
    message: t('security.google_auth_enable_success'),
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
.google-auth-page {
  min-height: 100vh;
  background-color: #0E0E0E;
  padding-top: 12px;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.content-wrapper {
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

/* 说明文字 */
.description-text {
  font-size: 14px;
  color: #8E8E93;
  text-align: center;
  line-height: 1.5;
  padding: 0 20px;
}

/* QR 二维码容器 - 淡入动画 */
.qr-container {
  width: 100%;
  max-width: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin: 20px 0;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.qr-placeholder {
  width: 240px;
  height: 240px;
  background-color: #1C1C1E; /* 深灰卡片色，作为白色二维码的托盘 */
  border: 1px solid rgba(255, 255, 255, 0.08); /* 增加边框 */
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px; /* 增加内边距 */
}

/* 修复：白色背景，确保二维码可见 */
.qr-grid {
  display: grid;
  grid-template-columns: repeat(25, 1fr);
  grid-template-rows: repeat(25, 1fr);
  gap: 1px;
  width: 100%;
  height: 100%;
  background-color: #FFFFFF !important;
  border-radius: 8px; /* 增加圆角 */
  padding: 12px; /* 增加内边距 */
  box-sizing: border-box;
}

.qr-grid-cell {
  background-color: transparent;
  transition: background-color 0.1s;
}

/* 修复：黑色点阵 */
.qr-grid-cell.filled {
  background-color: #000000 !important;
}

.qr-hint {
  font-size: 13px;
  color: #8E8E93;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.refresh-qr {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #FCD535;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.2s ease;
}

.refresh-qr:active {
  opacity: 0.7;
}

/* 密钥绑定区 */
.secret-key-section {
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.secret-key-label {
  font-size: 15px;
  color: #FFFFFF;
  font-weight: 500;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.secret-key-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 14px 16px;
  gap: 12px;
}

.secret-key-value {
  flex: 1;
  font-size: 16px;
  color: #FFFFFF;
  font-weight: 700; /* 字体加粗 */
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  font-variant-numeric: tabular-nums;
  letter-spacing: 2px;
  word-spacing: 4px;
}

.copy-icon {
  cursor: pointer;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.copy-icon:active {
  opacity: 0.7;
  transform: scale(0.85); /* 明显的缩放反馈 */
}

/* 验证码输入区域 */
.code-section {
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-label {
  font-size: 15px;
  color: #FFFFFF;
  font-weight: 500;
  display: flex;
  align-items: center;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
}

.code-input-container {
  width: 100%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 验证码密码输入框样式 */
:deep(.code-password-input) {
  display: flex;
  justify-content: center;
  width: 100%;
}

:deep(.code-password-input .van-password-input__item) {
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

:deep(.code-password-input .van-password-input__item--focus) {
  border-color: #FCD535;
  background-color: rgba(252, 213, 53, 0.1);
}

:deep(.code-password-input .van-password-input__item--filled) {
  border-color: #FCD535;
}

/* 提示文字 */
.hint-text {
  font-size: 13px;
  color: #8E8E93;
  text-align: center;
  line-height: 1.5;
  padding: 0 20px;
}

/* 提交按钮区域 */
.submit-section {
  width: 100%;
  max-width: 320px;
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
  box-shadow: 0 4px 12px rgba(252, 213, 53, 0.2); /* 微弱的呼吸灯阴影效果 */
  transition: all 0.3s ease;
  animation: breathe 2s ease-in-out infinite, fadeInButton 0.5s ease-in; /* 添加进入页面的淡入动画 */
}

@keyframes fadeInButton {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes breathe {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(252, 213, 53, 0.2);
  }
  50% {
    box-shadow: 0 4px 16px rgba(252, 213, 53, 0.3);
  }
}

.submit-btn:active {
  opacity: 0.8;
  transform: scale(0.98);
}

.submit-btn:disabled {
  background-color: #333;
  color: #8E8E93;
  opacity: 0.5;
  animation: none; /* 禁用状态下移除呼吸灯动画 */
  box-shadow: none;
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
  color: #FFFFFF !important;
  border-radius: 8px !important;
  margin: 0 0 6px 0 !important;
  box-shadow: 0 2px 0 rgba(0,0,0,0.5) !important;
  font-family: 'DIN Alternate', sans-serif !important;
  font-size: 24px !important;
  height: 54px !important;
}

.custom-keyboard .van-key:active {
  background-color: #FCD535 !important;
  color: #000000 !important;
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