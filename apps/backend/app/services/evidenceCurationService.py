import re


class EvidenceCurationService:
    """Produces safe reading text while retaining raw audit records unchanged."""

    def curateCandidates(self, candidates: list) -> list:
        # A Vision transcription is a reviewed replacement for noisy local OCR
        # from the same photographed page. Retain the raw OCR in storage/audit,
        # but do not feed it to the student-facing pedagogical context.
        reviewedMaterialIds = {
            item.materialId
            for item in candidates
            if item.locator.startswith("Vision/OCR")
            and len(item.content.strip()) >= 80
        }
        return [
            item
            for item in candidates
            if not (
                item.materialId in reviewedMaterialIds
                and item.locator.startswith("OCR local")
            )
        ]

    @staticmethod
    def cleanText(text: str) -> str:
        """Remove isolated OCR noise without silently inventing corrections."""
        cleanedLines = []
        for rawLine in text.replace("\r", "\n").splitlines():
            line = re.sub(r"\s+", " ", rawLine).strip(" \t|•*·")
            alphanumeric = len(re.findall(r"[A-Za-zÀ-ÿ0-9]", line))
            letters = len(re.findall(r"[A-Za-zÀ-ÿ]", line))
            if not line or (letters < 4 and alphanumeric < 5):
                continue
            if alphanumeric / max(len(line), 1) < 0.38:
                continue
            cleanedLines.append(line)

        cleaned = "\n".join(cleanedLines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned or text.strip()