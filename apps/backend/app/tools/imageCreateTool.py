from uuid import UUID

from sqlalchemy.orm import Session

from app.services.imageGenerationService import ImageGenerationService


class ImageCreateTool:
    toolName = "IMAGE_GENERATION"

    def __init__(self, session: Session):
        self.service = ImageGenerationService(session)

    def execute(self, *, studentId: UUID, imageMode: str, instruction: str, materialIds: list[UUID], studentLearningContextId: UUID, studentSubjectId: UUID, studentLearningUnitId: UUID, agentThreadId: UUID, agentRunId: UUID, relatedVisualTaskId: UUID | None = None) -> dict:
        task = self.service.create(studentId=studentId, imageMode=imageMode, instruction=instruction, materialIds=materialIds, studentLearningContextId=studentLearningContextId, studentSubjectId=studentSubjectId, studentLearningUnitId=studentLearningUnitId, agentThreadId=agentThreadId, agentRunId=agentRunId, relatedVisualTaskId=relatedVisualTaskId)
        return {"imageTaskId": str(task.imageTaskId), "imageMode": task.imageMode, "status": task.status, "title": task.title}
