<script setup lang="ts">
import { ref } from 'vue'
import type { ReadingGuide } from './imageReadingGuide'
defineProps<{ src: string; alt: string; guide: ReadingGuide | null; maxHeight?: string }>()
const ratio = ref(4 / 3)
function loaded(event: Event) { const img = event.target as HTMLImageElement; if (img.naturalHeight) ratio.value = img.naturalWidth / img.naturalHeight }
</script>
<template>
  <div class="guidedFigure" :style="{ maxWidth: `calc(${maxHeight || '460px'} * ${ratio})` }">
    <img :src="src" :alt="alt" @load="loaded" />
    <template v-for="(step, index) in guide?.steps || []" :key="index">
      <span v-if="step.x !== null && step.y !== null" class="readingMarker" aria-hidden="true" :style="{ left: step.x + '%', top: step.y + '%' }">{{ index + 1 }}</span>
    </template>
  </div>
</template>
<style scoped>
.guidedFigure { position: relative; width: 100%; margin: auto; }
.guidedFigure img { display: block; width: 100%; height: auto; }
.readingMarker { position: absolute; transform: translate(-50%, -50%); width: 27px; height: 27px; display: grid; place-items: center; border-radius: 50%; background: #102e5b; color: white; border: 2px solid white; box-shadow: 0 1px 5px #0008; font: bold 15px sans-serif; pointer-events: none; }
</style>
