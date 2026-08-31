from pathlib import Path
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
