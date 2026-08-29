export interface AgentThreadContract {
  contractName: 'AgentThread.v1'
  agentThreadId: string
  studentId: string
  studentLearningContextId: string | null
  studentSubjectId: string | null
  studentLearningUnitId: string | null
  title: string
  status: 'ACTIVE' | 'ARCHIVED'
  memory: Record<string, unknown>
  createdAt: string
  updatedAt: string
  lastMessageAt: string | null
}

export interface AgentMessageContract {
  contractName: 'AgentMessage.v1'
  agentMessageId: string
  agentThreadId: string
  role: 'USER' | 'ASSISTANT'
  content: string
  citations: Array<Record<string, unknown>>
  visualTaskIds: string[]
  actions: Array<Record<string, unknown>>
  createdAt: string
}

export interface AgentRunContract {
  contractName: 'AgentRun.v1'
  agentRunId: string
  agentThreadId: string
  userMessageId: string
  assistantMessageId: string | null
  status: 'QUEUED' | 'RUNNING' | 'READY' | 'FAILED' | 'CANCELLED'
  stage: string
  progressPercent: number
  message: string
  requestedTextModelId: string | null
  effectiveTextModelId: string | null
  thinkingMode: 'AUTO' | 'ON' | 'OFF'
  effectiveThinkingEnabled: boolean | null
  plan: Record<string, unknown> | null
  errorCode: string | null
  errorMessage: string | null
  createdAt: string
  startedAt: string | null
  finishedAt: string | null
}

export interface AgentConversationContract {
  contractName: 'AgentConversation.v1'
  thread: AgentThreadContract
  messages: AgentMessageContract[]
  activeRun: AgentRunContract | null
}
