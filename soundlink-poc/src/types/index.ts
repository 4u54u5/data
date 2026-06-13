// 型定義

export interface ReceiverCallbacks {
  onText?: (text: string) => void
  onBytes?: (bytes: Uint8Array) => void
  onDebug?: (message: string) => void
  onLevel?: (level: number) => void
  onSpectrum?: (spectrum: Float32Array) => void
  onCrc?: (ok: boolean) => void
}

export interface TransmitterState {
  inputText: string
  packetHex: string
  nibbles: number[]
  isSending: boolean
}

export interface ReceiverState {
  isListening: boolean
  level: number
  spectrum: Float32Array
  receivedHex: string
  decodedText: string
  crcOk: boolean | null
  debugLog: string[]
}
