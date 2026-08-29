from pathlib import Path


def testMaterialDeleteCommitsDatabaseBeforeRemovingPhysicalTree():
    sourcePath = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    )
    source = sourcePath.read_text(encoding="utf-8")

    start = source.index("    def deleteMaterial(")
    end = source.index("    def listMaterials(", start)
    method = source[start:end]

    assert "self.documentRepository.deleteByMaterialId(materialId)" in method
    assert "self.jobRepository.deleteByMaterialId(" in method
    assert "self.repository.deleteFilesByMaterialId(" in method
    assert "self.repository.deleteMaterialById(" in method
    assert "self.session.commit()" in method
    assert "self.storageService.removeMaterialTree(" in method

    assert method.index("self.session.commit()") < method.index(
        "self.storageService.removeMaterialTree("
    )


def testMaterialDeleteRollsBackIntegrityErrors():
    sourcePath = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    )
    source = sourcePath.read_text(encoding="utf-8")

    assert "except IntegrityError as error:" in source
    assert 'code="MATERIAL_DELETE_CONSTRAINT_ERROR"' in source
    assert "self.session.rollback()" in source


def testMaterialDeleteBlocksActiveProcessing():
    sourcePath = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialService.py"
    )
    source = sourcePath.read_text(encoding="utf-8")

    assert 'code="MATERIAL_PROCESSING_ACTIVE"' in source
