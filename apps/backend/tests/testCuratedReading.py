from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import Mock

from app.contracts.ragContract import RagQueryRequestContract
from app.services.materialService import MaterialService
from app.services.ragService import RagService
from app.repositories.ragRepository import RagCandidate


def testDocumentReadingHidesOnlyFullySupersededText():
    blocks = [SimpleNamespace(documentBlockId=uuid4(), blockType=kind)
              for kind in ["TEXT", "TEXT", "TEXT", "IMAGE", "FIGURE", "CAPTION"]]
    service = object.__new__(MaterialService)
    service.documentRepository = SimpleNamespace(listBlocks=lambda page: blocks)
    service.session = SimpleNamespace(execute=lambda statement: [
        (blocks[0].documentBlockId, "SUPERSEDED"),
        (blocks[1].documentBlockId, "SUPERSEDED"), (blocks[1].documentBlockId, "ACTIVE"),
        (blocks[3].documentBlockId, "SUPERSEDED"), (blocks[4].documentBlockId, "ARCHIVED"),
        (blocks[5].documentBlockId, "ARCHIVED"),
    ])
    assert service._visibleDocumentBlocks(uuid4()) == blocks[1:5]


def testRagCuratesBeforeRankingSoHighSimilarityRawOcrDoesNotWin():
    service = object.__new__(RagService)
    material, page = uuid4(), uuid4()
    def candidate(locator, text, vector):
        return RagCandidate(uuid4(), uuid4(), material, "Material", None, None,
            locator, text, vector, "embed", documentPageId=page)
    raw = candidate("OCR local", "RAW_NOISE", [1., 0.])
    reviewed = candidate("Vision/OCR", "Conteúdo revisado e auditado. " * 8, [0.9, 0.1])
    service.repository = SimpleNamespace(listCandidates=lambda **kwargs: [raw, reviewed])
    service.studentRepository = SimpleNamespace(findById=lambda student: object())
    service.ollama = Mock()
    service.ollama.embed.return_value = [[1., 0.]]
    service.ollama.chatStructured.return_value = {"answer": "Resposta", "citations": [1]}
    service.contentGuard = SimpleNamespace(protect=lambda text: SimpleNamespace(content=text))
    service.router = SimpleNamespace(route=lambda *args, **kwargs: SimpleNamespace(effectiveModelId="current"))
    service.thinking = SimpleNamespace(additionalCapabilities=lambda mode: [], resolve=lambda **kwargs: False)
    result = service.query(uuid4(), RagQueryRequestContract(query="Explique o conteúdo", topK=1))
    assert result.evidence[0].evidenceId == reviewed.evidenceId
    assert "RAW_NOISE" not in service.ollama.chatStructured.call_args.kwargs["prompt"]
