<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref
} from 'vue'

const props = defineProps<{
  spec: Record<string, unknown>
}>()

interface MindNode {
  nodeId: string
  parentId: string | null
  label: string
  detail: string
  x: number
  y: number
  level: number
  width?: number
  height?: number
}

const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const lastX = ref(0)
const lastY = ref(0)
const selectedNodeId = ref<string | null>(null)
const expanded = ref(false)

const nodes = computed(() => {
  const source = (
    Array.isArray(props.spec.nodes)
      ? props.spec.nodes as MindNode[]
      : []
  )

  const hasCompleteLayout = (
    source.length > 0
    && source.every(
      node =>
        Number.isFinite(node.x)
        && Number.isFinite(node.y)
        && Number.isFinite(node.width)
        && Number.isFinite(node.height)
    )
  )

  if (source.length === 0 || hasCompleteLayout) {
    return source
  }

  const rootId = String(
    props.spec.rootId
    ?? source.find(node => node.parentId === null)?.nodeId
    ?? source[0]?.nodeId
    ?? ''
  )
  const root = source.find(
    node => node.nodeId === rootId
  ) ?? source[0]

  if (!root) {
    return []
  }

  const byId = new Map(
    source.map(node => [node.nodeId, node])
  )
  const children = new Map<string, MindNode[]>()

  source.forEach(node => {
    children.set(node.nodeId, [])
  })

  source.forEach(node => {
    if (
      node.nodeId !== root.nodeId
      && node.parentId
      && byId.has(node.parentId)
    ) {
      children.set(
        node.parentId,
        [...(children.get(node.parentId) ?? []), node]
      )
    }
  })

  const size = (node: MindNode) => {
    const lines = Math.max(
      1,
      Math.ceil(node.label.length / 24)
    )
    return {
      width: Math.min(
        320,
        Math.max(188, 88 + Math.min(
          Math.max(node.label.length, 12),
          30
        ) * 7)
      ),
      height: Math.max(68, 34 + lines * 20)
    }
  }
  const widths = new Map<string, number>()
  const measure = (
    node: MindNode,
    ancestry = new Set<string>()
  ): number => {
    if (widths.has(node.nodeId)) {
      return widths.get(node.nodeId)!
    }

    if (ancestry.has(node.nodeId)) {
      return size(node).width
    }

    const next = new Set(ancestry)
    next.add(node.nodeId)
    const childWidths = (children.get(node.nodeId) ?? [])
      .filter(child => !next.has(child.nodeId))
      .map(child => measure(child, next))
    const width = Math.max(
      size(node).width,
      childWidths.reduce(
        (total, value) => total + value,
        0
      ) + Math.max(childWidths.length - 1, 0) * 56
    )
    widths.set(node.nodeId, width)
    return width
  }

  const result: MindNode[] = []
  const positioned = new Set<string>()
  const place = (
    node: MindNode,
    left: number,
    level: number,
    ancestry = new Set<string>()
  ) => {
    if (ancestry.has(node.nodeId)) {
      return
    }

    const next = new Set(ancestry)
    next.add(node.nodeId)
    const dimensions = size(node)
    const subtreeWidth = measure(node)
    result.push({
      ...node,
      x: left + subtreeWidth / 2,
      y: 120 + level * 180,
      level,
      width: dimensions.width,
      height: dimensions.height
    })
    positioned.add(node.nodeId)

    let childLeft = left

    for (const child of children.get(node.nodeId) ?? []) {
      if (!next.has(child.nodeId)) {
        place(child, childLeft, level + 1, next)
        childLeft += measure(child) + 56
      }
    }
  }

  place(root, 120, 0)

  source
    .filter(node => !positioned.has(node.nodeId))
    .forEach(node => {
      const left = (
        Math.max(
          ...result.map(item => item.x + nodeWidth(item) / 2),
          120
        ) + 56
      )
      place(node, left, 1)
    })

  return result
})

const viewport = computed(() => {
  const source = (
    props.spec.viewport
    && typeof props.spec.viewport === 'object'
      ? props.spec.viewport as Record<string, unknown>
      : {}
  )
  const width = Math.max(
    Number(source.width) || 0,
    ...nodes.value.map(
      node => node.x + nodeWidth(node) / 2 + 120
    ),
    960
  )
  const height = Math.max(
    Number(source.height) || 0,
    ...nodes.value.map(
      node => node.y + nodeHeight(node) / 2 + 120
    ),
    560
  )

  return { width, height }
})

