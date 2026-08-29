from pathlib import Path


def testThreadCreationValidatesStudentOwnershipOfContextSubjectAndUnit():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "agentTutorService.py"
    ).read_text(encoding="utf-8")

    assert "_validateContextOwnership(" in source
    assert 'code="AGENT_CONTEXT_NOT_OWNED"' in source
    assert 'code="AGENT_SUBJECT_NOT_OWNED"' in source
    assert 'code="AGENT_UNIT_NOT_OWNED"' in source
    assert 'code="AGENT_CONTEXT_MISMATCH"' in source
    assert 'code="AGENT_SUBJECT_MISMATCH"' in source


def testMessageMaterialScopeIsValidatedAgainstStudent():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "agentTutorService.py"
    ).read_text(encoding="utf-8")

    assert "_validateMaterials(" in source
    assert 'code="AGENT_MATERIAL_NOT_OWNED"' in source
