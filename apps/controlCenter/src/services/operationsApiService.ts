import type {
  ManagedServiceKey,
  OperationalEventContract,
  OperationAction,
  OperationsStatusContract
} from '../contracts/operationContract'
import { AdminSessionService } from './adminSessionService'

export class OperationsApiService {
  constructor(
    private readonly adminSessionService = new AdminSessionService()
  ) {}

  private headers(): HeadersInit {
    return {
      Accept: 'application/json',
      'X-Lia2-Admin-Token': this.adminSessionService.getToken()
    }
  }

  async getStatus(): Promise<OperationsStatusContract> {
    const response = await fetch('/api/operations/status', {
      headers: this.headers()
    })
    await this.ensureSuccess(response)
    return await response.json() as OperationsStatusContract
  }

  async listEvents(limit = 10): Promise<OperationalEventContract[]> {
    const response = await fetch(`/api/operations/events?limit=${limit}`, {
      headers: this.headers()
    })
    await this.ensureSuccess(response)
    return await response.json() as OperationalEventContract[]
  }

  async executeApplicationAction(
    action: OperationAction
  ): Promise<OperationalEventContract> {
    const response = await fetch(`/api/operations/application/${action}`, {
      method: 'POST',
      headers: this.headers()
    })
    await this.ensureSuccess(response)
    return await response.json() as OperationalEventContract
  }

  async executeServiceAction(
    serviceKey: ManagedServiceKey,
    action: OperationAction
  ): Promise<OperationalEventContract> {
    const response = await fetch(
      `/api/operations/services/${serviceKey}/${action}`,
      {
        method: 'POST',
        headers: this.headers()
      }
    )
    await this.ensureSuccess(response)
    return await response.json() as OperationalEventContract
  }

  private async ensureSuccess(response: Response): Promise<void> {
    if (response.ok) {
      return
    }

    if (response.status === 401) {
      throw new Error('ADMIN_TOKEN_INVALID')
    }

    throw new Error(`Falha operacional: HTTP ${response.status}`)
  }
}
