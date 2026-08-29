import type { SubjectContract } from './subjectContract'

export interface LearningContextSubjectContract {
  contractName: 'LearningContextSubject.v1'
  learningContextSubjectId: string
  learningContextId: string
  subjectId: string
  displayOrder: number | null
  status: 'ACTIVE' | 'INACTIVE'
  createdAt: string
  updatedAt: string
}

export interface LearningContextSubjectViewContract {
  contractName: 'LearningContextSubjectView.v1'
  association: LearningContextSubjectContract
  subject: SubjectContract
}
