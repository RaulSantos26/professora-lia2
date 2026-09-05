from uuid import uuid4

import pytest

from app.agents.specialists.evidenceSpecialist import EvidenceSpecialist
from app.agents.specialists.specialistContracts import SpecialistScope
from app.domain.common.domainError import DomainError


def testEvidenceSpecialistRejectsEvidenceOutsideSelectedMaterialScope():
    allowed_material = uuid4()
    scope = SpecialistScope(
        studentId=uuid4(),
        studentLearningContextId=uuid4(),
        studentSubjectId=uuid4(),
        studentLearningUnitId=uuid4(),
        materialIds=(allowed_material,),
        runId=uuid4(),
    )

    class FakeEvidenceTool:
        def execute(self, **_request):
            return {
                "context": "texto",
                "hits": [{"materialId": str(uuid4()), "index": 1}],
            }

    with pytest.raises(DomainError, match="fora da lição"):
        EvidenceSpecialist(FakeEvidenceTool()).collect(
            scope=scope,
            query="O que é erosão?",
        )


def testHarnessUsesAllowlistedInternalSpecialists():
    source = open(
        "app/agents/tutorAgentHarness.py",
        encoding="utf-8",
    ).read()

    assert "TutorSpecialistRegistry" in source
    assert "self.specialists.evidence.collect" in source
    assert "self.specialists.tutor.draft" in source
    assert "self.specialists.review.review" in source