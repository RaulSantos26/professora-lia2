import type { DocumentStructureContract } from '../contracts/documentStructureContract'
import type { AiExecutionMode, ThinkingMode } from '../contracts/aiExecutionPreferenceContract'
import type { ErrorContract } from '../contracts/errorContract'
import type {
  MaterialContract
} from '../contracts/materialContract'
import type {
  MaterialAsyncBatchUploadResultContract,
  MaterialProcessingJobContract
} from '../contracts/materialProcessingContract'

export interface MaterialBatchUploadRequest {
  title: string | null
  description: string | null
  studentLearningContextId: string | null
  studentSubjectId: string | null
  studentLearningUnitId: string | null
  analysisRequested: boolean
  studyEnabled: boolean
  requestedModelId: string | null
  aiMode: AiExecutionMode
  fixedModelId: string | null
  textModelId: string | null
  visionModelId: string | null
  embeddingModelId: string | null
  thinkingMode: ThinkingMode
  files: File[]
}

export class LiaApiError extends Error {
  readonly code: string
  readonly correlationId: string | null

  constructor(
    message: string,
    code: string,
    correlationId: string | null
  ) {
    super(message)
    this.name = 'LiaApiError'
    this.code = code
    this.correlationId = correlationId
  }
}

export class MaterialApiService {
  async listMaterials(
    studentId: string
  ): Promise<MaterialContract[]> {
    return await this.request<MaterialContract[]>(
      `/api/students/${studentId}/materials`
    )
  }

  async uploadBatchAsync(
    studentId: string,
    request: MaterialBatchUploadRequest,
    onProgress: (percent: number) => void
  ): Promise<MaterialAsyncBatchUploadResultContract> {
    const body = this.toFormData(request)

    return await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      xhr.open(
        'POST',
        `/api/students/${studentId}/materials/upload-batch-async`
      )

      xhr.setRequestHeader('Accept', 'application/json')

      xhr.upload.onprogress = event => {
        if (!event.lengthComputable || event.total <= 0) {
          return
        }

        onProgress(
          Math.max(
            0,
            Math.min(
              100,
              Math.round((event.loaded / event.total) * 100)
            )
          )
        )
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            onProgress(100)
            resolve(
              JSON.parse(xhr.responseText) as MaterialAsyncBatchUploadResultContract
            )
          } catch {
            reject(
              new LiaApiError(
                'A resposta do upload não pôde ser interpretada.',
                'UPLOAD_RESPONSE_INVALID',
                null
              )
            )
          }
          return
        }

