from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence.models.learningGoalModel import LearningGoalModel

class LearningGoalRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: LearningGoalModel) -> LearningGoalModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(self, learningGoalId: UUID) -> LearningGoalModel | None:
        return self.session.get(LearningGoalModel, learningGoalId)

    def listByStudentId(self, studentId: UUID) -> list[LearningGoalModel]:
        statement = (
            select(LearningGoalModel)
            .where(
                LearningGoalModel.studentId == studentId,
                LearningGoalModel.status != "ARCHIVED",
            )
            .order_by(
                LearningGoalModel.targetDate.asc().nullslast(),
                LearningGoalModel.priority.desc(),
                LearningGoalModel.createdAt.desc(),
            )
        )
        return list(self.session.scalars(statement))
