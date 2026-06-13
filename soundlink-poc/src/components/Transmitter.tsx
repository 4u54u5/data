/**
 * 送信側コンポーネント
 * テキスト入力 → パケット生成 → MFSK波形生成 → 再生 / WAV保存
 */

import { useState, useCallback } from 'react'
import { encodePacket } from '../lib/packet'
import { bytesToNibbles } from '../lib/mfsk'
import { generateMfskWave, playWave } from '../lib/audioTx'
import { float32ToWavBlob } from '../lib/wav'

export default function Transmitter() {
  const [inputText, setInputText] = useState('HELLO1234')
  const [packetHex, setPacketHex] = useState('')
  const [nibbleStr, setNibbleStr] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [log, setLog] = useState<string[]>([])

  const addLog = (msg: string) =>
    setLog(prev => [`[TX] ${msg}`, ...prev].slice(0, 20))

  const buildPacket = useCallback(() => {
    const packet = encodePacket(inputText)
    const hex = Array.from(packet).map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ')
    const nibbles = bytesToNibbles(packet)
    const nibStr = nibbles.map(n => n.toString(16).toUpperCase()).join(' ')
    setPacketHex(hex)
    setNibbleStr(nibStr)
    addLog(`Packet: ${hex}`)
    addLog(`Nibbles: ${nibStr}`)
    return { packet, nibbles }
  }, [inputText])

  const handleSend = useCallback(async () => {
    if (isSending) return
    setIsSending(true)
    addLog(`Sending: "${inputText}"`)
    try {
      const { nibbles } = buildPacket()
      const wave = generateMfskWave(nibbles)
      addLog(`Wave length: ${wave.length} samples (${(wave.length / 48000).toFixed(2)}s)`)
      await playWave(wave)
      addLog('Playback started')
    } catch (e) {
      addLog(`Error: ${e}`)
    } finally {
      setIsSending(false)
    }
  }, [inputText, isSending, buildPacket])

  const handleSaveWav = useCallback(() => {
    try {
      const { nibbles } = buildPacket()
      const wave = generateMfskWave(nibbles)
      const blob = float32ToWavBlob(wave, 48000)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `soundlink_${Date.now()}.wav`
      a.click()
      URL.revokeObjectURL(url)
      addLog('WAV saved')
    } catch (e) {
      addLog(`WAV save error: ${e}`)
    }
  }, [buildPacket])

  return (
    <div style={styles.panel}>
      <h2 style={styles.title}>送信 (TX)</h2>

      <div style={styles.row}>
        <label style={styles.label}>送信テキスト</label>
        <input
          style={styles.input}
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          maxLength={64}
          placeholder="最大64文字"
        />
      </div>

      <div style={styles.btnRow}>
        <button
          style={{ ...styles.btn, ...(isSending ? styles.btnDisabled : {}) }}
          onClick={handleSend}
          disabled={isSending}
        >
          {isSending ? '送信中...' : '送信'}
        </button>
        <button style={styles.btnSecondary} onClick={handleSaveWav}>
          WAV保存
        </button>
      </div>

      <div style={styles.section}>
        <label style={styles.label}>パケットHEX</label>
        <div style={styles.hexBox}>{packetHex || '—'}</div>
      </div>

      <div style={styles.section}>
        <label style={styles.label}>シンボル列（ニブル）</label>
        <div style={styles.hexBox}>{nibbleStr || '—'}</div>
      </div>

      <div style={styles.section}>
        <label style={styles.label}>ログ</label>
        <div style={styles.logBox}>
          {log.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  panel: {
    background: '#16213e',
    border: '1px solid #0f3460',
    borderRadius: 8,
    padding: 16,
    minWidth: 320,
    flex: 1,
  },
  title: {
    color: '#e94560',
    marginTop: 0,
    marginBottom: 16,
    fontSize: 18,
    fontFamily: 'monospace',
  },
  row: { marginBottom: 12 },
  label: {
    display: 'block',
    color: '#a0a0b0',
    fontSize: 12,
    marginBottom: 4,
    fontFamily: 'monospace',
  },
  input: {
    width: '100%',
    padding: '8px 10px',
    background: '#0d0d1a',
    border: '1px solid #0f3460',
    borderRadius: 4,
    color: '#e0e0ff',
    fontFamily: 'monospace',
    fontSize: 16,
    boxSizing: 'border-box',
  },
  btnRow: { display: 'flex', gap: 8, marginBottom: 16 },
  btn: {
    padding: '8px 20px',
    background: '#e94560',
    border: 'none',
    borderRadius: 4,
    color: '#fff',
    fontFamily: 'monospace',
    fontSize: 14,
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  btnDisabled: { background: '#555', cursor: 'not-allowed' },
  btnSecondary: {
    padding: '8px 20px',
    background: '#0f3460',
    border: '1px solid #444',
    borderRadius: 4,
    color: '#e0e0ff',
    fontFamily: 'monospace',
    fontSize: 14,
    cursor: 'pointer',
  },
  section: { marginBottom: 12 },
  hexBox: {
    background: '#0d0d1a',
    border: '1px solid #333',
    borderRadius: 4,
    padding: '6px 10px',
    color: '#00ff88',
    fontFamily: 'monospace',
    fontSize: 12,
    wordBreak: 'break-all',
    minHeight: 32,
    lineHeight: 1.6,
  },
  logBox: {
    background: '#0d0d1a',
    border: '1px solid #333',
    borderRadius: 4,
    padding: '6px 10px',
    color: '#888',
    fontFamily: 'monospace',
    fontSize: 11,
    height: 100,
    overflowY: 'auto',
    lineHeight: 1.5,
  },
}
