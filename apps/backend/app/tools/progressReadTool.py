from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.studentLearningStateModel import StudentLearningStateModel
from app.persistence.models.studentLearningUnitModel import StudentLearningUnitModel
from app.persistence.models.studentSubjectModel import StudentSubjectModel


class ProgressReadTool:
    toolName = "PROGRESS_READ"

    def __init__(self, session: Session):
        self.session = session

    def execute(
        self,
        *,
        studentId: UUID,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
    ) -> dict:
        statement = (
            select(
                StudentLearningStateModel.status,
                StudentLearningStateModel.masteryLevel,
                StudentLearningStateModel.confidenceLevel,
                StudentLearningStateModel.studyCount,
                StudentLearningStateModel.lastStudiedAt,
                StudentLearningStateModel.nextReviewAt,
                StudentLearningUnitModel.studentLearningUnitId,
                StudentLearningUnitModel.title,
                StudentSubjectModel.studentSubjectId,
                StudentSubjectModel.name,
            )
            .join(
                StudentLearningUnitModel,
                StudentLearningUnitModel.studentLearningUnitId
                == StudentLearningStateModel.studentLearningUnitId,
            )
            .join(
                StudentSubjectModel,
                StudentSubjectModel.studentSubjectId
                == StudentLearningUnitModel.studentSubjectId,
            )
            .where(
                StudentLearningStateModel.studentId
                == studentId
            )
        )

        if studentSubjectId is not None:
            statement = statement.where(
                StudentSubjectModel.studentSubjectId
                == studentSubjectId
            )

        if studentLearningUnitId is not None:
            statement = statement.where(
                StudentLearningUnitModel.studentLearningUnitId
                == studentLearningUnitId
            )

        rows = self.session.execute(statement).all()

        units = []

        for row in rows:
            units.append(
                {
                    "unitId": str(
                        row.studentLearningUnitId
                    ),
                    "unitTitle": row.title,
                    "subjectId": str(
                        row.studentSubjectId
                    ),
                    "subjectName": row.name,
                    "status": row.status,
                    "masteryLevel": row.masteryLevel,
                    "confidenceLevel": (
                        row.confidenceLevel
                    ),
                    "studyCount": row.studyCount,
                    "lastStudiedAt": (
                        row.lastStudiedAt.isoformat()
                        if row.lastStudiedAt
                        else None
                    ),
                    "nextReviewAt": (
                        row.nextReviewAt.isoformat()
                        if row.nextReviewAt
                        else None
                    ),
                }
            )

        averageMastery = (
            round(
                sum(
                    item["masteryLevel"]
                    for item in units
                )
                / len(units),
                1,
            )
            if units
            else 0
        )

        return {
            "units": units,
            "averageMastery": averageMastery,
            "trackedUnitCount": len(units),
        }
