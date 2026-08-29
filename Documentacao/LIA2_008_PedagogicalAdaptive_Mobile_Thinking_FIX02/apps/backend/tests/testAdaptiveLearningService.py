from datetime import datetime
from uuid import uuid4

from app.persistence.models.studentLearningStateModel import (
    StudentLearningStateModel,
)
from app.services.adaptiveLearningService import AdaptiveLearningService


class FakeStateRepository:
    def __init__(self):
        self.states = {}

    def findByUnitId(self, unitId):
        return self.states.get(unitId)

    def create(self, model):
        self.states[model.studentLearningUnitId] = model
        return model


def serviceWithUnit(unitId):
    service = AdaptiveLearningService.__new__(
        AdaptiveLearningService
    )
    service.stateRepository = FakeStateRepository()
    service._unitIds = lambda studentId, materialIds: [unitId]
    return service


def testAdaptiveDifficultyUsesMastery():
    studentId = uuid4()
    unitId = uuid4()
    service = serviceWithUnit(unitId)

    state = StudentLearningStateModel(
        studentId=studentId,
        studentLearningUnitId=unitId,
        status="LEARNING",
        masteryLevel=80,
        confidenceLevel=70,
        studyCount=2,
    )
    service.stateRepository.states[unitId] = state

    assert service.resolveDifficulty(
        studentId=studentId,
        materialIds=[],
        requestedDifficulty="AUTO",
    ) == "HARD"


def testLowScoreSchedulesEarlyReviewAndReducesMastery():
    studentId = uuid4()
    unitId = uuid4()
    service = serviceWithUnit(unitId)

    state = StudentLearningStateModel(
        studentId=studentId,
        studentLearningUnitId=unitId,
        status="LEARNING",
        masteryLevel=40,
        confidenceLevel=40,
        studyCount=1,
    )
    service.stateRepository.states[unitId] = state

    updated, message = service.applyAttempt(
        studentId=studentId,
        materialIds=[],
        scorePercent=30,
    )

    assert updated == [unitId]
    assert state.masteryLevel == 36
    assert state.confidenceLevel == 35
    assert state.status == "REVIEWING"
    assert state.studyCount == 2
    assert state.nextReviewAt is not None
    assert "dificuldade" in message.lower()


def testHighScoreCanReachMastered():
    studentId = uuid4()
    unitId = uuid4()
    service = serviceWithUnit(unitId)

    state = StudentLearningStateModel(
        studentId=studentId,
        studentLearningUnitId=unitId,
        status="LEARNING",
        masteryLevel=80,
        confidenceLevel=70,
        studyCount=2,
    )
    service.stateRepository.states[unitId] = state

    service.applyAttempt(
        studentId=studentId,
        materialIds=[],
        scorePercent=100,
    )

    assert state.masteryLevel == 92
    assert state.status == "MASTERED"
