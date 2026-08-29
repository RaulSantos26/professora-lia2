from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.subjectModel import SubjectModel


class SubjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, subject: SubjectModel) -> SubjectModel:
        self.session.add(subject)
        self.session.flush()
        return subject

    def findById(self, subjectId: UUID) -> SubjectModel | None:
        return self.session.get(SubjectModel, subjectId)

    def findByCode(self, code: str) -> SubjectModel | None:
        statement = (
            select(SubjectModel)
            .where(SubjectModel.code == code)
            .limit(1)
        )
        return self.session.scalar(statement)

    def listActive(self) -> list[SubjectModel]:
        statement = (
            select(SubjectModel)
            .where(SubjectModel.status == "ACTIVE")
            .order_by(SubjectModel.name.asc())
        )
        return list(self.session.scalars(statement))
