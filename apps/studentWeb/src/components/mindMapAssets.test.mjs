import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import vm from 'node:vm'
import ts from 'typescript'

const source = readFileSync(new URL('./useMindMapAssets.ts', import.meta.url), 'utf8')
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText
const student = '11111111-1111-4111-8111-111111111111'
const id = '22222222-2222-4222-8222-222222222222'
const png = new Uint8Array([137,80,78,71,13,10,26,10,0])
function setup(fetcher, initial = { nodes: [{ nodeId: 'branch', imageTaskId: id }] }) {
  const module = { exports: {} }, timers = new Map(); let next = 0, watcher, unmount, spec = initial
  vm.runInNewContext(compiled, {
    exports: module.exports, module, AbortController, Uint8Array, btoa,
    fetch: fetcher,
    setTimeout: (fn, delay) => { const key = ++next; timers.set(key, { fn, delay }); return key },
    clearTimeout: key => timers.delete(key),
    require: () => ({ ref: value => ({ value }), watch: (_source, callback) => { watcher = callback }, onBeforeUnmount: callback => { unmount = callback } })
  })
  const assets = module.exports.useMindMapAssets(() => student, () => spec)
  return { assets, switch: value => { spec = value; watcher() }, unmount: () => unmount(), tick: async () => { const item = [...timers].find(([, t]) => t.delay === 2500); assert.ok(item); timers.delete(item[0]); await item[1].fn(); await new Promise(resolve => setImmediate(resolve)) } }
}
const ready = () => Response.json({ imageTaskId: id, studentId: student, status: 'READY', assetUrl: 'https://evil.invalid/asset' })
test('uses fixed owned asset path and embeds validated raster', async () => {
  const paths = []
  const { assets } = setup(async (path, options) => { paths.push(path); assert.equal(options.method, 'GET'); return path.endsWith('/asset') ? new Response(png, { headers: { 'content-type': 'image/png' } }) : ready() })
  await assets.refresh()
  assert.equal(assets.states.value.branch, 'READY')
  assert.match(assets.images.value.branch, /^data:image\/png;base64,/)
  assert.deepEqual(paths, [`/api/students/${student}/image-tasks/${id}`, `/api/students/${student}/image-tasks/${id}/asset`])
})
test('bad raster cannot become READY and is terminal', async () => {
  let calls = 0
  const gate = setup(async path => { calls++; return path.endsWith('/asset') ? new Response('<svg/>', { headers: { 'content-type': 'image/png' } }) : ready() })
  await gate.assets.refresh()
  assert.equal(gate.assets.states.value.branch, 'ERROR'); assert.equal(calls, 2)
  assert.equal(Object.keys(gate.assets.images.value).length, 0)
})
test('rejects another student without fetching asset', async () => {
  let calls = 0
  const { assets } = setup(async () => { calls++; return Response.json({ imageTaskId: id, studentId: 'other', status: 'READY' }) })
  await assets.refresh(); assert.equal(calls, 1); assert.equal(assets.states.value.branch, 'ERROR')
})
test('scope change discards late response', async () => {
  let finish
  const gate = setup(() => new Promise(resolve => { finish = resolve }))
  const pending = gate.assets.refresh(); gate.switch({ nodes: [] }); finish(ready()); await pending
  assert.equal(Object.keys(gate.assets.images.value).length, 0)
  assert.equal(Object.keys(gate.assets.states.value).length, 0)
})
test('invalid IDs never fetch and excessive nodes are limited', async () => {
  let calls = 0
  const nodes = Array.from({ length: 10 }, (_, i) => ({ nodeId: String(i), imageTaskId: id }))
  nodes.push({ nodeId: 'bad', imageTaskId: '../secret' })
  const { assets } = setup(async () => { calls++; return Response.json({ imageTaskId: id, studentId: student, status: 'ERROR' }) }, { nodes })
  await assets.refresh(); assert.equal(calls, 8); assert.equal(assets.states.value['8'], 'LIMIT'); assert.equal(assets.states.value.bad, undefined)
})
test('oversized content-length is refused before reading', async () => {
  const { assets } = setup(async path => path.endsWith('/asset') ? new Response(png, { headers: { 'content-type': 'image/png', 'content-length': String(9 * 1024 * 1024) } }) : ready())
  await assets.refresh(); assert.equal(assets.states.value.branch, 'ERROR'); assert.equal(assets.images.value.branch, undefined)
})
test('network failures retry only three times', async () => {
  let calls = 0
  const gate = setup(async () => { calls++; throw new TypeError('offline') })
  await gate.assets.refresh(); await gate.tick(); await gate.tick()
  assert.equal(calls, 3); assert.equal(gate.assets.states.value.branch, 'ERROR')
})
