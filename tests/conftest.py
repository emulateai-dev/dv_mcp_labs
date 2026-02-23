import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
from unittest.mock import Mock, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration dictionary."""
    return {
        "debug": True,
        "host": "localhost",
        "port": 8000,
        "workers": 1,
        "log_level": "DEBUG",
        "database_url": "sqlite:///:memory:",
        "secret_key": "test-secret-key",
        "allowed_hosts": ["localhost", "127.0.0.1"],
        "cors_origins": ["http://localhost:3000"],
    }


@pytest.fixture
def mock_fastapi_app():
    """Mock FastAPI application instance."""
    app = MagicMock()
    app.state = MagicMock()
    app.state.config = {}
    return app


@pytest.fixture
def mock_request():
    """Mock FastAPI request object."""
    request = Mock()
    request.headers = {}
    request.query_params = {}
    request.path_params = {}
    request.cookies = {}
    request.client = Mock()
    request.client.host = "127.0.0.1"
    request.client.port = 50000
    request.url = Mock()
    request.url.path = "/test"
    request.method = "GET"
    return request


@pytest.fixture
def mock_response():
    """Mock FastAPI response object."""
    response = Mock()
    response.status_code = 200
    response.headers = {}
    response.body = b""
    return response


@pytest.fixture
def mock_http_client():
    """Mock httpx client for testing external API calls."""
    client = MagicMock()
    client.get = MagicMock()
    client.post = MagicMock()
    client.put = MagicMock()
    client.delete = MagicMock()
    client.patch = MagicMock()
    return client


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_challenge_data() -> Dict[str, Any]:
    """Sample challenge data for testing."""
    return {
        "id": "test-challenge-1",
        "name": "Test Challenge",
        "description": "A test challenge for unit testing",
        "difficulty": "easy",
        "points": 100,
        "solution": "test_solution",
        "hints": ["Hint 1", "Hint 2"],
        "tags": ["test", "sample"],
    }


@pytest.fixture
def mock_sse_event():
    """Mock Server-Sent Event data."""
    return {
        "event": "test_event",
        "data": {"message": "Test SSE message", "timestamp": "2024-01-01T00:00:00Z"},
        "id": "test-event-1",
        "retry": 3000,
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing MCP-related functionality."""
    client = MagicMock()
    client.connect = MagicMock()
    client.disconnect = MagicMock()
    client.send_message = MagicMock()
    client.receive_message = MagicMock()
    client.is_connected = MagicMock(return_value=True)
    return client


@pytest.fixture
def capture_logs():
    """Capture log messages during tests."""
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Get root logger
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    yield log_capture
    
    # Clean up
    logger.removeHandler(handler)
    handler.close()


@pytest.fixture
def mock_supervisor_config():
    """Mock supervisor configuration for testing process management."""
    return {
        "programs": [
            {
                "name": "test_process",
                "command": "python test.py",
                "directory": "/workspace",
                "autostart": True,
                "autorestart": True,
                "stdout_logfile": "/tmp/test_stdout.log",
                "stderr_logfile": "/tmp/test_stderr.log",
            }
        ]
    }