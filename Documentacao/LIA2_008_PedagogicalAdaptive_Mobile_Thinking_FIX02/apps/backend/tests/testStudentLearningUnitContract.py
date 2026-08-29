from app.contracts.studentLearningUnitContract import (
    StudentLearningUnitCreateContract,
)


def testStudentLearningUnitNormalizesFields():
    contract = StudentLearningUnitCreateContract(
        code=" funcoes 01 ",
        title="  Funções  ",
    )

    assert contract.code == "FUNCOES_01"
    assert contract.title == "Funções"
