class TutorSkillRegistry:
    INTENT_TO_SKILL = {
        "GREETING": "conversationSkill",
        "ANSWER": "groundedAnswerSkill",
        "TEACH": "pedagogicalSkill",
        "EXPLAIN": "pedagogicalSkill",
        "SUMMARY": "pedagogicalSkill",
        "FLASHCARDS": "pedagogicalSkill",
        "EXERCISES": "pedagogicalSkill",
        "QUIZ": "pedagogicalSkill",
        "MIND_MAP": "visualLearningSkill",
        "DIAGRAM": "visualLearningSkill",
        "CHART": "visualLearningSkill",
        "ANIMATION_2D": "visualLearningSkill",
        "SCENE_3D": "visualLearningSkill",
        "PROGRESS": "progressSkill",
    }

    def resolve(self, intent: str) -> str:
        return self.INTENT_TO_SKILL.get(
            intent,
            "groundedAnswerSkill",
        )
