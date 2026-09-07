<script setup lang="ts">
import type { ReadingGuide } from './imageReadingGuide'
defineProps<{ guide: ReadingGuide }>()
</script>
<template>
  <section class="readingGuide">
    <h4>Como entender esta imagem</h4>
    <p>{{ guide.introduction }}</p>
    <ol>
      <li v-for="(step, index) in guide.steps" :key="index">
        <strong>{{ step.title }}</strong><p class="where">Onde olhar: {{ step.where }}</p><p>{{ step.explanation }}</p>
      </li>
    </ol>
    <p><strong>O que aprender com ela: </strong>{{ guide.takeaway }}</p>
    <p v-if="guide.caveat"><strong>Atenção: </strong>{{ guide.caveat }}</p>
  </section>
</template>
<style scoped>
.readingGuide { margin: 14px 0; padding: 14px; border-radius: 10px; background: #eef5ff; line-height: 1.6; overflow-wrap: anywhere; }
.readingGuide h4 { margin: 0; }.readingGuide ol { padding-left: 25px; }.readingGuide li { margin: 14px 0; padding-left: 5px; }.readingGuide p { margin: 5px 0; }.where { color: #385276; font-size: .92em; }
</style>
