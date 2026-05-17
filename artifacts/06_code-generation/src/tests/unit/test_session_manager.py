"""セッションマネージャの単体テスト"""

import re

from session.session_manager import SessionManagerFactory


class TestSessionManagerFactory:
    """SessionManagerFactory のテスト"""

    def test_session_id_format(self):
        """セッションID形式が正しいこと"""
        sid = SessionManagerFactory.generate_session_id()
        # YYYYMMDD_HHMMSS_xxxxxxxx
        assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", sid)

    def test_session_id_unique(self):
        """100回連続生成で全て一意であること"""
        ids = {SessionManagerFactory.generate_session_id() for _ in range(100)}
        assert len(ids) == 100

    def test_create_session_manager(self, tmp_path, monkeypatch):
        """FileSessionManager が正しく生成されること"""
        monkeypatch.setattr(
            "session.session_manager._STORAGE_DIR", tmp_path / "sessions"
        )
        sid = "20260517_120000_abcd1234"
        sm = SessionManagerFactory.create_session_manager(sid)
        assert sm is not None

    def test_session_exists(self, tmp_path, monkeypatch):
        """session_exists() が正しく判定すること"""
        monkeypatch.setattr(
            "session.session_manager._STORAGE_DIR", tmp_path / "sessions"
        )
        sid = "20260517_120000_abcd1234"
        assert not SessionManagerFactory.session_exists(sid)
        SessionManagerFactory.create_session_manager(sid)
        assert SessionManagerFactory.session_exists(sid)
