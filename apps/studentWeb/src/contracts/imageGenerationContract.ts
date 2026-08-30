export type ImageGenerationStatus =
  | 'QUEUED'
  | 'PREPARING'
  | 'GENERATING'
  | 'LABELING'
  | 'READY'
  | 'ERROR'
  | 'CANCELLED'

export interface ImageGenerationTaskContract {
  contractName: 'ImageGenerationTask.v1'
  imageTaskId: string
  studentId: string
  agentThreadId: string | null
  agentRunId: string | null
  relatedVisualTaskId: string | null
  imageMode: 'ILLUSTRATION' | 'MIND_MAP_COMPANION'
  status: ImageGenerationStatus
  progressPercent: number
  message: string
  title: string
  labels: string[]
  assetUrl: string | null
  sourceMaterialIds: string[]
  seed: number | null
  elapsedSeconds: number | null
  errorCode: string | null
  errorMessage: string | null
  createdAt: string
  finishedAt: string | null
}
