from pathlib import Path


def test_material_archive_preserves_pedagogical_artifacts_and_visual_tasks():
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
    assert "deleteByArtifactIds(" not in method
    assert "deleteByIds(" not in method
    assert "deleteByMaterialId(" not in method
    assert "material.status = \"ARCHIVED\"" in method


def test_archive_blocks_active_pedagogical_generation():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    ).read_text(encoding="utf-8")

    assert 'code="PEDAGOGICAL_PROCESSING_ACTIVE"' in source
    assert 'artifact.status in {"QUEUED", "RUNNING"}' in source
