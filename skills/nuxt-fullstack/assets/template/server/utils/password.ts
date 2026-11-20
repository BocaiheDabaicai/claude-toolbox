import { randomBytes, scryptSync, timingSafeEqual } from 'node:crypto'

const N = 16384
const R = 8
const P = 1
const KEY_LENGTH = 64
const MAX_MEM = 64 * 1024 * 1024

export function hashPassword(password: string): string {
  const salt = randomBytes(16)
  const hash = scryptSync(password, salt, KEY_LENGTH, {
    N,
    r: R,
    p: P,
    maxmem: MAX_MEM,
  })
  return `scrypt$${N}$${R}$${P}$${salt.toString('base64')}$${hash.toString('base64')}`
}

export function verifyPassword(password: string, stored: string): boolean {
  const parts = stored.split('$')
  if (parts.length !== 6 || parts[0] !== 'scrypt') return false

  const [, n, r, p, saltBase64, hashBase64] = parts
  if (!saltBase64 || !hashBase64) return false
  const salt = Buffer.from(saltBase64, 'base64')
  const expected = Buffer.from(hashBase64, 'base64')
  if (!expected.length) return false

  const parsedN = Number(n)
  const parsedR = Number(r)
  const parsedP = Number(p)
  if (!Number.isInteger(parsedN) || !Number.isInteger(parsedR) || !Number.isInteger(parsedP)) {
    return false
  }

  const actual = scryptSync(password, salt, expected.length, {
    N: parsedN,
    r: parsedR,
    p: parsedP,
    maxmem: MAX_MEM,
  })
  return actual.length === expected.length && timingSafeEqual(actual, expected)
}
