from pathlib import Path


def testAgentToolsUseEvidenceMaterialScopeWhenNoManualSelection():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "agents"
        / "tutorAgentHarness.py"
    ).read_text(encoding="utf-8")

    assert "actionMaterialIds = list(materialIds)" in source
    assert "UUID(hit[\"materialId\"])" in source
    assert "materialIds=actionMaterialIds" in source
    assert '"materialIds": actionMaterialIds' in source


def testEvidenceSearchRemainsFilteredByThreadContext():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "agents"
        / "tutorAgentHarness.py"
    ).read_text(encoding="utf-8")

    assert "thread.studentLearningContextId" in source
    assert "thread.studentSubjectId" in source
    assert "thread.studentLearningUnitId" in source
