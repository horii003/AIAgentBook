"""セッション永続化テスト（TC-INT-020〜021）"""
import os
import pytest
from session.session_manager import SessionManagerFactory


class TestSessionPersistence:
    def test_session_file_created(self, tmp_path):
        """TC-INT-020: セッションファイルがstorage/sessions/に生成されること"""
        session_id = "test_session_20260510_143022_a1b2c3d4"
        storage_dir = str(tmp_path / "sessions")
        manager = SessionManagerFactory.create_session_manager(
            session_id=session_id,
            storage_dir=storage_dir,
        )
        # ストレージディレクトリが作成されること
        assert os.path.exists(storage_dir)

    def test_session_manager_returns_file_session_manager(self, tmp_path):
        """TC-INT-021: FileSessionManagerインスタンスが返されること"""
        from strands.session.file_session_manager import FileSessionManager
        session_id = "test_session"
        manager = SessionManagerFactory.create_session_manager(
            session_id=session_id,
            storage_dir=str(tmp_path),
        )
        assert isinstance(manager, FileSessionManager)

    def test_different_session_ids_are_unique(self):
        """異なるセッションIDが生成されること"""
        id1 = SessionManagerFactory.generate_session_id()
        id2 = SessionManagerFactory.generate_session_id()
        assert id1 != id2
