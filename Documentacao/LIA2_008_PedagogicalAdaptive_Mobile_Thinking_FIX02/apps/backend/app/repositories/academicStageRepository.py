from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.academicStageModel import AcademicStageModel


class AcademicStageRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, academicStage: AcademicStageModel) -> AcademicStageModel:
        self.session.add(academicStage)
        self.session.flush()
        return academicStage

    def findCurrentByStudentId(
        self,
        studentId: UUID,
    ) -> AcademicStageModel | None:
        statement = (
            select(AcademicStageModel)
            .where(
                AcademicStageModel.studentId == studentId,
                AcademicStageModel.status == "CURRENT",
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listByStudentId(
        self,
        studentId: UUID,
    ) -> list[AcademicStageModel]:
        statement = (
            select(AcademicStageModel)
            .where(AcademicStageModel.studentId == studentId)
            .order_by(
                AcademicStageModel.startedAt.desc().nullslast(),
                AcademicStageModel.createdAt.desc(),
            )
        )
        return list(self.session.scalars(statement))
