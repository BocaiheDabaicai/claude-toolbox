#!/usr/bin/env node
// 用法：
//   node scripts/scaffold.mjs <target-dir> [--name my-app] [--title "我的应用"] [--force]
// 作用：复制 Nuxt 全栈业务模板，替换占位符，生成 docs 与 .env。
import { randomBytes } from 'node:crypto'
import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptPath = fileURLToPath(import.meta.url)
const skillRoot = resolve(dirname(scriptPath), '..')
const templateDir = join(skillRoot, 'assets', 'template')
const docsTemplateDir = join(skillRoot, 'assets', 'docs-templates')

function fail(message) {
  console.error(`\n[scaffold] ${message}\n`)
  process.exit(1)
}

function parseArgs(argv) {
  const result = { target: '', name: '', title: '', force: false, help: false }
  const positional = []
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--force') result.force = true
    else if (arg === '--name') result.name = argv[++index] || ''
    else if (arg === '--title') result.title = argv[++index] || ''
    else if (arg === '--help' || arg === '-h') result.help = true
    else if (arg.startsWith('--')) fail(`未知参数：${arg}`)
    else positional.push(arg)
  }
  result.target = positional[0] || ''
  return result
}

function slugify(value) {
  return (
    String(value)
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'nuxt-app'
  )
}

function assertTemplate() {
  if (!existsSync(templateDir)) fail(`找不到模板目录：${templateDir}`)
  if (!existsSync(docsTemplateDir)) fail(`找不到文档模板目录：${docsTemplateDir}`)
}

function copyTemplate(target) {
  if (existsSync(target) && readdirSync(target).length > 0 && !args.force) {
    fail(
      `目标目录非空：${target}\n如需覆盖，追加 --force（不会删除目标里已有的其他文件）。`,
    )
  }
  mkdirSync(target, { recursive: true })
  cpSync(templateDir, target, { recursive: true })

  const docsDir = join(target, 'docs')
  mkdirSync(docsDir, { recursive: true })
  for (const file of readdirSync(docsTemplateDir)) {
    cpSync(join(docsTemplateDir, file), join(docsDir, file))
  }
}

function isTextFile(file) {
  const name = basename(file)
  if (name.startsWith('.env')) return true
  return /\.(ts|mjs|json|vue|md|toml|css|txt|example)$/i.test(name)
}

function replaceAllInFile(file, replacements) {
  if (!isTextFile(file)) return
  const raw = readFileSync(file, 'utf8')
  let next = raw
  for (const [from, to] of Object.entries(replacements)) {
    next = next.split(from).join(to)
  }
  if (next !== raw) writeFileSync(file, next)
}

function walk(dir, replacements) {
  for (const entry of readdirSync(dir)) {
    if (entry === 'node_modules' || entry === '.nuxt' || entry === '.output') continue
    const full = join(dir, entry)
    const stat = statSync(full)
    if (stat.isDirectory()) walk(full, replacements)
    else replaceAllInFile(full, replacements)
  }
}

function prepareEnv(target) {
  const example = join(target, '.env.example')
  const envPath = join(target, '.env')
  if (!existsSync(example) || existsSync(envPath)) return false

  const secret = randomBytes(48).toString('base64')
  const content = readFileSync(example, 'utf8').replace(
    'replace-with-at-least-32-random-characters',
    secret,
  )
  writeFileSync(envPath, content)
  return true
}

const args = parseArgs(process.argv.slice(2))

if (args.help || !args.target) {
  console.log(`
用法：
  node scripts/scaffold.mjs <target-dir> [选项]

选项：
  --name <slug>    项目 slug / package.json 名称，默认取目标目录名
  --title <标题>    页面标题与文档标题，默认同 name
  --force           目标目录非空时仍然写入（不删除已有文件）
`)
  process.exit(args.help ? 0 : 1)
}

assertTemplate()

const target = resolve(args.target)
const projectName = slugify(args.name || basename(target))
if (!/^[a-z0-9][a-z0-9-]*$/.test(projectName)) {
  fail(`项目 slug 不合法：${projectName}`)
}
const projectTitle = args.title || args.name || projectName

copyTemplate(target)

walk(target, {
  __PROJECT_NAME__: projectName,
  __PROJECT_SLUG__: projectName,
  __PROJECT_DB__: projectName.replace(/-/g, '_'),
  __PROJECT_TITLE__: projectTitle,
})

const envCreated = prepareEnv(target)

console.log(`
[scaffold] 已生成：${target}
  项目名：${projectName}
  标题：${projectTitle}
  ${envCreated ? '已生成 .env，并随机生成 NUXT_SESSION_SECRET' : '.env 已存在，未覆盖'}

下一步：
  cd ${target}
  # 修改 .env：NUXT_DATABASE_URL、SEED_ADMIN_EMAIL、SEED_ADMIN_PASSWORD
  pnpm install
  pnpm db:generate
  pnpm db:migrate
  pnpm db:seed
  pnpm dev

接入顺序：
  1. 先填 docs/brief.md、docs/features.md、docs/data-model.md
  2. 按业务域改 server/database/schema.ts，再 pnpm db:generate
  3. 在 server/api 增加接口，在 shared/schemas 增加 Zod 校验
  4. 在 app/pages 增加页面，复用 PageHeader / EmptyState / daisyUI 组件类
  5. pnpm check && pnpm build
  6. 部署前确认 ops/project.toml 与端口、健康路径一致
`)
