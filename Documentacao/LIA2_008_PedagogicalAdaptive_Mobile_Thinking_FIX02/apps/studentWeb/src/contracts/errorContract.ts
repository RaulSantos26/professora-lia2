export interface ErrorContract {
  contractName: 'Error.v1'
  code: string
  message: string
  correlationId?: string | null
}
