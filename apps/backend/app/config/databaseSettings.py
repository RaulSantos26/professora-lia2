import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatabaseSettings:
    host: str = os.getenv("LIA2_POSTGRES_HOST", "postgres")
    port: int = int(os.getenv("LIA2_POSTGRES_PORT", "5432"))
    user: str = os.getenv("LIA2_POSTGRES_USER", "")
    password: str = field(
        default=os.getenv("LIA2_POSTGRES_PASSWORD", ""),
        repr=False,
    )
    database: str = os.getenv("LIA2_POSTGRES_DB", "")


databaseSettings = DatabaseSettings()
