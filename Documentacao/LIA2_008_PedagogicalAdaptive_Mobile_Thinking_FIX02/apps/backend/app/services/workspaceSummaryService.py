from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.contracts.workspaceSummaryContract import WorkspaceSummaryContract
from app.domain.common.domainError import DomainError
from app.persistence.models.academicStageModel import AcademicStageModel
from app.persistence.models.learningGoalModel import LearningGoalModel
from app.persistence.models.materialModel import MaterialModel
from app.persistence.models.pedagogicalArtifactModel import PedagogicalArtifactModel
from app.persistence.models.studyScopeModel import StudyScopeModel
from app.persistence.models.studySessionModel import StudySessionModel
from app.persistence.models.studentLearningContextModel import (
    StudentLearningContextModel,
)
from app.persistence.models.studentLearningStateModel import (
    StudentLearningStateModel,
)
from app.persistence.models.studentLearningUnitModel import (
    StudentLearningUnitModel,
)
from app.persistence.models.studentSubjectModel import StudentSubjectModel
from app.repositories.studentRepository import StudentRepository


class WorkspaceSummaryService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)

    def get(self, studentId: UUID) -> WorkspaceSummaryContract:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        return WorkspaceSummaryContract(
            academicStageCount=self._count(
                select(func.count(AcademicStageModel.academicStageId)).where(
                    AcademicStageModel.studentId == studentId,
                    AcademicStageModel.status == "CURRENT",
                )
            ),
            learningContextCount=self._count(
                select(
                    func.count(
                        StudentLearningContextModel.studentLearningContextId
                    )
                ).where(
                    StudentLearningContextModel.studentId == studentId,
                    StudentLearningContextModel.status == "ACTIVE",
                )
            ),
            subjectCount=self._count(
                select(func.count(StudentSubjectModel.studentSubjectId))
                .join(
                    StudentLearningContextModel,
                    StudentLearningContextModel.studentLearningContextId
                    == StudentSubjectModel.studentLearningContextId,
                )
                .where(
                    StudentLearningContextModel.studentId == studentId,
                    StudentSubjectModel.status == "ACTIVE",
                )
            ),
            learningUnitCount=self._count(
                select(
                    func.count(
                        StudentLearningUnitModel.studentLearningUnitId
                    )
                )
                .join(
                    StudentSubjectModel,
                    StudentSubjectModel.studentSubjectId
                    == StudentLearningUnitModel.studentSubjectId,
                )
                .join(
                    StudentLearningContextModel,
                    StudentLearningContextModel.studentLearningContextId
                    == StudentSubjectModel.studentLearningContextId,
                )
                .where(
                    StudentLearningContextModel.studentId == studentId,
                    StudentLearningUnitModel.status == "ACTIVE",
                )
            ),
            materialCount=self._count(
                select(func.count(MaterialModel.materialId)).where(
                    MaterialModel.studentId == studentId,
                    MaterialModel.status != "ARCHIVED",
                )
            ),
            pedagogicalArtifactCount=self._count(
                select(
                    func.count(
                        PedagogicalArtifactModel.pedagogicalArtifactId
                    )
                ).where(
                    PedagogicalArtifactModel.studentId == studentId,
                    PedagogicalArtifactModel.status != "ARCHIVED",
                )
            ),
            learningGoalCount=self._count(
                select(func.count(LearningGoalModel.learningGoalId)).where(
                    LearningGoalModel.studentId == studentId,
                    LearningGoalModel.status != "ARCHIVED",
                )
            ),
            studyScopeCount=self._count(
                select(func.count(StudyScopeModel.studyScopeId))
                .join(
                    LearningGoalModel,
                    LearningGoalModel.learningGoalId
                    == StudyScopeModel.learningGoalId,
                )
                .where(
                    LearningGoalModel.studentId == studentId,
                    StudyScopeModel.status != "ARCHIVED",
                )
            ),
            studySessionCount=self._count(
                select(func.count(StudySessionModel.studySessionId)).where(
                    StudySessionModel.studentId == studentId,
                )
            ),
            learningProgressCount=self._count(
                select(
                    func.count(
                        StudentLearningStateModel.studentLearningStateId
                    )
                ).where(
                    StudentLearningStateModel.studentId == studentId,
                )
            ),
        )

    def _count(self, statement) -> int:
        return int(self.session.scalar(statement) or 0)
