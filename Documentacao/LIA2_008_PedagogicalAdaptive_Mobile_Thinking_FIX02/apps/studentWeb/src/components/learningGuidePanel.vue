<script setup lang="ts">
import type { LearningGuideContract } from '../contracts/learningGuideContract'
import type { EducationWorkspaceSection } from '../types/educationWorkspaceSection'

defineProps<{
  guide: LearningGuideContract
}>()

const emit = defineEmits<{
  navigate: [section: EducationWorkspaceSection]
}>()
</script>

<template>
  <section class="learningGuide">
    <div class="learningGuidePrimary">
      <div class="learningGuideProgress">
        <span>
          {{ guide.completedSteps }}/{{ guide.totalSteps }} etapas concluídas
        </span>
        <div class="learningGuideProgressTrack">
          <div
            class="learningGuideProgressValue"
            :style="{
              width: `${Math.round(
                (guide.completedSteps / guide.totalSteps) * 100
              )}%`
            }"
          />
        </div>
      </div>

      <div class="learningGuideMessage">
        <p class="eyebrow">GUIA DA LIA</p>
        <h2>{{ guide.headline }}</h2>
        <p>{{ guide.message }}</p>
      </div>

      <button
        type="button"
        class="guideNextButton"
        @click="emit('navigate', guide.recommendedSection)"
      >
        Ir para o próximo passo
      </button>
    </div>

    <details class="learningGuideDetails">
      <summary>Ver roteiro completo</summary>

      <div class="learningGuideSteps">
        <button
          v-for="step in guide.steps"
          :key="step.section"
          type="button"
          class="learningGuideStep"
          :data-status="step.status"
          :disabled="step.status === 'BLOCKED'"
          @click="emit('navigate', step.section)"
        >
          <span class="guideStepIndicator">
            <template v-if="step.status === 'COMPLETE'">✓</template>
            <template v-else-if="step.status === 'NEXT'">→</template>
            <template v-else-if="step.status === 'OPTIONAL'">○</template>
            <template v-else>•</template>
          </span>

          <span class="guideStepText">
            <strong>{{ step.title }}</strong>
            <small>{{ step.description }}</small>
          </span>

          <span class="guideStepStatus">
            {{ step.status }}
          </span>
        </button>
      </div>
    </details>
  </section>
</template>
