/**
 * パケットエンコード/デコード
 *
 * フォーマット: [PREAMBLE(4)][SYNC(2)][LEN(1)][PAYLOAD(N)][CRC16(2)]
 *   PREAMBLE = AA AA AA AA
 *   SYNC     = 2D D4
 *   LEN      = PAYLOAD長 (1byte, 最大64)
 *   CRC対象  = [SYNC][LEN][PAYLOAD]
 */

import { crc16CcittFalse } from './crc16'

const PREAMBLE = new Uint8Array([0xaa, 0xaa, 0xaa, 0xaa])
const SYNC = new Uint8Array([0x2d, 0xd4])
const MAX_PAYLOAD = 64

export function encodePacket(text: string): Uint8Array {
  const payload = new TextEncoder().encode(text)
  if (payload.length > MAX_PAYLOAD) {
    throw new Error(`Payload too long: ${payload.length} > ${MAX_PAYLOAD}`)
  }

  const len = payload.length

  // CRC対象: [SYNC][LEN][PAYLOAD]
  const crcData = new Uint8Array(2 + 1 + len)
  crcData.set(SYNC, 0)
  crcData[2] = len
  crcData.set(payload, 3)
  const crc = crc16CcittFalse(crcData)

  // 全体バッファ組み立て
  const total = PREAMBLE.length + SYNC.length + 1 + len + 2
  const packet = new Uint8Array(total)
  let offset = 0
  packet.set(PREAMBLE, offset); offset += PREAMBLE.length
  packet.set(SYNC, offset);     offset += SYNC.length
  packet[offset++] = len
  packet.set(payload, offset);  offset += len
  packet[offset++] = (crc >> 8) & 0xff  // CRC high byte
  packet[offset++] = crc & 0xff          // CRC low byte

  return packet
}

export function tryDecodePacket(bytes: Uint8Array): {
  ok: boolean
  text?: string
  error?: string
} {
  // 最小長チェック: PREAMBLE(4) + SYNC(2) + LEN(1) + CRC(2) = 9
  if (bytes.length < 9) {
    return { ok: false, error: `Too short: ${bytes.length} bytes` }
  }

  // PREAMBLE確認
  for (let i = 0; i < 4; i++) {
    if (bytes[i] !== 0xaa) {
      return { ok: false, error: `Bad preamble at byte ${i}: 0x${bytes[i].toString(16)}` }
    }
  }

  // SYNC確認
  if (bytes[4] !== 0x2d || bytes[5] !== 0xd4) {
    return { ok: false, error: `Bad sync: 0x${bytes[4].toString(16)} 0x${bytes[5].toString(16)}` }
  }

  const len = bytes[6]

  if (len > MAX_PAYLOAD) {
    return { ok: false, error: `LEN too large: ${len}` }
  }

  const expectedTotal = 4 + 2 + 1 + len + 2
  if (bytes.length < expectedTotal) {
    return { ok: false, error: `Insufficient data: need ${expectedTotal}, got ${bytes.length}` }
  }

  const payload = bytes.slice(7, 7 + len)

  // CRC検証
  const crcData = new Uint8Array(2 + 1 + len)
  crcData.set(SYNC, 0)
  crcData[2] = len
  crcData.set(payload, 3)
  const expectedCrc = crc16CcittFalse(crcData)

  const receivedCrc = (bytes[7 + len] << 8) | bytes[7 + len + 1]

  if (expectedCrc !== receivedCrc) {
    return {
      ok: false,
      error: `CRC mismatch: expected 0x${expectedCrc.toString(16).padStart(4, '0')}, got 0x${receivedCrc.toString(16).padStart(4, '0')}`
    }
  }

  const text = new TextDecoder().decode(payload)
  return { ok: true, text }
}
