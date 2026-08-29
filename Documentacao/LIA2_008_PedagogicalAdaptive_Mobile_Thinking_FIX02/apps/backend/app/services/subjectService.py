from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.subjectContract import SubjectContract, SubjectCreateContract
from app.domain.common.domainError import DomainError
from app.mappers.subjectMapper import SubjectMapper
from app.repositories.subjectRepository import SubjectRepository


class SubjectService:
    def __init__(self, session: Session):
        self.session = session
        self.subjectRepository = SubjectRepository(session)

    def createSubject(
        self,
        request: SubjectCreateContract,
    ) -> SubjectContract:
        if self.subjectRepository.findByCode(request.code) is not None:
            raise DomainError(
                code="SUBJECT_CODE_EXISTS",
                message="Já existe uma matéria com esse código.",
                httpStatus=409,
            )

        model = SubjectMapper.toModel(request)

        try:
            self.subjectRepository.create(model)
            self.session.commit()
            self.session.refresh(model)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="SUBJECT_CONFLICT",
                message="Não foi possível criar a matéria.",
                httpStatus=409,
            ) from error

        return SubjectMapper.toContract(model)

    def listSubjects(self) -> list[SubjectContract]:
        return [
            SubjectMapper.toContract(model)
            for model in self.subjectRepository.listActive()
        ]
