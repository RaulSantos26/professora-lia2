from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence.models.studySessionItemModel import StudySessionItemModel

class StudySessionItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: StudySessionItemModel) -> StudySessionItemModel:
        self.session.add(model)
        self.session.flush()
        return model

    def listBySessionId(self, studySessionId: UUID) -> list[StudySessionItemModel]:
        statement = (
            select(StudySessionItemModel)
            .where(StudySessionItemModel.studySessionId == studySessionId)
            .order_by(StudySessionItemModel.createdAt.asc())
        )
        return list(self.session.scalars(statement))
