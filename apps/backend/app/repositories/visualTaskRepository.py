from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.persistence.models.visualTaskModel import VisualTaskModel


class VisualTaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        model: VisualTaskModel,
    ) -> VisualTaskModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(
        self,
        visualTaskId: UUID,
    ) -> VisualTaskModel | None:
        return self.session.get(
            VisualTaskModel,
            visualTaskId,
        )

    def listByStudent(
        self,
        studentId: UUID,
        limit: int = 50,
    ) -> list[VisualTaskModel]:
        statement = (
            select(VisualTaskModel)
            .where(
                VisualTaskModel.studentId == studentId,
                VisualTaskModel.status == "READY",
            )
            .order_by(VisualTaskModel.createdAt.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def deleteByIds(
        self,
        visualTaskIds: list[UUID],
    ) -> int:
        if not visualTaskIds:
            return 0

        result = self.session.execute(
            delete(VisualTaskModel).where(
                VisualTaskModel.visualTaskId.in_(
                    visualTaskIds
                )
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)
