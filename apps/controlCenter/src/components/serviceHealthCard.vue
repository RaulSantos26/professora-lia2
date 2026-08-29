<script setup lang="ts">
import type { ServiceStatusContract } from '../contracts/serviceStatusContract'

defineProps<{
  service: ServiceStatusContract
}>()
</script>

<template>
  <article class="serviceCard">
    <div>
      <p class="serviceName">{{ service.serviceName }}</p>
      <p v-if="service.version" class="serviceVersion">Versão {{ service.version }}</p>
    </div>

    <span
      class="serviceStatus"
      :data-status="service.status"
    >
      {{ service.status }}
    </span>
  </article>
</template>
