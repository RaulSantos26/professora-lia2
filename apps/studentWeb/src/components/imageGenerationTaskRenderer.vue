<script setup lang="ts">
import type { ImageGenerationTaskContract } from '../contracts/imageGenerationContract'

defineProps<{ task: ImageGenerationTaskContract }>()
</script>

<template>
  <article class="visualTaskCard imageGenerationCard">
    <header class="visualTaskHeader">
      <div>
        <p class="eyebrow">Z-IMAGE · {{ task.imageMode === 'MIND_MAP_COMPANION' ? 'MAPA ILUSTRADO' : 'ILUSTRAÇÃO' }}</p>
        <h4>{{ task.title }}</h4>
      </div>
      <span class="agentRunBadge">{{ task.progressPercent }}%</span>
    </header>
    <p v-if="task.status !== 'READY'">{{ task.message }}</p>
    <div class="operationProgressTrack" v-if="task.status !== 'READY' && task.status !== 'ERROR' && task.status !== 'CANCELLED'">
      <div class="operationProgressValue" :style="{ width: `${task.progressPercent}%` }" />
    </div>
    <img v-if="task.status === 'READY' && task.assetUrl" :src="task.assetUrl" :alt="task.title" class="didacticImage" />
    <p v-if="task.status === 'ERROR'" class="emptyState">{{ task.errorMessage ?? task.message }}</p>
    <ul v-if="task.status === 'READY' && task.labels.length" class="imageLabelList">
      <li v-for="label in task.labels" :key="label">{{ label }}</li>
    </ul>
  </article>
</template>

<style scoped>
.didacticImage { display: block; width: 100%; border-radius: 12px; margin-top: 12px; }
.imageLabelList { margin: 12px 0 0; padding-left: 20px; }
</style>
