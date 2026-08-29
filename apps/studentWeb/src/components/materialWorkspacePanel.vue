<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import MaterialAiPreferenceEditor from './materialAiPreferenceEditor.vue'
import MaterialUploadCard from './materialUploadCard.vue'

import type {
  AiExecutionMode,
  ThinkingMode
} from '../contracts/aiExecutionPreferenceContract'
import type { AiModelRegistryContract } from '../contracts/aiModelContract'
import type { DocumentStructureContract } from '../contracts/documentStructureContract'
import type { MaterialContract } from '../contracts/materialContract'
import type { MaterialProcessingJobContract } from '../contracts/materialProcessingContract'
import type { RagQueryResponseContract } from '../contracts/ragContract'
import type { StudentLearningContextViewContract } from '../contracts/studentLearningContextContract'
import type { StudentLearningUnitContract } from '../contracts/studentLearningUnitContract'
import type { StudentSubjectContract } from '../contracts/studentSubjectContract'
import type {
  MaterialBatchUploadRequest
} from '../services/materialApiService'

const props = defineProps<{
  contexts: StudentLearningContextViewContract[]
  subjects: StudentSubjectContract[]
  units: StudentLearningUnitContract[]
  materials: MaterialContract[]
  selectedMaterial: MaterialContract | null
  structure: DocumentStructureContract | null
  modelRegistry: AiModelRegistryContract | null
  busy: boolean
  uploadProgress: number | null
  processingJobs: MaterialProcessingJobContract[]
  ragResponse: RagQueryResponseContract | null
  ragBusy: boolean
  isMaterialProcessing: (materialId: string) => boolean
}>()

const emit = defineEmits<{
  selectContext: [contextId: string]
  selectSubject: [subjectId: string]
  uploadBatch: [request: MaterialBatchUploadRequest]
  selectMaterial: [material: MaterialContract]
  analyze: [material: MaterialContract]
  indexRag: [material: MaterialContract]
  updateAiPreference: [
    material: MaterialContract,
    preference: {
      mode: AiExecutionMode
      fixedModelId: string | null
      textModelId: string | null
      visionModelId: string | null
      embeddingModelId: string | null
      thinkingMode: ThinkingMode
    }
  ]
  toggleStudy: [material: MaterialContract, enabled: boolean]
  delete: [material: MaterialContract]
  refreshModels: []
  queryRag: [
    query: string,
    modelId: string | null,
    selectedOnly: boolean,
    thinkingMode: ThinkingMode
  ]
}>()

const ragQuery = ref('')
const ragModelId = ref('')
const ragSelectedOnly = ref(false)
const ragThinkingMode = ref<ThinkingMode>('AUTO')

const activeJobs = computed(
  () => props.processingJobs.filter(
    job =>
      job.status === 'QUEUED'
      || job.status === 'RUNNING'
  )
)

const recentFinishedJobs = computed(
  () => props.processingJobs.filter(
    job =>
      job.status !== 'QUEUED'
      && job.status !== 'RUNNING'
  ).slice(0, 4)
)

const textModels = computed(
  () => (props.modelRegistry?.models ?? []).filter(model => {
    const capabilities = new Set(
      model.capabilities.map(
        capability => capability.toUpperCase()
      )
    )

    if (!model.available || !capabilities.has('TEXT')) {
      return false
    }

    if (ragThinkingMode.value === 'ON') {
      return capabilities.has('THINKING')
    }

    return true
  })
)

watch(
  () => props.selectedMaterial?.materialId,
  () => {
    ragSelectedOnly.value = Boolean(props.selectedMaterial)
  },
  { immediate: true }
)

function submitRag() {
  const query = ragQuery.value.trim()

  if (query.length < 3) {
    return
  }

  emit(
    'queryRag',
    query,
    ragModelId.value || null,
    ragSelectedOnly.value,
    ragThinkingMode.value
  )
}

function confirmDelete(material: MaterialContract) {
  if (props.isMaterialProcessing(material.materialId)) {
    return
  }

  const confirmed = window.confirm(
    `Excluir definitivamente "${material.title}"?\n\n`
    + 'O arquivo original e toda a estrutura derivada serão removidos.'
  )

  if (confirmed) {
    emit('delete', material)
  }
}

function configurationLabel(material: MaterialContract): string {
  const thinking = `THINK ${material.thinkingMode}`

  if (material.aiMode === 'FIXED') {
    return (
      `FIXO · ${material.fixedModelId ?? 'não definido'}`
      + ` · ${thinking}`
    )
  }

  if (material.aiMode === 'CUSTOM') {
    return `PERSONALIZADO · ${thinking}`
  }

  return `AUTO · ${thinking}`
}

