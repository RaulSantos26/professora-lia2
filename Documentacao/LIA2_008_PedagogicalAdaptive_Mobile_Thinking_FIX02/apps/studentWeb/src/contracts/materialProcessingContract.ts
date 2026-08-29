export type MaterialProcessingStatus =
  | 'QUEUED'
  | 'RUNNING'
  | 'COMPLETED'
  | 'COMPLETED_WITH_WARNINGS'
  | 'FAILED'
  | 'CANCELLED'

export interface MaterialProcessingJobContract {
  contractName: 'MaterialProcessingJob.v1'
  materialProcessingJobId: string
  materialId: string
  materialTitle: string | null
  studentId: string
  jobType: 'ANALYZE' | 'INDEX_RAG'
  status: MaterialProcessingStatus
  stage: string
  progressPercent: number
  message: string
  requestedModelId: string | null
  effectiveVisionModelId: string | null
  effectiveEmbeddingModelId: string | null
  fallbackReason: string | null
  errorCode: string | null
  errorMessage: string | null
  createdAt: string
  startedAt: string | null
  finishedAt: string | null
}

export interface MaterialAsyncUploadItemContract {
  contractName: 'MaterialAsyncUploadItem.v1'
  fileName: string
  success: boolean
  materialId: string | null
  materialTitle: string | null
  materialStatus: string | null
  job: MaterialProcessingJobContract | null
  errorCode: string | null
  errorMessage: string | null
}

export interface MaterialAsyncBatchUploadResultContract {
  contractName: 'MaterialAsyncBatchUploadResult.v1'
  totalFiles: number
  successCount: number
  errorCount: number
  items: MaterialAsyncUploadItemContract[]
}
