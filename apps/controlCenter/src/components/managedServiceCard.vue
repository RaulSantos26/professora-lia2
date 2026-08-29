<script setup lang="ts">
import type {
  ManagedServiceStatusContract,
  OperationAction
} from '../contracts/operationContract'

defineProps<{
  service: ManagedServiceStatusContract
  busy: boolean
}>()

const emit = defineEmits<{
  action: [serviceKey: 'backend' | 'studentWeb', action: OperationAction]
}>()

function displayName(serviceKey: string): string {
  return serviceKey === 'backend' ? 'Backend' : 'Student Web'
}
</script>

<template>
  <article class="managedServiceCard">
    <div>
      <p class="serviceName">{{ displayName(service.serviceKey) }}</p>
      <p class="serviceVersion">{{ service.containerName }}</p>
    </div>

    <div class="managedServiceActions">
      <strong :data-status="service.state === 'RUNNING' ? 'ONLINE' : 'OFFLINE'">
        {{ service.state }}
      </strong>

      <button
        :disabled="busy || service.state === 'RUNNING'"
        @click="emit('action', service.serviceKey, 'START')"
      >
        Subir
      </button>

      <button
        :disabled="busy || service.state !== 'RUNNING'"
        @click="emit('action', service.serviceKey, 'RESTART')"
      >
        Reiniciar
      </button>

      <button
        :disabled="busy || service.state !== 'RUNNING'"
        @click="emit('action', service.serviceKey, 'STOP')"
      >
        Parar
      </button>
    </div>
  </article>
</template>
