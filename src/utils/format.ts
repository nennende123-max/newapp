type NumericInput = number | string | null | undefined

const DEFAULT_LOCALE = 'en-US'

export const toSafeNumber = (value: NumericInput, fallback = 0): number => {
  if (value === null || value === undefined || value === '') return fallback
  const number = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(number) ? number : fallback
}

const safeLocaleString = (
  value: number,
  options: Intl.NumberFormatOptions = {},
  locale = DEFAULT_LOCALE
): string => {
  try {
    return value.toLocaleString(locale, options)
  } catch (error) {
    console.warn('[format] toLocaleString failed:', error)
    return String(value)
  }
}

export const formatInteger = (value: NumericInput, locale = DEFAULT_LOCALE): string => {
  return safeLocaleString(Math.trunc(toSafeNumber(value)), {
    maximumFractionDigits: 0
  }, locale)
}

export const formatNumber = (
  value: NumericInput,
  digits = 2,
  locale = DEFAULT_LOCALE
): string => {
  const precision = Math.max(0, Math.min(20, Math.trunc(toSafeNumber(digits))))
  return safeLocaleString(toSafeNumber(value), {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision
  }, locale)
}

export const formatCurrency = (
  value: NumericInput,
  currency = 'USD',
  digits = 2,
  locale = DEFAULT_LOCALE
): string => {
  const precision = Math.max(0, Math.min(20, Math.trunc(toSafeNumber(digits))))
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: precision,
      maximumFractionDigits: precision
    }).format(toSafeNumber(value))
  } catch (error) {
    console.warn('[format] formatCurrency failed:', error)
    return `${currency} ${formatNumber(value, precision, locale)}`
  }
}

export function formatAssetAmount(value: NumericInput, symbol = ''): string {
  const numValue = toSafeNumber(value)
  if (numValue === 0) return '0.00'

  let precision: number
  let maxDecimals: number
  const symbolUpper = String(symbol || '').toUpperCase()

  if (symbolUpper === 'USDT') {
    precision = 100
    maxDecimals = 2
  } else if (symbolUpper === 'BTC' || symbolUpper === 'ETH') {
    precision = 100000000
    maxDecimals = 8
  } else {
    precision = 10000
    maxDecimals = 4
  }

  const truncatedValue = Math.floor(numValue * precision) / precision

  if (symbolUpper === 'BTC' || symbolUpper === 'ETH') {
    const formatted = truncatedValue.toFixed(maxDecimals).replace(/\.?0+$/, '')
    if (!formatted.includes('.') && truncatedValue !== Math.floor(truncatedValue)) {
      return truncatedValue.toFixed(2)
    }
    return formatted
  }

  return truncatedValue.toFixed(maxDecimals)
}

export function formatAssetAmountWithSeparator(value: NumericInput, symbol = ''): string {
  const formatted = formatAssetAmount(value, symbol)
  const parts = formatted.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return parts.join('.')
}
