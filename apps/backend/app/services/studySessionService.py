from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.contracts.studySessionContract import StudySessionStartContract, StudySessionViewContract
from app.domain.common.domainError import DomainError
from app.mappers.studySessionMapper import StudySessionMapper
from app.persistence.models.studySessionItemModel import StudySessionItemModel
from app.persistence.models.studySessionModel import StudySessionModel
from app.persistence.models.studentLearningStateModel import StudentLearningStateModel
from app.repositories.learningGoalRepository import LearningGoalRepository
from app.repositories.studyScopeItemRepository import StudyScopeItemRepository
from app.repositories.studyScopeRepository import StudyScopeRepository
from app.repositories.studySessionItemRepository import StudySessionItemRepository
from app.repositories.studySessionRepository import StudySessionRepository
from app.repositories.studentLearningStateRepository import StudentLearningStateRepository

class StudySessionService:
    def __init__(self, session: Session):
        self.session = session
        self.learningGoalRepository = LearningGoalRepository(session)
        self.studyScopeRepository = StudyScopeRepository(session)
        self.studyScopeItemRepository = StudyScopeItemRepository(session)
        self.studySessionRepository = StudySessionRepository(session)
        self.studySessionItemRepository = StudySessionItemRepository(session)
        self.studentLearningStateRepository = StudentLearningStateRepository(session)

    def _buildView(self, sessionModel):
        items = self.studySessionItemRepository.listBySessionId(sessionModel.studySessionId)
        return StudySessionViewContract(
            session=StudySessionMapper.toContract(sessionModel),
            items=[StudySessionMapper.itemToContract(item) for item in items],
        )

    def startSession(self, studyScopeId: UUID, request: StudySessionStartContract) -> StudySessionViewContract:
        scope = self.studyScopeRepository.findById(studyScopeId)
        if scope is None or scope.status not in ("ACTIVE", "DRAFT"):
            raise DomainError(code="STUDY_SCOPE_NOT_AVAILABLE", message="Escopo não disponível.", httpStatus=409)

        goal = self.learningGoalRepository.findById(scope.learningGoalId)
        if goal is None or goal.status != "ACTIVE":
            raise DomainError(code="LEARNING_GOAL_NOT_ACTIVE", message="Objetivo não está ativo.", httpStatus=409)

        if self.studySessionRepository.findInProgressByScopeId(studyScopeId) is not None:
            raise DomainError(code="STUDY_SESSION_ALREADY_IN_PROGRESS", message="Já existe uma sessão em andamento.", httpStatus=409)

        scopeItems = self.studyScopeItemRepository.listActiveByScopeId(studyScopeId)
        if not scopeItems:
            raise DomainError(code="STUDY_SCOPE_EMPTY", message="Adicione ao menos uma unidade ao escopo.", httpStatus=409)

        sessionModel = StudySessionModel(
            studyScopeId=studyScopeId,
            studentId=goal.studentId,
            sessionType=request.sessionType,
            status="IN_PROGRESS",
            notes=request.notes,
        )
        self.studySessionRepository.create(sessionModel)

        now = datetime.now(timezone.utc)
        for scopeItem in scopeItems:
            self.studySessionItemRepository.create(
                StudySessionItemModel(
                    studySessionId=sessionModel.studySessionId,
                    studyScopeItemId=scopeItem.studyScopeItemId,
                    status="IN_PROGRESS",
                    startedAt=now,
                    timeSpentSeconds=0,
                )
            )

        self.session.commit()
        self.session.refresh(sessionModel)
        return self._buildView(sessionModel)

    def completeSession(self, studySessionId: UUID) -> StudySessionViewContract:
        sessionModel = self.studySessionRepository.findById(studySessionId)
        if sessionModel is None:
            raise DomainError(code="STUDY_SESSION_NOT_FOUND", message="Sessão não encontrada.", httpStatus=404)
        if sessionModel.status != "IN_PROGRESS":
            raise DomainError(code="STUDY_SESSION_NOT_IN_PROGRESS", message="A sessão não está em andamento.", httpStatus=409)

        now = datetime.now(timezone.utc)
        sessionModel.status = "COMPLETED"
        sessionModel.endedAt = now

        for sessionItem in self.studySessionItemRepository.listBySessionId(studySessionId):
            sessionItem.status = "COMPLETED"
            sessionItem.completedAt = now
            scopeItem = self.studyScopeItemRepository.findById(sessionItem.studyScopeItemId)
            if scopeItem is None:
                continue

            state = self.studentLearningStateRepository.findByUnitId(
                scopeItem.studentLearningUnitId
            )
            if state is None:
                self.studentLearningStateRepository.create(
                    StudentLearningStateModel(
                        studentId=sessionModel.studentId,
                        studentLearningUnitId=scopeItem.studentLearningUnitId,
                        status="LEARNING",
                        masteryLevel=0,
                        confidenceLevel=0,
                        studyCount=1,
                        lastStudiedAt=now,
                    )
                )
            else:
                state.studyCount += 1
                state.lastStudiedAt = now
                if state.status == "NOT_STARTED":
                    state.status = "LEARNING"

        self.session.commit()
        self.session.refresh(sessionModel)
        return self._buildView(sessionModel)

    def listSessions(self, studyScopeId: UUID) -> list[StudySessionViewContract]:
        if self.studyScopeRepository.findById(studyScopeId) is None:
            raise DomainError(code="STUDY_SCOPE_NOT_FOUND", message="Escopo não encontrado.", httpStatus=404)

        return [
            self._buildView(model)
            for model in self.studySessionRepository.listByScopeId(studyScopeId)
        ]
