/**
 * 模拟网络请求工具
 * 用于模拟网络延迟和标准响应格式
 */

/**
 * 模拟网络请求
 * @param {Function|any} callbackOrData - 回调函数或直接返回的数据
 * @param {Object} options - 配置选项
 * @param {number} options.minDelay - 最小延迟时间（毫秒），默认 500
 * @param {number} options.maxDelay - 最大延迟时间（毫秒），默认 1500
 * @param {boolean} options.shouldFail - 是否模拟失败，默认 false
 * @param {string} options.errorMsg - 失败时的错误消息，默认 'Request failed'
 * @returns {Promise} 返回 Promise，resolve 时包含标准响应格式
 */
export function mockRequest(callbackOrData, options = {}) {
  const {
    minDelay = 500,
    maxDelay = 1500,
    shouldFail = false,
    errorMsg = 'Request failed'
  } = options;

  // 生成随机延迟时间
  const delay = Math.floor(Math.random() * (maxDelay - minDelay + 1)) + minDelay;

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (shouldFail) {
        // 失败响应格式
        reject({
          code: 500,
          msg: errorMsg
        });
      } else {
        // 成功响应格式
        let data;
        
        if (typeof callbackOrData === 'function') {
          // 如果是函数，执行函数获取数据
          try {
            data = callbackOrData();
          } catch (error) {
            reject({
              code: 500,
              msg: error.message || 'Callback execution failed'
            });
            return;
          }
        } else {
          // 如果是数据，直接使用
          data = callbackOrData;
        }

        resolve({
          code: 200,
          msg: 'success',
          data
        });
      }
    }, delay);
  });
}

/**
 * 模拟成功请求（便捷方法）
 * @param {Function|any} callbackOrData - 回调函数或直接返回的数据
 * @param {number} minDelay - 最小延迟时间（毫秒），默认 500
 * @param {number} maxDelay - 最大延迟时间（毫秒），默认 1500
 * @returns {Promise} 返回 Promise
 */
export function mockSuccess(callbackOrData, minDelay = 500, maxDelay = 1500) {
  return mockRequest(callbackOrData, { minDelay, maxDelay, shouldFail: false });
}

/**
 * 模拟失败请求（便捷方法）
 * @param {string} errorMsg - 错误消息，默认 'Request failed'
 * @param {number} minDelay - 最小延迟时间（毫秒），默认 500
 * @param {number} maxDelay - 最大延迟时间（毫秒），默认 1500
 * @returns {Promise} 返回 Promise（会被 reject）
 */
export function mockError(errorMsg = 'Request failed', minDelay = 500, maxDelay = 1500) {
  return mockRequest(null, { minDelay, maxDelay, shouldFail: true, errorMsg });
}

export default {
  mockRequest,
  mockSuccess,
  mockError
};

