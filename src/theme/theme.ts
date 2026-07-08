export type ThemeName = 'light' | 'dark';

type ThemeTokens = {
  name: ThemeName;
  colors: Record<string, string>;
  background: Record<string, string>;
  surface: Record<string, string>;
  text: Record<string, string>;
  border: Record<string, string>;
  primary: Record<string, string>;
  status: Record<'success' | 'danger' | 'warning', string>;
  shadows: Record<string, string>;
  cssVars: Record<string, string>;
};

const shared = {
  primary: '#F3BA2F',
  primaryRgb: '243 186 47',
  coinBtc: '#F7931A',
  coinEth: '#627EEA',
  coinSol: '#9945FF',
  coinUsdt: '#26A17B',
  coinAic: '#4ECDC4',
  coinMeme: '#95E1D3',
  referralStart: '#8B5CF6',
  referralEnd: '#6D28D9',
};

export const lightTheme: ThemeTokens = {
  name: 'light',
  colors: {
    bg: '#ffffff',
    surface1: '#f7f8fa',
    surface2: '#ffffff',
    border: '#eaecef',
    primary: shared.primary,
    success: '#16a34a',
    danger: '#ef4444',
    warning: '#f59e0b',
  },
  background: {
    page: '#f7f8fa',
    base: '#ffffff',
    elevated: '#f7f8fa',
    input: '#ffffff',
  },
  surface: {
    muted: '#eef2f6',
    card: '#ffffff',
    elevated: '#ffffff',
  },
  text: {
    primary: '#111827',
    secondary: '#6b7280',
    muted: '#9ca3af',
    inverse: '#ffffff',
    onAccent: '#111111',
  },
  border: {
    default: '#eaecef',
    subtle: '#f0f2f5',
    strong: '#d7dde6',
  },
  primary: {
    default: shared.primary,
    hover: '#D99A00',
    soft: `rgb(${shared.primaryRgb} / 0.12)`,
    border: `rgb(${shared.primaryRgb} / 0.38)`,
  },
  status: {
    success: '#16a34a',
    danger: '#ef4444',
    warning: '#f59e0b',
  },
  shadows: {
    sm: '0 1px 2px rgb(17 24 39 / 0.05)',
    md: '0 8px 20px rgb(17 24 39 / 0.07), 0 1px 2px rgb(17 24 39 / 0.04)',
    lg: '0 18px 48px rgb(17 24 39 / 0.14)',
  },
  cssVars: {
    '--color-bg': '#ffffff',
    '--color-surface-1': '#f7f8fa',
    '--color-surface-2': '#ffffff',
    '--color-bg-elevated': '#f7f8fa',
    '--color-bg-card': '#ffffff',
    '--color-bg-input': '#ffffff',
    '--color-surface': '#f7f8fa',
    '--color-surface-elevated': '#ffffff',
    '--color-surface-muted': '#eef2f6',
    '--color-primary': shared.primary,
    '--color-primary-hover': '#D99A00',
    '--color-primary-soft': `rgb(${shared.primaryRgb} / 0.12)`,
    '--color-primary-border': `rgb(${shared.primaryRgb} / 0.38)`,
    '--color-brand': shared.primary,
    '--color-brand-legacy': shared.primary,
    '--color-accent': shared.primary,
    '--color-accent-strong': '#D99A00',
    '--color-success': '#16a34a',
    '--color-danger': '#ef4444',
    '--color-warning': '#f59e0b',
    '--color-earn': '#16a34a',
    '--color-loss': '#ef4444',
    '--color-text-primary': '#111827',
    '--color-text-secondary': '#6b7280',
    '--color-text-muted': '#9ca3af',
    '--color-text-on-accent': '#111111',
    '--color-text-inverse': '#ffffff',
    '--color-border': '#eaecef',
    '--color-border-subtle': '#f0f2f5',
    '--color-border-strong': '#d7dde6',
    '--color-focus-ring': `rgb(${shared.primaryRgb} / 0.24)`,
    '--color-overlay': 'rgb(17 17 17 / 0.45)',
    '--color-overlay-strong': 'rgb(17 17 17 / 0.7)',
    '--color-bg-rgb': '255 255 255',
    '--color-surface-rgb': '247 248 250',
    '--color-surface-2-rgb': '255 255 255',
    '--color-text-primary-rgb': '17 24 39',
    '--color-text-secondary-rgb': '107 114 128',
    '--color-text-muted-rgb': '156 163 175',
    '--color-border-rgb': '234 236 239',
    '--color-shadow-rgb': '17 24 39',
    '--color-primary-rgb': shared.primaryRgb,
    '--color-brand-rgb': shared.primaryRgb,
    '--color-brand-legacy-rgb': shared.primaryRgb,
    '--color-success-rgb': '22 163 74',
    '--color-danger-rgb': '239 68 68',
    '--color-warning-rgb': '245 158 11',
    '--color-earn-rgb': '22 163 74',
    '--color-loss-rgb': '239 68 68',
    '--color-qr-dark': '#111111',
    '--color-qr-light': '#ffffff',
    '--shadow-sm': '0 1px 2px rgb(17 24 39 / 0.05)',
    '--shadow-md': '0 8px 20px rgb(17 24 39 / 0.07), 0 1px 2px rgb(17 24 39 / 0.04)',
    '--shadow-lg': '0 18px 48px rgb(17 24 39 / 0.14)',
  },
};

