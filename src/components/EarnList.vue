<template>
  <div class="earn-list-page">
    <van-nav-bar
      v-if="!isEmbedded"
      :title="t('earn.title')"
      left-arrow
      fixed
      placeholder
      :border="false"
      @click-left="router.back()"
    />
    <Miner />
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Miner from './Miner.vue'

defineOptions({ name: 'EarnList' })

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()

const isEmbedded = computed(() => route.path === '/me' || route.query.from === 'me')

const updatePageTitle = () => {
  document.title = t('earn.title') || 'Earn'
}

watch(() => locale.value, updatePageTitle)

onMounted(updatePageTitle)
</script>

<style scoped>
.earn-list-page {
  min-height: 100vh;
  background: var(--color-surface-1);
}

:deep(.van-nav-bar) {
  --van-nav-bar-background: var(--color-surface-1);
  --van-nav-bar-title-text-color: var(--color-text-primary);
  --van-nav-bar-icon-color: #f0b90b;
}
</style>
