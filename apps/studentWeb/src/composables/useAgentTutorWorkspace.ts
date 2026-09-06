import {
  computed,
  ref,
  type Ref
} from 'vue'

import type {
  AgentConversationContract,
  AgentThreadContract
} from '../contracts/agentTutorContract'
import type {
  VisualTaskContract
} from '../contracts/visualTaskContract'
import type { ImageGenerationTaskContract } from '../contracts/imageGenerationContract'
import type {
  StudentContract
} from '../contracts/studentContract'
import {
  AgentTutorApiService
} from '../services/agentTutorApiService'
import {
  VisualTaskApiService
} from '../services/visualTaskApiService'
import { ImageGenerationApiService } from '../services/imageGenerationApiService'

interface TutorContext {
  contextId: string | null
  subjectId: string | null
  unitId: string | null
  title: string
}

interface Options {
  selectedStudent: Ref<StudentContract | null>
  showError: (error: unknown) => void
  setSuccess: (message: string) => void
  refreshGuide?: () => Promise<void>
  refreshWorkspaceSummary?: () => Promise<void>
}

export function useAgentTutorWorkspace(
  options: Options
) {
  const api = new AgentTutorApiService()
  const visualApi = new VisualTaskApiService()
  const imageApi = new ImageGenerationApiService()

  const threads = ref<AgentThreadContract[]>([])
  const conversation = ref<AgentConversationContract | null>(null)
  const visualTasks = ref<Record<string, VisualTaskContract>>({})
  const imageTasks = ref<Record<string, ImageGenerationTaskContract>>({})
  const busy = ref(false)
  let pollTimer: number | null = null
  let lastActiveRunId: string | null = null
  let stateVersion = 0
  let currentContext: TutorContext | null = null
  let contextLoading: Promise<void> | null = null
  let contextKey = ''

  const selectedThread = computed(
    () => conversation.value?.thread ?? null
  )

  const activeRun = computed(
    () => conversation.value?.activeRun ?? null
  )

  async function loadThreads(context?: TutorContext) {
    if (!options.selectedStudent.value || !context?.contextId || !context.subjectId || !context.unitId) {
      threads.value = []
      return
    }
    const version = stateVersion
    const studentId = options.selectedStudent.value.studentId
    const loaded = await api.listThreads(
      studentId,
      {
        studentLearningContextId: context.contextId,
        studentSubjectId: context.subjectId,
        studentLearningUnitId: context.unitId
      }
    )
    if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return
    threads.value = loaded
  }

  function ensureContextThread(context: TutorContext): Promise<void> {
    const key = JSON.stringify([options.selectedStudent.value?.studentId, context])
    if (contextLoading && key === contextKey) return contextLoading
    currentContext = { ...context }
    contextKey = key
    const version = ++stateVersion
    stopPolling()
    conversation.value = null
    const pending = prepareContextThread(context, version).finally(() => {
      if (contextLoading === pending) contextLoading = null
    })
    contextLoading = pending
    return pending
  }

  async function prepareContextThread(
    context: TutorContext,
    version: number
  ) {
    if (
      !options.selectedStudent.value
      || !context.contextId
      || !context.subjectId
      || !context.unitId
    ) {
      reset()
      return
    }

    await loadThreads(context)
    if (version !== stateVersion) return

    const matching = threads.value.find(
      thread =>
        thread.studentLearningContextId
          === context.contextId
        && thread.studentSubjectId
          === context.subjectId
        && thread.studentLearningUnitId
          === context.unitId
    )

    if (matching) {
      await selectThread(matching)
      return
    }

    const created = await api.createThread(
      options.selectedStudent.value.studentId,
      {
        title: context.title,
        studentLearningContextId: context.contextId,
        studentSubjectId: context.subjectId,
        studentLearningUnitId: context.unitId
      }
    )
    if (version !== stateVersion) return

    threads.value = [
      created,
      ...threads.value
    ]
    await selectThread(created)
  }

  async function selectThread(
    thread: AgentThreadContract
  ) {
    if (!options.selectedStudent.value) {
      return
    }


    stopPolling()

    const version = ++stateVersion
    const studentId = options.selectedStudent.value.studentId
    const loaded = await api.getConversation(
      studentId,
      thread.agentThreadId
    )
    if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return
    conversation.value = loaded

    await hydrateVisualTasks()
    await hydrateImageTasks()

    if (version !== stateVersion) return
    lastActiveRunId = (
      conversation.value.activeRun?.agentRunId
      ?? null
    )

    if (conversation.value.activeRun || hasPendingConversationImages()) {
      startPolling()
    }
  }

  async function sendMessage(
    request: {
      content: string
      requestedTextModelId: string | null
      thinkingMode: 'AUTO' | 'ON' | 'OFF'
      materialIds: string[]
    }
  ): Promise<{ accepted: boolean; error?: string }> {
    if (busy.value) return { accepted: false, error: 'Aguarde o envio atual terminar.' }
    busy.value = true
    let accepted = false
    try {
      const context = currentContext
      if (!options.selectedStudent.value || !context?.contextId || !context.subjectId || !context.unitId) {
        return { accepted: false, error: 'Escolha a matéria e a lição antes de enviar. Sua pergunta foi mantida.' }
      }
      if (contextLoading) await contextLoading
      if (!conversation.value) await ensureContextThread(context)
      if (!conversation.value || currentContext?.contextId !== context.contextId || currentContext?.subjectId !== context.subjectId || currentContext?.unitId !== context.unitId) {
        return { accepted: false, error: 'A lição mudou durante o envio. Confira a seleção e tente novamente.' }
      }
      const run = await api.sendMessage(
        options.selectedStudent.value.studentId,
        conversation.value.thread.agentThreadId,
        request
      )
      accepted = true
      lastActiveRunId = run.agentRunId
      startPolling()
      await refreshConversation()
      return { accepted: true }
    } catch {
      // The composer displays this failure next to the preserved draft.
      return { accepted, error: accepted
        ? 'Sua pergunta foi recebida, mas não foi possível atualizar a resposta. Aguarde a reconexão.'
        : 'Não foi possível enviar. Sua pergunta foi mantida; tente novamente.' }
    } finally {
      busy.value = false
    }
  }

  async function refreshConversation() {
    if (
      !options.selectedStudent.value
      || !conversation.value
    ) {
      return
    }

    const studentId = options.selectedStudent.value.studentId
    const threadId = conversation.value.thread.agentThreadId
    const trackedRunId = lastActiveRunId
    const version = stateVersion

    const loaded = await api.getConversation(
      studentId,
      threadId
    )
    if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId || conversation.value?.thread.agentThreadId !== threadId) return
    conversation.value = loaded

    await hydrateVisualTasks()
    await hydrateImageTasks()

    if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return
    if (conversation.value.activeRun) {
      lastActiveRunId = conversation.value.activeRun.agentRunId
      return
    }

    if (trackedRunId) {
      const terminalRun = await api.getRun(
        studentId,
        threadId,
        trackedRunId
      )
      if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return

      if (
        terminalRun.status === 'QUEUED'
        || terminalRun.status === 'RUNNING'
      ) {
        lastActiveRunId = terminalRun.agentRunId
        return
      }

      lastActiveRunId = null
      await Promise.all([
        loadThreads({
          contextId: conversation.value.thread.studentLearningContextId,
          subjectId: conversation.value.thread.studentSubjectId,
          unitId: conversation.value.thread.studentLearningUnitId,
          title: conversation.value.thread.title
        }),
        options.refreshGuide?.() ?? Promise.resolve(),
        options.refreshWorkspaceSummary?.() ?? Promise.resolve()
      ])
    }


    if (hasPendingConversationImages()) {
      return
    }
    stopPolling()
  }

  async function retryLastRun() {
    if (
      !options.selectedStudent.value
      || !conversation.value
      || !conversation.value.lastRun
      || (
        conversation.value.lastRun.status !== 'FAILED'
        && conversation.value.lastRun.status !== 'CANCELLED'
      )
    ) {
      return
    }

    busy.value = true

    try {
      const run = await api.retryRun(
        options.selectedStudent.value.studentId,
        conversation.value.thread.agentThreadId,
        conversation.value.lastRun.agentRunId
      )
      lastActiveRunId = run.agentRunId
      await refreshConversation()
      startPolling()
    } catch (error) {
      options.showError(error)
    } finally {
      busy.value = false
    }
  }

  async function archiveCurrentThread() {
    if (
      !options.selectedStudent.value
      || !conversation.value
      || busy.value
    ) {
      return
    }

    const studentId = options.selectedStudent.value.studentId
    const threadId = conversation.value.thread.agentThreadId
    busy.value = true
    try {
      await api.archiveThread(
        studentId,
        threadId
      )
      if (options.selectedStudent.value?.studentId !== studentId) return
      threads.value = threads.value.filter(thread => thread.agentThreadId !== threadId)
      if (conversation.value?.thread.agentThreadId === threadId) {
        stateVersion++
        stopPolling()
        lastActiveRunId = null
        conversation.value = null
        visualTasks.value = {}
        imageTasks.value = {}
      }
      options.setSuccess('Conversa arquivada.')
    } catch (error) {
      options.showError(error)
    } finally {
      busy.value = false
    }
  }

  async function hydrateVisualTasks() {
    const version = stateVersion
    const studentId = options.selectedStudent.value?.studentId
    if (
      !options.selectedStudent.value
      || !conversation.value
    ) {
      return
    }

    const ids = Array.from(
      new Set(
        conversation.value.messages.flatMap(
          message => message.visualTaskIds
        )
      )
    )

    const missing = ids.filter(
      id => !visualTasks.value[id]
    )

    if (missing.length === 0) {
      return
    }

    const loaded = await Promise.all(
      missing.map(
        id => visualApi.get(
          options.selectedStudent.value!.studentId,
          id
        )
      )
    )

    const next = {
      ...visualTasks.value
    }
    if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return

    loaded.forEach(task => {
      next[task.visualTaskId] = task
    })

    visualTasks.value = next
  }

  async function hydrateImageTasks() {
    if (!options.selectedStudent.value || !conversation.value) return
    const version = stateVersion
    const studentId = options.selectedStudent.value.studentId
    const ids = Array.from(new Set(conversation.value.messages.flatMap(message => message.imageTaskIds)))
    const missing = ids.filter(id => !imageTasks.value[id])
    if (missing.length > 0) {
      const loaded = await Promise.all(missing.map(id => imageApi.get(options.selectedStudent.value!.studentId, id)))
      if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return
      const next = { ...imageTasks.value }
      loaded.forEach(task => { next[task.imageTaskId] = task })
      imageTasks.value = next
    }
    const activeIds = ids.filter(id => {
      const status = imageTasks.value[id]?.status
      return status === "QUEUED" || status === "PREPARING" || status === "GENERATING" || status === "LABELING"
    })
    if (activeIds.length > 0) {
      const loaded = await Promise.all(activeIds.map(id => imageApi.get(options.selectedStudent.value!.studentId, id)))
      if (version !== stateVersion || options.selectedStudent.value?.studentId !== studentId) return
      const next = { ...imageTasks.value }
      loaded.forEach(task => { next[task.imageTaskId] = task })
      imageTasks.value = next
    }
  }

  function hasPendingConversationImages() {
    return conversation.value?.messages.some(message => message.imageTaskIds.some(id =>
      ["QUEUED", "PREPARING", "GENERATING", "LABELING"].includes(imageTasks.value[id]?.status)
    )) ?? false
  }

  function startPolling() {
    if (pollTimer !== null) {
      return
    }

    pollTimer = window.setInterval(
      async () => {
        try {
          await refreshConversation()
        } catch (error) {

    stopPolling()
          options.showError(error)
        }
      },
      1200
    )
  }

  function stopPolling() {
    if (pollTimer === null) {
      return
    }

    window.clearInterval(pollTimer)
    pollTimer = null
  }

  function reset() {

    currentContext = null
    contextLoading = null
    contextKey = ''
    stateVersion++
    stopPolling()
    threads.value = []
    conversation.value = null
    visualTasks.value = {}
    imageTasks.value = {}
    busy.value = false
    lastActiveRunId = null
  }

  return {
    threads,
    conversation,
    selectedThread,
    activeRun,
    visualTasks,
    imageTasks,
    busy,
    loadThreads,
    ensureContextThread,
    selectThread,
    sendMessage,
    refreshConversation,
    retryLastRun,
    archiveCurrentThread,
    reset
  }
}
