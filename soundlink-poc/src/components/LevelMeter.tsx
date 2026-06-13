/**
 * マイク入力レベルをバー表示するコンポーネント
 */

import { useEffect, useRef } from 'react'

interface Props {
  level: number  // 0.0 〜 1.0 (RMS値)
}

export default function LevelMeter({ level }: Props) {
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
    ctx.fillStyle = '#1a1a2e'
    ctx.fillRect(0, 0, W, H)

    // レベルバー
    const barWidth = Math.min(1, level * 5) * (W - 4)  // RMSは小さいので5倍スケール
    const hue = 120 - level * 600  // 緑→赤
    ctx.fillStyle = `hsl(${Math.max(0, hue)}, 90%, 50%)`
    ctx.fillRect(2, 2, barWidth, H - 4)

    // ボーダー
    ctx.strokeStyle = '#444'
    ctx.strokeRect(0, 0, W, H)
  }, [level])

  return (
    <canvas
      ref={canvasRef}
      width={300}
      height={20}
      style={{ display: 'block', borderRadius: 4 }}
    />
  )
}
