<script setup lang="ts">
import { ref } from 'vue'

import type { AcademicStageCreateContract } from '../contracts/academicStageContract'

const emit = defineEmits<{
  create: [payload: AcademicStageCreateContract]
}>()

const educationLevel = ref('')
const stageCode = ref('')
const stageLabel = ref('')
const startedAt = ref('')
const endedAt = ref('')
const status = ref<'CURRENT' | 'COMPLETED' | 'CANCELLED'>('CURRENT')

function submit() {
  if (educationLevel.value.trim().length < 2 || stageLabel.value.trim().length < 2) {
    return
  }

  emit('create', {
    contractName: 'AcademicStageCreate.v1',
    educationLevel: educationLevel.value.trim(),
    stageCode: stageCode.value.trim() || null,
    stageLabel: stageLabel.value.trim(),
    startedAt: startedAt.value || null,
    endedAt: endedAt.value || null,
    status: status.value
  })

  educationLevel.value = ''
  stageCode.value = ''
  stageLabel.value = ''
  startedAt.value = ''
  endedAt.value = ''
  status.value = 'CURRENT'
}
</script>

<template>
  <form class="formCard" @submit.prevent="submit">
    <div>
      <p class="eyebrow">ACADEMIC STAGE</p>
      <h2>Adicionar etapa acadêmica</h2>
    </div>

    <label>
      Nível educacional
      <input
        v-model="educationLevel"
        required
        maxlength="80"
        placeholder="Ex.: Ensino Fundamental"
      />
    </label>

    <label>
      Etapa
      <input
        v-model="stageLabel"
        required
        maxlength="160"
        placeholder="Ex.: 5º ano"
      />
    </label>

    <label>
      Código da etapa
      <input
        v-model="stageCode"
        maxlength="80"
        placeholder="Opcional"
      />
    </label>

    <div class="fieldGrid">
      <label>
        Início
        <input v-model="startedAt" type="date" />
      </label>

      <label>
        Fim
        <input v-model="endedAt" type="date" />
      </label>
    </div>

    <label>
      Situação
      <select v-model="status">
        <option value="CURRENT">Atual</option>
        <option value="COMPLETED">Concluída</option>
        <option value="CANCELLED">Cancelada</option>
      </select>
    </label>

    <button type="submit">Adicionar etapa</button>
  </form>
</template>
