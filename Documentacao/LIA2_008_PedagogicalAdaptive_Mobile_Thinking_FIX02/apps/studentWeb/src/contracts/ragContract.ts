export interface RagEvidenceHitContract {
  contractName: 'RagEvidenceHit.v1'
  evidenceId: string | null
  materialId: string
  materialTitle: string
  locator: string
  excerpt: string
  score: number
}

export interface RagQueryResponseContract {
  contractName: 'RagQueryResponse.v1'
  answer: string
  citations: number[]
  textModelId: string
  embeddingModelId: string
  thinkingMode: 'AUTO' | 'ON' | 'OFF'
  thinkingEnabled: boolean
  evidence: RagEvidenceHitContract[]
}
