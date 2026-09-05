from uuid import uuid4

from app.services.pedagogicalService import PedagogicalService


def testAssessmentPublicContentDoesNotLeakAnswerKey():
    service = PedagogicalService.__new__(PedagogicalService)

    public = service._publicContent(
        "EXERCISES",
        {
            "title": "Teste",
            "questions": [
                {
                    "questionId": "q1",
                    "questionType": "MULTIPLE_CHOICE",
                    "prompt": "Pergunta",
                    "options": ["A", "B"],
                    "correctAnswer": "A",
                    "explanation": "Porque A.",
                    "difficulty": "MEDIUM",
                }
            ],
        },
    )

    question = public["questions"][0]

    assert "correctAnswer" not in question
    assert "explanation" not in question
    assert question["options"] == ["A", "B"]


def testNonAssessmentContentIsPreserved():
    service = PedagogicalService.__new__(PedagogicalService)
    content = {
        "title": "Resumo",
        "keyPoints": ["A", "B"],
    }

    assert service._publicContent("SUMMARY", content) == content


def testEvidencePresentationConsolidatesUploadPagesWithoutDroppingAuditSource():
    service = PedagogicalService.__new__(PedagogicalService)
    student_id = uuid4()
    group_id = uuid4()
    first_material_id = uuid4()
    second_material_id = uuid4()

    class Material:
        def __init__(self, material_id):
            self.materialId = material_id
            self.sourceGroupId = group_id

    evidence = service._consolidateEvidenceForPresentation(
        [
            {
                "evidenceId": str(uuid4()),
                "materialId": str(first_material_id),
                "materialTitle": "WhatsApp Image page 1",
                "locator": "Vision/OCR · página 1",
                "excerpt": "Texto revisado da página 1.",
            },
            {
                "evidenceId": str(uuid4()),
                "materialId": str(second_material_id),
                "materialTitle": "WhatsApp Image page 2",
                "locator": "Vision/OCR · página 2",
                "excerpt": "Texto revisado da página 2.",
            },
        ],
        materials=[Material(first_material_id), Material(second_material_id)],
        studentId=student_id,
    )

    assert len(evidence) == 1
    assert evidence[0].materialTitle == "Material consolidado · 2 páginas"
    assert evidence[0].locator == "Texto estruturado e auditado"
    assert "página 1" in evidence[0].excerpt
    assert "página 2" in evidence[0].excerpt