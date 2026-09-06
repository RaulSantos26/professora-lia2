export interface MindNode { nodeId: string; parentId: string | null; label: string; detail: string; icon?: string }
export interface MindBranch { node: MindNode; descendants: MindNode[] }
export interface MindDocument { title: string; root: MindNode; branches: MindBranch[] }

// Compatibility adapter: stored node contracts remain the source of truth.
export function mindDocument(spec: Record<string, unknown>): MindDocument {
  const source = Array.isArray(spec.nodes) ? spec.nodes : []
  const nodes: MindNode[] = source.filter(n => n && typeof n === 'object').map((n: any, i) => ({
    nodeId: String(n.nodeId ?? i), parentId: n.parentId == null ? null : String(n.parentId),
    label: String(n.label ?? ''), detail: String(n.detail ?? ''), icon: String(n.icon ?? '')
  }))
  const root = nodes.find(n => n.nodeId === spec.rootId) ?? nodes.find(n => !n.parentId) ?? nodes[0]
    ?? { nodeId: 'root', parentId: null, label: String(spec.title ?? 'Mapa mental'), detail: '' }
  const seen = new Set([root.nodeId])
  const branches: MindBranch[] = []
  function collect(parent: string): MindNode[] {
    return nodes.filter(n => n.parentId === parent && !seen.has(n.nodeId)).flatMap(n => {
      if (seen.has(n.nodeId)) return []
      seen.add(n.nodeId)
      return [n, ...collect(n.nodeId)]
    })
  }
  for (const n of nodes.filter(n => n.parentId === root.nodeId)) {
    if (seen.has(n.nodeId)) continue
    seen.add(n.nodeId); branches.push({ node: n, descendants: collect(n.nodeId) })
  }
  // Never silently lose old orphaned concepts or cycles.
  for (const n of nodes) {
    if (seen.has(n.nodeId)) continue
    seen.add(n.nodeId); branches.push({ node: n, descendants: collect(n.nodeId) })
  }
  return { title: String(spec.title ?? root.label), root, branches }
}

export function wrapText(text: string, limit: number): string[] {
  const lines: string[] = []; let line = ''
  for (const paragraph of text.split(/\n/)) {
    for (const word of paragraph.split(/\s+/).filter(Boolean)) {
      for (let i = 0; i < word.length; i += limit) {
        const part = word.slice(i, i + limit)
        if (line && line.length + part.length + 1 > limit) { lines.push(line); line = '' }
        line += (line ? ' ' : '') + part
      }
    }
    if (line) lines.push(line)
    line = ''
  }
  return lines
}
const escape = (text: string) => text.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]!))
const colors = ['#176c51', '#205fab', '#9a5010', '#76449d', '#ab365a', '#126c7b', '#685b15']
export function mindSvg(doc: MindDocument): { svg: string; height: number } {
  const text = (lines: string[], x: number, y: number, size = 25, weight = 400, fill = '#233448') =>
    `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}">${lines.map((l, i) => `<tspan x="${x}" dy="${i ? size * 1.4 : 0}">${escape(l)}</tspan>`).join('')}</text>`
  const rootTitle = wrapText(doc.root.label || doc.title, 30)
  const rootDetail = wrapText(doc.root.detail, 42)
  const rootHeight = 58 + rootTitle.length * 48 + rootDetail.length * 31
  const top = rootHeight + 120
  const bottoms = [top, top]
  const cards: string[] = [], paths: string[] = []
  doc.branches.forEach((branch, index) => {
    const side = index % 2, x = side ? 850 : 50, y = bottoms[side], color = colors[index % colors.length]
    const icon = branch.node.icon && /^\p{Extended_Pictographic}[\p{Extended_Pictographic}\uFE0F\u200D\p{Emoji_Modifier}]*$/u.test(branch.node.icon) ? branch.node.icon : ''
    const heading = wrapText(branch.node.label, icon ? 26 : 31)
    let cursor = y + 48
    let content = text(heading, x + (icon ? 100 : 30), cursor, 32, 700, color)
    if (icon) content += text([icon], x + 24, cursor + 5, 48)
    cursor += heading.length * 45 + 16
    const items = [branch.node.detail, ...branch.descendants.map(n => [n.label, n.detail].filter(Boolean).join(': '))].filter(Boolean)
    for (const item of items) {
      const lines = wrapText(item, 43)
      content += `<circle cx="${x + 25}" cy="${cursor - 8}" r="4" fill="${color}"/>` + text(lines, x + 42, cursor)
      cursor += lines.length * 35 + 18
    }
    const height = Math.max(160, cursor - y + 14)
    cards.push(`<g><rect x="${x}" y="${y}" width="700" height="${height}" rx="26" fill="white" stroke="${color}" stroke-width="3"/><rect x="${x}" y="${y + 24}" width="7" height="${height - 48}" rx="3" fill="${color}"/>${content}</g>`)
    const edgeX = side ? x : x + 700
    paths.push(`<path d="M800 ${rootHeight + 40} V${y + 54} Q800 ${y + 75} ${edgeX} ${y + 75}" fill="none" stroke="${color}" stroke-width="4"/>`)
    bottoms[side] += height + 36
  })
  const height = Math.max(1200, ...bottoms) + 40
  return { height, svg: `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="${height}" viewBox="0 0 1600 ${height}" role="img" aria-labelledby="map-title" font-family="Arial, sans-serif"><title id="map-title">${escape(doc.title)}</title><rect width="1600" height="${height}" fill="#fffdf5"/>${paths.join('')}<rect x="390" y="40" width="820" height="${rootHeight}" rx="40" fill="#edf5ff" stroke="#17385f" stroke-width="4"/>${text(rootTitle, 430, 100, 38, 700, '#17385f')}${text(rootDetail, 430, 100 + rootTitle.length * 48, 23)}${cards.join('')}</svg>` }
}
