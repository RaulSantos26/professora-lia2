export interface AiModelContract {
  contractName: 'AiModel.v1'
  modelId: string
  displayName: string
  provider: string
  capabilities: string[]
  available: boolean
}

export interface AiModelRegistryContract {
  contractName: 'AiModelRegistry.v1'
  providerAvailable: boolean
  provider: string
  defaultMode: 'AUTO'
  models: AiModelContract[]
  warning: string | null
}
