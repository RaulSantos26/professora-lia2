export interface StudyScopeContract {
  contractName: 'StudyScope.v1'
  studyScopeId: string
  learningGoalId: string
  name: string
  description: string | null
  status: 'DRAFT' | 'ACTIVE' | 'COMPLETED' | 'ARCHIVED'
  createdAt: string
  updatedAt: string
}

export interface StudyScopeCreateContract {
  contractName: 'StudyScopeCreate.v1'
  name: string
  description: string | null
}
