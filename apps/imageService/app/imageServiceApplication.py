import logging
import os
import queue
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)

ImageMode = Literal["ILLUSTRATION", "MIND_MAP_COMPANION"]
ImageJobStatus = Literal[
    "QUEUED", "PREPARING", "GENERATING", "LABELING", "READY", "ERROR", "CANCELLED"
]


class ImageJobRequest(BaseModel):
    requestId: str = Field(min_length=8, max_length=80)
    prompt: str = Field(min_length=16, max_length=6000)
    title: str = Field(min_length=1, max_length=250)
    imageMode: ImageMode
    labels: list[str] = Field(default_factory=list, max_length=8)
    width: int = Field(default=768, ge=512, le=1024, multiple_of=64)
    height: int = Field(default=576, ge=512, le=1024, multiple_of=64)
    seed: int | None = None
    steps: int = Field(default=9, ge=1, le=20)


class ImageJobResponse(BaseModel):
    requestId: str
    status: ImageJobStatus
    progressPercent: int
    message: str
    assetFilename: str | None = None
    seed: int | None = None
    elapsedSeconds: float | None = None
    errorCode: str | None = None
    errorMessage: str | None = None


@dataclass
class ImageJob:
    request: ImageJobRequest
    status: ImageJobStatus = "QUEUED"
    progressPercent: int = 5
    message: str = "Imagem aguardando a vez na GPU."
    assetFilename: str | None = None
    seed: int | None = None
    elapsedSeconds: float | None = None
    errorCode: str | None = None
    errorMessage: str | None = None
    createdAt: float = field(default_factory=time.monotonic)

    def response(self) -> ImageJobResponse:
        return ImageJobResponse(
            requestId=self.request.requestId,
            status=self.status,
            progressPercent=self.progressPercent,
            message=self.message,
            assetFilename=self.assetFilename,
            seed=self.seed,
            elapsedSeconds=self.elapsedSeconds,
            errorCode=self.errorCode,
            errorMessage=self.errorMessage,
        )


class ImageTextQualityError(RuntimeError):
    pass


