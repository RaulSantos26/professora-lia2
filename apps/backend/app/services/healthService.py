import os
from datetime import datetime, timezone

from app.contracts.serviceStatusContract import ServiceStatusContract


class HealthService:
    def getStatus(self) -> ServiceStatusContract:
        return ServiceStatusContract(
            serviceName="lia2-backend",
            status="ONLINE",
            checkedAt=datetime.now(timezone.utc),
            version=os.getenv("LIA2_RELEASE", "unknown"),
            environment=os.getenv("LIA2_ENVIRONMENT", "DEV"),
        )
