<script setup lang="ts">
import { reactive } from 'vue'
import type {
  LearningStateStatus,
  StudentLearningStateViewContract
} from '../contracts/studentLearningStateContract'

defineProps<{
  states: StudentLearningStateViewContract[]
}>()

const emit = defineEmits<{
  update: [
    unitId: string,
    status: LearningStateStatus,
    mastery: number,
    confidence: number
  ]
}>()

interface DraftState {
  status: LearningStateStatus
  mastery: number
  confidence: number
}

const drafts = reactive<Record<string, DraftState>>({})

function getDraft(item: StudentLearningStateViewContract): DraftState {
  const key = item.studentLearningUnitId

  if (!drafts[key]) {
    drafts[key] = {
      status: item.state?.status ?? 'NOT_STARTED',
      mastery: item.state?.masteryLevel ?? 0,
      confidence: item.state?.confidenceLevel ?? 0
    }
  }

  return drafts[key]
}
</script>

<template>
  <section class="workspaceFeaturePanel">
    <div class="workspaceFeatureHeader">
      <div>
        <p class="eyebrow">LEARNING STATE</p>
        <h2>Progresso</h2>
      </div>
      <span class="countBadge">{{ states.length }}</span>
    </div>

    <p v-if="states.length === 0" class="emptyState">
      Nenhuma unidade para acompanhar.
    </p>

    <article
      v-for="item in states"
      :key="item.studentLearningUnitId"
      class="progressRow"
    >
      <div class="progressIdentity">
        <strong>{{ item.unitTitle }}</strong>
        <span>
          {{ item.contextName }} · {{ item.subjectName }} · {{ item.unitCode }}
        </span>
        <small>Estudos: {{ item.state?.studyCount ?? 0 }}</small>
      </div>

      <label>
        Estado
        <select v-model="getDraft(item).status">
          <option value="NOT_STARTED">Não iniciado</option>
          <option value="LEARNING">Aprendendo</option>
          <option value="REVIEWING">Revisando</option>
          <option value="MASTERED">Dominado</option>
        </select>
      </label>

      <label>
        Domínio
        <input v-model.number="getDraft(item).mastery" type="number" min="0" max="100" />
      </label>

      <label>
        Confiança
        <input v-model.number="getDraft(item).confidence" type="number" min="0" max="100" />
      </label>

      <button
        type="button"
        @click="
          emit(
            'update',
            item.studentLearningUnitId,
            getDraft(item).status,
            getDraft(item).mastery,
            getDraft(item).confidence
          )
        "
      >
        Atualizar
      </button>
    </article>
  </section>
</template>
