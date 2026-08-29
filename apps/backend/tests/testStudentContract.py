from app.contracts.studentContract import StudentCreateContract


def testStudentCreateNormalizesWhitespace():
    contract = StudentCreateContract(
        fullName="  Aluno   Exemplo  ",
        preferredName="  Exemplo ",
    )

    assert contract.fullName == "Aluno Exemplo"
    assert contract.preferredName == "Exemplo"
