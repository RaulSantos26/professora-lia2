<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

interface MindNode {
  nodeId: string
  parentId: string | null
  label: string
  detail: string
  evidenceRefs?: number[]
}

const nodes = computed(
  () => (
    Array.isArray(props.content.nodes)
      ? props.content.nodes as MindNode[]
      : []
  )
)

const rootId = computed(
  () => String(
    props.content.rootId
    ?? nodes.value.find(node => node.parentId === null)?.nodeId
    ?? ''
  )
)

const rootNode = computed(
  () => nodes.value.find(node => node.nodeId === rootId.value) ?? null
)

const branches = computed(
  () => nodes.value.filter(
    node => node.parentId === rootId.value
  )
)

function children(parentId: string): MindNode[] {
  return nodes.value.filter(node => node.parentId === parentId)
}
</script>

<template>
  <div class="mindMapCanvas">
    <article
      v-if="rootNode"
      class="mindMapRoot"
    >
      <strong>{{ rootNode.label }}</strong>
      <p>{{ rootNode.detail }}</p>
    </article>

    <div class="mindMapBranches">
      <section
        v-for="branch in branches"
        :key="branch.nodeId"
        class="mindMapBranch"
      >
        <article class="mindMapBranchHead">
          <strong>{{ branch.label }}</strong>
          <p>{{ branch.detail }}</p>
        </article>

        <div class="mindMapLeaves">
          <article
            v-for="leaf in children(branch.nodeId)"
            :key="leaf.nodeId"
            class="mindMapLeaf"
          >
            <strong>{{ leaf.label }}</strong>
            <p>{{ leaf.detail }}</p>

            <div
              v-if="children(leaf.nodeId).length > 0"
              class="mindMapNestedLeaves"
            >
              <span
                v-for="nested in children(leaf.nodeId)"
                :key="nested.nodeId"
              >
                <b>{{ nested.label }}</b>
                {{ nested.detail }}
              </span>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>
