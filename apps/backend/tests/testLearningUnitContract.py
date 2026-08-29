from app.contracts.learningUnitContract import LearningUnitCreateContract


def testLearningUnitNormalizesCodeAndTitle():
    contract = LearningUnitCreateContract(
        code=" funcoes 01 ",
        title="  Funções   e gráficos ",
    )

    assert contract.code == "FUNCOES_01"
    assert contract.title == "Funções e gráficos"
