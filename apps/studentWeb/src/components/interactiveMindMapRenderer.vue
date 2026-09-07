<script setup lang="ts">
import { computed, ref } from 'vue'
import { mindDocument, mindSvg } from './mindMapDocument'
import { useMindMapAssets } from './useMindMapAssets'
const props = defineProps<{ spec: Record<string, unknown>; studentId?: string }>()
const { images, states, refresh } = useMindMapAssets(() => props.studentId, () => props.spec)
const doc = computed(() => mindDocument(props.spec))
const drawing = computed(() => mindSvg(doc.value, images.value, states.value))
const requested = computed(() => [doc.value.root, ...doc.value.branches.map(b => b.node)].filter(n => n.imageTaskId))
const loaded = computed(() => requested.value.filter(n => images.value[n.nodeId]).length)
const pending = computed(() => requested.value.filter(n => !images.value[n.nodeId] && !['ERROR', 'CANCELLED', 'LIMIT'].includes(states.value[n.nodeId])).length)
const source = computed(() => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(drawing.value.svg))
const dialog = ref<HTMLDialogElement | null>(null)
const zoom = ref(1)
const error = ref('')
const exporting = ref(false)
function save(blob: Blob, extension: string) {
  const url = URL.createObjectURL(blob), link = document.createElement('a')
  link.href = url; link.download = 'lia-mapa-mental.' + extension; link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
async function exportMap(format: 'svg' | 'png') {
  error.value = ''; exporting.value = true
  try {
    if (loaded.value < requested.value.length && !window.confirm('Algumas figuras ainda não estão disponíveis. Baixar o mapa parcial, com todo o texto e os espaços indicados?')) return
    const snapshot = drawing.value
    if (format === 'svg') { save(new Blob([snapshot.svg], { type: 'image/svg+xml;charset=utf-8' }), 'svg'); return }
    const img = new Image(); img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(snapshot.svg); await img.decode()
    const canvas = document.createElement('canvas')
    const ratio = Math.min(1.5, 8000 / snapshot.height)
    canvas.width = 1600 * ratio; canvas.height = snapshot.height * ratio
    const context = canvas.getContext('2d'); if (!context) throw new Error()
    context.drawImage(img, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/png'))
    if (!blob) throw new Error(); save(blob, 'png')
  } catch { error.value = 'Não foi possível baixar agora. O mapa continua disponível; tente novamente.' }
  finally { exporting.value = false }
}
</script>

<template>
  <section class="liaMindDocument" aria-label="Mapa mental didático">
    <div class="mindToolbar">
      <button type="button" @click="zoom = 1; dialog?.showModal()">Abrir em tela cheia</button>
      <button type="button" :disabled="exporting" @click="exportMap('png')">Baixar PNG</button>
      <button type="button" :disabled="exporting" @click="exportMap('svg')">Baixar SVG</button>
    </div>
    <p class="mindHint">Um tema central, ideias conectadas. Amplie o mapa ou leia os tópicos abaixo.</p>
    <p v-if="requested.length" class="mindHint" role="status">Figuras: {{ loaded }} de {{ requested.length }} disponíveis. {{ pending ? 'O texto já está pronto; as ilustrações estão sendo preparadas.' : 'O mapa continua utilizável mesmo se uma figura falhar.' }} <button v-if="loaded < requested.length" type="button" @click="refresh()">Verificar figuras</button></p>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="spec.assetWarning" role="status">{{ spec.assetWarning }}</p>
    <button class="mindPreview" type="button" aria-label="Ampliar mapa mental" @click="zoom = 1; dialog?.showModal()">
      <img :src="source" :alt="'Mapa mental: ' + doc.title" />
    </button>
    <details class="mindReading">
      <summary>Ler conteúdo completo do mapa</summary>
      <h3>{{ doc.root.label }}</h3><p>{{ doc.root.detail }}</p>
      <section v-for="branch in doc.branches" :key="branch.node.nodeId">
        <h4>{{ branch.node.label }}</h4><p>{{ branch.node.detail }}</p>
        <img v-if="images[branch.node.nodeId]" :src="images[branch.node.nodeId]" :alt="'Ilustração de ' + branch.node.label" class="mindReadingImage" />
        <ul><li v-for="node in branch.descendants" :key="node.nodeId"><strong>{{ node.label }}</strong>: {{ node.detail }}</li></ul>
      </section>
    </details>
    <dialog ref="dialog" class="mindDialog" aria-label="Mapa mental ampliado">
      <div class="mindToolbar">
        <strong>{{ doc.title }}</strong>
        <button type="button" aria-label="Diminuir zoom" @click="zoom = Math.max(.5, zoom - .25)">−</button>
        <button type="button" aria-label="Aumentar zoom" @click="zoom = Math.min(3, zoom + .25)">+</button>
        <button type="button" @click="zoom = 1">Ajustar à tela</button>
        <button type="button" autofocus @click="dialog?.close()">Fechar</button>
      </div>
      <div class="mindScroll"><img :src="source" :alt="doc.title" :style="{ width: `${zoom * 100}%`, maxWidth: 'none' }" /></div>
    </dialog>
  </section>
</template>

<style scoped>
.liaMindDocument { min-width: 0; }
.mindToolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; padding: 10px 0; }
.mindToolbar button { min-height: 44px; padding: 8px 14px; background: white; color: #17385f; border: 1px solid #b4c8df; border-radius: 10px; cursor: pointer; }
.mindToolbar strong { margin-right: auto; }
.mindHint { color: #445870; line-height: 1.5; }
.mindPreview { display: block; width: 100%; background: #fffdf5; border: 1px solid #d8e1ea; border-radius: 16px; padding: 0; cursor: zoom-in; overflow: hidden; }
.mindPreview img { display: block; width: 100%; }
.mindReading { margin-top: 16px; padding: 16px; background: #f5f8fc; border-radius: 12px; line-height: 1.7; font-size: 16px; overflow-wrap: anywhere; }
.mindReading summary { cursor: pointer; font-weight: 700; }
.mindReading h4 { margin-bottom: 4px; }
.mindReadingImage { width: 100%; max-width: 360px; display: block; border-radius: 14px; margin: 10px 0; }
.mindDialog { width: calc(100vw - 32px); max-width: 1500px; max-height: calc(100dvh - 32px); padding: 16px; border: 0; border-radius: 18px; }
.mindDialog::backdrop { background: #101b2cbb; }
.mindScroll { overflow: auto; max-height: calc(100dvh - 160px); }
.mindScroll img { display: block; }
button:focus-visible, summary:focus-visible { outline: 3px solid #246bd8; outline-offset: 3px; }
@media(max-width: 600px) { .mindDialog { width: calc(100vw - 16px); padding: 8px; } .mindReading { padding: 12px; } }
</style>
