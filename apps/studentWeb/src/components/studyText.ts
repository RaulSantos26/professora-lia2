import { defineComponent, h } from 'vue'

// Only render a small, safe teaching-text subset. Model output is never HTML.
export function inlineText(text: string) {
  return text.split(/(\*\*[^*\n]+\*\*)/g).map(part =>
    part.startsWith('**') && part.endsWith('**') && part.length > 4
      ? h('strong', part.slice(2, -2))
      : part
  )
}

export function studyBlocks(text: string) {
  const lines = text.replace(/\r\n?/g, '\n').split('\n')
  const blocks = []
  for (let index = 0; index < lines.length;) {
    const line = lines[index]
    if (!line.trim()) { index++; continue }
    if (/^\s*```/.test(line)) {
      const code = []
      index++
      while (index < lines.length && !/^\s*```/.test(lines[index])) code.push(lines[index++])
      if (index < lines.length) index++
      blocks.push(h('pre', [h('code', code.join('\n'))]))
      continue
    }
    const heading = line.match(/^\s{0,3}#{1,6}\s+(.+)$/)
    if (heading) { blocks.push(h('h4', inlineText(heading[1]))); index++; continue }
    const list = line.match(/^\s*(?:([-*•])|(\d+)[.)])\s+(.+)$/)
    if (list) {
      const ordered = Boolean(list[2])
      const items = []
      while (index < lines.length) {
        const item = lines[index].match(/^\s*(?:([-*•])|(\d+)[.)])\s+(.+)$/)
        if (!item || Boolean(item[2]) !== ordered) break
        items.push(h('li', inlineText(item[3])))
        index++
      }
      blocks.push(h(ordered ? 'ol' : 'ul', ordered ? { start: Number(list[2]) } : {}, items))
      continue
    }
    blocks.push(h('p', inlineText(line)))
    index++
  }
  return blocks
}

export default defineComponent({
  name: 'StudyText',
  props: { text: { type: String, required: true } },
  setup: props => () => h('div', { class: 'studyText' }, studyBlocks(props.text))
})
