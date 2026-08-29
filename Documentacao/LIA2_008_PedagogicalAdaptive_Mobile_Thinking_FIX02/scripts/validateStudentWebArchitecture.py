from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
STUDENT_WEB = ROOT / "apps" / "studentWeb"


def read(relative: str) -> str:
    path = STUDENT_WEB / relative

    if not path.exists():
        raise AssertionError(
            f"Arquivo do Student Web não encontrado: {path}"
        )

    return path.read_text(encoding="utf-8")


def validateMobileMaterialCapture() -> None:
    source = read(
        "src/components/materialUploadCard.vue"
    )

    required = [
        "Tirar foto",
        "Escolher foto ou arquivo",
        'capture="environment"',
        "Refazer foto",
        "multiple",
        "Enviar e analisar",
        "selectedUploads.value.map",
        "moveFile(",
    ]

    for token in required:
        assert token in source, (
            "Arquitetura mobile de upload perdeu "
            f"o requisito: {token}"
        )


def validateMobileNavigation() -> None:
    source = read(
        "src/components/mobileStudentNavigation.vue"
    )

    for token in [
        "Início",
        "Materiais",
        "Estudar",
        "Progresso",
    ]:
        assert token in source, (
            "Navegação mobile perdeu "
            f"o item obrigatório: {token}"
        )

    assert "label: 'Lia'" not in source, (
        "O Tutor Lia ainda não pertence ao 008."
    )


def validateThinkingUi() -> None:
    material = read(
        "src/components/materialUploadCard.vue"
    )
    pedagogical = read(
        "src/components/pedagogicalWorkspacePanel.vue"
    )
    rag = read(
        "src/components/materialWorkspacePanel.vue"
    )

    assert "Raciocínio / Thinking" in material
    assert "Raciocínio / Thinking" in pedagogical
    assert "Raciocínio: Automático" in rag
    assert "Thinking:" in rag


def validateTestBoundary() -> None:
    backendTests = ROOT / "apps" / "backend" / "tests"

    forbidden = []

    for path in backendTests.glob("test*.py"):
        source = path.read_text(encoding="utf-8")

        if (
            "studentWeb" in source
            or "materialUploadCard.vue" in source
            or "mobileStudentNavigation.vue" in source
        ):
            forbidden.append(path.name)

    assert not forbidden, (
        "Testes do backend não podem depender de arquivos do "
        "Student Web. Mova essas validações para o nível do "
        f"repositório. Arquivos: {', '.join(forbidden)}"
    )


def main() -> int:
    try:
        validateMobileMaterialCapture()
        validateMobileNavigation()
        validateThinkingUi()
        validateTestBoundary()
    except AssertionError as error:
        print(
            "[LIA2][STUDENT-WEB-ARCH] FAIL:",
            error,
            file=sys.stderr,
        )
        return 1

    print(
        "[LIA2][STUDENT-WEB-ARCH] PASS "
        "mobile + camera + Thinking UI + test boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
