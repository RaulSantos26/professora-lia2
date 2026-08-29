<script setup lang="ts">
import { ref } from 'vue'

import type { SubjectCreateContract } from '../contracts/subjectContract'

const emit = defineEmits<{
  create: [payload: SubjectCreateContract]
}>()

const code = ref('')
const name = ref('')
const description = ref('')

function submit() {
  if (code.value.trim().length < 2 || name.value.trim().length < 2) {
    return
  }

  emit('create', {
    contractName: 'SubjectCreate.v1',
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
  <form class="formCard" @submit.prevent="submit">
    <div>
      <p class="eyebrow">SUBJECT</p>
      <h2>Criar matéria</h2>
    </div>

    <label>
      Código
      <input v-model="code" required placeholder="Ex.: MATEMATICA" />
    </label>

    <label>
      Nome
      <input v-model="name" required placeholder="Ex.: Matemática" />
    </label>

    <label>
      Descrição
      <textarea
        v-model="description"
        rows="3"
        placeholder="Opcional"
      />
    </label>

    <button type="submit">Criar matéria</button>
  </form>
</template>
