from fastapi import APIRouter, Query

from app.contracts.aiModelContract import AiModelRegistryContract
from app.services.aiModelRegistryService import AiModelRegistryService


router = APIRouter(
    prefix="/ai",
    tags=["ai-models"],
)


@router.get(
    "/models",
    response_model=AiModelRegistryContract,
)
def listModels(
    forceRefresh: bool = Query(default=False),
) -> AiModelRegistryContract:
    return AiModelRegistryService().listModels(forceRefresh)
