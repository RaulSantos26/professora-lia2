export type LearningUnitType = 'LESSON' | 'MODULE' | 'CHAPTER' | 'SECTION'
export type LearningUnitStatus = 'DRAFT' | 'ACTIVE' | 'INACTIVE' | 'ARCHIVED'

export interface LearningUnitContract {
  contractName: 'LearningUnit.v1'
  learningUnitId: string
  learningContextSubjectId: string
  parentLearningUnitId: string | null
  unitType: LearningUnitType
  code: string
  title: string
  description: string | null
  displayOrder: number | null
  status: LearningUnitStatus
  createdAt: string
  updatedAt: string
}

export interface LearningUnitCreateContract {
  contractName: 'LearningUnitCreate.v1'
  parentLearningUnitId: string | null
  unitType: LearningUnitType
  code: string
  title: string
  description: string | null
  displayOrder: number | null
  status: LearningUnitStatus
}
