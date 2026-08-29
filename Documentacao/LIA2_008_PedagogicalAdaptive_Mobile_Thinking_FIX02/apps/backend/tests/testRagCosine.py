from app.services.ragService import RagService


def testCosineRanksIdenticalVectorsAtOne():
    service = RagService.__new__(RagService)

    score = service._cosine(
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
    )

    assert round(score, 6) == 1.0


def testCosineRejectsDifferentDimensions():
    service = RagService.__new__(RagService)

    assert service._cosine(
        [1.0, 0.0],
        [1.0],
    ) == -1.0
