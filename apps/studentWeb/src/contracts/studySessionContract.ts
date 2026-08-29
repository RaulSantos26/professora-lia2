export type StudySessionType = 'STUDY' | 'REVIEW' | 'PRACTICE' | 'MOCK_EXAM'

export interface StudySessionContract {
  contractName: 'StudySession.v1'
  studySessionId: string
  studyScopeId: string
  studentId: string
  sessionType: StudySessionType
  status: 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  startedAt: string
  endedAt: string | null
  notes: string | null
  createdAt: string
  updatedAt: string
}

export interface StudySessionItemContract {
  contractName: 'StudySessionItem.v1'
  studySessionItemId: string
  studySessionId: string
  studyScopeItemId: string
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED'
  timeSpentSeconds: number
  startedAt: string | null
  completedAt: string | null
  notes: string | null
  createdAt: string
  updatedAt: string
}

export interface StudySessionViewContract {
  contractName: 'StudySessionView.v1'
  session: StudySessionContract
  items: StudySessionItemContract[]
}
