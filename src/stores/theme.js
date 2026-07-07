import { defineStore } from 'pinia';
import { applyTheme, themes } from '@/theme';

const STORAGE_KEY = 'truthfi-theme';
const isValidTheme = (theme) => theme === 'light' || theme === 'dark';

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light',
  }),

  getters: {
    currentTheme: (state) => themes[state.theme] || themes.light,
    isDark: (state) => state.theme === 'dark',
  },

  actions: {
    initializeTheme() {
      const savedTheme = localStorage.getItem(STORAGE_KEY);
      this.theme = isValidTheme(savedTheme) ? savedTheme : 'light';
      applyTheme(this.theme);
    },

    setTheme(theme) {
      if (!isValidTheme(theme)) return;
      this.theme = theme;
      localStorage.setItem(STORAGE_KEY, theme);
      applyTheme(theme);
    },

    toggleTheme() {
      this.setTheme(this.theme === 'dark' ? 'light' : 'dark');
    },
  },
});
