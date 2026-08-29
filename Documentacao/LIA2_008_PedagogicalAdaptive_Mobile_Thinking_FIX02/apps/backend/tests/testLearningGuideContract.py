from app.contracts.learningGuideContract import (
    LearningGuideContract,
    LearningGuideStepContract,
)


def testLearningGuideCanRecommendPedagogicalStudy():
    guide = LearningGuideContract(
        recommendedSection="PEDAGOGICAL",
        headline="Próximo passo: Estudar com a Lia",
        message="Use os materiais para estudar.",
        completedSteps=5,
        totalSteps=10,
        steps=[
            LearningGuideStepContract(
                section="PEDAGOGICAL",
                title="Estudar com a Lia",
                description="Use os materiais para estudar.",
                status="NEXT",
                actionLabel="Abrir Estudar",
            )
        ],
    )

    assert guide.recommendedSection == "PEDAGOGICAL"
    assert guide.steps[0].status == "NEXT"
    assert guide.totalSteps == 10
