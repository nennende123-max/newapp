<template>
  <div class="google-auth-page">
    <van-nav-bar
      title="Google 验证器"
      left-arrow
      fixed
      placeholder
      :border="false"
      class="page-nav-bar"
      @click-left="handleBack"
    />

    <main class="google-auth-content">
      <section class="qr-card">
        <div class="card-heading">
          <div>
            <h2>扫描二维码</h2>
          </div>
          <button class="refresh-qr" type="button" @click="refreshQRCode">
            <van-icon name="replay" />
            <span>刷新</span>
          </button>
        </div>

        <div class="qr-frame">
          <canvas ref="qrCanvas" class="qr-canvas"></canvas>
        </div>
        <p class="qr-tip">请使用 Google Authenticator 扫描二维码</p>
      </section>

      <section class="form-card">
        <div class="field-block">
          <div class="field-header">
            <span>备用密钥</span>
            <button type="button" class="copy-btn" @click="handleCopySecretKey">
              <van-icon name="description-o" />
              <span>复制</span>
            </button>
          </div>
          <button class="secret-key-box" type="button" @click="handleCopySecretKey">
            <span>{{ formattedSecretKey }}</span>
          </button>
        </div>

        <div class="field-block">
          <div class="field-header">
            <span>验证码</span>
            <small>6 位数字</small>
          </div>
          <button class="code-input-trigger" type="button" @click.stop="handleCodeInputClick">
            <span
              v-for="i in 6"
              :key="i"
              :class="[
                'auth-code-item',
                {
                  'is-filled': verifyCode.length >= i,
                  'is-focused': showCodeKeyboard && verifyCode.length === i - 1
                }
              ]"
            >
              {{ verifyCode[i - 1] || '' }}
            </span>
          </button>
        </div>

        <div class="sync-note">
          <van-icon name="clock-o" />
          <span>验证码每 30 秒更新一次，请确保设备时间同步。</span>
        </div>
      </section>

      <van-button
        block
        class="submit-btn"
        :disabled="verifyCode.length !== 6"
        @click="handleSubmit"
      >
        启用验证
      </van-button>

      <van-number-keyboard
        v-model="verifyCode"
        v-model:show="showCodeKeyboard"
        :show-delete-key="true"
        theme="custom"
        extra-key=""
        close-button-text="完成"
        :z-index="5000"
        class="custom-keyboard"
        @delete="onCodeDelete"
        @input="onCodeInput"
        @update:model-value="onCodeInput"
        @blur="closeKeyboard"
        @close="closeKeyboard"
      />
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showSuccessToast, showToast } from 'vant';
import QRCode from 'qrcode';

const router = useRouter();

const verifyCode = ref('');
const showCodeKeyboard = ref(false);
const qrCanvas = ref(null);

const generateSecretKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let key = '';

  for (let i = 0; i < 16; i += 1) {
    key += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return key;
};

const secretKey = ref(generateSecretKey());

const formattedSecretKey = computed(() => {
  const key = secretKey.value;
  return `${key.slice(0, 4)} ${key.slice(4, 8)} ${key.slice(8, 12)} ${key.slice(12, 16)}`;
});

const generateQRCode = async () => {
  if (!qrCanvas.value) return;

  try {
    const issuer = 'TruthFi';
    const accountName = 'user@truthfi.app';
    const otpauthUrl = `otpauth://totp/${encodeURIComponent(issuer)}:${encodeURIComponent(accountName)}?secret=${secretKey.value}&issuer=${encodeURIComponent(issuer)}`;

    await QRCode.toCanvas(qrCanvas.value, otpauthUrl, {
      width: 212,
      margin: 1,
      color: {
        dark: '#111111',
        light: '#FFFFFF'
      },
      errorCorrectionLevel: 'M'
    });
  } catch (error) {
    console.error('Failed to generate QR code', error);
    showToast({
      message: '二维码生成失败，请稍后重试',
      icon: 'fail',
      duration: 2000,
      position: 'middle'
    });
  }
};

const refreshQRCode = async () => {
  secretKey.value = generateSecretKey();
  await nextTick();
  await generateQRCode();
  showSuccessToast({
    message: '二维码已刷新',
    duration: 1400,
    position: 'middle'
  });
};

const closeKeyboard = () => {
  showCodeKeyboard.value = false;
  document.activeElement?.blur?.();
};

const handleBack = () => {
  closeKeyboard();
  router.back();
};

