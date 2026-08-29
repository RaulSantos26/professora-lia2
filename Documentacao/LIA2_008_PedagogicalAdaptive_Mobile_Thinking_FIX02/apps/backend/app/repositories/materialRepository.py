from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.persistence.models.materialFileModel import MaterialFileModel
from app.persistence.models.materialModel import MaterialModel


class MaterialRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: MaterialModel) -> MaterialModel:
        self.session.add(model)
        self.session.flush()
        return model

    def createFile(self, model: MaterialFileModel) -> MaterialFileModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(self, materialId: UUID) -> MaterialModel | None:
        return self.session.get(MaterialModel, materialId)

    def listByStudentId(self, studentId: UUID) -> list[MaterialModel]:
        statement = (
            select(MaterialModel)
            .where(
                MaterialModel.studentId == studentId,
                MaterialModel.status != "ARCHIVED",
            )
            .order_by(MaterialModel.createdAt.desc())
        )
        return list(self.session.scalars(statement))

    def findActiveFile(
        self,
        materialId: UUID,
    ) -> MaterialFileModel | None:
        statement = (
            select(MaterialFileModel)
            .where(
                MaterialFileModel.materialId == materialId,
                MaterialFileModel.status == "ACTIVE",
            )
            .order_by(MaterialFileModel.createdAt.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def listFiles(
        self,
        materialId: UUID,
    ) -> list[MaterialFileModel]:
        statement = (
            select(MaterialFileModel)
            .where(MaterialFileModel.materialId == materialId)
            .order_by(MaterialFileModel.createdAt.asc())
        )
        return list(self.session.scalars(statement))

    def deleteFilesByMaterialId(
        self,
        materialId: UUID,
    ) -> int:
        result = self.session.execute(
            delete(MaterialFileModel).where(
                MaterialFileModel.materialId == materialId
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)

    def deleteMaterialById(
        self,
        materialId: UUID,
    ) -> int:
        result = self.session.execute(
            delete(MaterialModel).where(
                MaterialModel.materialId == materialId
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)
