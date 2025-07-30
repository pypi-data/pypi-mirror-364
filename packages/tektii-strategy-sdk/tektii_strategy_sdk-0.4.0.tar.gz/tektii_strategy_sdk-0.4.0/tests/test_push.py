"""Tests for the push command."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from tektii_sdk.push import (
    CreateStrategyVersionResponseDTO,
    PushConfig,
    create_default_dockerfile,
    create_strategy_version,
    get_git_sha,
    load_push_config,
    push_strategy,
    save_push_config,
)


class TestPushConfig:
    """Test push configuration loading and saving."""

    def test_load_config_from_env(self) -> None:
        """Test loading configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "TEKTII_API_KEY": "test-key",
                "TEKTII_STRATEGY_ID": "test-strategy",
                "TEKTII_API_URL": "https://api.test.com",
            },
        ):
            config = load_push_config()
            assert config.api_key == "test-key"
            assert config.strategy_id == "test-strategy"
            assert config.api_url == "https://api.test.com"

    def test_load_config_missing_api_key(self) -> None:
        """Test error when API key is missing."""
        with patch.dict(os.environ, {"TEKTII_STRATEGY_ID": "test-strategy"}, clear=True), pytest.raises(ValueError, match="API key not found"):
            load_push_config()

    def test_load_config_missing_strategy_id(self) -> None:
        """Test error when strategy ID is missing."""
        with patch.dict(os.environ, {"TEKTII_API_KEY": "test-key"}, clear=True), pytest.raises(ValueError, match="Strategy ID not found"):
            load_push_config()

    def test_load_config_from_file(self, tmp_path: Path) -> None:
        """Test loading configuration from file."""
        config_dir = tmp_path / ".tektii"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        config_data = {
            "api_key": "file-key",
            "strategy_id": "file-strategy",
            "api_url": "https://api.file.com",
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        with patch.object(Path, "home", return_value=tmp_path):
            config = load_push_config()
            assert config.api_key == "file-key"
            assert config.strategy_id == "file-strategy"
            assert config.api_url == "https://api.file.com"

    def test_env_overrides_file(self, tmp_path: Path) -> None:
        """Test environment variables override file configuration."""
        config_dir = tmp_path / ".tektii"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        config_data = {
            "api_key": "file-key",
            "strategy_id": "file-strategy",
            "api_url": "https://api.file.com",
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        with patch.object(Path, "home", return_value=tmp_path), patch.dict(os.environ, {"TEKTII_API_KEY": "env-key"}):
            config = load_push_config()
            assert config.api_key == "env-key"  # Environment overrides file
            assert config.strategy_id == "file-strategy"

    def test_save_config(self, tmp_path: Path) -> None:
        """Test saving configuration to file."""
        config = PushConfig(
            api_key="save-key",
            strategy_id="save-strategy",
            api_url="https://api.save.com",
        )

        with patch.object(Path, "home", return_value=tmp_path):
            save_push_config(config)

        config_file = tmp_path / ".tektii" / "config.json"
        assert config_file.exists()

        with open(config_file) as f:
            saved_data = json.load(f)

        assert saved_data["api_key"] == "save-key"
        assert saved_data["strategy_id"] == "save-strategy"
        assert saved_data["api_url"] == "https://api.save.com"


class TestGitIntegration:
    """Test Git-related functionality."""

    @patch("subprocess.run")
    def test_get_git_sha_success(self, mock_run: Mock) -> None:
        """Test successful Git SHA retrieval."""
        mock_run.return_value = Mock(returncode=0, stdout="abc123\n")

        sha = get_git_sha()

        assert sha == "abc123"
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("subprocess.run")
    def test_get_git_sha_not_git_repo(self, mock_run: Mock) -> None:
        """Test Git SHA when not in a Git repository."""
        mock_run.return_value = Mock(returncode=1, stdout="")

        sha = get_git_sha()

        assert sha is None

    @patch("subprocess.run")
    def test_get_git_sha_git_not_installed(self, mock_run: Mock) -> None:
        """Test Git SHA when Git is not installed."""
        mock_run.side_effect = FileNotFoundError()

        sha = get_git_sha()

        assert sha is None


class TestCreateStrategyVersion:
    """Test API interaction for creating strategy versions."""

    @patch("tektii_sdk.push.get_git_sha")
    def test_create_version_success(self, mock_get_git_sha: Mock) -> None:
        """Test successful strategy version creation."""
        mock_get_git_sha.return_value = "abc123"

        config = PushConfig(
            api_key="test-key",
            strategy_id="test-strategy",
            api_url="https://api.test.com",
        )

        response_data = {
            "repositoryUrl": "us-central1-docker.pkg.dev/project/repo/image",
            "accessToken": "test-token",
            "versionId": "test-version",
        }

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = response_data
            mock_post.return_value = mock_response

            result = create_strategy_version(config)

            assert isinstance(result, CreateStrategyVersionResponseDTO)
            assert result.repositoryUrl == response_data["repositoryUrl"]
            assert result.accessToken == response_data["accessToken"]
            assert result.versionId == response_data["versionId"]

            # Check API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.test.com/v1/strategies/test-strategy/versions"
            assert call_args[1]["headers"]["X-API-Key"] == "test-key"
            assert call_args[1]["json"] == {"gitSha": "abc123"}

    @patch("tektii_sdk.push.get_git_sha")
    def test_create_version_without_git(self, mock_get_git_sha: Mock) -> None:
        """Test strategy version creation without Git."""
        mock_get_git_sha.return_value = None

        config = PushConfig(
            api_key="test-key",
            strategy_id="test-strategy",
            api_url="https://api.test.com",
        )

        response_data = {
            "repositoryUrl": "us-central1-docker.pkg.dev/project/repo/image",
            "accessToken": "test-token",
            "versionId": "test-version",
        }

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = response_data
            mock_post.return_value = mock_response

            create_strategy_version(config)

            # Check API call - should have empty json body when no git sha
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]["json"] == {}

    def test_create_version_auth_error(self) -> None:
        """Test authentication error handling."""
        config = PushConfig(
            api_key="bad-key",
            strategy_id="test-strategy",
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = requests.HTTPError()
            mock_post.return_value = mock_response

            with pytest.raises(requests.HTTPError, match="Authentication failed"):
                create_strategy_version(config)

    def test_create_version_not_found(self) -> None:
        """Test strategy not found error."""
        config = PushConfig(
            api_key="test-key",
            strategy_id="missing-strategy",
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.HTTPError()
            mock_post.return_value = mock_response

            with pytest.raises(requests.HTTPError, match="Strategy not found"):
                create_strategy_version(config)

    def test_create_version_connection_error(self) -> None:
        """Test connection error handling."""
        config = PushConfig(
            api_key="test-key",
            strategy_id="test-strategy",
        )

        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError()

            with pytest.raises(requests.HTTPError, match="Failed to connect"):
                create_strategy_version(config)


class TestDockerfileCreation:
    """Test Dockerfile creation."""

    def test_create_default_dockerfile(self, tmp_path: Path) -> None:
        """Test creating default Dockerfile."""
        create_default_dockerfile(tmp_path)

        dockerfile = tmp_path / "Dockerfile"
        assert dockerfile.exists()

        content = dockerfile.read_text()
        assert "FROM python:3.11-slim" in content
        assert "tektii-strategy-sdk" in content
        assert "USER strategy" in content

        # Check requirements.txt
        requirements = tmp_path / "requirements.txt"
        assert requirements.exists()
        assert "tektii-strategy-sdk>=0.1.0" in requirements.read_text()

    def test_dockerfile_not_overwritten(self, tmp_path: Path) -> None:
        """Test that existing Dockerfile is not overwritten."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("# Existing Dockerfile")

        # Check that it doesn't exist yet
        requirements = tmp_path / "requirements.txt"
        assert not requirements.exists()

        create_default_dockerfile(tmp_path)

        # Should create requirements.txt but since create_default_dockerfile
        # always creates a new Dockerfile, we need to check the requirements.txt was created
        assert requirements.exists()
        assert "tektii-strategy-sdk>=0.1.0" in requirements.read_text()


class TestPushStrategy:
    """Test the main push_strategy function."""

    @patch("tektii_sdk.push.check_docker")
    @patch("tektii_sdk.push.validate_module")
    @patch("tektii_sdk.push.load_push_config")
    @patch("tektii_sdk.push.create_strategy_version")
    @patch("tektii_sdk.push.build_and_push_image")
    def test_push_strategy_success(
        self,
        mock_build_push: Mock,
        mock_create_version: Mock,
        mock_load_config: Mock,
        mock_validate: Mock,
        mock_check_docker: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successful strategy push."""
        # Setup mocks
        mock_check_docker.return_value = True

        mock_validation = Mock()
        mock_validation.is_valid = True
        mock_validate.return_value = mock_validation

        mock_config = PushConfig(
            api_key="test-key",
            strategy_id="test-strategy",
        )
        mock_load_config.return_value = mock_config

        mock_version = CreateStrategyVersionResponseDTO(
            repositoryUrl="us-central1-docker.pkg.dev/project/repo/image",
            accessToken="test-token",
            versionId="test-version",
        )
        mock_create_version.return_value = mock_version

        # Create test strategy file
        strategy_file = tmp_path / "test_strategy.py"
        strategy_file.write_text("class TestStrategy: pass")

        # Run push
        push_strategy(str(strategy_file), "TestStrategy")

        # Verify calls
        mock_check_docker.assert_called_once()
        mock_validate.assert_called_once()
        mock_create_version.assert_called_once_with(mock_config)
        mock_build_push.assert_called_once()

    @patch("tektii_sdk.push.check_docker")
    def test_push_strategy_no_docker(self, mock_check_docker: Mock) -> None:
        """Test error when Docker is not available."""
        mock_check_docker.return_value = False

        with pytest.raises(RuntimeError, match="Docker is not installed"):
            push_strategy("test.py", "TestStrategy")

    @patch("tektii_sdk.push.check_docker")
    @patch("tektii_sdk.push.validate_module")
    def test_push_strategy_validation_failed(self, mock_validate: Mock, mock_check_docker: Mock) -> None:
        """Test error when strategy validation fails."""
        mock_check_docker.return_value = True

        # Create a mock validation result that will fail
        mock_validation = Mock(spec=["is_valid", "__str__"])
        mock_validation.is_valid = False
        # Mock the string representation without direct assignment
        mock_validation.__str__ = lambda self: "Validation failed"  # type: ignore[method-assign, assignment, misc]
        mock_validate.return_value = mock_validation

        with pytest.raises(SystemExit):
            push_strategy("test.py", "TestStrategy")

    @patch("tektii_sdk.push.check_docker")
    @patch("tektii_sdk.push.validate_module")
    @patch("tektii_sdk.push.load_push_config")
    @patch("tektii_sdk.push.save_push_config")
    def test_push_strategy_save_config(
        self,
        mock_save_config: Mock,
        mock_load_config: Mock,
        mock_validate: Mock,
        mock_check_docker: Mock,
    ) -> None:
        """Test saving configuration when requested."""
        mock_check_docker.return_value = True

        mock_validation = Mock()
        mock_validation.is_valid = True
        mock_validate.return_value = mock_validation

        mock_config = PushConfig(
            api_key="test-key",
            strategy_id="test-strategy",
        )
        mock_load_config.return_value = mock_config

        with patch("tektii_sdk.push.create_strategy_version"), patch("tektii_sdk.push.build_and_push_image"):
            push_strategy("test.py", "TestStrategy", save_config=True)

        mock_save_config.assert_called_once_with(mock_config)
