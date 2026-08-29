from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.contracts.studentLearningStateContract import (
    StudentLearningStateContract,
    StudentLearningStateUpdateContract,
    StudentLearningStateViewContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.studentLearningStateMapper import StudentLearningStateMapper
from app.persistence.models.learningContextModel import LearningContextModel
from app.persistence.models.studentLearningContextModel import StudentLearningContextModel
from app.persistence.models.studentLearningStateModel import StudentLearningStateModel
from app.persistence.models.studentLearningUnitModel import StudentLearningUnitModel
from app.persistence.models.studentSubjectModel import StudentSubjectModel
from app.repositories.studentLearningStateRepository import StudentLearningStateRepository
from app.repositories.studentRepository import StudentRepository
from app.services.studentContentOwnershipService import StudentContentOwnershipService

class StudentLearningStateService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)
        self.stateRepository = StudentLearningStateRepository(session)
        self.ownershipService = StudentContentOwnershipService(session)

    def updateState(
        self,
        studentId: UUID,
        studentLearningUnitId: UUID,
        request: StudentLearningStateUpdateContract,
    ) -> StudentLearningStateContract:
        self.ownershipService.assertUnitBelongsToStudent(
            studentLearningUnitId,
            studentId,
        )
        state = self.stateRepository.findByUnitId(studentLearningUnitId)

        if state is None:
            state = StudentLearningStateModel(
                studentId=studentId,
                studentLearningUnitId=studentLearningUnitId,
                status=request.status,
                masteryLevel=request.masteryLevel,
                confidenceLevel=request.confidenceLevel,
                studyCount=0,
                nextReviewAt=request.nextReviewAt,
            )
            self.stateRepository.create(state)
        else:
            state.status = request.status
            state.masteryLevel = request.masteryLevel
            state.confidenceLevel = request.confidenceLevel
            state.nextReviewAt = request.nextReviewAt

        self.session.commit()
        self.session.refresh(state)
        return StudentLearningStateMapper.toContract(state)

    def listStates(self, studentId: UUID) -> list[StudentLearningStateViewContract]:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(code="STUDENT_NOT_FOUND", message="Aluno não encontrado.", httpStatus=404)

        statement = (
            select(
                StudentLearningContextModel.studentLearningContextId,
                LearningContextModel.name.label("contextName"),
                StudentSubjectModel.studentSubjectId,
                StudentSubjectModel.name.label("subjectName"),
                StudentLearningUnitModel.studentLearningUnitId,
                StudentLearningUnitModel.code.label("unitCode"),
                StudentLearningUnitModel.title.label("unitTitle"),
            )
            .join(LearningContextModel, LearningContextModel.learningContextId == StudentLearningContextModel.learningContextId)
            .join(StudentSubjectModel, StudentSubjectModel.studentLearningContextId == StudentLearningContextModel.studentLearningContextId)
            .join(StudentLearningUnitModel, StudentLearningUnitModel.studentSubjectId == StudentSubjectModel.studentSubjectId)
            .where(
                StudentLearningContextModel.studentId == studentId,
                StudentLearningContextModel.status == "ACTIVE",
                StudentSubjectModel.status == "ACTIVE",
                StudentLearningUnitModel.status == "ACTIVE",
            )
            .order_by(
                LearningContextModel.name.asc(),
                StudentSubjectModel.name.asc(),
                StudentLearningUnitModel.title.asc(),
            )
        )

        rows = self.session.execute(statement).mappings().all()
        result = []
        for row in rows:
            state = self.stateRepository.findByUnitId(row["studentLearningUnitId"])
            result.append(
                StudentLearningStateViewContract(
                    studentLearningContextId=row["studentLearningContextId"],
                    contextName=row["contextName"],
                    studentSubjectId=row["studentSubjectId"],
                    subjectName=row["subjectName"],
                    studentLearningUnitId=row["studentLearningUnitId"],
                    unitCode=row["unitCode"],
                    unitTitle=row["unitTitle"],
                    state=StudentLearningStateMapper.toContract(state) if state else None,
                )
            )
        return result
