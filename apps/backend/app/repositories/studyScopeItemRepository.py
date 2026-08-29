from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence.models.studyScopeItemModel import StudyScopeItemModel

class StudyScopeItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: StudyScopeItemModel) -> StudyScopeItemModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(self, studyScopeItemId: UUID) -> StudyScopeItemModel | None:
        return self.session.get(StudyScopeItemModel, studyScopeItemId)

    def findByScopeAndUnit(
        self,
        studyScopeId: UUID,
        studentLearningUnitId: UUID,
    ) -> StudyScopeItemModel | None:
        statement = (
            select(StudyScopeItemModel)
            .where(
                StudyScopeItemModel.studyScopeId == studyScopeId,
                StudyScopeItemModel.studentLearningUnitId == studentLearningUnitId,
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listActiveByScopeId(self, studyScopeId: UUID) -> list[StudyScopeItemModel]:
        statement = (
            select(StudyScopeItemModel)
            .where(
                StudyScopeItemModel.studyScopeId == studyScopeId,
                StudyScopeItemModel.status == "ACTIVE",
            )
            .order_by(
                StudyScopeItemModel.displayOrder.asc().nullslast(),
                StudyScopeItemModel.createdAt.asc(),
            )
        )
        return list(self.session.scalars(statement))
