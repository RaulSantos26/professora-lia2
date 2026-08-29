import type { ErrorContract } from '../contracts/errorContract'
import type { LearningGuideContract } from '../contracts/learningGuideContract'

export class LearningGuideApiService {
  async getGuide(studentId: string): Promise<LearningGuideContract> {
    const response = await fetch(`/api/students/${studentId}/learning-guide`, {
      headers: { Accept: 'application/json' }
    })

    if (response.ok) {
      return await response.json() as LearningGuideContract
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
