import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_ai_model():
    return MagicMock()

@pytest.fixture
def mock_database():
    return MagicMock()

@pytest.fixture
def mock_api_client():
    return MagicMock()

@pytest.fixture
def mock_auth_service():
    return MagicMock() 