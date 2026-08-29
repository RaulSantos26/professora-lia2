<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import PedagogicalArtifactRenderer from './pedagogicalArtifactRenderer.vue'

import type {
  AiModelRegistryContract
} from '../contracts/aiModelContract'
import type {
  LearningAttemptContract,
  PedagogicalArtifactContract,
  PedagogicalArtifactType
} from '../contracts/pedagogicalContract'
import type {
  MaterialContract
} from '../contracts/materialContract'

const props = defineProps<{
  materials: MaterialContract[]
  selectedMaterial: MaterialContract | null
  modelRegistry: AiModelRegistryContract | null
  artifacts: PedagogicalArtifactContract[]
  selectedArtifact: PedagogicalArtifactContract | null
  attempt: LearningAttemptContract | null
  busy: boolean
}>()

const emit = defineEmits<{
  create: [request: {
    artifactType: PedagogicalArtifactType
    title: string | null
    instruction: string | null
    materialIds: string[]
    difficulty: 'AUTO' | 'EASY' | 'MEDIUM' | 'HARD'
    questionCount: number
    requestedTextModelId: string | null
    thinkingMode: 'AUTO' | 'ON' | 'OFF'
  }]
  select: [artifact: PedagogicalArtifactContract]
  archive: [artifactId: string]
  submitAttempt: [
    artifactId: string,
    answers: Record<string, string>
  ]
}>()

const artifactType = ref<PedagogicalArtifactType>('TEACH')
const instruction = ref('')
const difficulty = ref<'AUTO' | 'EASY' | 'MEDIUM' | 'HARD'>('AUTO')
const questionCount = ref(8)
const requestedTextModelId = ref('')
const thinkingMode = ref<'AUTO' | 'ON' | 'OFF'>('AUTO')
const selectedMaterialIds = ref<string[]>([])

const actionCards: Array<{
  type: PedagogicalArtifactType
  title: string
  description: string
  icon: string
}> = [
  {
    type: 'TEACH',
    title: 'Me ensine',
    description: 'Aula guiada, passo a passo.',
    icon: '📖'
  },
  {
    type: 'EXPLAIN',
    title: 'Explicar',
    description: 'Outra explicação para uma dúvida.',
    icon: '💡'
  },
  {
    type: 'SUMMARY',
    title: 'Resumo',
    description: 'Revisão dos pontos principais.',
    icon: '📝'
  },
  {
    type: 'MIND_MAP',
    title: 'Mapa mental',
    description: 'Conceitos e relações de forma visual.',
    icon: '🧠'
  },
  {
    type: 'FLASHCARDS',
    title: 'Flashcards',
    description: 'Cartões rápidos para memorizar.',
    icon: '🃏'
  },
  {
    type: 'EXERCISES',
    title: 'Exercícios',
    description: 'Prática com correção e progresso.',
    icon: '✏️'
  },
  {
    type: 'QUIZ',
    title: 'Quiz',
    description: 'Teste rápido de compreensão.',
    icon: '🎯'
  }
]

const studyMaterials = computed(
  () => props.materials.filter(
    material =>
      material.studyEnabled
      && (
        material.status === 'READY'
        || material.status === 'PARTIAL'
      )
  )
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

    if (thinkingMode.value === 'ON') {
      return capabilities.has('THINKING')
    }

    return true
  })
)

const activeArtifact = computed(
  () => props.artifacts.find(
    artifact =>
      artifact.status === 'QUEUED'
      || artifact.status === 'RUNNING'
  ) ?? null
)

const showAssessmentOptions = computed(
  () => (
    artifactType.value === 'EXERCISES'
    || artifactType.value === 'QUIZ'
  )
)

watch(
  () => props.selectedMaterial?.materialId,
  materialId => {
    const selected = studyMaterials.value.find(
      item => item.materialId === materialId
    )

    if (selected?.sourceGroupId) {
      selectedMaterialIds.value = studyMaterials.value
        .filter(
          item => item.sourceGroupId === selected.sourceGroupId
        )
        .sort(
          (left, right) =>
            (left.sourceSequence ?? 0)
            - (right.sourceSequence ?? 0)
        )
        .map(item => item.materialId)
      return
    }

    if (selected) {
      selectedMaterialIds.value = [selected.materialId]
    } else if (
      selectedMaterialIds.value.length === 0
      && studyMaterials.value.length > 0
    ) {
      selectedMaterialIds.value = [studyMaterials.value[0].materialId]
    }
  },
  { immediate: true }
)

