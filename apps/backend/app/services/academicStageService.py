from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.academicStageContract import (
    AcademicStageContract,
    AcademicStageCreateContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.academicStageMapper import AcademicStageMapper
from app.repositories.academicStageRepository import AcademicStageRepository
from app.repositories.studentRepository import StudentRepository


class AcademicStageService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)
        self.academicStageRepository = AcademicStageRepository(session)

    def createAcademicStage(
        self,
        studentId: UUID,
        request: AcademicStageCreateContract,
    ) -> AcademicStageContract:
        student = self.studentRepository.findById(studentId)

        if student is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        if request.status == "CURRENT":
            current = self.academicStageRepository.findCurrentByStudentId(studentId)

            if current is not None:
                raise DomainError(
                    code="CURRENT_ACADEMIC_STAGE_EXISTS",
                    message="O aluno já possui uma etapa acadêmica atual.",
                    httpStatus=409,
                )

        academicStage = AcademicStageMapper.toModel(studentId, request)

        try:
            self.academicStageRepository.create(academicStage)
            self.session.commit()
            self.session.refresh(academicStage)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="ACADEMIC_STAGE_CONFLICT",
                message="Não foi possível criar a etapa acadêmica.",
                httpStatus=409,
            ) from error

        return AcademicStageMapper.toContract(academicStage)

    def listAcademicStages(
        self,
        studentId: UUID,
    ) -> list[AcademicStageContract]:
        student = self.studentRepository.findById(studentId)

        if student is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        return [
            AcademicStageMapper.toContract(stage)
            for stage in self.academicStageRepository.listByStudentId(studentId)
        ]
