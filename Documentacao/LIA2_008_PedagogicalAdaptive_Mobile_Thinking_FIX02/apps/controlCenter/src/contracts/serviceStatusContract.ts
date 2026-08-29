export type ServiceHealthStatus = 'ONLINE' | 'OFFLINE' | 'DEGRADED'

export interface ServiceStatusContract {
  contractName: 'ServiceStatus.v1'
  serviceName: string
  status: ServiceHealthStatus
  checkedAt: string
  version?: string | null
  details?: Record<string, unknown>
}

export interface PlatformHealthContract {
  contractName: 'PlatformHealth.v1'
  environment: string
  release: string
  overallStatus: ServiceHealthStatus
  checkedAt: string
  services: ServiceStatusContract[]
}