function selectAction(type: PedagogicalArtifactType) {
  artifactType.value = type
}

function create() {
  if (selectedMaterialIds.value.length === 0) {
    return
  }

  emit('create', {
    artifactType: artifactType.value,
    title: null,
    instruction: instruction.value.trim() || null,
    materialIds: [...selectedMaterialIds.value],
    difficulty: difficulty.value,
    questionCount: questionCount.value,
    requestedTextModelId: requestedTextModelId.value || null,
    thinkingMode: thinkingMode.value
  })
}

function typeLabel(type: PedagogicalArtifactType): string {
  return actionCards.find(item => item.type === type)?.title ?? type
}

function confirmArchive(artifact: PedagogicalArtifactContract) {
  if (
    artifact.status === 'QUEUED'
    || artifact.status === 'RUNNING'
  ) {
    return
  }

  if (window.confirm(`Remover "${artifact.title}" do histórico?`)) {
    emit('archive', artifact.pedagogicalArtifactId)
  }
}
</script>

<template>
  <section class="workspaceFeaturePanel pedagogicalWorkspace">
    <header class="workspaceFeatureHeader">
      <div>
        <p class="eyebrow">MOTOR PEDAGÓGICO</p>
        <h2>Estudar com a Lia</h2>
        <p>
          Escolha como quer estudar. A Lia usa somente as evidências
          dos materiais selecionados.
        </p>
      </div>

      <span class="countBadge">{{ artifacts.length }}</span>
    </header>

    <section
      v-if="activeArtifact"
      class="pedagogicalGenerationProgress"
    >
      <div class="operationProgressHeader">
        <span class="liaSpinner" />

        <div>
          <strong>{{ activeArtifact.title }}</strong>
          <small>{{ activeArtifact.message }}</small>
        </div>

        <b>{{ activeArtifact.progressPercent }}%</b>
      </div>

      <div class="operationProgressTrack">
        <div
          class="operationProgressValue"
          :style="{
            width: `${activeArtifact.progressPercent}%`
          }"
        />
      </div>
    </section>

    <div class="pedagogicalActionGrid">
      <button
        v-for="action in actionCards"
        :key="action.type"
        type="button"
        class="pedagogicalActionCard"
        :data-selected="artifactType === action.type"
        @click="selectAction(action.type)"
      >
        <span class="pedagogicalActionIcon">
          {{ action.icon }}
        </span>

        <span>
          <strong>{{ action.title }}</strong>
          <small>{{ action.description }}</small>
        </span>
      </button>
    </div>

    <section class="pedagogicalComposer">
      <div class="pedagogicalComposerHeader">
        <div>
          <p class="eyebrow">CRIAR ATIVIDADE</p>
          <h3>{{ typeLabel(artifactType) }}</h3>
        </div>
      </div>

      <label>
        O que você quer focar?
        <textarea
          v-model="instruction"
          rows="3"
          :placeholder="
            artifactType === 'EXPLAIN'
              ? 'Ex.: Não entendi a diferença entre tecido conjuntivo e tecido nervoso.'
              : 'Opcional: informe um assunto ou objetivo específico.'
          "
        />
      </label>

      <details class="pedagogicalSourceSelector" open>
        <summary>
          Materiais usados ({{ selectedMaterialIds.length }})
        </summary>

        <div class="pedagogicalMaterialChoices">
          <label
            v-for="material in studyMaterials"
            :key="material.materialId"
            class="materialChoice"
          >
            <input
              v-model="selectedMaterialIds"
              type="checkbox"
              :value="material.materialId"
            />
            <span>
              <strong>{{ material.title }}</strong>
              <small>
                {{ material.materialType }}
                · {{ material.aiMode }}
              </small>
            </span>
          </label>
        </div>
      </details>

      <div class="pedagogicalSettingsGrid">
        <label>
          Modelo para explicar/criar
          <select v-model="requestedTextModelId">
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
          Raciocínio / Thinking
          <select v-model="thinkingMode">
            <option value="AUTO">
              Automático — usar se suportado
            </option>
            <option value="ON">
              Sempre usar — exigir THINKING
            </option>
            <option value="OFF">
              Desativado
            </option>
          </select>
        </label>

        <label v-if="showAssessmentOptions">
          Dificuldade
          <select v-model="difficulty">
            <option value="AUTO">
              Adaptativa — recomendada
            </option>
            <option value="EASY">Fácil</option>
            <option value="MEDIUM">Média</option>
            <option value="HARD">Difícil</option>
          </select>
        </label>

        <label v-if="showAssessmentOptions">
          Quantidade
          <select v-model.number="questionCount">
            <option :value="5">5</option>
            <option :value="8">8</option>
            <option :value="10">10</option>
            <option :value="15">15</option>
            <option :value="20">20</option>
          </select>
        </label>
      </div>

      <button
        type="button"
        class="primaryStudyAction"
        :disabled="
          busy
          || selectedMaterialIds.length === 0
        "
        @click="create"
      >
        {{
          busy
            ? 'Preparando...'
            : `Criar ${typeLabel(artifactType)}`
        }}
      </button>
    </section>

    <div class="pedagogicalWorkspaceGrid">
      <aside class="pedagogicalHistory">
        <div class="sectionHeader">
          <div>
            <p class="eyebrow">HISTÓRICO</p>
            <h3>Conteúdos criados</h3>
          </div>
        </div>

        <p
          v-if="artifacts.length === 0"
          class="emptyState"
        >
          Nenhuma atividade criada ainda.
        </p>

        <article
          v-for="artifact in artifacts"
          :key="artifact.pedagogicalArtifactId"
          class="pedagogicalHistoryItem"
          :data-selected="
            selectedArtifact?.pedagogicalArtifactId
            === artifact.pedagogicalArtifactId
          "
        >
          <button
            type="button"
            @click="emit('select', artifact)"
          >
            <strong>{{ artifact.title }}</strong>
            <small>
              {{ typeLabel(artifact.artifactType) }}
              · {{ artifact.status }}
            </small>
          </button>

          <button
            v-if="
              artifact.status !== 'QUEUED'
              && artifact.status !== 'RUNNING'
            "
            type="button"
            class="historyDeleteButton"
            @click="confirmArchive(artifact)"
          >
            Remover
          </button>
        </article>
      </aside>

      <section class="pedagogicalResult">
        <div
          v-if="!selectedArtifact"
          class="pedagogicalEmptyResult"
        >
          <strong>Escolha uma atividade</strong>
          <p>
            O conteúdo gerado ficará salvo aqui para continuar depois,
            inclusive no celular ou tablet.
          </p>
        </div>

        <template v-else>
          <header class="pedagogicalResultHeader">
            <div>
              <p class="eyebrow">
                {{ typeLabel(selectedArtifact.artifactType) }}
              </p>
              <h3>{{ selectedArtifact.title }}</h3>
              <small v-if="selectedArtifact.effectiveTextModelId">
                Modelo: {{ selectedArtifact.effectiveTextModelId }}
                · Thinking:
                {{
                  selectedArtifact.effectiveThinkingEnabled
                    ? 'ATIVADO'
                    : 'DESATIVADO'
                }}
              </small>
            </div>

            <span
              class="artifactStatusBadge"
              :data-status="selectedArtifact.status"
            >
              {{ selectedArtifact.status }}
            </span>
          </header>

          <div
            v-if="
              selectedArtifact.status === 'QUEUED'
              || selectedArtifact.status === 'RUNNING'
            "
            class="pedagogicalWaiting"
          >
            <span class="liaSpinner" />
            <strong>{{ selectedArtifact.message }}</strong>
            <span>{{ selectedArtifact.progressPercent }}%</span>
          </div>

          <div
            v-else-if="selectedArtifact.status === 'FAILED'"
            class="materialErrorSummary"
          >
            <strong>{{ selectedArtifact.errorCode }}</strong>
            <span>{{ selectedArtifact.errorMessage }}</span>
          </div>

          <PedagogicalArtifactRenderer
            v-else-if="
              selectedArtifact.status === 'READY'
              && selectedArtifact.content
            "
            :artifact="selectedArtifact"
            :attempt="attempt"
            :busy="busy"
            @submit-attempt="
              answers =>
                emit(
                  'submitAttempt',
                  selectedArtifact.pedagogicalArtifactId,
                  answers
                )
            "
          />

          <details
            v-if="selectedArtifact.sourceEvidence.length > 0"
            class="pedagogicalEvidenceDetails"
          >
            <summary>
              Evidências usadas
              ({{ selectedArtifact.sourceEvidence.length }})
            </summary>

            <article
              v-for="(evidence, index) in selectedArtifact.sourceEvidence"
              :key="`${evidence.materialId}-${index}`"
            >
              <strong>
                [{{ index + 1 }}] {{ evidence.materialTitle }}
              </strong>
              <small>{{ evidence.locator }}</small>
              <p>{{ evidence.excerpt }}</p>
            </article>
          </details>
        </template>
      </section>
    </div>
  </section>
</template>
