/**
 * 16-FSK変調定数と変換ユーティリティ
 *
 * 周波数割当:
 *   0x0=1600Hz, 0x1=1700Hz, ..., 0xF=3100Hz
 */

export const SAMPLE_RATE = 48000
export const SYMBOL_MS = 100
export const BASE_FREQ = 1600
export const STEP_FREQ = 100
export const SYMBOL_COUNT = 16

/**
 * バイト列をニブル列（4bit値の配列）に変換
 * 上位4bitを先に、下位4bitを後に並べる
 */
export function bytesToNibbles(bytes: Uint8Array): number[] {
  const nibbles: number[] = []
  for (const b of bytes) {
    nibbles.push((b >> 4) & 0x0f)
    nibbles.push(b & 0x0f)
  }
  return nibbles
}

/**
 * ニブル列をバイト列に変換
 * 奇数長の場合は末尾を0でパディング
 */
export function nibblesToBytes(nibbles: number[]): Uint8Array {
  const len = Math.ceil(nibbles.length / 2)
  const bytes = new Uint8Array(len)
  for (let i = 0; i < len; i++) {
    const hi = nibbles[i * 2] ?? 0
    const lo = nibbles[i * 2 + 1] ?? 0
    bytes[i] = ((hi & 0x0f) << 4) | (lo & 0x0f)
  }
  return bytes
}

/**
 * ニブル(0-15)を対応周波数(Hz)に変換
 */
export function nibbleToFrequency(nibble: number): number {
  return BASE_FREQ + (nibble & 0x0f) * STEP_FREQ
}

/**
 * 周波数(Hz)を最も近いニブル(0-15)に変換
 */
export function frequencyToNibble(freq: number): number {
  const nibble = Math.round((freq - BASE_FREQ) / STEP_FREQ)
  return Math.max(0, Math.min(15, nibble))
}
