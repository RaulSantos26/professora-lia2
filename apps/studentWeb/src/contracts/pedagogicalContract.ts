export type PedagogicalArtifactType =
  | 'TEACH'
  | 'EXPLAIN'
  | 'SUMMARY'
  | 'MIND_MAP'
  | 'FLASHCARDS'
  | 'EXERCISES'
  | 'QUIZ'

export interface PedagogicalEvidenceContract {
  evidenceId: string | null
  materialId: string
  materialTitle: string
  locator: string
  excerpt: string
}

export interface PedagogicalArtifactContract {
  contractName: 'PedagogicalArtifact.v1'
  pedagogicalArtifactId: string
  studentId: string
  artifactType: PedagogicalArtifactType
  status: 'QUEUED' | 'RUNNING' | 'READY' | 'FAILED' | 'ARCHIVED'
  progressPercent: number
  message: string
  title: string
  instruction: string | null
  difficulty: string | null
  questionCount: number | null
  requestedTextModelId: string | null
  effectiveTextModelId: string | null
  thinkingMode: 'AUTO' | 'ON' | 'OFF'
  effectiveThinkingEnabled: boolean | null
  sourceMaterialIds: string[]
  sourceEvidence: PedagogicalEvidenceContract[]
  content: Record<string, unknown> | null
  errorCode: string | null
  errorMessage: string | null
  createdAt: string
  startedAt: string | null
  finishedAt: string | null
}

export interface LearningQuestionResultContract {
  questionId: string
  correct: boolean
  submittedAnswer: string
  correctAnswer: string
  explanation: string
}

export interface LearningAttemptContract {
  contractName: 'LearningAttempt.v1'
  learningAttemptId: string
  studentId: string
  pedagogicalArtifactId: string
  attemptType: 'EXERCISES' | 'QUIZ'
  scorePercent: number
  correctCount: number
  totalCount: number
  results: LearningQuestionResultContract[]
  adaptiveMessage: string
  updatedUnitIds: string[]
  createdAt: string
  completedAt: string
}
