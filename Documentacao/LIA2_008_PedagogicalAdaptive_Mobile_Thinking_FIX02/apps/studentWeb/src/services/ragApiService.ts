import type { ErrorContract } from '../contracts/errorContract'
import type { RagQueryResponseContract } from '../contracts/ragContract'
import { LiaApiError } from './materialApiService'

export interface RagQueryRequest {
  query: string
  topK: number
  requestedModelId: string | null
  thinkingMode: 'AUTO' | 'ON' | 'OFF'
  studentLearningContextId: string | null
  studentSubjectId: string | null
  studentLearningUnitId: string | null
  materialIds: string[]
}

export class RagApiService {
  async query(
    studentId: string,
    request: RagQueryRequest
  ): Promise<RagQueryResponseContract> {
    const response = await fetch(
      `/api/students/${studentId}/rag/query`,
      {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contractName: 'RagQueryRequest.v1',
          ...request
        })
      }
    )

    if (response.ok) {
      return await response.json() as RagQueryResponseContract
    }

    let payload: ErrorContract | null = null

    try {
      payload = await response.json() as ErrorContract
    } catch {
      // fallback
    }

    throw new LiaApiError(
      payload?.message ?? `Falha HTTP ${response.status}`,
      payload?.code ?? `HTTP_${response.status}`,
      payload?.correlationId ?? null
    )
  }
}
