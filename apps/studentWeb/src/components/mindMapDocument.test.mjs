import test from 'node:test'
import assert from 'node:assert/strict'
import { mindDocument, mindSvg, wrapText } from './mindMapDocument.ts'

test('legacy roots and details stay visible without topic rules', () => {
  for (const title of ['Continentes', 'Figuras de linguagem', 'Um conceito inédito']) {
    const spec = { title, rootId: 'r', nodes: [{ nodeId: 'r', parentId: null, label: title, detail: 'Introdução' }, { nodeId: 'a', parentId: 'r', label: 'Conceito', detail: 'Explicação com acentuação' }] }
    const doc = mindDocument(spec), { svg } = mindSvg(doc)
    assert.equal(doc.branches.length, 1)
    assert.ok(svg.includes('Explicação com acentuação'))
    assert.ok(svg.includes(title))
  }
})
test('orphaned nodes and cycles are not hidden', () => {
  const doc = mindDocument({ nodes: [{ nodeId: 'r', parentId: null }, { nodeId: 'a', parentId: 'b' }, { nodeId: 'b', parentId: 'a' }, { nodeId: 'c', parentId: 'missing' }] })
  assert.equal(doc.branches.flatMap(b => [b.node, ...b.descendants]).length, 3)
})
test('SVG escapes untrusted text rather than executing markup', () => {
  const { svg } = mindSvg(mindDocument({ title: '<script>alert(1)</script>' }))
  assert.ok(!svg.includes('<script>'))
  assert.ok(svg.includes('&lt;script&gt;'))
})
test('long text increases document height without truncating content', () => {
  const nodes = [{ nodeId: 'r', parentId: null, label: 'Tema' }, ...Array.from({ length: 9 }, (_, i) => ({ nodeId: String(i), parentId: 'r', label: 'Tópico ' + i, detail: ('Conteúdo completo com acentos. ').repeat(20) + 'FINAL' }))]
  const { svg, height } = mindSvg(mindDocument({ nodes }))
  assert.ok(height > 1200)
  assert.equal(svg.match(/FINAL/g).length, 9)
})
test('unbroken words wrap within available line budget', () => {
  assert.ok(wrapText('X'.repeat(180), 43).every(line => line.length <= 43))
})
test('semantic icons supplied by content are optional and never markup', () => {
  const nodes = [{ nodeId: 'r', parentId: null, label: 'Tema' }, { nodeId: 'a', parentId: 'r', label: 'Ideia', icon: '<img>' }]
  assert.ok(!mindSvg(mindDocument({ nodes })).svg.includes('<img>'))
  nodes[1].icon = '🌿'
  assert.ok(mindSvg(mindDocument({ nodes })).svg.includes('🌿'))
})
