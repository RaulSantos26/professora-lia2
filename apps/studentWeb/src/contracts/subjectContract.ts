export interface SubjectContract {
  contractName: 'Subject.v1'
  subjectId: string
  code: string
  name: string
  description: string | null
  status: 'ACTIVE' | 'INACTIVE'
  createdAt: string
  updatedAt: string
}

export interface SubjectCreateContract {
  contractName: 'SubjectCreate.v1'
  code: string
  name: string
  description: string | null
}
