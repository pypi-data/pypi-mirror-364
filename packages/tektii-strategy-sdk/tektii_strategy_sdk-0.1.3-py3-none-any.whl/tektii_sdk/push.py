"""Push command implementation for deploying strategies to Tektii platform."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, Field, ValidationError

from tektii_sdk.validator import validate_module


class CreateStrategyVersionResponseDTO(BaseModel):
    """Response from create strategy version API."""

    repositoryUrl: str = Field(..., description="Container registry URL")
    accessToken: str = Field(..., description="Access token for registry authentication")
    versionId: str = Field(..., description="Strategy version ID")


class PushConfig(BaseModel):
    """Configuration for push command."""

    api_key: str = Field(..., description="Tektii API key")
    strategy_id: str = Field(..., description="Strategy ID")
    api_url: str = Field(default="https://api.tektii.com", description="Tektii API URL")
    platform: Optional[str] = Field(default="linux/amd64", description="Docker platform")


def load_push_config() -> PushConfig:
    """Load push configuration from environment or .tektii file.

    Returns:
        Push configuration

    Raises:
        ValueError: If required configuration is missing
    """
    # First try to load from .tektii file
    config_file = Path.home() / ".tektii" / "config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config_data = json.load(f)
                # Allow environment variables to override file config
                config_data["api_key"] = os.environ.get("TEKTII_API_KEY", config_data.get("api_key"))
                config_data["strategy_id"] = os.environ.get("TEKTII_STRATEGY_ID", config_data.get("strategy_id"))
                config_data["api_url"] = os.environ.get("TEKTII_API_URL", config_data.get("api_url", "https://api.tektii.com"))
                return PushConfig(**config_data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Warning: Error loading config from {config_file}: {e}")

    # Fall back to environment variables
    api_key = os.environ.get("TEKTII_API_KEY")
    strategy_id = os.environ.get("TEKTII_STRATEGY_ID")
    api_url = os.environ.get("TEKTII_API_URL", "https://api.tektii.com")

    if not api_key:
        raise ValueError(
            "API key not found. Please set TEKTII_API_KEY environment variable or create ~/.tektii/config.json\n"
            "You can get your API key from https://app.tektii.com/settings"
        )

    if not strategy_id:
        raise ValueError(
            "Strategy ID not found. Please set TEKTII_STRATEGY_ID environment variable or create ~/.tektii/config.json\n"
            "You can find your strategy ID in the Tektii web UI"
        )

    return PushConfig(api_key=api_key, strategy_id=strategy_id, api_url=api_url)


def save_push_config(config: PushConfig) -> None:
    """Save push configuration to .tektii file.

    Args:
        config: Push configuration to save
    """
    config_dir = Path.home() / ".tektii"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.json"
    with open(config_file, "w") as f:
        # Don't save the access token
        config_dict = config.model_dump(exclude={"access_token"})
        json.dump(config_dict, f, indent=2)

    print(f"✅ Configuration saved to {config_file}")


def get_git_sha() -> Optional[str]:
    """Get the current Git commit SHA (short form).

    Returns:
        Short Git SHA or None if not in a Git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        # Git not installed
        pass
    return None


