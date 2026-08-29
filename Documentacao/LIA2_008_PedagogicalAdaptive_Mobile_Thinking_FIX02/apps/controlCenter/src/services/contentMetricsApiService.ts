import type { ContentMetricsContract } from '../contracts/contentMetricsContract'

export class ContentMetricsApiService {
  async getMetrics(): Promise<ContentMetricsContract> {
    const response = await fetch('/api/platform/content-metrics', {
      headers: { Accept: 'application/json' }
    })

    if (!response.ok) {
      throw new Error(
        `Falha ao consultar métricas de conteúdo: HTTP ${response.status}`
      )
    }

    return await response.json() as ContentMetricsContract
  }
}
