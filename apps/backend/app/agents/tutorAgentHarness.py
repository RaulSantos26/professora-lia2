from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.agentToolExecutor import AgentToolExecutor
from app.agents.tutorAgentGuardrails import TutorAgentGuardrails
from app.agents.tutorPlannerService import TutorPlannerService
from app.agents.tutorResponseService import TutorResponseService
from app.agents.tutorSkillRegistry import TutorSkillRegistry
from app.domain.common.domainError import DomainError
from app.persistence.models.agentMessageModel import AgentMessageModel
from app.persistence.models.agentRunModel import AgentRunModel
from app.persistence.models.agentThreadModel import AgentThreadModel
from app.repositories.agentTutorRepository import AgentTutorRepository
from app.services.capabilityRouterService import CapabilityRouterService
from app.services.thinkingPolicyService import ThinkingPolicyService
from app.tools.evidenceSearchTool import EvidenceSearchTool
from app.tools.pedagogicalCreateTool import PedagogicalCreateTool
from app.tools.progressReadTool import ProgressReadTool
from app.tools.visualCreateTool import VisualCreateTool


class TutorAgentHarness:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AgentTutorRepository(session)
        self.router = CapabilityRouterService()
        self.thinking = ThinkingPolicyService()
        self.planner = TutorPlannerService()
        self.response = TutorResponseService()
        self.guardrails = TutorAgentGuardrails()
        self.skills = TutorSkillRegistry()
        self.toolExecutor = AgentToolExecutor(session)
        self.evidenceTool = EvidenceSearchTool(session)
        self.progressTool = ProgressReadTool(session)
        self.pedagogicalTool = PedagogicalCreateTool(
            session
        )
        self.visualTool = VisualCreateTool(session)

    def process(
        self,
        *,
        run: AgentRunModel,
        thread: AgentThreadModel,
        userMessage: AgentMessageModel,
        materialIds: list[UUID],
    ) -> AgentMessageModel:
        decision = self.router.route(
            "TEXT",
            run.requestedTextModelId,
            allowFallback=(
                run.requestedTextModelId is None
            ),
            additionalCapabilities=(
                self.thinking.additionalCapabilities(
                    run.thinkingMode
                )
            ),
        )
        thinkingEnabled = self.thinking.resolve(
            modelId=decision.effectiveModelId,
            thinkingMode=run.thinkingMode,
        )

        run.effectiveTextModelId = (
            decision.effectiveModelId
        )
        run.effectiveThinkingEnabled = (
            thinkingEnabled
        )
        run.stage = "PLANNING"
        run.progressPercent = 20
        run.message = "A Lia está planejando a melhor forma de ajudar."
        self.session.commit()

        plan = self.planner.plan(
            modelId=decision.effectiveModelId,
            thinkingEnabled=thinkingEnabled,
            message=userMessage.content,
            contextSummary=self._memoryText(thread),
        )
        self.guardrails.validatePlan(plan)

        run.planJson = {
            **plan,
            "skill": self.skills.resolve(
                str(plan.get("intent"))
            ),
        }
        run.stage = "TOOLS"
        run.progressPercent = 35
        run.message = "A Lia está consultando os recursos necessários."
        self.session.commit()

        evidence = None
        progress = None
        actions = []
        visualTaskIds = []

        tools = list(plan.get("tools") or [])

        if "EVIDENCE_SEARCH" in tools:
            evidence = self.toolExecutor.execute(
                runId=run.agentRunId,
                toolName="EVIDENCE_SEARCH",
                request={
                    "query": userMessage.content,
                    "materialIds": materialIds,
                    "studentLearningContextId": (
                        thread.studentLearningContextId
                    ),
                    "studentSubjectId": (
                        thread.studentSubjectId
                    ),
                    "studentLearningUnitId": (
                        thread.studentLearningUnitId
                    ),
                },
                callback=lambda: self.evidenceTool.execute(
                    studentId=thread.studentId,
                    query=userMessage.content,
                    studentLearningContextId=(
                        thread.studentLearningContextId
                    ),
                    studentSubjectId=(
                        thread.studentSubjectId
                    ),
                    studentLearningUnitId=(
                        thread.studentLearningUnitId
                    ),
                    materialIds=materialIds,
                ),
            )

        actionMaterialIds = list(materialIds)

        if (
            not actionMaterialIds
            and evidence
        ):
            actionMaterialIds = list(
                dict.fromkeys(
                    UUID(hit["materialId"])
                    for hit in evidence.get("hits", [])
                    if hit.get("materialId")
                )
            )

        if "PROGRESS_READ" in tools:
            progress = self.toolExecutor.execute(
                runId=run.agentRunId,
                toolName="PROGRESS_READ",
                request={
                    "studentSubjectId": (
                        thread.studentSubjectId
                    ),
                    "studentLearningUnitId": (
                        thread.studentLearningUnitId
                    ),
                },
                callback=lambda: self.progressTool.execute(
                    studentId=thread.studentId,
                    studentSubjectId=(
                        thread.studentSubjectId
                    ),
                    studentLearningUnitId=(
                        thread.studentLearningUnitId
                    ),
                ),
            )

        if "PEDAGOGICAL_CREATE" in tools:
            artifactType = (
                plan.get("pedagogicalType")
                or plan.get("intent")
            )

            action = self.toolExecutor.execute(
                runId=run.agentRunId,
                toolName="PEDAGOGICAL_CREATE",
                request={
                    "artifactType": artifactType,
                    "materialIds": actionMaterialIds,
                    "studentLearningContextId": str(
                        thread.studentLearningContextId
                    ),
                    "studentSubjectId": str(
                        thread.studentSubjectId
                    ),
                    "studentLearningUnitId": str(
                        thread.studentLearningUnitId
                    ),
                },
                callback=lambda: self.pedagogicalTool.execute(
                    studentId=thread.studentId,
                    artifactType=str(artifactType),
                    instruction=userMessage.content,
                    materialIds=actionMaterialIds,
                    studentLearningContextId=(
                        thread.studentLearningContextId
                    ),
                    studentSubjectId=thread.studentSubjectId,
                    studentLearningUnitId=(
                        thread.studentLearningUnitId
                    ),
                    requestedTextModelId=(
                        run.requestedTextModelId
                    ),
                    thinkingMode=run.thinkingMode,
                ),
            )
            actions.append(
                {
                    "type": "PEDAGOGICAL_ARTIFACT",
                    **action,
                }
            )

        if "VISUAL_CREATE" in tools:
            visualType = (
                plan.get("visualType")
                or plan.get("intent")
            )

            action = self.toolExecutor.execute(
                runId=run.agentRunId,
                toolName="VISUAL_CREATE",
                request={
                    "visualType": visualType,
                    "materialIds": actionMaterialIds,
                    "studentLearningContextId": str(
                        thread.studentLearningContextId
                    ),
                    "studentSubjectId": str(
                        thread.studentSubjectId
                    ),
                    "studentLearningUnitId": str(
                        thread.studentLearningUnitId
                    ),
                },
                callback=lambda: self.visualTool.execute(
                    studentId=thread.studentId,
                    visualType=str(visualType),
                    instruction=userMessage.content,
                    materialIds=actionMaterialIds,
                    studentLearningContextId=(
                        thread.studentLearningContextId
                    ),
                    studentSubjectId=thread.studentSubjectId,
                    studentLearningUnitId=(
                        thread.studentLearningUnitId
                    ),
                    requestedTextModelId=(
                        run.requestedTextModelId
                    ),
                    thinkingMode=run.thinkingMode,
                    agentThreadId=thread.agentThreadId,
                    agentRunId=run.agentRunId,
                ),
            )
            actions.append(
                {
                    "type": "VISUAL_TASK",
                    **action,
                }
            )
            visualTaskIds.append(
                action["visualTaskId"]
            )

        run.stage = "ANSWERING"
        run.progressPercent = 75
        run.message = "A Lia está preparando a resposta."
        self.session.commit()

        response = self.response.generate(
            modelId=decision.effectiveModelId,
            thinkingEnabled=thinkingEnabled,
            userMessage=userMessage.content,
            plan=run.planJson,
            evidenceContext=(
                evidence.get("context", "")
                if evidence
                else ""
            ),
            progress=progress,
            actionResults=actions,
            memory=thread.memoryJson or {},
        )

        citations = []

        if evidence:
            refs = {
                int(ref)
                for ref in (
                    response.get("evidenceRefs")
                    or []
                )
                if isinstance(ref, int)
            }

            citations = [
                hit
                for hit in evidence.get("hits", [])
                if int(hit.get("index", 0)) in refs
            ]

            if (
                not citations
                and evidence.get("hits")
            ):
                citations = evidence["hits"][:4]

        assistant = AgentMessageModel(
            agentThreadId=thread.agentThreadId,
            role="ASSISTANT",
            content=str(
                response.get("answer")
                or "Concluí a atividade."
            ),
            citationsJson=citations,
            visualTaskIds=visualTaskIds,
            actionsJson=actions,
        )
        self.repository.createMessage(assistant)

        self._updateMemory(
            thread=thread,
            plan=run.planJson,
            userMessage=userMessage.content,
            materialIds=materialIds,
        )
        self.repository.completeRun(
            run,
            assistantMessageId=assistant.agentMessageId,
        )
        self.session.commit()

        return assistant

    def _memoryText(
        self,
        thread: AgentThreadModel,
    ) -> str:
        memory = thread.memoryJson or {}

        return (
            f"última intenção: "
            f"{memory.get('lastIntent') or 'nenhuma'}; "
            f"tópicos recentes: "
            f"{memory.get('recentTopics') or []}; "
            f"materiais recentes: "
            f"{memory.get('recentMaterialIds') or []}"
        )

    def _updateMemory(
        self,
        *,
        thread: AgentThreadModel,
        plan: dict,
        userMessage: str,
        materialIds: list[UUID],
    ) -> None:
        current = dict(thread.memoryJson or {})
        topics = list(
            current.get("recentTopics") or []
        )
        topic = " ".join(
            userMessage.split()
        )[:160]

        topics.append(topic)
        topics = topics[-5:]

        current.update(
            {
                "lastIntent": plan.get("intent"),
                "lastSkill": plan.get("skill"),
                "recentTopics": topics,
                "recentMaterialIds": [
                    str(value)
                    for value in materialIds[-10:]
                ],
            }
        )
        thread.memoryJson = current
