<template>
  <van-nav-bar
    title="个人资料"
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

  <div class="profile-page">
    <!-- 头像容器 -->
    <div class="avatar-section">
      <div class="avatar-container" @click="handleAvatarClick">
        <div class="avatar-circle">
          <van-icon name="user-o" size="48" color="#848E9C" />
        </div>
        <div class="avatar-edit-icon">
          <van-icon name="photograph" size="16" color="#FFFFFF" />
        </div>
      </div>
    </div>

    <!-- 信息列表 -->
    <div class="info-list">
      <div class="info-item" @click="handleNicknameClick">
        <div class="info-label">昵称</div>
        <div class="info-value">
          <span>{{ nickname }}</span>
          <van-icon name="arrow" size="14" color="#848E9C" />
        </div>
      </div>

      <div class="info-item">
        <div class="info-label">UID</div>
        <div class="info-value">
          <span>{{ uid }}</span>
          <van-icon name="doc-on-doc-o" size="16" color="#FCD535" @click.stop="handleCopyUID" />
        </div>
      </div>

      <div class="info-item">
        <div class="info-label">身份认证</div>
        <div class="info-value">
          <span :class="{ 'verified': isVerified, 'unverified': !isVerified }">
            {{ isVerified ? '已认证' : '未认证' }}
          </span>
        </div>
      </div>

      <div class="info-item">
        <div class="info-label">注册时间</div>
        <div class="info-value">
          <span>{{ registerDate }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const router = useRouter();

// 数据
const nickname = ref('User_8829');
const uid = ref('8293012');
const isVerified = ref(true);
const registerDate = ref('2025-01-15');

// 方法
const handleAvatarClick = () => {
  showToast({ message: '头像上传功能开发中', duration: 2000 });
};

const handleNicknameClick = () => {
  showToast({ message: '昵称修改功能开发中', duration: 2000 });
};

const handleCopyUID = async () => {
  try {
    await navigator.clipboard.writeText(uid.value);
    showToast({ message: 'UID 已复制', icon: 'success', duration: 1500 });
  } catch (err) {
    showToast({ message: '复制失败', duration: 1500 });
  }
};
</script>

<style scoped>
.profile-page {
  background: #0E0E0E;
  min-height: 100vh;
  padding-top: 64px;
  padding-bottom: 100px;
  color: #FFFFFF;
}

/* NavBar */
.profile-nav-bar {
  background: #0E0E0E !important;
  border-bottom: none !important;
  height: 52px !important;
}

:deep(.profile-nav-bar .van-nav-bar__arrow),
:deep(.profile-nav-bar .van-icon-arrow-left) {
  color: #FCD535 !important;
  font-size: 28px !important;
  font-weight: bold !important;
}

:deep(.profile-nav-bar .van-nav-bar__title) {
  color: #FCD535 !important;
  font-weight: 700 !important;
  font-size: 18px !important;
}

:deep(.profile-nav-bar .van-nav-bar__left) {
  padding: 0 12px;
  min-width: 60px;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
  margin-bottom: 24px;
}

.avatar-container {
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.avatar-container:active {
  transform: scale(0.95);
}

.avatar-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #1C1C1E;
  border: 2px solid rgba(252, 213, 53, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s ease;
}

.avatar-container:hover .avatar-circle {
  border-color: #FCD535;
}

.avatar-edit-icon {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #FCD535;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #0E0E0E;
}

 .avatar-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #666666;
}

/* 信息列表 */
.info-list {
  margin: 16px;
  background: #1C1C1E;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  cursor: pointer;
  transition: background-color 0.2s ease;
  background: transparent;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item:active {
  background-color: rgba(255,255,255,0.05);
}

.info-label {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 500;
  font-family: sans-serif;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #FFFFFF;
  font-weight: 500;
  font-family: sans-serif;
}

.info-value .verified {
  color: #0ECB81;
  font-weight: 600;
}

.info-value .unverified {
  color: #8E8E93;
}

.info-value .van-icon {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.info-value .van-icon:active {
  opacity: 0.7;
}
</style>

