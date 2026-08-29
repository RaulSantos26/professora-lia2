<script setup lang="ts">
import type { AcademicStageContract } from '../contracts/academicStageContract'
import type { LearningContextContract } from '../contracts/learningContextContract'
import type {
  StudentLearningContextViewContract
} from '../contracts/studentLearningContextContract'

defineProps<{
  availableContexts: LearningContextContract[]
  assignedContexts: StudentLearningContextViewContract[]
  currentAcademicStage: AcademicStageContract | null
  busy: boolean
}>()

const emit = defineEmits<{
  assign: [learningContextId: string, academicStageId: string | null]
}>()

function isAssigned(learningContextId: string): boolean {
  return false
}
</script>

<template>
  <section class="contentCard">
    <div class="sectionHeader">
      <div>
        <p class="eyebrow">CONTEXTOS ATIVOS</p>
        <h2>Contextos do aluno</h2>
      </div>
      <span class="countBadge">{{ assignedContexts.length }}</span>
    </div>

    <div v-if="assignedContexts.length" class="contextList">
      <article
        v-for="item in assignedContexts"
        :key="item.association.studentLearningContextId"
        class="contextRow"
      >
        <div>
          <strong>{{ item.context.name }}</strong>
          <p>{{ item.context.contextType }} · {{ item.context.code }}</p>
        </div>
        <span data-status="ONLINE">ACTIVE</span>
      </article>
    </div>

    <p v-else class="emptyState">
      Nenhum contexto de estudo ativo para este aluno.
    </p>

    <div class="contextCatalog">
      <p class="eyebrow">DISPONÍVEIS</p>

      <article
        v-for="context in availableContexts"
        :key="context.learningContextId"
        class="contextRow"
      >
        <div>
          <strong>{{ context.name }}</strong>
          <p>{{ context.contextType }} · {{ context.code }}</p>
        </div>

        <button
          type="button"
          :disabled="
            busy ||
            assignedContexts.some(
              item => item.context.learningContextId === context.learningContextId
            )
          "
          @click="
            emit(
              'assign',
              context.learningContextId,
              currentAcademicStage?.academicStageId ?? null
            )
          "
        >
          {{
            assignedContexts.some(
              item => item.context.learningContextId === context.learningContextId
            )
              ? 'Vinculado'
              : 'Vincular'
          }}
        </button>
      </article>
    </div>
  </section>
</template>
