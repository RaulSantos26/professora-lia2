from uuid import UUID

from sqlalchemy.orm import Session

from app.contracts.pedagogicalContract import PedagogicalArtifactCreateContract
from app.services.pedagogicalService import PedagogicalService


class PedagogicalCreateTool:
    toolName = "PEDAGOGICAL_CREATE"

    def __init__(self, session: Session):
        self.service = PedagogicalService(session)

    def execute(
        self,
        *,
        studentId: UUID,
        artifactType: str,
        instruction: str,
        materialIds: list[UUID],
        studentLearningContextId: UUID,
        studentSubjectId: UUID,
        studentLearningUnitId: UUID,
        requestedTextModelId: str | None,
        thinkingMode: str,
    ) -> dict:
        artifact = self.service.createArtifact(
            studentId=studentId,
            request=PedagogicalArtifactCreateContract(
                artifactType=artifactType,
                instruction=instruction,
                materialIds=materialIds,
                studentLearningContextId=studentLearningContextId,
                studentSubjectId=studentSubjectId,
                studentLearningUnitId=studentLearningUnitId,
                difficulty="AUTO",
                questionCount=8,
                requestedTextModelId=requestedTextModelId,
                thinkingMode=thinkingMode,
            ),
        )

        return {
            "pedagogicalArtifactId": str(
                artifact.pedagogicalArtifactId
            ),
            "artifactType": artifact.artifactType,
            "status": artifact.status,
            "title": artifact.title,
        }
