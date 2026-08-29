from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.persistence.models.studySessionModel import StudySessionModel

class StudySessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: StudySessionModel) -> StudySessionModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(self, studySessionId: UUID) -> StudySessionModel | None:
        return self.session.get(StudySessionModel, studySessionId)

    def findInProgressByScopeId(self, studyScopeId: UUID) -> StudySessionModel | None:
        statement = (
            select(StudySessionModel)
            .where(
                StudySessionModel.studyScopeId == studyScopeId,
                StudySessionModel.status == "IN_PROGRESS",
            )
            .order_by(StudySessionModel.startedAt.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def listByScopeId(self, studyScopeId: UUID) -> list[StudySessionModel]:
        statement = (
            select(StudySessionModel)
            .where(StudySessionModel.studyScopeId == studyScopeId)
            .order_by(StudySessionModel.startedAt.desc())
        )
        return list(self.session.scalars(statement))
