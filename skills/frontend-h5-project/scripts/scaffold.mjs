#!/usr/bin/env node
// 用法：
//   node scripts/scaffold.mjs <target-dir> [--name my-app] [--title "我的应用"] [--api https://api.example.com/] [--force]
// 作用：把 assets/template 复制到目标目录，替换项目名/标题/接口地址/存储前缀，并生成 docs 模板。
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
  const result = { target: '', name: '', title: '', api: '', force: false }
  const positional = []
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--force') result.force = true
    else if (arg === '--name') result.name = argv[++index] || ''
    else if (arg === '--title') result.title = argv[++index] || ''
    else if (arg === '--api') result.api = argv[++index] || ''
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
      .replace(/^-+|-+$/g, '') || 'h5-app'
  )
}

function assertTemplate() {
  if (!existsSync(templateDir)) fail(`找不到模板目录：${templateDir}`)
  if (!existsSync(docsTemplateDir)) fail(`找不到文档模板目录：${docsTemplateDir}`)
}

function copyTemplate(target) {
  if (existsSync(target) && readdirSync(target).length > 0 && !args.force) {
    fail(`目标目录非空：${target}\n如需覆盖，追加 --force（不会删除目标里已有的其他文件）。`)
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
  return /\.(js|mjs|json|vue|md|html|css|svg|txt)$/i.test(name)
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
    const full = join(dir, entry)
    const stat = statSync(full)
    if (stat.isDirectory()) walk(full, replacements)
    else replaceAllInFile(full, replacements)
  }
}

const args = parseArgs(process.argv.slice(2))

if (args.help || !args.target) {
  console.log(`
用法：
  node scripts/scaffold.mjs <target-dir> [选项]

选项：
  --name <slug>        package.json 名称，默认取目标目录名
  --title <标题>       页面标题与文档标题，默认同 name
  --api <url>          接口 Base URL，默认 http://localhost:8080/
  --force              目标目录非空时仍然写入（不删除已有文件）
`)
  process.exit(args.help ? 0 : 1)
}

assertTemplate()

const target = resolve(args.target)
const projectName = slugify(args.name || basename(target))
const projectTitle = args.title || args.name || projectName
const apiBase = args.api || 'http://localhost:8080/'
const storagePrefix = projectName.replace(/-/g, '_')

copyTemplate(target)

const replacements = {
  __PROJECT_NAME__: projectName,
  __PROJECT_TITLE__: projectTitle,
  __API_BASE__: apiBase,
  __STORAGE_PREFIX__: storagePrefix,
}
walk(target, replacements)

console.log(`
[scaffold] 已生成：${target}
  项目名：${projectName}
  标题：${projectTitle}
  接口地址：${apiBase}
  存储前缀：${storagePrefix}

下一步：
  cd ${target}
  pnpm install
  pnpm dev

接入顺序：
  1. 阅读 docs/architecture.md 与 docs/backend-contract.md
  2. 按目标后端实现 src/utils/request.js 与 src/stores/user.js
  3. 在 src/router/routes.js 登记页面，替换 src/views 占位页
  4. 接入真实登录后删除 stores/user.js 的 loginDemo 与登录页演示入口
  5. pnpm build，并确认 pnpm-lock.yaml 无非预期改动
`)