const handleCopySecretKey = async () => {
  try {
    await navigator.clipboard.writeText(secretKey.value);
    showSuccessToast({
      message: '密钥已复制',
      duration: 1400,
      position: 'middle'
    });
  } catch (err) {
    showToast({
      message: '复制失败，请手动复制',
      duration: 1500,
      position: 'middle'
    });
  }
};

const handleCodeInputClick = () => {
  document.activeElement?.blur?.();
  showCodeKeyboard.value = true;
};

const onCodeInput = (value) => {
  verifyCode.value = String(value || '').replace(/\D/g, '').slice(0, 6);

  if (window.navigator?.vibrate) {
    window.navigator.vibrate(10);
  }
};

const onCodeDelete = () => {
  verifyCode.value = verifyCode.value.slice(0, -1);

  if (window.navigator?.vibrate) {
    window.navigator.vibrate(10);
  }
};

const handleSubmit = () => {
  if (verifyCode.value.length !== 6) {
    showToast({
      message: '请输入 6 位验证码',
      duration: 1800,
      position: 'middle'
    });
    return;
  }

  if (!/^\d{6}$/.test(verifyCode.value)) {
    showToast({
      message: '验证码格式错误',
      duration: 1800,
      position: 'middle'
    });
    return;
  }

  localStorage.setItem('googleAuthEnabled', 'true');
  localStorage.setItem('googleAuthStatus', '已开启');
  localStorage.setItem('googleAuthSecretKey', secretKey.value);

  showSuccessToast({
    message: 'Google 验证器启用成功',
    duration: 1500,
    position: 'middle',
    forbidClick: true
  });

  setTimeout(() => {
    router.push('/security-center');
  }, 1500);
};

watch(verifyCode, (value) => {
  if (value.length === 6) {
    setTimeout(closeKeyboard, 100);
  }
});

watch(secretKey, async () => {
  await nextTick();
  await generateQRCode();
});

onMounted(async () => {
  await nextTick();
  await generateQRCode();
});
</script>

<style scoped>
.google-auth-page {
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

.google-auth-content {
  min-height: calc(100dvh - var(--van-nav-bar-height));
  padding: 16px 16px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.auth-hero {
  min-height: 122px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF9E8 100%);
  border: 1px solid rgba(240, 185, 11, 0.2);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.07);
  display: grid;
  grid-template-columns: minmax(0, 1fr) 54px;
  gap: 14px;
  align-items: center;
}

.hero-kicker {
  display: block;
  margin-bottom: 6px;
  color: #B7791F;
  font-size: 12px;
  font-weight: 900;
  line-height: 1;
}

.auth-hero h1 {
  margin: 0;
  color: #111827;
  font-size: 25px;
  font-weight: 950;
  line-height: 1.15;
}

.auth-hero p {
  margin: 10px 0 0;
  color: #64748B;
  font-size: 13px;
  line-height: 1.48;
}

.hero-badge {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: #111827;
  font-size: 26px;
  background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
  box-shadow: 0 12px 24px rgba(240, 185, 11, 0.22);
}

.qr-card,
.form-card {
  border-radius: 18px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}

.qr-card {
  padding: 16px;
}

.card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.step-label {
  display: block;
  margin-bottom: 4px;
  color: #F0B90B;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
}

.card-heading h2 {
  margin: 0;
  color: #111827;
  font-size: 17px;
  font-weight: 900;
  line-height: 1.2;
}

.refresh-qr,
.copy-btn {
  appearance: none;
  -webkit-appearance: none;
  border: 0;
  background: #FFF8E1;
  color: #B7791F;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 850;
}

.refresh-qr {
  height: 30px;
  padding: 0 11px;
}

.qr-frame {
  width: 244px;
  height: 244px;
  margin: 0 auto;
  padding: 16px;
  border-radius: 16px;
  background:
    linear-gradient(#FFFFFF, #FFFFFF) padding-box,
    linear-gradient(135deg, rgba(240, 185, 11, 0.24), rgba(226, 232, 240, 0.9)) border-box;
  border: 1px solid transparent;
  display: grid;
  place-items: center;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.12);
}

.qr-canvas {
  width: 212px;
  height: 212px;
  display: block;
}

.qr-tip {
  margin: 12px 0 0;
  color: #64748B;
  font-size: 13px;
  text-align: center;
  line-height: 1.4;
}

.form-card {
  padding: 16px;
}

.field-block + .field-block {
  margin-top: 16px;
}

.field-header {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: #111827;
  font-size: 14px;
  font-weight: 900;
}

