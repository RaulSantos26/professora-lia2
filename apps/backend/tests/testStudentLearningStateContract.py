from app.contracts.studentLearningStateContract import StudentLearningStateUpdateContract

def testLearningStateAcceptsValidLevels():
    contract = StudentLearningStateUpdateContract(
        status="LEARNING",
        masteryLevel=70,
        confidenceLevel=60,
    )
    assert contract.masteryLevel == 70
    assert contract.confidenceLevel == 60
