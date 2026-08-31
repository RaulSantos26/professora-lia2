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
    assert labels[:3] == [
        "Matéria: Geografia",
        "Lição: Recursos naturais",
        "Explicação visual: Ilustre o relevo brasileiro",
    ]
    assert "Montanhas|Grandes elevações do terreno" in labels
    assert "Depressões|Áreas mais baixas que o entorno" in labels


def testVisualFactsDiscardSourceLabelsAndInfographicInstructions():
    service = ImageGenerationService.__new__(ImageGenerationService)

    assert service._visualFact(
        "Uma montanha sob céu azul. Rótulos: Montanha, Planalto"
    ) == "Uma montanha sob céu azul."
    assert service._visualFact(
        "Diagrama em corte transversal com várias formas de relevo."
    ) == ""
