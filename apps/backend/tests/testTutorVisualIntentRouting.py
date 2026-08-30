from app.agents.tutorPlannerService import TutorPlannerService


def testExplicitIllustrationAlwaysUsesInternalImageTool():
    result = TutorPlannerService.enforceVisualIntent(
        plan={"intent": "ANSWER", "tools": ["EVIDENCE_SEARCH"]},
        message="Gere uma ilustração dos relevos, do mais profundo à superfície.",
    )

    assert result["tools"] == ["EVIDENCE_SEARCH", "IMAGE_GENERATION"]
    assert result["imageMode"] == "ILLUSTRATION"


def testExplicitMindMapKeepsSvgAndAddsImageCompanion():
    result = TutorPlannerService.enforceVisualIntent(
        plan={"intent": "ANSWER", "tools": ["EVIDENCE_SEARCH"]},
        message="Crie um mapa mental sobre recursos naturais.",
    )

    assert result["intent"] == "MIND_MAP"
    assert result["tools"] == [
        "EVIDENCE_SEARCH",
        "VISUAL_CREATE",
        "IMAGE_GENERATION",
    ]
    assert result["visualType"] == "MIND_MAP"
    assert result["imageMode"] == "MIND_MAP_COMPANION"
