/**
 * リアルタイムMFSK受信器
 *
 * Goertzel法で各候補周波数のエネルギーを検出し、
 * プリアンブル → SYNC → LEN → PAYLOAD → CRC の順に復調する。
 */

import { SAMPLE_RATE, SYMBOL_MS, SYMBOL_COUNT, BASE_FREQ, STEP_FREQ, nibblesToBytes } from './mfsk'
import { tryDecodePacket } from './packet'
import type { ReceiverCallbacks } from '../types'

const SAMPLES_PER_SYMBOL = Math.round(SAMPLE_RATE * SYMBOL_MS / 1000)  // = 4800

// 候補周波数リスト (1600Hz〜3100Hz, 100Hzステップ)
const CANDIDATE_FREQS: number[] = Array.from(
  { length: SYMBOL_COUNT },
  (_, i) => BASE_FREQ + i * STEP_FREQ
)

/**
 * Goertzel法で単一周波数のエネルギーを計算する
 * @returns 正規化されたパワー値
 */
function goertzel(samples: Float32Array, freq: number, sampleRate: number): number {
  const N = samples.length
  const k = freq / sampleRate * N
  const omega = 2 * Math.PI * k / N
  const cos2 = 2 * Math.cos(omega)

  let s0 = 0, s1 = 0, s2 = 0
  for (let i = 0; i < N; i++) {
    s0 = samples[i] + cos2 * s1 - s2
    s2 = s1
    s1 = s0
  }

  // パワー = s1^2 + s2^2 - s1*s2*cos2
  const power = s1 * s1 + s2 * s2 - s1 * s2 * cos2
  return power / (N * N)
}

/**
 * サンプル配列から最も強い周波数のニブルを返す
 * 同時にスペクトラム配列（各候補周波数のパワー）を更新する
 */
function detectNibble(samples: Float32Array, spectrumOut: Float32Array): number {
  let maxPower = -1
  let bestNibble = 0

  for (let i = 0; i < SYMBOL_COUNT; i++) {
    const power = goertzel(samples, CANDIDATE_FREQS[i], SAMPLE_RATE)
    spectrumOut[i] = power
    if (power > maxPower) {
      maxPower = power
      bestNibble = i
    }
  }

  return bestNibble
}

// 受信FSM状態
type RxState =
  | 'HUNT'       // プリアンブル探索中
  | 'SYNC'       // SYNCパターン待ち
  | 'LEN'        // LENバイト待ち
  | 'PAYLOAD'    // PAYLOAD受信中
  | 'CRC'        // CRC受信中

export class MfskReceiver {
  private callbacks: ReceiverCallbacks
  private audioCtx: AudioContext | null = null
  private stream: MediaStream | null = null
  private processor: ScriptProcessorNode | null = null
  private analyser: AnalyserNode | null = null

  // 受信ニブル列
  private rxNibbles: number[] = []

  // FSM状態
  private state: RxState = 'HUNT'
  private preambleCount = 0  // 0xAAが連続した回数（ニブル単位: AA=nibble(0xA),nibble(0xA)）
  private expectedLen = 0

  // スペクトラム出力バッファ
  private spectrum: Float32Array = new Float32Array(SYMBOL_COUNT)

  constructor(callbacks: ReceiverCallbacks) {
    this.callbacks = callbacks
  }

