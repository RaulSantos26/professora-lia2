from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.studentLearningUnitContract import (
    StudentLearningUnitContract,
    StudentLearningUnitCreateContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.studentLearningUnitMapper import StudentLearningUnitMapper
from app.persistence.models.studentLearningUnitModel import (
    StudentLearningUnitModel,
)
from app.repositories.studentLearningUnitRepository import (
    StudentLearningUnitRepository,
)
from app.repositories.studentSubjectRepository import StudentSubjectRepository


class StudentLearningUnitService:
    def __init__(self, session: Session):
        self.session = session
        self.studentSubjectRepository = StudentSubjectRepository(session)
        self.studentLearningUnitRepository = StudentLearningUnitRepository(
            session
        )

    def createLearningUnit(
        self,
        studentSubjectId: UUID,
        request: StudentLearningUnitCreateContract,
    ) -> StudentLearningUnitContract:
        subject = self.studentSubjectRepository.findById(studentSubjectId)

        if subject is None or subject.status != "ACTIVE":
            raise DomainError(
                code="STUDENT_SUBJECT_NOT_FOUND",
                message="Matéria do aluno não encontrada ou inativa.",
                httpStatus=404,
            )

        if self.studentLearningUnitRepository.findBySubjectAndCode(
            studentSubjectId,
            request.code,
        ) is not None:
            raise DomainError(
                code="STUDENT_LEARNING_UNIT_CODE_EXISTS",
                message="Já existe uma unidade com esse código nesta matéria.",
                httpStatus=409,
            )

        if request.parentStudentLearningUnitId is not None:
            parent = self.studentLearningUnitRepository.findById(
                request.parentStudentLearningUnitId
            )
            if parent is None:
                raise DomainError(
                    code="PARENT_STUDENT_LEARNING_UNIT_NOT_FOUND",
                    message="Unidade pai não encontrada.",
                    httpStatus=404,
                )

            if parent.studentSubjectId != studentSubjectId:
                raise DomainError(
                    code="PARENT_STUDENT_LEARNING_UNIT_SUBJECT_MISMATCH",
                    message="A unidade pai pertence a outra matéria.",
                    httpStatus=409,
                )

        model = StudentLearningUnitModel(
            studentSubjectId=studentSubjectId,
            parentStudentLearningUnitId=request.parentStudentLearningUnitId,
            unitType=request.unitType,
            code=request.code,
            title=request.title,
            description=request.description,
            displayOrder=request.displayOrder,
            status=request.status,
        )

        try:
            self.studentLearningUnitRepository.create(model)
            self.session.commit()
            self.session.refresh(model)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="STUDENT_LEARNING_UNIT_CONFLICT",
                message="Não foi possível criar a unidade de aprendizagem.",
                httpStatus=409,
            ) from error

        return StudentLearningUnitMapper.toContract(model)

    def listLearningUnits(
        self,
        studentSubjectId: UUID,
    ) -> list[StudentLearningUnitContract]:
        subject = self.studentSubjectRepository.findById(studentSubjectId)

        if subject is None:
            raise DomainError(
                code="STUDENT_SUBJECT_NOT_FOUND",
                message="Matéria do aluno não encontrada.",
                httpStatus=404,
            )

        return [
            StudentLearningUnitMapper.toContract(model)
            for model in self.studentLearningUnitRepository.listBySubjectId(
                studentSubjectId
            )
        ]
