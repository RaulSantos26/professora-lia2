from uuid import uuid4

from app.repositories.ragRepository import RagCandidate
from app.services.evidenceCurationService import EvidenceCurationService


def _candidate(*, locator: str, content: str) -> RagCandidate:
    return RagCandidate(
        documentChunkId=uuid4(),
        evidenceId=uuid4(),
        materialId=uuid4(),
        materialTitle="Página",
        sourceGroupId=uuid4(),
        sourceSequence=1,
        locator=locator,
        content=content,
        embedding=[0.1, 0.2],
        embeddingModelId="nomic-embed-text",
    )


def testCuratorPrefersReviewedVisionTextOverRawOcr():
    materialId = uuid4()
    raw = _candidate(locator="OCR local · texto extraído", content="ruido")
    reviewed = _candidate(locator="Vision/OCR · texto extraído", content="texto revisado " * 20)
    raw.materialId = materialId
    reviewed.materialId = materialId

    curated = EvidenceCurationService().curateCandidates([raw, reviewed])

    assert curated == [reviewed]


def testCuratorRemovesIsolatedOcrNoiseWithoutInventingText():
    text = EvidenceCurationService.cleanText(
        "\n)\n\\ 9 —\nAs paisagens brasileiras\n! mares com biodiversidade.\n"
    )

    assert "As paisagens brasileiras" in text
    assert "biodiversidade" in text
    assert "\\ 9" not in text