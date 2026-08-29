from app.contracts.materialContract import MaterialContract, MaterialFileContract
from app.persistence.models.materialFileModel import MaterialFileModel
from app.persistence.models.materialModel import MaterialModel


class MaterialMapper:
    @staticmethod
    def toContract(model: MaterialModel) -> MaterialContract:
        return MaterialContract.model_validate(model)

    @staticmethod
    def fileToContract(model: MaterialFileModel) -> MaterialFileContract:
        return MaterialFileContract.model_validate(model)
