<script setup lang="ts">
defineProps<{
  student: string
  academicStage: string
  learningContext: string
  subject: string
}>()
</script>

<template>
  <section class="workspaceContextBar" aria-label="Contexto educacional atual">
    <div class="workspaceContextItem">
      <span>Aluno</span>
      <strong>{{ student }}</strong>
    </div>

    <div class="workspaceContextItem">
      <span>Etapa</span>
      <strong>{{ academicStage }}</strong>
    </div>

    <div class="workspaceContextItem">
      <span>Contexto</span>
      <strong>{{ learningContext }}</strong>
    </div>

    <div class="workspaceContextItem">
      <span>Matéria</span>
      <strong>{{ subject }}</strong>
    </div>
  </section>
</template>
