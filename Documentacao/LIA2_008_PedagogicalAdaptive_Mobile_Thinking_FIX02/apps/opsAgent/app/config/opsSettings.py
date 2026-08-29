import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class OpsSettings:
    environment: str = os.getenv("LIA2_ENVIRONMENT", "DEV")
    release: str = os.getenv("LIA2_RELEASE", "unknown")
    internalToken: str = field(
        default=os.getenv("LIA2_OPS_INTERNAL_TOKEN", ""),
        repr=False,
    )
    auditPath: str = os.getenv(
        "LIA2_OPS_AUDIT_PATH",
        "/var/lib/lia2-ops-audit/operationalEvents.jsonl",
    )


settings = OpsSettings()
