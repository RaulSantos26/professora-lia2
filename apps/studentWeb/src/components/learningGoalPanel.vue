<script setup lang="ts">
import { ref } from 'vue'
import type {
  LearningGoalContract,
  LearningGoalCreateContract,
  LearningGoalType
} from '../contracts/learningGoalContract'
import type { StudentLearningContextViewContract } from '../contracts/studentLearningContextContract'

defineProps<{
  contexts: StudentLearningContextViewContract[]
  goals: LearningGoalContract[]
  selectedGoalId: string | null
}>()

const emit = defineEmits<{
  create: [payload: LearningGoalCreateContract]
  select: [goal: LearningGoalContract]
}>()

const goalType = ref<LearningGoalType>('TEST')
const title = ref('')
const contextId = ref('')
const targetDate = ref('')
const priority = ref(3)
const description = ref('')

function submit() {
  if (title.value.trim().length < 2) return

  emit('create', {
    contractName: 'LearningGoalCreate.v1',
    studentLearningContextId: contextId.value || null,
    goalType: goalType.value,
    title: title.value.trim(),
    description: description.value.trim() || null,
    targetDate: targetDate.value || null,
    priority: priority.value
  })

  title.value = ''
  targetDate.value = ''
  description.value = ''
}
</script>

<template>
  <section class="workspaceFeaturePanel">
    <div class="workspaceFeatureHeader">
      <div>
        <p class="eyebrow">LEARNING GOAL</p>
        <h2>Objetivos de estudo</h2>
      </div>
      <span class="countBadge">{{ goals.length }}</span>
    </div>

    <div class="workspacePanelGrid">
      <form class="formCard workspaceEmbeddedCard" @submit.prevent="submit">
        <label>
          Tipo
          <select v-model="goalType">
            <option value="TEST">Prova</option>
            <option value="EXAM">Exame</option>
            <option value="REVIEW">Revisão</option>
            <option value="PROJECT">Projeto</option>
            <option value="COURSE">Curso</option>
            <option value="CERTIFICATION">Certificação</option>
            <option value="OTHER">Outro</option>
          </select>
        </label>

        <label>
          Objetivo
          <input v-model="title" required placeholder="Ex.: Prova de História" />
        </label>

        <label>
          Contexto
          <select v-model="contextId">
            <option value="">Sem restrição de contexto</option>
            <option
              v-for="item in contexts"
              :key="item.association.studentLearningContextId"
              :value="item.association.studentLearningContextId"
            >
              {{ item.context.name }}
            </option>
          </select>
        </label>

        <div class="fieldGrid">
          <label>
            Data-alvo
            <input v-model="targetDate" type="date" />
          </label>
          <label>
            Prioridade
            <select v-model="priority">
              <option :value="1">1 - Baixa</option>
              <option :value="2">2</option>
              <option :value="3">3 - Normal</option>
              <option :value="4">4</option>
              <option :value="5">5 - Alta</option>
            </select>
          </label>
        </div>

        <label>
          Descrição
          <textarea v-model="description" rows="3" placeholder="Opcional" />
        </label>

        <button type="submit">Criar objetivo</button>
      </form>

      <div class="workspaceListCard">
        <p v-if="goals.length === 0" class="emptyState">
          Nenhum objetivo criado.
        </p>
        <button
          v-for="goal in goals"
          :key="goal.learningGoalId"
          type="button"
          class="workspaceSelectableRow"
          :data-selected="goal.learningGoalId === selectedGoalId"
          @click="emit('select', goal)"
        >
          <span>
            <strong>{{ goal.title }}</strong>
            <small>
              {{ goal.goalType }}
              <template v-if="goal.targetDate"> · {{ goal.targetDate }}</template>
            </small>
          </span>
          <span data-status="ONLINE">{{ goal.status }}</span>
        </button>
      </div>
    </div>
  </section>
</template>
