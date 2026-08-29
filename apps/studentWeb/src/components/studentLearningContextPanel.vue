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
  deactivate: [
    studentLearningContextId: string,
    contextName: string
  ]
}>()

function isAssigned(learningContextId: string): boolean {
  return props.assignedContexts.some(
    item =>
      item.context.learningContextId === learningContextId
  )
}

function confirmDeactivate(
  item: StudentLearningContextViewContract
) {
  if (
    window.confirm(
      `Remover "${item.context.name}" dos contextos ativos?\n\n`
      + 'As lições e materiais já criados serão preservados.'
    )
  ) {
    emit(
      'deactivate',
      item.association.studentLearningContextId,
      item.context.name
    )
  }
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
        <div class="contextRowActions">
          <span data-status="ONLINE">ATIVO</span>
          <button
            type="button"
            class="secondaryButton"
            :disabled="busy"
            @click="confirmDeactivate(item)"
          >
            Remover
          </button>
        </div>
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
            isAssigned(context.learningContextId)
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
            isAssigned(context.learningContextId)
              ? 'Vinculado'
              : 'Vincular'
          }}
        </button>
      </article>
    </div>
  </section>
</template>
