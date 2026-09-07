export interface MindNode { nodeId: string; parentId: string | null; label: string; detail: string; icon?: string; imageTaskId?: string }
export interface MindBranch { node: MindNode; descendants: MindNode[] }
export interface MindDocument { title: string; root: MindNode; branches: MindBranch[]; relationship?: string }

// Compatibility adapter: stored node contracts remain the source of truth.
export function mindDocument(spec: Record<string, unknown>): MindDocument {
  const source = Array.isArray(spec.nodes) ? spec.nodes : []
  const nodes: MindNode[] = source.filter(n => n && typeof n === 'object').map((n: any, i) => ({
    nodeId: String(n.nodeId ?? i), parentId: n.parentId == null ? null : String(n.parentId),
    label: String(n.label ?? ''), detail: String(n.detail ?? ''), icon: String(n.icon ?? ''), imageTaskId: typeof n.imageTaskId === 'string' ? n.imageTaskId : undefined
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
  return { title: String(spec.title ?? root.label), root, branches, relationship: spec.relationship === 'SEQUENCE' ? 'SEQUENCE' : 'PARALLEL' }
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
export function mindSvg(doc: MindDocument, images: Record<string, string> = {}, states: Record<string, string> = {}): { svg: string; height: number } {
  const text = (lines: string[], x: number, y: number, size = 25, weight = 400, fill = '#233448') =>
    `<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}">${lines.map((l, i) => `<tspan x="${x}" dy="${i ? size * 1.4 : 0}">${escape(l)}</tspan>`).join('')}</text>`
  const sequence = doc.relationship === 'SEQUENCE'
  const art = (node: MindNode, x: number, y: number, w: number, h: number, color: string, number: string) => {
    const uri = images[node.nodeId]
    // Only raster bytes loaded through our scoped API may enter the SVG/export.
    if (uri && /^data:image\/(png|jpeg);base64,[A-Za-z0-9+/=]+$/.test(uri) && uri.length <= 12000000)
      return `<image x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet" href="${uri}"><title>${escape(node.label)}</title></image>`
    const icon = node.icon && /^\p{Extended_Pictographic}[\p{Extended_Pictographic}\uFE0F\u200D\p{Emoji_Modifier}]*$/u.test(node.icon) ? node.icon : number
    const status = node.imageTaskId ? (['ERROR','CANCELLED'].includes(states[node.nodeId]) ? 'Figura indisponível' : 'Preparando figura') : 'Ideia principal'
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="22" fill="${color}" fill-opacity=".055"/>` +
      text([icon], x + w / 2 - 24, y + h / 2 + 10, 52, 700, color) + text([status], x + 18, y + h - 18, 17, 400, color)
  }
  const rootTitle = wrapText(doc.root.label || doc.title, 41)
  const rootDetail = wrapText(doc.root.detail, 64)
  const rootHeight = Math.max(248, 62 + rootTitle.length * 52 + rootDetail.length * 32)
  const top = rootHeight + 118
  const bottoms = [top, top]
  const cards: string[] = [], paths: string[] = []
  doc.branches.forEach((branch, index) => {
    const side = sequence ? 0 : index % 2, x = sequence ? 120 : side ? 850 : 50, y = bottoms[side], color = colors[index % colors.length]
    const width = sequence ? 1360 : 700
    const heading = wrapText(branch.node.label, sequence ? 64 : 30)
    let cursor = y + 49
    let content = `<circle cx="${x + 36}" cy="${y + 38}" r="20" fill="${color}"/>` + text([String(index + 1)], x + 29, y + 46, 22, 700, 'white')
    content += text(heading, x + 70, cursor, 31, 700, color)
    cursor += heading.length * 44 + 14
    const pictureY = cursor - 16
    content += art(branch.node, x + 24, pictureY, 218, 164, color, String(index + 1))
    const intro = wrapText(branch.node.detail, sequence ? 67 : 26)
    content += text(intro, x + 262, cursor + 9, 24)
    cursor = Math.max(pictureY + 184, cursor + intro.length * 34 + 14)
    const items = branch.descendants.map(n => [n.label, n.detail].filter(Boolean).join(': ')).filter(Boolean)
    for (const item of items) {
      const lines = wrapText(item, sequence ? 87 : 43)
      content += `<circle cx="${x + 25}" cy="${cursor - 8}" r="4" fill="${color}"/>` + text(lines, x + 42, cursor)
      cursor += lines.length * 35 + 18
    }
    const height = Math.max(160, cursor - y + 14)
    cards.push(`<g><rect x="${x + 4}" y="${y + 6}" width="${width}" height="${height}" rx="26" fill="${color}" fill-opacity=".08"/><rect x="${x}" y="${y}" width="${width}" height="${height}" rx="26" fill="white" stroke="${color}" stroke-width="3"/>${content}</g>`)
    const edgeX = side ? x : x + 700
    paths.push(sequence
      ? `<path d="M70 ${index ? y - 36 : rootHeight + 40} V${y + 38} H${x}" fill="none" stroke="${color}" stroke-width="4"/>`
      : `<path d="M800 ${rootHeight + 40} V${y + 17} Q800 ${y + 38} ${edgeX} ${y + 38}" fill="none" stroke="${color}" stroke-width="4"/>`)
    bottoms[side] += height + 36
  })
  const height = Math.max(1200, ...bottoms) + 40
  return { height, svg: `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="${height}" viewBox="0 0 1600 ${height}" role="img" aria-labelledby="map-title" font-family="Arial, sans-serif"><title id="map-title">${escape(doc.title)}</title><rect width="1600" height="${height}" fill="#fffdf5"/>${paths.join('')}<rect x="50" y="40" width="1500" height="${rootHeight}" rx="40" fill="#edf5ff" stroke="#17385f" stroke-width="3"/>${art(doc.root, 82, 62, 310, rootHeight - 44, '#17385f', '✦')}${text(rootTitle, 430, 102, 38, 700, '#17385f')}${text(rootDetail, 430, 112 + rootTitle.length * 52, 23)}${cards.join('')}</svg>` }
}
