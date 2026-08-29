<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

import AdminLoginCard from '../components/adminLoginCard.vue'
import ContentMetricsCard from '../components/contentMetricsCard.vue'
import ManagedServiceCard from '../components/managedServiceCard.vue'
import OperationalEventsCard from '../components/operationalEventsCard.vue'
import ServiceHealthCard from '../components/serviceHealthCard.vue'
import type {
  ManagedServiceKey,
  OperationalEventContract,
  OperationAction,
  OperationsStatusContract
} from '../contracts/operationContract'
import type { PlatformHealthContract } from '../contracts/serviceStatusContract'
import type { ContentMetricsContract } from '../contracts/contentMetricsContract'
import { AdminSessionService } from '../services/adminSessionService'
import { OperationsApiService } from '../services/operationsApiService'
import { PlatformHealthApiService } from '../services/platformHealthApiService'
import { ContentMetricsApiService } from '../services/contentMetricsApiService'

const platformHealthApiService = new PlatformHealthApiService()
const contentMetricsApiService = new ContentMetricsApiService()
const adminSessionService = new AdminSessionService()
const operationsApiService = new OperationsApiService(adminSessionService)

const health = ref<PlatformHealthContract | null>(null)
const contentMetrics = ref<ContentMetricsContract | null>(null)
const operationsStatus = ref<OperationsStatusContract | null>(null)
const operationalEvents = ref<OperationalEventContract[]>([])
const errorMessage = ref('')
const operationMessage = ref('')
const loading = ref(true)
const operationBusy = ref(false)
const authenticated = ref(adminSessionService.isAuthenticated())
let refreshTimer: number | undefined


async function refreshContentMetrics() {
  try {
    contentMetrics.value = await contentMetricsApiService.getMetrics()
  } catch {
    contentMetrics.value = null
  }
}

async function refreshHealth() {
  try {
    health.value = await platformHealthApiService.getHealth()
    errorMessage.value = ''
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Erro não identificado'
  } finally {
    loading.value = false
  }
}

async function refreshOperations() {
  if (!authenticated.value) {
    return
  }

  try {
    operationsStatus.value = await operationsApiService.getStatus()
    operationalEvents.value = await operationsApiService.listEvents(10)
  } catch (error) {
    if (error instanceof Error && error.message === 'ADMIN_TOKEN_INVALID') {
      adminSessionService.clearToken()
      authenticated.value = false
      operationsStatus.value = null
      operationalEvents.value = []
      operationMessage.value = 'Token administrativo inválido.'
      return
    }

    operationMessage.value = error instanceof Error
      ? error.message
      : 'Erro operacional não identificado.'
  }
}

async function authenticate(token: string) {
  adminSessionService.setToken(token)
  authenticated.value = true
  operationMessage.value = ''
  await refreshOperations()
}

async function executeApplicationAction(action: OperationAction) {
  operationBusy.value = true
  operationMessage.value = ''

  try {
    const event = await operationsApiService.executeApplicationAction(action)
    operationMessage.value = `${event.action} ${event.target}: ${event.status}`
    await refreshOperations()
    window.setTimeout(refreshHealth, 1200)
  } catch (error) {
    operationMessage.value = error instanceof Error
      ? error.message
      : 'Erro operacional não identificado.'
  } finally {
    operationBusy.value = false
  }
}

async function executeServiceAction(
  serviceKey: ManagedServiceKey,
  action: OperationAction
) {
  operationBusy.value = true
  operationMessage.value = ''

  try {
    const event = await operationsApiService.executeServiceAction(serviceKey, action)
    operationMessage.value = `${event.action} ${event.target}: ${event.status}`
    await refreshOperations()
    window.setTimeout(refreshHealth, 1200)
  } catch (error) {
    operationMessage.value = error instanceof Error
      ? error.message
      : 'Erro operacional não identificado.'
  } finally {
    operationBusy.value = false
  }
}

onMounted(async () => {
  await refreshHealth()
  await refreshContentMetrics()
  await refreshOperations()

  refreshTimer = window.setInterval(async () => {
    await refreshHealth()
    await refreshContentMetrics()
    await refreshOperations()
  }, 10000)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
  }
})
</script>

<template>
  <main class="controlShell">
    <header class="topBar">
      <div>
        <p class="eyebrow">LIA CONTROL CENTER</p>
        <h1>Visão operacional</h1>
      </div>

      <button class="refreshButton" type="button" @click="refreshHealth">
        Atualizar saúde
      </button>
    </header>

    <section v-if="health" class="summaryCard">
      <div>
        <span class="summaryLabel">Ambiente</span>
        <strong>{{ health.environment }}</strong>
      </div>
      <div>
        <span class="summaryLabel">Release</span>
        <strong>{{ health.release }}</strong>
      </div>
      <div>
        <span class="summaryLabel">Saúde geral</span>
        <strong :data-status="health.overallStatus">
          {{ health.overallStatus }}
        </strong>
      </div>
    </section>

    <p v-if="loading" class="messageCard">Consultando serviços...</p>
    <p v-if="errorMessage" class="messageCard errorCard">{{ errorMessage }}</p>

    <section v-if="health" class="serviceGrid">
      <ServiceHealthCard
        v-for="service in health.services"
        :key="service.serviceName"
        :service="service"
      />
    </section>

    <ContentMetricsCard
      v-if="contentMetrics"
      :metrics="contentMetrics"
    />

    <AdminLoginCard
      v-if="!authenticated"
      @authenticated="authenticate"
    />

    <template v-else>
      <section class="operationsCard">
        <div class="operationsHeader">
          <div>
            <p class="eyebrow">APLICAÇÃO</p>
            <h2>Controles gerais</h2>
          </div>

          <div class="operationButtons">
            <button
              :disabled="operationBusy"
              @click="executeApplicationAction('START')"
            >
              Subir aplicação
            </button>
            <button
              :disabled="operationBusy"
              @click="executeApplicationAction('RESTART')"
            >
              Reiniciar aplicação
            </button>
            <button
              :disabled="operationBusy"
              @click="executeApplicationAction('STOP')"
            >
              Parar aplicação
            </button>
          </div>
        </div>

        <p>
          O Control Center, Control API e OpsAgent permanecem ativos para que
          a aplicação possa ser ligada novamente pelo próprio painel.
        </p>

        <p v-if="operationMessage" class="operationMessage">
          {{ operationMessage }}
        </p>
      </section>

      <section
        v-if="operationsStatus"
        class="managedServiceGrid"
      >
        <ManagedServiceCard
          v-for="service in operationsStatus.services"
          :key="service.serviceKey"
          :service="service"
          :busy="operationBusy"
          @action="executeServiceAction"
        />
      </section>

      <OperationalEventsCard :events="operationalEvents" />
    </template>
  </main>
</template>
