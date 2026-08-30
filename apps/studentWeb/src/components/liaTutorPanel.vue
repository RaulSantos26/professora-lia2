<script setup lang="ts">
import {
  computed,
  nextTick,
  ref,
  watch
} from 'vue'

import VisualTaskRenderer from './visualTaskRenderer.vue'

import type {
  AgentConversationContract,
  AgentRunContract,
  AgentThreadContract
} from '../contracts/agentTutorContract'
import type {
  AiModelRegistryContract
} from '../contracts/aiModelContract'
import type {
  MaterialContract
} from '../contracts/materialContract'
import type { StudentSubjectContract } from '../contracts/studentSubjectContract'
import type { StudentLearningUnitContract } from '../contracts/studentLearningUnitContract'
import type {
  VisualTaskContract
} from '../contracts/visualTaskContract'

const props = defineProps<{
  threads: AgentThreadContract[]
  conversation: AgentConversationContract | null
  visualTasks: Record<string, VisualTaskContract>
  materials: MaterialContract[]
  selectedMaterial: MaterialContract | null
  subjects: StudentSubjectContract[]
  units: StudentLearningUnitContract[]
  selectedSubjectId: string | null
  selectedUnitId: string | null
  modelRegistry: AiModelRegistryContract | null
  busy: boolean
}>()

const emit = defineEmits<{
  selectThread: [thread: AgentThreadContract]
  selectSubject: [subjectId: string]
  selectUnit: [unitId: string]
  send: [request: {
    content: string
    requestedTextModelId: string | null
    thinkingMode: 'AUTO' | 'ON' | 'OFF'
    materialIds: string[]
  }]
  archiveThread: []
  retryLastRun: []
  openPedagogical: [artifactId: string]
}>()

const message = ref('')
const modelId = ref('')
const thinkingMode = ref<'AUTO' | 'ON' | 'OFF'>('AUTO')
const selectedMaterialIds = ref<string[]>([])
const messageList = ref<HTMLDivElement | null>(null)

