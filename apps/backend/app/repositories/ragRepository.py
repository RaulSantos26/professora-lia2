from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.persistence.models.documentChunkModel import DocumentChunkModel
from app.persistence.models.documentModel import DocumentModel
from app.persistence.models.documentPageModel import DocumentPageModel
from app.persistence.models.documentVersionModel import DocumentVersionModel
from app.persistence.models.evidenceModel import EvidenceModel
from app.persistence.models.materialModel import MaterialModel


@dataclass
class RagCandidate:
    documentChunkId: UUID
    evidenceId: UUID | None
    materialId: UUID
    materialTitle: str
    sourceGroupId: UUID | None
    sourceSequence: int | None
    locator: str
    content: str
    embedding: list[float]
    embeddingModelId: str
    documentPageId: UUID | None = None
    pageNumber: int | None = None
    chunkIndex: int | None = None


class RagRepository:
    def __init__(self, session: Session):
        self.session = session

    def listCandidates(
        self,
        *,
        studentId: UUID,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
        materialIds: list[UUID],
    ) -> list[RagCandidate]:
        latestVersions = (
            select(
                DocumentVersionModel.documentId,
                func.max(DocumentVersionModel.versionNumber).label("latestVersionNumber"),
            )
            .group_by(DocumentVersionModel.documentId)
            .subquery()
        )
        statement = (
            select(
                DocumentChunkModel.documentChunkId,
                DocumentChunkModel.evidenceId,
                MaterialModel.materialId,
                MaterialModel.title,
                MaterialModel.sourceGroupId,
                MaterialModel.sourceSequence,
                EvidenceModel.locator,
                DocumentChunkModel.content,
                DocumentChunkModel.embedding,
                DocumentChunkModel.embeddingModelId,
                DocumentChunkModel.documentPageId,
                DocumentPageModel.pageNumber,
                DocumentChunkModel.chunkIndex,
            )
            .join(
                DocumentVersionModel,
                DocumentVersionModel.documentVersionId
                == DocumentChunkModel.documentVersionId,
            )
            .join(
                DocumentModel,
                DocumentModel.documentId
                == DocumentVersionModel.documentId,
            )
            .join(
                latestVersions,
                (latestVersions.c.documentId == DocumentVersionModel.documentId)
                & (latestVersions.c.latestVersionNumber == DocumentVersionModel.versionNumber),
            )
            .outerjoin(
                DocumentPageModel,
                (DocumentPageModel.documentPageId == DocumentChunkModel.documentPageId)
                & (DocumentPageModel.documentVersionId == DocumentChunkModel.documentVersionId),
            )
            .join(
                MaterialModel,
                MaterialModel.materialId
                == DocumentModel.materialId,
            )
            .outerjoin(
                EvidenceModel,
                EvidenceModel.evidenceId
                == DocumentChunkModel.evidenceId,
            )
            .where(
                MaterialModel.studentId == studentId,
                MaterialModel.studyEnabled.is_(True),
                MaterialModel.status != "ARCHIVED",
                DocumentChunkModel.status == "EMBEDDED",
                DocumentChunkModel.embedding.is_not(None),
                DocumentChunkModel.embeddingModelId.is_not(None),
                or_(
                    DocumentChunkModel.evidenceId.is_(None),
                    (EvidenceModel.status == "ACTIVE")
                    & (EvidenceModel.studentId == studentId)
                    & (EvidenceModel.materialId == MaterialModel.materialId)
                    & (EvidenceModel.documentVersionId == DocumentVersionModel.documentVersionId),
                ),
            )
        )

        if studentLearningContextId is not None:
            statement = statement.where(
                MaterialModel.studentLearningContextId
                == studentLearningContextId
            )

        if studentSubjectId is not None:
            statement = statement.where(
                MaterialModel.studentSubjectId == studentSubjectId
            )

        if studentLearningUnitId is not None:
            statement = statement.where(
                MaterialModel.studentLearningUnitId
                == studentLearningUnitId
            )

        if materialIds:
            statement = statement.where(
                MaterialModel.materialId.in_(materialIds)
            )

        rows = self.session.execute(statement).all()

        candidates = []

        for row in rows:
            if not isinstance(row.embedding, list):
                continue

            if not row.embeddingModelId:
                continue

            candidates.append(
                RagCandidate(
                    documentChunkId=row.documentChunkId,
                    evidenceId=row.evidenceId,
                    materialId=row.materialId,
                    materialTitle=row.title,
                    sourceGroupId=row.sourceGroupId,
                    sourceSequence=row.sourceSequence,
                    locator=row.locator or "sem localizador",
                    content=row.content,
                    embedding=[
                        float(value)
                        for value in row.embedding
                    ],
                    embeddingModelId=row.embeddingModelId,
                    documentPageId=row.documentPageId,
                    pageNumber=row.pageNumber,
                    chunkIndex=row.chunkIndex,
                )
            )

        return candidates
