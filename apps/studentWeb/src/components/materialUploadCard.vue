<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  ref,
  watch
} from 'vue'

import type {
  AiExecutionMode,
  ThinkingMode
} from '../contracts/aiExecutionPreferenceContract'
import type { AiModelRegistryContract } from '../contracts/aiModelContract'
import type {
  StudentLearningContextViewContract
} from '../contracts/studentLearningContextContract'
import type {
  StudentLearningUnitContract
} from '../contracts/studentLearningUnitContract'
import type {
  StudentSubjectContract
} from '../contracts/studentSubjectContract'
import type {
  MaterialBatchUploadRequest
} from '../services/materialApiService'

const props = defineProps<{
  contexts: StudentLearningContextViewContract[]
  subjects: StudentSubjectContract[]
  units: StudentLearningUnitContract[]
  selectedContextId: string | null
  selectedSubjectId: string | null
  selectedUnitId: string | null
  modelRegistry: AiModelRegistryContract | null
  busy: boolean
}>()

const emit = defineEmits<{
  selectContext: [contextId: string]
  selectSubject: [subjectId: string]
  selectUnit: [unitId: string]
  uploadBatch: [request: MaterialBatchUploadRequest]
  refreshModels: []
}>()

interface SelectedUpload {
  file: File
  previewUrl: string | null
  source: 'CAMERA' | 'PICKER'
}

const cameraInput = ref<HTMLInputElement | null>(null)
const pickerInput = ref<HTMLInputElement | null>(null)

const selectedUploads = ref<SelectedUpload[]>([])
const replaceCameraIndex = ref<number | null>(null)
const title = ref('')
const description = ref('')
const contextId = ref(props.selectedContextId ?? '')
const subjectId = ref(props.selectedSubjectId ?? '')
const unitId = ref(props.selectedUnitId ?? '')
const analysisRequested = ref(true)
const studyEnabled = ref(true)

const aiMode = ref<AiExecutionMode>('AUTO')
const fixedModelId = ref('')
const textModelId = ref('')
const visionModelId = ref('')
const embeddingModelId = ref('')
const thinkingMode = ref<ThinkingMode>('AUTO')

const isMultiFile = computed(
  () => selectedUploads.value.length > 1
)

const textModels = computed(
  () => availableModels('TEXT')
)

const visionModels = computed(
  () => availableModels('VISION')
)

const embeddingModels = computed(
  () => availableModels('EMBEDDINGS')
)

const fixedModel = computed(
  () => (props.modelRegistry?.models ?? []).find(
    model => model.modelId === fixedModelId.value
  ) ?? null
)

const requiredCapabilities = computed(() => {
  if (!analysisRequested.value) {
    return new Set<string>()
  }

  const required = new Set<string>(['TEXT', 'EMBEDDINGS'])

  if (
    selectedUploads.value.some(
      item => needsVision(item.file)
    )
  ) {
    required.add('VISION')
  }

  if (thinkingMode.value === 'ON') {
    required.add('THINKING')
  }

  return required
})

const fixedMissingCapabilities = computed(() => {
  if (
    aiMode.value !== 'FIXED'
    || !fixedModel.value
  ) {
    return []
  }

  const capabilities = new Set(
    fixedModel.value.capabilities.map(
      capability => capability.toUpperCase()
    )
  )

  return [...requiredCapabilities.value].filter(
    capability => !capabilities.has(capability)
  )
})

const canSubmit = computed(() => {
  if (props.busy || selectedUploads.value.length === 0) {
    return false
  }

  if (
    selectedUploads.value.length === 1
    && title.value.trim().length < 2
  ) {
    return false
  }

  if (
    aiMode.value === 'FIXED'
    && (
      !fixedModelId.value
      || fixedMissingCapabilities.value.length > 0
    )
  ) {
    return false
  }

  return true
})

watch(
  () => props.selectedContextId,
  value => {
    if ((value ?? '') !== contextId.value) {
      contextId.value = value ?? ''
    }
  }
)

watch(
  () => props.selectedSubjectId,
  value => {
    if ((value ?? '') !== subjectId.value) {
      subjectId.value = value ?? ''
    }
  }
)

watch(
  () => props.selectedUnitId,
  value => {
    if ((value ?? '') !== unitId.value) {
      unitId.value = value ?? ''
    }
  }
)

