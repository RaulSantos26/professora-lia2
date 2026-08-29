import type {
  AgentConversationContract,
  AgentRunContract,
  AgentThreadContract
} from '../contracts/agentTutorContract'
import { LiaApiError } from './materialApiService'

export class AgentTutorApiService {
  async createThread(
    studentId: string,
    request: {
      title: string | null
      studentLearningContextId: string | null
      studentSubjectId: string | null
      studentLearningUnitId: string | null
    }
  ): Promise<AgentThreadContract> {
    return await this.request<AgentThreadContract>(
      `/api/students/${studentId}/lia/threads`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'AgentThreadCreate.v1',
          ...request
        })
      }
    )
  }

  async listThreads(
    studentId: string
  ): Promise<AgentThreadContract[]> {
    return await this.request<AgentThreadContract[]>(
      `/api/students/${studentId}/lia/threads`
    )
  }

  async getConversation(
    studentId: string,
    threadId: string
  ): Promise<AgentConversationContract> {
    return await this.request<AgentConversationContract>(
      `/api/students/${studentId}/lia/threads/${threadId}`
    )
  }

  async sendMessage(
    studentId: string,
    threadId: string,
    request: {
      content: string
      requestedTextModelId: string | null
      thinkingMode: 'AUTO' | 'ON' | 'OFF'
      materialIds: string[]
    }
  ): Promise<AgentRunContract> {
    return await this.request<AgentRunContract>(
      `/api/students/${studentId}/lia/threads/${threadId}/messages`,
      {
        method: 'POST',
        body: JSON.stringify({
          contractName: 'AgentMessageCreate.v1',
          ...request
        })
      }
    )
  }

  async archiveThread(
    studentId: string,
    threadId: string
  ): Promise<void> {
    await this.request<void>(
      `/api/students/${studentId}/lia/threads/${threadId}`,
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
