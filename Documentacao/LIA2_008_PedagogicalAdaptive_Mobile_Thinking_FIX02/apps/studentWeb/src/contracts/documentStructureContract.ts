export interface DocumentBlockViewContract {
  contractName: 'DocumentBlockView.v1'
  documentBlockId: string
  sequenceNumber: number
  blockType: string
  textContent: string | null
  processingStatus: string
  orientationDegrees: number | null
  visionModelId: string | null
  visionThinkingEnabled: boolean | null
}

export interface DocumentPageViewContract {
  contractName: 'DocumentPageView.v1'
  documentPageId: string
  pageNumber: number
  nativeText: string | null
  status: string
  blocks: DocumentBlockViewContract[]
}

export interface DocumentStructureContract {
  contractName: 'DocumentStructure.v2'
  documentId: string
  documentVersionId: string
  extractionStatus: string
  pageCount: number
  pages: DocumentPageViewContract[]
  evidenceCount: number
  chunkCount: number
  embeddedChunkCount: number
  visualPendingCount: number
}
