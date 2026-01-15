<template>
  <van-nav-bar
    title="帮助中心"
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

  <div class="support-page">
    <!-- Search -->
    <div class="search-section">
      <van-field
        v-model="searchQuery"
        :placeholder="uiText.searchPlaceholder"
        class="search-field"
        left-icon="search"
        autocomplete="off"
      />
    </div>

    <!-- Self Service -->
    <div class="self-service-section">
      <div class="section-title">{{ uiText.selfService }}</div>
      <div class="service-grid">
        <div
          v-for="service in services"
          :key="service.id"
          class="service-item"
          @click="handleServiceClick(service)"
        >
          <div class="service-icon">
            <van-icon :name="service.icon" size="24" color="#FCD535" />
          </div>
          <div class="service-label">{{ service.label }}</div>
        </div>
      </div>
    </div>

    <!-- FAQ -->
    <div class="faq-section">
      <div class="section-title">{{ uiText.faqTitle }}</div>
      <div class="faq-list">
        <div
          v-for="(faq, index) in faqs"
          :key="index"
          class="faq-item"
          :class="{ 'expanded': expandedIndex === index }"
        >
          <div class="faq-question" @click="toggleFaq(index)">
            <span>{{ faq.question }}</span>
            <van-icon
              name="arrow-down"
              size="14"
              color="#848E9C"
              :class="{ 'rotated': expandedIndex === index }"
            />
          </div>
          <div v-if="expandedIndex === index" class="faq-answer">
            {{ faq.answer }}
          </div>
        </div>
      </div>
    </div>

    <!-- Topics -->
    <div class="topics-section">
      <div class="section-title">{{ uiText.topicsTitle }}</div>
      <van-grid :column-num="3" :gutter="12" :border="false">
        <van-grid-item
          v-for="(topic, index) in helpTopics"
          :key="index"
          class="topic-item"
          @click="handleTopicClick(topic)"
        >
          <div class="topic-label">{{ topic }}</div>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- Community -->
    <div class="community-section">
      <div class="telegram-card" @click="handleCommunityClick">
        <van-icon name="guide-o" size="20" class="telegram-icon" />
        <span class="telegram-text">{{ uiText.telegramText }}</span>
        <van-icon name="arrow" size="16" color="#848E9C" />
      </div>
    </div>

    <!-- Bottom Button -->
    <div class="bottom-button-container">
      <van-button
        block
        class="contact-button"
        @click="handleContactService"
      >
        <van-icon name="service-o" size="18" style="margin-right: 8px;" />
        {{ uiText.contactService }}
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const router = useRouter();

const uiText = {
  title: '\u5e2e\u52a9\u4e2d\u5fc3',
  searchPlaceholder: '\u641c\u7d22\u60a8\u9047\u5230\u7684\u95ee\u9898...',
  selfService: '\u81ea\u52a9\u670d\u52a1',
  faqTitle: '\u5e38\u89c1\u95ee\u9898',
  topicsTitle: '\u95ee\u9898\u5206\u7c7b',
  telegramText: '\u52a0\u5165\u5b98\u65b9 Telegram \u793e\u533a',
  contactService: '\u8054\u7cfb\u5728\u7ebf\u5ba2\u670d'
};

// Data
const searchQuery = ref('');
const expandedIndex = ref(null);

const services = [
  { id: 1, icon: 'gold-coin-o', label: '\u5145\u503c' },
  { id: 2, icon: 'balance-list-o', label: '\u63d0\u73b0' },
  { id: 3, icon: 'user-o', label: '\u8d26\u53f7' },
  { id: 4, icon: 'shield-o', label: '\u5b89\u5168' }
];

const helpTopics = [
  '\u65b0\u624b\u5fc5\u8bfb',
  '\u4e70\u5e01\u6307\u5357',
  '\u5408\u7ea6\u4ea4\u6613',
  '\u8d39\u7387\u6807\u51c6',
  '\u5b89\u5168\u9a8c\u8bc1',
  'API\u63a5\u5165'
];

const faqs = [
  {
    question: '\u5145\u503c\u5df2\u786e\u8ba4\u4f46\u672a\u5230\u8d26\uff1f',
    answer: '\u8bf7\u68c0\u67e5\u533a\u5757\u786e\u8ba4\u6570\u662f\u5426\u5145\u8db3\uff0c\u6216\u8054\u7cfb\u5ba2\u670d\u5e76\u63d0\u4f9b\u4ea4\u6613 Hash \u4ee5\u4fbf\u6838\u67e5\u3002'
  },
  {
    question: '\u5982\u4f55\u8fde\u63a5/\u66f4\u6362\u94b1\u5305\uff1f',
    answer: '\u70b9\u51fb\u53f3\u4e0a\u89d2\u94b1\u5305\u6309\u94ae\u8fdb\u884c\u8fde\u63a5\uff0c\u5df2\u8fde\u63a5\u72b6\u6001\u4e0b\u53ef\u65ad\u5f00\u540e\u91cd\u65b0\u8fde\u63a5\u65b0\u7684\u94b1\u5305\u3002'
  },
  {
    question: '\u63d0\u73b0\u624b\u7eed\u8d39\uff08Gas\uff09\u8bf4\u660e',
    answer: '\u624b\u7eed\u8d39\u7531\u94fe\u4e0a Gas \u51b3\u5b9a\uff0c\u7f51\u7edc\u62e5\u5835\u65f6\u8d39\u7528\u4f1a\u4e0a\u5347\uff0c\u5efa\u8bae\u9009\u62e9\u5408\u9002\u7f51\u7edc\u3002'
  },
  {
    question: '\u5408\u7ea6\u5730\u5740\u5728\u54ea\u91cc\u67e5\u770b\uff1f',
    answer: '\u5728\u5145\u503c/\u63d0\u73b0\u9875\u9762\u6216\u8d44\u4ea7\u8be6\u60c5\u4e2d\u53ef\u67e5\u770b\u5b98\u65b9\u5408\u7ea6\u5730\u5740\uff0c\u8c28\u9632\u4eff\u5192\u3002'
  }
];

