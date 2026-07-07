<template>
  <van-action-sheet
    v-model:show="show"
    :actions="actions"
    :cancel-text="t('common.cancel')"
    close-on-click-action
    @select="onSelect"
  />
</template>

<script setup>
import { computed, ref, defineExpose } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, t } = useI18n()
const show = ref(false)

const actions = computed(() => [
  { name: 'English', value: 'en' },
  { name: '简体中文', value: 'zh' }
])

const onSelect = (item) => {
  locale.value = item.value
  localStorage.setItem('language', item.value)
  show.value = false
}

defineExpose({
  open: () => {
    show.value = true
  }
})
</script>
