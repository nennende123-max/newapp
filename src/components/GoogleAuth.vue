<template>
  <div class="google-auth-page">
    <van-nav-bar
      :title="$t('security.google_auth_title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="handleBack"
      style="--van-nav-bar-background: #000000; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    
    <div class="content-wrapper">
      <div class="description-text">
        {{ $t('security.google_auth_description') }}
      </div>

      <div class="qr-container">
        <div class="qr-placeholder">
          <canvas ref="qrCanvas" class="qr-canvas"></canvas>
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
        <div class="code-input-container" @click.stop="handleCodeInputClick">
          <!-- 自定义 6 位验证码输入框，替代 van-password-input 以解决 Vue 渲染冲突 -->
          <div class="custom-code-input">
            <div 
              v-for="i in 6" 
              :key="i" 
              class="code-item"
              :class="{ 
                'is-filled': verifyCode.length >= i,
                'is-focused': showCodeKeyboard && verifyCode.length === i - 1
              }"
            >
              {{ verifyCode[i-1] || '' }}
            </div>
          </div>
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
        ref="keyboardRef"
        v-model="verifyCode"
        v-model:show="showCodeKeyboard"
        :show-delete-key="true"
        theme="custom"
        extra-key=""
        :close-button-text="$t('common.complete')"
        :z-index="5000"
        class="custom-keyboard"
        @delete="onCodeDelete"
        @blur="closeKeyboard"
        @input="onCodeInput"
        @update:model-value="onCodeInput"
        @close="closeKeyboard"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { showToast } from 'vant';
import QRCode from 'qrcode';

const router = useRouter();
const { t } = useI18n();

// 数据
const verifyCode = ref('');
// 修复：默认不弹出键盘
const showCodeKeyboard = ref(false);
const codeInputRef = ref(null);
const qrCanvas = ref(null);
const keyboardRef = ref(null);

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

// 生成二维码
const generateQRCode = async () => {
  if (!qrCanvas.value) return;
  
  try {
    // 生成 Google Authenticator 格式的 otpauth URL
    const issuer = 'TruthFi';
    const accountName = 'user@truthfi.app';
    const otpauthUrl = `otpauth://totp/${encodeURIComponent(issuer)}:${encodeURIComponent(accountName)}?secret=${secretKey.value}&issuer=${encodeURIComponent(issuer)}`;
    
    await QRCode.toCanvas(qrCanvas.value, otpauthUrl, {
      width: 240,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      },
      errorCorrectionLevel: 'M'
    });
  } catch (error) {
    console.error('生成二维码失败:', error);
    showToast({
      message: t('security.google_auth_qr_generate_failed') || '二维码生成失败',
      icon: 'fail',
      duration: 2000
    });
  }
};

// 切换二维码
const refreshQRCode = async () => {
  secretKey.value = generateSecretKey();
  await nextTick();
  await generateQRCode();
  showToast({
    message: t('security.google_auth_qr_refreshed'),
    duration: 1500,
    position: 'middle'
  });
};

// 统一更新验证码显示函数
const updateCodeDisplay = () => {
  // 自定义实现后不再需要手动 DOM 操作，Vue 会自动处理模板中的渲染
};

// 监听键盘显示
watch(showCodeKeyboard, (show) => {
  // 不再需要手动逻辑
});

// 关闭键盘
const closeKeyboard = () => {
  showCodeKeyboard.value = false;
  if (document.activeElement) {
    document.activeElement.blur();
  }
};

// 返回处理
const handleBack = () => {
  closeKeyboard();
  router.back();
};

// 监听验证码输入
watch(verifyCode, (newVal) => {
  updateCodeDisplay();
  if (newVal.length === 6) {
    setTimeout(() => {
      closeKeyboard();
    }, 100);
  }
});

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
  console.log('🟡 Input container clicked, showing keyboard');
  if (document.activeElement) {
    document.activeElement.blur();
  }
  showCodeKeyboard.value = true;
  
  // 延迟后添加 PC 端点击支持
  setTimeout(() => {
    const keyboardEl = document.querySelector('.van-number-keyboard');
    if (keyboardEl) {
      const keys = keyboardEl.querySelectorAll('.van-key');
      keys.forEach((key) => {
        // 不要使用 replaceChild，直接添加事件监听器
        // 先移除旧的（如果存在）以防重复
        key.onclick = (e) => {
          e.stopPropagation();
          const keyText = key.textContent.trim();
          
          if (keyText === '删除' || keyText === 'Delete' || key.classList.contains('van-key--delete')) {
            onCodeDelete();
          } else if (keyText === '完成' || keyText === 'Done' || key.classList.contains('van-key--close')) {
            closeKeyboard();
          } else if (/^\d$/.test(keyText)) {
            const currentValue = verifyCode.value || '';
            if (currentValue.length < 6) {
              verifyCode.value = currentValue + keyText;
            }
          }
        };
      });
    }
  }, 300);
};

// 验证码键盘输入处理
const onCodeInput = (value) => {
  const newValue = String(value || '').replace(/\D/g, '');
  if (newValue.length <= 6) {
    verifyCode.value = newValue;
    if (window.navigator?.vibrate) {
      window.navigator.vibrate(10);
    }
  } else {
    verifyCode.value = newValue.slice(0, 6);
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

// 监听密钥变化，重新生成二维码
watch(secretKey, async () => {
  await nextTick();
  await generateQRCode();
});

// 页面加载时生成二维码
onMounted(async () => {
  await nextTick();
  await generateQRCode();
});
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
  background-color: #FFFFFF; /* 白色背景，确保二维码可见 */
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.qr-canvas {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 8px;
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

/* 自定义验证码输入框样式 */
.custom-code-input {
  display: flex;
  gap: 10px;
  justify-content: center;
  width: 100%;
}

.code-item {
  width: 48px;
  height: 48px;
  background-color: #1C1C1E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'DIN Alternate', 'Roboto', sans-serif;
  transition: all 0.2s ease;
}

.code-item.is-filled {
  border-color: #FCD535;
}

.code-item.is-focused {
  border-color: #FCD535;
  background-color: rgba(252, 213, 53, 0.1);
  box-shadow: 0 0 8px rgba(252, 213, 53, 0.3);
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
  pointer-events: auto !important;
  cursor: pointer !important;
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