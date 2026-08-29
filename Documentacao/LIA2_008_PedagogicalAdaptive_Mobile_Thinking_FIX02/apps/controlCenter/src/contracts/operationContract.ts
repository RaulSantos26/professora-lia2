export type OperationAction = 'START' | 'STOP' | 'RESTART'
export type OperationStatus = 'SUCCESS' | 'FAILED'
export type ManagedServiceState = 'RUNNING' | 'STOPPED' | 'MISSING' | 'UNKNOWN'
export type ManagedServiceKey = 'backend' | 'studentWeb'

export interface OperationalEventContract {
  contractName: 'OperationalEvent.v1'
  eventId: string
  action: OperationAction
  target: string
  requestedAt: string
  finishedAt: string
  status: OperationStatus
  affectedServices: string[]
  errorType?: string | null
}

export interface ManagedServiceStatusContract {
  contractName: 'ManagedServiceStatus.v1'
  serviceKey: ManagedServiceKey
  containerName: string
  state: ManagedServiceState
}

export interface OperationsStatusContract {
  contractName: 'OperationsStatus.v1'
  services: ManagedServiceStatusContract[]
}
