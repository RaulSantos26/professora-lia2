import type { AiModelRegistryContract } from '../contracts/aiModelContract'
import type { ErrorContract } from '../contracts/errorContract'

export class AiModelApiService {
  async listModels(
    forceRefresh = false
  ): Promise<AiModelRegistryContract> {
    const response = await fetch(
      `/api/ai/models?forceRefresh=${forceRefresh ? 'true' : 'false'}`,
      {
        headers: { Accept: 'application/json' }
      }
    )

    if (response.ok) {
      return await response.json() as AiModelRegistryContract
    }

    let errorPayload: ErrorContract | null = null

    try {
      errorPayload = await response.json() as ErrorContract
    } catch {
      // fallback
    }

    throw new Error(
      errorPayload?.message ?? `Falha HTTP ${response.status}`
    )
  }
}
