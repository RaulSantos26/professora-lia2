import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config.opsSettings import settings


opsTokenHeader = APIKeyHeader(
    name="X-Lia2-Ops-Token",
    auto_error=False,
)


def requireInternalToken(
    suppliedToken: str | None = Security(opsTokenHeader),
) -> None:
    expectedToken = settings.internalToken

    if not expectedToken:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpsAgent sem token interno configurado.",
        )

    if not suppliedToken or not secrets.compare_digest(suppliedToken, expectedToken):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token interno inválido.",
        )
