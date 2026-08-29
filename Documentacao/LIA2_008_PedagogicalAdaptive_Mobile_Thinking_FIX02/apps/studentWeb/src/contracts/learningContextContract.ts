export type LearningContextType =
  | 'REGULAR_EDUCATION'
  | 'ENEM'
  | 'VESTIBULAR'
  | 'PUBLIC_EXAM'
  | 'GRADUATION'
  | 'POSTGRAD'
  | 'FREE_COURSE'
  | 'OTHER'

export interface LearningContextContract {
  contractName: 'LearningContext.v1'
  learningContextId: string
  contextType: LearningContextType
  code: string
  name: string
  description: string | null
  status: 'ACTIVE' | 'INACTIVE'
  startsAt: string | null
  endsAt: string | null
  createdAt: string
  updatedAt: string
}

export interface LearningContextCreateContract {
  contractName: 'LearningContextCreate.v1'
  contextType: LearningContextType
  code: string
  name: string
  description: string | null
  startsAt: string | null
  endsAt: string | null
}