export const darkTheme: ThemeTokens = {
  name: 'dark',
  colors: {
    bg: '#0B1220',
    surface1: '#151E2E',
    surface2: '#172133',
    border: 'rgba(255,255,255,0.08)',
    primary: shared.primary,
    success: '#22c55e',
    danger: '#f87171',
    warning: '#f59e0b',
  },
  background: {
    page: '#0B1220',
    base: '#0B1220',
    elevated: '#151E2E',
    input: '#172133',
  },
  surface: {
    muted: '#202B3D',
    card: '#151E2E',
    elevated: '#172133',
  },
  text: {
    primary: '#F8FAFC',
    secondary: '#CBD5E1',
    muted: '#94A3B8',
    inverse: '#0B1220',
    onAccent: '#111111',
  },
  border: {
    default: 'rgba(255,255,255,0.08)',
    subtle: 'rgba(255,255,255,0.08)',
    strong: 'rgba(255,255,255,0.16)',
  },
  primary: {
    default: shared.primary,
    hover: '#D6A21F',
    soft: `rgb(${shared.primaryRgb} / 0.14)`,
    border: `rgb(${shared.primaryRgb} / 0.32)`,
  },
  status: {
    success: '#22c55e',
    danger: '#f87171',
    warning: '#f59e0b',
  },
  shadows: {
    sm: '0 1px 2px rgb(0 0 0 / 0.28)',
    md: '0 12px 28px rgb(0 0 0 / 0.32), 0 1px 0 rgb(255 255 255 / 0.03) inset',
    lg: '0 24px 56px rgb(0 0 0 / 0.42)',
  },
  cssVars: {
    '--color-bg': '#0B1220',
    '--color-surface-1': '#151E2E',
    '--color-surface-2': '#172133',
    '--color-bg-elevated': '#151E2E',
    '--color-bg-card': '#151E2E',
    '--color-bg-input': '#172133',
    '--color-surface': '#151E2E',
    '--color-surface-elevated': '#172133',
    '--color-surface-muted': '#202B3D',
    '--color-primary': shared.primary,
    '--color-primary-hover': '#D6A21F',
    '--color-primary-soft': `rgb(${shared.primaryRgb} / 0.14)`,
    '--color-primary-border': `rgb(${shared.primaryRgb} / 0.32)`,
    '--color-brand': shared.primary,
    '--color-brand-legacy': shared.primary,
    '--color-accent': shared.primary,
    '--color-accent-strong': '#D6A21F',
    '--color-success': '#22c55e',
    '--color-danger': '#f87171',
    '--color-warning': '#f59e0b',
    '--color-earn': '#22c55e',
    '--color-loss': '#f87171',
    '--color-text-primary': '#F8FAFC',
    '--color-text-secondary': '#CBD5E1',
    '--color-text-muted': '#94A3B8',
    '--color-text-on-accent': '#111111',
    '--color-text-inverse': '#0B1220',
    '--color-border': 'rgba(255,255,255,0.08)',
    '--color-border-subtle': 'rgba(255,255,255,0.08)',
    '--color-border-strong': 'rgba(255,255,255,0.16)',
    '--color-focus-ring': `rgb(${shared.primaryRgb} / 0.22)`,
    '--color-overlay': 'rgb(0 0 0 / 0.58)',
    '--color-overlay-strong': 'rgb(0 0 0 / 0.78)',
    '--color-bg-rgb': '11 18 32',
    '--color-surface-rgb': '21 30 46',
    '--color-surface-2-rgb': '23 33 51',
    '--color-text-primary-rgb': '248 250 252',
    '--color-text-secondary-rgb': '203 213 225',
    '--color-text-muted-rgb': '148 163 184',
    '--color-border-rgb': '255 255 255',
    '--color-shadow-rgb': '0 0 0',
    '--color-primary-rgb': shared.primaryRgb,
    '--color-brand-rgb': shared.primaryRgb,
    '--color-brand-legacy-rgb': shared.primaryRgb,
    '--color-success-rgb': '34 197 94',
    '--color-danger-rgb': '248 113 113',
    '--color-warning-rgb': '245 158 11',
    '--color-earn-rgb': '34 197 94',
    '--color-loss-rgb': '248 113 113',
    '--color-qr-dark': '#111827',
    '--color-qr-light': '#f8fafc',
    '--shadow-sm': '0 1px 2px rgb(0 0 0 / 0.28)',
    '--shadow-md': '0 12px 28px rgb(0 0 0 / 0.32), 0 1px 0 rgb(255 255 255 / 0.03) inset',
    '--shadow-lg': '0 24px 56px rgb(0 0 0 / 0.42)',
  },
};

export const themes = {
  light: lightTheme,
  dark: darkTheme,
};

export const applyTheme = (themeName: ThemeName) => {
  if (typeof document === 'undefined') return;

  const theme = themes[themeName] ?? lightTheme;
  const root = document.documentElement;

  root.dataset.theme = theme.name;
  root.style.colorScheme = theme.name;

  Object.entries(theme.cssVars).forEach(([token, value]) => {
    root.style.setProperty(token, value);
  });
};
