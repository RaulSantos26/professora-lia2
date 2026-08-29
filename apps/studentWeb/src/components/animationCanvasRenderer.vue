<script setup lang="ts">
import {
  onBeforeUnmount,
  onMounted,
  ref,
  watch
} from 'vue'

const props = defineProps<{
  spec: Record<string, unknown>
}>()

interface AnimationObject {
  objectId: string
  label: string
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

function render(time: number) {
  const element = canvas.value

  if (!element) {
    return
  }

  const ctx = element.getContext('2d')

  if (!ctx) {
    return
  }

  const width = element.width
  const height = element.height
  ctx.clearRect(0, 0, width, height)

  const elapsed = (
    paused.value
      ? 0
      : (time - startTime) / 1000
  )

  const current = new Map<string, {
    x: number
    y: number
  }>()

  for (const item of objects()) {
    let x = item.x
    let y = item.y

    if (item.motion === 'ORBIT') {
      const center = (
        item.parentId
          ? current.get(item.parentId)
          : null
      ) ?? { x: item.x, y: item.y }

      x = center.x + Math.cos(
        elapsed * item.speed
      ) * item.orbitRadius

      y = center.y + Math.sin(
        elapsed * item.speed
      ) * item.orbitRadius
    }

    if (item.motion === 'LINEAR') {
      x = (
        item.x
        + (
          (elapsed * item.speed * 80)
          % Math.max(width - 100, 100)
        )
      )
    }

    current.set(item.objectId, { x, y })

    ctx.beginPath()

    if (item.shape === 'RECTANGLE') {
      ctx.strokeRect(
        x - item.size,
        y - item.size,
        item.size * 2,
        item.size * 2
      )
    } else {
      ctx.arc(
        x,
        y,
        item.size,
        0,
        Math.PI * 2
      )
      ctx.stroke()
    }

    ctx.font = '12px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(
      item.label,
      x,
      y + item.size + 18
    )
  }

  frameId = requestAnimationFrame(render)
}

function restart() {
  startTime = performance.now()
  paused.value = false
}

watch(() => props.spec, restart, { deep: true })

onMounted(() => {
  const element = canvas.value

  if (element) {
    element.width = 960
    element.height = 540
  }

  frameId = requestAnimationFrame(render)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
})
</script>

<template>
  <section class="canvasAnimationVisual">
    <div class="visualToolbar">
      <button
        type="button"
        @click="paused = !paused"
      >
        {{ paused ? 'Continuar' : 'Pausar' }}
      </button>
      <button type="button" @click="restart">
        Reiniciar
      </button>
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
