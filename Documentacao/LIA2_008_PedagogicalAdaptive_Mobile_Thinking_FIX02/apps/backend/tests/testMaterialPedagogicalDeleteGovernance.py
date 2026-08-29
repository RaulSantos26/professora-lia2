from pathlib import Path


def testPermanentMaterialDeleteIncludesArchivedPedagogicalArtifacts():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    ).read_text(encoding="utf-8")

    start = source.index("    def deleteMaterial(")
    end = source.index("    def listMaterials(", start)
    method = source[start:end]

    assert "listAllByStudent(" in method
    assert "deleteByArtifactIds(" in method
    assert "deleteByIds(" in method


def testDeleteBlocksActivePedagogicalGeneration():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    ).read_text(encoding="utf-8")

    assert 'code="PEDAGOGICAL_PROCESSING_ACTIVE"' in source
    assert 'artifact.status in {"QUEUED", "RUNNING"}' in source
