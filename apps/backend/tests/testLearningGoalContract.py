from app.contracts.learningGoalContract import LearningGoalCreateContract

def testLearningGoalNormalizesTitle():
    contract = LearningGoalCreateContract(
        goalType="TEST",
        title="  Prova   de História  ",
        priority=4,
    )
    assert contract.title == "Prova de História"
    assert contract.priority == 4