def create_strategy_version(config: PushConfig) -> CreateStrategyVersionResponseDTO:
    """Create a new strategy version via API.

    Args:
        config: Push configuration

    Returns:
        API response with repository details

    Raises:
        requests.HTTPError: If API request fails
    """
    url = f"{config.api_url}/v1/strategies/{config.strategy_id}/versions"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": config.api_key,
    }

    # Get current Git SHA if available
    git_sha = get_git_sha()
    request_data: Dict[str, str] = {}
    if git_sha:
        request_data["gitSha"] = git_sha
        print(f"📡 Creating new strategy version (git: {git_sha})...")
    else:
        print("📡 Creating new strategy version...")
        print("   ⚠️  Not in a Git repository or Git not available")

    print(f"   API: {config.api_url}")
    print(f"   Strategy ID: {config.strategy_id}")

    response = None
    try:
        response = requests.post(url, headers=headers, json=request_data, timeout=30)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise requests.HTTPError(f"Failed to connect to {config.api_url}. Please check your internet connection and API URL.") from None
    except requests.exceptions.Timeout:
        raise requests.HTTPError("Request timed out. Please try again.")
    except requests.HTTPError as e:
        if response and response.status_code == 401:
            raise requests.HTTPError("Authentication failed. Please check your API key.")
        elif response and response.status_code == 404:
            raise requests.HTTPError(f"Strategy not found. Please check your strategy ID: {config.strategy_id}")
        elif response and response.status_code == 429:
            raise requests.HTTPError("Rate limit exceeded. Please try again later.")
        elif response:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg += f": {error_data['message']}"
            except json.JSONDecodeError:
                pass
            raise requests.HTTPError(error_msg) from e
        else:
            raise

    try:
        data = response.json()
        return CreateStrategyVersionResponseDTO(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Invalid response from API: {e}") from e


def run_command(cmd: str, description: str, capture_output: bool = False) -> Tuple[int, str]:
    """Run a shell command with progress indication.

    Args:
        cmd: Command to run
        description: Description for progress message
        capture_output: Whether to capture output

    Returns:
        Tuple of (return code, output)
    """
    print(f"🔧 {description}...")

    # Using shell=False and splitting command for security
    # For Docker commands, we need shell=True but these are controlled inputs
    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # nosec B602
        return result.returncode, result.stdout + result.stderr
    else:
        result_no_capture = subprocess.run(cmd, shell=True)  # nosec B602
        return result_no_capture.returncode, ""


def check_docker() -> bool:
    """Check if Docker is available.

    Returns:
        True if Docker is available
    """
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def build_and_push_image(
    version_response: CreateStrategyVersionResponseDTO,
    strategy_path: Path,
    platform: Optional[str] = "linux/amd64",
) -> None:
    """Build and push Docker image to registry.

    Args:
        version_response: API response with registry details
        strategy_path: Path to strategy directory
        platform: Docker platform to build for

    Raises:
        RuntimeError: If build or push fails
    """
    # Parse registry URL to get components
    parsed_url = urlparse(version_response.repositoryUrl)
    registry_host = parsed_url.netloc
    image_path = parsed_url.path.lstrip("/")

    # Full image tag
    image_tag = f"{registry_host}/{image_path}:{version_response.versionId}"

    # Check for Dockerfile
    dockerfile_path = strategy_path / "Dockerfile"
    if not dockerfile_path.exists():
        print("📝 No Dockerfile found. Creating a default one...")
        create_default_dockerfile(strategy_path)

    # Login to registry
    print(f"🔐 Logging in to {registry_host}...")
    login_cmd = f'echo "{version_response.accessToken}" | docker login -u oauth2accesstoken --password-stdin https://{registry_host}'
    returncode, output = run_command(login_cmd, "Authenticating with container registry", capture_output=True)
    if returncode != 0:
        raise RuntimeError(f"Failed to login to registry: {output}")

    # Build image
    platform_args = f"--platform {platform}" if platform else ""
    build_cmd = f"docker build {platform_args} -t {image_tag} {strategy_path}"
    returncode, output = run_command(build_cmd, f"Building Docker image for {platform or 'default platform'}")
    if returncode != 0:
        raise RuntimeError("Failed to build Docker image")

    # Push image
    push_cmd = f"docker push {image_tag}"
    returncode, output = run_command(push_cmd, "Pushing image to registry")
    if returncode != 0:
        raise RuntimeError("Failed to push Docker image")

    print(f"✅ Successfully pushed {image_tag}")


def create_default_dockerfile(strategy_path: Path) -> None:
    """Create a default Dockerfile for the strategy.

    Args:
        strategy_path: Path to strategy directory
    """
    dockerfile_content = """FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 strategy

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || pip install tektii-strategy-sdk

# Copy strategy code
COPY --chown=strategy:strategy . .

# Switch to non-root user
USER strategy

# The entry point will be provided by the platform
# Your strategy will be run with: tektii run <module> <class>
"""

    dockerfile_path = strategy_path / "Dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)

    # Also create a requirements.txt if it doesn't exist
    requirements_path = strategy_path / "requirements.txt"
    if not requirements_path.exists():
        with open(requirements_path, "w") as f:
            f.write("tektii-strategy-sdk>=0.1.0\n")


def push_strategy(
    module_path: str,
    class_name: str,
    config_path: Optional[str] = None,
    api_url: Optional[str] = None,
    save_config: bool = False,
) -> None:
    """Push a strategy to the Tektii platform.

    Args:
        module_path: Path to strategy module
        class_name: Name of strategy class
        config_path: Optional path to config file
        api_url: Optional API URL override
        save_config: Whether to save configuration

    Raises:
        Various exceptions on failure
    """
    print("🚀 Tektii Strategy Push")
    print("=" * 50)

    # Check Docker availability
    if not check_docker():
        raise RuntimeError(
            "Docker is not installed or not running. Please install Docker and try again.\n"
            "Visit https://docs.docker.com/get-docker/ for installation instructions."
        )

    # Validate strategy first
    print("\n📋 Validating strategy...")
    validation_result = validate_module(module_path, class_name, config=None)
    if not validation_result.is_valid:
        print(f"\n❌ Strategy validation failed:\n{validation_result}")
        sys.exit(1)
    print("✅ Strategy validation passed")

    # Load push configuration
    try:
        push_config = load_push_config()
        if api_url:
            push_config.api_url = api_url
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        sys.exit(1)

    # Save config if requested
    if save_config:
        save_push_config(push_config)

    # Get strategy directory
    strategy_path = Path(module_path).parent.resolve()
    if strategy_path == Path.cwd():
        # Module is in current directory
        strategy_path = Path.cwd()

    print(f"\n📁 Strategy directory: {strategy_path}")

    try:
        # Create strategy version
        version_response = create_strategy_version(push_config)
        print(f"✅ Created version: {version_response.versionId}")

        # Build and push Docker image
        build_and_push_image(version_response, strategy_path, push_config.platform)

        print("\n🎉 Strategy successfully deployed!")
        print(f"   Version ID: {version_response.versionId}")
        print(f"   View in console: {push_config.api_url.replace('api.', 'app.')}/strategies/{push_config.strategy_id}")

    except requests.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Deployment Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
