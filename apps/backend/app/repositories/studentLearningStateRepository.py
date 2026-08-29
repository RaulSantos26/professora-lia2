from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence.models.studentLearningStateModel import StudentLearningStateModel

class StudentLearningStateRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: StudentLearningStateModel) -> StudentLearningStateModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findByUnitId(self, studentLearningUnitId: UUID) -> StudentLearningStateModel | None:
        statement = (
            select(StudentLearningStateModel)
            .where(StudentLearningStateModel.studentLearningUnitId == studentLearningUnitId)
            .limit(1)
        )
        return self.session.scalar(statement)
