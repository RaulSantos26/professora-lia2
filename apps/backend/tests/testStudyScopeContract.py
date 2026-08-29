from app.contracts.studyScopeContract import StudyScopeCreateContract

def testStudyScopeNormalizesName():
    contract = StudyScopeCreateContract(name="  Conteúdo   da prova  ")
    assert contract.name == "Conteúdo da prova"
