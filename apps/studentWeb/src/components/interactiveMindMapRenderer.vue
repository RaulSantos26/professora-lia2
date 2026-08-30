<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch
} from 'vue'

const props = defineProps<{
  spec: Record<string, unknown>
}>()

interface MindNode {
  nodeId: string
  parentId: string | null
  label: string
  detail: string
  x?: number
  y?: number
  level?: number
  width?: number
  height?: number
  branchIndex?: number
  color?: string
  icon?: string
  isRoot?: boolean
}

const colors = [
  '#ef4444',
  '#f97316',
  '#eab308',
  '#22c55e',
  '#06b6d4',
  '#3b82f6',
  '#8b5cf6',
  '#ec4899'
]

const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const lastX = ref(0)
const lastY = ref(0)
const selectedNodeId = ref<string | null>(null)
const expanded = ref(false)
const customPositions = ref<
  Record<string, { x: number, y: number }>
>({})
const draggedNodeId = ref<string | null>(null)

const layoutStorageKey = computed(
  () => [
    'lia2-mind-map-layout',
    String(props.spec.rootId ?? 'root'),
    String(props.spec.title ?? 'mapa')
  ].join(':')
)

function loadCustomPositions() {
  try {
    const saved = window.localStorage.getItem(
      layoutStorageKey.value
    )
    customPositions.value = saved
      ? JSON.parse(saved) as Record<string, {
          x: number
          y: number
        }>
      : {}
  } catch {
    customPositions.value = {}
  }
}

function saveCustomPositions() {
  window.localStorage.setItem(
    layoutStorageKey.value,
    JSON.stringify(customPositions.value)
  )
}

function iconFor(node: Pick<MindNode, 'label' | 'detail' | 'parentId'>) {
  const value = `${node.label} ${node.detail}`.toLocaleLowerCase()

  if (/(minotauro|monstro|fera|animal)/.test(value)) return '🐂'
  if (/(teseu|herói|guerreiro|luta)/.test(value)) return '🗡️'
  if (/(ariadne|novelo|fio)/.test(value)) return '🧶'
  if (/(labirinto|caminho|trajeto)/.test(value)) return '🌀'
  if (/(conflito|batalha|confronto|guerra)/.test(value)) return '⚔️'
  if (/(fuga|viagem|partida|retorno)/.test(value)) return '🏃'
  if (/(deus|deusa|mito|grécia)/.test(value)) return '🏛️'
  if (/(personagem|pessoa|autor|poeta)/.test(value)) return '🧑'
  if (/(planta|flor|floresta|natureza)/.test(value)) return '🌿'
  if (/(animal|vida|corpo|célula)/.test(value)) return '🔬'
  if (/(número|equação|função|cálculo)/.test(value)) return '➗'
  if (/(experimento|química|elemento)/.test(value)) return '⚗️'
  if (/(história|época|tempo|passado)/.test(value)) return '⌛'
  return node.parentId ? '✦' : '🧠'
}

const baseNodes = computed<MindNode[]>(() => {
  const source = (
    Array.isArray(props.spec.nodes)
      ? props.spec.nodes as MindNode[]
      : []
  )

  if (source.length === 0) {
    return []
  }

  const root = source.find(
    node => node.nodeId === String(props.spec.rootId)
  ) ?? source.find(node => node.parentId === null)
    ?? source[0]
  const byId = new Map(
    source.map(node => [node.nodeId, node])
  )
  const children = new Map<string, MindNode[]>()

  source.forEach(node => {
    children.set(node.nodeId, [])
  })

  const effectiveParents = new Map<string, string | null>()

  source.forEach(node => {
    if (node.nodeId === root.nodeId) {
      effectiveParents.set(node.nodeId, null)
      return
    }

    const parentId = node.parentId && byId.has(node.parentId)
      && node.parentId !== node.nodeId
      ? node.parentId
      : root.nodeId

    effectiveParents.set(node.nodeId, parentId)
    children.set(
      parentId,
      [...(children.get(parentId) ?? []), node]
    )
  })

  const raw: Array<MindNode & {
    x: number
    y: number
    level: number
    width: number
    height: number
    branchIndex: number
    color: string
    icon: string
    isRoot: boolean
  }> = []
  const seen = new Set<string>()

  const sizeFor = (node: MindNode, depth: number) => {
    const lines = Math.max(1, Math.ceil(node.label.length / 24))
    return {
      width: depth === 0
        ? 264
        : Math.min(270, Math.max(188, 100 + Math.min(
          Math.max(node.label.length, 12),
          28
        ) * 6)),
      height: depth === 0
        ? 112
        : Math.max(74, 38 + lines * 20)
    }
  }

  const place = (
    node: MindNode,
    depth: number,
    angle: number,
    branchIndex: number,
    ancestry = new Set<string>()
  ) => {
    if (ancestry.has(node.nodeId)) {
      return
    }

    const next = new Set(ancestry)
    next.add(node.nodeId)
    const distance = depth === 0
      ? 0
      : 360 + (depth - 1) * 230
    const dimensions = sizeFor(node, depth)
    const color = colors[branchIndex % colors.length]

    raw.push({
      ...node,
      parentId: effectiveParents.get(node.nodeId) ?? null,
      x: Math.cos(angle) * distance,
      y: Math.sin(angle) * distance,
      level: depth,
      width: dimensions.width,
      height: dimensions.height,
      branchIndex,
      color,
      icon: iconFor(node),
      isRoot: depth === 0
    })
    seen.add(node.nodeId)

    if (depth === 0) {
      return
    }

    const childNodes = (children.get(node.nodeId) ?? [])
      .filter(child => !next.has(child.nodeId))
    const step = Math.min(
      Math.PI / 5,
      Math.max(Math.PI / 16, Math.PI / Math.max(
        childNodes.length + 2,
        4
      ))
    )

    childNodes.forEach((child, index) => {
      const childAngle = (
        angle + (index - (childNodes.length - 1) / 2) * step
      )
      place(
        child,
        depth + 1,
        childAngle,
        depth === 0 ? index : branchIndex,
        next
      )
    })
  }

  const mainBranches = children.get(root.nodeId) ?? []
  place(root, 0, 0, 0)

  mainBranches.forEach((branch, index) => {
    const angle = (
      -Math.PI / 2
      + (index * 2 * Math.PI) / Math.max(mainBranches.length, 1)
    )
    place(branch, 1, angle, index, new Set([root.nodeId]))
  })

  source
    .filter(node => !seen.has(node.nodeId))
    .forEach((node, index) => {
      place(
        node,
        1,
        -Math.PI / 2 + index * Math.PI / 6,
        index,
        new Set()
      )
    })

  const minX = Math.min(
    ...raw.map(node => node.x - node.width / 2),
    -420
  )
  const minY = Math.min(
    ...raw.map(node => node.y - node.height / 2),
    -300
  )

  return raw.map(node => ({
    ...node,
    x: Math.round(node.x - minX + 150),
    y: Math.round(node.y - minY + 150)
  }))
})

