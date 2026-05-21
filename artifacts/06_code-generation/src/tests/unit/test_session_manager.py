"""セッション管理の単体テスト"""
import sys
import os
import re
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from strands.session.file_session_manager import FileSessionManager
from session.session_manager import SessionManagerFactory


class TestSessionManagerFactory:
    """SessionManagerFactory のテスト"""

    def setup_method(self):
        """各テスト前にキャッシュをリセットする。"""
        SessionManagerFactory._storage_dir = None

    def test_generate_session_id_format(self):
        """generate_session_id() が YYYYMMDDHHMMSS_xxxxxxxx 形式であること"""
        session_id = SessionManagerFactory.generate_session_id()
        assert re.match(r"^\d{14}_[0-9a-f]{8}$", session_id), f"形式不正: {session_id}"

    def test_generate_session_id_with_prefix(self):
        """generate_session_id("test") が test_YYYYMMDDHHMMSS_xxxxxxxx 形式であること"""
        session_id = SessionManagerFactory.generate_session_id("test")
        assert re.match(r"^test_\d{14}_[0-9a-f]{8}$", session_id), f"形式不正: {session_id}"

    def test_generate_session_id_unique(self):
        """同時に2回呼び出しても異なるIDが生成されること"""
        id1 = SessionManagerFactory.generate_session_id()
        id2 = SessionManagerFactory.generate_session_id()
        assert id1 != id2

    def test_create_session_manager_returns_file_session_manager(self, tmp_path):
        """create_session_manager() が FileSessionManager インスタンスを返すこと"""
        SessionManagerFactory._storage_dir = str(tmp_path / "sessions")
        manager = SessionManagerFactory.create_session_manager("test_session")
        assert isinstance(manager, FileSessionManager)

    def test_get_storage_dir_creates_directory(self, tmp_path):
        """get_storage_dir() がディレクトリを自動作成すること"""
        target_dir = str(tmp_path / "sessions")
        SessionManagerFactory._storage_dir = None
        # DEFAULT_STORAGE_DIR を一時的に上書き
        original = SessionManagerFactory.DEFAULT_STORAGE_DIR
        SessionManagerFactory.DEFAULT_STORAGE_DIR = target_dir
        try:
            result = SessionManagerFactory.get_storage_dir()
            assert os.path.isdir(result)
        finally:
            SessionManagerFactory.DEFAULT_STORAGE_DIR = original
            SessionManagerFactory._storage_dir = None
