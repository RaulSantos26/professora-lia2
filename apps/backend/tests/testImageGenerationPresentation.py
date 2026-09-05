from types import SimpleNamespace
from uuid import uuid4

from app.services.imageGenerationService import ImageGenerationService


class _Ownership:
    def assertUnitBelongsToStudent(self, unitId, studentId):
        return (
            SimpleNamespace(title="Recursos naturais"),
            SimpleNamespace(name="Geografia"),
            SimpleNamespace(),
        )


def testImageExplanationUsesSelectedSubjectAndLessonInPortuguese():
    service = ImageGenerationService.__new__(ImageGenerationService)
    service.ownership = _Ownership()

    context = service._learningContext(uuid4(), uuid4())
    labels = service._labels("Ilustre o relevo brasileiro", context)

    assert context == {"subject": "Geografia", "lesson": "Recursos naturais"}
    assert labels == [
        "Matéria: Geografia",
        "Lição: Recursos naturais",
        "Explicação visual: Ilustre o relevo brasileiro",
    ]


def testReliefPromptUsesStudentRequestForConcreteScene():
    service = ImageGenerationService.__new__(ImageGenerationService)
    prompt = service._prompt(
        "Faça uma ilustração sobre os relevos, corte globo na diagonal para melhor visualização",
        "ILLUSTRATION",
        [],
        {"subject": "Geografia", "lesson": "Recursos naturais"},
    )

    assert "Earth globe cut diagonally open" in prompt
    assert "mountains, a plateau, a plain, a valley and a depression" in prompt
    assert "corkboard" in prompt
    assert "not a poster, slide" in prompt


def testVisualFactsDiscardSourceLabelsAndInfographicInstructions():
    service = ImageGenerationService.__new__(ImageGenerationService)

    assert service._visualFact(
        "Uma montanha sob céu azul. Rótulos: Montanha, Planalto"
    ) == "Uma montanha sob céu azul."
    assert service._visualFact(
        "Diagrama em corte transversal com várias formas de relevo."
    ) == ""