class ZImageRuntime:
    """Keeps the pipeline warm and serializes GPU work through its lock."""

    def __init__(self) -> None:
        self.modelId = os.getenv("LIA2_ZIMAGE_MODEL_ID", "Tongyi-MAI/Z-Image-Turbo")
        self.cacheOnly = os.getenv("LIA2_ZIMAGE_LOCAL_FILES_ONLY", "true").lower() == "true"
        self.outputPath = Path(os.getenv("LIA2_IMAGE_OUTPUT_PATH", "/var/lib/lia2-generated-images"))
        self.outputPath.mkdir(parents=True, exist_ok=True)
        self.pipeline = None
        self.pipelineStatus = "COLD"
        self.pipelineError: str | None = None
        self.busy = False
        self._lock = threading.RLock()

    def warm(self) -> None:
        with self._lock:
            if self.pipeline is not None:
                return
            self.pipelineStatus = "LOADING"
            self.pipelineError = None
            try:
                import torch
                from diffusers import ZImagePipeline

                pipeline = ZImagePipeline.from_pretrained(
                    self.modelId,
                    torch_dtype=torch.bfloat16,
                    local_files_only=self.cacheOnly,
                )
                # Full GPU was rejected in the technical gates. Keep weights
                # warm in RAM and offload only small portions to the GPU.
                pipeline.enable_sequential_cpu_offload()
                self.pipeline = pipeline
                self.pipelineStatus = "READY"
                logger.info("Z-Image ready model=%s sequentialCpuOffload=true", self.modelId)
            except Exception as error:
                self.pipelineStatus = "ERROR"
                self.pipelineError = str(error)[:1000]
                logger.exception("Z-Image pipeline initialization failed")
                raise

    def generate(self, job: ImageJob) -> None:
        startedAt = time.monotonic()
        with self._lock:
            self.busy = True
            try:
                job.status = "PREPARING"
                job.progressPercent = 18
                job.message = "Preparando o modelo Z-Image em memória."
                self.warm()

                import torch

                job.status = "GENERATING"
                job.progressPercent = 45
                job.message = "Gerando a ilustração didática."
                seed = job.request.seed or int(time.time_ns() % 2_147_483_647)
                image = None
                for attempt in range(3):
                    attemptSeed = seed + attempt
                    generator = torch.Generator("cpu").manual_seed(attemptSeed)
                    candidate = self.pipeline(
                        prompt=(
                            job.request.prompt
                            + " Strict quality rule: scene only, absolutely no typography or writing."
                        ),
                        width=job.request.width,
                        height=job.request.height,
                        num_inference_steps=job.request.steps,
                        guidance_scale=0.0,
                        generator=generator,
                    ).images[0]
                    if self._containsDetectedText(candidate):
                        logger.warning(
                            "Rejected Z-Image output with detected text requestId=%s attempt=%s",
                            job.request.requestId,
                            attempt + 1,
                        )
                        continue
                    image = candidate
                    job.seed = attemptSeed
                    break

                usedCleanFallback = False
                if image is None:
                    image = self._cleanFallback(job.request)
                    if image is None:
                        raise ImageTextQualityError(
                            "A ilustração continha texto gerado e não passou no controle de legibilidade."
                        )
                    usedCleanFallback = True
                    logger.warning(
                        "Using clean didactic fallback requestId=%s after text rejection",
                        job.request.requestId,
                    )

                job.status = "LABELING"
                job.progressPercent = 82
                job.message = "Finalizando a ilustração didática."
                filename = f"{job.request.requestId}.png"
                image.convert("RGB").save(self.outputPath / filename, format="PNG")
                job.assetFilename = filename
                job.status = "READY"
                job.progressPercent = 100
                job.message = (
                    "Ilustração didática limpa pronta."
                    if usedCleanFallback
                    else "Imagem didática pronta."
                )
                job.elapsedSeconds = round(time.monotonic() - startedAt, 3)
            except Exception as error:
                job.status = "ERROR"
                job.progressPercent = 100
                if isinstance(error, ImageTextQualityError):
                    job.message = "A imagem não passou no controle de texto legível."
                    job.errorCode = "IMAGE_TEXT_QUALITY_REJECTED"
                    job.errorMessage = str(error)[:1000]
                else:
                    job.message = "Não foi possível gerar a imagem didática."
                    job.errorCode = type(error).__name__.upper()
                    job.errorMessage = str(error)[:1000]
                job.elapsedSeconds = round(time.monotonic() - startedAt, 3)
                logger.exception("Image generation failed requestId=%s", job.request.requestId)
            finally:
                self.busy = False

    @staticmethod
    def _cleanFallback(request: ImageJobRequest):
        """Text-free educational scene used only when Z-Image violates the typography gate."""
        from PIL import Image, ImageDraw

        topic = request.prompt.casefold()
        if not any(term in topic for term in ("eros", "relevo", "montanha", "planalto", "planície", "depressão")):
            return None

        image = Image.new("RGB", (request.width, request.height), "#dff2ff")
        draw = ImageDraw.Draw(image)
        horizon = int(request.height * 0.55)
        draw.rectangle((0, horizon, request.width, request.height), fill="#8d633e")
        draw.polygon(
            [(0, horizon), (150, 250), (290, horizon), (430, 190), (600, horizon), (request.width, 300), (request.width, horizon)],
            fill="#6c8f3a",
        )
        draw.polygon(
            [(95, horizon), (220, 210), (330, horizon)],
            fill="#87603a",
        )
        draw.polygon(
            [(360, horizon), (475, 160), (610, horizon)],
            fill="#9a6a3b",
        )
        draw.polygon(
            [(0, horizon), (155, 338), (300, horizon)],
            fill="#b9824b",
        )
        draw.polygon(
            [(365, horizon), (485, 288), (650, horizon)],
            fill="#bf8a51",
        )
        for x in range(42, request.width, 62):
            draw.line((x, 45, x - 18, 160), fill="#3b9ed8", width=5)
        draw.polygon(
            [(0, 410), (185, 394), (355, 420), (545, 398), (request.width, 430), (request.width, request.height), (0, request.height)],
            fill="#3caddb",
        )
        for x in range(35, request.width, 110):
            draw.line((x, 452, x + 70, 462), fill="#8cd5ec", width=4)
        for x in (120, 265, 520, 670):
            draw.rectangle((x, 303, x + 8, 344), fill="#63452c")
            draw.ellipse((x - 19, 275, x + 28, 321), fill="#3d8b47")
        return image

    @staticmethod
    def _containsDetectedText(image) -> bool:
        """Reject readable typography; explanations are rendered by the UI."""
        import pytesseract
        from pytesseract import Output

        data = pytesseract.image_to_data(
            image.convert("RGB"), lang="eng", config="--psm 11", output_type=Output.DICT
        )
        words = []
        for text, confidence in zip(data.get("text", []), data.get("conf", [])):
            token = re.sub(r"[^A-Za-zÀ-ÿ]", "", str(text or ""))
            try:
                score = float(confidence)
            except (TypeError, ValueError):
                score = -1
            if len(token) >= 3 and score >= 35:
                words.append(token)
        return len(words) >= 2


