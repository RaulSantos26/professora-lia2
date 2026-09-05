from sqlalchemy.orm import Session

from app.agents.specialists.evidenceSpecialist import EvidenceSpecialist
from app.agents.specialists.pedagogicalReviewSpecialist import PedagogicalReviewSpecialist
from app.agents.specialists.tutorSpecialist import TutorSpecialist
from app.agents.tutorResponseService import TutorResponseService
from app.tools.evidenceSearchTool import EvidenceSearchTool


class TutorSpecialistRegistry:
    """Allowlisted internal specialists. The Harness remains their sole orchestrator."""

    def __init__(self, session: Session):
        self.evidence = EvidenceSpecialist(EvidenceSearchTool(session))
        self.tutor = TutorSpecialist(TutorResponseService())
        self.review = PedagogicalReviewSpecialist()