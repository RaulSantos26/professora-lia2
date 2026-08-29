<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import ExerciseRunner from './exerciseRunner.vue'
import MindMapView from './mindMapView.vue'

import type {
  LearningAttemptContract,
  PedagogicalArtifactContract
} from '../contracts/pedagogicalContract'

const props = defineProps<{
  artifact: PedagogicalArtifactContract
  attempt: LearningAttemptContract | null
  busy: boolean
}>()

const emit = defineEmits<{
  submitAttempt: [answers: Record<string, string>]
}>()

const revealedCards = ref<Set<string>>(new Set())

watch(
  () => props.artifact.pedagogicalArtifactId,
  () => {
    revealedCards.value = new Set()
  }
)

const content = computed(
  () => props.artifact.content ?? {}
)

const sections = computed(
  () => (
    Array.isArray(content.value.sections)
      ? content.value.sections as Array<{
          heading: string
          body: string
          evidenceRefs?: number[]
        }>
      : []
  )
)

const keyPoints = computed(
  () => (
    Array.isArray(content.value.keyPoints)
      ? content.value.keyPoints as string[]
      : []
  )
)

const cards = computed(
  () => (
    Array.isArray(content.value.cards)
      ? content.value.cards as Array<{
          cardId: string
          front: string
          back: string
        }>
      : []
  )
)

function toggleCard(cardId: string) {
  const next = new Set(revealedCards.value)

  if (next.has(cardId)) {
    next.delete(cardId)
  } else {
    next.add(cardId)
  }

  revealedCards.value = next
}
</script>

<template>
  <section class="pedagogicalArtifactRenderer">
    <template
      v-if="
        artifact.artifactType === 'TEACH'
        || artifact.artifactType === 'EXPLAIN'
        || artifact.artifactType === 'SUMMARY'
      "
    >
      <p
        v-if="String(content.intro ?? '')"
        class="pedagogicalIntro"
      >
        {{ content.intro }}
      </p>

      <article
        v-for="section in sections"
        :key="section.heading"
        class="pedagogicalTextSection"
      >
        <h4>{{ section.heading }}</h4>
        <p>{{ section.body }}</p>
      </article>

      <section
        v-if="keyPoints.length > 0"
        class="keyPointsCard"
      >
        <h4>Pontos principais</h4>
        <ul>
          <li
            v-for="point in keyPoints"
            :key="point"
          >
            {{ point }}
          </li>
        </ul>
      </section>
    </template>

    <MindMapView
      v-else-if="artifact.artifactType === 'MIND_MAP'"
      :content="content"
    />

    <div
      v-else-if="artifact.artifactType === 'FLASHCARDS'"
      class="flashcardGrid"
    >
      <button
        v-for="card in cards"
        :key="card.cardId"
        type="button"
        class="flashcard"
        @click="toggleCard(card.cardId)"
      >
        <span class="flashcardLabel">
          {{
            revealedCards.has(card.cardId)
              ? 'Resposta'
              : 'Pergunta'
          }}
        </span>

        <strong>
          {{
            revealedCards.has(card.cardId)
              ? card.back
              : card.front
          }}
        </strong>

        <small>Toque para virar</small>
      </button>
    </div>

    <ExerciseRunner
      v-else-if="
        artifact.artifactType === 'EXERCISES'
        || artifact.artifactType === 'QUIZ'
      "
      :content="content"
      :attempt="attempt"
      :busy="busy"
      @submit="emit('submitAttempt', $event)"
    />
  </section>
</template>
