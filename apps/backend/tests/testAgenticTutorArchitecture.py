from pathlib import Path


ROOT = Path(__file__).parents[1]


def testAgentHarnessHasExplicitSkillsToolsAndGuardrails():
    harness = (
        ROOT
        / "app"
        / "agents"
        / "tutorAgentHarness.py"
    ).read_text(encoding="utf-8")

    assert "TutorAgentGuardrails" in harness
    assert "TutorSkillRegistry" in harness
    assert "AgentToolExecutor" in harness
    assert "EVIDENCE_SEARCH" in harness
    assert "PROGRESS_READ" in harness
    assert "PEDAGOGICAL_CREATE" in harness
    assert "VISUAL_CREATE" in harness
    assert "IMAGE_GENERATION" in harness


def _migrationFile() -> Path:
    relative = (
        Path("database")
        / "migrations"
        / "versions"
        / "0010_createAgenticTutorVisualFoundation.py"
    )

    candidates = [
        ROOT / relative,
        ROOT.parent.parent / relative,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise AssertionError(
        "Migration 0010 não encontrada nem no layout Docker "
        "(/app/database) nem no layout do repositório."
    )


def testAgentDoesNotPersistReasoningTrace():
    migration = _migrationFile().read_text(
        encoding="utf-8"
    )

    messageModel = (
        ROOT
        / "app"
        / "persistence"
        / "models"
        / "agentMessageModel.py"
    ).read_text(encoding="utf-8")

    assert "thinking_trace" not in migration
    assert "chain_of_thought" not in migration
    assert "thinkingTrace" not in messageModel
    assert "chainOfThought" not in messageModel


def testAgentWorkerCanResumeAfterRestart():
    source = (
        ROOT
        / "app"
        / "services"
        / "agentTutorWorker.py"
    ).read_text(encoding="utf-8")

    assert "requeueRunning" in source
    assert "LIA2_AGENT_TUTOR_WORKER_ENABLED" in source
