<script setup lang="ts">
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
</script>

<template>
  <nav
    class="workspaceNavigation"
    aria-label="Navegação do Learning Workspace"
  >
    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'STUDENT'"
      @click="emit('select','STUDENT')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">STUDENT</small>
        <strong>Alunos</strong>
        <span>{{ studentSummary }}</span>
      </span>
      <span class="countBadge">{{ studentCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'ACADEMIC_STAGE'"
      :data-recommended="recommendedSection === 'ACADEMIC_STAGE'"
      @click="emit('select','ACADEMIC_STAGE')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">ACADEMIC STAGE</small>
        <strong>Etapa</strong>
        <span>{{ academicStageSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'ACADEMIC_STAGE'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ academicStageCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'LEARNING_CONTEXT'"
      :data-recommended="recommendedSection === 'LEARNING_CONTEXT'"
      @click="emit('select','LEARNING_CONTEXT')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">LEARNING CONTEXT</small>
        <strong>Contextos</strong>
        <span>{{ learningContextSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'LEARNING_CONTEXT'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ learningContextCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'SUBJECT'"
      :data-recommended="recommendedSection === 'SUBJECT'"
      @click="emit('select','SUBJECT')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">SUBJECT</small>
        <strong>Matérias</strong>
        <span>{{ subjectSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'SUBJECT'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ subjectCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'LEARNING_UNIT'"
      :data-recommended="recommendedSection === 'LEARNING_UNIT'"
      @click="emit('select','LEARNING_UNIT')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">LEARNING UNIT</small>
        <strong>Unidades</strong>
        <span>{{ learningUnitSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'LEARNING_UNIT'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ learningUnitCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'MATERIAL'"
      :data-recommended="recommendedSection === 'MATERIAL'"
      @click="emit('select','MATERIAL')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">CONTENT & MATERIAL</small>
        <strong>Materiais</strong>
        <span>{{ materialSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'MATERIAL'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ materialCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard pedagogicalNavigationCard"
      :data-active="activeSection === 'PEDAGOGICAL'"
      :data-recommended="recommendedSection === 'PEDAGOGICAL'"
      @click="emit('select','PEDAGOGICAL')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">PEDAGOGICAL ENGINE</small>
        <strong>Estudar</strong>
        <span>{{ pedagogicalSummary }}</span>
      </span>
      <span
        v-if="recommendedSection === 'PEDAGOGICAL'"
        class="nextBadge"
      >
        PRÓXIMO
      </span>
      <span v-else class="countBadge">
        {{ pedagogicalCount }}
      </span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'LEARNING_GOAL'"
      :data-recommended="recommendedSection === 'LEARNING_GOAL'"
      @click="emit('select','LEARNING_GOAL')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">LEARNING GOAL</small>
        <strong>Objetivos</strong>
        <span>{{ learningGoalSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'LEARNING_GOAL'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ learningGoalCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'STUDY_SCOPE'"
      :data-recommended="recommendedSection === 'STUDY_SCOPE'"
      @click="emit('select','STUDY_SCOPE')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">STUDY SCOPE</small>
        <strong>Escopos</strong>
        <span>{{ studyScopeSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'STUDY_SCOPE'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ studyScopeCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'STUDY_SESSION'"
      :data-recommended="recommendedSection === 'STUDY_SESSION'"
      @click="emit('select','STUDY_SESSION')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">STUDY SESSION</small>
        <strong>Sessões</strong>
        <span>{{ studySessionSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'STUDY_SESSION'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ studySessionCount }}</span>
    </button>

    <button
      type="button"
      class="workspaceNavigationCard"
      :data-active="activeSection === 'LEARNING_PROGRESS'"
      :data-recommended="recommendedSection === 'LEARNING_PROGRESS'"
      @click="emit('select','LEARNING_PROGRESS')"
    >
      <span class="workspaceNavigationText">
        <small class="eyebrow">LEARNING STATE</small>
        <strong>Progresso</strong>
        <span>{{ learningProgressSummary }}</span>
      </span>
      <span v-if="recommendedSection === 'LEARNING_PROGRESS'" class="nextBadge">PRÓXIMO</span>
      <span v-else class="countBadge">{{ learningProgressCount }}</span>
    </button>
  </nav>
</template>
