import type { ErrorContract } from '../contracts/errorContract'
import type {
  LearningContextSubjectViewContract
} from '../contracts/learningContextSubjectContract'
import type {
  LearningUnitContract,
  LearningUnitCreateContract
} from '../contracts/learningUnitContract'
import type {
  SubjectContract,
  SubjectCreateContract
} from '../contracts/subjectContract'

export class ContentStructureApiService {
  async listSubjects(): Promise<SubjectContract[]> {
    return await this.request<SubjectContract[]>('/api/subjects')
  }

  async createSubject(
    payload: SubjectCreateContract
  ): Promise<SubjectContract> {
    return await this.request<SubjectContract>(
      '/api/subjects',
      {
        method: 'POST',
        body: JSON.stringify(payload)
      }
    )
  }

  async listContextSubjects(
    learningContextId: string
  ): Promise<LearningContextSubjectViewContract[]> {
    return await this.request<LearningContextSubjectViewContract[]>(
      `/api/learning-contexts/${learningContextId}/subjects`
    )
  }

  async assignSubject(
    learningContextId: string,
    subjectId: string
  ): Promise<LearningContextSubjectViewContract> {
    return await this.request<LearningContextSubjectViewContract>(
      `/api/learning-contexts/${learningContextId}/subjects/${subjectId}`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'LearningContextSubjectCreate.v1',
          displayOrder: null
        })
      }
    )
  }

  async listLearningUnits(
    learningContextSubjectId: string
  ): Promise<LearningUnitContract[]> {
    return await this.request<LearningUnitContract[]>(
      `/api/context-subjects/${learningContextSubjectId}/units`
    )
  }

  async createLearningUnit(
    learningContextSubjectId: string,
    payload: LearningUnitCreateContract
  ): Promise<LearningUnitContract> {
    return await this.request<LearningUnitContract>(
      `/api/context-subjects/${learningContextSubjectId}/units`,
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
