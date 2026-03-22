import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path("test_fieldops.db")


@pytest.fixture(scope="session")
def client():
    if TEST_DB.exists():
        TEST_DB.unlink()
    os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    if TEST_DB.exists():
        TEST_DB.unlink()