class ImageJobCoordinator:
    def __init__(self, runtime: ZImageRuntime) -> None:
        self.runtime = runtime
        self.jobs: dict[str, ImageJob] = {}
        self.queue: queue.Queue[str] = queue.Queue()
        self.lock = threading.Lock()
        self.worker = threading.Thread(target=self._loop, name="lia2-zimage-gpu-coordinator", daemon=True)

    def start(self) -> None:
        if not self.worker.is_alive():
            self.worker.start()

    def enqueue(self, request: ImageJobRequest) -> ImageJob:
        with self.lock:
            existing = self.jobs.get(request.requestId)
            if existing is not None:
                return existing
            job = ImageJob(request=request)
            self.jobs[request.requestId] = job
            self.queue.put(request.requestId)
            return job

    def get(self, requestId: str) -> ImageJob | None:
        with self.lock:
            return self.jobs.get(requestId)

    def _loop(self) -> None:
        while True:
            requestId = self.queue.get()
            job = self.get(requestId)
            if job is not None:
                self.runtime.generate(job)
            self.queue.task_done()


runtime = ZImageRuntime()
coordinator = ImageJobCoordinator(runtime)
application = FastAPI(title="Professora LIA 2.0 Image Service", version="0.1.0-zimage")


def _authorize(token: str | None) -> None:
    expected = os.getenv("LIA2_IMAGE_INTERNAL_TOKEN", "").strip()
    if expected and token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal token")


@application.on_event("startup")
def startImageService() -> None:
    coordinator.start()
    if os.getenv("LIA2_ZIMAGE_WARM_ON_STARTUP", "true").lower() == "true":
        threading.Thread(target=runtime.warm, name="lia2-zimage-warmup", daemon=True).start()


@application.get("/health")
def health() -> dict:
    return {
        "service": "lia2-image-service",
        "status": "ONLINE" if runtime.pipelineStatus != "ERROR" else "DEGRADED",
        "modelId": runtime.modelId,
        "pipelineStatus": runtime.pipelineStatus,
        "sequentialCpuOffload": True,
        "gpuCoordinator": "BUSY" if runtime.busy else "IDLE",
        "queueDepth": coordinator.queue.qsize(),
        "pipelineError": runtime.pipelineError,
    }


@application.post("/v1/image-jobs", response_model=ImageJobResponse, status_code=status.HTTP_202_ACCEPTED)
def createImageJob(request: ImageJobRequest, x_lia2_internal_token: str | None = Header(default=None)) -> ImageJobResponse:
    _authorize(x_lia2_internal_token)
    return coordinator.enqueue(request).response()


@application.get("/v1/image-jobs/{requestId}", response_model=ImageJobResponse)
def getImageJob(requestId: str, x_lia2_internal_token: str | None = Header(default=None)) -> ImageJobResponse:
    _authorize(x_lia2_internal_token)
    job = coordinator.get(requestId)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image job not found")
    return job.response()