function stageLabel(stage: string): string {
  const labels: Record<string, string> = {
    QUEUED: 'Na fila',
    STARTING: 'Iniciando',
    PREPARING: 'Preparando documento',
    DOCUMENT_EXTRACTED: 'Estrutura criada',
    OCR: 'Lendo texto da imagem',
    VISION: 'Interpretando imagens / Vision',
    EMBEDDING: 'Gerando embeddings',
    FINALIZING: 'Finalizando',
    READY: 'Concluído',
    FAILED: 'Falha'
  }

  return labels[stage] ?? stage
}

function jobStatusClass(job: MaterialProcessingJobContract): string {
  if (job.status === 'FAILED') {
    return 'FAILED'
  }

  if (job.status === 'COMPLETED_WITH_WARNINGS') {
    return 'WARNING'
  }

  if (job.status === 'COMPLETED') {
    return 'DONE'
  }

  return 'ACTIVE'
}
</script>

<template>
  <section class="workspaceFeaturePanel materialWorkspace">
    <div class="workspaceFeatureHeader">
      <div>
        <p class="eyebrow">MULTIMODAL CONTENT & RAG</p>
        <h2>Materiais de estudo</h2>
        <p>
          Upload assíncrono, leitura multimodal, Vision, embeddings e
          evidências para RAG.
        </p>
      </div>

      <span class="countBadge">{{ materials.length }}</span>
    </div>

    <section
      v-if="uploadProgress !== null"
      class="materialOperationProgress uploadProgressPanel"
    >
      <div class="operationProgressHeader">
        <span class="liaSpinner" aria-hidden="true" />

        <div>
          <strong>Enviando arquivos...</strong>
          <small>
            Não feche esta página durante o envio.
          </small>
        </div>

        <b>{{ uploadProgress }}%</b>
      </div>

      <div class="operationProgressTrack">
        <div
          class="operationProgressValue"
          :style="{ width: `${uploadProgress}%` }"
        />
      </div>
    </section>

    <section
      v-if="activeJobs.length > 0"
      class="materialProcessingQueue"
    >
      <div class="sectionHeader">
        <div>
          <p class="eyebrow">PROCESSAMENTO EM ANDAMENTO</p>
          <h3>A Lia está trabalhando nos seus materiais</h3>
          <p>
            Você pode acompanhar cada etapa sem precisar adivinhar
            se o processamento terminou.
          </p>
        </div>

        <span class="processingLiveBadge">
          <span class="liaSpinner smallSpinner" />
          {{ activeJobs.length }} ativo(s)
        </span>
      </div>

      <article
        v-for="job in activeJobs"
        :key="job.materialProcessingJobId"
        class="processingJobCard"
      >
        <div class="processingJobHeader">
          <div>
            <strong>
              {{ job.materialTitle ?? job.materialId }}
            </strong>
            <small>
              {{ stageLabel(job.stage) }} · {{ job.message }}
            </small>
          </div>

          <b>{{ job.progressPercent }}%</b>
        </div>

        <div class="operationProgressTrack">
          <div
            class="operationProgressValue"
            :style="{ width: `${job.progressPercent}%` }"
          />
        </div>

        <div class="processingModelDetails">
          <span v-if="job.effectiveVisionModelId">
            Vision: {{ job.effectiveVisionModelId }}
          </span>

          <span v-if="job.effectiveEmbeddingModelId">
            Embedding: {{ job.effectiveEmbeddingModelId }}
          </span>

          <span v-if="job.fallbackReason">
            Fallback: {{ job.fallbackReason }}
          </span>
        </div>
      </article>
    </section>

    <details
      v-if="recentFinishedJobs.length > 0"
      class="recentProcessingDetails"
    >
      <summary>
        Últimos processamentos
      </summary>

      <div class="recentProcessingList">
        <article
          v-for="job in recentFinishedJobs"
          :key="job.materialProcessingJobId"
          class="recentProcessingItem"
          :data-status="jobStatusClass(job)"
        >
          <span>
            <strong>{{ job.materialTitle ?? job.materialId }}</strong>
            <small>
              {{ job.status }} · {{ job.message }}
            </small>
          </span>

          <b>{{ job.progressPercent }}%</b>
        </article>
      </div>
    </details>

    <div class="workspacePanelGrid materialWorkspaceGrid">
      <MaterialUploadCard
        :contexts="contexts"
        :subjects="subjects"
        :units="units"
        :model-registry="modelRegistry"
        :busy="busy"
        @select-context="emit('selectContext', $event)"
        @select-subject="emit('selectSubject', $event)"
        @upload-batch="emit('uploadBatch', $event)"
        @refresh-models="emit('refreshModels')"
      />

      <div class="workspaceListCard materialList">
        <p
          v-if="materials.length === 0"
          class="emptyState"
        >
          Nenhum material enviado para este aluno.
        </p>

        <article
          v-for="material in materials"
          :key="material.materialId"
          class="materialLibraryItem"
          :data-selected="
            material.materialId
            === selectedMaterial?.materialId
          "
        >
          <button
            type="button"
            class="materialLibrarySelect"
            @click="emit('selectMaterial', material)"
          >
            <span>
              <strong>{{ material.title }}</strong>

              <small>
                {{ material.materialType }}
                · {{ material.status }}
                <template v-if="material.sourceSequence">
                  · página {{ material.sourceSequence }}
                </template>
                · IA {{ configurationLabel(material) }}
              </small>
            </span>

            <span class="materialLibraryBadges">
              <span
                v-if="isMaterialProcessing(material.materialId)"
                class="processingMaterialBadge"
              >
                PROCESSANDO
              </span>

              <span
                v-if="!material.studyEnabled"
                class="studyDisabledBadge"
              >
                FORA DO ESTUDO
              </span>

              <span
                :data-status="
                  material.status === 'READY'
                    ? 'ONLINE'
                    : material.status === 'ERROR'
                      ? 'OFFLINE'
                      : 'NEUTRAL'
                "
              >
                {{ material.status }}
              </span>
            </span>
          </button>

          <div
            v-if="material.lastProcessingErrorMessage"
            class="materialErrorSummary"
          >
            <strong>{{ material.lastProcessingErrorCode }}</strong>
            <span>{{ material.lastProcessingErrorMessage }}</span>
          </div>

          <div class="materialItemActions">
            <button
              type="button"
              class="secondaryButton"
              @click="emit('selectMaterial', material)"
            >
              Detalhes
            </button>

            <button
              type="button"
              class="secondaryButton"
              :disabled="isMaterialProcessing(material.materialId)"
              @click="emit('analyze', material)"
            >
              {{
                material.status === 'UPLOADED'
                  || material.status === 'ERROR'
                  ? 'Analisar'
                  : 'Reanalisar'
              }}
            </button>

            <button
              v-if="material.status === 'READY'"
              type="button"
              class="secondaryButton"
              :disabled="isMaterialProcessing(material.materialId)"
              @click="emit('indexRag', material)"
            >
              Indexar RAG
            </button>

            <button
              type="button"
              class="secondaryButton"
              @click="
                emit(
                  'toggleStudy',
                  material,
                  !material.studyEnabled
                )
              "
            >
              {{
                material.studyEnabled
                  ? 'Não usar no estudo'
                  : 'Usar no estudo'
              }}
            </button>

            <a
              class="secondaryButton materialActionLink"
              :href="`/api/materials/${material.materialId}/file`"
              target="_blank"
              rel="noopener"
            >
              Abrir
            </a>

            <button
              type="button"
              class="dangerButton"
              :disabled="isMaterialProcessing(material.materialId)"
              @click="confirmDelete(material)"
            >
              Excluir
            </button>
          </div>
        </article>
      </div>
    </div>

    <MaterialAiPreferenceEditor
      v-if="selectedMaterial"
      :material="selectedMaterial"
      :model-registry="modelRegistry"
      @update="
        (material, preference) =>
          emit('updateAiPreference', material, preference)
      "
    />

    <section
      v-if="
        selectedMaterial
        && selectedMaterial.status === 'UPLOADED'
      "
      class="storedOnlyNotice"
    >
      <strong>Arquivo armazenado sem análise.</strong>
      <p>
        Clique em <b>Analisar</b> quando quiser iniciar o pipeline.
      </p>
    </section>

    <section
      v-if="structure"
      class="documentStructure"
    >
      <div class="sectionHeader">
        <div>
          <p class="eyebrow">DOCUMENT INTELLIGENCE</p>
          <h3>Documento processado</h3>
        </div>

        <div class="documentMetrics">
          <span>{{ structure.pageCount }} pág.</span>
          <span>{{ structure.evidenceCount }} evidências</span>
          <span>{{ structure.chunkCount }} chunks</span>
          <span>
            {{ structure.embeddedChunkCount }} indexados
          </span>
          <span v-if="structure.visualPendingCount">
            {{ structure.visualPendingCount }} Vision pendente
          </span>
          <span>{{ structure.extractionStatus }}</span>
        </div>
      </div>

      <div class="documentPages">
        <details
          v-for="page in structure.pages"
          :key="page.documentPageId"
          class="documentPage"
        >
          <summary>
            <span>Página {{ page.pageNumber }}</span>
            <span>{{ page.status }}</span>
          </summary>

          <div class="documentBlocks">
            <article
              v-for="block in page.blocks"
              :key="block.documentBlockId"
              class="documentBlock"
            >
              <div class="documentBlockHeader">
                <strong>{{ block.blockType }}</strong>
                <span>
                  {{ block.processingStatus }}
                  <template v-if="block.visionModelId">
                    · {{ block.visionModelId }}
                    · Thinking:
                    {{
                      block.visionThinkingEnabled
                        ? 'ON'
                        : 'OFF'
                    }}
                  </template>
                  <template v-if="block.orientationDegrees">
                    · rotação {{ block.orientationDegrees }}°
                  </template>
                </span>
              </div>

              <p v-if="block.textContent">
                {{ block.textContent.slice(0, 900) }}
                <template v-if="block.textContent.length > 900">…</template>
              </p>

              <p
                v-else-if="
                  block.processingStatus === 'PENDING_VISION'
                "
                class="visualPendingMessage"
              >
                Conteúdo visual preservado. Aguardando Vision.
              </p>
            </article>
          </div>
        </details>
      </div>
    </section>

    <section class="ragWorkspace">
      <div class="sectionHeader">
        <div>
          <p class="eyebrow">RAG COM EVIDÊNCIAS</p>
          <h3>Perguntar aos materiais</h3>
          <p>
            A resposta deve usar somente trechos indexados dos materiais
            deste aluno habilitados para estudo.
          </p>
        </div>
      </div>

      <form
        class="ragQueryForm"
        @submit.prevent="submitRag"
      >
        <textarea
          v-model="ragQuery"
          rows="3"
          placeholder="Ex.: Quais são os tipos de tecido conjuntivo mostrados na apostila?"
        />

        <select v-model="ragModelId">
          <option value="">Modelo de texto: Automático</option>

          <option
            v-for="model in textModels"
            :key="model.modelId"
            :value="model.modelId"
          >
            {{ model.displayName }}
          </option>
        </select>

        <select v-model="ragThinkingMode">
          <option value="AUTO">
            Raciocínio: Automático
          </option>
          <option value="ON">
            Raciocínio: Sempre usar
          </option>
          <option value="OFF">
            Raciocínio: Desativado
          </option>
        </select>

        <label class="checkboxField compactCheckbox">
          <input
            v-model="ragSelectedOnly"
            type="checkbox"
            :disabled="!selectedMaterial"
          />
          <span>
            <strong>Somente material selecionado</strong>
          </span>
        </label>

        <button
          type="submit"
          :disabled="ragBusy || ragQuery.trim().length < 3"
        >
          <span
            v-if="ragBusy"
            class="liaSpinner smallSpinner"
          />
          {{ ragBusy ? 'Consultando...' : 'Perguntar à Lia' }}
        </button>
      </form>

      <article
        v-if="ragResponse"
        class="ragAnswerCard"
      >
        <div class="ragAnswerHeader">
          <strong>Resposta baseada nos materiais</strong>
          <small>
            Texto: {{ ragResponse.textModelId }}
            · Embedding: {{ ragResponse.embeddingModelId }}
            · Thinking:
            {{ ragResponse.thinkingEnabled ? 'ATIVADO' : 'DESATIVADO' }}
          </small>
        </div>

        <p class="ragAnswerText">
          {{ ragResponse.answer }}
        </p>

        <details open>
          <summary>
            Evidências recuperadas ({{ ragResponse.evidence.length }})
          </summary>

          <div class="ragEvidenceList">
            <article
              v-for="(evidence, index) in ragResponse.evidence"
              :key="`${evidence.materialId}-${index}`"
              class="ragEvidenceItem"
            >
              <strong>
                [{{ index + 1 }}] {{ evidence.materialTitle }}
              </strong>
              <small>
                {{ evidence.locator }}
                · score {{ evidence.score.toFixed(3) }}
              </small>
              <p>{{ evidence.excerpt }}</p>
            </article>
          </div>
        </details>
      </article>
    </section>
  </section>
</template>
