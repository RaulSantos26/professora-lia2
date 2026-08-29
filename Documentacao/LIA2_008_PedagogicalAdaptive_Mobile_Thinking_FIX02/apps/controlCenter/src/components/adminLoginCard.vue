<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  authenticated: [token: string]
}>()

const token = ref('')

function authenticate() {
  const normalizedToken = token.value.trim()

  if (normalizedToken) {
    emit('authenticated', normalizedToken)
  }
}
</script>

<template>
  <section class="adminLoginCard">
    <div>
      <p class="eyebrow">CONTROLES PROTEGIDOS</p>
      <h2>Habilitar operações</h2>
      <p>
        Informe o token administrativo mostrado pelo bootstrap.
        Ele fica somente nesta sessão do navegador.
      </p>
    </div>

    <form class="loginForm" @submit.prevent="authenticate">
      <input
        v-model="token"
        type="password"
        autocomplete="off"
        placeholder="Token administrativo"
      />
      <button type="submit">Habilitar controles</button>
    </form>
  </section>
</template>
