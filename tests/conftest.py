import os

import pytest
from fastapi.testclient import TestClient

os.environ["CC_MONITOR_API_KEY"] = "test-key"

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app, headers={"Authorization": "Bearer test-key"})


@pytest.fixture
def anon():
    return TestClient(app)