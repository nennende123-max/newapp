<template>
  <div class="support-shell">
    <van-nav-bar
      title="帮助与客服"
      left-arrow
      fixed
      placeholder
      :border="false"
      class="page-nav-bar"
      @click-left="router.back()"
    />

    <main class="support-page">
      <section class="support-hero" aria-label="客服中心">
        <div class="hero-copy">
          <span class="hero-kicker">TruthFi Support</span>
          <h1>我们随时为你服务</h1>
          <p>遇到充值、交易、安全问题，可优先联系在线客服</p>
        </div>
        <span class="hero-badge" aria-hidden="true">
          <van-icon name="service-o" />
        </span>
      </section>

      <section class="primary-actions" aria-label="客服入口">
        <button
          class="support-action is-primary"
          type="button"
          :disabled="communityLoading || serviceLoading"
          @click="handleContactService"
        >
          <span class="action-icon">
            <van-loading v-if="serviceLoading" size="18" color="#111827" />
            <van-icon v-else name="service-o" />
          </span>
          <span class="action-copy">
            <strong>{{ serviceLoading ? '正在分配客服...' : '联系在线客服' }}</strong>
            <small>充值、提现、交易问题优先处理</small>
          </span>
          <van-icon v-if="!serviceLoading" name="arrow" class="action-arrow" />
        </button>

        <button
          class="support-action"
          type="button"
          :disabled="communityLoading || serviceLoading"
          @click="handleCommunityClick"
        >
          <span class="action-icon">
            <van-loading v-if="communityLoading" size="18" color="#F0B90B" />
            <van-icon v-else name="guide-o" />
          </span>
          <span class="action-copy">
            <strong>{{ communityLoading ? '正在打开社区...' : '加入官方 Telegram 社区' }}</strong>
            <small>获取公告、进度同步与社区协助</small>
          </span>
          <van-icon v-if="!communityLoading" name="arrow" class="action-arrow" />
        </button>
      </section>

      <section class="promise-card" aria-label="客服服务优势">
        <div class="promise-item">
          <span class="promise-icon"><van-icon name="shield-o" /></span>
          <strong>隐私加密</strong>
          <small>会话安全保护</small>
        </div>
        <div class="promise-item">
          <span class="promise-icon"><van-icon name="clock-o" /></span>
          <strong>快速响应</strong>
          <small>优先分配线路</small>
        </div>
        <div class="promise-item">
          <span class="promise-icon"><van-icon name="user-o" /></span>
          <strong>人工服务</strong>
          <small>专员协助处理</small>
        </div>
      </section>

      <section class="faq-section" aria-label="常见问题">
        <h2>常见问题</h2>
        <div class="faq-list">
          <button
            v-for="item in faqItems"
            :key="item.title"
            class="faq-row"
            type="button"
            @click="handleFaqClick(item.title)"
          >
            <span class="faq-icon"><van-icon :name="item.icon" /></span>
            <span>{{ item.title }}</span>
            <van-icon name="arrow" class="faq-arrow" />
          </button>
        </div>
      </section>

      <section class="security-note" aria-label="安全提示">
        <van-icon name="shield-o" />
        <span>客服不会向你索要密码、验证码或私钥</span>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showSuccessToast, showToast } from 'vant';

const router = useRouter();
const communityLoading = ref(false);
const serviceLoading = ref(false);

const faqItems = [
  { title: '充值未到账', icon: 'balance-o' },
  { title: '提现处理中', icon: 'paid' },
  { title: '如何绑定 Google 验证器', icon: 'shield-o' },
  { title: '修改登录密码', icon: 'lock' },
  { title: '账户安全设置', icon: 'setting-o' }
];

const handleCommunityClick = () => {
  if (communityLoading.value || serviceLoading.value) return;

  communityLoading.value = true;
  setTimeout(() => {
    communityLoading.value = false;
    showSuccessToast({
      message: '社区入口已准备好',
      duration: 1500,
      position: 'middle'
    });
  }, 1100);
};

const handleContactService = () => {
  if (communityLoading.value || serviceLoading.value) return;

  serviceLoading.value = true;
  setTimeout(() => {
    serviceLoading.value = false;
    showToast({
      message: '客服已进入排队通道，请稍候',
      icon: 'service-o',
      duration: 1700,
      position: 'middle'
    });
  }, 1200);
};

const handleFaqClick = (title) => {
  showToast({
    message: `${title}帮助内容整理中`,
    icon: 'info-o',
    duration: 1400,
    position: 'middle'
  });
};
</script>

