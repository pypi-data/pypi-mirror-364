import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.responses import FileResponse
from bedrock_server_manager.web.main import app
from bedrock_server_manager.web.dependencies import validate_server_exists
from bedrock_server_manager.web.auth_utils import create_access_token
from datetime import timedelta
import os

# Test data
TEST_USER = "testuser"


@pytest.fixture
def client():
    """Create a test client for the app, with authentication and mocked dependencies."""
    os.environ["BEDROCK_SERVER_MANAGER_USERNAME"] = TEST_USER
    os.environ["BEDROCK_SERVER_MANAGER_PASSWORD"] = "testpassword"
    os.environ["BEDROCK_SERVER_MANAGER_SECRET_KEY"] = "test-secret-key"

    app.dependency_overrides[validate_server_exists] = lambda: "test-server"

    access_token = create_access_token(
        data={"sub": TEST_USER}, expires_delta=timedelta(minutes=15)
    )
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {access_token}"

    yield client

    del os.environ["BEDROCK_SERVER_MANAGER_USERNAME"]
    del os.environ["BEDROCK_SERVER_MANAGER_PASSWORD"]
    del os.environ["BEDROCK_SERVER_MANAGER_SECRET_KEY"]
    app.dependency_overrides = {}


import tempfile


@pytest.mark.skip(reason="FileResponse is causing issues")
@patch("bedrock_server_manager.web.routers.util.FileResponse")
@patch("bedrock_server_manager.web.routers.util.get_settings_instance")
@patch("bedrock_server_manager.web.routers.util.os.path.isfile")
def test_serve_custom_panorama_api_custom(
    mock_isfile, mock_get_settings, mock_file_response, client
):
    """Test the serve_custom_panorama_api route with a custom panorama."""
    mock_get_settings.return_value.config_dir = "/fake/path"
    mock_isfile.return_value = True

    async def fake_file_response(*args, **kwargs):
        return MagicMock(status_code=200)

    mock_file_response.side_effect = fake_file_response

    response = client.get("/api/panorama")
    assert response.status_code == 200


@patch("bedrock_server_manager.web.routers.util.get_settings_instance")
@patch("bedrock_server_manager.web.routers.util.os.path.isfile")
def test_serve_custom_panorama_api_default(mock_isfile, mock_get_settings, client):
    """Test the serve_custom_panorama_api route with a default panorama."""
    with tempfile.NamedTemporaryFile(suffix=".jpeg") as tmp:
        mock_get_settings.return_value.config_dir = "/fake/path"
        mock_isfile.side_effect = [False, True]

        response = client.get("/api/panorama")
        assert response.status_code == 200


@patch("bedrock_server_manager.web.routers.util.get_settings_instance")
@patch("bedrock_server_manager.web.routers.util.os.path.isfile")
def test_serve_custom_panorama_api_not_found(mock_isfile, mock_get_settings, client):
    """Test the serve_custom_panorama_api route with no panorama found."""
    mock_get_settings.return_value.config_dir = "/fake/path"
    mock_isfile.return_value = False

    response = client.get("/api/panorama")
    assert response.status_code == 404


@pytest.mark.skip(reason="FileResponse is causing issues")
@pytest.mark.skip(reason="FileResponse is causing issues")
def test_serve_world_icon_api_default(client):
    """Test the serve_world_icon_api route with a custom icon."""
    mock_get_server.return_value.world_icon_filesystem_path = "/fake/path"
    mock_get_server.return_value.has_world_icon.return_value = True
    mock_isfile.return_value = True

    async def fake_file_response(*args, **kwargs):
        return MagicMock(status_code=200)

    mock_file_response.side_effect = fake_file_response

    response = client.get("/api/server/test-server/world/icon")
    assert response.status_code == 200


@pytest.mark.skip(reason="FileResponse is causing issues")
def test_serve_world_icon_api_default(client):
    """Test the serve_world_icon_api route with a default icon."""
    mock_get_server.return_value.world_icon_filesystem_path = "/fake/path"
    mock_get_server.return_value.has_world_icon.return_value = False
    mock_isfile.side_effect = [False, True]
    mock_file_response.return_value = MagicMock(spec=FileResponse, background=None)
    mock_file_response.return_value.status_code = 200

    response = client.get("/api/server/test-server/world/icon")
    assert response.status_code == 200


@patch("bedrock_server_manager.web.routers.util.get_server_instance")
@patch("bedrock_server_manager.web.routers.util.os.path.isfile")
def test_serve_world_icon_api_not_found(mock_isfile, mock_get_server, client):
    """Test the serve_world_icon_api route with no icon found."""
    mock_get_server.return_value.world_icon_filesystem_path = "/fake/path"
    mock_get_server.return_value.has_world_icon.return_value = False
    mock_isfile.return_value = False

    response = client.get("/api/server/test-server/world/icon")
    assert response.status_code == 404


@patch("bedrock_server_manager.web.routers.util.os.path.exists")
def test_get_root_favicon(mock_exists, client):
    """Test the get_root_favicon route with a successful response."""
    mock_exists.return_value = True

    response = client.get("/favicon.ico")
    assert response.status_code == 200


@patch("bedrock_server_manager.web.routers.util.os.path.exists")
def test_get_root_favicon_not_found(mock_exists, client):
    """Test the get_root_favicon route with no favicon found."""
    mock_exists.return_value = False

    response = client.get("/favicon.ico")
    assert response.status_code == 404


def test_catch_all_api_route(client):
    """Test the catch_all_api_route with a successful redirect."""
    response = client.get("/invalid/path")
    assert response.status_code == 200
    assert "Bedrock Server Manager" in response.text
