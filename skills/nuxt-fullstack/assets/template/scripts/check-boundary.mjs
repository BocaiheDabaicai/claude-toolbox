import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'

const root = process.cwd()
const sourceDirs = ['app', 'shared']
const extensions = new Set(['.ts', '.js', '.mjs', '.vue'])

const rules = [
  { pattern: /from\s+['"][^'"]*server\//, message: '客户端代码不能引用 server/' },
  { pattern: /from\s+['"]drizzle-orm/, message: '客户端代码不能引用 drizzle-orm' },
  { pattern: /from\s+['"]pg['"]/, message: '客户端代码不能引用 pg' },
  { pattern: /from\s+['"]node:/, message: '客户端代码不能引用 node: 内置模块' },
  {
    pattern: /NUXT_SESSION_SECRET|NUXT_DATABASE_URL/,
    message: '客户端代码不能读取服务端密钥或数据库地址',
  },
]

const violations = []

function walk(dir) {
  let entries
  try {
    entries = readdirSync(dir)
  } catch {
    return
  }
  for (const entry of entries) {
    const full = join(dir, entry)
    const stat = statSync(full)
    if (stat.isDirectory()) {
      if (entry === 'node_modules' || entry === '.nuxt' || entry === '.output') continue
      walk(full)
      continue
    }
    if (!extensions.has(full.slice(full.lastIndexOf('.')))) continue

    const lines = readFileSync(full, 'utf8').split(/\r?\n/)
    lines.forEach((line, index) => {
      for (const rule of rules) {
        if (rule.pattern.test(line)) {
          violations.push({
            file: relative(root, full),
            line: index + 1,
            message: rule.message,
          })
        }
      }
    })
  }
}

for (const dir of sourceDirs) walk(join(root, dir))

if (violations.length) {
  console.error('\n[边界检查未通过] 客户端代码越界访问服务端能力：\n')
  for (const item of violations) {
    console.error(`  ${item.file}:${item.line}  ${item.message}`)
  }
  console.error('\n数据库、会话、密钥逻辑只允许放在 server/ 下。\n')
  process.exit(1)
}

console.log('[边界检查] 通过：app/ 与 shared/ 未引用服务端能力。')
