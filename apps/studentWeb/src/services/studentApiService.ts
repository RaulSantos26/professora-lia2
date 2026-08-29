import type {
  StudentContract,
  StudentCreateContract
} from '../contracts/studentContract'
import type {
  AcademicStageContract,
  AcademicStageCreateContract
} from '../contracts/academicStageContract'
import type { ErrorContract } from '../contracts/errorContract'

export class StudentApiService {
  async listStudents(): Promise<StudentContract[]> {
    return await this.request<StudentContract[]>('/api/students')
  }

  async createStudent(
    payload: StudentCreateContract
  ): Promise<StudentContract> {
    return await this.request<StudentContract>(
      '/api/students',
      {
        method: 'POST',
        body: JSON.stringify(payload)
      }
    )
  }

  async listAcademicStages(
    studentId: string
  ): Promise<AcademicStageContract[]> {
    return await this.request<AcademicStageContract[]>(
      `/api/students/${studentId}/academic-stages`
    )
  }

  async createAcademicStage(
    studentId: string,
    payload: AcademicStageCreateContract
  ): Promise<AcademicStageContract> {
    return await this.request<AcademicStageContract>(
      `/api/students/${studentId}/academic-stages`,
      {
        method: 'POST',
        body: JSON.stringify(payload)
      }
    )
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
      return await response.json() as T
    }

    let errorPayload: ErrorContract | null = null

    try {
      errorPayload = await response.json() as ErrorContract
    } catch {
      // Fallback preserva erro compreensível sem depender do payload.
    }

    throw new Error(
      errorPayload?.message ?? `Falha HTTP ${response.status}`
    )
  }
}
