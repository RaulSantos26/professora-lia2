import { computed, ref, type Ref } from 'vue'

import type { AiExecutionMode, ThinkingMode } from '../contracts/aiExecutionPreferenceContract'

import type { DocumentStructureContract } from '../contracts/documentStructureContract'
import type { MaterialContract } from '../contracts/materialContract'
import type {
  MaterialProcessingJobContract
} from '../contracts/materialProcessingContract'
import type { RagQueryResponseContract } from '../contracts/ragContract'
import type { StudentContract } from '../contracts/studentContract'
import type { StudentLearningUnitContract } from '../contracts/studentLearningUnitContract'
import type { StudentSubjectContract } from '../contracts/studentSubjectContract'
import {
  MaterialApiService,
  type MaterialBatchUploadRequest
} from '../services/materialApiService'
import {
  RagApiService
} from '../services/ragApiService'
import { StudentContentApiService } from '../services/studentContentApiService'

interface MaterialWorkspaceOptions {
  selectedStudent: Ref<StudentContract | null>
  refreshGuide: () => Promise<void>
  refreshWorkspaceSummary: () => Promise<void>
  showError: (error: unknown) => void
  setSuccess: (message: string) => void
  setError: (message: string) => void
}

export function useMaterialWorkspace(
  options: MaterialWorkspaceOptions
) {
  const materialApiService = new MaterialApiService()
  const studentContentApiService = new StudentContentApiService()
  const ragApiService = new RagApiService()

  const materials = ref<MaterialContract[]>([])
  const selectedMaterial = ref<MaterialContract | null>(null)
  const selectedMaterialStructure =
    ref<DocumentStructureContract | null>(null)

  const materialSubjects = ref<StudentSubjectContract[]>([])
  const materialUnits = ref<StudentLearningUnitContract[]>([])
  const selectedMaterialContextId = ref<string | null>(null)
  const selectedMaterialSubjectId = ref<string | null>(null)
  const selectedMaterialUnitId = ref<string | null>(null)

  const materialBusy = ref(false)
  const materialFormVersion = ref(0)

  const uploadProgress = ref<number | null>(null)
  const processingJobs = ref<MaterialProcessingJobContract[]>([])
  const ragResponse = ref<RagQueryResponseContract | null>(null)
  const ragBusy = ref(false)

  let pollingTimer: number | null = null

  const hasActiveProcessing = computed(
    () => processingJobs.value.some(
      job => job.status === 'QUEUED' || job.status === 'RUNNING'
    )
  )

  async function refreshMaterials() {
    if (!options.selectedStudent.value) {
      materials.value = []
      return
    }

    const items = await materialApiService.listMaterials(
      options.selectedStudent.value.studentId
    )

    materials.value = items

    if (selectedMaterial.value) {
      const updated = items.find(
        item =>
          item.materialId
          === selectedMaterial.value?.materialId
      )

      selectedMaterial.value = updated ?? null
    }
  }

  async function refreshProcessingJobs() {
    if (!options.selectedStudent.value) {
      processingJobs.value = []
      stopPolling()
      return
    }

    const jobs = await materialApiService.listProcessingJobs(
      options.selectedStudent.value.studentId,
      false
    )

    processingJobs.value = jobs.slice(0, 12)

    if (hasActiveProcessing.value) {
      startPolling()
    } else {
      stopPolling()
    }
  }

  function resetMaterialWorkspace() {
    stopPolling()

    materials.value = []
    selectedMaterial.value = null
    selectedMaterialStructure.value = null
    materialSubjects.value = []
    materialUnits.value = []
    selectedMaterialContextId.value = null
    selectedMaterialSubjectId.value = null
    selectedMaterialUnitId.value = null
    processingJobs.value = []
    uploadProgress.value = null
    ragResponse.value = null
  }

  function clearSelectionOutsideScope() {
    if (!selectedMaterial.value) {
      return
    }

    const isInScope = (
      !selectedMaterialUnitId.value
      || selectedMaterial.value.studentLearningUnitId
        === selectedMaterialUnitId.value
    ) && (
      !selectedMaterialSubjectId.value
      || selectedMaterial.value.studentSubjectId
        === selectedMaterialSubjectId.value
    ) && (
      !selectedMaterialContextId.value
      || selectedMaterial.value.studentLearningContextId
        === selectedMaterialContextId.value
    )

    if (!isInScope) {
      selectedMaterial.value = null
      selectedMaterialStructure.value = null
      ragResponse.value = null
    }
  }

  async function selectMaterialContext(contextId: string) {
    selectedMaterialContextId.value = contextId || null
    selectedMaterialSubjectId.value = null
    selectedMaterialUnitId.value = null
    materialSubjects.value = []
    materialUnits.value = []
    clearSelectionOutsideScope()

    if (!contextId) {
      return
    }

    materialSubjects.value =
      await studentContentApiService.listSubjects(contextId)
  }

  async function selectMaterialSubject(subjectId: string) {
    selectedMaterialSubjectId.value = subjectId || null
    selectedMaterialUnitId.value = null
    materialUnits.value = []
    clearSelectionOutsideScope()

    if (!subjectId) {
      return
    }

    materialUnits.value =
      await studentContentApiService.listLearningUnits(subjectId)
  }

  function selectMaterialUnit(unitId: string) {
    selectedMaterialUnitId.value = unitId || null
    clearSelectionOutsideScope()
  }

  async function uploadMaterials(
    request: MaterialBatchUploadRequest
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    materialBusy.value = true
    uploadProgress.value = 0
    options.setError('')

    try {
      const batch = await materialApiService.uploadBatchAsync(
        options.selectedStudent.value.studentId,
        request,
        percent => {
          uploadProgress.value = percent
        }
      )

      await refreshMaterials()
      await options.refreshGuide()
      await options.refreshWorkspaceSummary()

      const newJobs = batch.items
        .map(item => item.job)
        .filter(
          (job): job is MaterialProcessingJobContract =>
            job !== null
        )

      if (newJobs.length > 0) {
        processingJobs.value = [
          ...newJobs,
          ...processingJobs.value.filter(
            existing =>
              !newJobs.some(
                job =>
                  job.materialProcessingJobId
                  === existing.materialProcessingJobId
              )
          )
        ].slice(0, 12)

        startPolling()
      }

      materialFormVersion.value += 1

      options.setSuccess(
        `${batch.successCount}/${batch.totalFiles} arquivo(s) `
        + (
          newJobs.length > 0
            ? 'recebido(s). A análise continua em segundo plano.'
            : 'armazenado(s).'
        )
      )

      if (batch.errorCount > 0) {
        const failures = batch.items
          .filter(item => !item.success)
          .map(
            item =>
              `${item.fileName}: `
              + `${item.errorCode ?? 'ERROR'}`
              + (
                item.errorMessage
                  ? ` — ${item.errorMessage}`
                  : ''
              )
          )

        options.setError(
          `${batch.errorCount} arquivo(s) tiveram problema:\n`
          + failures.join('\n')
        )
      }
    } catch (error) {
      options.showError(error)
    } finally {
      materialBusy.value = false

      window.setTimeout(
        () => {
          uploadProgress.value = null
        },
        700
      )
    }
  }

  async function selectMaterial(
    material: MaterialContract
  ) {
    selectedMaterial.value = material
    selectedMaterialStructure.value = null
    ragResponse.value = null

    if (
      material.status === 'UPLOADED'
      || material.status === 'ERROR'
    ) {
      return
    }

    try {
      selectedMaterialStructure.value =
        await materialApiService.getStructure(
          material.materialId
        )
    } catch {
      // PROCESSING can legitimately exist before Document is created.
    }
  }

  async function analyzeMaterial(
    material: MaterialContract
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    options.setError('')

    try {
      const job = await materialApiService.analyzeAsync(
        options.selectedStudent.value.studentId,
        material.materialId
      )

      addJob(job)
      startPolling()

      await refreshMaterials()

      options.setSuccess(
        `Análise de "${material.title}" colocada na fila.`
      )
    } catch (error) {
      options.showError(error)
    }
  }

  async function indexMaterialRag(
    material: MaterialContract
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    options.setError('')

    try {
      const job = await materialApiService.indexRag(
        options.selectedStudent.value.studentId,
        material.materialId
      )

      addJob(job)
      startPolling()

      options.setSuccess(
        `Indexação RAG de "${material.title}" colocada na fila.`
      )
    } catch (error) {
      options.showError(error)
    }
  }

  async function updateMaterialAiPreference(
    material: MaterialContract,
    preference: {
      mode: AiExecutionMode
      fixedModelId: string | null
      textModelId: string | null
      visionModelId: string | null
      embeddingModelId: string | null
      thinkingMode: ThinkingMode
    }
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    try {
      const updated = await materialApiService.setAiPreference(
        options.selectedStudent.value.studentId,
        material.materialId,
        preference
      )

      await refreshMaterials()

      if (
        selectedMaterial.value?.materialId
        === updated.materialId
      ) {
        selectedMaterial.value = updated
      }

      const label = {
        AUTO: 'Automático',
        FIXED: 'Modelo fixo',
        CUSTOM: 'Personalizado'
      }[preference.mode]

      options.setSuccess(
        `Configuração de IA salva: ${label}.`
      )
    } catch (error) {
      options.showError(error)
    }
  }

  async function toggleMaterialStudy(
    material: MaterialContract,
    enabled: boolean
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    try {
      const updated = await materialApiService.setStudyEnabled(
        options.selectedStudent.value.studentId,
        material.materialId,
        enabled
      )

      await refreshMaterials()

      if (
        selectedMaterial.value?.materialId
        === updated.materialId
      ) {
        selectedMaterial.value = updated
      }

      options.setSuccess(
        enabled
          ? 'Material voltou a ser usado no estudo.'
          : 'Material removido do uso no estudo.'
      )
    } catch (error) {
      options.showError(error)
    }
  }

  async function deleteMaterial(
    material: MaterialContract
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    if (isMaterialProcessing(material.materialId)) {
      options.setError(
        'Aguarde o processamento terminar antes de excluir este material.'
      )
      return
    }

    materialBusy.value = true

    try {
      await materialApiService.deleteMaterial(
        options.selectedStudent.value.studentId,
        material.materialId
      )

      if (
        selectedMaterial.value?.materialId
        === material.materialId
      ) {
        selectedMaterial.value = null
        selectedMaterialStructure.value = null
      }

      processingJobs.value = processingJobs.value.filter(
        job => job.materialId !== material.materialId
      )

      await refreshMaterials()
      await options.refreshGuide()
      await options.refreshWorkspaceSummary()

      options.setSuccess(
        `Material "${material.title}" excluído definitivamente.`
      )
      options.setError('')
    } catch (error) {
      options.showError(error)
    } finally {
      materialBusy.value = false
    }
  }

  async function queryRag(
    query: string,
    requestedModelId: string | null,
    selectedOnly: boolean,
    thinkingMode: ThinkingMode
  ) {
    if (!options.selectedStudent.value) {
      return
    }

    ragBusy.value = true
    ragResponse.value = null
    options.setError('')

    try {
      ragResponse.value = await ragApiService.query(
        options.selectedStudent.value.studentId,
        {
          query,
          topK: 6,
          requestedModelId,
          thinkingMode,
          studentLearningContextId: selectedMaterialContextId.value,
          studentSubjectId: selectedMaterialSubjectId.value,
          studentLearningUnitId: selectedMaterialUnitId.value,
          materialIds: (
            selectedOnly && selectedMaterial.value
              ? [selectedMaterial.value.materialId]
              : []
          )
        }
      )
    } catch (error) {
      options.showError(error)
    } finally {
      ragBusy.value = false
    }
  }

  function isMaterialProcessing(materialId: string): boolean {
    return processingJobs.value.some(
      job =>
        job.materialId === materialId
        && (
          job.status === 'QUEUED'
          || job.status === 'RUNNING'
        )
    )
  }

  function addJob(job: MaterialProcessingJobContract) {
    processingJobs.value = [
      job,
      ...processingJobs.value.filter(
        item =>
          item.materialProcessingJobId
          !== job.materialProcessingJobId
      )
    ].slice(0, 12)
  }

  function startPolling() {
    if (pollingTimer !== null) {
      return
    }

    pollingTimer = window.setInterval(
      async () => {
        await pollProcessing()
      },
      1000
    )
  }

  function stopPolling() {
    if (pollingTimer === null) {
      return
    }

    window.clearInterval(pollingTimer)
    pollingTimer = null
  }

  async function pollProcessing() {
    if (!options.selectedStudent.value) {
      stopPolling()
      return
    }

    try {
      const previousActiveIds = new Set(
        processingJobs.value
          .filter(
            job =>
              job.status === 'QUEUED'
              || job.status === 'RUNNING'
          )
          .map(job => job.materialProcessingJobId)
      )

      await refreshProcessingJobs()

      const currentActiveIds = new Set(
        processingJobs.value
          .filter(
            job =>
              job.status === 'QUEUED'
              || job.status === 'RUNNING'
          )
          .map(job => job.materialProcessingJobId)
      )

      const finishedSomething = [...previousActiveIds].some(
        id => !currentActiveIds.has(id)
      )

      if (finishedSomething) {
        await refreshMaterials()
        await options.refreshGuide()
        await options.refreshWorkspaceSummary()

        if (selectedMaterial.value) {
          const current = materials.value.find(
            item =>
              item.materialId
              === selectedMaterial.value?.materialId
          )

          if (current) {
            await selectMaterial(current)
          }
        }
      }
    } catch (error) {
      stopPolling()
      options.showError(error)
    }
  }

  return {
    materials,
    selectedMaterial,
    selectedMaterialStructure,
    materialSubjects,
    materialUnits,
    selectedMaterialContextId,
    selectedMaterialSubjectId,
    selectedMaterialUnitId,
    materialBusy,
    materialFormVersion,
    uploadProgress,
    processingJobs,
    hasActiveProcessing,
    ragResponse,
    ragBusy,
    refreshMaterials,
    refreshProcessingJobs,
    resetMaterialWorkspace,
    selectMaterialContext,
    selectMaterialSubject,
    selectMaterialUnit,
    uploadMaterials,
    selectMaterial,
    analyzeMaterial,
    indexMaterialRag,
    updateMaterialAiPreference,
    toggleMaterialStudy,
    deleteMaterial,
    queryRag,
    isMaterialProcessing
  }
}
