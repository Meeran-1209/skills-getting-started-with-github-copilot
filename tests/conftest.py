from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as api


@pytest.fixture
def activities(monkeypatch):
    test_activities = deepcopy(api.activities)
    monkeypatch.setattr(api, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    with TestClient(api.app) as test_client:
        yield test_client
