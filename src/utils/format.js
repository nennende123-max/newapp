/**
 * 资产格式化工具函数
 * 统一处理不同币种的数值显示格式
 */

/**
 * 格式化资产数量
 * @param {number} value - 资产数量
 * @param {string} symbol - 币种符号（如 'USDT', 'BTC', 'ETH'）
 * @returns {string} 格式化后的字符串
 * 
 * 精度规则：
 * - USDT: 强制保留 2 位小数
 * - BTC/ETH: 最多保留 8 位小数，去除末尾多余的 0
 * - 其他小币种: 保留 4 位小数
 * 
 * 使用 Math.floor 截断（只舍不入），确保不产生进位误差
 */
export function formatAssetAmount(value, symbol = '') {
  // 处理无效值
  if (value === null || value === undefined || isNaN(value)) {
    return '0.00';
  }

  // 确保 value 是数字类型
  const numValue = Number(value);
  
  // 如果值为 0，直接返回
  if (numValue === 0) {
    return '0.00';
  }

  // 根据币种确定精度
  let precision;
  let maxDecimals;
  
  const symbolUpper = symbol.toUpperCase();
  
  if (symbolUpper === 'USDT') {
    // USDT: 强制保留 2 位小数
    precision = 100; // 10^2
    maxDecimals = 2;
  } else if (symbolUpper === 'BTC' || symbolUpper === 'ETH') {
    // BTC/ETH: 最多保留 8 位小数，去除末尾多余的 0
    precision = 100000000; // 10^8
    maxDecimals = 8;
  } else {
    // 其他小币种: 保留 4 位小数
    precision = 10000; // 10^4
    maxDecimals = 4;
  }

  // 使用 Math.floor 截断（只舍不入）
  const truncatedValue = Math.floor(numValue * precision) / precision;

  // 格式化：去除末尾多余的 0
  // 对于 BTC/ETH，使用 toFixed(maxDecimals) 然后去除末尾 0
  // 对于 USDT，强制保留 2 位小数
  let formatted;
  
  if (symbolUpper === 'BTC' || symbolUpper === 'ETH') {
    // BTC/ETH: 去除末尾多余的 0
    formatted = truncatedValue.toFixed(maxDecimals).replace(/\.?0+$/, '');
    // 如果去除后没有小数部分，且值为整数，保持整数显示
    // 如果去除后没有小数部分，但值有小数，至少显示 2 位小数
    if (!formatted.includes('.') && truncatedValue !== Math.floor(truncatedValue)) {
      formatted = truncatedValue.toFixed(2);
    }
  } else {
    // USDT 和其他币种: 使用固定小数位数
    formatted = truncatedValue.toFixed(maxDecimals);
  }

  return formatted;
}

/**
 * 格式化资产数量（带千分位分隔符）
 * @param {number} value - 资产数量
 * @param {string} symbol - 币种符号
 * @returns {string} 格式化后的字符串（带千分位）
 */
export function formatAssetAmountWithSeparator(value, symbol = '') {
  const formatted = formatAssetAmount(value, symbol);
  
  // 如果值很大，添加千分位分隔符
  const parts = formatted.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  
  return parts.join('.');
}
