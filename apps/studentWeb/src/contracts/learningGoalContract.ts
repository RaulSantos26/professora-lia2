export type LearningGoalType =
  | 'TEST' | 'EXAM' | 'REVIEW' | 'PROJECT'
  | 'COURSE' | 'CERTIFICATION' | 'OTHER'

export interface LearningGoalContract {
  contractName: 'LearningGoal.v1'
  learningGoalId: string
  studentId: string
  studentLearningContextId: string | null
  goalType: LearningGoalType
  title: string
  description: string | null
  targetDate: string | null
  priority: number
  status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED' | 'ARCHIVED'
  completedAt: string | null
  createdAt: string
  updatedAt: string
}

export interface LearningGoalCreateContract {
  contractName: 'LearningGoalCreate.v1'
  studentLearningContextId: string | null
  goalType: LearningGoalType
  title: string
  description: string | null
  targetDate: string | null
  priority: number
}
