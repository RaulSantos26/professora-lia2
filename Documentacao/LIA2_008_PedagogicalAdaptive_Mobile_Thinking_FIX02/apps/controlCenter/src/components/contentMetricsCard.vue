<script setup lang="ts">
import type { ContentMetricsContract } from '../contracts/contentMetricsContract'

defineProps<{
  metrics: ContentMetricsContract
}>()
</script>

<template>
  <section class="contentMetricsCard">
    <div class="contentMetricsHeader">
      <div>
        <p class="eyebrow">CONTEÚDO, IA & PEDAGOGIA</p>
        <h2>Pipeline e aprendizagem</h2>
      </div>

      <span :data-status="metrics.available ? 'ONLINE' : 'OFFLINE'">
        {{ metrics.available ? 'ONLINE' : 'INDISPONÍVEL' }}
      </span>
    </div>

    <div v-if="metrics.available" class="contentMetricsGrid">
      <div><span>Alunos</span><strong>{{ metrics.students }}</strong></div>
      <div><span>Materiais</span><strong>{{ metrics.materials }}</strong></div>
      <div><span>Páginas</span><strong>{{ metrics.documentPages }}</strong></div>
      <div><span>Blocos texto</span><strong>{{ metrics.textBlocks }}</strong></div>

      <div>
        <span>Aguardando Vision</span>
        <strong>{{ metrics.visualPendingBlocks }}</strong>
      </div>

      <div>
        <span>Chunks indexados</span>
        <strong>{{ metrics.embeddedChunks }}</strong>
      </div>

      <div>
        <span>Chunks pendentes</span>
        <strong>{{ metrics.chunksPendingEmbedding }}</strong>
      </div>

      <div>
        <span>Jobs ativos</span>
        <strong>{{ metrics.processingJobs }}</strong>
      </div>

      <div>
        <span>Jobs com falha</span>
        <strong>{{ metrics.failedJobs }}</strong>
      </div>

      <div>
        <span>Objetivos ativos</span>
        <strong>{{ metrics.learningGoals }}</strong>
      </div>

      <div>
        <span>Sessões</span>
        <strong>{{ metrics.studySessions }}</strong>
      </div>

      <div>
        <span>Artefatos pedagógicos</span>
        <strong>{{ metrics.pedagogicalArtifacts }}</strong>
      </div>

      <div>
        <span>Gerações ativas</span>
        <strong>{{ metrics.pedagogicalJobsActive }}</strong>
      </div>

      <div>
        <span>Gerações com falha</span>
        <strong>{{ metrics.pedagogicalJobsFailed }}</strong>
      </div>

      <div>
        <span>Tentativas corrigidas</span>
        <strong>{{ metrics.learningAttempts }}</strong>
      </div>
    </div>

    <p v-else>
      Não foi possível ler as métricas do schema lia2.
      {{ metrics.errorType }}
    </p>
  </section>
</template>
