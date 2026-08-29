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
import type {
  StudentContract
} from '../contracts/studentContract'
import {
  AgentTutorApiService
} from '../services/agentTutorApiService'
import {
  VisualTaskApiService
} from '../services/visualTaskApiService'

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

  const threads = ref<AgentThreadContract[]>([])
  const conversation = ref<AgentConversationContract | null>(null)
  const visualTasks = ref<Record<string, VisualTaskContract>>({})
  const busy = ref(false)
  let pollTimer: number | null = null
  let lastActiveRunId: string | null = null

  const selectedThread = computed(
    () => conversation.value?.thread ?? null
  )

  const activeRun = computed(
    () => conversation.value?.activeRun ?? null
  )

  async function loadThreads() {
    if (!options.selectedStudent.value) {
      threads.value = []
      return
    }

    threads.value = await api.listThreads(
      options.selectedStudent.value.studentId
    )
  }

  async function ensureContextThread(
    context: TutorContext
  ) {
    if (!options.selectedStudent.value) {
      reset()
      return
    }

    await loadThreads()

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

    conversation.value = await api.getConversation(
      options.selectedStudent.value.studentId,
      thread.agentThreadId
    )

    await hydrateVisualTasks()

    lastActiveRunId = (
      conversation.value.activeRun?.agentRunId
      ?? null
    )

    if (conversation.value.activeRun) {
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
  ) {
    if (
      !options.selectedStudent.value
      || !conversation.value
    ) {
      return
    }

    busy.value = true

    try {
      const run = await api.sendMessage(
        options.selectedStudent.value.studentId,
        conversation.value.thread.agentThreadId,
        request
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

    conversation.value = await api.getConversation(
      studentId,
      threadId
    )

    await hydrateVisualTasks()

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

      if (
        terminalRun.status === 'QUEUED'
        || terminalRun.status === 'RUNNING'
      ) {
        lastActiveRunId = terminalRun.agentRunId
        return
      }

      lastActiveRunId = null
      await Promise.all([
        loadThreads(),
        options.refreshGuide?.() ?? Promise.resolve(),
        options.refreshWorkspaceSummary?.() ?? Promise.resolve()
      ])
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
    ) {
      return
    }

    try {
      await api.archiveThread(
        options.selectedStudent.value.studentId,
        conversation.value.thread.agentThreadId
      )
      conversation.value = null
      visualTasks.value = {}
      await loadThreads()
      options.setSuccess('Conversa arquivada.')
    } catch (error) {
      options.showError(error)
    }
  }

  async function hydrateVisualTasks() {
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

    loaded.forEach(task => {
      next[task.visualTaskId] = task
    })

    visualTasks.value = next
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
    stopPolling()
    threads.value = []
    conversation.value = null
    visualTasks.value = {}
    busy.value = false
    lastActiveRunId = null
  }

  return {
    threads,
    conversation,
    selectedThread,
    activeRun,
    visualTasks,
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
