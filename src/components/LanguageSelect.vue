<template>
    <van-action-sheet
      v-model:show="show"
      :actions="actions"
      cancel-text="Cancel"
      close-on-click-action
      @select="onSelect"
    />
  </template>
  
  <script setup>
    import { ref, defineExpose } from 'vue';
    import { useI18n } from 'vue-i18n'; // 👈 检查有没有这一行
    
    const { locale } = useI18n(); // 👈 检查有没有这一行
    const show = ref(false);
    
    const actions = [
      { name: 'English', value: 'en' },
      { name: '简体中文', value: 'zh' }
    ];
    
    const onSelect = (item) => {
      // 核心逻辑：这里会让整个 App 的语言发生翻转
      locale.value = item.value;
      // 保存语言设置到 localStorage，确保刷新后保持
      localStorage.setItem('language', item.value);
      show.value = false;
      console.log("当前语言已切换为:", locale.value); // 你可以按 F12 看看控制台有没有这行字
    };
    
    defineExpose({ open: () => { show.value = true; } });
    </script>