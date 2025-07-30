import pytest
from unittest.mock import patch, MagicMock

from bedrock_server_manager.api.addon import import_addon
from bedrock_server_manager.error import AppFileNotFoundError, MissingArgumentError


@pytest.fixture
def mock_bedrock_server():
    """Fixture for a mocked BedrockServer."""
    server = MagicMock()
    server.is_running.return_value = False
    return server


@pytest.fixture
def mock_get_server_instance(mock_bedrock_server):
    """Fixture to patch get_server_instance."""
    with patch(
        "bedrock_server_manager.api.addon.get_server_instance",
        return_value=mock_bedrock_server,
    ) as mock:
        yield mock


@pytest.fixture
def temp_addon_file(tmp_path):
    """Creates a temporary addon file for tests."""
    addon_file = tmp_path / "my_addon.mcpack"
    addon_file.touch()
    return str(addon_file)


class TestImportAddon:
    @patch("bedrock_server_manager.api.addon.server_lifecycle_manager")
    def test_import_addon_success_with_stop_start(
        self,
        mock_lifecycle_manager,
        mock_get_server_instance,
        mock_bedrock_server,
        temp_addon_file,
    ):
        result = import_addon("test-server", temp_addon_file)
        assert result["status"] == "success"
        assert "installed successfully" in result["message"]
        mock_lifecycle_manager.assert_called_once_with(
            "test-server",
            stop_before=True,
            start_after=True,
            restart_on_success_only=True,
        )
        mock_bedrock_server.process_addon_file.assert_called_once_with(temp_addon_file)

    @patch("bedrock_server_manager.api.addon.server_lifecycle_manager")
    def test_import_addon_success_no_stop_start(
        self,
        mock_lifecycle_manager,
        mock_get_server_instance,
        mock_bedrock_server,
        temp_addon_file,
    ):
        result = import_addon("test-server", temp_addon_file, stop_start_server=False)
        assert result["status"] == "success"
        mock_lifecycle_manager.assert_called_once_with(
            "test-server",
            stop_before=False,
            start_after=False,
            restart_on_success_only=True,
        )
        mock_bedrock_server.process_addon_file.assert_called_once_with(temp_addon_file)

    def test_import_addon_file_not_found(self, mock_get_server_instance):
        with pytest.raises(AppFileNotFoundError):
            import_addon("test-server", "/non/existent/file.mcpack")

    def test_import_addon_no_server_name(self):
        with pytest.raises(MissingArgumentError):
            import_addon("", "file.mcpack")

    def test_import_addon_no_file_path(self):
        with pytest.raises(MissingArgumentError):
            import_addon("test-server", "")

    def test_import_addon_lock_skipped(self, temp_addon_file):
        with patch("bedrock_server_manager.api.addon._addon_lock") as mock_lock:
            mock_lock.acquire.return_value = False
            result = import_addon("test-server", temp_addon_file)
            assert result["status"] == "skipped"

    @patch("bedrock_server_manager.api.addon.server_lifecycle_manager")
    def test_import_addon_exception(
        self,
        mock_lifecycle_manager,
        mock_get_server_instance,
        mock_bedrock_server,
        temp_addon_file,
    ):
        mock_bedrock_server.process_addon_file.side_effect = Exception("Test exception")
        result = import_addon("test-server", temp_addon_file)
        assert result["status"] == "error"
        assert "Test exception" in result["message"]
