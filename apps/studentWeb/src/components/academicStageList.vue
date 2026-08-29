<script setup lang="ts">
import type { AcademicStageContract } from '../contracts/academicStageContract'

defineProps<{
  stages: AcademicStageContract[]
}>()
</script>

<template>
  <section class="contentCard">
    <div class="sectionHeader">
      <div>
        <p class="eyebrow">HISTÓRICO</p>
        <h2>Etapas acadêmicas</h2>
      </div>
      <span class="countBadge">{{ stages.length }}</span>
    </div>

    <p v-if="stages.length === 0" class="emptyState">
      Nenhuma etapa acadêmica registrada.
    </p>

    <div v-else class="stageList">
      <article
        v-for="stage in stages"
        :key="stage.academicStageId"
        class="stageRow"
      >
        <div>
          <strong>{{ stage.stageLabel }}</strong>
          <p>{{ stage.educationLevel }}</p>
          <small v-if="stage.startedAt || stage.endedAt">
            {{ stage.startedAt || '—' }} → {{ stage.endedAt || 'atual' }}
          </small>
        </div>

        <span :data-status="stage.status === 'CURRENT' ? 'ONLINE' : 'NEUTRAL'">
          {{ stage.status }}
        </span>
      </article>
    </div>
  </section>
</template>
