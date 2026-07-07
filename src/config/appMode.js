const allowedModes = ['dev', 'test', 'prod']

export const APP_MODES = {
  DEV: 'dev',
  TEST: 'test',
  PROD: 'prod'
}

export const getAppMode = () => {
  const runtimeMode = localStorage.getItem('APP_MODE')
  const envMode = import.meta.env.VITE_APP_MODE
  const mode = (runtimeMode || envMode || APP_MODES.DEV).toLowerCase()
  return allowedModes.includes(mode) ? mode : APP_MODES.DEV
}

export const setAppMode = (mode) => {
  const normalized = String(mode || '').toLowerCase()
  if (!allowedModes.includes(normalized)) {
    throw new Error(`Unsupported APP_MODE: ${mode}`)
  }
  localStorage.setItem('APP_MODE', normalized)
  return normalized
}

export const isDevMode = () => getAppMode() === APP_MODES.DEV
export const isTestMode = () => getAppMode() === APP_MODES.TEST
export const isProdMode = () => getAppMode() === APP_MODES.PROD
