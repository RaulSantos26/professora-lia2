from uuid import UUID

from sqlalchemy.orm import Session

from app.contracts.visualTaskContract import VisualTaskCreateContract
from app.services.visualLearningService import VisualLearningService


class VisualCreateTool:
    toolName = "VISUAL_CREATE"

    def __init__(self, session: Session):
        self.service = VisualLearningService(session)

    def execute(
        self,
        *,
        studentId: UUID,
        visualType: str,
        instruction: str,
        materialIds: list[UUID],
        studentLearningContextId: UUID,
        studentSubjectId: UUID,
        studentLearningUnitId: UUID,
        requestedTextModelId: str | None,
        thinkingMode: str,
        agentThreadId: UUID,
        agentRunId: UUID,
    ) -> dict:
        visual = self.service.create(
            studentId=studentId,
            request=VisualTaskCreateContract(
                visualType=visualType,
                instruction=instruction,
                materialIds=materialIds,
                studentLearningContextId=studentLearningContextId,
                studentSubjectId=studentSubjectId,
                studentLearningUnitId=studentLearningUnitId,
                requestedTextModelId=requestedTextModelId,
                thinkingMode=thinkingMode,
            ),
            agentThreadId=agentThreadId,
            agentRunId=agentRunId,
        )

        return {
            "visualTaskId": str(
                visual.visualTaskId
            ),
            "visualType": visual.visualType,
            "renderer": visual.renderer,
            "title": visual.title,
        }
