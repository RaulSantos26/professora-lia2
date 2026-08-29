<script setup lang="ts">
import { ref } from 'vue'

import type { EducationWorkspaceSection } from '../types/educationWorkspaceSection'

defineProps<{
  activeSection: EducationWorkspaceSection
  recommendedSection: EducationWorkspaceSection | null
  studentSummary: string
  studentCount: number
  academicStageSummary: string
  academicStageCount: number
  learningContextSummary: string
  learningContextCount: number
  subjectSummary: string
  subjectCount: number
  learningUnitSummary: string
  learningUnitCount: number
  materialSummary: string
  materialCount: number
  pedagogicalSummary: string
  pedagogicalCount: number
  liaTutorSummary: string
  liaTutorCount: number
  learningGoalSummary: string
  learningGoalCount: number
  studyScopeSummary: string
  studyScopeCount: number
  studySessionSummary: string
  studySessionCount: number
  learningProgressSummary: string
  learningProgressCount: number
}>()

const emit = defineEmits<{
  select: [section: EducationWorkspaceSection]
}>()

const showOrganization = ref(false)
</script>

<template>
  <nav class="studentJourneyNav" aria-label="Jornada de estudo">
    <button
      type="button"
      class="journeyStudentButton"
      :data-active="activeSection === 'STUDENT'"
      @click="emit('select', 'STUDENT')"
    >
      <span aria-hidden="true">👤</span>
      <span>
        <small>ALUNA</small>
        <strong>{{ studentSummary }}</strong>
      </span>
    </button>

    <div class="journeyMainSteps">
      <button
        type="button"
        :data-active="
          activeSection === 'SUBJECT'
          || activeSection === 'LEARNING_UNIT'
        "
        :data-recommended="
          recommendedSection === 'SUBJECT'
          || recommendedSection === 'LEARNING_UNIT'
        "
        :disabled="studentCount === 0"
        @click="emit('select', 'SUBJECT')"
      >
        <span aria-hidden="true">📚</span>
        <span>
          <strong>Minhas lições</strong>
          <small>Escolher matéria e lição</small>
        </span>
      </button>

      <button
        type="button"
        :data-active="activeSection === 'MATERIAL'"
        :data-recommended="recommendedSection === 'MATERIAL'"
        :disabled="studentCount === 0"
        @click="emit('select', 'MATERIAL')"
      >
        <span aria-hidden="true">📷</span>
        <span>
          <strong>Materiais</strong>
          <small>Fotos e arquivos da lição</small>
        </span>
      </button>

      <button
        type="button"
        :data-active="activeSection === 'PEDAGOGICAL'"
        :data-recommended="recommendedSection === 'PEDAGOGICAL'"
        :disabled="studentCount === 0"
        @click="emit('select', 'PEDAGOGICAL')"
      >
        <span aria-hidden="true">✏️</span>
        <span>
          <strong>Estudar</strong>
          <small>Resumo, mapa e exercícios</small>
        </span>
      </button>

      <button
        type="button"
        :data-active="activeSection === 'LIA_TUTOR'"
        :data-recommended="recommendedSection === 'LIA_TUTOR'"
        :disabled="studentCount === 0"
        @click="emit('select', 'LIA_TUTOR')"
      >
        <span aria-hidden="true">💬</span>
        <span>
          <strong>Conversar com a Lia</strong>
          <small>Tirar dúvidas da lição</small>
        </span>
      </button>

      <button
        type="button"
        :data-active="activeSection === 'LEARNING_PROGRESS'"
        :disabled="studentCount === 0"
        @click="emit('select', 'LEARNING_PROGRESS')"
      >
        <span aria-hidden="true">🌱</span>
        <span>
          <strong>Meu progresso</strong>
          <small>Acompanhar a aprendizagem</small>
        </span>
      </button>
    </div>

    <button
      type="button"
      class="journeyOrganizationToggle"
      :aria-expanded="showOrganization"
      @click="showOrganization = !showOrganization"
    >
      Organização e planejamento
      <span aria-hidden="true">{{ showOrganization ? '⌃' : '⌄' }}</span>
    </button>

    <div v-if="showOrganization" class="journeyOrganization">
      <button type="button" @click="emit('select', 'ACADEMIC_STAGE')">
        Etapa escolar
      </button>
      <button type="button" @click="emit('select', 'LEARNING_CONTEXT')">
        Contextos de estudo
      </button>
      <button type="button" @click="emit('select', 'LEARNING_GOAL')">
        Objetivos
      </button>
      <button type="button" @click="emit('select', 'STUDY_SCOPE')">
        Plano de estudo
      </button>
      <button type="button" @click="emit('select', 'STUDY_SESSION')">
        Sessões
      </button>
    </div>
  </nav>
</template>
