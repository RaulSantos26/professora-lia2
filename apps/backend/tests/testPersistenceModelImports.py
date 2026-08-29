import importlib
import pkgutil

import app.persistence.models as persistenceModels


def testAllPersistenceModelsImportWithoutRuntimeErrors():
    discovered = list(
        pkgutil.iter_modules(persistenceModels.__path__)
    )

    assert discovered

    for moduleInfo in discovered:
        importlib.import_module(
            f"app.persistence.models.{moduleInfo.name}"
        )
