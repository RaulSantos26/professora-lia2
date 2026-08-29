<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type {
  AiExecutionMode,
  ThinkingMode
} from '../contracts/aiExecutionPreferenceContract'
import type {
  AiModelRegistryContract
} from '../contracts/aiModelContract'
import type {
  MaterialContract
} from '../contracts/materialContract'

const props = defineProps<{
  material: MaterialContract
  modelRegistry: AiModelRegistryContract | null
}>()

const emit = defineEmits<{
  update: [
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
}>()

const mode = ref<AiExecutionMode>('AUTO')
const fixedModelId = ref('')
const textModelId = ref('')
const visionModelId = ref('')
const embeddingModelId = ref('')
const thinkingMode = ref<ThinkingMode>('AUTO')

const textModels = computed(
  () => modelsFor('TEXT')
)
const visionModels = computed(
  () => modelsFor('VISION')
)
const embeddingModels = computed(
  () => modelsFor('EMBEDDINGS')
)

const fixedModel = computed(
  () => (props.modelRegistry?.models ?? []).find(
    model => model.modelId === fixedModelId.value
  ) ?? null
)

const fixedMissingCapabilities = computed(() => {
  if (mode.value !== 'FIXED' || !fixedModel.value) {
    return []
  }

  const required = new Set<string>([
    'TEXT',
    'EMBEDDINGS'
  ])

  if (
    props.material.materialType === 'IMAGE'
    || props.material.materialType === 'PDF'
    || props.material.materialType === 'DOCUMENT'
  ) {
    required.add('VISION')
  }

  if (thinkingMode.value === 'ON') {
    required.add('THINKING')
  }

  const available = new Set(
    fixedModel.value.capabilities.map(
      capability => capability.toUpperCase()
    )
  )

  return [...required].filter(
    capability => !available.has(capability)
  )
})

watch(
  () => props.material,
  material => {
    mode.value = material.aiMode
    fixedModelId.value = material.fixedModelId ?? ''
    textModelId.value = material.textModelId ?? ''
    visionModelId.value = material.visionModelId ?? ''
    embeddingModelId.value = material.embeddingModelId ?? ''
    thinkingMode.value = material.thinkingMode
  },
  { immediate: true }
)

function modelsFor(capability: string) {
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

function apply() {
  emit(
    'update',
    props.material,
    {
      mode: mode.value,
      fixedModelId: (
        mode.value === 'FIXED'
          ? fixedModelId.value || null
          : null
      ),
      textModelId: (
        mode.value === 'CUSTOM'
          ? textModelId.value || null
          : null
      ),
      visionModelId: (
        mode.value === 'CUSTOM'
          ? visionModelId.value || null
          : null
      ),
      embeddingModelId: (
        mode.value === 'CUSTOM'
          ? embeddingModelId.value || null
          : null
      ),
      thinkingMode: thinkingMode.value
    }
  )
}
</script>

<template>
  <section class="selectedMaterialPreferences aiPreferenceEditor">
    <div>
      <p class="eyebrow">IA DESTE MATERIAL</p>
      <strong>{{ material.title }}</strong>
      <small>
        A configuração abaixo é persistida e não troca de significado
        silenciosamente.
      </small>
    </div>

    <label>
      Modo
      <select v-model="mode">
        <option value="AUTO">Automático</option>
        <option value="FIXED">Modelo fixo</option>
        <option value="CUSTOM">Personalizado</option>
      </select>
    </label>

    <label>
      Raciocínio / Thinking
      <select v-model="thinkingMode">
        <option value="AUTO">Automático</option>
        <option value="ON">Sempre usar</option>
        <option value="OFF">Desativado</option>
      </select>
    </label>


    <label v-if="mode === 'FIXED'">
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
      v-if="
        mode === 'FIXED'
        && fixedMissingCapabilities.length > 0
      "
      class="modelRegistryWarning"
    >
      Este modelo não cobre:
      {{ fixedMissingCapabilities.join(', ') }}.
      A configuração não pode ser salva como Modelo fixo.
    </p>

    <div
      v-if="mode === 'CUSTOM'"
      class="customAiGrid"
    >
      <label>
        Texto
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

    <p
      v-if="mode === 'AUTO'"
      class="aiModeExplanation"
    >
      A Lia pode usar modelos diferentes para Texto, Vision e Embeddings,
      sempre mostrando o modelo efetivamente utilizado.
    </p>

    <button
      type="button"
      class="secondaryButton"
      :disabled="
        mode === 'FIXED'
        && (
          !fixedModelId
          || fixedMissingCapabilities.length > 0
        )
      "
      @click="apply"
    >
      Salvar configuração
    </button>
  </section>
</template>
