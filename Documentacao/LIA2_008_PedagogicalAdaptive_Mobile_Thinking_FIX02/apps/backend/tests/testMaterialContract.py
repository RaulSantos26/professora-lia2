from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.materialContract import MaterialContract


def testMaterialContractKeepsGovernanceAndOwnership():
    student_id = uuid4()

    contract = MaterialContract(
        materialId=uuid4(),
        studentId=student_id,
        studentLearningContextId=None,
        studentSubjectId=None,
        studentLearningUnitId=None,
        title="Apostila",
        materialType="PDF",
        sourceType="UPLOAD",
        description=None,
        status="UPLOADED",
        analysisRequested=False,
        studyEnabled=True,
        requestedModelId=None,
        lastProcessingErrorCode=None,
        lastProcessingErrorMessage=None,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )

    assert contract.studentId == student_id
    assert contract.analysisRequested is False
    assert contract.studyEnabled is True
    assert contract.contractName == "Material.v3"
    assert contract.aiMode == "AUTO"
    assert contract.thinkingMode == "AUTO"
