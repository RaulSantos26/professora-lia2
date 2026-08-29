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