<style scoped>
.support-shell {
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

.support-page {
  min-height: calc(100dvh - var(--van-nav-bar-height));
  padding: 16px 16px max(22px, env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  gap: 12px;
  background:
    linear-gradient(180deg, #FFFFFF 0%, #F7F9FC 42%, #F5F7FA 100%);
}

.support-hero {
  min-height: 126px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF9E8 100%);
  border: 1px solid rgba(240, 185, 11, 0.2);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.07);
  display: grid;
  grid-template-columns: minmax(0, 1fr) 54px;
  align-items: center;
  gap: 14px;
}

.hero-copy {
  min-width: 0;
}

.hero-kicker {
  display: block;
  margin-bottom: 7px;
  color: #B7791F;
  font-size: 12px;
  font-weight: 900;
  line-height: 1;
}

.support-hero h1 {
  margin: 0;
  color: #111827;
  font-size: 21px;
  font-weight: 950;
  line-height: 1.18;
  letter-spacing: 0;
}

.support-hero p {
  margin: 9px 0 0;
  color: #64748B;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.45;
}

.hero-badge {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: #111827;
  font-size: 27px;
  background: linear-gradient(135deg, #FCD535 0%, #F0B90B 100%);
  box-shadow: 0 12px 24px rgba(240, 185, 11, 0.22);
}

.primary-actions {
  display: grid;
  gap: 10px;
}

.support-action {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  min-height: 70px;
  padding: 12px 14px;
  border: 1px solid #E8EEF5;
  border-radius: 16px;
  background: #FFFFFF;
  color: #111827;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.045);
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) 20px;
  align-items: center;
  gap: 12px;
  text-align: left;
  transition: transform 0.16s ease, opacity 0.16s ease, box-shadow 0.16s ease;
}

.support-action.is-primary {
  border-color: rgba(240, 185, 11, 0.28);
  box-shadow: 0 12px 26px rgba(15, 23, 42, 0.07);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 13px;
  display: grid;
  place-items: center;
  color: #F0B90B;
  font-size: 21px;
  background: #FFF8E1;
  border: 1px solid rgba(240, 185, 11, 0.24);
}

.is-primary .action-icon {
  color: #111827;
  background: #F0B90B;
  border-color: #F0B90B;
}

.action-copy {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.action-copy strong {
  min-width: 0;
  overflow: hidden;
  color: #111827;
  font-size: 16px;
  font-weight: 900;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-copy small {
  min-width: 0;
  overflow: hidden;
  color: #64748B;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-arrow {
  color: #94A3B8;
  font-size: 20px;
}

.support-action:disabled {
  opacity: 0.76;
}

.support-action:active {
  transform: scale(0.985);
  box-shadow: 0 7px 16px rgba(15, 23, 42, 0.06);
}

.promise-card {
  height: 104px;
  padding: 13px 10px;
  border-radius: 16px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.promise-item {
  min-width: 0;
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 5px;
  text-align: center;
}

.promise-icon {
  width: 34px;
  height: 34px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  color: #F0B90B;
  font-size: 19px;
  background: #FFF8E1;
  border: 1px solid rgba(240, 185, 11, 0.22);
}

.promise-item strong {
  color: #111827;
  font-size: 14px;
  font-weight: 850;
  line-height: 1.15;
}

.promise-item small {
  color: #64748B;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.2;
}

.faq-section {
  display: grid;
  gap: 10px;
}

.faq-section h2 {
  margin: 2px 2px 0;
  color: #111827;
  font-size: 16px;
  font-weight: 900;
  line-height: 1.2;
}

.faq-list {
  overflow: hidden;
  border-radius: 16px;
  background: #FFFFFF;
  border: 1px solid #E8EEF5;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
}

.faq-row {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  min-height: 54px;
  padding: 0 14px;
  border: 0;
  border-bottom: 1px solid #EEF2F6;
  background: #FFFFFF;
  color: #111827;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) 18px;
  align-items: center;
  gap: 10px;
  text-align: left;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.2;
}

.faq-row:last-child {
  border-bottom: 0;
}

.faq-icon {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  display: grid;
  place-items: center;
  color: #B7791F;
  font-size: 16px;
  background: #FFF8E1;
}

.faq-arrow {
  color: #94A3B8;
  font-size: 17px;
}

.faq-row:active {
  background: #F8FAFC;
}

.security-note {
  min-height: 42px;
  padding: 10px 12px;
  border-radius: 13px;
  background: #EEF2F6;
  color: #64748B;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.35;
}

.security-note .van-icon {
  color: #F0B90B;
  flex: 0 0 auto;
  font-size: 15px;
}

@media (max-height: 720px) {
  .support-page {
    padding-top: 12px;
    gap: 10px;
  }

  .support-hero {
    min-height: 116px;
    padding: 15px 16px;
  }

  .support-hero h1 {
    font-size: 20px;
  }

  .support-hero p {
    margin-top: 7px;
    font-size: 12px;
  }

  .support-action {
    min-height: 66px;
  }

  .promise-card {
    height: 96px;
    padding: 10px 8px;
  }

  .promise-icon {
    width: 31px;
    height: 31px;
    font-size: 17px;
  }

  .promise-item strong {
    font-size: 13px;
  }

  .promise-item small {
    font-size: 11px;
  }
}

@media (max-width: 360px) {
  .support-page {
    padding-left: 14px;
    padding-right: 14px;
  }

  .support-hero {
    grid-template-columns: minmax(0, 1fr) 46px;
    gap: 10px;
  }

  .hero-badge {
    width: 46px;
    height: 46px;
    border-radius: 14px;
    font-size: 23px;
  }

  .action-copy strong {
    font-size: 15px;
  }

  .action-copy small {
    font-size: 11px;
  }
}
</style>

<style>
.support-page *,
.support-page *::before,
.support-page *::after {
  box-sizing: border-box !important;
}

.support-page button {
  font-family: inherit !important;
}
</style>
