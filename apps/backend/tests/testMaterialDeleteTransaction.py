from pathlib import Path


def _delete_method() -> str:
    source_path = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    )
    source = source_path.read_text(encoding="utf-8")
    start = source.index("    def deleteMaterial(")
    end = source.index("    def listMaterials(", start)
    return source[start:end]


def test_material_delete_archives_without_removing_learning_artifacts():
    method = _delete_method()

    assert 'material.status = "ARCHIVED"' in method
    assert "material.studyEnabled = False" in method
    assert "self.session.commit()" in method
    assert "deleteByMaterialId(" not in method
    assert "deleteByIds(" not in method
    assert "deleteMaterialById(" not in method
    assert "removeMaterialTree(" not in method


def test_material_archive_rolls_back_integrity_errors():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    ).read_text(encoding="utf-8")

    assert "except IntegrityError as error:" in source
    assert 'code="MATERIAL_ARCHIVE_CONSTRAINT_ERROR"' in source
    assert "self.session.rollback()" in source


def test_material_archive_blocks_active_processing():
    assert 'code="MATERIAL_PROCESSING_ACTIVE"' in _delete_method()
