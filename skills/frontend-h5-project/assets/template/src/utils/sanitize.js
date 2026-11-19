// 富文本清洗：只保留白名单标签/属性，移除脚本、事件处理器和危险 URL
// 后端商品描述、文章内容等富文本在 v-html 前统一走这里

const ALLOWED_TAGS = new Set([
  'a', 'abbr', 'b', 'blockquote', 'br', 'caption', 'code', 'col', 'colgroup',
  'dd', 'del', 'div', 'dl', 'dt', 'em', 'figcaption', 'figure', 'h1', 'h2',
  'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'li', 'mark', 'ol', 'p',
  'pre', 'q', 's', 'small', 'source', 'span', 'strong', 'sub', 'sup', 'table',
  'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'u', 'ul', 'video',
])

const DROP_TAGS = new Set([
  'script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'button',
  'textarea', 'select', 'option', 'link', 'meta', 'base', 'svg', 'math',
  'template', 'noscript',
])

const ALLOWED_ATTRS = new Set([
  'align', 'alt', 'class', 'colspan', 'controls', 'height', 'href', 'poster',
  'rel', 'rowspan', 'src', 'style', 'target', 'title', 'type', 'valign',
  'width',
])

const URL_ATTRS = new Set(['href', 'src', 'poster'])
const SAFE_LINK = /^(https?:|mailto:|tel:|\/|#)/i
const SAFE_RESOURCE = /^(https?:|\/|data:image\/(?:png|jpe?g|gif|webp|bmp);base64,)/i
const UNSAFE_STYLE = /expression|javascript:|vbscript:|-moz-binding|behavior\s*:|url\s*\(/i

function cleanAttributes(element) {
  for (const attr of Array.from(element.attributes)) {
    const name = attr.name.toLowerCase()
    const value = attr.value

    if (!ALLOWED_ATTRS.has(name) || name.startsWith('on')) {
      element.removeAttribute(attr.name)
      continue
    }
    if (name === 'href' && !SAFE_LINK.test(value.trim())) {
      element.removeAttribute(attr.name)
      continue
    }
    if ((name === 'src' || name === 'poster') && !SAFE_RESOURCE.test(value.trim())) {
      element.removeAttribute(attr.name)
      continue
    }
    if (name === 'style' && UNSAFE_STYLE.test(value)) {
      element.removeAttribute(attr.name)
    }
  }
  if (element.tagName.toLowerCase() === 'a' && element.getAttribute('target') === '_blank') {
    element.setAttribute('rel', 'noopener noreferrer')
  }
}

function cleanNode(parent) {
  for (const child of Array.from(parent.childNodes)) {
    if (child.nodeType === Node.COMMENT_NODE) {
      child.remove()
      continue
    }
    if (child.nodeType !== Node.ELEMENT_NODE) continue

    const tag = child.tagName.toLowerCase()
    if (!ALLOWED_TAGS.has(tag)) {
      if (DROP_TAGS.has(tag)) {
        child.remove()
        continue
      }
      // 未知但无害的标签（如 font）去掉标签、保留内容
      cleanNode(child)
      child.replaceWith(...Array.from(child.childNodes))
      continue
    }

    cleanAttributes(child)
    cleanNode(child)
  }
}

export function sanitizeHtml(html) {
  if (!html || typeof window === 'undefined' || typeof DOMParser === 'undefined') return ''
  try {
    // DOMParser 生成的是 inert document，脚本不会执行
    const doc = new DOMParser().parseFromString(`<div>${html}</div>`, 'text/html')
    const root = doc.body.firstElementChild
    if (!root) return ''
    cleanNode(root)
    return root.innerHTML
  } catch {
    return ''
  }
}
