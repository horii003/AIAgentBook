"""セッション管理機能

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化します。
"""
import os
import secrets
import logging
from datetime import datetime
from strands.session.file_session_manager import FileSessionManager

_logger = logging.getLogger(__name__)


class SessionManagerFactory:
    """セッションマネージャーのファクトリークラス"""

    # セッションの保存先ディレクトリ
    DEFAULT_STORAGE_DIR = "storage/sessions"

    @staticmethod
    def generate_session_id() -> str:
        """一意のセッションIDを生成

        Returns:
            str: 生成されたセッションID（{YYYYMMDD_HHMMSS}_{8桁英数字}形式）

        Examples:
            >>> SessionManagerFactory.generate_session_id()
            "20260510_143022_a1b2c3d4"
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = secrets.token_hex(4)
        session_id = f"{timestamp}_{random_part}"
        _logger.info("セッションIDを生成しました: %s", session_id)
        return session_id

    @classmethod
    def create_session_manager(
        cls,
        session_id: str,
        storage_dir: str = DEFAULT_STORAGE_DIR,
    ) -> FileSessionManager:
        """FileSessionManagerのインスタンスを作成

        Args:
            session_id: セッションID（ユーザーごとに一意）
            storage_dir: セッションデータの保存先ディレクトリ

        Returns:
            FileSessionManager: セッションマネージャーのインスタンス
        """
        os.makedirs(storage_dir, exist_ok=True)
        manager = FileSessionManager(session_id=session_id, storage_dir=storage_dir)
        _logger.info(
            "セッションマネージャを生成しました: session_id=%s, storage_dir=%s",
            session_id,
            storage_dir,
        )
        return manager

    @staticmethod
    def get_session_storage_path(
        session_id: str,
        storage_dir: str = DEFAULT_STORAGE_DIR,
    ) -> str:
        """指定されたセッションIDのセッションディレクトリパスを取得

        Args:
            session_id: セッションID
            storage_dir: セッションデータの保存先ディレクトリ

        Returns:
            str: セッションディレクトリのパス
        """
        return os.path.join(storage_dir, session_id)
