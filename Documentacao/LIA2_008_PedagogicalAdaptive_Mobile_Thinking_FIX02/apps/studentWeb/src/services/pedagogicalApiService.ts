import type {
  LearningAttemptContract,
  PedagogicalArtifactContract,
  PedagogicalArtifactType
} from '../contracts/pedagogicalContract'
import { LiaApiError } from './materialApiService'

export interface CreatePedagogicalArtifactRequest {
  artifactType: PedagogicalArtifactType
  title: string | null
  instruction: string | null
  materialIds: string[]
  difficulty: 'AUTO' | 'EASY' | 'MEDIUM' | 'HARD'
  questionCount: number
  requestedTextModelId: string | null
  thinkingMode: 'AUTO' | 'ON' | 'OFF'
}

export class PedagogicalApiService {
  async createArtifact(
    studentId: string,
    request: CreatePedagogicalArtifactRequest
  ): Promise<PedagogicalArtifactContract> {
    return await this.request<PedagogicalArtifactContract>(
      `/api/students/${studentId}/pedagogical/artifacts`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'PedagogicalArtifactCreate.v1',
          ...request
        })
      }
    )
  }

  async listArtifacts(
    studentId: string
  ): Promise<PedagogicalArtifactContract[]> {
    return await this.request<PedagogicalArtifactContract[]>(
      `/api/students/${studentId}/pedagogical/artifacts`
    )
  }

  async getArtifact(
    studentId: string,
    artifactId: string
  ): Promise<PedagogicalArtifactContract> {
    return await this.request<PedagogicalArtifactContract>(
      `/api/students/${studentId}/pedagogical/artifacts/${artifactId}`
    )
  }

  async submitAttempt(
    studentId: string,
    artifactId: string,
    answers: Record<string, string>
  ): Promise<LearningAttemptContract> {
    return await this.request<LearningAttemptContract>(
      `/api/students/${studentId}/pedagogical/artifacts/${artifactId}/attempts`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'LearningAttemptSubmit.v1',
          answers
        })
      }
    )
  }

  async archiveArtifact(
    studentId: string,
    artifactId: string
  ): Promise<void> {
    await this.request<void>(
      `/api/students/${studentId}/pedagogical/artifacts/${artifactId}`,
      { method: 'DELETE' }
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
      if (response.status === 204) {
        return undefined as T
      }

      return await response.json() as T
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
