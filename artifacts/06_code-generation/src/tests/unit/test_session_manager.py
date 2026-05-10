"""セッションマネージャの単体テスト"""
import re
import pytest
from unittest.mock import patch
from strands.session.file_session_manager import FileSessionManager
from session.session_manager import SessionManagerFactory


class TestSessionManagerFactory:
    def test_generate_session_id_format(self):
        """TC-UNIT-050: generate_session_id()が正しいフォーマットのIDを生成すること"""
        session_id = SessionManagerFactory.generate_session_id()
        assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", session_id)

    def test_generate_session_id_unique(self):
        """TC-UNIT-051: generate_session_id()が呼び出しごとに異なるIDを生成すること"""
        id1 = SessionManagerFactory.generate_session_id()
        id2 = SessionManagerFactory.generate_session_id()
        assert id1 != id2

    def test_create_session_manager_returns_instance(self, tmp_path):
        """TC-UNIT-052: create_session_manager()がFileSessionManagerインスタンスを返すこと"""
        manager = SessionManagerFactory.create_session_manager(
            session_id="test_session",
            storage_dir=str(tmp_path),
        )
        assert isinstance(manager, FileSessionManager)

    def test_get_session_storage_path(self):
        """get_session_storage_path()が正しいパスを返すこと"""
        path = SessionManagerFactory.get_session_storage_path(
            session_id="test_session",
            storage_dir="storage/sessions",
        )
        assert "test_session" in path
        assert "storage/sessions" in path
