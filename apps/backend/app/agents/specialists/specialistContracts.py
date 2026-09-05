from dataclasses import dataclass
from uuid import UUID

from app.domain.common.domainError import DomainError


@dataclass(frozen=True)
class SpecialistScope:
    studentId: UUID
    studentLearningContextId: UUID
    studentSubjectId: UUID
    studentLearningUnitId: UUID
    materialIds: tuple[UUID, ...]
    runId: UUID

    def assertEvidenceScope(self, hits: list[dict]) -> None:
        if not self.materialIds:
            return

        allowed = {str(materialId) for materialId in self.materialIds}
        invalid = [
            hit.get("materialId")
            for hit in hits
            if hit.get("materialId") not in allowed
        ]
        if invalid:
            raise DomainError(
                code="SPECIALIST_SCOPE_MISMATCH",
                message="O especialista recebeu evidências fora da lição selecionada.",
                httpStatus=409,
            )


@dataclass(frozen=True)
class EvidenceBundle:
    context: str
    hits: list[dict]

    def toToolResult(self) -> dict:
        return {"context": self.context, "hits": self.hits}


@dataclass(frozen=True)
class TutorDraft:
    response: dict


@dataclass(frozen=True)
class PedagogicalReview:
    approved: bool
    code: str | None
    message: str | None

    def toPlanSummary(self) -> dict:
        return {
            "approved": self.approved,
            "code": self.code,
            "message": self.message,
        }