  async start(): Promise<void> {
    this.audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE })

    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
        sampleRate: SAMPLE_RATE,
      }
    })

    const source = this.audioCtx.createMediaStreamSource(this.stream)

    // レベルメーター用アナライザー
    this.analyser = this.audioCtx.createAnalyser()
    this.analyser.fftSize = 2048
    source.connect(this.analyser)

    // ScriptProcessorでサンプルを取得（bufferSize = SAMPLES_PER_SYMBOL）
    // 注: ScriptProcessorはdeprecatedだがWorkletより実装が簡単なためPoCでは採用
    const bufSize = SAMPLES_PER_SYMBOL  // 4800 @ 48kHz
    this.processor = this.audioCtx.createScriptProcessor(bufSize, 1, 1)
    source.connect(this.processor)
    this.processor.connect(this.audioCtx.destination)

    this.processor.onaudioprocess = (e: AudioProcessingEvent) => {
      const input = e.inputBuffer.getChannelData(0)
      this.processSamples(input)
    }

    this.callbacks.onDebug?.('Microphone started')
  }

  stop(): void {
    this.processor?.disconnect()
    this.analyser?.disconnect()
    this.stream?.getTracks().forEach(t => t.stop())
    this.audioCtx?.close()
    this.processor = null
    this.analyser = null
    this.stream = null
    this.audioCtx = null
    this.callbacks.onDebug?.('Microphone stopped')
  }

  private processSamples(input: Float32Array): void {
    // 入力レベル計算 (RMS)
    let sumSq = 0
    for (let i = 0; i < input.length; i++) sumSq += input[i] * input[i]
    const rms = Math.sqrt(sumSq / input.length)
    this.callbacks.onLevel?.(rms)

    // ScriptProcessorのbufferSizeがSAMPLES_PER_SYMBOLと一致しているので
    // そのまま1シンボルとして処理できる
    const nibble = detectNibble(input, this.spectrum)
    this.callbacks.onSpectrum?.(this.spectrum.slice())

    this.callbacks.onDebug?.(`RX nibble: 0x${nibble.toString(16).toUpperCase()}`)

    this.processNibble(nibble)
  }

  /**
   * ニブルを受け取り、FSMで状態遷移する
   */
  private processNibble(nibble: number): void {
    switch (this.state) {
      case 'HUNT':
        this.huntPreamble(nibble)
        break

      case 'SYNC':
        this.receiveSyncNibble(nibble)
        break

      case 'LEN':
      case 'PAYLOAD':
      case 'CRC':
        this.rxNibbles.push(nibble)
        this.checkPacketProgress()
        break
    }
  }

  /**
   * プリアンブル探索
   * AA AA AA AA = ニブル列: A A A A A A A A (8ニブル)
   */
  private huntPreamble(nibble: number): void {
    if (nibble === 0xA) {
      this.preambleCount++
      if (this.preambleCount >= 8) {
        // プリアンブル検出 → SYNC待ちへ
        this.callbacks.onDebug?.('Preamble detected!')
        this.state = 'SYNC'
        this.rxNibbles = []
        this.preambleCount = 0
      }
    } else {
      // プリアンブル途切れ
      this.preambleCount = 0
    }
  }

  /**
   * SYNCパターン受信 (2D D4 = ニブル: 2 D D 4)
   */
  private syncNibbles: number[] = []

  private receiveSyncNibble(nibble: number): void {
    this.syncNibbles.push(nibble)

    if (this.syncNibbles.length === 4) {
      const expected = [0x2, 0xD, 0xD, 0x4]
      const ok = this.syncNibbles.every((n, i) => n === expected[i])

      if (ok) {
        this.callbacks.onDebug?.('Sync detected!')
        this.state = 'LEN'
        this.rxNibbles = []
      } else {
        this.callbacks.onDebug?.(
          `Bad sync: ${this.syncNibbles.map(n => n.toString(16)).join(' ')} - back to HUNT`
        )
        this.reset()
      }
      this.syncNibbles = []
    }
  }

  /**
   * LEN → PAYLOAD → CRC 受信の進捗チェック
   */
  private checkPacketProgress(): void {
    if (this.state === 'LEN' && this.rxNibbles.length === 2) {
      // LENは1バイト = 2ニブル
      const len = ((this.rxNibbles[0] << 4) | this.rxNibbles[1]) & 0xff
      this.callbacks.onDebug?.(`LEN = ${len}`)
      this.expectedLen = len
      this.state = 'PAYLOAD'
    }

    if (this.state === 'PAYLOAD') {
      const neededNibbles = 2 + this.expectedLen * 2
      if (this.rxNibbles.length >= neededNibbles) {
        this.state = 'CRC'
      }
    }

    if (this.state === 'CRC') {
      // LEN(2) + PAYLOAD(len*2) + CRC(4ニブル=2バイト)
      const neededNibbles = 2 + this.expectedLen * 2 + 4
      if (this.rxNibbles.length >= neededNibbles) {
        this.finalizePacket()
      }
    }
  }

  /**
   * パケット組み立て・CRC検証
   */
  private finalizePacket(): void {
    // rxNibbles → bytes へ変換
    // PREAMBLE(AA AA AA AA) + SYNC(2D D4) を付け直してtryDecodePacketに渡す
    const preambleNibbles = [0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA, 0xA]
    const syncNibbles = [0x2, 0xD, 0xD, 0x4]
    const allNibbles = [...preambleNibbles, ...syncNibbles, ...this.rxNibbles]
    const bytes = nibblesToBytes(allNibbles)

    const hex = Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join(' ')
    this.callbacks.onDebug?.(`RX bytes: ${hex}`)
    this.callbacks.onBytes?.(bytes)

    const result = tryDecodePacket(bytes)

    if (result.ok && result.text !== undefined) {
      this.callbacks.onDebug?.(`CRC OK! Decoded: ${result.text}`)
      this.callbacks.onCrc?.(true)
      this.callbacks.onText?.(result.text)
    } else {
      this.callbacks.onDebug?.(`CRC NG: ${result.error}`)
      this.callbacks.onCrc?.(false)
    }

    this.reset()
  }

  private reset(): void {
    this.state = 'HUNT'
    this.preambleCount = 0
    this.rxNibbles = []
    this.syncNibbles = []
    this.expectedLen = 0
  }
}
