<script setup lang="ts">
import { ref } from 'vue'

import type {
  LearningUnitContract,
  LearningUnitCreateContract,
  LearningUnitType
} from '../contracts/learningUnitContract'
import type {
  LearningContextSubjectViewContract
} from '../contracts/learningContextSubjectContract'

defineProps<{
  association: LearningContextSubjectViewContract | null
  units: LearningUnitContract[]
}>()

const emit = defineEmits<{
  create: [payload: LearningUnitCreateContract]
}>()

const unitType = ref<LearningUnitType>('LESSON')
const code = ref('')
const title = ref('')
const description = ref('')

function submit() {
  if (code.value.trim().length < 2 || title.value.trim().length < 2) {
    return
  }

  emit('create', {
    contractName: 'LearningUnitCreate.v1',
    parentLearningUnitId: null,
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
  <section class="contentCard">
    <template v-if="association">
      <div class="sectionHeader">
        <div>
          <p class="eyebrow">LEARNING UNIT</p>
          <h2>{{ association.subject.name }}</h2>
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

        <button type="submit">Criar unidade</button>
      </form>

      <div class="unitList">
        <article
          v-for="unit in units"
          :key="unit.learningUnitId"
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
        Nenhuma unidade criada nesta matéria/contexto.
      </p>
    </template>

    <template v-else>
      <h2>Unidades de aprendizagem</h2>
      <p class="emptyState">
        Selecione uma matéria vinculada para criar e visualizar unidades.
      </p>
    </template>
  </section>
</template>