// Methods
const handleServiceClick = (service) => {
  showToast({ message: `${service.label}\u529f\u80fd\u5f00\u53d1\u4e2d`, duration: 2000 });
};

const toggleFaq = (index) => {
  if (expandedIndex.value === index) {
    expandedIndex.value = null;
  } else {
    expandedIndex.value = index;
  }
};

const handleContactService = () => {
  showToast({ message: '\u6b63\u5728\u4e3a\u60a8\u8fde\u63a5\u5ba2\u670d...', duration: 2000 });
  // Navigate to support chat if needed
};

const handleTopicClick = (topic) => {
  showToast({ message: `${topic}\u529f\u80fd\u5f00\u53d1\u4e2d`, duration: 2000 });
  // Navigate to topic details if needed
};

const handleCommunityClick = () => {
  showToast({ message: '\u6b63\u5728\u8df3\u8f6c\u5230 Telegram \u793e\u533a...', duration: 2000 });
  // Open Telegram community link
};
</script>

<style scoped>
.support-page {
  background: #0E0E0E;
  min-height: 100vh;
  padding: 16px;
  padding-bottom: 120px;
  color: #FFFFFF;
}

/* Search */
.search-section {
  margin-bottom: 24px;
}

.search-field {
  background: #1C1C1E;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
}

::deep(.search-field .van-field__control) {
  color: #FFFFFF;
  font-size: 14px;
}

::deep(.search-field .van-field__control::placeholder) {
  color: #8E8E93;
}

::deep(.search-field .van-field__left-icon) {
  color: #848E9C;
}

/* 1. 强制搜索框内部容器透明 */
:deep(.van-search__content) {
  background-color: #1C1C1E !important;
}

/* 2. 强制输入文字颜色为白色 */
:deep(.van-field__control) {
  color: #FFFFFF !important;
}

/* 3. 去除浏览器自动填充白色背景 */
:deep(input:-webkit-autofill),
:deep(input:-webkit-autofill:hover),
:deep(input:-webkit-autofill:focus),
:deep(input:-webkit-autofill:active) {
  -webkit-box-shadow: 0 0 0 1000px #1C1C1E inset !important;
  -webkit-text-fill-color: #FFFFFF !important;
  transition: background-color 5000s ease-in-out 0s;
}

/* Section Title */
.section-title {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 600;
  margin-bottom: 16px;
  font-family: sans-serif;
}

/* Self Service */
.self-service-section {
  margin-bottom: 32px;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.service-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: #1C1C1E;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.service-item:active {
  background-color: #252A32;
  transform: scale(0.95);
}

.service-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #0E0E0E;
  border: 1px solid #FCD535;
  display: flex;
  align-items: center;
  justify-content: center;
}

.service-icon .van-icon {
  color: #FCD535 !important;
}

.service-label {
  font-size: 12px;
  color: #EAECEF;
  font-weight: 500;
  font-family: sans-serif;
}

/* FAQ */
.faq-section {
  margin-bottom: 32px;
}

.faq-list {
  background: #1C1C1E;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
}

.faq-item {
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  font-size: 14px;
  color: #FFFFFF;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-family: sans-serif;
}

.faq-question:active {
  background-color: rgba(255,255,255,0.05);
}

.faq-question .van-icon {
  transition: transform 0.3s ease;
}

.faq-question .van-icon.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 20px 16px 20px;
  font-size: 13px;
  color: #FFFFFF;
  line-height: 1.6;
  font-family: sans-serif;
  animation: fadeIn 0.3s ease;
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

/* Topics */
.topics-section {
  margin-bottom: 32px;
}

/* 修复 1: 修正语法为 :deep() */
:deep(.van-grid-item__content) {
  background-color: #1C1C1E !important; /* 强制背景变黑 */
  color: #FFFFFF !important;             /* 强制文字变白 */
}

/* 修复 2: 去除默认边框 */
:deep(.van-grid-item::after) {
  border: none !important;
}

/* 修复 3: 针对 topic-item 的具体样式 */
:deep(.topic-item .van-grid-item__content) {
  background: #1C1C1E;
  border-radius: 8px;
  border: none;
  padding: 12px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #FFFFFF;
}

/* 修复 4: 点击时的反馈效果 */
:deep(.topic-item .van-grid-item__content:active) {
  background-color: #252A32;
  transform: scale(0.95);
}

.topic-label {
  font-size: 13px;
  color: #FFFFFF;
  font-weight: 500;
  text-align: center;
  font-family: sans-serif;
}

/* Community */
.community-section {
  margin-bottom: 24px;
}

.telegram-card {
  background: #1C1C1E;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.telegram-card:active {
  transform: scale(0.98);
  opacity: 0.85;
}

.telegram-icon {
  color: #2AABEE;
}

.telegram-text {
  flex: 1;
  font-size: 14px;
  color: #FFFFFF;
  font-weight: 600;
  font-family: sans-serif;
}

/* Bottom Button */
.bottom-button-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: #0E0E0E;
  border-top: 1px solid rgba(255,255,255,0.08);
  z-index: 100;
}

.contact-button {
  background: #FCD535;
  color: #0E0E0E;
  height: 56px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-family: sans-serif;
}

.contact-button:active {
  opacity: 0.8;
  transform: scale(0.98);
}
</style>

