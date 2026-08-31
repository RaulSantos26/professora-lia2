<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'

import type { ImageGenerationTaskContract } from '../contracts/imageGenerationContract'

const props = defineProps<{ task: ImageGenerationTaskContract }>()
const fullscreen = ref(false)

const contextLabels = computed(
  () => props.task.labels.filter(label => !label.startsWith('Explicação visual:'))
)
const explanation = computed(
  () => props.task.labels.find(label => label.startsWith('Explicação visual:')) ?? null
)

function openFullscreen() {
  fullscreen.value = true
}

function closeFullscreen() {
  fullscreen.value = false
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') closeFullscreen()
}

window.addEventListener('keydown', handleKeydown)
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown))
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
    <div v-if="task.status !== 'READY' && task.status !== 'ERROR' && task.status !== 'CANCELLED'" class="operationProgressTrack">
      <div class="operationProgressValue" :style="{ width: `${task.progressPercent}%` }" />
    </div>

    <button
      v-if="task.status === 'READY' && task.assetUrl"
      type="button"
      class="imagePreview"
      :aria-label="`Abrir ${task.title} em tela cheia`"
      @click="openFullscreen"
    >
      <img :src="task.assetUrl" :alt="task.title" class="didacticImage" />
      <span>Abrir imagem em tela cheia</span>
    </button>

    <p v-if="task.status === 'ERROR'" class="emptyState">{{ task.errorMessage ?? task.message }}</p>

    <section v-if="task.status === 'READY' && task.labels.length" class="imageExplanation">
      <h5>Explicação da Lia</h5>
      <p v-if="explanation">{{ explanation.replace('Explicação visual: ', '') }}</p>
      <ul>
        <li v-for="label in contextLabels" :key="label">{{ label }}</li>
      </ul>
    </section>
  </article>

  <Teleport to="body">
    <section
      v-if="fullscreen && task.assetUrl"
      class="imageFullscreen"
      role="dialog"
      aria-modal="true"
      :aria-label="task.title"
      @click.self="closeFullscreen"
    >
      <div class="imageFullscreenContent">
        <header>
          <div>
            <p class="eyebrow">ILUSTRAÇÃO DIDÁTICA</p>
            <h3>{{ task.title }}</h3>
          </div>
          <button type="button" class="closeFullscreen" @click="closeFullscreen">Fechar</button>
        </header>
        <img :src="task.assetUrl" :alt="task.title" class="imageFullscreenImage" />
        <section class="fullscreenExplanation">
          <h4>Explicação da Lia</h4>
          <p v-if="explanation">{{ explanation.replace('Explicação visual: ', '') }}</p>
          <ul>
            <li v-for="label in contextLabels" :key="label">{{ label }}</li>
          </ul>
        </section>
      </div>
    </section>
  </Teleport>
</template>

<style scoped>
.imagePreview { display: block; width: 100%; margin-top: 12px; padding: 0; overflow: hidden; border: 1px solid #cbdcf4; border-radius: 12px; background: #f8fbff; color: #12315a; cursor: pointer; text-align: left; }
.didacticImage { display: block; width: 100%; max-height: 460px; object-fit: contain; background: #f6f9fc; }
.imagePreview span { display: block; padding: 9px 12px; font-size: .82rem; font-weight: 700; }
.imageExplanation { margin-top: 12px; padding: 12px; border-left: 4px solid #346ddb; border-radius: 8px; background: #f4f8ff; }
.imageExplanation h5, .imageExplanation p { margin: 0 0 7px; }
.imageExplanation ul { margin: 0; padding-left: 20px; }
.imageFullscreen { position: fixed; z-index: 3000; inset: 0; display: grid; place-items: center; padding: 20px; background: rgb(5 16 34 / 82%); }
.imageFullscreenContent { width: min(1180px, 100%); max-height: calc(100vh - 40px); overflow: auto; padding: 20px; border-radius: 16px; background: #fff; box-shadow: 0 20px 60px rgb(0 0 0 / 35%); }
.imageFullscreenContent > header { display: flex; align-items: start; justify-content: space-between; gap: 16px; margin-bottom: 14px; }
.imageFullscreenContent h3, .imageFullscreenContent h4 { margin: 0; }
.closeFullscreen { padding: 8px 12px; border: 1px solid #183e72; border-radius: 8px; background: #fff; color: #12315a; font-weight: 700; cursor: pointer; }
.imageFullscreenImage { display: block; width: 100%; max-height: 68vh; object-fit: contain; background: #f5f8fc; }
.fullscreenExplanation { margin-top: 14px; padding: 14px; border-radius: 10px; background: #f4f8ff; }
.fullscreenExplanation p { margin: 8px 0; }
.fullscreenExplanation ul { margin: 0; padding-left: 22px; }
@media (max-width: 640px) { .imageFullscreen { padding: 8px; } .imageFullscreenContent { max-height: calc(100vh - 16px); padding: 14px; } .imageFullscreenContent > header { align-items: center; } .imageFullscreenImage { max-height: 58vh; } }
</style>
