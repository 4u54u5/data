/**
 * MFSK音声波形生成
 *
 * - サンプリング周波数: 48000Hz
 * - シンボル長: 100ms
 * - 振幅: 0.5
 * - シンボル境界に5msフェード（ポップノイズ防止）
 * - 先頭・末尾に100ms無音
 */

import { SAMPLE_RATE, SYMBOL_MS, nibbleToFrequency } from './mfsk'

const AMPLITUDE = 0.5
const FADE_MS = 5  // フェードイン/アウト時間

export function generateMfskWave(nibbles: number[]): Float32Array {
  const samplesPerSymbol = Math.round(SAMPLE_RATE * SYMBOL_MS / 1000)
  const fadeSamples = Math.round(SAMPLE_RATE * FADE_MS / 1000)
  const silenceSamples = Math.round(SAMPLE_RATE * 100 / 1000)  // 100ms無音

  const totalSamples = silenceSamples + nibbles.length * samplesPerSymbol + silenceSamples
  const output = new Float32Array(totalSamples)

  let writePos = silenceSamples  // 先頭無音の後から書き込む

  for (const nibble of nibbles) {
    const freq = nibbleToFrequency(nibble)
    const omega = 2 * Math.PI * freq / SAMPLE_RATE

    // 前のシンボルとの位相連続性を保つため、絶対時刻ベースで位相計算
    // （ポップノイズをフェードで抑える）
    for (let i = 0; i < samplesPerSymbol; i++) {
      const t = writePos + i
      let sample = AMPLITUDE * Math.sin(omega * t)

      // フェードイン（シンボル先頭5ms）
      if (i < fadeSamples) {
        sample *= i / fadeSamples
      }
      // フェードアウト（シンボル末尾5ms）
      else if (i >= samplesPerSymbol - fadeSamples) {
        sample *= (samplesPerSymbol - i) / fadeSamples
      }

      output[writePos + i] = sample
    }

    writePos += samplesPerSymbol
  }

  // 末尾は0（無音）のままなのでそのままでOK

  return output
}

/**
 * Float32Arrayの波形をWeb Audio APIで再生する
 * Audioコンテキストを返すので呼び出し元でcloseできる
 */
export async function playWave(samples: Float32Array): Promise<AudioContext> {
  const ctx = new AudioContext({ sampleRate: SAMPLE_RATE })

  const buffer = ctx.createBuffer(1, samples.length, SAMPLE_RATE)
  const channelData = buffer.getChannelData(0)
  channelData.set(samples)

  const source = ctx.createBufferSource()
  source.buffer = buffer
  source.connect(ctx.destination)
  source.start()

  return ctx
}
