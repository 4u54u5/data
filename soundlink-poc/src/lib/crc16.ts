/**
 * CRC-16/CCITT-FALSE
 * poly   = 0x1021
 * init   = 0xFFFF
 * xorout = 0x0000
 * refin  = false
 * refout = false
 */

// 事前計算テーブルでパフォーマンスを向上
const TABLE = (() => {
  const t = new Uint16Array(256)
  for (let i = 0; i < 256; i++) {
    let crc = i << 8
    for (let j = 0; j < 8; j++) {
      crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1)
    }
    t[i] = crc & 0xffff
  }
  return t
})()

export function crc16CcittFalse(data: Uint8Array): number {
  let crc = 0xffff
  for (const byte of data) {
    crc = ((crc << 8) ^ TABLE[((crc >> 8) ^ byte) & 0xff]) & 0xffff
  }
  return crc
}
