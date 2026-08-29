<script setup lang="ts">
import { ref } from 'vue'

import type {
  StudentLearningUnitContract,
  StudentLearningUnitCreateContract,
  StudentLearningUnitType
} from '../contracts/studentLearningUnitContract'
import type {
  StudentSubjectContract
} from '../contracts/studentSubjectContract'

defineProps<{
  subject: StudentSubjectContract | null
  units: StudentLearningUnitContract[]
}>()

const emit = defineEmits<{
  create: [payload: StudentLearningUnitCreateContract]
}>()

const unitType = ref<StudentLearningUnitType>('LESSON')
const code = ref('')
const title = ref('')
const description = ref('')

function submit() {
  if (code.value.trim().length < 2 || title.value.trim().length < 2) {
    return
  }

  emit('create', {
    contractName: 'StudentLearningUnitCreate.v1',
    parentStudentLearningUnitId: null,
    unitType: unitType.value,
    code: code.value.trim(),
    title: title.value.trim(),
    description: description.value.trim() || null,
    displayOrder: null,
    status: 'ACTIVE'
  })

  code.value = ''
  title.value = ''
  description.value = ''
}
</script>

<template>
  <section class="studentSpecificPanel">
    <template v-if="subject">
      <div class="studentSpecificHeader">
        <div>
          <p class="eyebrow">STUDENT LEARNING UNIT</p>
          <h2>{{ subject.name }}</h2>
        </div>
        <span class="countBadge">{{ units.length }}</span>
      </div>

      <form class="inlineForm" @submit.prevent="submit">
        <label>
          Tipo
          <select v-model="unitType">
            <option value="LESSON">Lição</option>
            <option value="MODULE">Módulo</option>
            <option value="CHAPTER">Capítulo</option>
            <option value="SECTION">Seção</option>
          </select>
        </label>

        <label>
          Código
          <input v-model="code" required placeholder="Ex.: FUNCOES_01" />
        </label>

        <label>
          Título
          <input v-model="title" required placeholder="Ex.: Funções" />
        </label>

        <label class="wideField">
          Descrição
          <textarea v-model="description" rows="2" placeholder="Opcional" />
        </label>

        <button type="submit">Criar unidade deste aluno/contexto</button>
      </form>

      <div class="unitList">
        <article
          v-for="unit in units"
          :key="unit.studentLearningUnitId"
          class="unitRow"
        >
          <div>
            <strong>{{ unit.title }}</strong>
            <p>{{ unit.unitType }} · {{ unit.code }}</p>
          </div>
          <span :data-status="unit.status === 'ACTIVE' ? 'ONLINE' : 'NEUTRAL'">
            {{ unit.status }}
          </span>
        </article>
      </div>

      <p v-if="units.length === 0" class="emptyState">
        Nenhuma unidade criada para esta matéria.
      </p>
    </template>

    <template v-else>
      <section class="workspaceEmptyState">
        <h2>Selecione uma matéria do aluno</h2>
        <p>
          As unidades pertencem exclusivamente à matéria deste aluno/contexto.
        </p>
      </section>
    </template>
  </section>
</template>
