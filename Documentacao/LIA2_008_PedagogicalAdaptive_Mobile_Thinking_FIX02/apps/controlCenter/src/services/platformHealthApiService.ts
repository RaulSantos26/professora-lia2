import type { PlatformHealthContract } from '../contracts/serviceStatusContract'

export class PlatformHealthApiService {
  async getHealth(): Promise<PlatformHealthContract> {
    const response = await fetch('/api/platform/health', {
      headers: {
        Accept: 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Falha ao consultar saúde da plataforma: HTTP ${response.status}`)
    }

    return await response.json() as PlatformHealthContract
  }
}
