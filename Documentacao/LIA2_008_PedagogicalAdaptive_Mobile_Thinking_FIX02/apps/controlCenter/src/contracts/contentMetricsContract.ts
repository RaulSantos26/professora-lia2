export interface ContentMetricsContract {
  contractName: 'ContentMetrics.v3'
  available: boolean
  students: number
  materials: number
  documentPages: number
  textBlocks: number
  visualPendingBlocks: number
  embeddedChunks: number
  chunksPendingEmbedding: number
  processingJobs: number
  failedJobs: number
  learningGoals: number
  studySessions: number
  pedagogicalArtifacts: number
  pedagogicalJobsActive: number
  pedagogicalJobsFailed: number
  learningAttempts: number
  errorType: string | null
}
