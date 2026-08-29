<script setup lang="ts">
import AnimationCanvasRenderer from './animationCanvasRenderer.vue'
import ChartCanvasRenderer from './chartCanvasRenderer.vue'
import DiagramSvgRenderer from './diagramSvgRenderer.vue'
import InteractiveMindMapRenderer from './interactiveMindMapRenderer.vue'
import ThreeSceneRenderer from './threeSceneRenderer.vue'

import type {
  VisualTaskContract
} from '../contracts/visualTaskContract'

defineProps<{
  task: VisualTaskContract
}>()
</script>

<template>
  <article class="visualTaskCard">
    <header class="visualTaskHeader">
      <div>
        <p class="eyebrow">VISUAL LEARNING ENGINE</p>
        <h3>{{ task.title }}</h3>
        <small>
          {{ task.visualType }}
          · {{ task.renderer }}
          <template v-if="task.effectiveModelId">
            · {{ task.effectiveModelId }}
          </template>
          <template v-if="task.thinkingEnabled !== null">
            · Thinking {{ task.thinkingEnabled ? 'ON' : 'OFF' }}
          </template>
        </small>
      </div>
    </header>

    <InteractiveMindMapRenderer
      v-if="task.visualType === 'MIND_MAP'"
      :spec="task.spec"
    />

    <DiagramSvgRenderer
      v-else-if="task.visualType === 'DIAGRAM'"
      :spec="task.spec"
    />

    <ChartCanvasRenderer
      v-else-if="task.visualType === 'CHART'"
      :spec="task.spec"
    />

    <AnimationCanvasRenderer
      v-else-if="task.visualType === 'ANIMATION_2D'"
      :spec="task.spec"
    />

    <ThreeSceneRenderer
      v-else-if="task.visualType === 'SCENE_3D'"
      :spec="task.spec"
    />
  </article>
</template>
