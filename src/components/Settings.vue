<template>
  <div class="settings-page">
    <van-nav-bar
      :title="uiText.title"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
      style="--van-nav-bar-background: #0E0E0E; --van-nav-bar-title-text-color: #FCD535; --van-nav-bar-icon-color: #FCD535;"
    />
    <div class="content-wrapper">
      <van-cell-group inset class="section-group">
        <van-cell :title="uiText.securityCenter" is-link to="/security-center" center>
          <template #icon>
            <van-icon name="shield-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
      </van-cell-group>
      <van-cell-group inset class="section-group">
        <van-cell :title="uiText.currency" is-link :value="uiText.currencyValue" center>
          <template #icon>
            <van-icon name="balance-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
        <van-cell :title="uiText.notifications" center>
          <template #icon>
            <van-icon name="bullhorn-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
          <template #right-icon>
            <van-switch v-model="pushEnabled" size="20" active-color="#FCD535" inactive-color="#333" />
          </template>
        </van-cell>
        <van-cell :title="uiText.clearCache" is-link :value="uiText.cacheSize" center @click="handleClearCache">
          <template #icon>
            <van-icon name="delete-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
        <van-cell :title="uiText.privacy" is-link center>
          <template #icon>
            <van-icon name="description" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
        <van-cell :title="uiText.about" is-link :value="uiText.version" center>
          <template #icon>
            <van-icon name="info-o" color="#FCD535" size="18" style="margin-right: 10px" />
          </template>
        </van-cell>
      </van-cell-group>
      <div class="logout-btn" @click="handleLogout">{{ uiText.logout }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast, showConfirmDialog } from 'vant';

const router = useRouter();

const uiText = {
  title: '\u901a\u7528\u8bbe\u7f6e',
  securityCenter: '\u5b89\u5168\u4e2d\u5fc3',
  currency: '\u6c47\u7387\u5355\u4f4d',
  currencyValue: 'USD',
  notifications: '\u901a\u77e5\u8bbe\u7f6e',
  clearCache: '\u6e05\u9664\u7f13\u5b58',
  cacheSize: '24.5MB',
  privacy: '\u9690\u79c1\u653f\u7b56',
  about: '\u5173\u4e8e\u6211\u4eec',
  version: 'v1.0.0',
  logout: '\u9000\u51fa\u767b\u5f55',
  cacheCleared: '\u7f13\u5b58\u5df2\u6e05\u9664',
  logoutTitle: '\u63d0\u793a',
  logoutMessage: '\u786e\u5b9a\u8981\u9000\u51fa\u767b\u5f55\u5417\uff1f',
  logoutSuccess: '\u5df2\u9000\u51fa'
};

const pushEnabled = ref(true);

const handleClearCache = () => {
  showToast({ message: uiText.cacheCleared, duration: 1500 });
};

const handleLogout = () => {
  showConfirmDialog({
    title: uiText.logoutTitle,
    message: uiText.logoutMessage,
    className: 'dark-dialog'
  })
    .then(() => {
      localStorage.clear();
      showToast({ message: uiText.logoutSuccess, duration: 1500 });
      router.push('/login');
    })
    .catch(() => {});
};
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #0E0E0E;
  padding-top: 12px;
}

.content-wrapper {
  padding: 12px 0 24px;
}

.logout-btn {
  margin: 32px 16px;
  background: #1C1C1E;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #FF4D4F;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:active {
  opacity: 0.8;
  transform: scale(0.98);
}
</style>

