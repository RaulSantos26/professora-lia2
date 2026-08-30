from pathlib import Path

from PIL import Image, ImageOps

from app.contracts.visionAnalysisContract import VisionAnalysisContract
from app.services.ollamaClientService import OllamaClientService


class VisionAnalysisService:
    PROMPT = """
Você está analisando uma página ou imagem de material educacional.

Objetivos:
1. Detecte se a imagem precisa ser girada para ficar na orientação correta.
2. TRANSCRIÇÃO É A PRIORIDADE: copie integralmente cada parágrafo legível,
   na ordem em que aparece. Corrija somente erros evidentes do OCR preliminar,
   sem inventar trechos que não possa ver.
3. Identifique figuras, diagramas, tabelas, fotos e legendas.
4. Descreva apenas elementos visualmente sustentados pela imagem.
5. Preserve rótulos importantes de diagramas no campo labels.
6. Escreva summary, description, title e demais descrições em português brasileiro.
7. Preserve no idioma original apenas o texto literalmente presente na imagem.

orientationDegrees deve ser 0, 90, 180 ou 270 e significa quantos graus
a imagem precisa ser girada NO SENTIDO HORÁRIO para ficar corretamente
orientada.

Preencha extractedText com a transcrição completa. summary é somente um
resumo curto e nunca substitui a transcrição.
Se não houver texto legível, extractedText deve ser string vazia.
"""

    def __init__(self):
        self.ollama = OllamaClientService()

    def normalizeExif(self, imagePath: Path) -> None:
        with Image.open(imagePath) as image:
            normalized = ImageOps.exif_transpose(image)

            if normalized is not image:
                normalized.convert("RGB").save(
                    imagePath,
                    format=self._format(imagePath),
                    quality=92,
                )

    def analyze(
        self,
        *,
        imagePath: Path,
        modelId: str,
        thinkingEnabled: bool = False,
        ocrHint: str = "",
    ) -> VisionAnalysisContract:
        self.normalizeExif(imagePath)

        first = self._call(
            imagePath=imagePath,
            modelId=modelId,
            thinkingEnabled=thinkingEnabled,
            ocrHint=ocrHint,
        )

        if first.orientationDegrees:
            self._rotateClockwise(
                imagePath,
                first.orientationDegrees,
            )

            second = self._call(
                imagePath=imagePath,
                modelId=modelId,
                thinkingEnabled=thinkingEnabled,
                ocrHint=ocrHint,
            )
            second.orientationDegrees = first.orientationDegrees
            return second

        return first

    def _call(
        self,
        *,
        imagePath: Path,
        modelId: str,
        thinkingEnabled: bool,
        ocrHint: str,
    ) -> VisionAnalysisContract:
        prompt = self.PROMPT
        if ocrHint.strip():
            prompt += (
                "\n\nOCR preliminar possivelmente fragmentado. Use-o apenas "
                "como pista e reconstrua o texto olhando a imagem:\n"
                + ocrHint[:5000]
            )
        payload = self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=VisionAnalysisContract.model_json_schema(),
            imagePath=imagePath,
            think=thinkingEnabled,
        )

        return VisionAnalysisContract.model_validate(payload)

    def _rotateClockwise(
        self,
        imagePath: Path,
        degrees: int,
    ) -> None:
        with Image.open(imagePath) as image:
            rotated = image.rotate(
                -degrees,
                expand=True,
            )
            rotated.convert("RGB").save(
                imagePath,
                format=self._format(imagePath),
                quality=92,
            )

    def _format(self, imagePath: Path) -> str:
        suffix = imagePath.suffix.lower()

        if suffix in {".jpg", ".jpeg"}:
            return "JPEG"

        return "PNG"
