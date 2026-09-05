from app.agents.specialists.specialistContracts import EvidenceBundle, PedagogicalReview, TutorDraft


class PedagogicalReviewSpecialist:
    """Deterministic acceptance gate; it never calls models, storage or tools."""

    name = "pedagogical-review-specialist"

    def review(self, *, draft: TutorDraft, evidence: EvidenceBundle | None) -> PedagogicalReview:
        answer = str(draft.response.get("answer") or "").strip()
        if not answer:
            return PedagogicalReview(
                approved=False,
                code="SPECIALIST_EMPTY_ANSWER",
                message="A revisão pedagógica recusou uma resposta vazia.",
            )
        if evidence is not None and not evidence.hits:
            return PedagogicalReview(
                approved=False,
                code="SPECIALIST_EVIDENCE_EMPTY",
                message="A revisão pedagógica recusou resposta sem evidências da lição.",
            )
        return PedagogicalReview(approved=True, code=None, message=None)