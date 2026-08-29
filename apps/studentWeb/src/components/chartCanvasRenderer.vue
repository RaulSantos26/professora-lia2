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

const canvas = ref<HTMLCanvasElement | null>(null)
let observer: ResizeObserver | null = null

function draw() {
  const element = canvas.value

  if (!element) {
    return
  }

  const parent = element.parentElement
  const width = Math.max(
    320,
    parent?.clientWidth ?? 720
  )
  const height = 420
  const dpr = window.devicePixelRatio || 1

  element.width = width * dpr
  element.height = height * dpr
  element.style.width = `${width}px`
  element.style.height = `${height}px`

  const ctx = element.getContext('2d')

  if (!ctx) {
    return
  }

  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, width, height)

  const categories = Array.isArray(props.spec.categories)
    ? props.spec.categories as string[]
    : []
  const series = Array.isArray(props.spec.series)
    ? props.spec.series as Array<{
        name: string
        values: number[]
      }>
    : []

  const values = series.flatMap(item => item.values)
  const maxValue = Math.max(...values, 1)
  const left = 58
  const top = 30
  const right = 18
  const bottom = 70
  const plotWidth = width - left - right
  const plotHeight = height - top - bottom

  ctx.strokeStyle = 'currentColor'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(left, top)
  ctx.lineTo(left, top + plotHeight)
  ctx.lineTo(left + plotWidth, top + plotHeight)
  ctx.stroke()

  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'

  const chartType = String(
    props.spec.chartType ?? 'BAR'
  )

  if (chartType === 'LINE') {
    series.forEach((item, seriesIndex) => {
      ctx.beginPath()
      ctx.lineWidth = 2 + seriesIndex

      item.values.forEach((value, index) => {
        const x = left + (
          index / Math.max(categories.length - 1, 1)
        ) * plotWidth
        const y = top + plotHeight - (
          value / maxValue
        ) * plotHeight

        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }

        ctx.fillRect(x - 2, y - 2, 4, 4)
      })

      ctx.stroke()
    })
  } else {
    const groupWidth = (
      plotWidth
      / Math.max(categories.length, 1)
    )
    const barWidth = (
      groupWidth
      / Math.max(series.length + 1, 2)
    )

    categories.forEach((_, categoryIndex) => {
      series.forEach((item, seriesIndex) => {
        const value = item.values[categoryIndex] ?? 0
        const barHeight = (
          value / maxValue
        ) * plotHeight
        const x = (
          left
          + categoryIndex * groupWidth
          + barWidth * (seriesIndex + 0.5)
        )
        const y = top + plotHeight - barHeight

        ctx.strokeRect(
          x,
          y,
          barWidth * 0.8,
          barHeight
        )
      })
    })
  }

  categories.forEach((label, index) => {
    const x = left + (
      (index + 0.5)
      / Math.max(categories.length, 1)
    ) * plotWidth

    ctx.fillText(
      label.slice(0, 18),
      x,
      top + plotHeight + 24
    )
  })
}

watch(() => props.spec, draw, { deep: true })

onMounted(() => {
  draw()
  observer = new ResizeObserver(draw)

  if (canvas.value?.parentElement) {
    observer.observe(canvas.value.parentElement)
  }
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <section class="canvasVisual">
    <canvas
      ref="canvas"
      role="img"
      aria-label="Gráfico educacional"
    />
  </section>
</template>
