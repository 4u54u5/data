/**
 * 16候補周波数の強度を棒グラフ表示するコンポーネント
 */

import { useEffect, useRef } from 'react'
import { BASE_FREQ, STEP_FREQ, SYMBOL_COUNT } from '../lib/mfsk'

interface Props {
  spectrum: Float32Array  // 長さ16: 各周波数のパワー値
}

export default function SpectrumView({ spectrum }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const W = canvas.width
    const H = canvas.height

    ctx.clearRect(0, 0, W, H)

    // 背景
    ctx.fillStyle = '#0d0d1a'
    ctx.fillRect(0, 0, W, H)

    const barW = Math.floor(W / SYMBOL_COUNT) - 2
    const maxPower = Math.max(...spectrum, 1e-10)  // 0除算防止

    for (let i = 0; i < SYMBOL_COUNT; i++) {
      const normalized = spectrum[i] / maxPower
      const barH = Math.round(normalized * (H - 20))
      const x = i * (barW + 2) + 1

      // バー
      const hue = 200 + i * 10
      ctx.fillStyle = `hsl(${hue}, 80%, 55%)`
      ctx.fillRect(x, H - 20 - barH, barW, barH)

      // 周波数ラベル（1600, 1800, ... のみ表示）
      if (i % 2 === 0) {
        ctx.fillStyle = '#888'
        ctx.font = '9px monospace'
        ctx.textAlign = 'center'
        ctx.fillText(`${(BASE_FREQ + i * STEP_FREQ) / 100}`, x + barW / 2, H - 4)
      }
    }

    // グリッド線
    ctx.strokeStyle = '#333'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(0, H - 20)
    ctx.lineTo(W, H - 20)
    ctx.stroke()
  }, [spectrum])

  return (
    <canvas
      ref={canvasRef}
      width={320}
      height={120}
      style={{ display: 'block', borderRadius: 4, border: '1px solid #333' }}
    />
  )
}
