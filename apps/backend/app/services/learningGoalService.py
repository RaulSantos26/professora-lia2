from uuid import UUID
from sqlalchemy.orm import Session
from app.contracts.learningGoalContract import LearningGoalContract, LearningGoalCreateContract
from app.domain.common.domainError import DomainError
from app.mappers.learningGoalMapper import LearningGoalMapper
from app.persistence.models.learningGoalModel import LearningGoalModel
from app.repositories.learningGoalRepository import LearningGoalRepository
from app.repositories.studentLearningContextRepository import StudentLearningContextRepository
from app.repositories.studentRepository import StudentRepository
from app.repositories.studentSubjectRepository import StudentSubjectRepository

class LearningGoalService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)
        self.studentLearningContextRepository = StudentLearningContextRepository(session)
        self.learningGoalRepository = LearningGoalRepository(session)
        self.studentSubjectRepository = StudentSubjectRepository(session)

    def createGoal(self, studentId: UUID, request: LearningGoalCreateContract) -> LearningGoalContract:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(code="STUDENT_NOT_FOUND", message="Aluno não encontrado.", httpStatus=404)

        if request.studentSubjectId is None:
            raise DomainError(code="LEARNING_GOAL_SUBJECT_REQUIRED", message="Escolha a materia do objetivo de estudo.", httpStatus=422)
        subject = self.studentSubjectRepository.findById(request.studentSubjectId)
        if subject is None or subject.status != "ACTIVE":
            raise DomainError(code="LEARNING_GOAL_SUBJECT_NOT_OWNED", message="A materia selecionada nao esta disponivel.", httpStatus=409)
        context = self.studentLearningContextRepository.findById(subject.studentLearningContextId)
        if context is None or context.studentId != studentId:
            raise DomainError(code="LEARNING_GOAL_SUBJECT_NOT_OWNED", message="A materia selecionada nao pertence ao aluno.", httpStatus=409)
        if request.studentLearningContextId is not None and request.studentLearningContextId != context.studentLearningContextId:
            raise DomainError(code="LEARNING_GOAL_CONTEXT_MISMATCH", message="A materia nao pertence ao contexto escolhido.", httpStatus=409)

        model = LearningGoalModel(
            studentId=studentId,
            studentLearningContextId=context.studentLearningContextId,
            studentSubjectId=subject.studentSubjectId,
            goalType=request.goalType,
            title=request.title,
            description=request.description,
            targetDate=request.targetDate,
            priority=request.priority,
            status="ACTIVE",
        )
        self.learningGoalRepository.create(model)
        self.session.commit()
        self.session.refresh(model)
        return LearningGoalMapper.toContract(model)

    def listGoals(self, studentId: UUID) -> list[LearningGoalContract]:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(code="STUDENT_NOT_FOUND", message="Aluno não encontrado.", httpStatus=404)

        return [
            LearningGoalMapper.toContract(model)
            for model in self.learningGoalRepository.listByStudentId(studentId)
        ]