watch(contextId, () => {
  subjectId.value = ''
  unitId.value = ''
  emit('selectContext', contextId.value)
})

watch(subjectId, () => {
  unitId.value = ''
  emit('selectSubject', subjectId.value)
})

watch(unitId, () => {
  emit('selectUnit', unitId.value)
})

watch(aiMode, mode => {
  if (mode === 'AUTO') {
    fixedModelId.value = ''
    textModelId.value = ''
    visionModelId.value = ''
    embeddingModelId.value = ''
  }
})

function openCamera(replaceIndex: number | null = null) {
  replaceCameraIndex.value = replaceIndex
  cameraInput.value?.click()
}

function openPicker() {
  pickerInput.value?.click()
}

function cameraCaptured(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (file && replaceCameraIndex.value !== null) {
    replaceCameraFile(
      replaceCameraIndex.value,
      file
    )
  } else if (file) {
    appendFiles([file], 'CAMERA')
  }

  replaceCameraIndex.value = null
  input.value = ''
}

function filesPicked(event: Event) {
  const input = event.target as HTMLInputElement
  appendFiles(
    Array.from(input.files ?? []),
    'PICKER'
  )
  input.value = ''
}

function appendFiles(
  files: File[],
  source: 'CAMERA' | 'PICKER'
) {
  for (const file of files) {
    selectedUploads.value.push({
      file,
      previewUrl: (
        file.type.startsWith('image/')
          ? URL.createObjectURL(file)
          : null
      ),
      source
    })
  }

  syncTitle()
}

function replaceCameraFile(
  index: number,
  file: File
) {
  const previous = selectedUploads.value[index]

  if (!previous) {
    appendFiles([file], 'CAMERA')
    return
  }

  if (previous.previewUrl) {
    URL.revokeObjectURL(previous.previewUrl)
  }

  selectedUploads.value[index] = {
    file,
    previewUrl: URL.createObjectURL(file),
    source: 'CAMERA'
  }

  syncTitle()
}

function removeFile(index: number) {
  const item = selectedUploads.value[index]

  if (item?.previewUrl) {
    URL.revokeObjectURL(item.previewUrl)
  }

  selectedUploads.value.splice(index, 1)
  syncTitle()
}

function moveFile(
  index: number,
  direction: -1 | 1
) {
  const target = index + direction

  if (
    target < 0
    || target >= selectedUploads.value.length
  ) {
    return
  }

  const [item] = selectedUploads.value.splice(index, 1)
  selectedUploads.value.splice(target, 0, item)
}

function syncTitle() {
  if (selectedUploads.value.length === 1) {
    title.value = (
      title.value.trim()
      || selectedUploads.value[0].file.name.replace(/\.[^.]+$/, '')
    )
  } else {
    title.value = ''
  }
}

function submit() {
  if (!canSubmit.value) {
    return
  }

  emit('uploadBatch', {
    title: (
      selectedUploads.value.length === 1
        ? title.value.trim()
        : null
    ),
    description: description.value.trim() || null,
    studentLearningContextId: contextId.value || null,
    studentSubjectId: subjectId.value || null,
    studentLearningUnitId: unitId.value || null,
    analysisRequested: analysisRequested.value,
    studyEnabled: studyEnabled.value,
    requestedModelId: null,
    aiMode: aiMode.value,
    fixedModelId: fixedModelId.value || null,
    textModelId: textModelId.value || null,
    visionModelId: visionModelId.value || null,
    embeddingModelId: embeddingModelId.value || null,
    thinkingMode: thinkingMode.value,
    files: selectedUploads.value.map(item => item.file)
  })
}

function availableModels(capability: string) {
  return (props.modelRegistry?.models ?? []).filter(model => {
    const capabilities = new Set(
      model.capabilities.map(item => item.toUpperCase())
    )

    if (!model.available || !capabilities.has(capability)) {
      return false
    }

    if (
      thinkingMode.value === 'ON'
      && capability !== 'EMBEDDINGS'
    ) {
      return capabilities.has('THINKING')
    }

    return true
  })
}

function needsVision(file: File): boolean {
  const name = file.name.toLowerCase()

  return (
    file.type.startsWith('image/')
    || file.type === 'application/pdf'
    || name.endsWith('.pdf')
    || name.endsWith('.doc')
    || name.endsWith('.docx')
  )
}

