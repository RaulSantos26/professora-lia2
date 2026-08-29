from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.contracts.studyScopeContract import StudyScopeContract, StudyScopeCreateContract
from app.contracts.studyScopeItemContract import StudyScopeCandidateContract, StudyScopeItemContract, StudyScopeItemCreateContract
from app.domain.common.domainError import DomainError
from app.mappers.studyScopeItemMapper import StudyScopeItemMapper
from app.mappers.studyScopeMapper import StudyScopeMapper
from app.persistence.models.learningContextModel import LearningContextModel
from app.persistence.models.studyScopeItemModel import StudyScopeItemModel
from app.persistence.models.studyScopeModel import StudyScopeModel
from app.persistence.models.studentLearningContextModel import StudentLearningContextModel
from app.persistence.models.studentLearningUnitModel import StudentLearningUnitModel
from app.persistence.models.studentSubjectModel import StudentSubjectModel
from app.repositories.learningGoalRepository import LearningGoalRepository
from app.repositories.studyScopeItemRepository import StudyScopeItemRepository
from app.repositories.studyScopeRepository import StudyScopeRepository
from app.services.studentContentOwnershipService import StudentContentOwnershipService

class StudyScopeService:
    def __init__(self, session: Session):
        self.session = session
        self.learningGoalRepository = LearningGoalRepository(session)
        self.studyScopeRepository = StudyScopeRepository(session)
        self.studyScopeItemRepository = StudyScopeItemRepository(session)
        self.ownershipService = StudentContentOwnershipService(session)

    def _requireGoal(self, learningGoalId: UUID):
        goal = self.learningGoalRepository.findById(learningGoalId)
        if goal is None:
            raise DomainError(code="LEARNING_GOAL_NOT_FOUND", message="Objetivo não encontrado.", httpStatus=404)
        return goal

    def _requireScope(self, studyScopeId: UUID):
        scope = self.studyScopeRepository.findById(studyScopeId)
        if scope is None:
            raise DomainError(code="STUDY_SCOPE_NOT_FOUND", message="Escopo de estudo não encontrado.", httpStatus=404)
        return scope

    def createScope(self, learningGoalId: UUID, request: StudyScopeCreateContract) -> StudyScopeContract:
        goal = self._requireGoal(learningGoalId)
        if goal.status != "ACTIVE":
            raise DomainError(code="LEARNING_GOAL_NOT_ACTIVE", message="O objetivo não está ativo.", httpStatus=409)

        model = StudyScopeModel(
            learningGoalId=learningGoalId,
            name=request.name,
            description=request.description,
            status="ACTIVE",
        )
        self.studyScopeRepository.create(model)
        self.session.commit()
        self.session.refresh(model)
        return StudyScopeMapper.toContract(model)

    def listScopes(self, learningGoalId: UUID) -> list[StudyScopeContract]:
        self._requireGoal(learningGoalId)
        return [
            StudyScopeMapper.toContract(model)
            for model in self.studyScopeRepository.listByGoalId(learningGoalId)
        ]

    def addItem(self, studyScopeId: UUID, request: StudyScopeItemCreateContract) -> StudyScopeItemContract:
        scope = self._requireScope(studyScopeId)
        goal = self._requireGoal(scope.learningGoalId)
        _, _, context = self.ownershipService.assertUnitBelongsToStudent(
            request.studentLearningUnitId,
            goal.studentId,
        )

        if (
            goal.studentLearningContextId is not None
            and context.studentLearningContextId != goal.studentLearningContextId
        ):
            raise DomainError(
                code="STUDY_SCOPE_CONTEXT_MISMATCH",
                message="A unidade pertence a outro contexto do aluno.",
                httpStatus=409,
            )

        existing = self.studyScopeItemRepository.findByScopeAndUnit(
            studyScopeId,
            request.studentLearningUnitId,
        )
        if existing is not None:
            if existing.status == "ACTIVE":
                raise DomainError(code="STUDY_SCOPE_ITEM_EXISTS", message="A unidade já está no escopo.", httpStatus=409)
            existing.status = "ACTIVE"
            existing.displayOrder = request.displayOrder
            existing.isRequired = request.isRequired
            self.session.commit()
            self.session.refresh(existing)
            return StudyScopeItemMapper.toContract(existing)

        model = StudyScopeItemModel(
            studyScopeId=studyScopeId,
            studentLearningUnitId=request.studentLearningUnitId,
            displayOrder=request.displayOrder,
            isRequired=request.isRequired,
            status="ACTIVE",
        )
        self.studyScopeItemRepository.create(model)
        self.session.commit()
        self.session.refresh(model)
        return StudyScopeItemMapper.toContract(model)

    def removeItem(self, studyScopeId: UUID, studyScopeItemId: UUID) -> None:
        scope = self._requireScope(studyScopeId)
        item = self.studyScopeItemRepository.findById(studyScopeItemId)
        if item is None or item.studyScopeId != scope.studyScopeId:
            raise DomainError(code="STUDY_SCOPE_ITEM_NOT_FOUND", message="Item do escopo não encontrado.", httpStatus=404)
        item.status = "REMOVED"
        self.session.commit()

    def listItems(self, studyScopeId: UUID) -> list[StudyScopeItemContract]:
        self._requireScope(studyScopeId)
        return [
            StudyScopeItemMapper.toContract(model)
            for model in self.studyScopeItemRepository.listActiveByScopeId(studyScopeId)
        ]

    def listCandidates(
        self,
        learningGoalId: UUID,
        studyScopeId: UUID | None,
    ) -> list[StudyScopeCandidateContract]:
        goal = self._requireGoal(learningGoalId)

        selected = {}
        if studyScopeId is not None:
            scope = self._requireScope(studyScopeId)
            if scope.learningGoalId != learningGoalId:
                raise DomainError(code="STUDY_SCOPE_GOAL_MISMATCH", message="O escopo não pertence ao objetivo.", httpStatus=409)
            selected = {
                item.studentLearningUnitId: item.studyScopeItemId
                for item in self.studyScopeItemRepository.listActiveByScopeId(studyScopeId)
            }

        statement = (
            select(
                StudentLearningContextModel.studentLearningContextId,
                LearningContextModel.name.label("contextName"),
                StudentSubjectModel.studentSubjectId,
                StudentSubjectModel.name.label("subjectName"),
                StudentLearningUnitModel.studentLearningUnitId,
                StudentLearningUnitModel.code.label("unitCode"),
                StudentLearningUnitModel.title.label("unitTitle"),
                StudentLearningUnitModel.unitType.label("unitType"),
            )
            .join(LearningContextModel, LearningContextModel.learningContextId == StudentLearningContextModel.learningContextId)
            .join(StudentSubjectModel, StudentSubjectModel.studentLearningContextId == StudentLearningContextModel.studentLearningContextId)
            .join(StudentLearningUnitModel, StudentLearningUnitModel.studentSubjectId == StudentSubjectModel.studentSubjectId)
            .where(
                StudentLearningContextModel.studentId == goal.studentId,
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

        if goal.studentLearningContextId is not None:
            statement = statement.where(
                StudentLearningContextModel.studentLearningContextId == goal.studentLearningContextId
            )

        rows = self.session.execute(statement).mappings().all()
        return [
            StudyScopeCandidateContract(
                studentLearningContextId=row["studentLearningContextId"],
                contextName=row["contextName"],
                studentSubjectId=row["studentSubjectId"],
                subjectName=row["subjectName"],
                studentLearningUnitId=row["studentLearningUnitId"],
                unitCode=row["unitCode"],
                unitTitle=row["unitTitle"],
                unitType=row["unitType"],
                isSelected=row["studentLearningUnitId"] in selected,
                studyScopeItemId=selected.get(row["studentLearningUnitId"]),
            )
            for row in rows
        ]
