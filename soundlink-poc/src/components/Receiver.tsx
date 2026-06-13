/**
 * 受信側コンポーネント
 * マイク入力 → FFT/Goertzel → 復調 → CRC確認 → テキスト表示
 */

import { useState, useCallback, useRef } from 'react'
import { MfskReceiver } from '../lib/audioRx'
import LevelMeter from './LevelMeter'
import SpectrumView from './SpectrumView'

const EMPTY_SPECTRUM = new Float32Array(16)

export default function Receiver() {
  const [isListening, setIsListening] = useState(false)
  const [level, setLevel] = useState(0)
  const [spectrum, setSpectrum] = useState<Float32Array>(EMPTY_SPECTRUM)
  const [receivedHex, setReceivedHex] = useState('')
  const [decodedText, setDecodedText] = useState('')
  const [crcOk, setCrcOk] = useState<boolean | null>(null)
  const [debugLog, setDebugLog] = useState<string[]>([])

  const receiverRef = useRef<MfskReceiver | null>(null)

  const addLog = (msg: string) =>
    setDebugLog(prev => [`[RX] ${msg}`, ...prev].slice(0, 50))

  const handleStart = useCallback(async () => {
    if (isListening) return

    const rx = new MfskReceiver({
      onText: (text) => {
        setDecodedText(text)
        addLog(`Decoded text: ${text}`)
      },
      onBytes: (bytes) => {
        const hex = Array.from(bytes).map(b => b.toString(16).padStart(2, '0').toUpperCase()).join(' ')
        setReceivedHex(hex)
        addLog(`RX bytes (${bytes.length}): ${hex}`)
      },
      onDebug: (msg) => addLog(msg),
      onLevel: (lv) => setLevel(lv),
      onSpectrum: (sp) => setSpectrum(new Float32Array(sp)),
      onCrc: (ok) => {
        setCrcOk(ok)
        addLog(ok ? 'CRC OK ✓' : 'CRC NG ✗')
      },
    })

    try {
      await rx.start()
      receiverRef.current = rx
      setIsListening(true)
      addLog('Listening...')
    } catch (e) {
      addLog(`Error: ${e}`)
    }
  }, [isListening])

  const handleStop = useCallback(() => {
    receiverRef.current?.stop()
    receiverRef.current = null
    setIsListening(false)
    setLevel(0)
    setSpectrum(EMPTY_SPECTRUM)
    addLog('Stopped')
  }, [])

  const crcColor = crcOk === null ? '#888' : crcOk ? '#00ff88' : '#e94560'
  const crcLabel = crcOk === null ? '---' : crcOk ? 'CRC OK ✓' : 'CRC NG ✗'

  return (
    <div style={styles.panel}>
      <h2 style={styles.title}>受信 (RX)</h2>

      <div style={styles.btnRow}>
        <button
          style={{ ...styles.btn, ...(isListening ? styles.btnDisabled : {}) }}
          onClick={handleStart}
          disabled={isListening}
        >
          マイク開始
        </button>
        <button
          style={{ ...styles.btnStop, ...(!isListening ? styles.btnDisabled : {}) }}
          onClick={handleStop}
          disabled={!isListening}
        >
          マイク停止
        </button>
        <span style={{ ...styles.statusDot, background: isListening ? '#00ff88' : '#555' }} />
        <span style={{ color: isListening ? '#00ff88' : '#555', fontFamily: 'monospace', fontSize: 12 }}>
          {isListening ? 'LISTENING' : 'STOPPED'}
        </span>
      </div>

      <div style={styles.section}>
        <label style={styles.label}>入力レベル</label>
        <LevelMeter level={level} />
      </div>

      <div style={styles.section}>
        <label style={styles.label}>スペクトラム (1600〜3100Hz)</label>
        <SpectrumView spectrum={spectrum} />
      </div>

      <div style={styles.section}>
        <label style={styles.label}>受信HEX</label>
        <div style={styles.hexBox}>{receivedHex || '—'}</div>
      </div>

      <div style={styles.resultRow}>
        <div style={styles.section}>
          <label style={styles.label}>復元テキスト</label>
          <div style={{ ...styles.hexBox, fontSize: 20, color: '#ffffff', minHeight: 40 }}>
            {decodedText || '—'}
          </div>
        </div>

        <div style={styles.section}>
          <label style={styles.label}>CRC</label>
          <div style={{ ...styles.hexBox, color: crcColor, fontWeight: 'bold', fontSize: 16, textAlign: 'center' }}>
            {crcLabel}
          </div>
        </div>
      </div>

      <div style={styles.section}>
        <label style={styles.label}>デバッグログ</label>
        <div style={styles.logBox}>
          {debugLog.map((l, i) => (
            <div key={i} style={{ color: l.includes('OK') ? '#00ff88' : l.includes('NG') || l.includes('Error') ? '#e94560' : '#888' }}>
              {l}
            </div>
          ))}
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
    minWidth: 340,
    flex: 1,
  },
  title: {
    color: '#00b4d8',
    marginTop: 0,
    marginBottom: 16,
    fontSize: 18,
    fontFamily: 'monospace',
  },
  btnRow: { display: 'flex', gap: 8, alignItems: 'center', marginBottom: 16 },
  btn: {
    padding: '8px 16px',
    background: '#00b4d8',
    border: 'none',
    borderRadius: 4,
    color: '#000',
    fontFamily: 'monospace',
    fontSize: 14,
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  btnStop: {
    padding: '8px 16px',
    background: '#e94560',
    border: 'none',
    borderRadius: 4,
    color: '#fff',
    fontFamily: 'monospace',
    fontSize: 14,
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  btnDisabled: { background: '#333', color: '#555', cursor: 'not-allowed' },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: '50%',
    display: 'inline-block',
    marginLeft: 4,
  },
  section: { marginBottom: 12 },
  label: {
    display: 'block',
    color: '#a0a0b0',
    fontSize: 12,
    marginBottom: 4,
    fontFamily: 'monospace',
  },
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
  resultRow: { display: 'flex', gap: 12 },
  logBox: {
    background: '#0d0d1a',
    border: '1px solid #333',
    borderRadius: 4,
    padding: '6px 10px',
    fontFamily: 'monospace',
    fontSize: 11,
    height: 150,
    overflowY: 'auto',
    lineHeight: 1.6,
  },
}
