import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import vm from 'node:vm'
import ts from 'typescript'
import { ref } from 'vue'

const require = createRequire(import.meta.url)
const source = readFileSync(new URL('./useAgentTutorWorkspace.ts', import.meta.url), 'utf8')
function setup(archiveThread, extraApi = {}) {
  const api = { archiveThread, ...extraApi }
  const module = { exports: {} }
  const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText
  vm.runInNewContext(compiled, {
    exports: module.exports, module,
    require: name => name === 'vue' ? require('vue') : {
      AgentTutorApiService: class { constructor() { return api } },
      VisualTaskApiService: class {}, ImageGenerationApiService: class {}
    }
  })
  const errors = []
  const workspace = module.exports.useAgentTutorWorkspace({ selectedStudent: ref({ studentId: 'student' }), showError: error => errors.push(error), setSuccess: () => {} })
  workspace.threads.value = [{ agentThreadId: 'first' }, { agentThreadId: 'second' }]
  workspace.conversation.value = { thread: { agentThreadId: 'first' } }
  return { workspace, errors }
}
test('archiving removes only the selected conversation immediately', async () => {
  const { workspace } = setup(async (student, thread) => {
    assert.equal(student, 'student'); assert.equal(thread, 'first')
  })
  await workspace.archiveCurrentThread()
  assert.equal(workspace.conversation.value, null)
  assert.equal(workspace.threads.value.length, 1)
  assert.equal(workspace.threads.value[0].agentThreadId, 'second')
})
test('failed archive preserves history and conversation', async () => {
  const { workspace, errors } = setup(async () => { throw new Error('offline') })
  await workspace.archiveCurrentThread()
  assert.equal(workspace.threads.value.length, 2)
  assert.equal(workspace.conversation.value.thread.agentThreadId, 'first')
  assert.equal(errors.length, 1)
  assert.equal(workspace.busy.value, false)
})
test('switching conversations during archive does not clear the new selection', async () => {
  let finish
  const { workspace } = setup(() => new Promise(resolve => { finish = resolve }))
  const pending = workspace.archiveCurrentThread()
  workspace.conversation.value = { thread: { agentThreadId: 'second' } }
  finish()
  await pending
  assert.equal(workspace.conversation.value.thread.agentThreadId, 'second')
})
test('late polling response cannot restore an archived conversation', async () => {
  let finish
  const { workspace } = setup(async () => {}, {
    getConversation: () => new Promise(resolve => { finish = resolve })
  })
  const polling = workspace.refreshConversation()
  await workspace.archiveCurrentThread()
  finish({ thread: { agentThreadId: 'first' }, messages: [] })
  await polling
  assert.equal(workspace.conversation.value, null)
  assert.equal(workspace.threads.value.length, 1)
})
test('late polling response cannot restore a reset scope', async () => {
  let finish
  const { workspace } = setup(async () => {}, {
    getConversation: () => new Promise(resolve => { finish = resolve })
  })
  const polling = workspace.refreshConversation()
  workspace.reset()
  finish({ thread: { agentThreadId: 'first' }, messages: [] })
  await polling
  assert.equal(workspace.conversation.value, null)
  assert.equal(workspace.threads.value.length, 0)
})
