<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import type {
  LearningAttemptContract
} from '../contracts/pedagogicalContract'

const props = defineProps<{
  content: Record<string, unknown>
  attempt: LearningAttemptContract | null
  busy: boolean
}>()

const emit = defineEmits<{
  submit: [answers: Record<string, string>]
}>()

interface Question {
  questionId: string
  questionType: 'MULTIPLE_CHOICE' | 'TRUE_FALSE'
  prompt: string
  options: string[]
  difficulty: string
  evidenceRefs?: number[]
}

const answers = reactive<Record<string, string>>({})

const questions = computed(
  () => (
    Array.isArray(props.content.questions)
      ? props.content.questions as Question[]
      : []
  )
)

watch(
  () => props.content,
  () => {
    for (const key of Object.keys(answers)) {
      delete answers[key]
    }
  }
)

const complete = computed(
  () => (
    questions.value.length > 0
    && questions.value.every(
      question => Boolean(answers[question.questionId])
    )
  )
)

function resultFor(questionId: string) {
  return props.attempt?.results.find(
    result => result.questionId === questionId
  ) ?? null
}
</script>

<template>
  <div class="exerciseRunner">
    <article
      v-if="attempt"
      class="attemptScoreCard"
    >
      <strong>{{ attempt.scorePercent }}%</strong>
      <span>
        {{ attempt.correctCount }}/{{ attempt.totalCount }} corretas
      </span>
      <p>{{ attempt.adaptiveMessage }}</p>
    </article>

    <article
      v-for="(question, index) in questions"
      :key="question.questionId"
      class="exerciseQuestion"
      :data-result="
        resultFor(question.questionId)
          ? (
            resultFor(question.questionId)?.correct
              ? 'CORRECT'
              : 'WRONG'
          )
          : 'PENDING'
      "
    >
      <div class="exerciseQuestionHeader">
        <span>Questão {{ index + 1 }}</span>
        <small>{{ question.difficulty }}</small>
      </div>

      <p class="exercisePrompt">
        {{ question.prompt }}
      </p>

      <div class="exerciseOptions">
        <label
          v-for="option in question.options"
          :key="option"
          class="exerciseOption"
        >
          <input
            v-model="answers[question.questionId]"
            type="radio"
            :name="question.questionId"
            :value="option"
            :disabled="Boolean(attempt)"
          />
          <span>{{ option }}</span>
        </label>
      </div>

      <div
        v-if="resultFor(question.questionId)"
        class="questionFeedback"
      >
        <strong>
          {{
            resultFor(question.questionId)?.correct
              ? 'Correto'
              : 'Vamos revisar este ponto'
          }}
        </strong>

        <p>
          Resposta correta:
          {{ resultFor(question.questionId)?.correctAnswer }}
        </p>

        <p>
          {{ resultFor(question.questionId)?.explanation }}
        </p>
      </div>
    </article>

    <button
      v-if="!attempt"
      type="button"
      class="primaryStudyAction"
      :disabled="!complete || busy"
      @click="emit('submit', { ...answers })"
    >
      {{ busy ? 'Corrigindo...' : 'Corrigir atividade' }}
    </button>
  </div>
</template>
