export type StudentStatus = 'ACTIVE' | 'INACTIVE'

export interface StudentContract {
  contractName: 'Student.v1'
  studentId: string
  fullName: string
  preferredName: string | null
  status: StudentStatus
  createdAt: string
  updatedAt: string
}

export interface StudentCreateContract {
  contractName: 'StudentCreate.v1'
  fullName: string
  preferredName: string | null
}
