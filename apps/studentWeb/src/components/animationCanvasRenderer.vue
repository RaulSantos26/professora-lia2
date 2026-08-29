<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ spec: Record<string, unknown> }>()

interface AnimationObject {
  objectId: string
  label: string
  role?: string
  shape: 'CIRCLE' | 'RECTANGLE'
  x: number
  y: number
  size: number
  motion: 'STATIC' | 'ORBIT' | 'LINEAR'
  speed: number
  orbitRadius: number
  parentId: string | null
}

const canvas = ref<HTMLCanvasElement | null>(null)
const paused = ref(false)
let frameId = 0
let startTime = performance.now()

function objects(): AnimationObject[] {
  return Array.isArray(props.spec.objects)
    ? props.spec.objects as AnimationObject[]
    : []
}

function isGreekMythScene() {
  const text = [
    String(props.spec.title ?? ''),
    String(props.spec.description ?? ''),
    ...objects().map(item => item.label)
  ].join(' ').toLowerCase()

  return ['perseu', 'medusa', 'atena', 'hermes'].some(
    word => text.includes(word)
  )
}

function caption(ctx: CanvasRenderingContext2D, text: string) {
  ctx.fillStyle = 'rgba(15, 23, 42, .88)'
  ctx.fillRect(34, 470, 892, 48)
  ctx.fillStyle = '#f8fafc'
  ctx.font = '700 18px system-ui'
  ctx.textAlign = 'center'
  ctx.fillText(text, 480, 501)
}

