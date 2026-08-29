<script setup lang="ts">
import { computed, ref } from 'vue'

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
}

const scale = ref(0.9)
const offsetX = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const lastX = ref(0)
const lastY = ref(0)
const selectedNodeId = ref<string | null>(null)

const nodes = computed(() => {
  const source = (
    Array.isArray(props.spec.nodes)
      ? props.spec.nodes as MindNode[]
      : []
  )

  if (
    source.length === 0
    || source.every(
      node =>
        Number.isFinite(node.x)
        && Number.isFinite(node.y)
    )
  ) {
    return source
  }

  const rootId = String(
    props.spec.rootId
    ?? source.find(node => node.parentId === null)?.nodeId
    ?? source[0]?.nodeId
    ?? ''
  )

  const byParent = new Map<string | null, MindNode[]>()

  source.forEach(node => {
    const key = node.parentId ?? null
    const values = byParent.get(key) ?? []
    values.push(node)
    byParent.set(key, values)
  })

  const result: MindNode[] = []
  const root = source.find(
    node => node.nodeId === rootId
  ) ?? source[0]

  if (!root) {
    return []
  }

  result.push({
    ...root,
    x: 600,
    y: 90,
    level: 0
  })

  const branches = byParent.get(root.nodeId) ?? []

  branches.forEach((branch, branchIndex) => {
    const x = (
      130
      + branchIndex
      * (
        940
        / Math.max(branches.length - 1, 1)
      )
    )

    result.push({
      ...branch,
      x,
      y: 250,
      level: 1
    })

    const children = byParent.get(branch.nodeId) ?? []

    children.forEach((child, childIndex) => {
      const offset = (
        childIndex
        - (children.length - 1) / 2
      ) * 150

      result.push({
        ...child,
        x: x + offset,
        y: 430,
        level: 2
      })

      const grandchildren = byParent.get(child.nodeId) ?? []

      grandchildren.forEach((grand, grandIndex) => {
        result.push({
          ...grand,
          x: (
            x
            + offset
            + (
              grandIndex
              - (grandchildren.length - 1) / 2
            ) * 110
          ),
          y: 590,
          level: 3
        })
      })
    })
  })

  const known = new Set(
    result.map(node => node.nodeId)
  )

  source.forEach(node => {
    if (!known.has(node.nodeId)) {
      result.push({
        ...node,
        x: 600,
        y: 680,
        level: 4
      })
    }
  })

  return result
})

const edges = computed(
  () => nodes.value
    .filter(node => node.parentId)
    .map(node => ({
      child: node,
      parent: nodes.value.find(
        candidate =>
          candidate.nodeId === node.parentId
      ) ?? null
    }))
    .filter(edge => edge.parent)
)

const selectedNode = computed(
  () => nodes.value.find(
    node => node.nodeId === selectedNodeId.value
  ) ?? null
)

function wheel(event: WheelEvent) {
  event.preventDefault()
  const direction = event.deltaY > 0 ? -0.08 : 0.08
  scale.value = Math.min(
    1.8,
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
  scale.value = 0.9
  offsetX.value = 0
  offsetY.value = 0
}
</script>

<template>
  <section class="interactiveMindMap">
    <div class="visualToolbar">
      <button type="button" @click="scale = Math.min(1.8, scale + 0.1)">
        +
      </button>
      <button type="button" @click="scale = Math.max(0.45, scale - 0.1)">
        −
      </button>
      <button type="button" @click="resetView">
        Centralizar
      </button>
    </div>

    <div class="mindMapSvgViewport">
      <svg
        viewBox="0 0 1200 760"
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
            :key="`${edge.parent?.nodeId}-${edge.child.nodeId}`"
            :x1="edge.parent?.x"
            :y1="edge.parent?.y"
            :x2="edge.child.x"
            :y2="edge.child.y"
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
              x="-100"
              y="-34"
              width="200"
              height="68"
              rx="14"
            />
            <foreignObject
              x="-92"
              y="-27"
              width="184"
              height="54"
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
