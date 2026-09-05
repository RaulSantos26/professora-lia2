from app.agents.specialists.specialistContracts import TutorDraft


class TutorSpecialist:
    """Restricted specialist: drafts the student-facing answer from approved inputs."""

    name = "tutor-specialist"

    def __init__(self, responseService):
        self.responseService = responseService

    def draft(self, **request) -> TutorDraft:
        return TutorDraft(response=self.responseService.generate(**request))