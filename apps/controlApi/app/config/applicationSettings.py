import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ApplicationSettings:
    environment: str = os.getenv("LIA2_ENVIRONMENT", "DEV")
    release: str = os.getenv("LIA2_RELEASE", "unknown")
    backendUrl: str = os.getenv("LIA2_BACKEND_URL", "http://lia2-backend:8000")
    ollamaUrl: str = os.getenv("LIA2_OLLAMA_URL", "http://ollama:11434")
    opsAgentUrl: str = os.getenv("LIA2_OPS_AGENT_URL", "http://lia2-ops-agent:8000")
    opsInternalToken: str = field(
        default=os.getenv("LIA2_OPS_INTERNAL_TOKEN", ""),
        repr=False,
    )
    adminToken: str = field(
        default=os.getenv("LIA2_ADMIN_TOKEN", ""),
        repr=False,
    )
    postgresHost: str = os.getenv("LIA2_POSTGRES_HOST", "postgres")
    postgresPort: int = int(os.getenv("LIA2_POSTGRES_PORT", "5432"))
    postgresUser: str = os.getenv("LIA2_POSTGRES_USER", "")
    postgresPassword: str = field(
        default=os.getenv("LIA2_POSTGRES_PASSWORD", ""),
        repr=False,
    )
    postgresDb: str = os.getenv("LIA2_POSTGRES_DB", "")


settings = ApplicationSettings()
