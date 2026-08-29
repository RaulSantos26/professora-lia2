<script setup lang="ts">
import { ref } from 'vue'

import type {
  LearningContextCreateContract,
  LearningContextType
} from '../contracts/learningContextContract'

const emit = defineEmits<{
  create: [payload: LearningContextCreateContract]
}>()

const contextType = ref<LearningContextType>('ENEM')
const code = ref('')
const name = ref('')
const description = ref('')
const startsAt = ref('')
const endsAt = ref('')

function submit() {
  if (code.value.trim().length < 2 || name.value.trim().length < 2) {
    return
  }

  emit('create', {
    contractName: 'LearningContextCreate.v1',
    contextType: contextType.value,
    code: code.value.trim(),
    name: name.value.trim(),
    description: description.value.trim() || null,
    startsAt: startsAt.value || null,
    endsAt: endsAt.value || null
  })

  code.value = ''
  name.value = ''
  description.value = ''
  startsAt.value = ''
  endsAt.value = ''
}
</script>

<template>
  <form class="formCard" @submit.prevent="submit">
    <div>
      <p class="eyebrow">LEARNING CONTEXT</p>
      <h2>Criar contexto de estudo</h2>
    </div>

    <label>
      Tipo
      <select v-model="contextType">
        <option value="REGULAR_EDUCATION">Ensino regular</option>
        <option value="ENEM">ENEM</option>
        <option value="VESTIBULAR">Vestibular</option>
        <option value="PUBLIC_EXAM">Concurso</option>
        <option value="GRADUATION">Graduação</option>
        <option value="POSTGRAD">Pós-graduação</option>
        <option value="FREE_COURSE">Curso livre</option>
        <option value="OTHER">Outro</option>
      </select>
    </label>

    <label>
      Código
      <input v-model="code" required placeholder="Ex.: ENEM_2026" />
    </label>

    <label>
      Nome
      <input v-model="name" required placeholder="Ex.: ENEM 2026" />
    </label>

    <label>
      Descrição
      <textarea
        v-model="description"
        rows="3"
        placeholder="Opcional"
      />
    </label>

    <div class="fieldGrid">
      <label>
        Início
        <input v-model="startsAt" type="date" />
      </label>

      <label>
        Fim
        <input v-model="endsAt" type="date" />
      </label>
    </div>

    <button type="submit">Criar contexto</button>
  </form>
</template>
