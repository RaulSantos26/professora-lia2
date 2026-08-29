<script setup lang="ts">
import type { LearningContextContract } from '../contracts/learningContextContract'
import type {
  LearningContextSubjectViewContract
} from '../contracts/learningContextSubjectContract'
import type { SubjectContract } from '../contracts/subjectContract'

defineProps<{
  learningContexts: LearningContextContract[]
  selectedLearningContextId: string | null
  subjects: SubjectContract[]
  assignedSubjects: LearningContextSubjectViewContract[]
  selectedAssociationId: string | null
}>()

const emit = defineEmits<{
  selectContext: [learningContextId: string]
  assignSubject: [subjectId: string]
  selectAssociation: [association: LearningContextSubjectViewContract]
}>()
</script>

<template>
  <section class="contentCard">
    <div class="sectionHeader">
      <div>
        <p class="eyebrow">CONTEXT + SUBJECT</p>
        <h2>Matérias do contexto</h2>
      </div>
      <span class="countBadge">{{ assignedSubjects.length }}</span>
    </div>

    <label class="standaloneField">
      Contexto
      <select
        :value="selectedLearningContextId ?? ''"
        @change="
          emit(
            'selectContext',
            ($event.target as HTMLSelectElement).value
          )
        "
      >
        <option value="" disabled>Selecione</option>
        <option
          v-for="context in learningContexts"
          :key="context.learningContextId"
          :value="context.learningContextId"
        >
          {{ context.name }}
        </option>
      </select>
    </label>

    <template v-if="selectedLearningContextId">
      <div class="contextCatalog">
        <p class="eyebrow">VINCULADAS</p>

        <p v-if="assignedSubjects.length === 0" class="emptyState">
          Nenhuma matéria vinculada ao contexto.
        </p>

        <button
          v-for="item in assignedSubjects"
          :key="item.association.learningContextSubjectId"
          type="button"
          class="subjectChoice"
          :data-selected="
            item.association.learningContextSubjectId === selectedAssociationId
          "
          @click="emit('selectAssociation', item)"
        >
          <span>
            <strong>{{ item.subject.name }}</strong>
            <small>{{ item.subject.code }}</small>
          </span>
          <span data-status="ONLINE">ACTIVE</span>
        </button>
      </div>

      <div class="contextCatalog">
        <p class="eyebrow">CATÁLOGO</p>

        <article
          v-for="subject in subjects"
          :key="subject.subjectId"
          class="contextRow"
        >
          <div>
            <strong>{{ subject.name }}</strong>
            <p>{{ subject.code }}</p>
          </div>

          <button
            type="button"
            :disabled="
              assignedSubjects.some(
                item => item.subject.subjectId === subject.subjectId
              )
            "
            @click="emit('assignSubject', subject.subjectId)"
          >
            {{
              assignedSubjects.some(
                item => item.subject.subjectId === subject.subjectId
              )
                ? 'Vinculada'
                : 'Vincular'
            }}
          </button>
        </article>
      </div>
    </template>
  </section>
</template>
