import pytest

from app.agents.tutorAgentGuardrails import TutorAgentGuardrails
from app.domain.common.domainError import DomainError


def testContentIntentRequiresEvidenceSearch():
    guardrails = TutorAgentGuardrails()

    with pytest.raises(DomainError) as captured:
        guardrails.validatePlan(
            {
                "intent": "EXPLAIN",
                "tools": ["PEDAGOGICAL_CREATE"],
            }
        )

    assert captured.value.code == "AGENT_EVIDENCE_REQUIRED"


def testProgressDoesNotRequireEvidence():
    TutorAgentGuardrails().validatePlan(
        {
            "intent": "PROGRESS",
            "tools": ["PROGRESS_READ"],
        }
    )


def testUnknownToolIsRejected():
    with pytest.raises(DomainError) as captured:
        TutorAgentGuardrails().validatePlan(
            {
                "intent": "ANSWER",
                "tools": [
                    "EVIDENCE_SEARCH",
                    "UNSAFE_TOOL",
                ],
            }
        )

    assert captured.value.code == "AGENT_TOOL_NOT_ALLOWED"


def testToolCallLimitIsEnforced():
    with pytest.raises(DomainError) as captured:
        TutorAgentGuardrails().validatePlan(
            {
                "intent": "ANSWER",
                "tools": [
                    "EVIDENCE_SEARCH",
                    "PROGRESS_READ",
                    "PEDAGOGICAL_CREATE",
                    "VISUAL_CREATE",
                    "VISUAL_CREATE",
                ],
            }
        )

    assert captured.value.code == "AGENT_TOOL_LIMIT_EXCEEDED"
