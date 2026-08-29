from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.persistence.models.documentBlockModel import DocumentBlockModel
from app.persistence.models.documentChunkModel import DocumentChunkModel
from app.persistence.models.documentModel import DocumentModel
from app.persistence.models.documentPageModel import DocumentPageModel
from app.persistence.models.documentVersionModel import DocumentVersionModel
from app.persistence.models.evidenceModel import EvidenceModel


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def createDocument(
        self,
        model: DocumentModel,
    ) -> DocumentModel:
        self.session.add(model)
        self.session.flush()
        return model

    def createVersion(
        self,
        model: DocumentVersionModel,
    ) -> DocumentVersionModel:
        self.session.add(model)
        self.session.flush()
        return model

    def createPage(
        self,
        model: DocumentPageModel,
    ) -> DocumentPageModel:
        self.session.add(model)
        self.session.flush()
        return model

    def createBlock(
        self,
        model: DocumentBlockModel,
    ) -> DocumentBlockModel:
        self.session.add(model)
        self.session.flush()
        return model

    def createEvidence(
        self,
        model: EvidenceModel,
    ) -> EvidenceModel:
        self.session.add(model)
        self.session.flush()
        return model

    def createChunk(
        self,
        model: DocumentChunkModel,
    ) -> DocumentChunkModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findByMaterialId(
        self,
        materialId: UUID,
    ) -> DocumentModel | None:
        statement = (
            select(DocumentModel)
            .where(DocumentModel.materialId == materialId)
            .limit(1)
        )
        return self.session.scalar(statement)

    def findLatestVersion(
        self,
        documentId: UUID,
    ) -> DocumentVersionModel | None:
        statement = (
            select(DocumentVersionModel)
            .where(DocumentVersionModel.documentId == documentId)
            .order_by(DocumentVersionModel.versionNumber.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def listPages(
        self,
        documentVersionId: UUID,
    ) -> list[DocumentPageModel]:
        statement = (
            select(DocumentPageModel)
            .where(
                DocumentPageModel.documentVersionId == documentVersionId
            )
            .order_by(DocumentPageModel.pageNumber.asc())
        )
        return list(self.session.scalars(statement))

    def listBlocks(
        self,
        documentPageId: UUID,
    ) -> list[DocumentBlockModel]:
        statement = (
            select(DocumentBlockModel)
            .where(
                DocumentBlockModel.documentPageId == documentPageId
            )
            .order_by(DocumentBlockModel.sequenceNumber.asc())
        )
        return list(self.session.scalars(statement))

    def evidenceCount(
        self,
        documentVersionId: UUID,
    ) -> int:
        statement = select(
            func.count(EvidenceModel.evidenceId)
        ).where(
            EvidenceModel.documentVersionId == documentVersionId
        )
        return int(self.session.scalar(statement) or 0)

    def chunkCount(
        self,
        documentVersionId: UUID,
    ) -> int:
        statement = select(
            func.count(DocumentChunkModel.documentChunkId)
        ).where(
            DocumentChunkModel.documentVersionId == documentVersionId
        )
        return int(self.session.scalar(statement) or 0)

    def listBlocksByProcessingStatus(
        self,
        documentVersionId: UUID,
        processingStatus: str,
    ) -> list[DocumentBlockModel]:
        statement = (
            select(DocumentBlockModel)
            .join(
                DocumentPageModel,
                DocumentPageModel.documentPageId
                == DocumentBlockModel.documentPageId,
            )
            .where(
                DocumentPageModel.documentVersionId
                == documentVersionId,
                DocumentBlockModel.processingStatus
                == processingStatus,
            )
            .order_by(
                DocumentPageModel.pageNumber.asc(),
                DocumentBlockModel.sequenceNumber.asc(),
            )
        )
        return list(self.session.scalars(statement))

    def nextChunkIndex(
        self,
        documentVersionId: UUID,
    ) -> int:
        statement = select(
            func.max(DocumentChunkModel.chunkIndex)
        ).where(
            DocumentChunkModel.documentVersionId
            == documentVersionId
        )
        current = self.session.scalar(statement)
        return int(current if current is not None else -1) + 1

    def listChunks(
        self,
        documentVersionId: UUID,
    ) -> list[DocumentChunkModel]:
        statement = (
            select(DocumentChunkModel)
            .where(
                DocumentChunkModel.documentVersionId
                == documentVersionId
            )
            .order_by(
                DocumentChunkModel.chunkIndex.asc()
            )
        )
        return list(self.session.scalars(statement))

    def embeddedChunkCount(
        self,
        documentVersionId: UUID,
    ) -> int:
        statement = select(
            func.count(DocumentChunkModel.documentChunkId)
        ).where(
            DocumentChunkModel.documentVersionId
            == documentVersionId,
            DocumentChunkModel.status == "EMBEDDED",
        )
        return int(self.session.scalar(statement) or 0)

    def visualPendingCount(
        self,
        documentVersionId: UUID,
    ) -> int:
        statement = (
            select(func.count(DocumentBlockModel.documentBlockId))
            .join(
                DocumentPageModel,
                DocumentPageModel.documentPageId
                == DocumentBlockModel.documentPageId,
            )
            .where(
                DocumentPageModel.documentVersionId
                == documentVersionId,
                DocumentBlockModel.processingStatus
                == "PENDING_VISION",
            )
        )
        return int(self.session.scalar(statement) or 0)

    def nextSequenceNumber(
        self,
        documentPageId: UUID,
    ) -> int:
        statement = select(
            func.max(DocumentBlockModel.sequenceNumber)
        ).where(
            DocumentBlockModel.documentPageId
            == documentPageId
        )
        current = self.session.scalar(statement)
        return int(current or 0) + 1

    def findEvidenceByBlock(
        self,
        documentBlockId: UUID,
        evidenceType: str | None = None,
    ) -> EvidenceModel | None:
        statement = select(EvidenceModel).where(
            EvidenceModel.documentBlockId == documentBlockId
        )

        if evidenceType:
            statement = statement.where(
                EvidenceModel.evidenceType == evidenceType
            )

        return self.session.scalar(
            statement.order_by(
                EvidenceModel.createdAt.asc()
            ).limit(1)
        )

    def deleteByMaterialId(
        self,
        materialId: UUID,
    ) -> dict[str, int]:
        """
        Delete the derived document graph in explicit FK order.

        Important:
        Do not mix ORM session.delete(parent) with children that have only
        database FKs and no ORM relationship graph. PostgreSQL RESTRICT is
        intentionally strict and the Unit of Work cannot safely infer the
        ordering without relationship metadata.

        Order:
        chunk -> evidence -> block -> page -> version -> document
        """
        documentId = self.session.scalar(
            select(DocumentModel.documentId)
            .where(DocumentModel.materialId == materialId)
            .limit(1)
        )

        if documentId is None:
            return {
                "chunks": 0,
                "evidence": 0,
                "blocks": 0,
                "pages": 0,
                "versions": 0,
                "documents": 0,
            }

        versionIds = list(
            self.session.scalars(
                select(DocumentVersionModel.documentVersionId)
                .where(
                    DocumentVersionModel.documentId == documentId
                )
            )
        )

        pageIds: list[UUID] = []

        if versionIds:
            pageIds = list(
                self.session.scalars(
                    select(DocumentPageModel.documentPageId)
                    .where(
                        DocumentPageModel.documentVersionId.in_(
                            versionIds
                        )
                    )
                )
            )

        deleted = {
            "chunks": 0,
            "evidence": 0,
            "blocks": 0,
            "pages": 0,
            "versions": 0,
            "documents": 0,
        }

        if versionIds:
            result = self.session.execute(
                delete(DocumentChunkModel).where(
                    DocumentChunkModel.documentVersionId.in_(
                        versionIds
                    )
                )
            )
            deleted["chunks"] = int(result.rowcount or 0)

            result = self.session.execute(
                delete(EvidenceModel).where(
                    EvidenceModel.documentVersionId.in_(
                        versionIds
                    )
                )
            )
            deleted["evidence"] = int(result.rowcount or 0)

        if pageIds:
            result = self.session.execute(
                delete(DocumentBlockModel).where(
                    DocumentBlockModel.documentPageId.in_(
                        pageIds
                    )
                )
            )
            deleted["blocks"] = int(result.rowcount or 0)

            result = self.session.execute(
                delete(DocumentPageModel).where(
                    DocumentPageModel.documentPageId.in_(
                        pageIds
                    )
                )
            )
            deleted["pages"] = int(result.rowcount or 0)

        if versionIds:
            # Explicit SQL DELETE, not ORM session.delete().
            result = self.session.execute(
                delete(DocumentVersionModel).where(
                    DocumentVersionModel.documentVersionId.in_(
                        versionIds
                    )
                )
            )
            deleted["versions"] = int(result.rowcount or 0)

        # At this point there is no fk_document_version_document reference.
        result = self.session.execute(
            delete(DocumentModel).where(
                DocumentModel.documentId == documentId
            )
        )
        deleted["documents"] = int(result.rowcount or 0)

        # Force FK verification here, before MaterialFile/Material deletion.
        self.session.flush()

        return deleted
