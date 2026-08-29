export type StudentLearningUnitType =
  | 'LESSON'
  | 'MODULE'
  | 'CHAPTER'
  | 'SECTION'

export type StudentLearningUnitStatus =
  | 'DRAFT'
  | 'ACTIVE'
  | 'INACTIVE'
  | 'ARCHIVED'

export interface StudentLearningUnitContract {
  contractName: 'StudentLearningUnit.v1'
  studentLearningUnitId: string
  studentSubjectId: string
  parentStudentLearningUnitId: string | null
  unitType: StudentLearningUnitType
  code: string
  title: string
  description: string | null
  displayOrder: number | null
  status: StudentLearningUnitStatus
  createdAt: string
  updatedAt: string
}

export interface StudentLearningUnitCreateContract {
  contractName: 'StudentLearningUnitCreate.v1'
  parentStudentLearningUnitId: string | null
  unitType: StudentLearningUnitType
  code: string
  title: string
  description: string | null
  displayOrder: number | null
  status: StudentLearningUnitStatus
}
