import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers.healthController import router as healthRouter
from app.controllers.learningContextController import router as learningContextRouter
from app.controllers.studentLearningContextController import router as studentLearningContextRouter
from app.controllers.subjectController import router as subjectRouter
from app.controllers.learningContextSubjectController import router as learningContextSubjectRouter
from app.controllers.learningUnitController import router as learningUnitRouter
from app.controllers.studentSubjectController import router as studentSubjectRouter
from app.controllers.studentLearningUnitController import router as studentLearningUnitRouter
from app.controllers.learningGoalController import router as learningGoalRouter
from app.controllers.studyScopeController import router as studyScopeRouter
from app.controllers.studySessionController import router as studySessionRouter
from app.controllers.studentLearningStateController import router as studentLearningStateRouter
from app.controllers.materialController import router as materialRouter
from app.controllers.materialProcessingController import router as materialProcessingRouter
from app.controllers.learningGuideController import router as learningGuideRouter
from app.controllers.aiModelController import router as aiModelRouter
from app.controllers.workspaceSummaryController import router as workspaceSummaryRouter
from app.controllers.ragController import router as ragRouter
from app.controllers.pedagogicalController import router as pedagogicalRouter
from app.controllers.studentController import router as studentRouter
from app.domain.common.domainError import DomainError
from app.services.materialProcessingWorker import materialProcessingWorker
from app.services.pedagogicalWorker import pedagogicalWorker
from app.observability.correlationMiddleware import CorrelationMiddleware


application = FastAPI(
    title="Professora LIA 2.0 Backend",
    version="0.6.3-pedagogical-adaptive-mobile-thinking-fix02",
)

application.add_middleware(CorrelationMiddleware)
application.include_router(healthRouter)
application.include_router(studentRouter)
application.include_router(learningContextRouter)
application.include_router(studentLearningContextRouter)
application.include_router(subjectRouter)
application.include_router(learningContextSubjectRouter)
application.include_router(learningUnitRouter)
application.include_router(studentSubjectRouter)
application.include_router(studentLearningUnitRouter)
application.include_router(learningGoalRouter)
application.include_router(studyScopeRouter)
application.include_router(studySessionRouter)
application.include_router(studentLearningStateRouter)
application.include_router(materialRouter)
application.include_router(materialProcessingRouter)
application.include_router(learningGuideRouter)
application.include_router(aiModelRouter)
application.include_router(workspaceSummaryRouter)
application.include_router(ragRouter)
application.include_router(pedagogicalRouter)


@application.on_event("startup")
async def startMaterialProcessingWorker() -> None:
    materialProcessingWorker.start()
    pedagogicalWorker.start()


@application.on_event("shutdown")
async def stopMaterialProcessingWorker() -> None:
    materialProcessingWorker.stop()
    pedagogicalWorker.stop()


@application.exception_handler(DomainError)
async def handleDomainError(
    request: Request,
    error: DomainError,
) -> JSONResponse:
    correlationId = getattr(request.state, "correlationId", None)

    return JSONResponse(
        status_code=error.httpStatus,
        content={
            "contractName": "Error.v1",
            "code": error.code,
            "message": error.message,
            "correlationId": correlationId,
        },
    )


logger = logging.getLogger(__name__)


@application.exception_handler(Exception)
async def handleUnexpectedError(
    request: Request,
    error: Exception,
) -> JSONResponse:
    correlationId = getattr(
        request.state,
        "correlationId",
        None,
    )

    logger.exception(
        "Unhandled backend error correlationId=%s path=%s",
        correlationId,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "contractName": "Error.v1",
            "code": "INTERNAL_ERROR",
            "message": (
                "Ocorreu uma falha inesperada. "
                "Use o código de correlação para diagnóstico."
            ),
            "correlationId": correlationId,
        },
    )
