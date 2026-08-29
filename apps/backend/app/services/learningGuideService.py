from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.contracts.learningGuideContract import (
    LearningGuideContract,
    LearningGuideStepContract,
)
from app.domain.common.domainError import DomainError
from app.persistence.models.academicStageModel import AcademicStageModel
from app.persistence.models.agentMessageModel import AgentMessageModel
from app.persistence.models.agentThreadModel import AgentThreadModel
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


class LearningGuideService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)

    def build(self, studentId: UUID) -> LearningGuideContract:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        counts = self._counts(studentId)

        ordered = [
            ("ACADEMIC_STAGE", "Etapa acadêmica", "Informe a etapa atual quando fizer sentido para o aluno.", "Abrir Etapa"),
            ("LEARNING_CONTEXT", "Contexto de estudo", "Defina onde o aluno está estudando: escola, ENEM, vestibular, curso ou outro contexto.", "Abrir Contextos"),
            ("SUBJECT", "Matérias", "Crie as matérias específicas deste aluno e contexto.", "Abrir Matérias"),
            ("LEARNING_UNIT", "Unidades", "Cadastre lições, capítulos ou módulos que o aluno precisa estudar.", "Abrir Unidades"),
            ("MATERIAL", "Materiais", "Envie apostilas, PDFs, imagens ou textos que serão a fonte de estudo.", "Abrir Materiais"),
            ("PEDAGOGICAL", "Estudar com a Lia", "Use os materiais para aprender, resumir, criar mapas mentais, flashcards e exercícios.", "Abrir Estudar"),
            ("LIA_TUTOR", "Conversar com a Lia", "Converse com a tutora, faça perguntas e peça explicações ou recursos visuais.", "Abrir Lia"),
            ("LEARNING_GOAL", "Objetivo", "Defina o que o aluno quer alcançar, como uma prova ou revisão.", "Abrir Objetivos"),
            ("STUDY_SCOPE", "Escopo", "Escolha quais unidades entram neste objetivo de estudo.", "Abrir Escopos"),
            ("STUDY_SESSION", "Sessão", "Inicie uma sessão para trabalhar o escopo escolhido.", "Abrir Sessões"),
            ("LEARNING_PROGRESS", "Progresso", "Acompanhe estudos, domínio e confiança por unidade.", "Abrir Progresso"),
        ]

        complete = {
            "ACADEMIC_STAGE": counts["stage"] > 0,
            "LEARNING_CONTEXT": counts["context"] > 0,
            "SUBJECT": counts["subject"] > 0,
            "LEARNING_UNIT": counts["unit"] > 0,
            "MATERIAL": counts["material"] > 0,
            "PEDAGOGICAL": counts["pedagogical"] > 0,
            "LIA_TUTOR": counts["lia"] > 0,
            "LEARNING_GOAL": counts["goal"] > 0,
            "STUDY_SCOPE": counts["scope"] > 0,
            "STUDY_SESSION": counts["session"] > 0,
            "LEARNING_PROGRESS": counts["state"] > 0,
        }

        # AcademicStage is useful, but not mandatory for every preparatory context.
        if not complete["ACADEMIC_STAGE"] and complete["LEARNING_CONTEXT"]:
            optionalStage = True
        else:
            optionalStage = False

        recommendationOrder = [
            "ACADEMIC_STAGE",
            "LEARNING_CONTEXT",
            "SUBJECT",
            "LEARNING_UNIT",
            "MATERIAL",
            "PEDAGOGICAL",
            "LIA_TUTOR",
            "LEARNING_GOAL",
            "STUDY_SCOPE",
            "STUDY_SESSION",
            "LEARNING_PROGRESS",
        ]

        recommended = "LEARNING_PROGRESS"

        for section in recommendationOrder:
            if section == "ACADEMIC_STAGE" and optionalStage:
                continue

            if not complete[section]:
                recommended = section
                break

        prerequisites = {
            "ACADEMIC_STAGE": True,
            "LEARNING_CONTEXT": True,
            "SUBJECT": complete["LEARNING_CONTEXT"],
            "LEARNING_UNIT": complete["SUBJECT"],
            "MATERIAL": complete["LEARNING_UNIT"],
            "PEDAGOGICAL": complete["MATERIAL"],
            "LIA_TUTOR": complete["MATERIAL"],
            "LEARNING_GOAL": complete["LEARNING_UNIT"],
            "STUDY_SCOPE": complete["LEARNING_GOAL"],
            "STUDY_SESSION": complete["STUDY_SCOPE"],
            "LEARNING_PROGRESS": complete["STUDY_SESSION"],
        }

        steps = []
        for section, title, description, actionLabel in ordered:
            if complete[section]:
                status = "COMPLETE"
            elif section == "ACADEMIC_STAGE" and optionalStage:
                status = "OPTIONAL"
            elif section == recommended:
                status = "NEXT"
            elif prerequisites[section]:
                status = "AVAILABLE"
            else:
                status = "BLOCKED"

            steps.append(
                LearningGuideStepContract(
                    section=section,
                    title=title,
                    description=description,
                    status=status,
                    actionLabel=actionLabel,
                )
            )

        recommendedStep = next(
            step for step in steps if step.section == recommended
        )

        completedSteps = sum(
            1 for step in steps if step.status == "COMPLETE"
        )

        return LearningGuideContract(
            recommendedSection=recommended,
            headline=f"Próximo passo: {recommendedStep.title}",
            message=recommendedStep.description,
            completedSteps=completedSteps,
            totalSteps=len(steps),
            steps=steps,
        )

    def _counts(self, studentId: UUID) -> dict[str, int]:
        stage = self._count(
            select(func.count(AcademicStageModel.academicStageId)).where(
                AcademicStageModel.studentId == studentId,
                AcademicStageModel.status == "CURRENT",
            )
        )

        context = self._count(
            select(
                func.count(
                    StudentLearningContextModel.studentLearningContextId
                )
            ).where(
                StudentLearningContextModel.studentId == studentId,
                StudentLearningContextModel.status == "ACTIVE",
            )
        )

        subject = self._count(
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
        )

        unit = self._count(
            select(func.count(StudentLearningUnitModel.studentLearningUnitId))
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
        )

        material = self._count(
            select(func.count(MaterialModel.materialId)).where(
                MaterialModel.studentId == studentId,
                MaterialModel.status != "ARCHIVED",
            )
        )

        pedagogical = self._count(
            select(
                func.count(
                    PedagogicalArtifactModel.pedagogicalArtifactId
                )
            ).where(
                PedagogicalArtifactModel.studentId == studentId,
                PedagogicalArtifactModel.status == "READY",
            )
        )

        lia = self._count(
            select(
                func.count(
                    AgentMessageModel.agentMessageId
                )
            )
            .join(
                AgentThreadModel,
                AgentThreadModel.agentThreadId
                == AgentMessageModel.agentThreadId,
            )
            .where(
                AgentThreadModel.studentId == studentId,
                AgentMessageModel.role == "ASSISTANT",
            )
        )

        goal = self._count(
            select(func.count(LearningGoalModel.learningGoalId)).where(
                LearningGoalModel.studentId == studentId,
                LearningGoalModel.status == "ACTIVE",
            )
        )

        scope = self._count(
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
        )

        session = self._count(
            select(func.count(StudySessionModel.studySessionId)).where(
                StudySessionModel.studentId == studentId,
                StudySessionModel.status == "COMPLETED",
            )
        )

        state = self._count(
            select(
                func.count(
                    StudentLearningStateModel.studentLearningStateId
                )
            ).where(
                StudentLearningStateModel.studentId == studentId,
                StudentLearningStateModel.studyCount > 0,
            )
        )

        return {
            "stage": stage,
            "context": context,
            "subject": subject,
            "unit": unit,
            "material": material,
            "pedagogical": pedagogical,
            "lia": lia,
            "goal": goal,
            "scope": scope,
            "session": session,
            "state": state,
        }

    def _count(self, statement) -> int:
        return int(self.session.scalar(statement) or 0)
