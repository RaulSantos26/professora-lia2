from app.contracts.learningGuideContract import (
    LearningGuideContract,
    LearningGuideStepContract,
)


def testLearningGuideCanRecommendRealTutor():
    guide = LearningGuideContract(
        recommendedSection="LIA_TUTOR",
        headline="Próximo passo: Conversar com a Lia",
        message="Converse com a tutora.",
        completedSteps=6,
        totalSteps=11,
        steps=[
            LearningGuideStepContract(
                section="LIA_TUTOR",
                title="Conversar com a Lia",
                description="Converse com a tutora.",
                status="NEXT",
                actionLabel="Abrir Lia",
            )
        ],
    )

    assert guide.recommendedSection == "LIA_TUTOR"
    assert guide.steps[0].status == "NEXT"
    assert guide.totalSteps == 11