onBeforeUnmount(() => {
  for (const item of selectedUploads.value) {
    if (item.previewUrl) {
      URL.revokeObjectURL(item.previewUrl)
    }
  }
})
</script>

<template>
  <form
    class="formCard workspaceEmbeddedCard materialUploadCard"
    @submit.prevent="submit"
  >
    <div class="mobileUploadPrimaryActions">
      <button
        type="button"
        class="cameraActionButton"
        @click="openCamera()"
      >
        <span aria-hidden="true">📷</span>
        <span>
          <strong>Tirar foto</strong>
          <small>Use a câmera para apostila, livro ou exercício</small>
        </span>
      </button>

      <button
        type="button"
        class="pickerActionButton"
        @click="openPicker"
      >
        <span aria-hidden="true">🖼️</span>
        <span>
          <strong>Escolher foto ou arquivo</strong>
          <small>Galeria, PDF, DOCX ou arquivo do aparelho</small>
        </span>
      </button>
    </div>

    <input
      ref="cameraInput"
      class="hiddenFileInput"
      type="file"
      accept="image/*"
      capture="environment"
      @change="cameraCaptured"
    />

    <input
      ref="pickerInput"
      class="hiddenFileInput"
      type="file"
      multiple
      accept=".pdf,.txt,.md,.csv,.doc,.docx,image/*"
      @change="filesPicked"
    />

    <section
      v-if="selectedUploads.length > 0"
      class="mobileSelectedUploads"
    >
      <div class="selectedUploadHeader">
        <strong>
          {{ selectedUploads.length }}
          {{ selectedUploads.length === 1 ? 'arquivo' : 'arquivos' }}
        </strong>

        <small>
          Fotos são enviadas na ordem mostrada abaixo.
        </small>
      </div>

      <article
        v-for="(item, index) in selectedUploads"
        :key="`${item.file.name}-${item.file.size}-${index}`"
        class="mobileUploadPreview"
      >
        <img
          v-if="item.previewUrl"
          :src="item.previewUrl"
          :alt="`Prévia de ${item.file.name}`"
        />

        <div
          v-else
          class="fileTypePreview"
          aria-hidden="true"
        >
          DOC
        </div>

        <div class="mobileUploadPreviewInfo">
          <strong>{{ index + 1 }}. {{ item.file.name }}</strong>
          <small>
            {{ Math.max(1, Math.round(item.file.size / 1024)) }} KB
            · {{ item.source === 'CAMERA' ? 'Câmera' : 'Arquivo' }}
          </small>

          <div class="previewActions">
            <button
              v-if="item.file.type.startsWith('image/')"
              type="button"
              class="secondaryButton"
              @click="openCamera(index)"
            >
              Refazer foto
            </button>

            <button
              type="button"
              class="secondaryButton"
              :disabled="index === 0"
              @click="moveFile(index, -1)"
            >
              Subir
            </button>

            <button
              type="button"
              class="secondaryButton"
              :disabled="index === selectedUploads.length - 1"
              @click="moveFile(index, 1)"
            >
              Descer
            </button>

            <button
              type="button"
              class="dangerButton"
              @click="removeFile(index)"
            >
              Remover
            </button>
          </div>
        </div>
      </article>

      <button
        type="button"
        class="secondaryButton addAnotherPhotoButton"
        @click="openCamera()"
      >
        + Tirar outra foto
      </button>
    </section>

    <label v-if="!isMultiFile && selectedUploads.length > 0">
      Título
      <input
        v-model="title"
        required
        placeholder="Ex.: Apostila de Ciências"
      />
    </label>

    <details class="mobileUploadDetails" open>
      <summary>Organizar material</summary>

      <div class="detailsFormGrid">
        <label>
          Contexto
          <select v-model="contextId">
            <option value="">Somente aluno</option>

            <option
              v-for="item in contexts"
              :key="item.association.studentLearningContextId"
              :value="item.association.studentLearningContextId"
            >
              {{ item.context.name }}
            </option>
          </select>
        </label>

        <label>
          Matéria
          <select
            v-model="subjectId"
            :disabled="!contextId"
          >
            <option value="">Sem matéria específica</option>

            <option
              v-for="subject in subjects"
              :key="subject.studentSubjectId"
              :value="subject.studentSubjectId"
            >
              {{ subject.name }}
            </option>
          </select>
        </label>

        <label>
          Unidade
          <select
            v-model="unitId"
            :disabled="!subjectId"
          >
            <option value="">Sem unidade específica</option>

            <option
              v-for="unit in units"
              :key="unit.studentLearningUnitId"
              :value="unit.studentLearningUnitId"
            >
              {{ unit.title }}
            </option>
          </select>
        </label>
      </div>
    </details>

    <details class="mobileUploadDetails">
      <summary>Configuração de IA</summary>

      <div class="aiModeSelector">
        <label>
          Como a Lia deve escolher os modelos?
          <select v-model="aiMode">
            <option value="AUTO">
              Automático — recomendado
            </option>
            <option value="FIXED">
              Modelo fixo — não trocar silenciosamente
            </option>
            <option value="CUSTOM">
              Personalizado — modelo por capacidade
            </option>
          </select>
        </label>

        <p v-if="aiMode === 'AUTO'" class="formHint">
          A Lia escolhe modelos compatíveis para Texto, Vision e Embeddings
          e mostra quais foram usados.
        </p>

        <label>
          Raciocínio / Thinking
          <select v-model="thinkingMode">
            <option value="AUTO">
              Automático — usar quando o modelo suportar
            </option>
            <option value="ON">
              Sempre usar — exigir THINKING
            </option>
            <option value="OFF">
              Desativado — responder sem Thinking
            </option>
          </select>
        </label>

        <p class="formHint">
          Em Automático, Qwen, Gemma e outros modelos que declararem
          THINKING usam raciocínio; a Lia exibe apenas a resposta final.
        </p>


        <template v-if="aiMode === 'FIXED'">
          <label>
            Modelo único
            <select v-model="fixedModelId">
              <option value="">Selecione</option>

              <option
                v-for="model in modelRegistry?.models ?? []"
                :key="model.modelId"
                :value="model.modelId"
              >
                {{ model.displayName }}
                · {{ model.capabilities.join('/') }}
              </option>
            </select>
          </label>

          <p
            v-if="fixedMissingCapabilities.length > 0"
            class="modelRegistryWarning"
          >
            Este modelo não cobre:
            {{ fixedMissingCapabilities.join(', ') }}.
            Use Automático ou Personalizado.
          </p>
        </template>

        <div
          v-if="aiMode === 'CUSTOM'"
          class="customAiGrid"
        >
          <label>
            Texto / explicações
            <select v-model="textModelId">
              <option value="">Automático</option>
              <option
                v-for="model in textModels"
                :key="model.modelId"
                :value="model.modelId"
              >
                {{ model.displayName }}
              </option>
            </select>
          </label>

          <label>
            Vision
            <select v-model="visionModelId">
              <option value="">Automático</option>
              <option
                v-for="model in visionModels"
                :key="model.modelId"
                :value="model.modelId"
              >
                {{ model.displayName }}
              </option>
            </select>
          </label>

          <label>
            Embeddings
            <select v-model="embeddingModelId">
              <option value="">Automático</option>
              <option
                v-for="model in embeddingModels"
                :key="model.modelId"
                :value="model.modelId"
              >
                {{ model.displayName }}
              </option>
            </select>
          </label>
        </div>

        <button
          type="button"
          class="secondaryButton"
          @click="emit('refreshModels')"
        >
          Atualizar modelos
        </button>
      </div>
    </details>

    <label class="checkboxField">
      <input
        v-model="analysisRequested"
        type="checkbox"
      />
      <span>
        <strong>Analisar agora</strong>
        <small>
          OCR, Vision, evidências e indexação para estudo.
        </small>
      </span>
    </label>

    <label class="checkboxField">
      <input
        v-model="studyEnabled"
        type="checkbox"
      />
      <span>
        <strong>Usar no estudo</strong>
        <small>
          Materiais desligados não participam das atividades da Lia.
        </small>
      </span>
    </label>

    <details class="mobileUploadDetails">
      <summary>Descrição opcional</summary>

      <textarea
        v-model="description"
        rows="3"
        placeholder="Observações sobre o material"
      />
    </details>

    <button
      type="submit"
      class="primaryMobileSubmit"
      :disabled="!canSubmit"
    >
      <template v-if="busy">
        Enviando...
      </template>
      <template v-else-if="analysisRequested">
        Enviar e analisar
      </template>
      <template v-else>
        Armazenar sem analisar
      </template>
    </button>
  </form>
</template>
