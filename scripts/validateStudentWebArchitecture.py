from html.parser import HTMLParser
from pathlib import Path
import re
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
        "Lia",
        "Progresso",
    ]:
        assert token in source, (
            "Navegação mobile perdeu "
            f"o item obrigatório: {token}"
        )

    assert "section: 'LIA_TUTOR'" in source, (
        "O 009 exige navegação própria para o Tutor Lia."
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



def validateAgenticTutorAndVisualEngine() -> None:
    tutor = read(
        "src/components/liaTutorPanel.vue"
    )
    renderer = read(
        "src/components/visualTaskRenderer.vue"
    )
    mindMap = read(
        "src/components/interactiveMindMapRenderer.vue"
    )
    animation = read(
        "src/components/animationCanvasRenderer.vue"
    )
    scene3d = read(
        "src/components/threeSceneRenderer.vue"
    )
    package = read("package.json")

    for token in [
        "AGENTIC TUTOR",
        "Pergunte à Lia",
        "visualTasks",
        "Thinking",
    ]:
        assert token in tutor, (
            "Tutor Lia perdeu requisito: "
            f"{token}"
        )

    for token in [
        "MIND_MAP",
        "DIAGRAM",
        "CHART",
        "ANIMATION_2D",
        "SCENE_3D",
    ]:
        assert token in renderer, (
            "VisualTaskRenderer perdeu renderer: "
            f"{token}"
        )

    assert "<svg" in mindMap
    assert "<canvas" in animation
    assert "from 'three'" in scene3d
    assert '"three": "0.185.1"' in package


def validateInteractivePedagogicalMindMap() -> None:
    source = read(
        "src/components/pedagogicalArtifactRenderer.vue"
    )

    assert "InteractiveMindMapRenderer" in source, (
        "Mapa mental do módulo Estudar deve usar "
        "o renderer SVG interativo."
    )



class VueTemplateNode:
    def __init__(self, tag: str, attrs: dict[str, str | None]):
        self.tag = tag
        self.attrs = attrs
        self.children: list["VueTemplateNode"] = []


class VueTemplateParser(HTMLParser):
    VOID = {
        "area", "base", "br", "col", "embed",
        "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = VueTemplateNode("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = VueTemplateNode(
            tag,
            dict(attrs),
        )
        self.stack[-1].children.append(node)

        if tag.lower() not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = VueTemplateNode(
            tag,
            dict(attrs),
        )
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        for index in range(
            len(self.stack) - 1,
            0,
            -1,
        ):
            if self.stack[index].tag.lower() == tag.lower():
                del self.stack[index:]
                return


def validateVueDirectiveSafety() -> None:
    errors = []

    for path in STUDENT_WEB.rglob("*.vue"):
        source = path.read_text(encoding="utf-8")
        templateStart = source.find("<template>")
        templateEnd = source.rfind("</template>")

        if templateStart < 0 or templateEnd < 0:
            continue

        parser = VueTemplateParser()
        parser.feed(
            source[
                templateStart
                + len("<template>"):
                templateEnd
            ]
        )

        def inspect(node: VueTemplateNode):
            previous = None

            for child in node.children:
                attrs = child.attrs

                if (
                    "v-for" in attrs
                    and (
                        "v-if" in attrs
                        or "v-else-if" in attrs
                    )
                ):
                    errors.append(
                        f"{path.name}: não combine "
                        "v-for e v-if/v-else-if no mesmo elemento."
                    )

                if (
                    "v-else" in attrs
                    or "v-else-if" in attrs
                ):
                    if (
                        previous is None
                        or (
                            "v-if" not in previous.attrs
                            and "v-else-if" not in previous.attrs
                        )
                    ):
                        errors.append(
                            f"{path.name}: "
                            f"{child.tag} com v-else/v-else-if "
                            "não está imediatamente ligado "
                            "a um irmão v-if/v-else-if."
                        )

                inspect(child)
                previous = child

        inspect(parser.root)

    assert not errors, (
        "Template Vue possui diretivas inseguras: "
        + " | ".join(errors)
    )



def validateBackendDockerPathBoundary() -> None:
    backendTests = ROOT / "apps" / "backend" / "tests"
    forbidden = []

    for path in backendTests.glob("test*.py"):
        source = path.read_text(encoding="utf-8")

        # In the backend image, tests live in /app/tests and ROOT commonly
        # resolves to /app. Escaping ROOT with ROOT.parents[...] therefore
        # depends on repository depth and can break only inside Docker.
        if re.search(
            r"\bROOT\.parents\s*\[",
            source,
        ):
            forbidden.append(path.name)

    assert not forbidden, (
        "Testes do backend não podem depender da profundidade "
        "do diretório acima de /app. Use caminhos que funcionem "
        "tanto no repositório quanto no layout Docker. Arquivos: "
        + ", ".join(forbidden)
    )


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
        validateAgenticTutorAndVisualEngine()
        validateInteractivePedagogicalMindMap()
        validateVueDirectiveSafety()
        validateBackendDockerPathBoundary()
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
        "mobile + camera + Thinking + Agentic Tutor + Visual Engine + test boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
