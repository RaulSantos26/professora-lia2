import re
from dataclasses import dataclass
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps


@dataclass
class OcrAnalysisResult:
    orientationDegrees: int
    text: str
    confidence: float = 0.0
    wordCount: int = 0


class OcrAnalysisService:
    """Compare local OCR before normalizing; OSD is a candidate, never authority."""

    def analyzeAndNormalize(self, imagePath: Path) -> OcrAnalysisResult:
        suggested = self._detectOrientation(imagePath)
        with Image.open(imagePath) as opened:
            image = opened.convert('RGB')
        # All candidates are in memory; only the proven winner changes the source.
        baseline = self._read(image)
        candidates = {0: baseline}
        if suggested:
            candidates[suggested] = self._read(image.rotate(-suggested, expand=True))
        if max(value[1] for value in candidates.values()) < 75 or max(value[2] for value in candidates.values()) < 6:
            for angle in (90, 180, 270):
                if angle not in candidates:
                    candidates[angle] = self._read(image.rotate(-angle, expand=True))
        orientation = 0
        # At least eight confidence points and substantial text are required.
        for angle, value in candidates.items():
            if angle and value[2] >= max(3, baseline[2] * .6) and value[1] >= baseline[1] + 8:
                if value[1] > candidates[orientation][1]:
                    orientation = angle
        if orientation:
            self._rotateClockwise(imagePath, orientation)
        selected = candidates[orientation]
        return OcrAnalysisResult(orientationDegrees=orientation, text=selected[0], confidence=selected[1], wordCount=selected[2])

    def _read(self, image):
        prepared = ImageOps.autocontrast(ImageOps.grayscale(image))
        if prepared.width < 1800:
            prepared = prepared.resize((int(prepared.width * 1.5), int(prepared.height * 1.5)), Image.Resampling.LANCZOS)
        data = pytesseract.image_to_data(prepared, lang='por+eng', config='--oem 3 --psm 6', output_type=pytesseract.Output.DICT)
        lines = []; words = []; previous = None; weighted = 0.0; weight = 0; count = 0
        for index, raw in enumerate(data.get('text', [])):
            word = str(raw).strip()
            if not word:
                continue
            key = tuple(data.get(name, [0] * len(data['text']))[index] for name in ('block_num', 'par_num', 'line_num'))
            if previous is not None and key != previous:
                lines.append(' '.join(words)); words = []
                if key[:2] != previous[:2]:
                    lines.append('')
            previous = key; words.append(word)
            try:
                confidence = float(data['conf'][index])
            except (KeyError, IndexError, TypeError, ValueError):
                continue
            if 0 <= confidence <= 100 and any(c.isalnum() for c in word):
                length = min(len(word), 12)
                weighted += confidence * length; weight += length; count += 1
        if words:
            lines.append(' '.join(words))
        return '\n'.join(lines).strip(), weighted / weight if weight else 0.0, count

    def _detectOrientation(self, imagePath: Path) -> int:
        try:
            with Image.open(imagePath) as image:
                output = pytesseract.image_to_osd(image, config='--psm 0')
            match = re.search(r'Rotate:\s*(0|90|180|270)\b', output)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0

    def _rotateClockwise(self, imagePath: Path, degrees: int) -> None:
        with Image.open(imagePath) as image:
            image.rotate(-degrees, expand=True).convert('RGB').save(imagePath, format='PNG', optimize=True)
