<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    title: string
    eyebrow?: string
    summary?: string
    defaultOpen?: boolean
    badge?: string | number | null
  }>(),
  {
    eyebrow: '',
    summary: '',
    defaultOpen: false,
    badge: null
  }
)

const isOpen = ref(props.defaultOpen)

function toggle() {
  isOpen.value = !isOpen.value
}
</script>

<template>
  <section class="accordionCard" :data-open="isOpen">
    <button
      type="button"
      class="accordionHeader"
      :aria-expanded="isOpen"
      @click="toggle"
    >
      <span class="accordionHeaderText">
        <small v-if="eyebrow" class="eyebrow">{{ eyebrow }}</small>
        <strong>{{ title }}</strong>
        <span v-if="summary" class="accordionSummary">{{ summary }}</span>
      </span>

      <span class="accordionActions">
        <span v-if="badge !== null" class="countBadge">{{ badge }}</span>
        <span class="accordionChevron" aria-hidden="true">
          {{ isOpen ? '−' : '+' }}
        </span>
      </span>
    </button>

    <div v-show="isOpen" class="accordionBody">
      <slot />
    </div>
  </section>
</template>
