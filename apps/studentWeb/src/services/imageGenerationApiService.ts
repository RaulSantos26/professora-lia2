import type { ImageGenerationTaskContract } from '../contracts/imageGenerationContract'
import { LiaApiError } from './materialApiService'

export class ImageGenerationApiService {
  async get(studentId: string, imageTaskId: string): Promise<ImageGenerationTaskContract> {
    const response = await fetch(`/api/students/${studentId}/image-tasks/${imageTaskId}`, { headers: { Accept: 'application/json' } })
    if (response.ok) return await response.json() as ImageGenerationTaskContract
    let payload: { message?: string, code?: string, correlationId?: string | null } | null = null
    try { payload = await response.json() } catch { /* fallback */ }
    throw new LiaApiError(payload?.message ?? `Falha HTTP ${response.status}`, payload?.code ?? `HTTP_${response.status}`, payload?.correlationId ?? null)
  }
}
