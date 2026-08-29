export type LearningStateStatus =
  | 'NOT_STARTED' | 'LEARNING' | 'REVIEWING' | 'MASTERED'

export interface StudentLearningStateContract {
  contractName: 'StudentLearningState.v1'
  studentLearningStateId: string
  studentId: string
  studentLearningUnitId: string
  status: LearningStateStatus
  masteryLevel: number
  confidenceLevel: number
  studyCount: number
  lastStudiedAt: string | null
  nextReviewAt: string | null
  createdAt: string
  updatedAt: string
}

export interface StudentLearningStateViewContract {
  contractName: 'StudentLearningStateView.v1'
  studentLearningContextId: string
  contextName: string
  studentSubjectId: string
  subjectName: string
  studentLearningUnitId: string
  unitCode: string
  unitTitle: string
  state: StudentLearningStateContract | null
}
