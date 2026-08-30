from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.contracts.agentTutorContract import (
    AgentConversationContract,
    AgentMessageContract,
    AgentMessageCreateContract,
    AgentRunContract,
    AgentThreadContract,
    AgentThreadCreateContract,
)
from app.domain.common.domainError import DomainError
from app.persistence.models.agentMessageModel import AgentMessageModel
from app.persistence.models.agentRunModel import AgentRunModel
from app.persistence.models.agentThreadModel import AgentThreadModel
from app.persistence.models.studentLearningContextModel import StudentLearningContextModel
from app.persistence.models.studentLearningUnitModel import StudentLearningUnitModel
from app.persistence.models.studentSubjectModel import StudentSubjectModel
from app.repositories.agentTutorRepository import AgentTutorRepository
from app.repositories.materialRepository import MaterialRepository
from app.repositories.studentRepository import StudentRepository


class AgentTutorService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AgentTutorRepository(session)
        self.studentRepository = StudentRepository(session)
        self.materialRepository = MaterialRepository(session)

    def createThread(
        self,
        *,
        studentId: UUID,
        request: AgentThreadCreateContract,
    ) -> AgentThreadContract:
        self._requireStudent(studentId)
        self._validateRequiredScope(
            studentId=studentId,
            studentLearningContextId=request.studentLearningContextId,
            studentSubjectId=request.studentSubjectId,
            studentLearningUnitId=request.studentLearningUnitId,
        )

        thread = AgentThreadModel(
            studentId=studentId,
            studentLearningContextId=(
                request.studentLearningContextId
            ),
            studentSubjectId=request.studentSubjectId,
            studentLearningUnitId=(
                request.studentLearningUnitId
            ),
            title=(
                request.title.strip()
                if request.title and request.title.strip()
                else "Conversa com a Lia"
            ),
            status="ACTIVE",
            memoryJson={},
        )
        self.repository.createThread(thread)
        self.session.commit()
        self.session.refresh(thread)

        return self._threadContract(thread)

    def listThreads(
        self,
        *,
        studentId: UUID,
        studentLearningContextId: UUID,
        studentSubjectId: UUID,
        studentLearningUnitId: UUID,
    ) -> list[AgentThreadContract]:
        self._requireStudent(studentId)
        self._validateRequiredScope(
            studentId=studentId,
            studentLearningContextId=studentLearningContextId,
            studentSubjectId=studentSubjectId,
            studentLearningUnitId=studentLearningUnitId,
        )
        return [
            self._threadContract(thread)
            for thread in self.repository.listThreadsByScope(
                studentId,
                studentLearningContextId,
                studentSubjectId,
                studentLearningUnitId,
            )
        ]

    def conversation(
        self,
        *,
        studentId: UUID,
        threadId: UUID,
    ) -> AgentConversationContract:
        thread = self._ownedThread(
            studentId,
            threadId,
        )
        messages = self.repository.listMessages(
            threadId
        )
        activeRun = self.repository.activeRun(
            threadId
        )
        lastRun = self.repository.lastRun(
            threadId
        )

        return AgentConversationContract(
            thread=self._threadContract(thread),
            messages=[
                self._messageContract(message)
                for message in messages
            ],
            activeRun=(
                self._runContract(activeRun)
                if activeRun
                else None
            ),
            lastRun=(
                self._runContract(lastRun)
                if lastRun
                else None
            ),
        )

    def send(
        self,
        *,
        studentId: UUID,
        threadId: UUID,
        request: AgentMessageCreateContract,
    ) -> AgentRunContract:
        thread = self._ownedThread(
            studentId,
            threadId,
        )

        active = self.repository.activeRun(threadId)

        if active is not None:
            raise DomainError(
                code="AGENT_RUN_ACTIVE",
                message=(
                    "A Lia ainda está respondendo a mensagem anterior."
                ),
                httpStatus=409,
            )

        materialIds = self._validateMaterials(
            studentId,
            request.materialIds,
            thread,
        )

        userMessage = AgentMessageModel(
            agentThreadId=threadId,
            role="USER",
            content=" ".join(
                request.content.split()
            ),
            citationsJson=[],
            visualTaskIds=[],
            imageTaskIds=[],
            actionsJson=[
                {
                    "type": "MATERIAL_SCOPE",
                    "materialIds": [
                        str(value)
                        for value in materialIds
                    ],
                }
            ],
        )
        self.repository.createMessage(userMessage)

        run = AgentRunModel(
            agentThreadId=threadId,
            userMessageId=userMessage.agentMessageId,
            status="QUEUED",
            stage="QUEUED",
            progressPercent=5,
            message="Na fila para a Lia.",
            requestedTextModelId=(
                request.requestedTextModelId
            ),
            thinkingMode=request.thinkingMode,
        )
        self.repository.createRun(run)

        now = datetime.now(timezone.utc)
        thread.lastMessageAt = now
        thread.updatedAt = now

        self.session.commit()
        self.session.refresh(run)

        return self._runContract(run)

    def getRun(
        self,
        *,
        studentId: UUID,
        threadId: UUID,
        runId: UUID,
    ) -> AgentRunContract:
        self._ownedThread(studentId, threadId)
        run = self.repository.findRun(runId)

        if (
            run is None
            or run.agentThreadId != threadId
        ):
            raise DomainError(
                code="AGENT_RUN_NOT_FOUND",
                message="Execução da Lia não encontrada.",
                httpStatus=404,
            )

        return self._runContract(run)

    def retryRun(
        self,
        *,
        studentId: UUID,
        threadId: UUID,
        runId: UUID,
    ) -> AgentRunContract:
        thread = self._ownedThread(studentId, threadId)
        previousRun = self.repository.findRun(runId)

        if (
            previousRun is None
            or previousRun.agentThreadId != threadId
        ):
            raise DomainError(
                code="AGENT_RUN_NOT_FOUND",
                message="Execução da Lia não encontrada.",
                httpStatus=404,
            )

        if previousRun.status not in ["FAILED", "CANCELLED"]:
            raise DomainError(
                code="AGENT_RUN_NOT_RETRYABLE",
                message=(
                    "Somente uma execução que não foi concluída "
                    "pode ser tentada novamente."
                ),
                httpStatus=409,
            )

        if self.repository.activeRun(threadId) is not None:
            raise DomainError(
                code="AGENT_RUN_ACTIVE",
                message=(
                    "A Lia ainda está respondendo a mensagem anterior."
                ),
                httpStatus=409,
            )

        run = AgentRunModel(
            agentThreadId=threadId,
            userMessageId=previousRun.userMessageId,
            status="QUEUED",
            stage="QUEUED",
            progressPercent=5,
            message="Nova tentativa na fila para a Lia.",
            requestedTextModelId=previousRun.requestedTextModelId,
            thinkingMode=previousRun.thinkingMode,
        )
        self.repository.createRun(run)

        thread.updatedAt = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(run)

        return self._runContract(run)

    def archiveThread(
        self,
        *,
        studentId: UUID,
        threadId: UUID,
    ) -> None:
        thread = self._ownedThread(
            studentId,
            threadId,
        )

        if self.repository.activeRun(threadId):
            raise DomainError(
                code="AGENT_RUN_ACTIVE",
                message=(
                    "Aguarde a resposta da Lia antes de arquivar."
                ),
                httpStatus=409,
            )

        thread.status = "ARCHIVED"
        thread.updatedAt = datetime.now(
            timezone.utc
        )
        self.session.commit()

    def _validateRequiredScope(
        self,
        *,
        studentId: UUID,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
    ) -> None:
        if (
            studentLearningContextId is None
            or studentSubjectId is None
            or studentLearningUnitId is None
        ):
            raise DomainError(
                code="AGENT_SCOPE_REQUIRED",
                message="Escolha uma matéria e uma lição antes de conversar com a Lia.",
                httpStatus=422,
            )
        self._validateContextOwnership(
            studentId=studentId,
            studentLearningContextId=studentLearningContextId,
            studentSubjectId=studentSubjectId,
            studentLearningUnitId=studentLearningUnitId,
        )

    def _validateContextOwnership(
        self,
        *,
        studentId: UUID,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
    ) -> None:
        context = None
        subject = None
        unit = None

        if studentLearningContextId is not None:
            context = self.session.get(
                StudentLearningContextModel,
                studentLearningContextId,
            )

            if (
                context is None
                or context.studentId != studentId
                or context.status != "ACTIVE"
            ):
                raise DomainError(
                    code="AGENT_CONTEXT_NOT_OWNED",
                    message=(
                        "O contexto selecionado não pertence "
                        "ao aluno."
                    ),
                    httpStatus=409,
                )

        if studentSubjectId is not None:
            subject = self.session.get(
                StudentSubjectModel,
                studentSubjectId,
            )

            if subject is None or subject.status != "ACTIVE":
                raise DomainError(
                    code="AGENT_SUBJECT_NOT_OWNED",
                    message=(
                        "A matéria selecionada não está disponível."
                    ),
                    httpStatus=409,
                )

            subjectContext = self.session.get(
                StudentLearningContextModel,
                subject.studentLearningContextId,
            )

            if (
                subjectContext is None
                or subjectContext.studentId != studentId
            ):
                raise DomainError(
                    code="AGENT_SUBJECT_NOT_OWNED",
                    message=(
                        "A matéria selecionada não pertence "
                        "ao aluno."
                    ),
                    httpStatus=409,
                )

            if (
                studentLearningContextId is not None
                and subject.studentLearningContextId
                != studentLearningContextId
            ):
                raise DomainError(
                    code="AGENT_CONTEXT_MISMATCH",
                    message=(
                        "A matéria não pertence ao contexto "
                        "selecionado."
                    ),
                    httpStatus=409,
                )

        if studentLearningUnitId is not None:
            unit = self.session.get(
                StudentLearningUnitModel,
                studentLearningUnitId,
            )

            if unit is None or unit.status != "ACTIVE":
                raise DomainError(
                    code="AGENT_UNIT_NOT_OWNED",
                    message=(
                        "A unidade selecionada não está disponível."
                    ),
                    httpStatus=409,
                )

            unitSubject = self.session.get(
                StudentSubjectModel,
                unit.studentSubjectId,
            )

            if unitSubject is None:
                raise DomainError(
                    code="AGENT_UNIT_NOT_OWNED",
                    message=(
                        "A unidade selecionada não pertence ao aluno."
                    ),
                    httpStatus=409,
                )

            unitContext = self.session.get(
                StudentLearningContextModel,
                unitSubject.studentLearningContextId,
            )

            if (
                unitContext is None
                or unitContext.studentId != studentId
            ):
                raise DomainError(
                    code="AGENT_UNIT_NOT_OWNED",
                    message=(
                        "A unidade selecionada não pertence ao aluno."
                    ),
                    httpStatus=409,
                )

            if (
                studentSubjectId is not None
                and unit.studentSubjectId != studentSubjectId
            ):
                raise DomainError(
                    code="AGENT_SUBJECT_MISMATCH",
                    message=(
                        "A unidade não pertence à matéria "
                        "selecionada."
                    ),
                    httpStatus=409,
                )

    def _validateMaterials(
        self,
        studentId: UUID,
        materialIds: list[UUID],
        thread: AgentThreadModel,
    ) -> list[UUID]:
        if not materialIds:
            return []

        owned = {
            material.materialId
            for material in self.materialRepository.listByStudentId(studentId)
            if (
                material.studyEnabled
                and material.studentLearningContextId == thread.studentLearningContextId
                and material.studentSubjectId == thread.studentSubjectId
                and material.studentLearningUnitId == thread.studentLearningUnitId
            )
        }

        missing = [
            value
            for value in materialIds
            if value not in owned
        ]

        if missing:
            raise DomainError(
                code="AGENT_MATERIAL_NOT_OWNED",
                message=(
                    "Um material selecionado não pertence "
                    "ao aluno ou está fora do estudo."
                ),
                httpStatus=409,
            )

        return materialIds

    def _ownedThread(
        self,
        studentId: UUID,
        threadId: UUID,
    ) -> AgentThreadModel:
        thread = self.repository.findThread(
            threadId
        )

        if (
            thread is None
            or thread.studentId != studentId
            or thread.status != "ACTIVE"
        ):
            raise DomainError(
                code="AGENT_THREAD_NOT_FOUND",
                message="Conversa da Lia não encontrada.",
                httpStatus=404,
            )

        return thread

    def _requireStudent(
        self,
        studentId: UUID,
    ) -> None:
        if self.studentRepository.findById(
            studentId
        ) is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

    def _threadContract(
        self,
        model: AgentThreadModel,
    ) -> AgentThreadContract:
        return AgentThreadContract(
            agentThreadId=model.agentThreadId,
            studentId=model.studentId,
            studentLearningContextId=(
                model.studentLearningContextId
            ),
            studentSubjectId=model.studentSubjectId,
            studentLearningUnitId=(
                model.studentLearningUnitId
            ),
            title=model.title,
            status=model.status,
            memory=model.memoryJson or {},
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
            lastMessageAt=model.lastMessageAt,
        )

    def _messageContract(
        self,
        model: AgentMessageModel,
    ) -> AgentMessageContract:
        return AgentMessageContract(
            agentMessageId=model.agentMessageId,
            agentThreadId=model.agentThreadId,
            role=model.role,
            content=model.content,
            citations=model.citationsJson or [],
            visualTaskIds=[
                UUID(value)
                for value in (
                    model.visualTaskIds or []
                )
            ],
            imageTaskIds=[
                UUID(value)
                for value in (
                    model.imageTaskIds or []
                )
            ],
            actions=model.actionsJson or [],
            createdAt=model.createdAt,
        )

    def _runContract(
        self,
        model: AgentRunModel,
    ) -> AgentRunContract:
        return AgentRunContract(
            agentRunId=model.agentRunId,
            agentThreadId=model.agentThreadId,
            userMessageId=model.userMessageId,
            assistantMessageId=(
                model.assistantMessageId
            ),
            status=model.status,
            stage=model.stage,
            progressPercent=model.progressPercent,
            message=model.message,
            requestedTextModelId=(
                model.requestedTextModelId
            ),
            effectiveTextModelId=(
                model.effectiveTextModelId
            ),
            thinkingMode=model.thinkingMode,
            effectiveThinkingEnabled=(
                model.effectiveThinkingEnabled
            ),
            plan=model.planJson,
            errorCode=model.errorCode,
            errorMessage=model.errorMessage,
            createdAt=model.createdAt,
            startedAt=model.startedAt,
            finishedAt=model.finishedAt,
        )
