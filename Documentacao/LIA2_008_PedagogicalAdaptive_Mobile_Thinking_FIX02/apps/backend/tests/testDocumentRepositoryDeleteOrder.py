from pathlib import Path


def testDocumentRepositoryUsesExplicitVersionDeleteBeforeDocumentDelete():
    sourcePath = (
        Path(__file__).parents[1]
        / "app"
        / "repositories"
        / "documentRepository.py"
    )
    source = sourcePath.read_text(encoding="utf-8")

    versionDelete = (
        "delete(DocumentVersionModel).where("
    )
    documentDelete = (
        "delete(DocumentModel).where("
    )

    assert versionDelete in source
    assert documentDelete in source
    assert source.index(versionDelete) < source.index(documentDelete)

    # Regression: ORM deletes were the cause of PostgreSQL RESTRICT failure.
    deleteMethodSource = source[
        source.index("    def deleteByMaterialId("):
    ]

    assert "self.session.delete(version)" not in deleteMethodSource
    assert "self.session.delete(document)" not in deleteMethodSource
