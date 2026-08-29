<script setup lang="ts">
import { ref } from 'vue'
import type { StudyScopeContract } from '../contracts/studyScopeContract'
import type {
  StudySessionType,
  StudySessionViewContract
} from '../contracts/studySessionContract'

defineProps<{
  scope: StudyScopeContract | null
  sessions: StudySessionViewContract[]
}>()

const emit = defineEmits<{
  start: [sessionType: StudySessionType]
  complete: [studySessionId: string]
}>()

const sessionType = ref<StudySessionType>('STUDY')
</script>

<template>
  <section class="workspaceFeaturePanel">
    <div class="workspaceFeatureHeader">
      <div>
        <p class="eyebrow">STUDY SESSION</p>
        <h2>Sessões de estudo</h2>
        <p v-if="scope">{{ scope.name }}</p>
      </div>
      <span class="countBadge">{{ sessions.length }}</span>
    </div>

    <section v-if="!scope" class="workspaceEmptyState compactEmptyState">
      <h3>Selecione um escopo</h3>
    </section>

    <template v-else>
      <div class="sessionActionBar">
        <label>
          Tipo
          <select v-model="sessionType">
            <option value="STUDY">Estudo</option>
            <option value="REVIEW">Revisão</option>
            <option value="PRACTICE">Prática</option>
            <option value="MOCK_EXAM">Simulado</option>
          </select>
        </label>
        <button type="button" @click="emit('start', sessionType)">
          Iniciar sessão
        </button>
      </div>

      <div class="sessionList">
        <article
          v-for="item in sessions"
          :key="item.session.studySessionId"
          class="sessionRow"
        >
          <div>
            <strong>
              {{ item.session.sessionType }} · {{ item.items.length }} unidade(s)
            </strong>
            <p>{{ new Date(item.session.startedAt).toLocaleString() }}</p>
          </div>
          <div class="sessionRowActions">
            <span
              :data-status="item.session.status === 'COMPLETED' ? 'ONLINE' : 'NEUTRAL'"
            >
              {{ item.session.status }}
            </span>
            <button
              v-if="item.session.status === 'IN_PROGRESS'"
              type="button"
              @click="emit('complete', item.session.studySessionId)"
            >
              Concluir
            </button>
          </div>
        </article>

        <p v-if="sessions.length === 0" class="emptyState">
          Nenhuma sessão iniciada.
        </p>
      </div>
    </template>
  </section>
</template>
