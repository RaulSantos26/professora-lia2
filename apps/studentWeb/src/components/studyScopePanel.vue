<script setup lang="ts">
import { ref } from 'vue'
import type { LearningGoalContract } from '../contracts/learningGoalContract'
import type { StudyScopeContract, StudyScopeCreateContract } from '../contracts/studyScopeContract'
import type { StudyScopeCandidateContract } from '../contracts/studyScopeItemContract'

defineProps<{
  goal: LearningGoalContract | null
  scopes: StudyScopeContract[]
  selectedScopeId: string | null
  candidates: StudyScopeCandidateContract[]
}>()

const emit = defineEmits<{
  createScope: [payload: StudyScopeCreateContract]
  selectScope: [scope: StudyScopeContract]
  addUnit: [unitId: string]
  removeUnit: [itemId: string]
}>()

const name = ref('')
const description = ref('')

function submit() {
  if (name.value.trim().length < 2) return
  emit('createScope', {
    contractName: 'StudyScopeCreate.v1',
    name: name.value.trim(),
    description: description.value.trim() || null
  })
  name.value = ''
  description.value = ''
}
</script>

<template>
  <section class="workspaceFeaturePanel">
    <div class="workspaceFeatureHeader">
      <div>
        <p class="eyebrow">STUDY SCOPE</p>
        <h2>Escopo de estudo</h2>
        <p v-if="goal">{{ goal.title }}</p>
      </div>
      <span class="countBadge">{{ scopes.length }}</span>
    </div>

    <section v-if="!goal" class="workspaceEmptyState compactEmptyState">
      <h3>Selecione um objetivo</h3>
      <p>O escopo reúne várias unidades para um mesmo objetivo.</p>
    </section>

    <template v-else>
      <div class="workspacePanelGrid">
        <form class="formCard workspaceEmbeddedCard" @submit.prevent="submit">
          <label>
            Nome
            <input v-model="name" required placeholder="Ex.: Conteúdo da prova" />
          </label>
          <label>
            Descrição
            <textarea v-model="description" rows="3" placeholder="Opcional" />
          </label>
          <button type="submit">Criar escopo</button>
        </form>

        <div class="workspaceListCard">
          <p v-if="scopes.length === 0" class="emptyState">
            Nenhum escopo criado.
          </p>
          <button
            v-for="scope in scopes"
            :key="scope.studyScopeId"
            type="button"
            class="workspaceSelectableRow"
            :data-selected="scope.studyScopeId === selectedScopeId"
            @click="emit('selectScope', scope)"
          >
            <span>
              <strong>{{ scope.name }}</strong>
              <small>{{ scope.status }}</small>
            </span>
          </button>
        </div>
      </div>

      <section v-if="selectedScopeId" class="scopeCandidateSection">
        <div class="sectionHeader">
          <div>
            <p class="eyebrow">UNIDADES</p>
            <h3>Conteúdo do escopo</h3>
          </div>
          <span class="countBadge">
            {{ candidates.filter(item => item.isSelected).length }}
          </span>
        </div>

        <p v-if="candidates.length === 0" class="emptyState">
          Nenhuma unidade disponível para este objetivo.
        </p>

        <article
          v-for="candidate in candidates"
          :key="candidate.studentLearningUnitId"
          class="scopeCandidateRow"
        >
          <div>
            <strong>{{ candidate.unitTitle }}</strong>
            <p>
              {{ candidate.contextName }} · {{ candidate.subjectName }}
              · {{ candidate.unitCode }}
            </p>
          </div>

          <button
            v-if="!candidate.isSelected"
            type="button"
            @click="emit('addUnit', candidate.studentLearningUnitId)"
          >
            Adicionar
          </button>

          <button
            v-else
            type="button"
            class="secondaryButton"
            @click="candidate.studyScopeItemId && emit('removeUnit', candidate.studyScopeItemId)"
          >
            Remover
          </button>
        </article>
      </section>
    </template>
  </section>
</template>