.field-header small {
  color: #94A3B8;
  font-size: 12px;
  font-weight: 700;
}

.copy-btn {
  height: 28px;
  padding: 0 10px;
}

.secret-key-box {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  min-height: 54px;
  padding: 0 14px;
  border: 0;
  border-radius: 12px;
  background: #F8FAFC;
  color: #0F172A;
  display: flex;
  align-items: center;
  box-shadow: inset 0 0 0 1px #E8EEF5;
}

.secret-key-box span {
  min-width: 0;
  overflow: hidden;
  font-size: 15px;
  font-weight: 950;
  letter-spacing: 2px;
  word-spacing: 4px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.code-input-trigger {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  border: 0;
  padding: 0;
  background: transparent;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 8px;
}

.auth-code-item {
  aspect-ratio: 1;
  border-radius: 10px;
  background: #F8FAFC;
  border: 1px solid #E5EAF0;
  color: #111827;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  display: grid;
  place-items: center;
  font-size: 20px;
  font-weight: 950;
  line-height: 1;
}

.auth-code-item.is-filled,
.auth-code-item.is-focused {
  background: #FFFFFF;
  border-color: #F0B90B;
  box-shadow: 0 0 0 3px rgba(240, 185, 11, 0.14);
}

.sync-note {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #F8FAFC;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  line-height: 1.4;
}

.sync-note .van-icon {
  color: #F0B90B;
  flex: 0 0 auto;
}

.submit-btn {
  width: 100%;
  height: 52px;
  margin-top: 2px;
  border: 0;
  border-radius: 14px;
  background: #F0B90B;
  color: #111827;
  font-size: 15px;
  font-weight: 950;
  box-shadow: 0 14px 28px rgba(240, 185, 11, 0.2);
}

.submit-btn:disabled {
  background: #E5EAF0;
  color: #94A3B8;
  opacity: 1;
  box-shadow: none;
}

@media (max-height: 760px) {
  .google-auth-content {
    gap: 10px;
    padding-top: 12px;
    padding-bottom: 16px;
  }

  .auth-hero {
    min-height: 104px;
    padding: 14px 16px;
  }

  .auth-hero h1 {
    font-size: 22px;
  }

  .auth-hero p {
    margin-top: 7px;
    font-size: 12px;
  }

  .hero-badge {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .qr-card,
  .form-card {
    padding: 13px;
  }

  .qr-frame {
    width: 214px;
    height: 214px;
    padding: 12px;
  }

  .qr-canvas {
    width: 190px;
    height: 190px;
  }

  .qr-tip {
    margin-top: 8px;
  }

  .field-block + .field-block {
    margin-top: 12px;
  }

  .sync-note {
    margin-top: 10px;
    padding: 8px 10px;
  }

  .submit-btn {
    height: 48px;
  }
}

@media (max-width: 360px) {
  .google-auth-content {
    padding-left: 14px;
    padding-right: 14px;
  }

  .auth-hero {
    grid-template-columns: minmax(0, 1fr);
  }

  .hero-badge {
    display: none;
  }

  .code-input-trigger {
    gap: 7px;
  }

  .secret-key-box span {
    font-size: 13px;
    letter-spacing: 1.5px;
  }
}

/* Airy security setup polish */
.google-auth-page {
  background:
    linear-gradient(180deg, #F3F6FA 0%, #F8FAFC 48%, #F3F6FA 100%);
}

:deep(.page-nav-bar) {
  --van-nav-bar-height: 56px;
  box-shadow: 0 1px 0 rgba(15, 23, 42, 0.03);
}

:deep(.page-nav-bar .van-nav-bar__title) {
  font-size: 18px;
  font-weight: 900;
}

.google-auth-content {
  max-width: 520px;
  margin: 0 auto;
  padding: 22px 20px 28px;
  gap: 18px;
}

.auth-hero {
  min-height: 154px;
  padding: 24px 22px;
  border-radius: 16px;
  grid-template-columns: minmax(0, 1fr) 60px;
  gap: 18px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
}

.hero-kicker {
  margin-bottom: 12px;
  font-size: 13px;
  letter-spacing: 0;
}

.auth-hero h1 {
  font-size: 30px;
  line-height: 1.12;
  letter-spacing: 0;
}

.auth-hero p {
  margin-top: 14px;
  color: #334155;
  font-size: 15px;
  line-height: 1.6;
}

.hero-badge {
  width: 60px;
  height: 60px;
  border-radius: 16px;
}

.qr-card,
.form-card {
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.055);
}

.qr-card {
  padding: 22px 20px 20px;
}

.card-heading {
  margin-bottom: 18px;
}

.step-label {
  margin-bottom: 8px;
  letter-spacing: 0;
}

.card-heading h2 {
  font-size: 22px;
  line-height: 1.2;
}

.refresh-qr {
  height: 34px;
  padding: 0 13px;
}

.qr-frame {
  width: min(272px, calc(100vw - 88px));
  height: min(272px, calc(100vw - 88px));
  padding: 18px;
  border-radius: 16px;
}

.qr-canvas {
  width: 100% !important;
  height: 100% !important;
}

.qr-tip {
  margin-top: 16px;
  font-size: 14px;
}

.form-card {
  padding: 20px;
}

.field-block + .field-block {
  margin-top: 20px;
}

.field-header {
  margin-bottom: 12px;
  font-size: 15px;
}

.secret-key-box {
  min-height: 60px;
  padding: 0 16px;
  border-radius: 14px;
}

.secret-key-box span {
  font-size: 16px;
  letter-spacing: 2.4px;
}

.code-input-trigger {
  gap: 10px;
}

.auth-code-item {
  border-radius: 12px;
  font-size: 22px;
}

.sync-note {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 13px;
}

.submit-btn {
  height: 56px;
  margin-top: 0;
  border-radius: 14px;
  font-size: 16px;
}

@media (max-height: 760px) {
  .google-auth-content {
    padding-top: 16px;
    gap: 14px;
  }

  .auth-hero {
    min-height: 126px;
    padding: 18px;
  }

  .auth-hero h1 {
    font-size: 25px;
  }

  .auth-hero p {
    margin-top: 10px;
    font-size: 13px;
  }

  .qr-card,
  .form-card {
    padding: 16px;
  }
}

@media (max-width: 380px) {
  .google-auth-content {
    padding-left: 16px;
    padding-right: 16px;
  }

  .auth-hero {
    grid-template-columns: minmax(0, 1fr) 52px;
    padding: 20px 18px;
  }

  .auth-hero h1 {
    font-size: 26px;
  }

  .auth-hero p {
    font-size: 14px;
  }

  .hero-badge {
    width: 52px;
    height: 52px;
  }

  .code-input-trigger {
    gap: 8px;
  }
}

/* Final QR-first layout refinement */
.google-auth-content {
  padding-top: 28px;
}

.qr-card {
  padding: 26px 22px 22px;
}

.card-heading {
  align-items: center;
  margin-bottom: 22px;
}

.card-heading h2 {
  font-size: 25px;
  font-weight: 950;
  line-height: 1.16;
  letter-spacing: 0;
}

.refresh-qr {
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
}

@media (max-width: 380px) {
  .google-auth-content {
    padding-top: 22px;
  }

  .qr-card {
    padding: 22px 18px 20px;
  }

  .card-heading {
    margin-bottom: 18px;
  }

  .card-heading h2 {
    font-size: 23px;
  }
}
</style>

<style>
.google-auth-page .code-input-trigger {
  display: grid !important;
  grid-template-columns: repeat(6, minmax(0, 1fr)) !important;
}

.google-auth-page .auth-code-item {
  box-sizing: border-box !important;
  width: auto !important;
  height: auto !important;
  min-width: 0 !important;
  aspect-ratio: 1 !important;
  display: grid !important;
  place-items: center !important;
}

.google-auth-page .submit-btn.van-button {
  background: #F0B90B !important;
  color: #111827 !important;
  border: 0 !important;
}

.google-auth-page .submit-btn.van-button--disabled {
  background: #E5EAF0 !important;
  color: #94A3B8 !important;
}

.custom-keyboard.van-number-keyboard {
  background: #F5F7FA !important;
  border-top: 1px solid #E5EAF0 !important;
  padding-bottom: env(safe-area-inset-bottom) !important;
}

.custom-keyboard .van-key {
  height: 52px !important;
  margin-bottom: 6px !important;
  border-radius: 8px !important;
  background: #FFFFFF !important;
  color: #111827 !important;
  box-shadow: 0 2px 0 rgba(15, 23, 42, 0.08) !important;
  font-size: 22px !important;
}

.custom-keyboard .van-key:active {
  background: #F0B90B !important;
  color: #111827 !important;
}

.custom-keyboard .van-key--close {
  background: #F0B90B !important;
  color: #111827 !important;
  font-size: 15px !important;
  font-weight: 800 !important;
}
</style>
