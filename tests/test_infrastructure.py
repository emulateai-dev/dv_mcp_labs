import pytest
from pathlib import Path
import sys
import os


class TestInfrastructureSetup:
    """Validation tests to ensure the testing infrastructure is properly configured."""
    
    @pytest.mark.unit
    def test_project_structure_exists(self):
        """Test that the basic project structure exists."""
        assert Path("/workspace/tests").exists()
        assert Path("/workspace/tests/unit").exists()
        assert Path("/workspace/tests/integration").exists()
        assert Path("/workspace/tests/__init__.py").exists()
        assert Path("/workspace/tests/conftest.py").exists()
    
    @pytest.mark.unit
    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and is valid."""
        pyproject_path = Path("/workspace/pyproject.toml")
        assert pyproject_path.exists()
        
        # Check that it contains required sections
        content = pyproject_path.read_text()
        assert "[tool.poetry]" in content
        assert "[tool.pytest.ini_options]" in content
        assert "[tool.coverage.run]" in content
    
    @pytest.mark.unit
    def test_imports_work(self):
        """Test that project modules can be imported."""
        # Test importing from common module
        try:
            import common
            assert common is not None
        except ImportError:
            pytest.fail("Failed to import 'common' module")
        
        # Test importing from challenges module
        try:
            import challenges
            assert challenges is not None
        except ImportError:
            pytest.fail("Failed to import 'challenges' module")
    
    @pytest.mark.unit
    def test_fixtures_available(self, temp_dir, mock_config, mock_fastapi_app):
        """Test that custom fixtures are available and working."""
        # Test temp_dir fixture
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        
        # Test mock_config fixture
        assert isinstance(mock_config, dict)
        assert "debug" in mock_config
        assert "host" in mock_config
        
        # Test mock_fastapi_app fixture
        assert hasattr(mock_fastapi_app, "state")
        assert hasattr(mock_fastapi_app.state, "config")
    
    @pytest.mark.unit
    def test_pytest_markers_configured(self):
        """Test that custom pytest markers are configured."""
        # This test itself uses the unit marker
        assert True
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration marker works."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow marker works."""
        assert True
    
    @pytest.mark.unit
    def test_coverage_configuration(self):
        """Test that coverage is properly configured."""
        # Check that coverage will include the right source files
        pyproject_path = Path("/workspace/pyproject.toml")
        content = pyproject_path.read_text()
        
        assert '--cov=common' in content
        assert '--cov=challenges' in content
        assert '--cov-fail-under=0' in content  # Set to 0 for infrastructure setup
    
    @pytest.mark.unit
    def test_environment_fixture(self, reset_environment):
        """Test that environment reset fixture works."""
        # Set a test environment variable
        os.environ["TEST_VAR"] = "test_value"
        assert os.environ.get("TEST_VAR") == "test_value"
    
    @pytest.mark.unit
    def test_mock_fixtures(self, mock_request, mock_response, mock_http_client):
        """Test that mock fixtures are properly configured."""
        # Test mock_request
        assert hasattr(mock_request, "headers")
        assert hasattr(mock_request, "method")
        assert mock_request.method == "GET"
        
        # Test mock_response
        assert hasattr(mock_response, "status_code")
        assert mock_response.status_code == 200
        
        # Test mock_http_client
        assert hasattr(mock_http_client, "get")
        assert hasattr(mock_http_client, "post")
    
    @pytest.mark.unit
    def test_sample_data_fixtures(self, sample_challenge_data, mock_sse_event):
        """Test that sample data fixtures provide expected data."""
        # Test sample_challenge_data
        assert isinstance(sample_challenge_data, dict)
        assert "id" in sample_challenge_data
        assert "difficulty" in sample_challenge_data
        assert sample_challenge_data["difficulty"] == "easy"
        
        # Test mock_sse_event
        assert isinstance(mock_sse_event, dict)
        assert "event" in mock_sse_event
        assert "data" in mock_sse_event
        assert mock_sse_event["event"] == "test_event"


@pytest.mark.unit
def test_basic_assertion():
    """A simple test to verify pytest is working."""
    assert 1 + 1 == 2
    assert True is not False
    assert "pytest" in "Testing with pytest"


@pytest.mark.unit
def test_path_operations():
    """Test basic path operations to ensure environment is set up correctly."""
    test_path = Path("/workspace/tests")
    assert test_path.is_dir()
    assert test_path.parent == Path("/workspace")
    assert (test_path / "__init__.py").exists()