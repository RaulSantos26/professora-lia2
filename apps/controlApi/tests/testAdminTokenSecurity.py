from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.security import adminTokenSecurity


def testAdminTokenRejectsInvalidToken():
    fakeSettings = SimpleNamespace(adminToken="expected")

    with patch.object(adminTokenSecurity, "settings", fakeSettings):
        try:
            adminTokenSecurity.requireAdminToken("wrong")
            assert False, "Era esperado HTTPException."
        except HTTPException as error:
            assert error.status_code == 401


def testAdminTokenAcceptsValidToken():
    fakeSettings = SimpleNamespace(adminToken="expected")

    with patch.object(adminTokenSecurity, "settings", fakeSettings):
        adminTokenSecurity.requireAdminToken("expected")
