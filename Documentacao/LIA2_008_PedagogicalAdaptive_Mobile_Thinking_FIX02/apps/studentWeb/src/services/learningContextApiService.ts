import type {
  LearningContextContract,
  LearningContextCreateContract
} from '../contracts/learningContextContract'
import type {
  StudentLearningContextViewContract
} from '../contracts/studentLearningContextContract'
import type { ErrorContract } from '../contracts/errorContract'

export class LearningContextApiService {
  async listLearningContexts(): Promise<LearningContextContract[]> {
    return await this.request<LearningContextContract[]>(
      '/api/learning-contexts'
    )
  }

  async createLearningContext(
    payload: LearningContextCreateContract
  ): Promise<LearningContextContract> {
    return await this.request<LearningContextContract>(
      '/api/learning-contexts',
      {
        method: 'POST',
        body: JSON.stringify(payload)
      }
    )
  }

  async listStudentLearningContexts(
    studentId: string
  ): Promise<StudentLearningContextViewContract[]> {
    return await this.request<StudentLearningContextViewContract[]>(
      `/api/students/${studentId}/learning-contexts`
    )
  }

  async assignLearningContext(
    studentId: string,
    learningContextId: string,
    academicStageId: string | null
  ): Promise<StudentLearningContextViewContract> {
    return await this.request<StudentLearningContextViewContract>(
      `/api/students/${studentId}/learning-contexts/${learningContextId}`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'StudentLearningContextCreate.v1',
          academicStageId
        })
      }
    )
  }

  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(options.headers ?? {})
      }
    })

    if (response.ok) {
      return await response.json() as T
    }

    let errorPayload: ErrorContract | null = null

    try {
      errorPayload = await response.json() as ErrorContract
    } catch {
      // Fallback sem dependência do payload de erro.
    }

    throw new Error(
      errorPayload?.message ?? `Falha HTTP ${response.status}`
    )
  }
}
