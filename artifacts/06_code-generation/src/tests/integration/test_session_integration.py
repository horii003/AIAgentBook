"""セッション永続化の結合テスト"""

from session.session_manager import SessionManagerFactory


class TestSessionIntegration:
    """セッション管理の結合テスト"""

    def test_session_lifecycle(self, tmp_path, monkeypatch):
        """セッション作成→存在確認→ディレクトリ取得の一連フロー"""
        monkeypatch.setattr(
            "session.session_manager._STORAGE_DIR", tmp_path / "sessions"
        )

        # セッションID生成
        sid = SessionManagerFactory.generate_session_id()
        assert sid is not None

        # セッション作成前は存在しない
        assert not SessionManagerFactory.session_exists(sid)

        # セッション作成
        sm = SessionManagerFactory.create_session_manager(sid)
        assert sm is not None

        # セッション作成後は存在する
        assert SessionManagerFactory.session_exists(sid)

        # ディレクトリパス取得
        session_dir = SessionManagerFactory.get_session_dir(sid)
        assert sid in session_dir

    def test_multiple_sessions(self, tmp_path, monkeypatch):
        """複数セッションが独立して管理されること"""
        monkeypatch.setattr(
            "session.session_manager._STORAGE_DIR", tmp_path / "sessions"
        )

        sid1 = SessionManagerFactory.generate_session_id()
        sid2 = SessionManagerFactory.generate_session_id()
        assert sid1 != sid2

        SessionManagerFactory.create_session_manager(sid1)
        SessionManagerFactory.create_session_manager(sid2)

        assert SessionManagerFactory.session_exists(sid1)
        assert SessionManagerFactory.session_exists(sid2)
