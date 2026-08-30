from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MaterialContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["Material.v3"] = "Material.v3"
    materialId: UUID
    studentId: UUID
    studentLearningContextId: UUID | None
    studentSubjectId: UUID | None
    studentLearningUnitId: UUID | None
    title: str
    materialType: Literal["PDF","IMAGE","TEXT","DOCUMENT","OTHER"]
    sourceType: Literal["UPLOAD","MANUAL","LINK"]
    description: str | None
    status: Literal["UPLOADED","PROCESSING","PARTIAL","READY","ERROR","ARCHIVED"]
    analysisRequested: bool
    studyEnabled: bool
    sourceFileRetained: bool = True
    requestedModelId: str | None
    aiMode: Literal["AUTO","FIXED","CUSTOM"] = "AUTO"
    fixedModelId: str | None = None
    textModelId: str | None = None
    visionModelId: str | None = None
    embeddingModelId: str | None = None
    thinkingMode: Literal["AUTO","ON","OFF"] = "AUTO"
    sourceGroupId: UUID | None = None
    sourceSequence: int | None = None
    lastProcessingErrorCode: str | None
    lastProcessingErrorMessage: str | None
    createdAt: datetime
    updatedAt: datetime


class MaterialFileContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["MaterialFile.v1"] = "MaterialFile.v1"
    materialFileId: UUID
    materialId: UUID
    originalFileName: str
    mimeType: str
    sizeBytes: int
    sha256: str
    status: Literal["ACTIVE","SUPERSEDED","ERROR"]
    createdAt: datetime


class MaterialUploadResultContract(BaseModel):
    contractName: Literal["MaterialUploadResult.v2"] = "MaterialUploadResult.v2"
    material: MaterialContract
    file: MaterialFileContract
    documentId: UUID | None
    documentVersionId: UUID | None
    pageCount: int
    textBlockCount: int
    visualPendingCount: int
    chunkCount: int
    analysisPerformed: bool


class MaterialBatchItemContract(BaseModel):
    contractName: Literal["MaterialBatchItem.v1"] = "MaterialBatchItem.v1"
    fileName: str
    success: bool
    result: MaterialUploadResultContract | None = None
    errorCode: str | None = None
    errorMessage: str | None = None


class MaterialBatchUploadResultContract(BaseModel):
    contractName: Literal[
        "MaterialBatchUploadResult.v1"
    ] = "MaterialBatchUploadResult.v1"
    totalFiles: int
    successCount: int
    errorCount: int
    items: list[MaterialBatchItemContract]


class MaterialStudyUsageUpdateContract(BaseModel):
    contractName: Literal[
        "MaterialStudyUsageUpdate.v1"
    ] = "MaterialStudyUsageUpdate.v1"
    studyEnabled: bool



class MaterialModelPreferenceUpdateContract(BaseModel):
    contractName: Literal[
        "MaterialModelPreferenceUpdate.v1"
    ] = "MaterialModelPreferenceUpdate.v1"
    requestedModelId: str | None = None
