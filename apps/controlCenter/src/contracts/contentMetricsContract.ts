export interface ContentMetricsContract {
  contractName: 'ContentMetrics.v4'
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
  agentThreads: number
  agentRunsActive: number
  agentRunsFailed: number
  agentToolCalls: number
  visualTasks: number
  errorType: string | null
}
