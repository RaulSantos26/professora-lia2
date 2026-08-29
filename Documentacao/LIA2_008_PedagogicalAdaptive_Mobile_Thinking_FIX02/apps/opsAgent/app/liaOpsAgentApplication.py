from fastapi import FastAPI

from app.controllers.healthController import router as healthRouter
from app.controllers.operationsController import router as operationsRouter


application = FastAPI(
    title="Professora LIA 2.0 Ops Agent",
    version="0.1.1-ops",
)

application.include_router(healthRouter)
application.include_router(operationsRouter)
