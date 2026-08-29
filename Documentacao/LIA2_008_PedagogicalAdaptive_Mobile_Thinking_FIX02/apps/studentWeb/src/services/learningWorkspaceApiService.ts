import type { ErrorContract } from '../contracts/errorContract'
import type {
  LearningGoalContract,
  LearningGoalCreateContract
} from '../contracts/learningGoalContract'
import type {
  LearningStateStatus,
  StudentLearningStateContract,
  StudentLearningStateViewContract
} from '../contracts/studentLearningStateContract'
import type {
  StudyScopeContract,
  StudyScopeCreateContract
} from '../contracts/studyScopeContract'
import type { StudyScopeCandidateContract } from '../contracts/studyScopeItemContract'
import type {
  StudySessionType,
  StudySessionViewContract
} from '../contracts/studySessionContract'

export class LearningWorkspaceApiService {
  async listGoals(studentId: string): Promise<LearningGoalContract[]> {
    return await this.request<LearningGoalContract[]>(
      `/api/students/${studentId}/learning-goals`
    )
  }

  async createGoal(
    studentId: string,
    payload: LearningGoalCreateContract
  ): Promise<LearningGoalContract> {
    return await this.request<LearningGoalContract>(
      `/api/students/${studentId}/learning-goals`,
      { method: 'POST', body: JSON.stringify(payload) }
    )
  }

  async listScopes(goalId: string): Promise<StudyScopeContract[]> {
    return await this.request<StudyScopeContract[]>(
      `/api/learning-goals/${goalId}/study-scopes`
    )
  }

  async createScope(
    goalId: string,
    payload: StudyScopeCreateContract
  ): Promise<StudyScopeContract> {
    return await this.request<StudyScopeContract>(
      `/api/learning-goals/${goalId}/study-scopes`,
      { method: 'POST', body: JSON.stringify(payload) }
    )
  }

  async listCandidates(
    goalId: string,
    scopeId: string | null
  ): Promise<StudyScopeCandidateContract[]> {
    const suffix = scopeId
      ? `?studyScopeId=${encodeURIComponent(scopeId)}`
      : ''

    return await this.request<StudyScopeCandidateContract[]>(
      `/api/learning-goals/${goalId}/scope-candidates${suffix}`
    )
  }

  async addScopeItem(scopeId: string, unitId: string): Promise<void> {
    await this.request(
      `/api/study-scopes/${scopeId}/items`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'StudyScopeItemCreate.v1',
          studentLearningUnitId: unitId,
          displayOrder: null,
          isRequired: true
        })
      }
    )
  }

  async removeScopeItem(scopeId: string, itemId: string): Promise<void> {
    await this.request(
      `/api/study-scopes/${scopeId}/items/${itemId}`,
      { method: 'DELETE' },
      false
    )
  }

  async listSessions(scopeId: string): Promise<StudySessionViewContract[]> {
    return await this.request<StudySessionViewContract[]>(
      `/api/study-scopes/${scopeId}/sessions`
    )
  }

  async startSession(
    scopeId: string,
    sessionType: StudySessionType
  ): Promise<StudySessionViewContract> {
    return await this.request<StudySessionViewContract>(
      `/api/study-scopes/${scopeId}/sessions`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'StudySessionStart.v1',
          sessionType,
          notes: null
        })
      }
    )
  }

  async completeSession(sessionId: string): Promise<StudySessionViewContract> {
    return await this.request<StudySessionViewContract>(
      `/api/study-sessions/${sessionId}/complete`,
      { method: 'POST' }
    )
  }

  async listLearningStates(
    studentId: string
  ): Promise<StudentLearningStateViewContract[]> {
    return await this.request<StudentLearningStateViewContract[]>(
      `/api/students/${studentId}/learning-states`
    )
  }

  async updateLearningState(
    studentId: string,
    unitId: string,
    status: LearningStateStatus,
    masteryLevel: number,
    confidenceLevel: number
  ): Promise<StudentLearningStateContract> {
    return await this.request<StudentLearningStateContract>(
      `/api/students/${studentId}/learning-units/${unitId}/state`,
      {
        method: 'PUT',
        body: JSON.stringify({
          contractName: 'StudentLearningStateUpdate.v1',
          status,
          masteryLevel,
          confidenceLevel,
          nextReviewAt: null
        })
      }
    )
  }

  private async request<T>(
    url: string,
    options: RequestInit = {},
    expectJson = true
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
      if (!expectJson || response.status === 204) {
        return undefined as T
      }
      return await response.json() as T
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
