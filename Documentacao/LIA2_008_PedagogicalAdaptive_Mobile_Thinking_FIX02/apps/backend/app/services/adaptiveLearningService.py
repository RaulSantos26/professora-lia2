from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.persistence.models.studentLearningStateModel import StudentLearningStateModel
from app.repositories.materialRepository import MaterialRepository
from app.repositories.studentLearningStateRepository import StudentLearningStateRepository


class AdaptiveLearningService:
    def __init__(self, session: Session):
        self.session = session
        self.materialRepository = MaterialRepository(session)
        self.stateRepository = StudentLearningStateRepository(session)

    def resolveDifficulty(
        self,
        *,
        studentId: UUID,
        materialIds: list[UUID],
        requestedDifficulty: str,
    ) -> str:
        if requestedDifficulty != "AUTO":
            return requestedDifficulty

        unitIds = self._unitIds(studentId, materialIds)

        if not unitIds:
            return "MEDIUM"

        values = []

        for unitId in unitIds:
            state = self.stateRepository.findByUnitId(unitId)
            values.append(state.masteryLevel if state else 0)

        average = sum(values) / max(len(values), 1)

        if average < 35:
            return "EASY"

        if average < 72:
            return "MEDIUM"

        return "HARD"

    def applyAttempt(
        self,
        *,
        studentId: UUID,
        materialIds: list[UUID],
        scorePercent: int,
    ) -> tuple[list[UUID], str]:
        unitIds = self._unitIds(studentId, materialIds)

        if not unitIds:
            return [], (
                "Resultado salvo. Vincule o material a uma unidade "
                "para atualizar domínio e revisão automaticamente."
            )

        now = datetime.now(timezone.utc)

        if scorePercent >= 85:
            masteryDelta = 12
            confidenceDelta = 8
            reviewDays = 7
        elif scorePercent >= 70:
            masteryDelta = 7
            confidenceDelta = 4
            reviewDays = 4
        elif scorePercent >= 50:
            masteryDelta = 3
            confidenceDelta = 0
            reviewDays = 2
        else:
            masteryDelta = -4
            confidenceDelta = -5
            reviewDays = 1

        for unitId in unitIds:
            state = self.stateRepository.findByUnitId(unitId)

            if state is None:
                state = StudentLearningStateModel(
                    studentId=studentId,
                    studentLearningUnitId=unitId,
                    status="LEARNING",
                    masteryLevel=0,
                    confidenceLevel=0,
                    studyCount=0,
                )
                self.stateRepository.create(state)

            state.masteryLevel = max(
                0,
                min(100, state.masteryLevel + masteryDelta),
            )
            state.confidenceLevel = max(
                0,
                min(100, state.confidenceLevel + confidenceDelta),
            )
            state.studyCount += 1
            state.lastStudiedAt = now
            state.nextReviewAt = now + timedelta(days=reviewDays)

            if state.masteryLevel >= 85:
                state.status = "MASTERED"
            elif scorePercent < 50:
                state.status = "REVIEWING"
            else:
                state.status = "LEARNING"

        if scorePercent >= 85:
            message = (
                "Ótimo desempenho. A próxima revisão pode ser mais espaçada."
            )
        elif scorePercent >= 70:
            message = (
                "Bom desempenho. A Lia aumentou gradualmente o domínio."
            )
        elif scorePercent >= 50:
            message = (
                "Você está avançando. Uma nova revisão foi agendada em breve."
            )
        else:
            message = (
                "A Lia identificou dificuldade e antecipou a próxima revisão."
            )

        return unitIds, message

    def _unitIds(
        self,
        studentId: UUID,
        materialIds: list[UUID],
    ) -> list[UUID]:
        materials = self.materialRepository.listByStudentId(studentId)
        selected = [
            item
            for item in materials
            if (
                not materialIds
                or item.materialId in materialIds
            )
            and item.studentLearningUnitId is not None
        ]

        return list(
            dict.fromkeys(
                item.studentLearningUnitId
                for item in selected
                if item.studentLearningUnitId is not None
            )
        )
