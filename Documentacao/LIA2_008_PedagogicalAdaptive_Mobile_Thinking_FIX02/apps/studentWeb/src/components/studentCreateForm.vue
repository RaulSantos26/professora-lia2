<script setup lang="ts">
import { ref } from 'vue'

import type { StudentCreateContract } from '../contracts/studentContract'

const emit = defineEmits<{
  create: [payload: StudentCreateContract]
}>()

const fullName = ref('')
const preferredName = ref('')

function submit() {
  const normalizedFullName = fullName.value.trim()

  if (normalizedFullName.length < 2) {
    return
  }

  emit('create', {
    contractName: 'StudentCreate.v1',
    fullName: normalizedFullName,
    preferredName: preferredName.value.trim() || null
  })

  fullName.value = ''
  preferredName.value = ''
}
</script>

<template>
  <form class="formCard" @submit.prevent="submit">
    <div>
      <p class="eyebrow">ALUNO</p>
      <h2>Cadastrar aluno</h2>
    </div>

    <label>
      Nome completo
      <input
        v-model="fullName"
        required
        minlength="2"
        maxlength="200"
        placeholder="Nome do aluno"
      />
    </label>

    <label>
      Nome preferido
      <input
        v-model="preferredName"
        maxlength="120"
        placeholder="Opcional"
      />
    </label>

    <button type="submit">Cadastrar aluno</button>
  </form>
</template>
