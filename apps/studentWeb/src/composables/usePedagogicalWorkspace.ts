import { computed, ref, type Ref } from 'vue'

import type {
  LearningAttemptContract,
  PedagogicalArtifactContract,
  PedagogicalArtifactType
} from '../contracts/pedagogicalContract'
import type { StudentContract } from '../contracts/studentContract'
import {
  PedagogicalApiService
} from '../services/pedagogicalApiService'

interface Options {
  selectedStudent: Ref<StudentContract | null>
  showError: (error: unknown) => void
  setSuccess: (message: string) => void
  refreshLearningStates: () => Promise<void>
  refreshGuide: () => Promise<void>
  refreshWorkspaceSummary: () => Promise<void>
}

export function usePedagogicalWorkspace(options: Options) {
  const api = new PedagogicalApiService()

  const artifacts = ref<PedagogicalArtifactContract[]>([])
  const selectedArtifact = ref<PedagogicalArtifactContract | null>(null)
  const latestAttempt = ref<LearningAttemptContract | null>(null)
  const busy = ref(false)

  let timer: number | null = null
  let pollingScope: {
    studentLearningContextId: string
    studentSubjectId: string
    studentLearningUnitId: string
  } | null = null

  const activeArtifacts = computed(
    () => artifacts.value.filter(
      item =>
        item.status === 'QUEUED'
        || item.status === 'RUNNING'
    )
  )

  async function refreshArtifacts(scope?: { studentLearningContextId: string | null; studentSubjectId: string | null; studentLearningUnitId: string | null }) {
    if (!options.selectedStudent.value || !scope?.studentLearningContextId || !scope.studentSubjectId || !scope.studentLearningUnitId) {
      artifacts.value = []
      selectedArtifact.value = null
      stopPolling()
      return
    }
    if (!options.selectedStudent.value) {
      artifacts.value = []
      selectedArtifact.value = null
      stopPolling()
      return
    }

    pollingScope = {
      studentLearningContextId: scope.studentLearningContextId,
      studentSubjectId: scope.studentSubjectId,
      studentLearningUnitId: scope.studentLearningUnitId
    }
    artifacts.value = await api.listArtifacts(
      options.selectedStudent.value.studentId,
      pollingScope
    )

    if (selectedArtifact.value) {
      selectedArtifact.value = (
        artifacts.value.find(
          item =>
            item.pedagogicalArtifactId
            === selectedArtifact.value?.pedagogicalArtifactId
        )
        ?? null
      )
    }

    if (activeArtifacts.value.length > 0) {
      startPolling()
    } else {
      stopPolling()
    }
  }

  async function createArtifact(
    request: {
      artifactType: PedagogicalArtifactType
      title: string | null
      instruction: string | null
      materialIds: string[]
      difficulty: 'AUTO' | 'EASY' | 'MEDIUM' | 'HARD'
      questionCount: number
      requestedTextModelId: string | null
      thinkingMode: 'AUTO' | 'ON' | 'OFF'
    }
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    busy.value = true
    latestAttempt.value = null

    try {
      const artifact = await api.createArtifact(
        options.selectedStudent.value.studentId,
        request
      )

      artifacts.value = [
        artifact,
        ...artifacts.value
      ]
      selectedArtifact.value = artifact

      if (
        artifact.studentLearningContextId
        && artifact.studentSubjectId
        && artifact.studentLearningUnitId
      ) {
        pollingScope = {
          studentLearningContextId: artifact.studentLearningContextId,
          studentSubjectId: artifact.studentSubjectId,
          studentLearningUnitId: artifact.studentLearningUnitId
        }
      }
      startPolling()

      options.setSuccess(
        `${label(request.artifactType)} colocado na fila.`
      )
    } catch (error) {
      options.showError(error)
    } finally {
      busy.value = false
    }
  }

  function selectArtifact(artifact: PedagogicalArtifactContract) {
    selectedArtifact.value = artifact
    latestAttempt.value = null
  }

  async function submitAttempt(
    artifactId: string,
    answers: Record<string, string>
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    busy.value = true

    try {
      latestAttempt.value = await api.submitAttempt(
        options.selectedStudent.value.studentId,
        artifactId,
        answers
      )

      await Promise.all([
        options.refreshLearningStates(),
        options.refreshGuide(),
        options.refreshWorkspaceSummary()
      ])

      options.setSuccess(
        `Atividade corrigida: ${latestAttempt.value.scorePercent}% de acerto.`
      )
    } catch (error) {
      options.showError(error)
    } finally {
      busy.value = false
    }
  }

  async function archiveArtifact(artifactId: string) {
    if (!options.selectedStudent.value) {
      return
    }

    try {
      await api.archiveArtifact(
        options.selectedStudent.value.studentId,
        artifactId
      )

      if (
        selectedArtifact.value?.pedagogicalArtifactId
        === artifactId
      ) {
        selectedArtifact.value = null
      }

      options.setSuccess('Conteúdo removido do histórico de estudo.')
    } catch (error) {
      options.showError(error)
    }
  }

  function resetPedagogicalWorkspace() {
    pollingScope = null
    stopPolling()
    artifacts.value = []
    selectedArtifact.value = null
    latestAttempt.value = null
  }

  function startPolling() {
    if (timer !== null) {
      return
    }

    timer = window.setInterval(
      async () => {
        try {
          if (!pollingScope) {
            stopPolling()
            return
          }
          await refreshArtifacts(pollingScope)
        } catch (error) {
          stopPolling()
          options.showError(error)
        }
      },
      1200
    )
  }

  function stopPolling() {
    if (timer === null) {
      return
    }

    window.clearInterval(timer)
    timer = null
  }

  function label(type: PedagogicalArtifactType): string {
    return {
      TEACH: 'Aula',
      EXPLAIN: 'Explicação',
      SUMMARY: 'Resumo',
      MIND_MAP: 'Mapa mental',
      FLASHCARDS: 'Flashcards',
      EXERCISES: 'Exercícios',
      QUIZ: 'Quiz'
    }[type]
  }

  return {
    artifacts,
    selectedArtifact,
    latestAttempt,
    activeArtifacts,
    busy,
    refreshArtifacts,
    createArtifact,
    selectArtifact,
    submitAttempt,
    archiveArtifact,
    resetPedagogicalWorkspace
  }
}
