"""セッション管理機能

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化します。
"""
import os
import uuid
from datetime import datetime

from strands.session.file_session_manager import FileSessionManager


class SessionManagerFactory:
    """セッション管理ファクトリ。

    セッションIDの生成、FileSessionManagerインスタンスの生成、
    リセットコマンドの判定を提供するユーティリティクラス。
    全メソッドが@staticmethodであり、インスタンス化不要。
    """

    # セッションデータの保存先ベースディレクトリ
    _STORAGE_DIR = "storage/sessions"

    # リセットコマンドの一覧
    _RESET_COMMANDS = {"reset", "リセット", "最初から"}

    @staticmethod
    def generate_session_id() -> str:
        """セッションIDを生成する。

        Returns:
            session_{YYYYMMDD_HHMMSS}_{ランダム8文字}形式のセッションID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = uuid.uuid4().hex[:8]
        return f"session_{timestamp}_{random_suffix}"

    @staticmethod
    def create(session_id: str) -> FileSessionManager:
        """FileSessionManagerインスタンスを生成する。

        Args:
            session_id: セッションID（generate_session_idで生成した値）

        Returns:
            指定セッションIDに対応するFileSessionManagerインスタンス

        Raises:
            ValueError: session_idが空文字の場合
        """
        if not session_id:
            raise ValueError("session_id は空文字にできません")

        storage_dir = SessionManagerFactory._STORAGE_DIR
        os.makedirs(storage_dir, exist_ok=True)

        return FileSessionManager(session_id=session_id, storage_dir=storage_dir)

    @staticmethod
    def is_reset_command(user_input: str) -> bool:
        """ユーザー入力がリセットコマンドかどうかを判定する。

        Args:
            user_input: ユーザーからの入力テキスト

        Returns:
            リセットコマンドの場合True、それ以外はFalse
        """
        normalized = user_input.strip().lower()
        # 日本語コマンドは小文字変換しても変わらないため、元の値も確認
        return normalized in SessionManagerFactory._RESET_COMMANDS or user_input.strip() in SessionManagerFactory._RESET_COMMANDS
