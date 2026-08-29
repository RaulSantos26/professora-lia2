from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.documentChunkModel import DocumentChunkModel
from app.persistence.models.documentModel import DocumentModel
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
                )
            )

        return candidates
