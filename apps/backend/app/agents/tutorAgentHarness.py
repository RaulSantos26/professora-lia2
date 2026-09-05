from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.agentToolExecutor import AgentToolExecutor
from app.agents.tutorAgentGuardrails import TutorAgentGuardrails
from app.agents.tutorPlannerService import TutorPlannerService
from app.agents.tutorSkillRegistry import TutorSkillRegistry
from app.agents.specialists.specialistContracts import EvidenceBundle, SpecialistScope
from app.agents.specialists.tutorSpecialistRegistry import TutorSpecialistRegistry
from app.domain.common.domainError import DomainError
from app.persistence.models.agentMessageModel import AgentMessageModel
from app.persistence.models.agentRunModel import AgentRunModel
from app.persistence.models.agentThreadModel import AgentThreadModel
from app.repositories.agentTutorRepository import AgentTutorRepository
from app.services.capabilityRouterService import CapabilityRouterService
from app.services.thinkingPolicyService import ThinkingPolicyService
from app.tools.pedagogicalCreateTool import PedagogicalCreateTool
from app.tools.progressReadTool import ProgressReadTool
from app.tools.visualCreateTool import VisualCreateTool
from app.tools.imageCreateTool import ImageCreateTool


class TutorAgentHarness:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AgentTutorRepository(session)
        self.router = CapabilityRouterService()
        self.thinking = ThinkingPolicyService()
        self.planner = TutorPlannerService()
        self.guardrails = TutorAgentGuardrails()
        self.skills = TutorSkillRegistry()
        self.toolExecutor = AgentToolExecutor(session)
        self.progressTool = ProgressReadTool(session)
        self.pedagogicalTool = PedagogicalCreateTool(
            session
        )
        self.visualTool = VisualCreateTool(session)
        self.imageTool = ImageCreateTool(session)
        self.specialists = TutorSpecialistRegistry(session)

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
        imageTaskIds = []

        tools = list(plan.get("tools") or [])
        specialistScope = SpecialistScope(
            studentId=thread.studentId,
            studentLearningContextId=thread.studentLearningContextId,
            studentSubjectId=thread.studentSubjectId,
            studentLearningUnitId=thread.studentLearningUnitId,
            materialIds=tuple(materialIds),
            runId=run.agentRunId,
        )

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
                callback=lambda: self.specialists.evidence.collect(
                    scope=specialistScope,
                    query=userMessage.content,
                ).toToolResult(),
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

        if "IMAGE_GENERATION" in tools:
            imageMode = plan.get("imageMode") or "ILLUSTRATION"
            # Mind maps are structured visual tasks, never generated images.
            # Keep this guard for old persisted or model-produced plans.
            if imageMode != "MIND_MAP_COMPANION":
                action = self.toolExecutor.execute(
                    runId=run.agentRunId,
                    toolName="IMAGE_GENERATION",
                    request={
                        "imageMode": imageMode,
                        "materialIds": actionMaterialIds,
                        "relatedVisualTaskId": None,
                    },
                    callback=lambda: self.imageTool.execute(
                        studentId=thread.studentId,
                        imageMode=str(imageMode),
                        instruction=userMessage.content,
                        materialIds=actionMaterialIds,
                        studentLearningContextId=thread.studentLearningContextId,
                        studentSubjectId=thread.studentSubjectId,
                        studentLearningUnitId=thread.studentLearningUnitId,
                        agentThreadId=thread.agentThreadId,
                        agentRunId=run.agentRunId,
                        relatedVisualTaskId=None,
                    ),
                )
                actions.append({"type": "IMAGE_TASK", **action})
                imageTaskIds.append(action["imageTaskId"])
        run.stage = "ANSWERING"
        run.progressPercent = 75
        run.message = "A Lia está preparando a resposta."
        self.session.commit()

        draft = self.specialists.tutor.draft(
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

        review = self.specialists.review.review(
            draft=draft,
            evidence=(
                None
                if evidence is None
                else EvidenceBundle(
                    context=str(evidence.get("context") or ""),
                    hits=list(evidence.get("hits") or []),
                )
            ),
        )
        run.planJson["specialistReview"] = review.toPlanSummary()
        if not review.approved:
            raise DomainError(
                code=review.code or "SPECIALIST_REVIEW_REJECTED",
                message=review.message or "A revisão pedagógica recusou a resposta.",
                httpStatus=409,
            )
        response = draft.response

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
            imageTaskIds=imageTaskIds,
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