        reject(this.toXhrError(xhr))
      }

      xhr.onerror = () => {
        reject(
          new LiaApiError(
            'Falha de rede durante o envio do material.',
            'UPLOAD_NETWORK_ERROR',
            null
          )
        )
      }

      xhr.send(body)
    })
  }

  async analyzeAsync(
    studentId: string,
    materialId: string
  ): Promise<MaterialProcessingJobContract> {
    return await this.request<MaterialProcessingJobContract>(
      `/api/students/${studentId}/materials/${materialId}/analyze-async`,
      { method: 'POST' }
    )
  }

  async indexRag(
    studentId: string,
    materialId: string
  ): Promise<MaterialProcessingJobContract> {
    return await this.request<MaterialProcessingJobContract>(
      `/api/students/${studentId}/materials/${materialId}/index-rag`,
      { method: 'POST' }
    )
  }

  async listProcessingJobs(
    studentId: string,
    activeOnly = false
  ): Promise<MaterialProcessingJobContract[]> {
    return await this.request<MaterialProcessingJobContract[]>(
      `/api/students/${studentId}/material-processing-jobs`
      + `?activeOnly=${activeOnly ? 'true' : 'false'}`
    )
  }

  async setAiPreference(
    studentId: string,
    materialId: string,
    preference: {
      mode: AiExecutionMode
      fixedModelId: string | null
      textModelId: string | null
      visionModelId: string | null
      embeddingModelId: string | null
      thinkingMode: ThinkingMode
    }
  ): Promise<MaterialContract> {
    return await this.request<MaterialContract>(
      `/api/students/${studentId}/materials/${materialId}/ai-preference`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          contractName: 'MaterialAiPreferenceUpdate.v1',
          ...preference
        })
      }
    )
  }

  async setModelPreference(
    studentId: string,
    materialId: string,
    requestedModelId: string | null
  ): Promise<MaterialContract> {
    return await this.request<MaterialContract>(
      `/api/students/${studentId}/materials/${materialId}/model-preference`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          contractName: 'MaterialModelPreferenceUpdate.v1',
          requestedModelId
        })
      }
    )
  }

  async setStudyEnabled(
    studentId: string,
    materialId: string,
    studyEnabled: boolean
  ): Promise<MaterialContract> {
    return await this.request<MaterialContract>(
      `/api/students/${studentId}/materials/${materialId}/study-usage`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          contractName: 'MaterialStudyUsageUpdate.v1',
          studyEnabled
        })
      }
    )
  }

  async deleteMaterial(
    studentId: string,
    materialId: string
  ): Promise<void> {
    const response = await fetch(
      `/api/students/${studentId}/materials/${materialId}`,
      {
        method: 'DELETE'
      }
    )

    if (!response.ok) {
      throw await this.toError(response)
    }
  }

  async getStructure(
    materialId: string
  ): Promise<DocumentStructureContract> {
    return await this.request<DocumentStructureContract>(
      `/api/materials/${materialId}/structure`
    )
  }

  fileUrl(materialId: string): string {
    return `/api/materials/${materialId}/file`
  }

  private toFormData(
    request: MaterialBatchUploadRequest
  ): FormData {
    const body = new FormData()

    if (request.title) {
      body.append('title', request.title)
    }

    if (request.description) {
      body.append('description', request.description)
    }

    if (request.studentLearningContextId) {
      body.append(
        'studentLearningContextId',
        request.studentLearningContextId
      )
    }

    if (request.studentSubjectId) {
      body.append(
        'studentSubjectId',
        request.studentSubjectId
      )
    }

    if (request.studentLearningUnitId) {
      body.append(
        'studentLearningUnitId',
        request.studentLearningUnitId
      )
    }

    body.append(
      'analysisRequested',
      request.analysisRequested ? 'true' : 'false'
    )
    body.append(
      'studyEnabled',
      request.studyEnabled ? 'true' : 'false'
    )

    if (request.requestedModelId) {
      body.append('requestedModelId', request.requestedModelId)
    }

    body.append('aiMode', request.aiMode)

    if (request.fixedModelId) {
      body.append('fixedModelId', request.fixedModelId)
    }

    if (request.textModelId) {
      body.append('textModelId', request.textModelId)
    }

    if (request.visionModelId) {
      body.append('visionModelId', request.visionModelId)
    }

    if (request.embeddingModelId) {
      body.append('embeddingModelId', request.embeddingModelId)
    }

    body.append('thinkingMode', request.thinkingMode)

    for (const file of request.files) {
      body.append('files', file)
    }

    return body
  }

  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(options.headers ?? {})
      }
    })

    if (response.ok) {
      if (response.status === 204) {
        return undefined as T
      }

      return await response.json() as T
    }

    throw await this.toError(response)
  }

  private async toError(
    response: Response
  ): Promise<LiaApiError> {
    let errorPayload: ErrorContract | null = null

    try {
      errorPayload = await response.json() as ErrorContract
    } catch {
      // fallback
    }

    return new LiaApiError(
      errorPayload?.message ?? `Falha HTTP ${response.status}`,
      errorPayload?.code ?? `HTTP_${response.status}`,
      errorPayload?.correlationId ?? null
    )
  }

  private toXhrError(xhr: XMLHttpRequest): LiaApiError {
    try {
      const payload = JSON.parse(xhr.responseText) as ErrorContract

      return new LiaApiError(
        payload.message ?? `Falha HTTP ${xhr.status}`,
        payload.code ?? `HTTP_${xhr.status}`,
        payload.correlationId ?? null
      )
    } catch {
      return new LiaApiError(
        `Falha HTTP ${xhr.status}`,
        `HTTP_${xhr.status}`,
        null
      )
    }
  }
}