const edges = computed(
  () => nodes.value
    .map(child => ({
      child,
      parent: child.parentId
        ? nodes.value.find(
          candidate =>
            candidate.nodeId === child.parentId
        ) ?? null
        : null
    }))
    .filter(
      (
        edge
      ): edge is {
        child: MindNode
        parent: MindNode
      } => edge.parent !== null
    )
)

const selectedNode = computed(
  () => nodes.value.find(
    node => node.nodeId === selectedNodeId.value
  ) ?? null
)

function nodeWidth(node: MindNode) {
  return Number(node.width) || 200
}

function nodeHeight(node: MindNode) {
  return Number(node.height) || 68
}

function wheel(event: WheelEvent) {
  event.preventDefault()
  const direction = event.deltaY > 0 ? -0.08 : 0.08
  scale.value = Math.min(
    2.4,
    Math.max(0.45, scale.value + direction)
  )
}

function pointerDown(event: PointerEvent) {
  dragging.value = true
  lastX.value = event.clientX
  lastY.value = event.clientY
  ;(event.currentTarget as SVGElement)
    .setPointerCapture(event.pointerId)
}

function pointerMove(event: PointerEvent) {
  if (!dragging.value) {
    return
  }

  offsetX.value += event.clientX - lastX.value
  offsetY.value += event.clientY - lastY.value
  lastX.value = event.clientX
  lastY.value = event.clientY
}

function pointerUp() {
  dragging.value = false
}

function resetView() {
  scale.value = 1
  offsetX.value = 0
  offsetY.value = 0
}

function toggleExpanded() {
  expanded.value = !expanded.value
  resetView()
}

function closeOnEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && expanded.value) {
    expanded.value = false
    resetView()
  }
}

onMounted(() => {
  window.addEventListener('keydown', closeOnEscape)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', closeOnEscape)
})
</script>

<template>
  <section
    class="interactiveMindMap"
    :class="{ isExpanded: expanded }"
  >
    <div class="visualToolbar">
      <strong class="mindMapControlTitle">
        {{ expanded ? 'Mapa mental em tela ampliada' : 'Explorar mapa mental' }}
      </strong>
      <button
        type="button"
        aria-label="Aumentar mapa"
        @click="scale = Math.min(2.4, scale + 0.1)"
      >
        +
      </button>
      <button
        type="button"
        aria-label="Diminuir mapa"
        @click="scale = Math.max(0.45, scale - 0.1)"
      >
        −
      </button>
      <button type="button" @click="resetView">
        Ajustar à tela
      </button>
      <button
        type="button"
        class="mindMapExpandButton"
        @click="toggleExpanded"
      >
        {{ expanded ? 'Fechar' : 'Abrir em tela cheia' }}
      </button>
    </div>

    <div class="mindMapSvgViewport">
      <svg
        :viewBox="`0 0 ${viewport.width} ${viewport.height}`"
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label="Mapa mental interativo"
        @wheel="wheel"
        @pointerdown="pointerDown"
        @pointermove="pointerMove"
        @pointerup="pointerUp"
        @pointercancel="pointerUp"
      >
        <g
          :transform="
            `translate(${offsetX} ${offsetY}) scale(${scale})`
          "
        >
          <line
            v-for="edge in edges"
            :key="`${edge.parent.nodeId}-${edge.child.nodeId}`"
            :x1="edge.parent.x"
            :y1="edge.parent.y + nodeHeight(edge.parent) / 2"
            :x2="edge.child.x"
            :y2="edge.child.y - nodeHeight(edge.child) / 2"
            class="mindMapConnection"
          />

          <g
            v-for="node in nodes"
            :key="node.nodeId"
            class="mindMapNode"
            :data-level="node.level"
            :data-selected="selectedNodeId === node.nodeId"
            :transform="`translate(${node.x} ${node.y})`"
            @click.stop="selectedNodeId = node.nodeId"
          >
            <rect
              :x="-nodeWidth(node) / 2"
              :y="-nodeHeight(node) / 2"
              :width="nodeWidth(node)"
              :height="nodeHeight(node)"
              rx="14"
            />
            <foreignObject
              :x="-nodeWidth(node) / 2 + 8"
              :y="-nodeHeight(node) / 2 + 7"
              :width="nodeWidth(node) - 16"
              :height="nodeHeight(node) - 14"
            >
              <div class="mindMapNodeLabel">
                {{ node.label }}
              </div>
            </foreignObject>
          </g>
        </g>
      </svg>
    </div>

    <aside
      v-if="selectedNode"
      class="visualInspector"
    >
      <strong>{{ selectedNode.label }}</strong>
      <p>{{ selectedNode.detail }}</p>
    </aside>
  </section>
</template>
