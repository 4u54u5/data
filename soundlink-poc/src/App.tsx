/**
 * SoundLink PoC - メインアプリ
 * テキスト → 16-FSK音声 → スピーカー → マイク → 復調 → テキスト
 */

import Transmitter from './components/Transmitter'
import Receiver from './components/Receiver'
import './App.css'

export default function App() {
  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <h1 style={styles.heading}>SoundLink PoC</h1>
        <p style={styles.subtitle}>16-FSK Audio Data Transmission</p>
      </header>

      <main style={styles.main}>
        <Transmitter />
        <Receiver />
      </main>

      <footer style={styles.footer}>
        <span style={{ color: '#333' }}>
          16-FSK · 1600–3100Hz · 100ms/symbol · CRC-16/CCITT-FALSE
        </span>
      </footer>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    minHeight: '100vh',
    background: '#0d0d1a',
    color: '#e0e0ff',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'monospace',
  },
  header: {
    padding: '20px 24px 12px',
    borderBottom: '1px solid #0f3460',
  },
  heading: {
    margin: 0,
    fontSize: 28,
    color: '#e94560',
    letterSpacing: 4,
    textTransform: 'uppercase',
  },
  subtitle: {
    margin: '4px 0 0',
    fontSize: 12,
    color: '#555',
    letterSpacing: 2,
  },
  main: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 16,
    padding: 16,
    flex: 1,
    alignItems: 'flex-start',
  },
  footer: {
    padding: '8px 24px',
    borderTop: '1px solid #0f3460',
    textAlign: 'center',
    fontSize: 11,
  },
}
