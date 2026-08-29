import re
from dataclasses import dataclass
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps


@dataclass
class OcrAnalysisResult:
    orientationDegrees: int
    text: str


class OcrAnalysisService:
    """
    Local OCR layer.

    It is intentionally independent from the LLM/Vision provider so scanned
    pages can still yield searchable text even when no Vision model is
    installed. Vision remains responsible for semantic interpretation of
    diagrams, figures and other non-text visual content.
    """

    def analyzeAndNormalize(
        self,
        imagePath: Path,
    ) -> OcrAnalysisResult:
        orientation = self._detectOrientation(imagePath)

        if orientation:
            self._rotateClockwise(
                imagePath,
                orientation,
            )

        with Image.open(imagePath) as image:
            prepared = ImageOps.grayscale(image)
            prepared = ImageOps.autocontrast(prepared)

            if prepared.width < 1800:
                scale = 1.5
                prepared = prepared.resize(
                    (
                        int(prepared.width * scale),
                        int(prepared.height * scale),
                    ),
                    Image.Resampling.LANCZOS,
                )

            text = pytesseract.image_to_string(
                prepared,
                lang="por+eng",
                config="--oem 3 --psm 6",
            ).strip()

        return OcrAnalysisResult(
            orientationDegrees=orientation,
            text=text,
        )

    def _detectOrientation(
        self,
        imagePath: Path,
    ) -> int:
        try:
            with Image.open(imagePath) as image:
                output = pytesseract.image_to_osd(
                    image,
                    config="--psm 0",
                )

            match = re.search(
                r"Rotate:\s*(0|90|180|270)",
                output,
            )

            if not match:
                return 0

            return int(match.group(1))

        except Exception:
            # Orientation detection can fail on pages with too little text.
            # OCR and Vision can still proceed.
            return 0

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
                format="PNG",
                optimize=True,
            )
