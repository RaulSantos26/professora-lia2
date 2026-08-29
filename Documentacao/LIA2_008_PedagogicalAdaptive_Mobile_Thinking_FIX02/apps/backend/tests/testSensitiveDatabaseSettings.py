from app.config.databaseSettings import DatabaseSettings


def testDatabasePasswordIsNotExposedInRepr():
    settings = DatabaseSettings(password="database-secret")

    assert "database-secret" not in repr(settings)
