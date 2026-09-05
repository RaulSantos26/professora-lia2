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


def testMindMapNormalizationConnectsOrphanNodesToRoot():
    service = PedagogicalGenerationService()

    normalized = service._normalizeMindMap(
        {
            "title": "Tema",
            "rootId": "1",
            "nodes": [
                {"nodeId": "1", "parentId": None, "label": "Tema"},
                {"nodeId": "2", "parentId": None, "label": "Ramo"},
                {"nodeId": "3", "parentId": None, "label": "Outro ramo"},
            ],
        }
    )

    parents = {
        node["nodeId"]: node["parentId"]
        for node in normalized["nodes"]
    }
    assert parents == {"1": None, "2": "1", "3": "1"}


def testEvidenceCleanupRemovesStandaloneOcrNoiseWithoutChangingWords():
    from app.services.pedagogicalContextService import PedagogicalContextService

    cleaned = PedagogicalContextService._cleanEvidenceExcerpt(
        "\n)\n\\ 9 —\nAs paisagens brasileiras\n! mares, onde se esconde grande biodiversidade.\n"
    )

    assert "As paisagens brasileiras" in cleaned
    assert "biodiversidade" in cleaned
    assert "\\ 9" not in cleaned