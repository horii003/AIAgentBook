"""セッション管理機能。

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化する。
"""
import logging
import os
import uuid
from datetime import datetime

from strands.session.file_session_manager import FileSessionManager

_logger = logging.getLogger(__name__)

# セッションデータの保存先ディレクトリ（プロジェクトルートからの相対パス）
_SESSION_STORAGE_DIR = "storage/sessions"


class SessionManagerFactory:
    """セッションマネージャーのファクトリークラス。

    セッションID生成とFileSessionManagerインスタンス生成を担当する。
    """

    # セッションの保存先ディレクトリ（キャッシュ）
    _storage_dir: str = None

    @classmethod
    def generate_session_id(cls, prefix: str = "") -> str:
        """一意のセッションIDを生成する。

        セッションIDはタイムスタンプ（秒単位）とUUID（8文字）の組み合わせで生成される。
        これにより、同じ秒に複数のセッションが開始されても衝突を防ぐ。

        Args:
            prefix: セッションIDのプレフィックス（オプション）
                   例: "test", "user_a" など

        Returns:
            str: 生成されたセッションID
                - prefixなし: "YYYYMMDD_HHMMSS_uuid8"
                - prefixあり: "prefix_YYYYMMDD_HHMMSS_uuid8"

        Examples:
            >>> SessionManagerFactory.generate_session_id()
            "20260209_143022_a1b2c3d4"

            >>> SessionManagerFactory.generate_session_id("test")
            "test_20260209_143022_a1b2c3d4"
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        session_id = f"{timestamp}_{unique_id}"
        if prefix:
            session_id = f"{prefix}_{session_id}"
        return session_id

    @classmethod
    def get_storage_dir(cls) -> str:
        """セッションの保存先ディレクトリを取得する。

        初回呼び出し時にディレクトリを作成し、以降はキャッシュを返す。

        Returns:
            str: セッションデータの保存先ディレクトリパス
        """
        if cls._storage_dir is None:
            # プロジェクトルートからの相対パスでディレクトリを構築
            storage_dir = _SESSION_STORAGE_DIR
            os.makedirs(storage_dir, exist_ok=True)
            cls._storage_dir = storage_dir
        return cls._storage_dir

    @classmethod
    def create_session_manager(cls, session_id: str) -> FileSessionManager:
        """FileSessionManagerのインスタンスを作成する。

        Args:
            session_id: セッションID（ユーザーごとに一意）

        Returns:
            FileSessionManager: セッションマネージャーのインスタンス
        """
        storage_dir = cls.get_storage_dir()
        session_manager = FileSessionManager(
            session_id=session_id,
            storage_dir=storage_dir,
        )
        _logger.info("セッション作成: session_id=%s", session_id)
        return session_manager

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
