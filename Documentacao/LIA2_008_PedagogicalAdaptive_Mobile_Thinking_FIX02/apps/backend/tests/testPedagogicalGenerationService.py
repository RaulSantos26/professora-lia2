from app.services.pedagogicalGenerationService import (
    PedagogicalGenerationService,
)


def testPedagogicalPromptRequiresBrazilianPortugueseAndEvidenceOnly():
    service = PedagogicalGenerationService()

    prompt = service._prompt(
        artifactType="SUMMARY",
        context="[1] conteúdo do material",
        instruction=None,
        difficulty="MEDIUM",
        questionCount=8,
    )

    assert "português brasileiro" in prompt
    assert "SOMENTE as evidências" in prompt
    assert "Não complete lacunas" in prompt


def testAssessmentSchemaUsesExactQuestionCountAndObjectiveAnswers():
    service = PedagogicalGenerationService()

    schema = service._schema(
        "QUIZ",
        10,
    )

    questions = schema["properties"]["questions"]

    assert questions["minItems"] == 10
    assert questions["maxItems"] == 10
    assert "correctAnswer" in questions["items"]["required"]
    assert questions["items"]["properties"]["questionType"]["enum"] == [
        "MULTIPLE_CHOICE",
        "TRUE_FALSE",
    ]


def testMindMapSchemaIsStructured():
    service = PedagogicalGenerationService()

    schema = service._schema(
        "MIND_MAP",
        8,
    )

    assert "rootId" in schema["required"]
    assert "nodes" in schema["required"]
