import type { ErrorContract } from '../contracts/errorContract'
import type {
  StudentLearningUnitContract,
  StudentLearningUnitCreateContract
} from '../contracts/studentLearningUnitContract'
import type {
  StudentSubjectContract,
  StudentSubjectCreateContract
} from '../contracts/studentSubjectContract'

export class StudentContentApiService {
  async listSubjects(
    studentLearningContextId: string
  ): Promise<StudentSubjectContract[]> {
    return await this.request<StudentSubjectContract[]>(
      `/api/student-learning-contexts/${studentLearningContextId}/subjects`
    )
  }

  async createSubject(
    studentLearningContextId: string,
    payload: StudentSubjectCreateContract
  ): Promise<StudentSubjectContract> {
    return await this.request<StudentSubjectContract>(
      `/api/student-learning-contexts/${studentLearningContextId}/subjects`,
      {
        method: 'POST',
        body: JSON.stringify(payload)
      }
    )
  }

  async listLearningUnits(
    studentSubjectId: string
  ): Promise<StudentLearningUnitContract[]> {
    return await this.request<StudentLearningUnitContract[]>(
      `/api/student-subjects/${studentSubjectId}/units`
    )
  }

  async createLearningUnit(
    studentSubjectId: string,
    payload: StudentLearningUnitCreateContract
  ): Promise<StudentLearningUnitContract> {
    return await this.request<StudentLearningUnitContract>(
      `/api/student-subjects/${studentSubjectId}/units`,
      {
        method: 'POST',
        body: JSON.stringify(payload)
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
      // Fallback sem dependência do payload.
    }

    throw new Error(
      errorPayload?.message ?? `Falha HTTP ${response.status}`
    )
  }
}
