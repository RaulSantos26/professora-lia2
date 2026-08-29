from app.contracts.studentSubjectContract import StudentSubjectCreateContract


def testStudentSubjectNormalizesIndependentIdentityFields():
    contract = StudentSubjectCreateContract(
        code=" matematica ",
        name="  Matemática  ",
    )

    assert contract.code == "MATEMATICA"
    assert contract.name == "Matemática"
