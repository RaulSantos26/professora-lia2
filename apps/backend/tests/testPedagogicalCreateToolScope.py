from types import SimpleNamespace
from uuid import uuid4

from app.tools.pedagogicalCreateTool import PedagogicalCreateTool


def testPedagogicalCreateToolPropagatesRequiredStudyScope():
    student_id = uuid4()
    context_id = uuid4()
    subject_id = uuid4()
    unit_id = uuid4()
    material_id = uuid4()
    captured = {}

    class FakeService:
        def createArtifact(self, *, studentId, request):
            captured["studentId"] = studentId
            captured["request"] = request
            return SimpleNamespace(
                pedagogicalArtifactId=uuid4(),
                artifactType="EXPLAIN",
                status="QUEUED",
                title="Explicação da Lia",
            )

    tool = PedagogicalCreateTool.__new__(PedagogicalCreateTool)
    tool.service = FakeService()

    tool.execute(
        studentId=student_id,
        artifactType="EXPLAIN",
        instruction="O que é erosão?",
        materialIds=[material_id],
        studentLearningContextId=context_id,
        studentSubjectId=subject_id,
        studentLearningUnitId=unit_id,
        requestedTextModelId=None,
        thinkingMode="AUTO",
    )

    request = captured["request"]
    assert captured["studentId"] == student_id
    assert request.studentLearningContextId == context_id
    assert request.studentSubjectId == subject_id
    assert request.studentLearningUnitId == unit_id
    assert request.materialIds == [material_id]