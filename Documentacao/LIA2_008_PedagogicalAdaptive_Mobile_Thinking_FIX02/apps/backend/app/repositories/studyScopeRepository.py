from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence.models.studyScopeModel import StudyScopeModel

class StudyScopeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: StudyScopeModel) -> StudyScopeModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(self, studyScopeId: UUID) -> StudyScopeModel | None:
        return self.session.get(StudyScopeModel, studyScopeId)

    def listByGoalId(self, learningGoalId: UUID) -> list[StudyScopeModel]:
        statement = (
            select(StudyScopeModel)
            .where(
                StudyScopeModel.learningGoalId == learningGoalId,
                StudyScopeModel.status != "ARCHIVED",
            )
            .order_by(StudyScopeModel.createdAt.desc())
        )
        return list(self.session.scalars(statement))