function drawHero(ctx: CanvasRenderingContext2D, x: number, y: number) {
  ctx.save()
  ctx.translate(x, y)
  ctx.fillStyle = '#2b6cb0'
  ctx.fillRect(-18, -5, 36, 68)
  ctx.fillStyle = '#f2c9a5'
  ctx.beginPath()
  ctx.arc(0, -30, 22, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#5b3a29'
  ctx.fillRect(-22, -52, 44, 14)
  ctx.strokeStyle = '#d4af37'
  ctx.lineWidth = 7
  ctx.beginPath()
  ctx.arc(-38, 12, 26, -.9, 2.1)
  ctx.stroke()
  ctx.strokeStyle = '#dbeafe'
  ctx.lineWidth = 6
  ctx.beginPath()
  ctx.moveTo(26, -6)
  ctx.lineTo(54, -62)
  ctx.stroke()
  ctx.restore()
}

function drawMedusa(ctx: CanvasRenderingContext2D, x: number, y: number) {
  ctx.save()
  ctx.translate(x, y)
  ctx.fillStyle = '#79a84d'
  ctx.beginPath()
  ctx.arc(0, 0, 66, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#fff'
  for (const eye of [-24, 24]) {
    ctx.beginPath()
    ctx.arc(eye, -8, 15, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = '#111827'
    ctx.beginPath()
    ctx.arc(eye, -8, 6, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = '#fff'
  }
  ctx.strokeStyle = '#355e2b'
  ctx.lineWidth = 8
  for (let i = 0; i < 9; i += 1) {
    const angle = -2.7 + i * .68
    ctx.beginPath()
    ctx.moveTo(Math.cos(angle) * 48, Math.sin(angle) * 48)
    ctx.quadraticCurveTo(
      Math.cos(angle) * 95,
      Math.sin(angle) * 95 - 20,
      Math.cos(angle + .22) * 115,
      Math.sin(angle + .22) * 115
    )
    ctx.stroke()
  }
  ctx.restore()
}

function drawAthena(ctx: CanvasRenderingContext2D, x: number, y: number) {
  ctx.save()
  ctx.translate(x, y)
  ctx.fillStyle = '#e6b83f'
  ctx.beginPath()
  ctx.arc(0, -25, 31, Math.PI, 0)
  ctx.lineTo(31, 4)
  ctx.lineTo(-31, 4)
  ctx.closePath()
  ctx.fill()
  ctx.fillStyle = '#f2c9a5'
  ctx.beginPath()
  ctx.arc(0, 8, 25, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#9f3f46'
  ctx.fillRect(-22, 34, 44, 72)
  ctx.strokeStyle = '#d4af37'
  ctx.lineWidth = 7
  ctx.beginPath()
  ctx.arc(-34, 69, 29, -.8, 2.2)
  ctx.stroke()
  ctx.restore()
}

function drawHermes(ctx: CanvasRenderingContext2D, x: number, y: number) {
  ctx.save()
  ctx.translate(x, y)
  ctx.fillStyle = '#f2c9a5'
  ctx.beginPath()
  ctx.arc(0, -20, 20, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#f6c453'
  ctx.fillRect(-16, 0, 32, 55)
  ctx.fillStyle = '#dbeafe'
  for (const side of [-1, 1]) {
    ctx.beginPath()
    ctx.ellipse(side * 35, 10, 28, 13, side * .45, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.restore()
}

function renderGreekScene(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  elapsed: number
) {
  const sky = ctx.createLinearGradient(0, 0, 0, height)
  sky.addColorStop(0, '#dbeafe')
  sky.addColorStop(1, '#fef3c7')
  ctx.fillStyle = sky
  ctx.fillRect(0, 0, width, height)
  ctx.fillStyle = '#64748b'
  ctx.fillRect(0, 380, width, 90)
  ctx.fillStyle = '#e7e5e4'
  for (let x = 0; x < width; x += 95) {
    ctx.fillRect(x, 340, 45, 40)
    ctx.beginPath()
    ctx.arc(x + 22, 340, 22, Math.PI, 0)
    ctx.fill()
  }
  const phase = Math.floor(elapsed / 5) % 3
  const heroX = 165 + (phase === 2 ? 110 : 0)
  drawHero(ctx, heroX, 345)
  drawMedusa(ctx, 495, 290)
  drawAthena(ctx, 760, 300)
  drawHermes(ctx, 770 + Math.sin(elapsed * 1.8) * 22, 135)
  ctx.fillStyle = '#172554'
  ctx.font = '800 24px system-ui'
  ctx.textAlign = 'center'
  ctx.fillText('A jornada de Perseu', 480, 44)
  caption(ctx, [
    '1. Atena entrega o escudo: Perseu não deve olhar Medusa diretamente.',
    '2. Hermes ajuda o herói a chegar até a criatura com rapidez.',
    '3. Perseu usa o reflexo do escudo para agir com estratégia.'
  ][phase])
}

function renderGeneric(
  ctx: CanvasRenderingContext2D,
  width: number,
  elapsed: number
) {
  const current = new Map<string, { x: number, y: number }>()
  for (const item of objects()) {
    let x = item.x
    let y = item.y
    if (item.motion === 'ORBIT') {
      const center = item.parentId ? current.get(item.parentId) : null
      const origin = center ?? { x: item.x, y: item.y }
      x = origin.x + Math.cos(elapsed * item.speed) * item.orbitRadius
      y = origin.y + Math.sin(elapsed * item.speed) * item.orbitRadius
    }
    if (item.motion === 'LINEAR') {
      x = item.x + ((elapsed * item.speed * 80) % Math.max(width - 100, 100))
    }
    current.set(item.objectId, { x, y })
    ctx.strokeStyle = '#2563eb'
    ctx.fillStyle = '#eff6ff'
    ctx.lineWidth = 3
    ctx.beginPath()
    if (item.shape === 'RECTANGLE') {
      ctx.fillRect(x - item.size, y - item.size, item.size * 2, item.size * 2)
      ctx.strokeRect(x - item.size, y - item.size, item.size * 2, item.size * 2)
    } else {
      ctx.arc(x, y, item.size, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()
    }
    ctx.fillStyle = '#0f172a'
    ctx.font = '600 14px system-ui'
    ctx.textAlign = 'center'
    ctx.fillText(item.label, x, y + item.size + 21)
  }
}

function render(time: number) {
  const element = canvas.value
  const ctx = element?.getContext('2d')
  if (!element || !ctx) return
  const elapsed = paused.value ? 0 : (time - startTime) / 1000
  ctx.clearRect(0, 0, element.width, element.height)
  if (isGreekMythScene()) renderGreekScene(ctx, element.width, element.height, elapsed)
  else renderGeneric(ctx, element.width, elapsed)
  frameId = requestAnimationFrame(render)
}

function restart() {
  startTime = performance.now()
  paused.value = false
}

watch(() => props.spec, restart, { deep: true })
onMounted(() => {
  if (canvas.value) {
    canvas.value.width = 960
    canvas.value.height = 540
  }
  frameId = requestAnimationFrame(render)
})
onBeforeUnmount(() => cancelAnimationFrame(frameId))
</script>

<template>
  <section class="canvasAnimationVisual">
    <div class="visualToolbar">
      <button type="button" @click="paused = !paused">
        {{ paused ? 'Continuar' : 'Pausar' }}
      </button>
      <button type="button" @click="restart">Reiniciar</button>
    </div>
    <canvas
      ref="canvas"
      width="960"
      height="540"
      role="img"
      aria-label="Animação educacional em duas dimensões"
    />
  </section>
</template>
