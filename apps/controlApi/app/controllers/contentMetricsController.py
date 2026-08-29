from fastapi import APIRouter

from app.config.applicationSettings import settings
from app.contracts.contentMetricsContract import ContentMetricsContract
from app.repositories.contentMetricsRepository import ContentMetricsRepository


router = APIRouter(tags=["platform"])

repository = ContentMetricsRepository(
    host=settings.postgresHost,
    port=settings.postgresPort,
    user=settings.postgresUser,
    password=settings.postgresPassword,
    database=settings.postgresDb,
)


@router.get(
    "/platform/content-metrics",
    response_model=ContentMetricsContract,
)
async def getContentMetrics() -> ContentMetricsContract:
    return await repository.getMetrics()