const nodes = computed(
  () => baseNodes.value.map(node => ({
    ...node,
    ...(customPositions.value[node.nodeId] ?? {})
  }))
)

const viewport = computed(() => ({
  width: Math.max(
    1160,
    ...nodes.value.map(
      node => (node.x ?? 0) + (node.width ?? 200) / 2 + 150
    )
  ),
  height: Math.max(
    820,
    ...nodes.value.map(
      node => (node.y ?? 0) + (node.height ?? 74) / 2 + 150
    )
  )
}))

const byId = computed(
  () => new Map(nodes.value.map(node => [node.nodeId, node]))
)

const edges = computed(
  () => nodes.value
    .filter(node => node.parentId && byId.value.has(node.parentId))
    .map(child => ({
      child,
      parent: byId.value.get(child.parentId!)!
    }))
)

const selectedNode = computed(
  () => nodes.value.find(
    node => node.nodeId === selectedNodeId.value
  ) ?? null
)

watch(
  layoutStorageKey,
  () => {
    selectedNodeId.value = null
    loadCustomPositions()
  },
  { immediate: true }
)

function nodeWidth(node: MindNode) {
  return Number(node.width) || 200
}

function nodeHeight(node: MindNode) {
  return Number(node.height) || 74
}

function edgePath(edge: {
  parent: MindNode
  child: MindNode
}) {
  const dx = (edge.child.x ?? 0) - (edge.parent.x ?? 0)
  const dy = (edge.child.y ?? 0) - (edge.parent.y ?? 0)
  const distance = Math.max(Math.hypot(dx, dy), 1)
  const unitX = dx / distance
  const unitY = dy / distance
  const startX = (edge.parent.x ?? 0) + unitX * (
    nodeWidth(edge.parent) / 2 - 8
  )
  const startY = (edge.parent.y ?? 0) + unitY * (
    nodeHeight(edge.parent) / 2 - 8
  )
  const endX = (edge.child.x ?? 0) - unitX * (
    nodeWidth(edge.child) / 2 - 8
  )
  const endY = (edge.child.y ?? 0) - unitY * (
    nodeHeight(edge.child) / 2 - 8
  )
  const bend = Math.min(74, distance * 0.16)
  const controlX = (startX + endX) / 2 - unitY * bend
  const controlY = (startY + endY) / 2 + unitX * bend

  return `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`
}

function wheel(event: WheelEvent) {
  event.preventDefault()
  scale.value = Math.min(
    2.3,
    Math.max(
      0.45,
      scale.value + (event.deltaY > 0 ? -0.08 : 0.08)
    )
  )
}

function pointerDown(event: PointerEvent) {
  dragging.value = true
  lastX.value = event.clientX
  lastY.value = event.clientY
  ;(event.currentTarget as SVGElement)
    .setPointerCapture(event.pointerId)
}

function nodePointerDown(
  event: PointerEvent,
  node: MindNode
) {
  draggedNodeId.value = node.nodeId
  lastX.value = event.clientX
  lastY.value = event.clientY
  ;(event.currentTarget as SVGGElement)
    .ownerSVGElement
    ?.setPointerCapture(event.pointerId)
}

