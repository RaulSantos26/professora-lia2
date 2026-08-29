<script setup lang="ts">
import type { OperationalEventContract } from '../contracts/operationContract'

defineProps<{
  events: OperationalEventContract[]
}>()
</script>

<template>
  <section class="operationsCard">
    <h2>Últimas operações</h2>

    <p v-if="events.length === 0">
      Nenhuma operação administrativa registrada nesta Foundation.
    </p>

    <div v-else class="eventList">
      <article
        v-for="event in events"
        :key="event.eventId"
        class="eventRow"
      >
        <div>
          <strong>{{ event.action }} · {{ event.target }}</strong>
          <p>{{ new Date(event.finishedAt).toLocaleString('pt-BR') }}</p>
        </div>
        <strong :data-status="event.status === 'SUCCESS' ? 'ONLINE' : 'OFFLINE'">
          {{ event.status }}
        </strong>
      </article>
    </div>
  </section>
</template>
