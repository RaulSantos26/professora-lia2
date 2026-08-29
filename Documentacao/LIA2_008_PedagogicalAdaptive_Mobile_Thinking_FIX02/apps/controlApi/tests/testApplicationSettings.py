from app.config.applicationSettings import ApplicationSettings


def testSensitiveSettingsAreNotExposedInRepr():
    settings = ApplicationSettings(
        opsInternalToken="internal-secret",
        adminToken="admin-secret",
        postgresPassword="database-secret",
    )

    representation = repr(settings)

    assert "internal-secret" not in representation
    assert "admin-secret" not in representation
    assert "database-secret" not in representation
