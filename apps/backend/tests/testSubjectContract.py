from app.contracts.subjectContract import SubjectCreateContract


def testSubjectNormalizesCodeAndText():
    contract = SubjectCreateContract(
        code=" matematica geral ",
        name="  Matemática   Geral ",
    )

    assert contract.code == "MATEMATICA_GERAL"
    assert contract.name == "Matemática Geral"
