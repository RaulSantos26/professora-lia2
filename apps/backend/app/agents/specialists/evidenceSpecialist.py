from app.agents.specialists.specialistContracts import EvidenceBundle, SpecialistScope


class EvidenceSpecialist:
    """Restricted specialist: only retrieves scoped, curated study evidence."""

    name = "evidence-specialist"

    def __init__(self, evidenceTool):
        self.evidenceTool = evidenceTool

    def collect(self, *, scope: SpecialistScope, query: str) -> EvidenceBundle:
        result = self.evidenceTool.execute(
            studentId=scope.studentId,
            query=query,
            studentLearningContextId=scope.studentLearningContextId,
            studentSubjectId=scope.studentSubjectId,
            studentLearningUnitId=scope.studentLearningUnitId,
            materialIds=list(scope.materialIds),
        )
        hits = list(result.get("hits") or [])
        scope.assertEvidenceScope(hits)
        return EvidenceBundle(
            context=str(result.get("context") or ""),
            hits=hits,
        )