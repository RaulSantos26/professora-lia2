from app.contracts.studentSubjectContract import StudentSubjectContract
from app.persistence.models.studentSubjectModel import StudentSubjectModel


class StudentSubjectMapper:
    @staticmethod
    def toContract(model: StudentSubjectModel) -> StudentSubjectContract:
        return StudentSubjectContract.model_validate(model)
