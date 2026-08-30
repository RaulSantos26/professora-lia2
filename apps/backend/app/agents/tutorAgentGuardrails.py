from app.domain.common.domainError import DomainError


class TutorAgentGuardrails:
    MAX_TOOL_CALLS = 4

    ALLOWED_TOOLS = {
        "EVIDENCE_SEARCH",
        "PROGRESS_READ",
        "PEDAGOGICAL_CREATE",
        "VISUAL_CREATE",
        "IMAGE_GENERATION",
    }

    def validatePlan(self, plan: dict) -> None:
        tools = plan.get("tools") or []

        if len(tools) > self.MAX_TOOL_CALLS:
            raise DomainError(
                code="AGENT_TOOL_LIMIT_EXCEEDED",
                message=(
                    "O plano da Lia excedeu o limite seguro "
                    "de ferramentas por execução."
                ),
                httpStatus=409,
            )

        invalid = [
            tool
            for tool in tools
            if tool not in self.ALLOWED_TOOLS
        ]

        if invalid:
            raise DomainError(
                code="AGENT_TOOL_NOT_ALLOWED",
                message=(
                    "O plano solicitou ferramentas não permitidas: "
                    + ", ".join(invalid)
                ),
                httpStatus=409,
            )

        intent = plan.get("intent")

        if (
            intent
            not in {
                "PROGRESS",
                "GREETING",
            }
            and "EVIDENCE_SEARCH" not in tools
        ):
            raise DomainError(
                code="AGENT_EVIDENCE_REQUIRED",
                message=(
                    "A Lia precisa consultar evidências antes "
                    "de responder conteúdo de estudo."
                ),
                httpStatus=409,
            )