function pointerMove(event: PointerEvent) {
  const deltaX = event.clientX - lastX.value
  const deltaY = event.clientY - lastY.value
  lastX.value = event.clientX
  lastY.value = event.clientY

  if (draggedNodeId.value) {
    const current = nodes.value.find(
      node => node.nodeId === draggedNodeId.value
    )

    if (!current) return

    const svg = event.currentTarget as SVGSVGElement
    const scaleX = viewport.value.width / Math.max(
      svg.clientWidth,
      1
    ) / scale.value
    const scaleY = viewport.value.height / Math.max(
      svg.clientHeight,
      1
    ) / scale.value

    customPositions.value = {
      ...customPositions.value,
      [current.nodeId]: {
        x: (current.x ?? 0) + deltaX * scaleX,
        y: (current.y ?? 0) + deltaY * scaleY
      }
    }
    return
  }

  if (!dragging.value) return
  offsetX.value += deltaX
  offsetY.value += deltaY
}

function pointerUp() {
  if (draggedNodeId.value) {
    saveCustomPositions()
  }
  draggedNodeId.value = null
  dragging.value = false
}

function resetView() {
  scale.value = 1
  offsetX.value = 0
  offsetY.value = 0
}

function resetBranches() {
  customPositions.value = {}
  window.localStorage.removeItem(layoutStorageKey.value)
  selectedNodeId.value = null
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
    class="interactiveMindMap buzanMindMap"
    :class="{ isExpanded: expanded }"
  >
    <div class="visualToolbar">
      <div class="mindMapToolbarTitle">
        <span aria-hidden="true">🧠</span>
        <strong>
          {{ expanded ? 'Mapa mental em tela ampliada' : 'Mapa mental visual' }}
        </strong>
      </div>
      <button type="button" aria-label="Aumentar mapa" @click="scale = Math.min(2.3, scale + 0.1)">+</button>
      <button type="button" aria-label="Diminuir mapa" @click="scale = Math.max(0.45, scale - 0.1)">−</button>
      <button type="button" @click="resetView">Ajustar à tela</button>
      <button type="button" @click="resetBranches">Restaurar ramos</button>
      <button type="button" class="mindMapExpandButton" @click="toggleExpanded">
        {{ expanded ? 'Fechar' : 'Abrir em tela cheia' }}
      </button>
    </div>

    <p class="mindMapHint">
      Cada cor representa uma ideia principal. Arraste um ramo para ajustar
      a posição; toque nele para ver a explicação.
    </p>

    <div class="mindMapSvgViewport">
      <svg
        :viewBox="`0 0 ${viewport.width} ${viewport.height}`"
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label="Mapa mental visual interativo"
        @wheel="wheel"
        @pointerdown="pointerDown"
        @pointermove="pointerMove"
        @pointerup="pointerUp"
        @pointercancel="pointerUp"
      >
        <defs>
          <filter id="mindMapShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="5" stdDeviation="5" flood-opacity="0.14" />
          </filter>
        </defs>
        <g :transform="`translate(${offsetX} ${offsetY}) scale(${scale})`">
          <path
            v-for="edge in edges"
            :key="`${edge.parent.nodeId}-${edge.child.nodeId}`"
            :d="edgePath(edge)"
            class="mindMapConnection buzanConnection"
            :style="{ stroke: edge.child.color }"
          />

          <g
            v-for="node in nodes"
            :key="node.nodeId"
            class="mindMapNode buzanNode"
            :data-root="node.isRoot"
            :data-selected="selectedNodeId === node.nodeId"
            :style="{ '--branch-color': node.color }"
            :transform="`translate(${node.x} ${node.y})`"
            @pointerdown.stop="nodePointerDown($event, node)"
            @click.stop="selectedNodeId = node.nodeId"
          >
            <rect
              :x="-nodeWidth(node) / 2"
              :y="-nodeHeight(node) / 2"
              :width="nodeWidth(node)"
              :height="nodeHeight(node)"
              :rx="node.isRoot ? 40 : 22"
              filter="url(#mindMapShadow)"
            />
            <foreignObject
              :x="-nodeWidth(node) / 2 + 10"
              :y="-nodeHeight(node) / 2 + 9"
              :width="nodeWidth(node) - 20"
              :height="nodeHeight(node) - 18"
            >
              <div class="buzanNodeContent">
                <span class="buzanNodeIcon" aria-hidden="true">{{ node.icon }}</span>
                <span class="mindMapNodeLabel">{{ node.label }}</span>
              </div>
            </foreignObject>
          </g>
        </g>
      </svg>
    </div>

    <aside v-if="selectedNode" class="mindMapExplanation">
      <span class="mindMapExplanationIcon" aria-hidden="true">
        {{ selectedNode.icon }}
      </span>
      <div>
        <p class="eyebrow">EXPLICAÇÃO DO RAMO</p>
        <strong>{{ selectedNode.label }}</strong>
        <p>
          {{ selectedNode.detail || 'Este é um ponto importante para revisar nesta lição.' }}
        </p>
      </div>
    </aside>
  </section>
</template>
