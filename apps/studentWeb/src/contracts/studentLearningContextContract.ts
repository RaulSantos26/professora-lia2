import type { LearningContextContract } from './learningContextContract'

export interface StudentLearningContextContract {
  contractName: 'StudentLearningContext.v1'
  studentLearningContextId: string
  studentId: string
  learningContextId: string
  academicStageId: string | null
  status: 'ACTIVE' | 'INACTIVE' | 'COMPLETED'
  enrolledAt: string
  completedAt: string | null
  createdAt: string
  updatedAt: string
}

export interface StudentLearningContextViewContract {
  contractName: 'StudentLearningContextView.v1'
  association: StudentLearningContextContract
  context: LearningContextContract
}
