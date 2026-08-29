<script setup lang="ts">
import { ref } from 'vue'

import type {
  StudentSubjectContract,
  StudentSubjectCreateContract
} from '../contracts/studentSubjectContract'
import type {
  StudentLearningContextViewContract
} from '../contracts/studentLearningContextContract'

defineProps<{
  contexts: StudentLearningContextViewContract[]
  selectedContextId: string | null
  subjects: StudentSubjectContract[]
  selectedSubjectId: string | null
}>()

const emit = defineEmits<{
  selectContext: [studentLearningContextId: string]
  create: [payload: StudentSubjectCreateContract]
  selectSubject: [subject: StudentSubjectContract]
}>()

const code = ref('')
const name = ref('')
const description = ref('')

function submit() {
  if (code.value.trim().length < 2 || name.value.trim().length < 2) {
    return
  }

  emit('create', {
    contractName: 'StudentSubjectCreate.v1',
    subjectDefinitionId: null,
    code: code.value.trim(),
    name: name.value.trim(),
    description: description.value.trim() || null
  })

  code.value = ''
  name.value = ''
  description.value = ''
}
</script>

<template>
  <section class="studentSpecificPanel">
    <div class="studentSpecificHeader">
      <div>
        <p class="eyebrow">STUDENT SUBJECT</p>
        <h2>Matérias deste aluno/contexto</h2>
      </div>
      <span class="countBadge">{{ subjects.length }}</span>
    </div>

    <label class="standaloneField">
      Contexto do aluno
      <select
        :value="selectedContextId ?? ''"
        @change="
          emit(
            'selectContext',
            ($event.target as HTMLSelectElement).value
          )
        "
      >
        <option value="" disabled>Selecione</option>
        <option
          v-for="item in contexts"
          :key="item.association.studentLearningContextId"
          :value="item.association.studentLearningContextId"
        >
          {{ item.context.name }}
        </option>
      </select>
    </label>

    <form
      v-if="selectedContextId"
      class="inlineForm studentSubjectForm"
      @submit.prevent="submit"
    >
      <label>
        Código
        <input v-model="code" required placeholder="Ex.: MATEMATICA" />
      </label>

      <label>
        Nome
        <input v-model="name" required placeholder="Ex.: Matemática" />
      </label>

      <label class="wideField">
        Descrição
        <textarea
          v-model="description"
          rows="2"
          placeholder="Opcional"
        />
      </label>

      <button type="submit">Criar matéria deste contexto</button>
    </form>

    <div v-if="selectedContextId" class="studentSubjectList">
      <button
        v-for="subject in subjects"
        :key="subject.studentSubjectId"
        type="button"
        class="subjectChoice"
        :data-selected="subject.studentSubjectId === selectedSubjectId"
        @click="emit('selectSubject', subject)"
      >
        <span>
          <strong>{{ subject.name }}</strong>
          <small>{{ subject.code }}</small>
        </span>
        <span data-status="ONLINE">{{ subject.status }}</span>
      </button>

      <p v-if="subjects.length === 0" class="emptyState">
        Nenhuma matéria criada para este aluno neste contexto.
      </p>
    </div>

    <section v-else class="workspaceEmptyState compactEmptyState">
      <p>Selecione um contexto ativo do aluno.</p>
    </section>
  </section>
</template>
