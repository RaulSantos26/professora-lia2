from fastapi import FastAPI

from app.controllers.operationsController import router as operationsRouter
from app.controllers.platformHealthController import router as platformHealthRouter
from app.controllers.contentMetricsController import router as contentMetricsRouter
from app.observability.correlationMiddleware import CorrelationMiddleware


application = FastAPI(
    title="Professora LIA 2.0 Control API",
    version="0.7.2-agentic-tutor-ux-map-fix02",
)

application.add_middleware(CorrelationMiddleware)
application.include_router(platformHealthRouter)
application.include_router(contentMetricsRouter)
application.include_router(operationsRouter)
