export function getThemeColor(tokenName) {
  if (typeof window === 'undefined') return '';

  return getComputedStyle(document.documentElement)
    .getPropertyValue(tokenName)
    .trim();
}
