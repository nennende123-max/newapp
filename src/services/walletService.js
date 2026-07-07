import { walletConnect } from '@/api/user'
import { APP_MODES, getAppMode } from '@/config/appMode'

const MOCK_ADDRESS = '0xDEMO_USER_001'
const SESSION_KEY = 'truthfi_wallet_session'

const createTimeoutError = (message, code) => {
  const error = new Error(message)
  error.code = code
  return error
}

const withTimeout = (promise, ms, message, code = 'REQUEST_TIMEOUT') => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(createTimeoutError(message, code)), ms)
    Promise.resolve(promise)
      .then(value => {
        clearTimeout(timer)
        resolve(value)
      })
      .catch(error => {
        clearTimeout(timer)
        reject(error)
      })
  })
}

const readSession = () => {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')
  } catch (error) {
    return null
  }
}

const saveSession = (session) => {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
  return session
}

const createDevSignature = (message) => {
  return `mock_signature:${btoa(unescape(encodeURIComponent(message))).slice(0, 32)}`
}

class WalletService {
  constructor() {
    this.address = readSession()?.address || ''
    this.connected = Boolean(readSession()?.connected)
  }

  get mode() {
    return getAppMode()
  }

  checkWalletInstalled() {
    if (this.mode === APP_MODES.DEV) return true
    return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined'
  }

  async connectWallet() {
    if (this.mode === APP_MODES.DEV) {
      this.address = MOCK_ADDRESS
      this.connected = true
      return saveSession({
        address: MOCK_ADDRESS,
        connected: true,
        authenticated: true,
        mode: APP_MODES.DEV
      })
    }

    if (!this.checkWalletInstalled()) {
      throw createTimeoutError('Please install MetaMask wallet first', 'WALLET_NOT_INSTALLED')
    }

    const accounts = await withTimeout(
      window.ethereum.request({ method: 'eth_requestAccounts' }),
      30000,
      'Wallet authorization timeout. Please check MetaMask and retry.',
      'WALLET_REQUEST_TIMEOUT'
    )

    if (!accounts || accounts.length === 0) {
      throw createTimeoutError('No wallet address detected', 'WALLET_ADDRESS_EMPTY')
    }

    this.address = accounts[0]
    this.connected = true
    return {
      address: this.address,
      connected: true,
      mode: this.mode
    }
  }

  async signMessage(message) {
    const currentAddress = await this.getAddress()

    if (this.mode === APP_MODES.DEV) {
      return {
        address: currentAddress,
        signature: createDevSignature(message),
        message,
        mode: APP_MODES.DEV
      }
    }

    if (!currentAddress) {
      throw createTimeoutError('Wallet address unavailable', 'WALLET_ADDRESS_EMPTY')
    }

    const signature = await withTimeout(
      window.ethereum.request({
        method: 'personal_sign',
        params: [message, currentAddress]
      }),
      60000,
      'Signature timeout. Please confirm in MetaMask and retry.',
      'SIGN_TIMEOUT'
    )

    return {
      address: currentAddress,
      signature,
      message,
      mode: this.mode
    }
  }

  async createSession(message, options = {}) {
    const wallet = await this.connectWallet()
    const signed = await this.signMessage(message)

    if (this.mode === APP_MODES.DEV) {
      return saveSession({
        address: wallet.address,
        connected: true,
        authenticated: true,
        mode: APP_MODES.DEV,
        signature: signed.signature,
        token: 'dev_mock_token'
      })
    }

    if (this.mode === APP_MODES.TEST) {
      return saveSession({
        address: wallet.address,
        connected: true,
        authenticated: true,
        mode: APP_MODES.TEST,
        signature: signed.signature,
        token: 'test_signed_session'
      })
    }

    const payload = {
      address: signed.address,
      signature: signed.signature,
      message: signed.message,
      nonce: options.nonce || null,
      domain: window.location.host,
      uri: window.location.origin,
      chainId: options.chainId || null
    }

    const response = await withTimeout(
      walletConnect(payload),
      20000,
      'Login verification timeout. Please retry later.',
      'AUTH_TIMEOUT'
    )

    if (!response?.data || response.data.code !== 200 || !response.data.data) {
      throw createTimeoutError('Authentication failed: invalid server response', 'AUTH_FAILED')
    }

    return saveSession({
      address: wallet.address,
      connected: true,
      authenticated: true,
      mode: APP_MODES.PROD,
      signature: signed.signature,
      token: response.data.data.token,
      raw: response.data.data
    })
  }

  async getAddress() {
    if (this.address) return this.address

    const session = readSession()
    if (session?.address) {
      this.address = session.address
      this.connected = Boolean(session.connected)
      return this.address
    }

    if (this.mode === APP_MODES.DEV) {
      this.address = MOCK_ADDRESS
      this.connected = true
      return this.address
    }

    if (!this.checkWalletInstalled()) return ''
    const accounts = await window.ethereum.request({ method: 'eth_accounts' })
    this.address = accounts?.[0] || ''
    this.connected = Boolean(this.address)
    return this.address
  }

  getWalletState() {
    const session = readSession()
    return {
      address: session?.address || this.address || '',
      connected: Boolean(session?.connected || this.connected),
      authenticated: Boolean(session?.authenticated),
      mode: this.mode,
      session
    }
  }

  disconnect() {
    this.address = ''
    this.connected = false
    localStorage.removeItem(SESSION_KEY)
  }
}

export const walletService = new WalletService()
export default walletService
