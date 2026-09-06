import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import vm from 'node:vm'
import ts from 'typescript'
import { ref } from 'vue'

const require = createRequire(import.meta.url)
const source = readFileSync(new URL('./useAgentTutorWorkspace.ts', import.meta.url), 'utf8')
function setup(archiveThread, extraApi = {}, imageApi = {}) {
  let pollingStarts = 0
  const api = { archiveThread, ...extraApi }
  const module = { exports: {} }
  const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText
  vm.runInNewContext(compiled, {
    exports: module.exports, module,
    window: { setInterval: () => { pollingStarts++; return 1 }, clearInterval: () => {} },
    require: name => name === 'vue' ? require('vue') : {
      AgentTutorApiService: class { constructor() { return api } },
      VisualTaskApiService: class {}, ImageGenerationApiService: class { constructor() { return imageApi } }
    }
  })
  const errors = []
  const workspace = module.exports.useAgentTutorWorkspace({ selectedStudent: ref({ studentId: 'student' }), showError: error => errors.push(error), setSuccess: () => {} })
  workspace.threads.value = [{ agentThreadId: 'first' }, { agentThreadId: 'second' }]
  workspace.conversation.value = { thread: { agentThreadId: 'first' } }
  return { workspace, errors, pollingStarts: () => pollingStarts }
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
const context = { contextId: 'context', subjectId: 'subject', unitId: 'unit', title: 'Gate' }
test('opening a finished chat resumes polling for its pending illustration', async () => {
  const thread = { agentThreadId: 'first' }
  const { workspace, pollingStarts } = setup(async () => {}, {
    getConversation: async () => ({ thread, activeRun: null, messages: [{ visualTaskIds: [], imageTaskIds: ['image'] }] })
  }, { get: async () => ({ imageTaskId: 'image', status: 'GENERATING' }) })
  await workspace.selectThread(thread)
  assert.equal(pollingStarts(), 1)
})

test('pending images cached from another conversation do not start polling', async () => {
  const thread = { agentThreadId: 'second' }
  const { workspace, pollingStarts } = setup(async () => {}, {
    getConversation: async () => ({ thread, activeRun: null, messages: [] })
  })
  workspace.imageTasks.value = { old: { imageTaskId: 'old', status: 'GENERATING' } }
  await workspace.selectThread(thread)
  assert.equal(pollingStarts(), 0)
})
const request = { content: 'O que são recursos naturais?', requestedTextModelId: null, thinkingMode: 'AUTO', materialIds: [] }
function sendingSetup(failSend = false) {
  let created = 0
  let sent = 0
  const thread = { agentThreadId: 'created', studentLearningContextId: 'context', studentSubjectId: 'subject', studentLearningUnitId: 'unit' }
  const result = setup(async () => {}, {
    listThreads: async () => [],
    createThread: async () => { created++; return thread },
    getConversation: async () => ({ thread, messages: [], activeRun: null }),
    sendMessage: async () => { sent++; if (failSend) throw new Error('offline'); return { agentRunId: 'run' } },
    getRun: async () => ({ status: 'READY' })
  })
  return { ...result, counts: () => ({ created, sent }) }
}
test('send after archive recreates the scoped conversation and reaches API', async () => {
  const { workspace, counts } = sendingSetup()
  await workspace.ensureContextThread(context)
  await workspace.archiveCurrentThread()
  assert.equal(workspace.conversation.value, null)
  const result = await workspace.sendMessage(request)
  assert.equal(result.accepted, true)
  assert.deepEqual(counts(), { created: 2, sent: 1 })
})
test('send failure explicitly returns nonacceptance to preserve the draft', async () => {
  const { workspace } = sendingSetup(true)
  await workspace.ensureContextThread(context)
  const result = await workspace.sendMessage(request)
  assert.equal(result.accepted, false)
  assert.ok(result.error.includes('mantida'))
  assert.equal(workspace.busy.value, false)
})
test('send without scope gives an explicit error instead of silent return', async () => {
  const { workspace } = setup(async () => {})
  const result = await workspace.sendMessage(request)
  assert.equal(result.accepted, false)
  assert.ok(result.error.includes('matéria'))
})
