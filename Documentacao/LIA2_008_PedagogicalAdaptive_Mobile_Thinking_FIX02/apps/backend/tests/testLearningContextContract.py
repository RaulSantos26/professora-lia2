from datetime import date

import pytest
from pydantic import ValidationError

from app.contracts.learningContextContract import (
    LearningContextCreateContract,
)


def testLearningContextNormalizesCode():
    contract = LearningContextCreateContract(
        contextType="ENEM",
        code=" enem 2026 ",
        name="ENEM 2026",
    )

    assert contract.code == "ENEM_2026"


def testLearningContextRejectsInvalidDateRange():
    with pytest.raises(ValidationError):
        LearningContextCreateContract(
            contextType="VESTIBULAR",
            code="VEST_2026",
            name="Vestibular 2026",
            startsAt=date(2026, 8, 1),
            endsAt=date(2026, 7, 1),
        )
