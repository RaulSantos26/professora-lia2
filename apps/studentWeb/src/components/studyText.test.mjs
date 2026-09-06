import test from 'node:test'
import assert from 'node:assert/strict'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import StudyText from './studyText.ts'

const render = text => renderToString(createSSRApp({ render: () => h(StudyText, { text }) }))
test('teaching text renders headings, emphasis and semantic lists', async () => {
  const html = await render('# Erosão\n**Água** transporta o solo.\n- Chuva\n- Rios\n\n3. Observar\n4. Comparar')
  assert.match(html, /<h4>Erosão<\/h4>/)
  assert.match(html, /<strong>Água<\/strong>/)
  assert.match(html, /<ul><li>Chuva<\/li><li>Rios<\/li><\/ul>/)
  assert.match(html, /<ol start="3">/)
})
test('HTML and unsafe links stay inert text', async () => {
  const html = await render('<img src=x onerror=alert(1)>\n[link](javascript:alert(1))')
  assert.ok(!html.includes('<img'))
  assert.ok(!html.includes('<a '))
  assert.match(html, /&lt;img/)
})
test('code preserves markup and incomplete fences do not lose content', async () => {
  const html = await render('```html\n<strong>exemplo</strong>\n**literal**')
  assert.match(html, /<pre><code>&lt;strong&gt;exemplo&lt;\/strong&gt;\n\*\*literal\*\*<\/code><\/pre>/)
})
test('long explanations remain complete', async () => {
  const text = 'Uma explicação completa. '.repeat(3000) + 'FIM DA LIÇÃO'
  assert.ok((await render(text)).includes('FIM DA LIÇÃO'))
})
