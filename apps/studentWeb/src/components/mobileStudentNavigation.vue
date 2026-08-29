<script setup lang="ts">
import type {
  EducationWorkspaceSection
} from '../types/educationWorkspaceSection'

defineProps<{
  activeSection: EducationWorkspaceSection
  hasStudent: boolean
}>()

const emit = defineEmits<{
  select: [section: EducationWorkspaceSection]
}>()

const items: Array<{
  section: EducationWorkspaceSection
  icon: string
  label: string
}> = [
  {
    section: 'STUDENT',
    icon: '⌂',
    label: 'Início'
  },
  {
    section: 'MATERIAL',
    icon: '▣',
    label: 'Materiais'
  },
  {
    section: 'PEDAGOGICAL',
    icon: '✦',
    label: 'Estudar'
  },
  {
    section: 'LIA_TUTOR',
    icon: '●',
    label: 'Lia'
  },
  {
    section: 'LEARNING_PROGRESS',
    icon: '↗',
    label: 'Progresso'
  }
]
</script>

<template>
  <nav
    class="mobileStudentNavigation"
    aria-label="Navegação principal do aluno"
  >
    <button
      v-for="item in items"
      :key="`${item.section}-${item.label}`"
      type="button"
      :data-active="activeSection === item.section"
      :disabled="!hasStudent && item.section !== 'STUDENT'"
      @click="emit('select', item.section)"
    >
      <span aria-hidden="true">{{ item.icon }}</span>
      <small>{{ item.label }}</small>
    </button>
  </nav>
</template>
