export type MaterialStatus =
  | 'UPLOADED'
  | 'PROCESSING'
  | 'PARTIAL'
  | 'READY'
  | 'ERROR'
  | 'ARCHIVED'

export interface MaterialContract {
  contractName: 'Material.v3'
  materialId: string
  studentId: string
  studentLearningContextId: string | null
  studentSubjectId: string | null
  studentLearningUnitId: string | null
  title: string
  materialType: 'PDF' | 'IMAGE' | 'TEXT' | 'DOCUMENT' | 'OTHER'
  sourceType: 'UPLOAD' | 'MANUAL' | 'LINK'
  description: string | null
  status: MaterialStatus
  analysisRequested: boolean
  studyEnabled: boolean
  requestedModelId: string | null
  aiMode: 'AUTO' | 'FIXED' | 'CUSTOM'
  fixedModelId: string | null
  textModelId: string | null
  visionModelId: string | null
  embeddingModelId: string | null
  thinkingMode: 'AUTO' | 'ON' | 'OFF'
  sourceGroupId: string | null
  sourceSequence: number | null
  lastProcessingErrorCode: string | null
  lastProcessingErrorMessage: string | null
  createdAt: string
  updatedAt: string
}

export interface MaterialUploadResultContract {
  contractName: 'MaterialUploadResult.v2'
  material: MaterialContract
  file: {
    contractName: 'MaterialFile.v1'
    materialFileId: string
    materialId: string
    originalFileName: string
    mimeType: string
    sizeBytes: number
    sha256: string
    status: 'ACTIVE' | 'SUPERSEDED' | 'ERROR'
    createdAt: string
  }
  documentId: string | null
  documentVersionId: string | null
  pageCount: number
  textBlockCount: number
  visualPendingCount: number
  chunkCount: number
  analysisPerformed: boolean
}

export interface MaterialBatchItemContract {
  contractName: 'MaterialBatchItem.v1'
  fileName: string
  success: boolean
  result: MaterialUploadResultContract | null
  errorCode: string | null
  errorMessage: string | null
}

export interface MaterialBatchUploadResultContract {
  contractName: 'MaterialBatchUploadResult.v1'
  totalFiles: number
  successCount: number
  errorCount: number
  items: MaterialBatchItemContract[]
}
