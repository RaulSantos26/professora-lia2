from datetime import date

import pytest
from pydantic import ValidationError

from app.contracts.academicStageContract import AcademicStageCreateContract


def testAcademicStageRejectsInvalidDateRange():
    with pytest.raises(ValidationError):
        AcademicStageCreateContract(
            educationLevel="Ensino Fundamental",
            stageLabel="5º ano",
            startedAt=date(2026, 2, 1),
            endedAt=date(2026, 1, 1),
        )