const textModels = computed(
  () => (props.modelRegistry?.models ?? []).filter(model => {
    const capabilities = new Set(
      model.capabilities.map(
        item => item.toUpperCase()
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

const studyMaterials = computed(
  () => props.materials.filter(
    item =>
      item.studyEnabled
      && (
        item.status === 'READY'
        || item.status === 'PARTIAL'
      )
  )
)

const activeRun = computed(
  () => props.conversation?.activeRun ?? null
)

const failedRun = computed(
  () => {
    const run = props.conversation?.lastRun ?? null

    return run?.status === 'FAILED'
      ? run
      : null
  }
)

const failureGuidance = computed(
  () => {
    const code = failedRun.value?.errorCode

    if (code === 'AGENT_EVIDENCE_EMPTY') {
      return (
        'Ainda não há trechos pesquisáveis para este material. '
        + 'Em Materiais de estudo, analise e indexe o conteúdo antes de tentar novamente.'
      )
    }

    if (code === 'OLLAMA_TIMEOUT') {
      return (
        'O modelo demorou mais que o esperado. '
        + 'Tente novamente; se acontecer de novo, a Lia mostrará o erro para podermos ajustar.'
      )
    }

    return (
      'A Lia não conseguiu terminar esta resposta. '
      + 'Você pode tentar novamente sem perder sua pergunta.'
    )
  }
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
          item =>
            item.sourceGroupId === selected.sourceGroupId
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
    }
  },
  { immediate: true }
)

watch(
  () => props.conversation?.messages.length,
  async () => {
    await nextTick()
    messageList.value?.scrollTo({
      top: messageList.value.scrollHeight,
      behavior: 'smooth'
    })
  }
)

function selectSubject(event: Event) {
  emit('selectSubject', (event.target as HTMLSelectElement).value)
}
function selectUnit(event: Event) {
  emit('selectUnit', (event.target as HTMLSelectElement).value)
}

function submit() {
  const content = message.value.trim()

  if (
    content.length < 1
    || activeRun.value
    || props.busy
  ) {
    return
  }

  emit('send', {
    content,
    requestedTextModelId: modelId.value || null,
    thinkingMode: thinkingMode.value,
    materialIds: [...selectedMaterialIds.value]
  })

  message.value = ''
}

function actionArtifactId(
  action: Record<string, unknown>
): string | null {
  if (
    action.type !== 'PEDAGOGICAL_ARTIFACT'
    || typeof action.pedagogicalArtifactId !== 'string'
  ) {
    return null
  }

  return action.pedagogicalArtifactId
}

function openPedagogicalAction(
  action: Record<string, unknown>
) {
  const artifactId = actionArtifactId(action)

  if (artifactId) {
    emit('openPedagogical', artifactId)
  }
}
</script>

<template>
  <section class="liaTutorWorkspace">
    <header class="liaTutorHeader">
      <div>
        <p class="eyebrow">AGENTIC TUTOR</p>
        <h2>Lia</h2>
        <p>
          Converse sobre seus materiais. A Lia pode consultar evidências,
          acompanhar seu progresso e criar recursos visuais ou atividades.
        </p>
      </div>

      <span
        v-if="activeRun"
        class="agentRunBadge"
      >
        {{ activeRun.progressPercent }}%
      </span>
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
      v-if="activeRun"
      class="agentRunProgress"
    >
      <div>
        <span class="liaSpinner" />
        <strong>{{ activeRun.message }}</strong>
        <small>
          {{ activeRun.stage }}
          <template v-if="activeRun.effectiveTextModelId">
            · {{ activeRun.effectiveTextModelId }}
          </template>
        </small>
      </div>

      <div class="operationProgressTrack">
        <div
          class="operationProgressValue"
          :style="{
            width: `${activeRun.progressPercent}%`
          }"
        />
      </div>
    </section>

    <div class="liaTutorLayout">
      <aside class="liaThreadSidebar">
        <div class="sectionHeader">
          <div>
            <p class="eyebrow">CONVERSAS</p>
            <h3>Histórico</h3>
          </div>
        </div>

        <button
          v-for="thread in threads"
          :key="thread.agentThreadId"
          type="button"
          class="liaThreadButton"
          :data-selected="
            conversation?.thread.agentThreadId
            === thread.agentThreadId
          "
          @click="emit('selectThread', thread)"
        >
          <strong>{{ thread.title }}</strong>
          <small>
            {{
              thread.lastMessageAt
                ? new Date(thread.lastMessageAt).toLocaleString()
                : 'Sem mensagens'
            }}
          </small>
        </button>

        <button
          v-if="conversation && !activeRun"
          type="button"
          class="dangerButton archiveConversationButton"
          @click="emit('archiveThread')"
        >
          Excluir conversa do histórico
        </button>
      </aside>

      <section class="liaConversationColumn">
        <div
          ref="messageList"
          class="liaMessageList"
        >
          <div
            v-if="
              !conversation
              || conversation.messages.length === 0
            "
            class="liaConversationEmpty"
          >
            <span class="liaAvatar">L</span>
            <strong>Como posso ajudar?</strong>
            <p>
              Você pode pedir uma explicação, resumo, mapa mental,
              diagrama, gráfico, animação, cena 3D, exercício ou
              perguntar como está seu progresso.
            </p>

            <div class="liaPromptSuggestions">
              <button
                type="button"
                @click="
                  message = 'Explique essa matéria de um jeito mais simples.'
                "
              >
                Explique de outro jeito
              </button>

              <button
                type="button"
                @click="
                  message = 'Crie um mapa mental interativo desta matéria.'
                "
              >
                Mapa mental
              </button>

              <button
                type="button"
                @click="
                  message = 'Existe alguma forma visual ou animação que ajude a entender isso?'
                "
              >
                Explique visualmente
              </button>

              <button
                type="button"
                @click="
                  message = 'Como está meu progresso nesta matéria?'
                "
              >
                Meu progresso
              </button>
            </div>
          </div>

          <article
            v-for="item in conversation?.messages ?? []"
            :key="item.agentMessageId"
            class="liaMessage"
            :data-role="item.role"
          >
            <div class="liaMessageBubble">
              <strong>
                {{ item.role === 'USER' ? 'Você' : 'Lia' }}
              </strong>
              <p>{{ item.content }}</p>
            </div>

            <details
              v-if="
                item.role === 'ASSISTANT'
                && item.citations.length > 0
              "
              class="liaCitationDetails"
            >
              <summary>
                Evidências ({{ item.citations.length }})
              </summary>

              <article
                v-for="(citation, index) in item.citations"
                :key="`${item.agentMessageId}-${index}`"
              >
                <strong>
                  [{{ citation.index }}]
                  {{ citation.materialTitle }}
                </strong>
                <small>{{ citation.locator }}</small>
                <p>{{ citation.excerpt }}</p>
              </article>
            </details>

            <template
              v-for="visualTaskId in item.visualTaskIds"
              :key="visualTaskId"
            >
              <VisualTaskRenderer
                v-if="visualTasks[visualTaskId]"
                :task="visualTasks[visualTaskId]"
              />
            </template>

            <div
              v-if="
                item.role === 'ASSISTANT'
                && item.actions.length > 0
              "
              class="liaActionLinks"
            >
              <button
                v-for="(action, index) in item.actions"
                :key="index"
                v-show="actionArtifactId(action)"
                type="button"
                class="secondaryButton"
                @click="openPedagogicalAction(action)"
              >
                Abrir atividade em Estudar
              </button>
            </div>
          </article>

          <article
            v-if="failedRun"
            class="liaMessage liaRunFailure"
            data-role="ASSISTANT"
          >
            <div class="liaMessageBubble">
              <strong>Não foi possível concluir esta resposta</strong>
              <p>{{ failureGuidance }}</p>
              <button
                type="button"
                class="secondaryButton"
                :disabled="busy || Boolean(activeRun)"
                @click="emit('retryLastRun')"
              >
                Tentar novamente
              </button>
            </div>

            <details
              class="liaFailureDetails"
            >
              <summary>Detalhes técnicos</summary>
              <p>
                {{ failedRun.errorCode ?? 'AGENT_RUN_FAILED' }}
                · {{ failedRun.errorMessage ?? failedRun.message }}
              </p>
            </details>
          </article>

          <article
            v-if="activeRun"
            class="liaMessage"
            data-role="ASSISTANT"
          >
            <div class="liaMessageBubble liaTypingBubble">
              <span class="liaSpinner" />
              <span>{{ activeRun.message }}</span>
            </div>
          </article>
        </div>

        <form
          class="liaComposer"
          @submit.prevent="submit"
        >
          <div class="liaComposerOptions">
            <label>
              Modelo
              <select v-model="modelId">
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
              Thinking
              <select v-model="thinkingMode">
                <option value="AUTO">Automático (mais estável)</option>
                <option value="ON">Sempre usar</option>
                <option value="OFF">Desativado</option>
              </select>
            </label>
          </div>

          <details class="liaMaterialScope">
            <summary>
              Materiais desta conversa
              ({{ selectedMaterialIds.length }})
            </summary>

            <label
              v-for="material in studyMaterials"
              :key="material.materialId"
            >
              <input
                v-model="selectedMaterialIds"
                type="checkbox"
                :value="material.materialId"
              />
              <span>
                <strong>{{ material.title }}</strong>
                <small>{{ material.materialType }}</small>
              </span>
            </label>
          </details>

          <div class="liaComposerInput">
            <textarea
              v-model="message"
              rows="3"
              placeholder="Pergunte à Lia..."
              :disabled="Boolean(activeRun)"
              @keydown.ctrl.enter="submit"
            />

            <button
              type="submit"
              class="liaSendButton"
              :disabled="
                Boolean(activeRun)
                || busy
                || message.trim().length === 0
              "
            >
              Enviar
            </button>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>
