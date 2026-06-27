"""SessionManagerFactoryの単体テスト"""
import re
import pytest
from unittest.mock import patch, MagicMock

from session.session_manager import SessionManagerFactory


class TestSessionManagerFactory:
    """SessionManagerFactoryのテスト"""

    def test_generate_session_id_format(self):
        session_id = SessionManagerFactory.generate_session_id()
        assert re.match(r"^session_\d{8}_\d{6}_[0-9a-f]{8}$", session_id)

    def test_generate_session_id_unique(self):
        id1 = SessionManagerFactory.generate_session_id()
        id2 = SessionManagerFactory.generate_session_id()
        assert id1 != id2

    def test_create_empty_session_id_raises(self):
        with pytest.raises(ValueError):
            SessionManagerFactory.create("")

    def test_create_returns_file_session_manager(self):
        with patch("session.session_manager.FileSessionManager") as mock_fsm:
            with patch("os.makedirs"):
                SessionManagerFactory.create("test_session_id")
                mock_fsm.assert_called_once()

    def test_is_reset_command_reset(self):
        assert SessionManagerFactory.is_reset_command("reset") is True

    def test_is_reset_command_reset_uppercase(self):
        assert SessionManagerFactory.is_reset_command("Reset") is True

    def test_is_reset_command_reset_all_caps(self):
        assert SessionManagerFactory.is_reset_command("RESET") is True

    def test_is_reset_command_japanese_reset(self):
        assert SessionManagerFactory.is_reset_command("リセット") is True

    def test_is_reset_command_japanese_start_over(self):
        assert SessionManagerFactory.is_reset_command("最初から") is True

    def test_is_reset_command_with_spaces(self):
        assert SessionManagerFactory.is_reset_command(" reset ") is True

    def test_is_reset_command_hello_false(self):
        assert SessionManagerFactory.is_reset_command("hello") is False

    def test_is_reset_command_partial_false(self):
        assert SessionManagerFactory.is_reset_command("リセットする") is False

    def test_is_reset_command_empty_false(self):
        assert SessionManagerFactory.is_reset_command("") is False
