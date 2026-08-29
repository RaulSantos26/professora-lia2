import type {
  VisualTaskContract
} from '../contracts/visualTaskContract'
import { LiaApiError } from './materialApiService'

export class VisualTaskApiService {
  async get(
    studentId: string,
    visualTaskId: string
  ): Promise<VisualTaskContract> {
    const response = await fetch(
      `/api/students/${studentId}/visual-tasks/${visualTaskId}`,
      {
        headers: {
          Accept: 'application/json'
        }
      }
    )

    if (response.ok) {
      return await response.json() as VisualTaskContract
    }

    let payload: {
      message?: string
      code?: string
      correlationId?: string | null
    } | null = null

    try {
      payload = await response.json()
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
