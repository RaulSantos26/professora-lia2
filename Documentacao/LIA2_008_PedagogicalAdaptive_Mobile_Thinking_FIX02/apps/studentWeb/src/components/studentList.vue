<script setup lang="ts">
import type { StudentContract } from '../contracts/studentContract'

defineProps<{
  students: StudentContract[]
  selectedStudentId: string | null
}>()

const emit = defineEmits<{
  select: [student: StudentContract]
}>()
</script>

<template>
  <section class="contentCard">
    <div class="sectionHeader">
      <div>
        <p class="eyebrow">STUDENT</p>
        <h2>Alunos cadastrados</h2>
      </div>
      <span class="countBadge">{{ students.length }}</span>
    </div>

    <p v-if="students.length === 0" class="emptyState">
      Nenhum aluno cadastrado na Lia 2.0.
    </p>

    <div v-else class="studentList">
      <button
        v-for="student in students"
        :key="student.studentId"
        type="button"
        class="studentRow"
        :data-selected="student.studentId === selectedStudentId"
        @click="emit('select', student)"
      >
        <span>
          <strong>{{ student.preferredName || student.fullName }}</strong>
          <small>{{ student.fullName }}</small>
        </span>
        <span class="statusText">{{ student.status }}</span>
      </button>
    </div>
  </section>
</template>
