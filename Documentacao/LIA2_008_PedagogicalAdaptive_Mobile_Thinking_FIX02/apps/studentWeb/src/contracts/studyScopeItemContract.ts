export interface StudyScopeCandidateContract {
  contractName: 'StudyScopeCandidate.v1'
  studentLearningContextId: string
  contextName: string
  studentSubjectId: string
  subjectName: string
  studentLearningUnitId: string
  unitCode: string
  unitTitle: string
  unitType: string
  isSelected: boolean
  studyScopeItemId: string | null
}
