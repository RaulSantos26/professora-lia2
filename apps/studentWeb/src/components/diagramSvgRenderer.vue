<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  spec: Record<string, unknown>
}>()

interface DiagramNode {
  nodeId: string
  label: string
  detail: string
  x: number
  y: number
}

interface DiagramEdge {
  sourceId: string
  targetId: string
  label: string
}

const selectedId = ref<string | null>(null)

const nodes = computed(
  () => (
    Array.isArray(props.spec.nodes)
      ? props.spec.nodes as DiagramNode[]
      : []
  )
)

const edges = computed(
  () => (
    Array.isArray(props.spec.edges)
      ? props.spec.edges as DiagramEdge[]
      : []
  )
)

const selected = computed(
  () => nodes.value.find(
    node => node.nodeId === selectedId.value
  ) ?? null
)

function nodeById(id: string) {
  return nodes.value.find(node => node.nodeId === id)
}
</script>

<template>
  <section class="diagramVisual">
    <svg
      viewBox="0 0 1200 700"
      role="img"
      aria-label="Diagrama interativo"
    >
      <defs>
        <marker
          id="liaArrow"
          markerWidth="10"
          markerHeight="10"
          refX="8"
          refY="3"
          orient="auto"
        >
          <path d="M0,0 L0,6 L9,3 z" />
        </marker>
      </defs>

      <g
        v-for="(edge, index) in edges"
        :key="`${edge.sourceId}-${edge.targetId}-${index}`"
      >
        <line
          v-if="
            nodeById(edge.sourceId)
            && nodeById(edge.targetId)
          "
          :x1="nodeById(edge.sourceId)?.x"
          :y1="nodeById(edge.sourceId)?.y"
          :x2="nodeById(edge.targetId)?.x"
          :y2="nodeById(edge.targetId)?.y"
          class="diagramEdge"
          marker-end="url(#liaArrow)"
        />
      </g>

      <g
        v-for="node in nodes"
        :key="node.nodeId"
        class="diagramNode"
        :data-selected="selectedId === node.nodeId"
        :transform="`translate(${node.x} ${node.y})`"
        @click="selectedId = node.nodeId"
      >
        <rect
          x="-100"
          y="-40"
          width="200"
          height="80"
          rx="12"
        />
        <foreignObject
          x="-92"
          y="-32"
          width="184"
          height="64"
        >
          <div class="diagramNodeLabel">
            {{ node.label }}
          </div>
        </foreignObject>
      </g>
    </svg>

    <aside v-if="selected" class="visualInspector">
      <strong>{{ selected.label }}</strong>
      <p>{{ selected.detail }}</p>
    </aside>
  </section>
</template>
