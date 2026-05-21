"""セッション管理機能

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化する。
"""
import os
import uuid
import logging
from datetime import datetime
from strands.session.file_session_manager import FileSessionManager

_logger = logging.getLogger(__name__)


class SessionManagerFactory:
    """セッションマネージャーのファクトリークラス

    全メソッドが @staticmethod であり、インスタンス化不要で
    SessionManagerFactory.xxx() として直接呼び出せる。
    """

    DEFAULT_STORAGE_DIR = "storage/sessions"
    _storage_dir = None

    @staticmethod
    def generate_session_id(prefix: str = "") -> str:
        """一意のセッションIDを生成する。

        Args:
            prefix: セッションIDのプレフィックス（オプション）

        Returns:
            str: 生成されたセッションID
                - prefixなし: "YYYYMMDDHHMMSS_xxxxxxxx"
                - prefixあり: "prefix_YYYYMMDDHHMMSS_xxxxxxxx"
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        uuid_str = uuid.uuid4().hex[:8]
        session_id = f"{timestamp}_{uuid_str}" if not prefix else f"{prefix}_{timestamp}_{uuid_str}"
        _logger.info("セッションID生成: %s", session_id)
        return session_id

    @classmethod
    def get_storage_dir(cls) -> str:
        """セッションの保存先ディレクトリを取得する。

        Returns:
            str: セッション保存先ディレクトリのパス
        """
        if cls._storage_dir is None:
            storage_dir = cls.DEFAULT_STORAGE_DIR
            os.makedirs(storage_dir, exist_ok=True)
            cls._storage_dir = storage_dir
        return cls._storage_dir

    @classmethod
    def create_session_manager(cls, session_id: str) -> FileSessionManager:
        """FileSessionManagerのインスタンスを作成する。

        Args:
            session_id: セッションID

        Returns:
            FileSessionManager: セッションマネージャーのインスタンス
        """
        storage_dir = cls.get_storage_dir()
        _logger.info("FileSessionManager 生成: session_id=%s, storage_dir=%s", session_id, storage_dir)
        return FileSessionManager(session_id=session_id, storage_dir=storage_dir)

    @classmethod
    def get_session_path(cls, session_id: str) -> str:
        """指定されたセッションIDのセッションディレクトリパスを取得する。

        Args:
            session_id: セッションID

        Returns:
            str: セッションディレクトリのパス
        """
        storage_dir = cls.get_storage_dir()
        return os.path.join(storage_dir, session_id)
