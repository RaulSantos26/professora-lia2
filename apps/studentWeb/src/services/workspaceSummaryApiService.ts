import type { ErrorContract } from '../contracts/errorContract'
import type {
  WorkspaceSummaryContract
} from '../contracts/workspaceSummaryContract'

export class WorkspaceSummaryApiService {
  async getSummary(
    studentId: string
  ): Promise<WorkspaceSummaryContract> {
    const response = await fetch(
      `/api/students/${studentId}/workspace-summary`,
      {
        headers: { Accept: 'application/json' }
      }
    )

    if (response.ok) {
      return await response.json() as WorkspaceSummaryContract
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
