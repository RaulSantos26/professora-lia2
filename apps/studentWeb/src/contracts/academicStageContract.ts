export type AcademicStageStatus = 'CURRENT' | 'COMPLETED' | 'CANCELLED'

export interface AcademicStageContract {
  contractName: 'AcademicStage.v1'
  academicStageId: string
  studentId: string
  educationLevel: string
  stageCode: string | null
  stageLabel: string
  startedAt: string | null
  endedAt: string | null
  status: AcademicStageStatus
  createdAt: string
  updatedAt: string
}

export interface AcademicStageCreateContract {
  contractName: 'AcademicStageCreate.v1'
  educationLevel: string
  stageCode: string | null
  stageLabel: string
  startedAt: string | null
  endedAt: string | null
  status: AcademicStageStatus
}
