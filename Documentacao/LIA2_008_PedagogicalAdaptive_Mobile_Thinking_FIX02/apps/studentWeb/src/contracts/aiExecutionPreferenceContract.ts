export type AiExecutionMode = 'AUTO' | 'FIXED' | 'CUSTOM'
export type ThinkingMode = 'AUTO' | 'ON' | 'OFF'

export interface AiExecutionPreferenceContract {
  contractName: 'AiExecutionPreference.v1'
  mode: AiExecutionMode
  fixedModelId: string | null
  textModelId: string | null
  visionModelId: string | null
  embeddingModelId: string | null
  thinkingMode: ThinkingMode
}
