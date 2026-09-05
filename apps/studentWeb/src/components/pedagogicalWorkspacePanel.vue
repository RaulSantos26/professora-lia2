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
import type { StudentSubjectContract } from '../contracts/studentSubjectContract'
import type { StudentLearningUnitContract } from '../contracts/studentLearningUnitContract'

const props = defineProps<{
  materials: MaterialContract[]
  selectedMaterial: MaterialContract | null
  subjects: StudentSubjectContract[]
  units: StudentLearningUnitContract[]
  selectedSubjectId: string | null
  selectedUnitId: string | null
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
  selectSubject: [subjectId: string]
  selectUnit: [unitId: string]
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

type MaterialGroup = {
  groupId: string
  title: string
  materialIds: string[]
  pageCount: number
  aiMode: string
}

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
      && material.studentSubjectId === props.selectedSubjectId
      && material.studentLearningUnitId === props.selectedUnitId
      && (
        material.status === 'READY'
        || material.status === 'PARTIAL'
      )
  )
)

const materialGroups = computed<MaterialGroup[]>(() => {
  const grouped = new Map<string, MaterialContract[]>()

  for (const material of studyMaterials.value) {
    const groupId = material.sourceGroupId ?? material.materialId
    const items = grouped.get(groupId) ?? []
    items.push(material)
    grouped.set(groupId, items)
  }

  return Array.from(grouped.entries())
    .map(([groupId, items]) => {
      const ordered = [...items].sort(
        (left, right) => (left.sourceSequence ?? 0) - (right.sourceSequence ?? 0)
      )
      const first = ordered[0]

      return {
        groupId,
        title: ordered.length > 1
          ? `Material consolidado · ${ordered.length} páginas`
          : first.title,
        materialIds: ordered.map(item => item.materialId),
        pageCount: ordered.length,
        aiMode: first.aiMode
      }
    })
    .sort((left, right) => left.title.localeCompare(right.title))
})

const selectedMaterialGroupCount = computed(
  () => materialGroups.value.filter(isMaterialGroupSelected).length
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
  [
    () => props.selectedSubjectId,
    () => props.selectedUnitId,
    () => props.selectedMaterial?.materialId
  ],
  () => {
    const selected = studyMaterials.value.find(
      item => item.materialId === props.selectedMaterial?.materialId
    )
    const selectedGroup = materialGroups.value.find(
      group => group.materialIds.includes(selected?.materialId ?? '')
    )

    selectedMaterialIds.value = selectedGroup?.materialIds
      ?? materialGroups.value[0]?.materialIds
      ?? []
  },
  { immediate: true }
)

function isMaterialGroupSelected(group: MaterialGroup): boolean {
  return group.materialIds.every(
    materialId => selectedMaterialIds.value.includes(materialId)
  )
}

function toggleMaterialGroup(group: MaterialGroup, selected: boolean) {
  const allowedIds = new Set(studyMaterials.value.map(item => item.materialId))
  const current = selectedMaterialIds.value.filter(
    materialId => allowedIds.has(materialId)
  )

  selectedMaterialIds.value = selected
    ? Array.from(new Set([...current, ...group.materialIds]))
    : current.filter(materialId => !group.materialIds.includes(materialId))
}

function selectSubject(event: Event) {
  emit('selectSubject', (event.target as HTMLSelectElement).value)
}
function selectUnit(event: Event) {
  emit('selectUnit', (event.target as HTMLSelectElement).value)
}

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

function evidenceKind(locator: string): string {
  if (locator.startsWith('Vision/OCR')) return 'Texto conferido pela Lia'
  if (locator.startsWith('OCR local')) return 'Trecho OCR normalizado'
  if (locator.startsWith('Vision')) return 'Leitura visual da Lia'
  return 'Evidência do material'
}

function formattedEvidenceExcerpt(excerpt: string): string {
  return excerpt
    .split(/\r?\n/)
    .map(line => line.replace(/\s+/g, ' ').trim())
    .filter(line => {
      const letters = (line.match(/[A-Za-zÀ-ÿ]/g) ?? []).length
      const alphanumeric = (line.match(/[A-Za-zÀ-ÿ0-9]/g) ?? []).length
      return letters >= 4 || alphanumeric >= 5
    })
    .join('\n')
    .trim()
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

    <section class="pedagogicalComposer">
      <div class="pedagogicalSettingsGrid">
        <label>
          Matéria
          <select :value="selectedSubjectId ?? ''" @change="selectSubject">
            <option value="">Escolha a matéria</option>
            <option v-for="subject in subjects" :key="subject.studentSubjectId" :value="subject.studentSubjectId">
              {{ subject.name }}
            </option>
          </select>
        </label>
        <label>
          Lição
          <select :value="selectedUnitId ?? ''" :disabled="!selectedSubjectId" @change="selectUnit">
            <option value="">Escolha a lição</option>
            <option v-for="unit in units" :key="unit.studentLearningUnitId" :value="unit.studentLearningUnitId">
              {{ unit.title }}
            </option>
          </select>
        </label>
      </div>
      <p v-if="!selectedUnitId" class="emptyState">
        Escolha uma matéria e uma lição para ver somente o conteúdo delas.
      </p>
    </section>

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
          Materiais consolidados usados ({{ selectedMaterialGroupCount }})
        </summary>

        <p class="emptyState">
          Cada lote de fotos é um único texto estruturado e auditado desta lição.
        </p>

        <div class="pedagogicalMaterialChoices">
          <label
            v-for="group in materialGroups"
            :key="group.groupId"
            class="materialChoice"
          >
            <input
              type="checkbox"
              :checked="isMaterialGroupSelected(group)"
              @change="toggleMaterialGroup(group, ($event.target as HTMLInputElement).checked)"
            />
            <span>
              <strong>{{ group.title }}</strong>
              <small>
                {{ group.pageCount }} página(s)
                · TEXTO ESTRUTURADO
                · {{ group.aiMode }}
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
              Automático — desativado para estabilidade
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

            <p class="pedagogicalEvidenceIntro">
              Trechos organizados para leitura. Após sucesso completo, a foto original é descartada; permanecem o texto, a leitura visual e os metadados estruturados.
            </p>
            <article
              v-for="(evidence, index) in selectedArtifact.sourceEvidence"
              :key="`${evidence.materialId}-${index}`"
              class="pedagogicalEvidenceItem"
            >
              <strong>[{{ index + 1 }}] {{ evidence.materialTitle }}</strong>
              <small>{{ evidenceKind(evidence.locator) }} · {{ evidence.locator }}</small>
              <details>
                <summary>Ver trecho usado pela Lia</summary>
                <p>{{ formattedEvidenceExcerpt(evidence.excerpt) }}</p>
              </details>
            </article>
          </details>
        </template>
      </section>
    </div>
  </section>
</template>
