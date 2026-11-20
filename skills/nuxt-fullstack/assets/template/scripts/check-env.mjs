import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'))
const PNPM_VERSION = '9.15.9'
const NODE_RANGE = pkg.engines?.node || '^22.19.0 || >=24.11.0'

function fail(title, details) {
  console.error('')
  console.error(`[环境检查未通过] ${title}`)
  console.error('')
  for (const line of details) console.error(line)
  console.error('')
  console.error('修复环境后重新执行：pnpm install')
  console.error('')
  process.exit(1)
}

const ua = process.env.npm_config_user_agent || ''
const pnpmMatch = /^pnpm\/(\d+)\.(\d+)\.(\d+)/.exec(ua)
if (!pnpmMatch) {
  const detected = ua.split(' ')[0] || '未知包管理器'
  fail(`本项目只接受 pnpm ${PNPM_VERSION} 安装依赖，检测到 ${detected}。`, [
    'npm / yarn 会生成另一套锁文件，导致依赖版本漂移，因此不能用于安装。',
    '',
    '无需全局安装 pnpm，直接执行：',
    '  npx pnpm@9.15.9 install',
    '',
    '或先全局安装 pnpm：',
    '  npm i -g pnpm@9.15.9',
    '  pnpm install',
  ])
}

const pnpmVersion = `${pnpmMatch[1]}.${pnpmMatch[2]}.${pnpmMatch[3]}`
if (pnpmMatch[1] !== '9') {
  fail(`pnpm 版本不匹配：需要 9.x（锁定 ${PNPM_VERSION}），当前为 ${pnpmVersion}。`, [
    '安装 pnpm 9：',
    '  corepack enable',
    `  corepack prepare pnpm@${PNPM_VERSION} --activate`,
    '',
    '或：',
    `  npm i -g pnpm@${PNPM_VERSION}`,
  ])
}

const [nodeMajor, nodeMinor] = process.versions.node.split('.').map(Number)
const nodeOk =
  (nodeMajor === 22 && nodeMinor >= 19) ||
  (nodeMajor === 24 && nodeMinor >= 11) ||
  nodeMajor >= 26
if (!nodeOk) {
  fail(`Node.js 版本不匹配：需要 ${NODE_RANGE}，当前为 v${process.versions.node}。`, [
    '请升级 Node.js：',
    '  https://nodejs.org/',
    '',
    'Nuxt 4.5 要求 Node 22.19+、24.11+ 或 26+。',
  ])
}

let lockText = ''
try {
  lockText = readFileSync(join(root, 'pnpm-lock.yaml'), 'utf8')
} catch {
  console.warn('[环境检查] 首次安装：pnpm-lock.yaml 尚不存在，本次安装后会生成，请提交到仓库。')
}

if (lockText) {
  const firstLine = lockText.split(/\r?\n/, 1)[0]
  const lockVersion = firstLine.replace(/^lockfileVersion:\s*'?/, '').replace(/'$/, '')
  if (!lockVersion.startsWith('9.')) {
    fail(`锁文件版本不匹配：需要 9.x，当前为 ${lockVersion || '未知'}。`, [
      'pnpm-lock.yaml 可能被旧版 pnpm 重写过，请恢复锁文件而不是删除：',
      '  git checkout -- pnpm-lock.yaml',
      '',
      '然后使用 pnpm 9 重新安装：',
      '  npx pnpm@9.15.9 install',
    ])
  }
}
