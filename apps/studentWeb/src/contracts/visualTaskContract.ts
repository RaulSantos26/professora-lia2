export type VisualTaskType =
  | 'MIND_MAP'
  | 'DIAGRAM'
  | 'CHART'
  | 'ANIMATION_2D'
  | 'SCENE_3D'

export interface VisualTaskContract {
  contractName: 'VisualTask.v1'
  visualTaskId: string
  studentId: string
  agentThreadId: string | null
  agentRunId: string | null
  pedagogicalArtifactId: string | null
  visualType: VisualTaskType
  status: 'READY' | 'ARCHIVED'
  title: string
  renderer: 'SVG' | 'CANVAS' | 'THREE'
  spec: Record<string, unknown>
  evidence: Array<Record<string, unknown>>
  sourceMaterialIds: string[]
  effectiveModelId: string | null
  thinkingEnabled: boolean | null
  createdAt: string
}
