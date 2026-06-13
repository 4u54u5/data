/**
 * Float32Array → 16bit PCM WAVファイル変換
 */

export function float32ToWavBlob(samples: Float32Array, sampleRate: number): Blob {
  const numChannels = 1
  const bitsPerSample = 16
  const bytesPerSample = bitsPerSample / 8
  const blockAlign = numChannels * bytesPerSample
  const byteRate = sampleRate * blockAlign
  const dataBytes = samples.length * bytesPerSample

  const buffer = new ArrayBuffer(44 + dataBytes)
  const view = new DataView(buffer)

  // RIFFチャンクヘッダ
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataBytes, true)
  writeString(view, 8, 'WAVE')

  // fmtサブチャンク
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)          // fmtチャンクサイズ
  view.setUint16(20, 1, true)           // PCMフォーマット
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, byteRate, true)
  view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitsPerSample, true)

  // dataサブチャンク
  writeString(view, 36, 'data')
  view.setUint32(40, dataBytes, true)

  // サンプルデータをFloat32 → Int16に変換して書き込む
  let offset = 44
  for (let i = 0; i < samples.length; i++) {
    // クリッピングして[-1, 1]に収める
    const s = Math.max(-1, Math.min(1, samples[i]))
    // 16bit符号付き整数に変換
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
    offset += 2
  }

  return new Blob([buffer], { type: 'audio/wav' })
}

function writeString(view: DataView, offset: number, str: string): void {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i))
  }
}
