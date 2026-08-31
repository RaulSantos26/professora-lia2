import logging
import os
import queue
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
                job.seed = seed
                generator = torch.Generator("cpu").manual_seed(seed)
                image = self.pipeline(
                    prompt=job.request.prompt,
                    width=job.request.width,
                    height=job.request.height,
                    num_inference_steps=job.request.steps,
                    guidance_scale=0.0,
                    generator=generator,
                ).images[0]

                job.status = "LABELING"
                job.progressPercent = 82
                job.message = "Revisando a ilustração e montando a prancha em português."
                composed = self._composeTeachingBoard(
                    image,
                    job.request.title,
                    job.request.labels,
                )
                filename = f"{job.request.requestId}.png"
                composed.save(self.outputPath / filename, format="PNG")
                job.assetFilename = filename
                job.status = "READY"
                job.progressPercent = 100
                job.message = "Imagem didática pronta."
                job.elapsedSeconds = round(time.monotonic() - startedAt, 3)
            except Exception as error:
                job.status = "ERROR"
                job.progressPercent = 100
                job.message = "Não foi possível gerar a imagem didática."
                job.errorCode = type(error).__name__.upper()
                job.errorMessage = str(error)[:1000]
                job.elapsedSeconds = round(time.monotonic() - startedAt, 3)
                logger.exception("Image generation failed requestId=%s", job.request.requestId)
            finally:
                self.busy = False


    def _composeTeachingBoard(self, image, title: str, labels: list[str]):
        from PIL import Image, ImageDraw, ImageFont

        cleanImage = self._removeDetectedText(image)
        width, height = cleanImage.size
        board = Image.new("RGB", (width, height), (252, 248, 240))
        draw = ImageDraw.Draw(board)
        fontPath = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        titleFont = ImageFont.truetype(fontPath, max(22, width // 26))
        headingFont = ImageFont.truetype(fontPath, max(14, width // 52))
        bodyFont = ImageFont.truetype(fontPath, max(11, width // 68))

        lesson = next((item.removeprefix("Lição: ") for item in labels if item.startswith("Lição: ")), "Ilustração didática")
        concepts = [item.split("|", 1) for item in labels if "|" in item]
        draw.text((22, 16), lesson[:54], font=titleFont, fill=(14, 49, 94))

        leftWidth = 220 if concepts else 20
        visualX = leftWidth + 12
        visualY = 82
        visualWidth = width - visualX - 18
        visualHeight = height - visualY - 22
        visual = cleanImage.copy()
        visual.thumbnail((visualWidth, visualHeight), Image.Resampling.LANCZOS)
        visualX += (visualWidth - visual.width) // 2
        visualY += (visualHeight - visual.height) // 2
        board.paste(visual, (visualX, visualY))

        protectedTextAreas = [(0, 0, width, 70)]
        if concepts:
            y = 82
            for name, description in concepts[:5]:
                draw.rounded_rectangle((16, y, leftWidth, y + 80), radius=12, fill=(255, 255, 255), outline=(108, 139, 88), width=1)
                draw.text((28, y + 12), name[:22], font=headingFont, fill=(14, 49, 94))
                self._drawWrapped(draw, (28, y + 35), description[:74], bodyFont, 170, (32, 50, 70))
                protectedTextAreas.append((16, y, leftWidth, y + 80))
                y += 88
        else:
            explanation = next((item.removeprefix("Explicação visual: ") for item in labels if item.startswith("Explicação visual: ")), "")
            self._drawWrapped(draw, (22, 62), explanation, bodyFont, width - 44, (32, 50, 70))
        return self._removeDetectedText(board, protectedTextAreas)

    def _removeDetectedText(self, image, protectedTextAreas=None):
        from PIL import Image, ImageFilter
        try:
            import pytesseract
            from pytesseract import Output
            data = pytesseract.image_to_data(image, config="--psm 11", output_type=Output.DICT)
            cleaned = image.convert("RGB").copy()
            for index, value in enumerate(data["text"]):
                confidence = float(data["conf"][index])
                if not value.strip() or confidence < 0:
                    continue
                x, y = data["left"][index], data["top"][index]
                w, h = data["width"][index], data["height"][index]
                pad = max(8, min(20, h))
                area = (max(0, x - pad), max(0, y - pad), min(cleaned.width, x + w + pad), min(cleaned.height, y + h + pad))
                if any(
                    area[0] < protected[2] and area[2] > protected[0]
                    and area[1] < protected[3] and area[3] > protected[1]
                    for protected in (protectedTextAreas or [])
                ):
                    continue
                patch = cleaned.crop(area)
                washed = patch.resize(
                    (max(1, patch.width // 16), max(1, patch.height // 16)),
                    Image.Resampling.BILINEAR,
                ).resize(patch.size, Image.Resampling.BILINEAR)
                cleaned.paste(washed.filter(ImageFilter.GaussianBlur(radius=4)), area)
            return cleaned
        except Exception:
            logger.warning("Text review unavailable; preserving the generated visual", exc_info=True)
            return image.convert("RGB")

    def _drawWrapped(self, draw, origin, text: str, font, maxWidth: int, fill):
        words = text.split()
        line = ""
        x, y = origin
        for word in words:
            candidate = f"{line} {word}".strip()
            if line and draw.textlength(candidate, font=font) > maxWidth:
                draw.text((x, y), line, font=font, fill=fill)
                y += font.size + 3
                line = word
            else:
                line = candidate
        if line:
            draw.text((x, y), line, font=font, fill=fill)

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
