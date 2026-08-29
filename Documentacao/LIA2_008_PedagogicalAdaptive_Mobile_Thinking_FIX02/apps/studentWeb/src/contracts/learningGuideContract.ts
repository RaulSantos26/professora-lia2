import type { EducationWorkspaceSection } from '../types/educationWorkspaceSection'

export type LearningGuideStepStatus =
  | 'COMPLETE'
  | 'NEXT'
  | 'AVAILABLE'
  | 'OPTIONAL'
  | 'BLOCKED'

export interface LearningGuideStepContract {
  contractName: 'LearningGuideStep.v1'
  section: Exclude<EducationWorkspaceSection, 'STUDENT'>
  title: string
  description: string
  status: LearningGuideStepStatus
  actionLabel: string
}

export interface LearningGuideContract {
  contractName: 'LearningGuide.v1'
  recommendedSection: Exclude<EducationWorkspaceSection, 'STUDENT'>
  headline: string
  message: string
  completedSteps: number
  totalSteps: number
  steps: LearningGuideStepContract[]
}
