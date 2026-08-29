import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config.applicationSettings import settings


adminTokenHeader = APIKeyHeader(
    name="X-Lia2-Admin-Token",
    auto_error=False,
)


def requireAdminToken(
    suppliedToken: str | None = Security(adminTokenHeader),
) -> None:
    expectedToken = settings.adminToken

    if not expectedToken:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Control API sem token administrativo configurado.",
        )

    if not suppliedToken or not secrets.compare_digest(suppliedToken, expectedToken):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token administrativo inválido.",
        )
