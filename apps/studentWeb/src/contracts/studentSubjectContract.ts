export interface StudentSubjectContract {
  contractName: 'StudentSubject.v1'
  studentSubjectId: string
  studentLearningContextId: string
  subjectDefinitionId: string | null
  code: string
  name: string
  description: string | null
  status: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED'
  createdAt: string
  updatedAt: string
}

export interface StudentSubjectCreateContract {
  contractName: 'StudentSubjectCreate.v1'
  subjectDefinitionId: string | null
  code: string
  name: string
  description: string | null
}
